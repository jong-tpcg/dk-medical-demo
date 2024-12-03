## React Vite실행

pnpm install
pnpm run dev

## Deploy Cloud Run

set PROJECT_ID=dk-medical-solutions
set REGION=us-central1
set APP=demo-app-front
set TAG=gcr.io/%PROJECT_ID%/%APP%

gcloud builds submit --project=%PROJECT_ID% --tag %TAG%

gcloud run deploy %APP% --project %PROJECT_ID% --image %TAG% --platform managed --region %REGION% --allow-unauthenticated
