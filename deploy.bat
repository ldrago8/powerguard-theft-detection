@echo off
echo ============================================
echo  PowerGuard Cloud Deployment Helper
echo ============================================
echo.
echo This project is ready for FREE cloud deployment.
echo.
echo STEP 1: Upload to GitHub
echo   - Go to https://github.com/new
echo   - Create repo: powerguard-theft-detection
echo   - Upload all project files (skip .python and storage folders)
echo.
echo STEP 2: Deploy on Render.com
echo   - Go to https://render.com (sign up with GitHub)
echo   - New Web Service - connect your repo
echo   - Runtime: Docker, Plan: Free
echo   - Health Check: /api/health
echo   - Deploy!
echo.
echo STEP 3: Your live URL will be:
echo   https://powerguard-theft-detection.onrender.com
echo.
echo Full guide: see DEPLOY.md
echo Report content: see docs/CLOUD_REPORT.md
echo.
pause
