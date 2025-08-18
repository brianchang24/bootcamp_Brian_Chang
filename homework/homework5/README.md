## Data Storage (Stage 05)

- **Folders**: `data/raw/` holds timestamped CSV snapshots (unaltered). `data/processed/` holds Parquet files after minimal processing.
- **Formats**: CSV for portability; Parquet for efficient, typed storage and faster IO.
- **Env paths**: `.env` defines `DATA_DIR_RAW` and `DATA_DIR_PROCESSED`. Code reads these with `dotenv` so paths don’t need hardcoding.
- **Utilities**: `write_df` / `read_df` route by file suffix (`.csv` / `.parquet`) and handle missing directories and Parquet engine hints.
