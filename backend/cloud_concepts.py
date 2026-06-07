"""Cloud computing concepts aligned with course project requirements."""

import os
from datetime import datetime


def get_deployment_status() -> dict:
    env = os.getenv("DEPLOYMENT_ENV", "local")
    is_hf = bool(os.getenv("SPACE_ID") or os.getenv("SPACE_TITLE"))
    is_render = os.getenv("RENDER") == "true" or bool(os.getenv("RENDER_SERVICE_ID"))
    is_aws = env == "aws-cloud" or bool(os.getenv("AWS_S3_BUCKET") or os.getenv("AWS_EXECUTION_ENV"))
    is_cloud = env != "local" or is_hf or is_render or is_aws

    if is_aws:
        platform = "Amazon Web Services (EC2 + S3 + IAM)"
        bucket = os.getenv("AWS_S3_BUCKET", "")
        service_url = os.getenv("APP_URL", f"http://EC2-Public-IP (S3: {bucket})" if bucket else "AWS Cloud")
    elif is_hf:
        space = os.getenv("SPACE_ID", "powerguard-theft-detection")
        platform = f"Hugging Face Spaces — {space}"
        service_url = os.getenv("SPACE_HOST", f"https://huggingface.co/spaces/{space}")
    elif is_render:
        platform = f"Render.com — {os.getenv('RENDER_SERVICE_NAME', 'powerguard')}"
        service_url = os.getenv("RENDER_EXTERNAL_URL", "")
    else:
        platform = "Local Development"
        service_url = "http://127.0.0.1:8000"

    return {
        "environment": "cloud" if is_cloud else "local",
        "platform": platform,
        "deployment_env": env,
        "region": os.getenv("RENDER_REGION", os.getenv("SPACE_REGION", "local")),
        "service_url": service_url,
        "containerized": True,
        "last_checked": datetime.utcnow().isoformat() + "Z",
    }


