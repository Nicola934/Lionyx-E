from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

HEALTH_FILENAME = "health.txt"

@dataclass(frozen=True)
class HealthStatus:
    ok: bool
    message: str
    timestamp: str


def write_health_file(output_dir: Path, ok: bool, message: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True) # Ensure the output directory exists
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = output_dir / "health.txt" # Define the health file path
    content = f"{ts} | {'OK' if ok else 'FAIL'} | {message}\n"
    path.write_text(content, encoding="utf-8") # Creates the file with the content 
    # Or overwrites if it already exists; it appends content if the file exists
    return path

def read_health(output_dir: Path) -> str:
    health_path = output_dir / HEALTH_FILENAME
    if not health_path.exists():
        return "No health file found yet. Run: weekly_report run"

    return health_path.read_text(encoding="utf-8").strip()