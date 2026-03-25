# Customer Data Pipeline

A 3-service data pipeline built with Flask, FastAPI, PostgreSQL, and Docker.

## Services
- **mock-server** (port 5000) — Flask REST API serving customer data from JSON
- **pipeline-service** (port 8000) — FastAPI service that ingests data into PostgreSQL using dlt
- **postgres** (port 5432) — PostgreSQL database

## Prerequisites
- Docker Desktop
- Git

## How to Run
```bash
docker-compose up --build
```

## Test the Pipeline
```bash
# Health checks
curl http://localhost:5000/api/health
curl http://localhost:8000/api/health

# Flask — get customers
curl "http://localhost:5000/api/customers?page=1&limit=5"

# Ingest data from Flask into PostgreSQL
curl -X POST http://localhost:8000/api/ingest

# FastAPI — query from PostgreSQL
curl "http://localhost:8000/api/customers?page=1&limit=5"
curl http://localhost:8000/api/customers/CUST001
```

## Project Structure
```
customer-pipeline/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── database.py
    ├── models/customer.py
    ├── services/ingestion.py
    ├── Dockerfile
    └── requirements.txt
```