def get_course_cloud_concepts() -> dict:
    return {
        "project_title": "Cloud-Based Electricity Theft Detection System Using Machine Learning",
        "student": "Sahil Jamal — BCS223210",
        "course": "Cloud Computing",
        "sections": {
            "designing_phase": {
                "title": "1. Designing Phase — Options & Tradeoffs",
                "content": [
                    {
                        "option": "AWS (EC2 + S3 + RDS)",
                        "pros": ["Industry standard", "Full control", "Massive scale"],
                        "cons": ["Complex setup", "Free tier expires after 12 months", "Requires credit card"],
                        "verdict": "Best for enterprise production",
                    },
                    {
                        "option": "Google Cloud Platform (Cloud Run + BigQuery)",
                        "pros": ["Serverless scaling", "Strong ML tools", "Pay per use"],
                        "cons": ["Learning curve", "Billing complexity"],
                        "verdict": "Best for ML-heavy workloads",
                    },
                    {
                        "option": "Microsoft Azure (App Service + Blob + SQL)",
                        "pros": ["Enterprise integration", "Hybrid cloud support"],
                        "cons": ["Pricing complexity", "Setup overhead"],
                        "verdict": "Best for corporate environments",
                    },
                    {
                        "option": "AWS EC2 + S3 + IAM (SELECTED)",
                        "pros": ["Industry standard cloud", "EC2 free tier 12 months", "S3 cloud storage", "IAM security", "Best for semester presentation", "Sir expects AWS/GCP/Azure"],
                        "cons": ["Credit card required for account verification", "More setup than Hugging Face"],
                        "verdict": "SELECTED — primary deployment for Cloud Computing course",
                    },
                    {
                        "option": "Hugging Face Spaces + Docker",
                        "pros": ["Completely free", "No credit card required", "Docker-native", "16GB RAM free tier"],
                        "cons": ["Sleeps when idle", "Less recognized as enterprise cloud"],
                        "verdict": "Alternative for quick demo without AWS account",
                    },
                    {
                        "option": "Render.com + Docker",
                        "pros": ["Free tier", "Docker-native", "Auto-deploy from GitHub"],
                        "cons": ["Requires credit card for verification", "Sleeps after 15 min idle"],
                        "verdict": "Alternative if card available",
                    },
                ],
                "architecture_decision": "Containerized microservice architecture: single Docker image containing FastAPI API + ML model + SQLite DB, deployable to any cloud provider.",
            },
            "economic_structure": {
                "title": "2. Economic Structure — Cost Analysis",
                "cost_breakdown": [
                    {"service": "EC2 t2.micro (Free Tier)", "cost_usd": "$0/month", "usage": "750 hours/month for 12 months — runs Docker app"},
                    {"service": "S3 Standard Storage", "cost_usd": "$0/month", "usage": "5 GB free — stores dataset + ML model"},
                    {"service": "IAM Roles & Policies", "cost_usd": "$0", "usage": "EC2 role for secure S3 access"},
                    {"service": "CloudFormation", "cost_usd": "$0", "usage": "Infrastructure as Code deployment"},
                    {"service": "Data Transfer", "cost_usd": "$0", "usage": "15 GB outbound free/month"},
                ],
                "total_monthly_cost": "$0 (AWS Free Tier — first 12 months)",
                "cost_if_scaled": {
                    "100k_consumers_aws": "~$25–50/month (EC2 t3.small + S3 + RDS db.t3.micro)",
                    "1m_consumers_aws": "~$200–500/month (Auto-scaling EC2 + S3 + RDS + Lambda)",
                },
                "cost_optimization": [
                    "Docker multi-stage build reduces image size → faster deploys, less bandwidth cost",
                    "SQLite on free tier avoids separate database charges",
                    "Batch ML inference reduces compute calls vs per-request retraining",
                    "Indexed database queries minimize CPU usage per search",
                    "Container sleep on idle (free tier) saves compute hours",
                ],
            },
            "data_handling": {
                "title": "3. Data Handling, Optimization, Scheduling & Virtual Machines",
                "data_handling": [
                    "15,000 consumer records with 33 attributes collected and stored in cloud-accessible CSV",
                    "CSV imported into indexed SQLite database on startup for O(log n) search performance",
                    "Feature extraction pipeline: 11 numeric + 4 categorical features standardized via Scikit-learn",
                    "Prediction logs stored in cloud database for audit trail",
                    "Batch CSV upload processed sequentially on cloud compute VM",
                ],
                "optimization": [
                    "Database indexes on consumer_id, full_name, meter_number, cnic, region, label",
                    "ML model pre-trained and serialized (.pkl) — no retraining on each request",
                    "Autocomplete search limited to 12 results to reduce payload size",
                    "Paginated API responses (25 records/page) prevent memory overload",
                    "Docker layer caching speeds up cloud redeployment",
                ],
                "scheduling": [
                    "On-demand inference: ML model runs when user searches a consumer",
                    "Batch scheduling: CSV uploads processed as a job queue on the VM",
                    "Auto-deploy: GitHub push triggers Render build pipeline automatically",
                    "Health checks every 30 seconds ensure VM/container availability",
                ],
                "virtual_machines": [
                    "Docker container runs inside Render's shared Linux VM (free tier)",
                    "Container = lightweight VM abstraction with isolated Python runtime",
                    "Equivalent AWS setup: EC2 t2.micro instance running Docker",
                    "VM specs (free tier): 512 MB RAM, 0.5 CPU, Linux container",
                    "Horizontal scaling: add more VM instances behind load balancer (paid tier)",
                ],
            },
            "elasticity_scalability": {
                "title": "4. Support Services, Elasticity & Scalability",
                "support_services": [
                    {"service": "Health Check API", "description": "/api/health — monitors model and database status"},
                    {"service": "Auto-Deploy CI/CD", "description": "GitHub → Render automatic deployment on code push"},
                    {"service": "REST API Gateway", "description": "12+ endpoints for search, predict, analytics, system info"},
                    {"service": "Logging", "description": "Render dashboard logs + prediction history in database"},
                    {"service": "Container Registry", "description": "Docker image built and cached on Render infrastructure"},
                ],
                "elasticity": [
                    "Scale UP: Increase VM RAM/CPU on Render paid tier when traffic spikes (billing season)",
                    "Scale DOWN: Free tier auto-sleeps after 15 min idle — zero cost when unused",
                    "Auto-scaling (AWS equivalent): EC2 Auto Scaling Group adds instances when CPU > 70%",
                    "Database elasticity: SQLite → PostgreSQL migration when records exceed 100K",
                ],
                "scalability": [
                    "Current: 15,000 consumers — handles instantly on single container",
                    "10x scale (150K): PostgreSQL + 2 VM instances behind load balancer",
                    "100x scale (1.5M): AWS S3 for dataset + ECS cluster + RDS Multi-AZ + Redis cache",
                    "Geographic scale: Deploy containers in multiple regions (Islamabad, Karachi, Lahore)",
                    "ML scalability: Retrain model on cloud GPU (AWS SageMaker) with full WAPDA dataset",
                ],
            },
            "system_integration": {
                "title": "5. System Integration — Cloud-to-Cloud Connections",
                "integrations": [
                    {
                        "from": "GitHub (Source Control Cloud)",
                        "to": "Render.com (Compute Cloud)",
                        "how": "Git push triggers webhook → Render pulls code → builds Docker image → deploys container",
                        "protocol": "HTTPS webhook + Git protocol",
                    },
                    {
                        "from": "Render Container (Compute)",
                        "to": "Persistent Disk (Storage Cloud)",
                        "how": "SQLite database and ML model stored on Render persistent volume",
                        "protocol": "File system mount",
                    },
                    {
                        "from": "Web Dashboard (Frontend)",
                        "to": "FastAPI REST API (Backend)",
                        "how": "JavaScript fetch() calls to /api/* endpoints on same cloud container",
                        "protocol": "HTTPS REST/JSON",
                    },
                    {
                        "from": "FastAPI Backend",
                        "to": "Scikit-learn ML Engine",
                        "how": "joblib.load() loads model from disk → predict() on each consumer search",
                        "protocol": "In-process Python call",
                    },
                    {
                        "from": "External Billing System (Future)",
                        "to": "PowerGuard API",
                        "how": "K-Electric/WAPDA sends consumer data via POST /api/predict/batch",
                        "protocol": "REST API + CSV upload",
                    },
                    {
                        "from": "AWS S3 (Future Production)",
                        "to": "Render/AWS Compute",
                        "how": "Dataset stored in S3 bucket → downloaded on container startup for ML training",
                        "protocol": "AWS SDK (boto3) HTTPS",
                    },
                ],
                "diagram_flow": "Smart Meters → Cloud Storage (S3/CSV) → Cloud Database (SQLite/PostgreSQL) → Cloud Compute (Docker VM) → ML Engine → REST API → Web Dashboard → Distribution Company",
            },
            "technical_phase": {
                "title": "6. Technical Phase",
                "stack": {
                    "language": "Python 3.12",
                    "backend": "FastAPI + Uvicorn ASGI server",
                    "ml": "Scikit-learn (Decision Tree, Random Forest, Logistic Regression)",
                    "database": "SQLite (dev/free) → PostgreSQL (production cloud)",
                    "frontend": "HTML5 + CSS3 + JavaScript + Chart.js",
                    "container": "Docker (Linux container on cloud VM)",
                    "deployment": "Render.com / AWS EC2 / Azure App Service",
                },
                "ml_pipeline": [
                    "1. Generate/load 15,000 consumer records",
                    "2. Feature engineering: 11 numeric + 4 categorical features",
                    "3. StandardScaler + OneHotEncoder preprocessing",
                    "4. Train 3 models, select best by F1-score",
                    "5. Serialize model to .pkl for cloud deployment",
                    "6. Real-time inference via /api/consumers/{id}",
                ],
                "performance": {
                    "accuracy": "~99%",
                    "search_latency": "<50ms for 15K records",
                    "model_inference": "<10ms per consumer",
                    "dataset_size": "4.5 MB CSV, 15,000 rows, 33 columns",
                },
            },
            "implementation_phase": {
                "title": "7. Implementation Phase",
                "modules": [
                    {"module": "data/generate_dataset.py", "purpose": "Synthetic data generator — 15K Pakistani consumer records"},
                    {"module": "backend/database.py", "purpose": "SQLite cloud database layer with indexed search"},
                    {"module": "backend/app.py", "purpose": "FastAPI REST API — 15+ endpoints"},
                    {"module": "ml/train_model.py", "purpose": "ML training pipeline with 3 algorithms"},
                    {"module": "frontend/static/", "purpose": "Professional web dashboard with search, analytics, cloud docs"},
                    {"module": "backend/cloud_concepts.py", "purpose": "Cloud computing concepts for course requirements"},
                    {"module": "Dockerfile", "purpose": "Container image for cloud VM deployment"},
                ],
                "timeline": [
                    {"week": "Week 1", "task": "Project proposal, literature review, dataset design"},
                    {"week": "Week 2", "task": "Data generation, ML model training, evaluation metrics"},
                    {"week": "Week 3", "task": "FastAPI backend, database, REST API development"},
                    {"week": "Week 4", "task": "Web dashboard, search, consumer lookup UI"},
                    {"week": "Week 5", "task": "Cloud architecture design, Docker containerization"},
                    {"week": "Week 6", "task": "Render.com deployment, cloud concepts integration, report writing"},
                ],
            },
            "deployment_phase": {
                "title": "8. Deployment Phase",
                "steps": [
                    "1. AWS account created with Free Tier access",
                    "2. IAM access keys configured for AWS CLI",
                    "3. CloudFormation stack deploys EC2 + S3 + IAM + Security Group",
                    "4. EC2 UserData installs Docker, clones GitHub repo, builds image",
                    "5. Container runs on port 80 — FastAPI + ML + Dashboard",
                    "6. Dataset and model uploaded to S3 bucket automatically",
                    "7. Public IP URL accessible worldwide for presentation",
                ],
                "environments": [
                    {"env": "Development", "url": "http://127.0.0.1:8000", "purpose": "Local testing via run.bat"},
                    {"env": "AWS Production", "url": "http://EC2-Public-IP (from CloudFormation output)", "purpose": "EC2 + S3 cloud deployment for presentation"},
                ],
                "cicd": "CloudFormation IaC → EC2 UserData → Docker build → Live on AWS",
            },
            "optimized_architecture": {
                "title": "9. Optimized Cloud Architecture",
                "layers": [
                    {"layer": "Presentation Layer", "component": "Web Dashboard (HTML/JS)", "cloud_service": "CDN / Static hosting"},
                    {"layer": "API Layer", "component": "FastAPI REST API", "cloud_service": "Cloud Compute (VM/Container)"},
                    {"layer": "Business Logic", "component": "ML Inference Engine", "cloud_service": "Cloud Compute (same container)"},
                    {"layer": "Data Layer", "component": "SQLite / PostgreSQL", "cloud_service": "Cloud Database"},
                    {"layer": "Storage Layer", "component": "CSV + ML Model files", "cloud_service": "Cloud Storage (S3/Disk)"},
                ],
                "optimizations": [
                    "Single Docker container reduces latency (no network calls between services)",
                    "Pre-trained ML model eliminates training delay on each request",
                    "Indexed database enables instant consumer search at scale",
                    "Free tier auto-sleep saves 100% compute cost during idle periods",
                    "Health checks prevent serving traffic to unhealthy containers",
                    "Paginated APIs prevent memory exhaustion on large result sets",
                ],
                "future_improvements": [
                    "Migrate to AWS ECS + RDS + S3 for WAPDA production scale",
                    "Add Redis cache for frequent consumer lookups",
                    "Implement Kubernetes for multi-region auto-scaling",
                    "Real-time streaming from smart meters via AWS Kinesis",
                ],
            },
            "research_component": {
                "title": "10. Research Component",
                "problem": "Electricity theft causes billions of PKR losses annually in Pakistan. Manual inspection achieves only 60–70% detection accuracy.",
                "research_question": "Can machine learning combined with cloud computing improve electricity theft detection accuracy and enable scalable monitoring?",
                "methodology": "Synthetic dataset of 15,000 consumers → 3 ML algorithms compared → cloud-deployed inference system → evaluation via accuracy, precision, recall, F1-score",
                "findings": [
                    "ML detection achieves ~99% accuracy vs 60–70% for manual inspection",
                    "Random Forest / Logistic Regression outperform Decision Tree on this dataset",
                    "Cloud deployment enables monitoring 15,000+ consumers from a single web dashboard",
                    "Indexed cloud database enables consumer search in under 50ms",
                    "Containerized architecture allows deployment to any cloud provider",
                ],
                "comparison": {
                    "manual_inspection": {"accuracy": "60–70%", "cost": "High (physical visits)", "scale": "Limited"},
                    "rule_based": {"accuracy": "70–80%", "cost": "Medium", "scale": "Moderate"},
                    "ml_cloud_proposed": {"accuracy": "~99%", "cost": "$0 free tier", "scale": "Millions via cloud scaling"},
                },
                "references": [
                    "NIST SP 800-145 — NIST Definition of Cloud Computing",
                    "AWS, GCP, Azure official documentation",
                    "Scikit-learn ML documentation",
                    "WAPDA / K-Electric distribution reports",
                ],
            },
        },
    }


def get_full_cloud_report() -> dict:
    status = get_deployment_status()
    concepts = get_course_cloud_concepts()
    return {
        "deployment": status,
        "concepts": concepts,
    }
