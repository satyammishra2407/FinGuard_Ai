@echo off
REM FinGuard AI - Hugging Face Deployment Script
REM This script helps you prepare files for Hugging Face Spaces

echo ========================================
echo FinGuard AI - Hugging Face Deployment
echo ========================================
echo.

echo This script will prepare your files for Hugging Face Spaces deployment.
echo.
echo Steps to deploy:
echo 1. Create a new Space on Hugging Face (https://huggingface.co/spaces)
echo 2. Clone your Space repository
echo 3. Run this script to copy files
echo 4. Push to Hugging Face
echo.

set /p hf_space_path="Enter the path to your cloned HF Space directory (or 'skip' to skip): "

if /i "%hf_space_path%"=="skip" (
    echo.
    echo Skipping file copy. You can manually copy files later.
    echo See HUGGINGFACE_DEPLOYMENT.md for detailed instructions.
    pause
    exit /b 0
)

if not exist "%hf_space_path%" (
    echo.
    echo ERROR: Directory does not exist: %hf_space_path%
    echo Please create the directory or check the path.
    pause
    exit /b 1
)

echo.
echo [1/5] Copying main application files...
copy /Y app.py "%hf_space_path%\app.py"
copy /Y config.py "%hf_space_path%\config.py"
copy /Y database.py "%hf_space_path%\database.py"
copy /Y detection_algorithms.py "%hf_space_path%\detection_algorithms.py"
copy /Y ml_models.py "%hf_space_path%\ml_models.py"
copy /Y data_generator.py "%hf_space_path%\data_generator.py"
copy /Y setup_database.py "%hf_space_path%\setup_database.py"
copy /Y requirements.txt "%hf_space_path%\requirements.txt"
copy /Y LICENSE "%hf_space_path%\LICENSE"

echo.
echo [2/5] Copying README for Hugging Face...
copy /Y README_HF.md "%hf_space_path%\README.md"

echo.
echo [3/5] Copying models directory...
if exist "models" (
    xcopy /Y /E /I models "%hf_space_path%\models"
    echo Models copied successfully!
) else (
    echo No models directory found, skipping...
)

echo.
echo [4/5] Copying lib directory...
if exist "lib" (
    xcopy /Y /E /I lib "%hf_space_path%\lib"
    echo Lib copied successfully!
) else (
    echo No lib directory found, skipping...
)

echo.
echo [5/5] Creating .gitignore...
(
    echo # Python
    echo __pycache__/
    echo *.py[cod]
    echo *.db
    echo *.sqlite
    echo *.log
    echo .env
) > "%hf_space_path%\.gitignore"

echo.
echo ========================================
echo Files prepared successfully!
echo ========================================
echo.
echo Next steps:
echo 1. cd "%hf_space_path%"
echo 2. git add .
echo 3. git commit -m "Deploy FinGuard AI"
echo 4. git push
echo.
echo Your Hugging Face Space will build and deploy automatically!
echo.
echo NOTE: The database will be reset on each Space restart.
echo Users need to click "Generate Data" button after each restart.
echo.

pause

