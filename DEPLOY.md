# Deploy PowerGuard to Cloud (Free) — 10 Minutes

## What you get
- Live URL: `https://powerguard-theft-detection.onrender.com`
- Free cloud hosting (Render.com)
- Docker container on cloud VM
- All 15,000 records + ML model running remotely
- Sir can access from any browser

---

## Step 1 — Create GitHub account & repo (5 min)

1. Go to [github.com](https://github.com) → Sign up (free)
2. Click **New repository**
3. Name: `powerguard-theft-detection`
4. Public → Create
5. Click **uploading an existing file**
6. Drag ALL files from your `Cloud project` folder EXCEPT:
   - `.python/` folder
   - `storage/` folder  
   - `venv/` folder
7. Commit

---

## Step 2 — Deploy on Render.com (5 min)

1. Go to [render.com](https://render.com) → Sign up with GitHub (free, no credit card)
2. Dashboard → **New +** → **Web Service**
3. Connect your `powerguard-theft-detection` repo
4. Settings:
   - **Name:** `powerguard-theft-detection`
   - **Runtime:** Docker
   - **Plan:** Free
   - **Health Check Path:** `/api/health`
5. Click **Create Web Service**
6. Wait 5–10 minutes for build (generates dataset + trains ML model)
7. Your URL appears at top: `https://powerguard-theft-detection.onrender.com`

---

## Step 3 — Verify cloud deployment

Open your URL → check:
- Dashboard loads with 15,000 records
- Search `CONS-10001` works
- **Cloud Architecture** page shows "Running on Render.com Cloud"
- `/api/health` shows `"environment": "cloud"`

---

## Cloud services used (for sir's questions)

| Cloud Concept | Where Used |
|---------------|------------|
| **Virtual Machine** | Render Linux VM runs Docker container |
| **Cloud Compute** | FastAPI + ML inference on cloud VM |
| **Cloud Storage** | CSV dataset + ML model on persistent disk |
| **Cloud Database** | SQLite indexed DB (PostgreSQL on paid tier) |
| **Scalability** | Add more VM instances on paid tier |
| **Elasticity** | Auto-sleep when idle (free), scale up on demand |
| **System Integration** | GitHub → Render CI/CD pipeline |
| **Cost** | $0/month on free tier |

---

## Troubleshooting

**Build fails:** Check Render logs — usually pip install issue. Re-deploy.

**App sleeps:** Free tier sleeps after 15 min idle. First visit takes ~30 sec to wake up.

**Slow first load:** Normal — container starts, loads 15K records into DB.

---

## Alternative: Railway.app

1. [railway.app](https://railway.app) → Deploy from GitHub
2. Same Docker setup works automatically
