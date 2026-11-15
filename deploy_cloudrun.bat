@echo off
echo ============================================
echo  Apollo 13 AI - Google Cloud Run Deploy
echo ============================================
echo.

REM === CONFIG - Edit these ===
set PROJECT_ID=YOUR_GCP_PROJECT_ID
set REGION=us-central1
set SERVICE_NAME=apollo13-api
REM ============================

echo [1] Authenticating...
gcloud auth login

echo [2] Setting project...
gcloud config set project %PROJECT_ID%

echo [3] Building and pushing Docker image...
gcloud builds submit --tag gcr.io/%PROJECT_ID%/%SERVICE_NAME%

echo [4] Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
  --image gcr.io/%PROJECT_ID%/%SERVICE_NAME% ^
  --platform managed ^
  --region %REGION% ^
  --allow-unauthenticated ^
  --memory 1Gi ^
  --cpu 1 ^
  --port 8080

echo.
echo Done! Your backend URL is shown above (*.run.app)
pause
