@echo off
echo ============================================
echo  PowerGuard - AWS Cloud Deployment
echo ============================================
echo.
echo AWS Services: EC2 + S3 + IAM + Security Group
echo.
echo STEP 1: Create AWS account (free tier)
echo   https://aws.amazon.com/free
echo.
echo STEP 2: Create IAM access keys
echo   AWS Console - IAM - Users - Security credentials
echo.
echo STEP 3: Configure AWS CLI
echo   aws configure
echo   Region: us-east-1
echo.
echo STEP 4: Deploy
echo   powershell -ExecutionPolicy Bypass -File aws\deploy-aws.ps1
echo.
echo Full guide: docs\DEPLOY_AWS.md
pause
