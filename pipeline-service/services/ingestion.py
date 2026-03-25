import os
import httpx
import dlt
from dlt.sources.helpers import requests as dlt_requests
from datetime import datetime , date


MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://localhost:5000")

def fetch_all_customers():
    all_customers = []
    page = 1
    limit = 10

    while True:
        url = f"{MOCK_SERVER_URL}/api/customers?page={page}&limit={limit}"
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        customers = data.get("data", [])
        all_customers.extend(customers)

        total = data.get("total", 0)
        if len(all_customers) >= total or len(customers) == 0:
            break

        page += 1

    return all_customers

def parse_customer(customer):
    if customer.get("date_of_birth"):
        customer["date_of_birth"] = datetime.strptime(
            customer["date_of_birth"], "%Y-%m-%d"
        ).date().isoformat()

    if customer.get("created_at"):
        customer["created_at"] = datetime.strptime(
            customer["created_at"], "%Y-%m-%dT%H:%M:%S"
        ).isoformat()

    if customer.get("account_balance") is not None:
        customer["account_balance"] = float(customer["account_balance"])

    return customer

@dlt.resource(
    name="customers",
    write_disposition="merge",
    primary_key="customer_id",
    columns={
        "date_of_birth": {"data_type": "date"},
        "created_at":    {"data_type": "timestamp"},
        "account_balance": {"data_type": "decimal"}
    }
)
def customers_resource():
    data = fetch_all_customers()
    for customer in data:
        yield parse_customer(customer)


def run_ingestion_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="customer_pipeline",
        destination=dlt.destinations.postgres(
            os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/customer_db")
        ),
        dataset_name="public"
    )

    load_info = pipeline.run(customers_resource())

    # check if dlt had any errors during loading
    if load_info.has_failed_jobs:
        error_messages = []
        for package in load_info.load_packages:
            for job in package.jobs.get("failed_jobs", []):
                error_messages.append(str(job.failed_message))
        raise Exception(f"dlt pipeline failed: {'; '.join(error_messages)}")

    records = len(fetch_all_customers())
    return records