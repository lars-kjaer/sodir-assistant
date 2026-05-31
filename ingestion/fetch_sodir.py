"""
fetch_sodir.py
--------------
Raw file ingestion:
- Downloads raw .csv datasets from SODIR factpages
- Writes files to data/raw unchanged

This is the first step of the pipeline. It performs no transformations.

NOTE: the dataset list is mirrored in transform/sodir_dbt/models/sources.yml. If adding/renaming dataset update both.
"""

import os
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Sodir factpages serve tables as CSV files via a fixed URL pattern:
# BASE_URL + <table name> + PARAMS. Only table name varies

BASE_URL = "https://factpages.sodir.no/public?/Factpages/external/tableview/"

PARAMS = (
    "&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f"
    "&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false"    
)

RAW_DIR = "data/raw"

DATASETS = {
    # Wellbore information
    "wellbore_all": "wellbore_all_long",

    # Field information
    "field_overview": "field",
    "field_status": "field_activity_status_hst",
    "field_pdo": "field_pdo_hst",
    "field_operators": "field_operator_hst",
    "field_licencees": "field_licensee_hst",
    "field_prod_sale_mth": "field_production_monthly",
    "field_prod_sale_year": "field_production_yearly",
    "field_reserves": "field_reserves",
}

def fetch_dataset(name: str, table: str) -> bool:
    """
    Download single SODIR dataset to raw directory
    
    Returns True on success, False on failure. Failures logged but not raised.
    """

    url = f"{BASE_URL}{table}{PARAMS}"
    logger.info(f"Fetching {name}...")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed {name}: {e}")
        return False
    
    filepath = os.path.join(RAW_DIR, f"{name}.csv")
    with open(filepath, "wb") as f:
        f.write(response.content)
    logger.info(f"Saved {filepath}...")
    return True

if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    logger.info("Starting SODIR raw file ingestion.")

    succeeded = sum(fetch_dataset(name, table) for name, table in DATASETS.items())
    total = len(DATASETS)

    logger.info(f"SODIR raw file ingestion complete: {succeeded}/{total} datasets fetched.")