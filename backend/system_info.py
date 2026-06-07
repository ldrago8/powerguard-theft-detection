"""System storage statistics for data management dashboard."""

from pathlib import Path

from backend.database import DB_PATH, DATASET_PATH, get_connection

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "ml" / "artifacts" / "theft_detection_model.pkl"
METRICS_PATH = ROOT / "ml" / "artifacts" / "model_metrics.json"


def _file_size_mb(path: Path) -> float:
    if path.exists():
        return round(path.stat().st_size / (1024 * 1024), 2)
    return 0.0


def get_storage_stats() -> dict:
    with get_connection() as conn:
        consumer_count = conn.execute("SELECT COUNT(*) FROM consumers").fetchone()[0]
        prediction_count = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        theft_count = conn.execute("SELECT COUNT(*) FROM consumers WHERE label = 'Theft'").fetchone()[0]

    return {
        "consumer_records": consumer_count,
        "prediction_logs": prediction_count,
        "theft_records": theft_count,
        "dataset_file_mb": _file_size_mb(DATASET_PATH),
        "database_file_mb": _file_size_mb(DB_PATH),
        "model_file_mb": _file_size_mb(MODEL_PATH),
        "total_storage_mb": round(
            _file_size_mb(DATASET_PATH) + _file_size_mb(DB_PATH) + _file_size_mb(MODEL_PATH),
            2,
        ),
        "dataset_columns": 33,
        "dataset_path": "data/electricity_consumption.csv",
        "database_path": str(DB_PATH),
        "model_path": "ml/artifacts/theft_detection_model.pkl",
    }


def get_cloud_architecture() -> dict:
    return {
        "platform": "Hugging Face Spaces (Free, No Card) / Render / Docker",
        "deployment_model": "Containerized cloud deployment",
        "services": [
            {
                "name": "Cloud Compute",
                "icon": "cpu",
                "technology": "Render Web Service / Docker Container",
                "role": "Hosts the FastAPI backend, runs ML inference in real-time, processes batch uploads",
                "local_equivalent": "Uvicorn server on port 8000",
                "scalability": "Auto-scales on paid tiers; handles 15K+ records efficiently",
            },
            {
                "name": "Cloud Storage",
                "icon": "storage",
                "technology": "Persistent Disk / Object Storage (S3-compatible)",
                "role": "Stores the 4.5 MB CSV dataset, trained ML model (.pkl), and system artifacts",
                "local_equivalent": "data/ and ml/artifacts/ folders",
                "scalability": "Supports millions of consumer records with cloud object storage",
            },
            {
                "name": "Cloud Database",
                "icon": "database",
                "technology": "SQLite (local) → PostgreSQL (cloud production)",
                "role": "Indexes 15,000 consumer profiles for instant search; logs all theft predictions",
                "local_equivalent": "storage/consumers.db",
                "scalability": "PostgreSQL on Render handles concurrent queries from multiple users",
            },
            {
                "name": "ML Engine",
                "icon": "brain",
                "technology": "Scikit-learn on Cloud Compute",
                "role": "Decision Tree, Random Forest, Logistic Regression — trained on cloud compute, deployed for inference",
                "local_equivalent": "ml/train_model.py + theft_detection_model.pkl",
                "scalability": "Model retraining on larger datasets using cloud GPU/compute",
            },
            {
                "name": "Web Frontend",
                "icon": "web",
                "technology": "Static files served via FastAPI / CDN",
                "role": "Dashboard, search, analytics UI — accessible remotely by electricity companies",
                "local_equivalent": "frontend/static/",
                "scalability": "CDN distribution for global access (WAPDA, K-Electric regional offices)",
            },
            {
                "name": "API Gateway",
                "icon": "api",
                "technology": "FastAPI REST API",
                "role": "REST endpoints for search, prediction, analytics — enables integration with billing systems",
                "local_equivalent": "backend/app.py — 12+ API endpoints",
                "scalability": "Rate limiting and load balancing on cloud platforms",
            },
        ],
        "benefits": [
            "Large-scale data storage for millions of consumers across Pakistan",
            "High computational power for ML model training and real-time inference",
            "Remote access for WAPDA, K-Electric, LESCO regional offices",
            "Scalable architecture — add regions without hardware changes",
            "99.9% uptime with cloud hosting vs local machine dependency",
        ],
        "supported_providers": ["Hugging Face Spaces", "Render.com", "AWS (EC2 + S3 + RDS)", "Google Cloud Run", "Microsoft Azure App Service"],
    }


def get_data_pipeline() -> dict:
    stats = get_storage_stats()
    return {
        "overview": "Electricity consumption data flows through 5 stages: Collection → Storage → Processing → ML Analysis → Detection Output",
        "stages": [
            {
                "step": 1,
                "title": "Data Collection",
                "description": "Electricity consumption records collected from smart meters, billing systems, and distribution companies (IESCO, K-Electric, LESCO, etc.)",
                "source": "Smart Meters + Billing Systems + Simulated Dataset Generator",
                "output": f"{stats['consumer_records']:,} consumer records with 33 attributes",
                "fields": ["Consumer ID", "CNIC", "Meter Number", "6-month consumption", "Billing", "Region"],
            },
            {
                "step": 2,
                "title": "Cloud Storage",
                "description": "Raw CSV dataset stored in cloud-accessible storage. Locally stored as electricity_consumption.csv (4.5 MB), deployable to S3/Render disk.",
                "source": "data/electricity_consumption.csv",
                "output": f"{stats['dataset_file_mb']} MB CSV file with {stats['consumer_records']:,} rows",
                "fields": ["Persistent file storage", "Version controlled", "Downloadable via API"],
            },
            {
                "step": 3,
                "title": "Database Indexing",
                "description": "CSV imported into SQLite/PostgreSQL cloud database with indexed columns for instant search by ID, name, CNIC, meter number, region.",
                "source": "CSV → SQLite import on startup",
                "output": f"{stats['database_file_mb']} MB indexed database, {stats['consumer_records']:,} searchable records",
                "fields": ["Indexed: consumer_id, full_name, meter_number, cnic, region, label"],
            },
            {
                "step": 4,
                "title": "ML Processing",
                "description": "Scikit-learn pipeline: feature extraction → standardization → model inference. Three models compared; best model deployed.",
                "source": "11 numeric + 4 categorical features per consumer",
                "output": f"{stats['model_file_mb']} MB trained model (Logistic Regression / Random Forest / Decision Tree)",
                "fields": ["Accuracy ~99%", "Precision, Recall, F1-Score tracked", "Confusion matrix logged"],
            },
            {
                "step": 5,
                "title": "Detection & Logging",
                "description": "Each search/prediction logged to cloud database. Results shown on dashboard with risk factors, confidence scores, and consumption charts.",
                "source": "Real-time API inference",
                "output": f"{stats['prediction_logs']} predictions logged so far",
                "fields": ["Theft/Normal classification", "Risk level", "Confidence %", "Timestamp"],
            },
        ],
        "storage": stats,
        "search_capabilities": {
            "fields": ["Consumer ID (CONS-10001)", "Full Name", "CNIC", "Meter Number", "Phone Number"],
            "filters": ["Region (8 regions)", "Label (Normal/Theft)", "Connection Type", "Payment Status"],
            "performance": "Indexed SQLite queries — results in <50ms for 15,000 records",
        },
    }
