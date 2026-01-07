---
post_title: "Cloud Scheduler → Cloud Run OIDC setup (Windows & Linux)"
author1: "ac484"
post_slug: "cloud-scheduler-oidc-guide"
microsoft_alias: "ac484"
featured_image: ""
categories:
  - "runbook"
tags:
  - "cloud-run"
  - "cloud-scheduler"
  - "oidc"
  - "iam"
ai_note: "Generated with AI assistance"
summary: "Step-by-step guide to let Cloud Scheduler call the Cloud Run service with OIDC on Windows and Linux using scheduler@qrl-api.iam.gserviceaccount.com."
post_date: 2026-01-07
---

## Prerequisites
- gcloud CLI installed (Linux/macOS shell or Windows PowerShell).
- Project set to the Cloud Run service project: `gcloud config set project qrl-api`.
- Service account for Scheduler caller: `scheduler@qrl-api.iam.gserviceaccount.com`.
- Cloud Run service name and region (example: `qrl-url`, `asia-east1`).

## Configure Cloud Run service account
Cloud Run needs its own runtime service account (example: `qrl-runner@qrl-api.iam.gserviceaccount.com`).
```bash
gcloud run services update qrl-url \
  --region=asia-east1 \
  --service-account=qrl-runner@qrl-api.iam.gserviceaccount.com
```

## Grant Cloud Scheduler Invoker on Cloud Run
Allow the scheduler service account to invoke the service.
```bash
gcloud run services add-iam-policy-binding qrl-url \
  --region=asia-east1 \
  --member=serviceAccount:scheduler@qrl-api.iam.gserviceaccount.com \
  --role=roles/run.invoker
```

## Create Scheduler job (Linux/macOS bash)
Set variables, then create the HTTP target with OIDC.
```bash
SERVICE=qrl-url
REGION=asia-east1
JOB_NAME=qrl-url-scheduler
SCHEDULER_SA=scheduler@qrl-api.iam.gserviceaccount.com
SERVICE_URL=$(gcloud run services describe $SERVICE --region=$REGION --format='value(status.url)')

gcloud scheduler jobs create http $JOB_NAME \
  --location=$REGION \
  --schedule="*/5 * * * *" \
  --uri="${SERVICE_URL}/tasks/allocation" \
  --http-method=POST \
  --oidc-service-account-email=$SCHEDULER_SA \
  --oidc-token-audience=$SERVICE_URL \
  --attempt-deadline=60s \
  --max-retry-attempts=3 \
  --min-backoff=10s
```

## Create Scheduler job (Windows PowerShell)
```powershell
$SERVICE="qrl-url"
$REGION="asia-east1"
$JOB_NAME="qrl-url-scheduler"
$SCHEDULER_SA="scheduler@qrl-api.iam.gserviceaccount.com"
$SERVICE_URL=$(gcloud run services describe $SERVICE --region=$REGION --format="value(status.url)")

gcloud scheduler jobs create http $JOB_NAME `
  --location=$REGION `
  --schedule="*/5 * * * *" `
  --uri="$SERVICE_URL/tasks/allocation" `
  --http-method=POST `
  --oidc-service-account-email=$SCHEDULER_SA `
  --oidc-token-audience=$SERVICE_URL `
  --attempt-deadline=60s `
  --max-retry-attempts=3 `
  --min-backoff=10s
```

## Verify and test
- Check IAM: `gcloud run services get-iam-policy qrl-url --region=asia-east1`.
- Run a one-off invocation: `gcloud scheduler jobs run qrl-url-scheduler --location=asia-east1`.
- Confirm Cloud Run logs show a 200/504 from `/tasks/allocation` and that Scheduler retries on 504.

## Troubleshooting tips
- 401/403: ensure the scheduler service account has `roles/run.invoker` and audience matches the service URL.
- 404: confirm the service URL and route `/tasks/allocation` exist in the deployed revision.
- Timeouts: align Scheduler attempt deadline with app timeout and `TASK_TIMEOUT_SECONDS`; keep Cloud Run request timeout ≥ Scheduler deadline.
- Cold starts: set a small min instance on Cloud Run to reduce startup latency.***
