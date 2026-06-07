# Fix AWS Permissions — Required Before Deploy

Your IAM user `electricity_theft_detection` can log in but has **no permissions** attached.

## Quick fix (5 minutes) — AWS Console

1. Log in to **AWS Console** as root or admin: https://console.aws.amazon.com
2. Go to **IAM** → **Users** → **electricity_theft_detection**
3. Click **Add permissions** → **Attach policies directly**
4. Search and attach ONE of these:
   - **AdministratorAccess** (easiest for student project), OR
   - **PowerUserAccess** + create custom policy from `iam-policy-powerguard.json`
5. Click **Add permissions**

## Then deploy

```powershell
cd "C:\Users\princ\OneDrive\Desktop\Cloud project"
powershell -ExecutionPolicy Bypass -File aws\deploy-aws.ps1
```

## Custom policy (more secure)

IAM → Policies → Create policy → JSON → paste contents of `aws/iam-policy-powerguard.json` → Name: `PowerGuardDeploy` → Attach to user.

## Verify permissions work

```powershell
aws sts get-caller-identity
aws ec2 describe-instances --max-items 1
aws cloudformation list-stacks --max-items 1
```

All three should succeed without AccessDenied.
