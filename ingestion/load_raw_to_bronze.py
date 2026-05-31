"""
load_raw_to_bronze.py
---------------------
Loads raw SODIR CSV files from data/raw into SQLite database as bronze tables.

This is the second pipeline step (raw files -> bronze tables). It still performs no
transformation - the bronze tables are a copy of the raw CSV files.

Each run fully replaces the bronze tables (idempotent).

NOTE: the dataset list is mirrored in fetch_sodir.py and in transform/sodir_dbt/models/sources.yml. 
"""

import os
import logging
import sqlite3
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DB_PATH = "data/sodir.db"
RAW_DIR = "data/raw"

# Raw datasets to load. Each becomes a table named bronze_<name>.
DATASETS = [
    "wellbore_all",
    "field_overview",
    "field_status",
    "field_pdo",
    "field_operators",
    "field_licencees",
    "field_prod_sale_mth",
    "field_prod_sale_year",
    "field_reserves",
]

def load_csv_to_db(name: str, conn: sqlite3.Connection) -> bool:
    """
    Load one raw CSV into the database as bronze_<name> table
    
    Replaces the table if it already exists, so each run is a clean rebuild.
    Returns True on success, False if the file is missing.
    """
    filepath = os.path.join(RAW_DIR, f"{name}.csv")
    if not os.path.exists(filepath):
        logger.warning(f"File not found, skipping: {filepath}")
        return False
    
    table_name = f"bronze_{name}"
    logger.info(f"Loading {name}...")

    df = pd.read_csv(filepath, low_memory=False)
    df.to_sql(table_name, conn, if_exists="replace", index=False)

    logger.info(f"Loaded {len(df)} rows into table '{table_name}'")
    return True

if __name__ == "__main__":
    logger.info("Starting raw -> bronze load...")

    conn = sqlite3.connect(DB_PATH)
    try:
        succeeded = sum(load_csv_to_db(name, conn) for name in DATASETS)
    finally:
        # Always close the connection, even if a load raises.
        conn.close()

    total = len(DATASETS)
    logger.info(f"Bronze load complete: {succeeded}/{total} tables loaded.")