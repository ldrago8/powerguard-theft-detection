"""FastAPI backend for Cloud-Based Electricity Theft Detection System."""

import json
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import joblib
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.database import (
    autocomplete_search,
    get_analytics,
    get_consumer_by_id,
    get_prediction_history,
    import_csv_if_needed,
    init_database,
    save_prediction,
    search_consumers,
)
from backend.cloud_concepts import get_course_cloud_concepts, get_deployment_status, get_full_cloud_report
from ml.preprocess import CATEGORICAL_COLUMNS, FEATURE_COLUMNS, record_to_feature_row

MODEL_PATH = ROOT / "ml" / "artifacts" / "theft_detection_model.pkl"
METRICS_PATH = ROOT / "ml" / "artifacts" / "model_metrics.json"
COMPARISON_PATH = ROOT / "ml" / "artifacts" / "model_comparison.json"
DATASET_PATH = ROOT / "data" / "electricity_consumption.csv"
STATIC_DIR = ROOT / "frontend" / "static"

model = None
metrics_cache: dict[str, Any] = {}


class ConsumerRecord(BaseModel):
    consumer_id: str
    region: str
    connection_type: str = "Residential"
    meter_type: str = "Digital"
    payment_status: str = "Paid"
    monthly_consumption: float = Field(..., ge=0)
    previous_month_consumption: float = Field(..., ge=0)
    billing_amount: float = Field(..., ge=0)
    area_average_consumption: float = Field(..., ge=0)
    meter_reading_difference: float
    peak_load_kw: float = Field(default=3.5, ge=0)
    power_factor: float = Field(default=0.92, ge=0, le=1)
    sanctioned_load_kw: float = Field(default=5.0, ge=0)
    outstanding_balance: float = Field(default=0.0, ge=0)


def load_model() -> None:
    global model, metrics_cache
    if not MODEL_PATH.exists():
        from ml.train_model import main as train_main

        train_main()
    model = joblib.load(MODEL_PATH)
    if METRICS_PATH.exists():
        metrics_cache = json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def analyze_risk_factors(record: dict, prediction: str) -> list[dict]:
    factors = []
    area_avg = record["area_average_consumption"]
    monthly = record["monthly_consumption"]

    if monthly < area_avg * 0.55:
        factors.append({"factor": "Low consumption vs area average", "severity": "high", "detail": f"{monthly:.0f} units vs {area_avg:.0f} area avg"})
    if record["meter_reading_difference"] < -30:
        factors.append({"factor": "Abnormal meter reading gap", "severity": "high", "detail": f"Difference: {record['meter_reading_difference']:.1f} units"})
    if record["billing_amount"] < monthly * 12:
        factors.append({"factor": "Billing amount unusually low", "severity": "medium", "detail": f"PKR {record['billing_amount']:.0f} for {monthly:.0f} units"})
    if record.get("payment_status") in ("Overdue", "Partial"):
        factors.append({"factor": "Payment irregularity", "severity": "medium", "detail": f"Status: {record.get('payment_status')}"})
    if record.get("outstanding_balance", 0) > 5000:
        factors.append({"factor": "High outstanding balance", "severity": "medium", "detail": f"PKR {record['outstanding_balance']:.0f} pending"})
    if record.get("power_factor", 1) < 0.85:
        factors.append({"factor": "Low power factor", "severity": "low", "detail": f"Power factor: {record.get('power_factor')}"})

    if not factors and prediction == "Normal":
        factors.append({"factor": "Consumption pattern within normal range", "severity": "info", "detail": "No significant anomalies detected"})
    elif not factors:
        factors.append({"factor": "Combined pattern analysis", "severity": "medium", "detail": "Multiple subtle indicators flagged by ML model"})

    return factors


