import requests
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://factpages.sodir.no/public?/Factpages/external/tableview/"
PARAMS = "&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false"

DATASETS = {
    # Wellbore
    "wellbore_all": "wellbore_all_long",

    # Field
    "field_overview": "field",
    "field_status": "field_activity_status_hst",
    "field_pdo": "field_pdo_hst",
    "field_operators": "field_operator_hst",
    "field_licencees": "field_licensee_hst",
    "field_prod_sale_mth": "field_production_monthly",
    "field_prod_sale_year": "field_production_yearly",
    "field_reserves": "field_reserves"
}

def fetch_dataset(name, table):
    url = f"{BASE_URL}{table}{PARAMS}"
    logger.info(f"Fetching {name}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        filepath = f"data/bronze/{name}.csv"
        with open(filepath, "wb") as f:
            f.write(response.content)
        logger.info(f"Saved {filepath}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed {name}: {e}")

if __name__ == "__main__":
    os.makedirs("data/bronze", exist_ok=True)
    logger.info("Starting SODIR bronze ingestion...")
    for name, table in DATASETS.items():
        fetch_dataset(name, table)
    logger.info("Bronze ingestion complete.")