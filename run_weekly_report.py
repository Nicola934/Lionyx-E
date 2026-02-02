from __future__ import annotations

import argparse
import logging
from pathlib import Path

from weekly_report.config import AppConfig
from weekly_report.logging_setup import setup_logging
from weekly_report.pipeline import run_pipeline


# Entry point for running the weekly report pipeline
# Function returns an int so that it can be used as an exit code for the program
# An exit code of 0 typically indicates that the program completed successfully without errors.
def main() ->int:
    # Parse command-line arguments
    # argpasrse is a module in Python's standard library that provides a way to handle command-line arguments passed to a script.
    # It allows you to define what arguments your program requires, handle optional arguments, and generate help messages for users.
    parser = argparse.ArgumentParser(description="Weekly Auto-Reporting System")
    parser.add_argument("--config", default="config.json", help="Path to config.json")
    parser.add_argument("--dry-run", action="store_true", help="Process without moving files or sending email")

    # Parse the command-line arguments and store them in the args variable
    args = parser.parse_args()
    cfg = AppConfig.from_json(Path(args.config))
    setup_logging(cfg.log_dir)

    logging.getLogger(__name__).info("=== Weekly report run starting ===")
    artifacts = run_pipeline(cfg, dry_run=args.dry_run)
    logging.getLogger(__name__).info("=== Weekly report run complete ===")
    logging.getLogger(__name__).info("Artifacts: %s", artifacts)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
