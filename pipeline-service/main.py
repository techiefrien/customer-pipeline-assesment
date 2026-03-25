from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models.customer import Customer
from services.ingestion import run_ingestion_pipeline

app = FastAPI(title="Customer Pipeline Service")

Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "pipeline-service"}


@app.post("/api/ingest")
def ingest_customers():
    try:
        records = run_ingestion_pipeline()
        return {"status": "success", "records_processed": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers")
def get_customers(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()
    total = db.query(Customer).count()

    return {
        "data": [
            {
                "customer_id":     c.customer_id,
                "first_name":      c.first_name,
                "last_name":       c.last_name,
                "email":           c.email,
                "phone":           c.phone,
                "address":         c.address,
                "date_of_birth":   str(c.date_of_birth),
                "account_balance": float(c.account_balance),
                "created_at":      str(c.created_at),
            }
            for c in customers
        ],
        "total": total,
        "page": page,
        "limit": limit
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    return {
        "data": {
            "customer_id":     customer.customer_id,
            "first_name":      customer.first_name,
            "last_name":       customer.last_name,
            "email":           customer.email,
            "phone":           customer.phone,
            "address":         customer.address,
            "date_of_birth":   str(customer.date_of_birth),
            "account_balance": float(customer.account_balance),
            "created_at":      str(customer.created_at),
        }
    }