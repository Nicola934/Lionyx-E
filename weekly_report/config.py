from __future__ import annotations # Enable postponed evaluation of annotations for compatibility with older Python versions.

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass(frozen=True)
class ColumnMap:
    service_col: str # name of the column for service
    region_col: str # name of the column for region
    satisfied_col: str # name of the column for satisfied
    recommend_col: str # name of the column for recommend
    date_col: Optional[str] = None # name of the column for date (optional)
    respondent_id_col: Optional[str] = None # name of the column for respondent ID (optional)

@dataclass(frozen=True)
class EmailConfig:
    enabled: bool # whether email sending is enabled
    smtp_host: str # SMTP server hostname
    smtp_port: int # SMTP server port
    use_starttls: bool # whether to use STARTTLS for secure connection
    from_addr: str # sender email address
    to_addrs: List[str] # list of recipient email addresses
    subject_prefix: str # prefix for the email subject line

@dataclass(frozen=True)
class AppConfig:
    inbox_dir: Path # Path to the inbox directory
    processed_dir: Path # Path to the processed files directory
    failed_dir: Path # Path to the failed files directory
    output_dir: Path # Path to the output directory
    log_dir: Path # Path to the log directory

    input_globs: List[str] # List of glob patterns for input files

    report_basename: str # Base name for report files
    write_cleaned_csv: bool # Whether to write cleaned CSV files
    write_kpi_json: bool # Whether to write KPI JSON files

    # It holds the column mapping settings from the JSON file stored as a ColumnMap dataclass instance.
    column_map: ColumnMap # Mapping of column names
    # It holds the email configuration settings from the JSON file stored as an EmailConfig dataclass instance.
    email: EmailConfig # Email configuration


    # It is a method that reads a JSON configuration file from the specified path and constructs an AppConfig
    #  instance based on the contents of the file.
    @staticmethod # type: ignore
    def from_json(path: Path) -> "AppConfig":

        # Load the JSON content from the specified file path
        raw: Dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))

        # Load column_map and email configurations from the raw JSON data
        cm = raw["column_map"] # Column_map is a JSON inside the main JSON containing the column mapping settings.
        email = raw["email"] # email is also a JSON inside the main JSON containing the email settings.

        return AppConfig(
            inbox_dir=Path(raw["inbox_dir"]), # Path to the inbox directory
            processed_dir=Path(raw["processed_dir"]), # Path to the processed directory
            failed_dir=Path(raw["failed_dir"]), # Path to the failed directory
            output_dir=Path(raw["output_dir"]), # Path to output directory
            log_dir=Path(raw["log_dir"]), # Path to the log directory

            input_globs=list(raw.get("input_globs", ["*.csv"])), # List of glob patterns for input files which are [".csv", "*.xlsx", "*.json"]

            report_basename=str(raw.get("report_basename", "weekly_report")), # Base name for report files
            write_cleaned_csv=bool(raw.get("write_cleaned_csv", True)), # Whether to write cleaned CSV files
            write_kpi_json=bool(raw.get("write_kpi_json", True)), # Whether to write KPI JSON files

            column_map=ColumnMap(
                service_col=cm["service_col"], # name of the column for service
                region_col=cm["region_col"], # name of the column for region
                recommend_col=cm["recommend_col"], # name of the column for recommend
                satisfied_col=cm["satisfied_col"], # name of the column for satisfied
                date_col=cm.get("date_col"), # name of the column for date (optional)
                respondent_id_col=cm.get("respondent_id_col"), # name of the column for respondent ID (optional)
            ),

            email=EmailConfig(
                # bool() converts the value to a boolean type
                # .get() retrieves the value associated with the "enabled" key from the email dictionary. 
                # If the key is not present, it returns False by default.
                enabled=bool(email.get("enabled", False)),# whether email sending is enabled
                smtp_host=str(email["smtp_host"]), # SMTP server hostname
                smtp_port=int(email["smtp_port"]), # SMTP server port
                use_starttls=bool(email.get("use_starttls", True)), # whether to use STARTTLS for secure connection return True by default if the key is not present
                from_addr=str(email["from_addr"]), # sender email address example: "<EMAIL>"
                to_addrs=list(email["to_addrs"]), # list of recipient email addresses example: ["<EMAIL>"]
                subject_prefix=str(email.get("subject_prefix", "[Weekly Report]")), # prefix for the email subject line example: [Weekly Report]
            ),
        )
    def ensure_dirs(self) -> None:
        for p in [self.inbox_dir, self.processed_dir, self.failed_dir, self.output_dir, self.log_dir]:
            p.mkdir(parents=True, exist_ok=True) # creates the listed directories if they do not already exist
