from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List

from .config import AppConfig
from .ingest import discover_inputs
from .processing import process_files
from .kpis import compute_kpis
from .report import write_reports
from .emailer import send_report_email
from .monitor import write_health_file

logger = logging.getLogger(__name__)


def _move_file(src: Path, dest_dir: Path, dry_run: bool) -> Path:
    """
    Move a file into a destination directory, avoiding overwrites.
    In dry-run mode, only logs what would happen.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / src.name
    if dest.exists():
        dest = dest_dir / f"{src.stem}__dup{src.suffix}"

    if dry_run:
        logger.info("DRY RUN: Would move %s -> %s", src, dest)
        return dest

    shutil.move(str(src), str(dest))
    return dest


def run_pipeline(cfg: AppConfig, dry_run: bool = False) -> Dict[str, Any]:
    """
    Orchestrates the weekly auto-reporting workflow.

    Returns a dict describing the outcome. Keys are strings; values vary by key.
    """
    # Ensure all required folders exist before doing anything
    cfg.ensure_dirs()

    # ---- Run context (debug) ----
    logger.debug("Pipeline starting")
    logger.debug("dry_run=%s", dry_run)
    logger.debug("inbox_dir=%s", cfg.inbox_dir)
    logger.debug("input_globs=%s", cfg.input_globs)
    logger.debug("processed_dir=%s", cfg.processed_dir)
    logger.debug("failed_dir=%s", cfg.failed_dir)
    logger.debug("output_dir=%s", cfg.output_dir)

    # ---- Discover inputs ----
    files = discover_inputs(cfg.inbox_dir, cfg.input_globs)
    logger.info("Discovered %d input file(s) in %s", len(files), cfg.inbox_dir)
    logger.debug("Input files: %s", [p.name for p in files])

    # If no inputs exit gracefully, write a health file saying "nothing to do"
    if not files:
        logger.debug("Early exit: no input files found.")
        health = write_health_file(
            cfg.output_dir,
            ok=True,
            message="No input files found. Nothing to do.",
        )
        return {
            "ok": True,
            "status": "no_inputs",
            "message": "No input files found. Nothing to do.",
            "inputs_found": 0,
            "inputs_processed": 0,
            "health_file": str(health),
        }

    # Track which files were moved successfully vs failed
    processed_ok: List[Path] = []
    processed_fail: List[Path] = []

    # NOTE: Your original "validation" try/except couldn’t actually fail.
    # We keep the structure, but treat all discovered files as valid inputs.
    valid_files: List[Path] = list(files)

    # ---- Processing stage ----
    logger.debug("Starting processing stage on %d file(s)", len(valid_files))
    try:
        result = process_files(valid_files, cfg.column_map)
    except Exception as e:
        logger.exception("Fatal: processing crashed before producing outputs: %s", e)
        health = write_health_file(cfg.output_dir, ok=False, message=f"Fatal process error: {e}")
        return {
            "ok": False,
            "status": "fatal",
            "message": f"Fatal process error: {e}",
            "inputs_found": len(files),
            "inputs_processed": 0,
            "health_file": str(health),
        }

    # ---- Move inputs (workflow boundary) ----
    logger.debug("Moving %d processed file(s) to %s", len(valid_files), cfg.processed_dir)
    for f in valid_files:
        try:
            _move_file(f, cfg.processed_dir, dry_run=dry_run)
            processed_ok.append(f)
        except Exception as e:
            logger.exception("Failed moving processed file %s: %s", f, e)

    logger.debug("Moving %d failed file(s) to %s", len(processed_fail), cfg.failed_dir)
    for f in processed_fail:
        try:
            _move_file(f, cfg.failed_dir, dry_run=dry_run)
        except Exception as e:
            logger.exception("Failed moving failed file %s: %s", f, e)

    # ---- KPIs ----
    logger.debug("Computing KPIs")
    kpis = compute_kpis(result.combined, cfg.column_map)

    # ---- Reports ----
    logger.debug("Writing reports to %s (basename=%s)", cfg.output_dir, cfg.report_basename)
    artifacts = write_reports(
        output_dir=cfg.output_dir,
        basename=cfg.report_basename,
        combined_df=result.combined,
        file_summaries=result.file_summaries,
        kpis=kpis,
        write_cleaned_csv=cfg.write_cleaned_csv,
        write_kpi_json=cfg.write_kpi_json,
    )

    # Health marker (success — may be overwritten if email fails)
    health = write_health_file(cfg.output_dir, ok=True, message="Run completed successfully.")

    # ---- Email delivery ----
    attach_paths: List[Path] = [Path(artifacts.file_summary_csv)]
    if artifacts.cleaned_csv:
        attach_paths.append(Path(artifacts.cleaned_csv))
    if artifacts.kpi_json:
        attach_paths.append(Path(artifacts.kpi_json))

    logger.debug("Preparing email with %d attachment(s)", len(attach_paths))
    try:
        send_report_email(cfg.email, kpis=kpis, attachments=attach_paths, dry_run=dry_run)
    except Exception as e:
        logger.exception("Email send failed: %s", e)
        # Still keep pipeline result, but mark health as failed due to email
        health = write_health_file(cfg.output_dir, ok=False, message=f"Run OK but email failed: {e}")

    # ---- Final debug summary ----
    logger.debug(
        "Pipeline finished | status=ok | inputs_found=%d | inputs_processed=%d",
        len(files),
        len(processed_ok),
    )

    return {
        "ok": True,
        "status": "ok",
        "message": "Run completed successfully.",
        "inputs_found": len(files),
        "inputs_processed": len(processed_ok),
        "run_stamp": artifacts.run_stamp,
        "cleaned_csv": artifacts.cleaned_csv,
        "kpi_json": artifacts.kpi_json,
        "file_summary_csv": artifacts.file_summary_csv,
        "health_file": str(health),
    }
