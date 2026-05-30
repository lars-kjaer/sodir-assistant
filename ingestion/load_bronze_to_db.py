import pandas as pd
import sqlite3
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data/sodir.db"
BRONZE_PATH = "data/bronze"

DATASETS = [
    "wellbore_all",
    "field_overview",
    "field_status",
    "field_pdo",
    "field_operators",
    "field_licencees",
    "field_prod_sale_mth",
    "field_prod_sale_year",
    "field_reserves"
]

def load_csv_to_db(name, conn):
    filepath = f"{BRONZE_PATH}/{name}.csv"
    if not os.path.exists(filepath):
        logger.warning(f"File not found,skipping: {filepath}")
        return
    logger.info(f"Loading {name}...")
    df = pd.read_csv(filepath, low_memory=False)
    df.to_sql(name, conn, if_exists="replace", index=False)
    logger.info(f"Loaded {len(df)} rows into table '{name}'")

if __name__ == "__main__":
    logger.info("Connecting to SQLite database...")
    conn = sqlite3.connect(DB_PATH)
    for name in DATASETS:
        load_csv_to_db(name, conn)
    conn.close()
    logger.info("Bronze load complete.")