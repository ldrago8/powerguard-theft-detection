# Deploy FREE on Cloud — No Credit Card Required

Render.com now asks for card details even on free tier. **Use Hugging Face Spaces instead** — completely free, no card.

---

## Step 1 — Create Hugging Face account (2 min)

1. Go to [huggingface.co/join](https://huggingface.co/join) — sign up free (no card)
2. Verify your email

---

## Step 2 — Create a Space (2 min)

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Space name:** `powerguard-theft-detection`
   - **License:** MIT
   - **SDK:** `Docker` ← important!
   - **Visibility:** Public
   - **Hardware:** CPU basic (free)
3. Click **Create Space**

---

## Step 3 — Push code from your PC (3 min)

### Get your Hugging Face token
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click **Create new token** → Role: **Write** → Copy token

### Push from terminal (PowerShell)

Replace `YOUR_USERNAME` with your Hugging Face username (e.g. `ldrago8`):

```powershell
cd "C:\Users\princ\OneDrive\Desktop\Cloud project"
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/powerguard-theft-detection
git push huggingface main
```

When asked for password, paste your **HF token** (not your password).

---

## Step 4 — Wait for build (5–10 min)

- Open your Space page: `https://huggingface.co/spaces/YOUR_USERNAME/powerguard-theft-detection`
- Watch **Build logs** — it generates dataset + trains ML model
- When status shows **Running**, click **App** tab

### Your live cloud URL:
```
https://YOUR_USERNAME-powerguard-theft-detection.hf.space
```

---

## What to tell your sir

| Cloud Concept | In This Project |
|---------------|-----------------|
| **Cloud Platform** | Hugging Face Spaces (free tier) |
| **Virtual Machine** | Docker container on HF Linux VM (2 CPU, 16GB RAM) |
| **Cloud Compute** | FastAPI + ML inference on cloud container |
| **Cloud Storage** | Dataset + ML model inside container |
| **Cloud Database** | SQLite indexed database |
| **Scalability** | Upgrade to GPU/paid hardware on HF |
| **Elasticity** | Free tier sleeps when idle, wakes on visit |
| **Cost** | **$0 — no credit card** |
| **CI/CD** | Git push → automatic Docker rebuild |
| **Integration** | GitHub (code) + Hugging Face (hosting) |

---

## Troubleshooting

**Build fails:** Check Build logs on Space page. Usually a pip install issue.

**App sleeping:** Free Spaces sleep after ~48h inactive. First visit takes ~1 min to wake.

**Port error:** App must use port **7860** (already configured in Dockerfile).

---

## Alternative: Render (needs card)

Render free tier works but requires card for verification (won't charge if you stay on free).
See `render.yaml` if you add a card later.