def run_prediction(record: dict, persist: bool = True) -> dict:
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    feature_row = record_to_feature_row(record)
    feature_df = pd.DataFrame([{k: feature_row.get(k) for k in FEATURE_COLUMNS + CATEGORICAL_COLUMNS}])

    prediction = model.predict(feature_df)[0]
    probabilities = model.predict_proba(feature_df)[0]
    label = "Theft" if prediction == 1 else "Normal"
    confidence = float(max(probabilities) * 100)
    risk_level = (
        "Critical" if label == "Theft" and confidence >= 90
        else "High" if label == "Theft" and confidence >= 75
        else "Medium" if label == "Theft"
        else "Low"
    )

    if persist:
        save_prediction(
            record["consumer_id"],
            record.get("region", "Unknown"),
            label,
            round(confidence, 2),
            risk_level,
            datetime.now(timezone.utc).isoformat(),
        )

    return {
        "prediction": label,
        "confidence": round(confidence, 2),
        "risk_level": risk_level,
        "probability_normal": round(float(probabilities[0]) * 100, 2),
        "probability_theft": round(float(probabilities[1]) * 100, 2),
        "risk_factors": analyze_risk_factors(record, label),
        "model_used": metrics_cache.get("model", "random_forest"),
    }


def build_consumer_response(consumer: dict) -> dict:
    months = ["Jun 2025", "May 2025", "Apr 2025", "Mar 2025", "Feb 2025", "Jan 2025"]
    consumption_history = [
        {"month": months[0], "units": consumer["monthly_consumption"]},
        {"month": months[1], "units": consumer["previous_month_consumption"]},
        {"month": months[2], "units": consumer["consumption_month_3"]},
        {"month": months[3], "units": consumer["consumption_month_4"]},
        {"month": months[4], "units": consumer["consumption_month_5"]},
        {"month": months[5], "units": consumer["consumption_month_6"]},
    ]

    ml_result = run_prediction(consumer, persist=True)
    actual_label = consumer["label"]
    model_match = ml_result["prediction"] == actual_label

    return {
        "profile": {
            "consumer_id": consumer["consumer_id"],
            "full_name": consumer["full_name"],
            "cnic": consumer["cnic"],
            "phone": consumer["phone"],
            "email": consumer["email"],
            "address": consumer["address"],
            "city": consumer["city"],
            "region": consumer["region"],
            "distribution_company": consumer["distribution_company"],
            "meter_number": consumer["meter_number"],
            "meter_type": consumer["meter_type"],
            "connection_type": consumer["connection_type"],
            "tariff_category": consumer["tariff_category"],
            "account_status": consumer["account_status"],
            "registration_date": consumer["registration_date"],
            "sanctioned_load_kw": consumer["sanctioned_load_kw"],
            "payment_status": consumer["payment_status"],
            "outstanding_balance": consumer["outstanding_balance"],
        },
        "consumption": {
            "monthly_consumption": consumer["monthly_consumption"],
            "previous_month_consumption": consumer["previous_month_consumption"],
            "consumption_change": consumer["consumption_change"],
            "area_average_consumption": consumer["area_average_consumption"],
            "usage_vs_area_average": consumer["usage_vs_area_average"],
            "peak_load_kw": consumer["peak_load_kw"],
            "power_factor": consumer["power_factor"],
            "meter_reading_difference": consumer["meter_reading_difference"],
            "history": consumption_history,
        },
        "billing": {
            "current_bill": consumer["billing_amount"],
            "previous_bill": consumer["previous_billing_amount"],
            "bill_change": round(consumer["billing_amount"] - consumer["previous_billing_amount"], 2),
            "payment_status": consumer["payment_status"],
            "outstanding_balance": consumer["outstanding_balance"],
            "tariff_category": consumer["tariff_category"],
        },
        "detection": {
            **ml_result,
            "actual_label": actual_label,
            "model_match": model_match,
        },
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    if not DATASET_PATH.exists():
        from data.generate_dataset import main as generate_main

        generate_main()
    imported = import_csv_if_needed()
    print(f"Database ready with {imported:,} consumer records")
    load_model()
    yield


app = FastAPI(
    title="Cloud-Based Electricity Theft Detection System",
    description="Enterprise ML platform for detecting abnormal electricity consumption",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    analytics = get_analytics()
    deployment = get_deployment_status()
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "consumers_in_database": analytics["total_consumers"],
        "version": "3.0.0",
        "environment": deployment["environment"],
        "platform": deployment["platform"],
        "service_url": deployment["service_url"],
    }


@app.get("/api/metrics")
def get_metrics():
    if not metrics_cache:
        raise HTTPException(status_code=404, detail="Metrics not available")
    return metrics_cache


@app.get("/api/comparison")
def get_comparison():
    if not COMPARISON_PATH.exists():
        raise HTTPException(status_code=404, detail="Model comparison not available")
    return json.loads(COMPARISON_PATH.read_text(encoding="utf-8"))


@app.get("/api/analytics")
def analytics():
    return get_analytics()


@app.get("/api/dataset/stats")
def get_dataset_stats():
    return get_analytics()


@app.get("/api/consumers/search")
def consumers_search(
    q: str = Query(default="", description="Search by ID, name, meter, CNIC, phone"),
    region: str | None = None,
    label: str | None = None,
    connection_type: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=5, le=100),
):
    return search_consumers(q, region, label, connection_type, page, page_size)


