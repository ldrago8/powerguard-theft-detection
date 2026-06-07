# Deploy PowerGuard to AWS Free Tier
# Prerequisites: AWS account + aws configure (access key + secret)

param(
    [string]$StackName = "powerguard-theft-detection",
    [string]$Region = "us-east-1",
    [string]$KeyPairName = ""
)

$ErrorActionPreference = "Stop"
$env:Path = "C:\Program Files\Amazon\AWSCLIV2;C:\Program Files\Git\cmd;" + $env:Path

Write-Host "=== PowerGuard AWS Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Check AWS CLI
try {
    $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "AWS Account: $($identity.Account)" -ForegroundColor Green
    Write-Host "AWS User:    $($identity.Arn)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: AWS CLI not configured." -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Create free AWS account: https://aws.amazon.com/free"
    Write-Host "2. Create access keys: IAM -> Users -> Security credentials"
    Write-Host "3. Run: aws configure"
    Write-Host "   Region: us-east-1"
    Write-Host "4. Re-run: .\aws\deploy-aws.ps1"
    exit 1
}

$templatePath = Join-Path $PSScriptRoot "cloudformation.yaml"

$vpcId = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $Region
if (-not $vpcId -or $vpcId -eq "None") {
    Write-Host "ERROR: No default VPC found in $Region. Create one or pass VpcId manually." -ForegroundColor Red
    exit 1
}

$params = @("InstanceType=t3.micro", "VpcId=$vpcId")
if ($KeyPairName) { $params += "KeyPairName=$KeyPairName" }

Write-Host ""
Write-Host "Deploying CloudFormation stack: $StackName" -ForegroundColor Cyan
Write-Host "Region: $Region"
Write-Host "This creates: EC2 + S3 + IAM + Security Group"
Write-Host ""

aws cloudformation deploy `
    --template-file $templatePath `
    --stack-name $StackName `
    --parameter-overrides $params `
    --capabilities CAPABILITY_NAMED_IAM `
    --region $Region `
    --no-fail-on-empty-changeset

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed. Check AWS CloudFormation console for errors." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== DEPLOYMENT SUCCESSFUL ===" -ForegroundColor Green
Write-Host ""

$outputs = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query "Stacks[0].Outputs" `
    --output json | ConvertFrom-Json

foreach ($out in $outputs) {
    Write-Host "$($out.OutputKey): $($out.OutputValue)"
}

$appUrl = ($outputs | Where-Object { $_.OutputKey -eq "ApplicationURL" }).OutputValue
Write-Host ""
Write-Host "Your cloud app URL: $appUrl" -ForegroundColor Green
Write-Host "Wait 5-10 minutes for EC2 setup, then open the URL."
Write-Host "Show this URL to your sir for the presentation."
