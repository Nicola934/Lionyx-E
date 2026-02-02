from __future__ import annotations


import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple

import pandas as pd 

from .config import ColumnMap

logger = logging.getLogger(__name__)


YES = {"yes", "y", "true", "t", "1"}
NO = {"no", "n", "false", "f", "0"}


@dataclass(frozen=True)
class ProcessResult:
    combined: pd.DataFrame # This a combination of all the files that were processed
    file_summaries: pd.DataFrame # one row per file

def _read_any(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suf == ".json":
        return pd.read_json(path)
    return pd.read_csv(path)

def _normalize_text(s: pd.Series) -> pd.Series: # It accepts a pandas series as input and returns a cleaned version of that series
    return(
        # astype("string") ensures that the series is treated as string data type
        # str.strip() removes leading and trailing whitespace from each string in the series
        # str.replace(r"\s+", " ", regex=True) replaces multiple consecutive whitespace characters within the strings with a single space
        # str.title() converts the strings to title case, capitalizing the first letter of each word
        # regex=True indicates that the first argument is a regular expression pattern meaning it will match one or more whitespace characters
        # r before the string indicates that it is a raw string literal, which treats backslashes as literal characters
        # \s+ is a regex pattern that matches one or more whitespace characters (spaces, tabs, newlines, etc.)
        # In essennce this function standardizes text data by cleaning up whitespace and formatting it in a consistent title case style.
        s.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

def _normalize_yes_no(s: pd.Series) -> pd.Series:
    s_str = s.astype("string").str.strip().str.lower() # Convert to string, strip whitespace, and convert to lowercase
    # pd.Series() is used to create a new pandas Series object named out
    # It initializes this Series with pd.NA values, which represent missing or null values in pandas
    # The index of this new Series is set to be the same as the index of the input Series s_str
    # The dtype="boolean" argument specifies that the data type of the Series should be boolean, allowing it to hold True, False, or pd.NA values.
    # pd.Na values are used to represent missing or undefined values in the Series. 
    # example: if the input series has values that are neither in YES nor NO sets then it writes pd.NA in the output series
    out = pd.Series(pd.Na, index=s.index, dtype="boolean")
    # Sets the corresponding entries in out to True where the values in s_str are found in the YES set
    # mask() is a pandas Series method that allows you to conditionally replace values in the Series based on a boolean mask.
    # s_str.isin(YES) creates a boolean mask where each element is True if the corresponding value in s_str is found in the YES set and False otherwise
    out = out.mask(s_str.isin(YES), True) 
    out = out.mask(s_str.isin(NO), False) # Sets the corresponding entries in out to False where the values in s_str are found in the NO set
    # It returns a pandas series that is cleared of whitespaces, standardized to lowercase, and converted to boolean values based on predefined sets of yes/no indicators.
    return out

def _parse_date_safe(s: pd.Series) -> pd.Series:
    # It attempts to convert the series s to datetime format
    # errors="coerce" means that any values that cannot be converted to datetime will be set to NaT (Not a Time), which represents missing or null datetime values in pandas
    # This ensures that the function handles invalid date formats gracefully without raising errors.
    # to_datetime is a pandas function that converts a pandas Series or array-like object to datetime format.
    return pd.to_datetime(s, errors="coerce")

def _validate_columns(df: pd.DataFrame, cm: ColumnMap) -> None:
    # Stores a list of columns names as defined in the ColumnMap instance cm
    required = [cm.service_col, cm.region_col, cm.satisfied_col, cm.recommend_col]
    # Checks if any required columns are missing from the DataFrame df
    missing = [c for c in required if c not in df.columns]
    # If there are missing columns, it raises a KeyError with a message listing the missing columns and the available columns in the DataFrame
    if missing:
        raise KeyError(f"Missing required columns {missing}. Available: {list(df.columns)}")

def clean_df(df: pd.DataFrame, cm: ColumnMap) -> pd.DataFrame:
    # Before cleaning it validates the number of columns in the dataframe
    _validate_columns(df, cm)
    # Make a copy to avoid modifying original
    df = df.copy()

    df[cm.service_col] = _normalize_text(df[cm.service_col])
    df[cm.region_col] = _normalize_text(df[cm.region_col])

    
    df[cm.satisfied_col] = _normalize_yes_no(df[cm.satisfied_col])
    df[cm.recommend_col] = _normalize_yes_no(df[cm.recommend_col])

    if cm.date_col and cm.date_col in df.columns:
        df[cm.date_col] = _parse_date_safe(df[cm.date_col])

    # Drop rows missing key fields
    df = df.dropna(subset=[cm.service_col, cm.region_col, cm.satisfied_col, cm.recommend_col])

    # Remove empties after normalization
    df = df[
        (df[cm.service_col].astype("string").srt.len() > 0) &
        (df[cm.region_col].astype("string").str.len() > 0)
    ]

    return df

def dedupe_df(df: pd.DataFrame, cm: ColumnMap) -> pd.DataFrame:# Accepts a DataFrame as df and a ColumnMap as cm and then returns a DataFrame
    df = df.copy() # Creates a copy to aviod editing the original

    # Dedupe logic
    # If respondent_id_col is defined in cm and exists in the dataframe columns
    # it checks if date_col is also defined and exists in the dataframe columns
    # If both conditions are met, it drops duplicates based on respondent_id_col and date_col
    if cm.respondent_id_col and cm.respondent_id_col in df.columns:
        # If date_col is defined and exists in the dataframe columns
        # Returns a DataFrame with duplicates dropped based on respondent_id_col and date_col, keeping the last occurrence
        # keeping the last occurence means that if there are multiple entries for the same respondent_id and date, only the most recent one is retained
        # subset= specifies the columns to consider for identifying duplicates
        # An entire row is removed if the values in these columns are the same as another row
        if cm.date_col and cm.date_col in df.columns:
            return df.drop_duplicates(subset=[cm.respondent_id_col, cm.date_col], keep="last")
        # If date_col is not defined or does not exist in the dataframe columns
        # it drops duplicates based only on respondent_id_col
        return df.drop_duplicates(subset=[cm.respondent_id_col], keep="last")
    
    subset = [cm.service_col, cm.region_col, cm.satisfied_col, cm.recommend_col]
    if cm.date_col and cm.date_col in df.columns:
        subset = [cm.date_col] + subset

    return df.drop_duplicates(subset=subset, keep="last")

# Process multiple files
# It accepts a list of path objects from pipe.py and a ColumnMap instance from config.py
def process_files(paths: List[Path], cm: ColumnMap) -> ProcessResult:
    cleaned_frames: List[pd.DataFrame] = []
    summaries: List[dict] = []

    for p in paths:
        raw = _read_any(p)
        
        raw_rows, raw_cols = int(raw.shape[0]), int(raw.shape[1])
                                 
        # Clean and dedupe
        # First, clean the dataframe using the clean_df function, which normalizes text fields, converts yes/no fields to boolean, parses dates, and drops rows with missing key fields.
        # Then, deduplicate the cleaned dataframe using the dedupe_df function, which removes duplicate entries based on respondent ID and date or other key fields.
        cleaned = clean_df(raw, cm)
        cleaned = dedupe_df(cleaned, cm)


        summaries.append({
            "filename": p.name, # strips the file directory and leave only the name of the file and stores the result in a dictionary value paired with key "filename"
            "raw_rows": raw_rows, # stores the number of rows calculated earlier
            "raw_cols": raw_cols, # stores the number of columns calculated earlier
            "clean_rows": int(cleaned.shape[0]), # stores the number of rows in the cleaned dataframe
            "clean_cols": int(cleaned.shape[1]), # stores the number of columns in the cleaned dataframe
        })

        cleaned_frames.append(cleaned) # Append the cleaned dataframe to the cleaned_frames list for later concatenation
        logger.info("Processed %s (raw_rows=%s clean_rows=%s)", p.name, raw_rows, int(cleaned.shape[0]))
    # Combines the data frames into one 
    # "if cleaned_frames else pd.DataFrame()" ensures that if there are no cleaned frames, an empty DataFrame is returned instead of causing an error.
    combined = pd.concat(cleaned_frames, ignore_index=True) if cleaned_frames else pd.DataFrame()
    file_summaries = pd.DataFrame(summaries) # Create a DataFrame from the list of summary dictionaries for easier analysis and reporting

    # Final dedupe across files (important!)
    if not combined.empty: # only dedupe if there is data
        combined = dedupe_df(combined, cm)

    # Return the combined cleaned DataFrame and the file summaries as a ProcessResult object
    return ProcessResult(combined=combined, file_summaries=file_summaries)  