@app.get("/api/search/autocomplete")
def search_autocomplete(
    q: str = Query(..., min_length=1, description="Search query"),
    type: str = Query(default="all", alias="type", description="id|name|cnic|meter|phone|all"),
    limit: int = Query(default=12, ge=1, le=30),
):
    results = autocomplete_search(q, type, limit)
    return {"query": q, "search_type": type, "count": len(results), "results": results}


@app.get("/api/system/cloud")
def cloud_architecture():
    from backend.system_info import get_cloud_architecture
    return {
        **get_cloud_architecture(),
        "deployment": get_deployment_status(),
        "course_concepts": get_course_cloud_concepts()["sections"],
    }


@app.get("/api/system/cloud/concepts")
def cloud_concepts_full():
    return get_full_cloud_report()


@app.get("/api/system/data")
def data_management():
    from backend.system_info import get_data_pipeline
    return get_data_pipeline()


@app.get("/api/system/storage")
def storage_stats():
    from backend.system_info import get_storage_stats
    return get_storage_stats()


@app.get("/api/consumers/{consumer_id}")
def get_consumer(consumer_id: str):
    consumer = get_consumer_by_id(consumer_id)
    if not consumer:
        raise HTTPException(status_code=404, detail=f"Consumer '{consumer_id}' not found")
    return build_consumer_response(consumer)


@app.get("/api/predictions/history")
def prediction_history(limit: int = Query(default=50, ge=1, le=200)):
    return get_prediction_history(limit)


@app.post("/api/predict")
def predict_single(record: ConsumerRecord):
    result = run_prediction(record.model_dump(), persist=True)
    return {"consumer_id": record.consumer_id, **result}


@app.post("/api/predict/batch")
async def predict_batch(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    df = pd.read_csv(pd.io.common.BytesIO(content))
    required = ["consumer_id", "region", "monthly_consumption", "previous_month_consumption",
                "billing_amount", "area_average_consumption", "meter_reading_difference"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    results = []
    for _, row in df.iterrows():
        data = row.to_dict()
        for col in FEATURE_COLUMNS + CATEGORICAL_COLUMNS:
            if col not in data:
                data[col] = {"connection_type": "Residential", "meter_type": "Digital",
                             "payment_status": "Paid", "peak_load_kw": 3.5, "power_factor": 0.92,
                             "sanctioned_load_kw": 5.0, "outstanding_balance": 0.0}.get(col, 0)
        pred = run_prediction(data, persist=True)
        results.append({"consumer_id": data["consumer_id"], **pred})

    theft_count = sum(1 for r in results if r["prediction"] == "Theft")
    return {
        "total_processed": len(results),
        "theft_detected": theft_count,
        "normal_detected": len(results) - theft_count,
        "results": results,
    }


@app.get("/api/download/dataset")
def download_dataset():
    if not DATASET_PATH.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    return FileResponse(DATASET_PATH, filename="electricity_consumption.csv")


if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
