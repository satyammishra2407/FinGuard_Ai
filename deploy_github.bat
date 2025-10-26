@echo off
REM FinGuard AI - GitHub Deployment Script
REM This script helps you deploy to GitHub

echo ========================================
echo FinGuard AI - GitHub Deployment
echo ========================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo [1/5] Checking Git status...
git status

echo.
echo [2/5] Adding files to Git...
git add .

echo.
echo [3/5] Creating commit...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update: FinGuard AI deployment

git commit -m "%commit_msg%"

echo.
echo [4/5] Checking remote repository...
git remote -v

REM Check if remote 'origin' exists
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Remote 'origin' not configured. Adding GitHub repository...
    echo.
    echo Please enter your GitHub repository URL:
    echo Example: https://github.com/satyammishra2407/FinGuard_Ai.git
    set /p repo_url="Repository URL: "
    git remote add origin %repo_url%
    echo Remote added successfully!
    echo.
)

echo.
echo [5/5] Pushing to GitHub...
echo.
echo NOTE: You may be prompted for your GitHub credentials:
echo - Username: Your GitHub username
echo - Password: Your Personal Access Token (NOT your password)
echo.
echo If you don't have a token, create one at:
echo https://github.com/settings/tokens
echo.
pause

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Deployed to GitHub
    echo ========================================
    echo.
    echo Your repository: https://github.com/satyammishra2407/FinGuard_Ai
    echo.
) else (
    echo.
    echo ========================================
    echo DEPLOYMENT FAILED
    echo ========================================
    echo.
    echo Common issues:
    echo 1. Incorrect credentials - Use Personal Access Token
    echo 2. Remote not configured properly
    echo 3. Branch name mismatch - Try: git branch -M main
    echo.
    echo See GITHUB_DEPLOYMENT.md for detailed instructions
    echo.
)

pause

