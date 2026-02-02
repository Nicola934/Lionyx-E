from __future__ import annotations

from pathlib import Path
from typing import List


def discover_inputs(inbox_dir: Path, globs: List[str]) -> List[Path]:
    files: List[Path] = []
    for pat in globs:
        files.extend(inbox_dir.glob(pat))
    return sorted({p for p in files if p.is_file()})