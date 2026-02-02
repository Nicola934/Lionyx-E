from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import AppConfig
from .pipeline import run_pipeline
from .monitor import read_health
from .logging_setup import setup_logging


EXIT_OK = 0
EXIT_BAD_ARGS = 1
EXIT_PIPELINE_FAILED = 2
EXIT_CONFIG_INVALID = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="weekly_report",
        description="Weekly Auto-Reporting System",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.json"),
        help="Path to config.json (default: ./config.json)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    sub_parsers = parser.add_subparsers(dest="command", required=True)

    run_parser = sub_parsers.add_parser("run", help="Run the full pipeline")
    run_parser.add_argument("--dry-run", action="store_true", help="Simulate run safely")

    sub_parsers.add_parser("status", help="Show last run status")
    sub_parsers.add_parser("validate-config", help="Validate configuration and folders")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return EXIT_BAD_ARGS

    # Load config + ensure dirs + configure logging
    try:
        cfg = AppConfig.from_json(args.config)
        cfg.ensure_dirs()
        setup_logging(cfg.log_dir, verbose=args.verbose)
    except Exception as e:
        print(f"Config error: {e}")
        return EXIT_CONFIG_INVALID

    if args.command == "validate-config":
        print("Config loaded OK and directories ensured.")
        return EXIT_OK

    if args.command == "status":
        print(read_health(cfg.output_dir))
        return EXIT_OK

    if args.command == "run":
        result = run_pipeline(cfg, dry_run=args.dry_run)

        # Standard path: result is dict (your pipeline returns dict)
        if isinstance(result, dict):
            msg = result.get("message", "Run complete.")
            ok = bool(result.get("ok", result.get("status") in ("ok", "no_inputs")))
            print(msg)
            return EXIT_OK if ok else EXIT_PIPELINE_FAILED

        # Fallback: dataclass-like object
        msg = getattr(result, "message", "Run complete.")
        ok = bool(getattr(result, "ok", False))
        print(msg)
        return EXIT_OK if ok else EXIT_PIPELINE_FAILED

    return EXIT_BAD_ARGS


if __name__ == "__main__":
    raise SystemExit(main())
