# One-command deploy to Hugging Face (no card required)
# Usage:  .\push-hf.ps1 -Token hf_xxxxxxxxxxxxxxxx

param(
    [Parameter(Mandatory = $true)]
    [string]$Token
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:Path = "C:\Program Files\Git\cmd;C:\Users\princ\.local\bin;" + $env:Path

Set-Location $PSScriptRoot

Write-Host "Deploying to Hugging Face Space..." -ForegroundColor Cyan

git remote remove huggingface 2>$null
git remote add huggingface "https://Ldrago8:$Token@huggingface.co/spaces/Ldrago8/powerguard-theft-detection"
git push huggingface main --force

Write-Host ""
Write-Host "SUCCESS! Your app is building on cloud." -ForegroundColor Green
Write-Host "Space page:  https://huggingface.co/spaces/Ldrago8/powerguard-theft-detection"
Write-Host "Live URL:    https://ldrago8-powerguard-theft-detection.hf.space"
Write-Host ""
Write-Host "Wait 5-10 minutes for build to finish, then open the Live URL."
