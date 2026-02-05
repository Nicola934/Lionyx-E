from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any

import pandas as pd

from .config import ColumnMap

logger = logging.getLogger(__name__)

YES = {"yes", "y", "true", "t", "1", "1.0"}
NO = {"no", "n", "false", "f", "0", "0.0"}


@dataclass(frozen=True)
class ProcessResult:
    combined: pd.DataFrame
    file_summaries: pd.DataFrame


def _read_any(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suf == ".json":
        return pd.read_json(path)
    return pd.read_csv(path)


def _normalize_text(s: pd.Series) -> pd.Series:
    # Always safe even if s contains NaNs
    return (
        s.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )


def _normalize_yes_no(s: pd.Series) -> pd.Series:
    """
    Convert common yes/no representations into pandas BooleanDtype:
      - strings: yes/no, true/false, y/n, 1/0
      - numbers: 1/0, 1.0/0.0
    Anything unknown becomes <NA>.
    """
    # Fast-path for numeric-like data: map 1/0 directly
    # (This avoids string edge cases like "1.0")
    if pd.api.types.is_numeric_dtype(s):
        out = pd.Series(pd.NA, index=s.index, dtype="boolean")
        out = out.mask(s == 1, True)
        out = out.mask(s == 0, False)
        return out

    s_str = s.astype("string").str.strip().str.lower()

    # Also normalize common numeric-string variants like "1.0"/"0.0"
    # and remove trailing .0 if present
    s_str = s_str.str.replace(r"^\s*([01])\.0\s*$", r"\1", regex=True)

    out = pd.Series(pd.NA, index=s.index, dtype="boolean")
    out = out.mask(s_str.isin(YES), True)
    out = out.mask(s_str.isin(NO), False)
    return out


def _parse_date_safe(s: pd.Series) -> pd.Series:
    # Returns datetime64[ns] with NaT where parsing fails
    return pd.to_datetime(s, errors="coerce")


def _validate_columns(df: pd.DataFrame, cm: ColumnMap) -> None:
    required = [cm.service_col, cm.region_col, cm.satisfied_col, cm.recommend_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns {missing}. Available: {list(df.columns)}")


def clean_df(df: pd.DataFrame, cm: ColumnMap) -> pd.DataFrame:
    _validate_columns(df, cm)

    df = df.copy()

    df[cm.service_col] = _normalize_text(df[cm.service_col])
    df[cm.region_col] = _normalize_text(df[cm.region_col])

    df[cm.satisfied_col] = _normalize_yes_no(df[cm.satisfied_col])
    df[cm.recommend_col] = _normalize_yes_no(df[cm.recommend_col])

    if cm.date_col and cm.date_col in df.columns:
        df[cm.date_col] = _parse_date_safe(df[cm.date_col])

    # Drop rows missing any required values
    df = df.dropna(subset=[cm.service_col, cm.region_col, cm.satisfied_col, cm.recommend_col])

    # Drop empty strings after normalization
    df = df[
        (df[cm.service_col].astype("string").str.len() > 0) &
        (df[cm.region_col].astype("string").str.len() > 0)
    ]

    return df


def dedupe_df(df: pd.DataFrame, cm: ColumnMap) -> pd.DataFrame:
    df = df.copy()

    if cm.respondent_id_col and cm.respondent_id_col in df.columns:
        if cm.date_col and cm.date_col in df.columns:
            return df.drop_duplicates(subset=[cm.respondent_id_col, cm.date_col], keep="last")
        return df.drop_duplicates(subset=[cm.respondent_id_col], keep="last")

    subset = [cm.service_col, cm.region_col, cm.satisfied_col, cm.recommend_col]
    if cm.date_col and cm.date_col in df.columns:
        subset = [cm.date_col] + subset

    return df.drop_duplicates(subset=subset, keep="last")


def process_files(paths: List[Path], cm: ColumnMap) -> ProcessResult:
    cleaned_frames: List[pd.DataFrame] = []
    summaries: List[Dict[str, Any]] = []

    for p in paths:
        raw = _read_any(p)
        raw_rows, raw_cols = int(raw.shape[0]), int(raw.shape[1])

        cleaned = clean_df(raw, cm)
        cleaned = dedupe_df(cleaned, cm)

        summaries.append({
            "filename": p.name,
            "raw_rows": raw_rows,
            "raw_cols": raw_cols,
            "clean_rows": int(cleaned.shape[0]),
            "clean_cols": int(cleaned.shape[1]),
        })

        cleaned_frames.append(cleaned)
        logger.info("Processed %s (raw_rows=%s clean_rows=%s)", p.name, raw_rows, int(cleaned.shape[0]))

    combined = pd.concat(cleaned_frames, ignore_index=True) if cleaned_frames else pd.DataFrame()
    file_summaries = pd.DataFrame(summaries)

    if not combined.empty:
        combined = dedupe_df(combined, cm)

    return ProcessResult(combined=combined, file_summaries=file_summaries)
