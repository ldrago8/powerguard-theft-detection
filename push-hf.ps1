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

$hfRemote = "https://Ldrago8:$Token@huggingface.co/spaces/Ldrago8/powerguard-theft-detection"
$currentBranch = git branch --show-current

Write-Host "Creating HF deploy branch (excludes PDF binaries)..." -ForegroundColor Yellow
git checkout --orphan hf-deploy 2>$null
if ($LASTEXITCODE -ne 0) { git checkout hf-deploy; git reset --soft HEAD~1 2>$null; git reset }

if (-not (Select-String -Path .gitignore -Pattern '^\*\.pdf$' -Quiet)) {
    Add-Content .gitignore "`n# HF deploy - no binary PDFs`n*.pdf`n"
}
git add -A
git rm --cached -f "BCS223210 Sahil Jamal.pdf" 2>$null
git -c user.name="Sahil Jamal" -c user.email="ldrago8@users.noreply.github.com" commit -m "PowerGuard Electricity Theft Detection - Cloud deployment" 2>$null

git remote remove huggingface 2>$null
git remote add huggingface $hfRemote
git push huggingface hf-deploy:main --force

git checkout $currentBranch 2>$null
Write-Host "Returned to branch: $currentBranch" -ForegroundColor Gray

Write-Host ""
Write-Host "SUCCESS! Your app is building on cloud." -ForegroundColor Green
Write-Host "Space page:  https://huggingface.co/spaces/Ldrago8/powerguard-theft-detection"
Write-Host "Live URL:    https://ldrago8-powerguard-theft-detection.hf.space"
Write-Host ""
Write-Host "Wait 5-10 minutes for build to finish, then open the Live URL."
