# Weekly Auto-Reporting System (Week 7 Capstone)

This project ingests survey files from `data/inbox`, cleans + deduplicates them, computes KPIs, writes reports to `output/`, archives inputs, and can email results with attachments.

## 1) Setup

Create folders:
- data/inbox
- data/processed
- data/failed
- output
- logs

Put your input files into `data/inbox` (CSV/XLSX/JSON).

Edit `config.json` to match your column names.

Install dependencies:
- pandas
- openpyxl (needed for Excel)

## 2) Run manually

```bash
python run_weekly_report.py --config config.json
