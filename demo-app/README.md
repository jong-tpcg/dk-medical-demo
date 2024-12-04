FastAPI 실행
uvicorn main:app --reload

Deploy Cloud Run
pip freeze > requirements.txt
set PROJECT_ID=dk-medical-solutions
set REGION=us-central1
set APP=demo-app-test
set TAG=gcr.io/%PROJECT_ID%/%APP%

gcloud builds submit --project=%PROJECT_ID% --tag %TAG%

gcloud run deploy %APP% --project %PROJECT_ID% --image %TAG% --platform managed --region %REGION% --allow-unauthenticated
