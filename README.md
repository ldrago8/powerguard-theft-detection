# PowerGuard — Cloud-Based Electricity Theft Detection System

**Semester Project · Cloud Computing · BCS223210 Sahil Jamal**  
Capital University of Science and Technology, Islamabad

---

## Overview

Enterprise-grade electricity theft detection platform with **15,000 consumer records**, machine learning analysis, and a professional web dashboard. Enter any Consumer ID to instantly view full profile, billing, consumption history, and AI theft detection results.

## Key Features

| Feature | Description |
|---------|-------------|
| **Consumer Lookup** | Enter `CONS-10001` → full profile, billing, 6-month chart, ML analysis |
| **15,000 Records** | Synthetic dataset with names, CNIC, meters, 8 regions, 8 distribution companies |
| **ML Detection** | Decision Tree, Random Forest, Logistic Regression (~99% accuracy) |
| **Dashboard** | Live stats, regional charts, recent detections |
| **All Consumers** | Search, filter, paginate through entire database |
| **Analytics** | Regional breakdown, payment status, company distribution |
| **Batch Analysis** | Upload CSV for bulk theft detection |
| **Cloud Ready** | Docker + Render.com free deployment |

## Quick Start

### Windows (one command)
```bat
run.bat
```

### Manual
```bash
pip install -r requirements.txt
python data/generate_dataset.py    # Creates 15,000 records (~4.5 MB)
python ml/train_model.py             # Trains all 3 ML models
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**

## Demo Consumer IDs

Try these in **Consumer Lookup**:
- `CONS-10001` — sample consumer with full profile
- `CONS-10500` — mid-range record
- `CONS-12000` — another sample
- `CONS-15000` — last record in dataset

## Dataset Fields (33 columns)

**Personal:** consumer_id, full_name, cnic, phone, email, address, city, region  
**Account:** distribution_company, meter_number, meter_type, connection_type, tariff_category, account_status, registration_date, sanctioned_load_kw  
**Consumption:** monthly + 5 previous months, area average, meter reading difference, peak load, power factor  
**Billing:** current/previous bill, payment_status, outstanding_balance  
**Label:** Normal / Theft

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/consumers/{id}` | **Full consumer details + ML analysis** |
| GET | `/api/consumers/search` | Search & filter with pagination |
| GET | `/api/analytics` | Regional & company analytics |
| GET | `/api/metrics` | Active model performance |
| POST | `/api/predict/batch` | Bulk CSV analysis |
| GET | `/api/download/dataset` | Download 15K CSV |

## Project Structure

```
├── backend/
│   ├── app.py              # FastAPI REST API (v2)
│   └── database.py         # SQLite consumer database
├── frontend/static/
│   ├── index.html          # Professional dashboard UI
│   ├── styles.css          # Modern dark theme
│   └── app.js              # Full frontend logic + charts
├── data/
│   ├── generate_dataset.py # 15K record generator
│   └── electricity_consumption.csv
├── ml/
│   ├── preprocess.py       # Feature engineering
│   ├── train_model.py      # Model training
│   └── artifacts/          # Trained model + metrics
├── storage/                # SQLite databases
├── Dockerfile              # Cloud deployment
└── run.bat                 # One-click startup
```

## Monday Presentation Flow

1. Run `run.bat` → open http://127.0.0.1:8000
2. **Dashboard** — show 15,000 records, theft stats, model accuracy
3. **Consumer Lookup** — enter `CONS-10001`, show full profile + chart + theft detection
4. **All Consumers** — search by name, filter by region/label
5. **Analytics** — regional charts and distribution companies
6. **ML Models** — compare Decision Tree vs Random Forest vs Logistic Regression
7. Explain cloud role: storage (CSV/DB), compute (ML), database (SQLite/PostgreSQL)

## Cloud Deployment (Render.com — Free)

1. Push to GitHub
2. [render.com](https://render.com) → New Web Service → Docker → Free
3. Live URL in ~5 minutes

---

**Author:** Sahil Jamal · BCS223210 · Dr. Muhammad Masroor Ahmed
