# Deploy on AWS (Free Tier) — For Cloud Computing Project

This deployment uses **real AWS services** your sir will ask about:

| AWS Service | Role in Project |
|-------------|-----------------|
| **EC2** | Cloud compute — runs Docker container with FastAPI + ML |
| **S3** | Cloud storage — stores dataset CSV and ML model |
| **IAM** | Security — EC2 role with S3 access permissions |
| **VPC / Security Group** | Networking — controls HTTP port access |
| **CloudFormation** | Infrastructure as Code — one-click deploy |
| **CloudWatch** | Monitoring — EC2 logs at `/var/log/powerguard-setup.log` |

---

## Step 1 — Create AWS Account (one time)

1. Go to [aws.amazon.com/free](https://aws.amazon.com/free)
2. Create account (credit card required for verification, free tier won't charge if you use t2.micro)
3. **Free tier includes:** 750 hrs/month EC2 t2.micro for 12 months, 5GB S3

---

## Step 2 — Create Access Keys

1. AWS Console → **IAM** → **Users** → your user
2. **Security credentials** → **Create access key**
3. Choose "CLI" → Copy **Access Key ID** and **Secret Access Key**

---

## Step 3 — Configure AWS CLI

```powershell
aws configure
```
- AWS Access Key ID: paste your key
- AWS Secret Access Key: paste your secret
- Default region: `us-east-1`
- Default output: `json`

---

## Step 4 — Deploy (one command)

```powershell
cd "C:\Users\princ\OneDrive\Desktop\Cloud project"
.\aws\deploy-aws.ps1
```

Wait 5–10 minutes. You'll get a URL like:
```
http://54.xxx.xxx.xxx
```

---

## What to tell your sir

| Question | Answer |
|----------|--------|
| Which cloud? | **Amazon Web Services (AWS)** |
| Compute? | **EC2 t2.micro** running Docker container |
| Storage? | **S3 bucket** for dataset and ML model |
| Database? | SQLite on EC2 (upgrade to **RDS** for production) |
| Security? | **IAM role** — EC2 can only access its S3 bucket |
| Networking? | **Security Group** — ports 80 and 8000 |
| Scalability? | Auto Scaling Group + Load Balancer (add more EC2 instances) |
| Cost? | **$0** on free tier (t2.micro + 5GB S3) |
| Integration? | EC2 ↔ S3 via IAM role, GitHub → EC2 via UserData clone |

---

## Tear down (avoid charges after project)

```powershell
aws cloudformation delete-stack --stack-name powerguard-theft-detection --region us-east-1
```

This deletes EC2, S3 bucket, IAM role, and security group.
