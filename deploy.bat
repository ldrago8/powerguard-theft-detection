@echo off
echo ============================================
echo  FREE Cloud Deploy - NO CREDIT CARD
echo  Hugging Face Spaces
echo ============================================
echo.
echo Render asks for card. Use Hugging Face instead:
echo.
echo 1. Sign up: https://huggingface.co/join
echo 2. Create Space: https://huggingface.co/new-space
echo    - Name: powerguard-theft-detection
echo    - SDK: Docker
echo    - Hardware: CPU basic (free)
echo.
echo 3. Get token: https://huggingface.co/settings/tokens
echo.
echo 4. Run these commands (replace YOUR_USERNAME):
echo.
echo    cd "%~dp0"
echo    git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/powerguard-theft-detection
echo    git push huggingface main
echo.
echo    Password = paste your HF token
echo.
echo Full guide: DEPLOY.md
pause
