---
post_title: "Cloud Scheduler → Cloud Run OIDC 設定（Windows 與 Linux）"
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
summary: "逐步教學：使用 scheduler@qrl-api.iam.gserviceaccount.com，讓 Cloud Scheduler 在 Windows 與 Linux 透過 OIDC 呼叫 Cloud Run 服務。"
post_date: 2026-01-07
---

## 前置需求
- 已安裝 gcloud CLI（Linux/macOS shell 或 Windows PowerShell 皆可）。
- 專案需設定為 Cloud Run 所在專案：`gcloud config set project qrl-api`。
- Cloud Scheduler 呼叫用的服務帳戶：`scheduler@qrl-api.iam.gserviceaccount.com`。
- Cloud Run 服務名稱與地區（本指南示範：`qrl-trading-api`，`asia-southeast1`）。

## 設定 Cloud Run 執行服務帳戶
Cloud Run 需要自己的執行服務帳戶（範例：`qrl-runner@qrl-api.iam.gserviceaccount.com`）。
```bash
gcloud run services update qrl-trading-api \
  --region=asia-southeast1 \
  --service-account=qrl-runner@qrl-api.iam.gserviceaccount.com
```

## 將 Cloud Scheduler 授權為 Cloud Run Invoker
允許排程服務帳戶呼叫 Cloud Run。
```bash
gcloud run services add-iam-policy-binding qrl-trading-api \
  --region=asia-southeast1 \
  --member=serviceAccount:scheduler@qrl-api.iam.gserviceaccount.com \
  --role=roles/run.invoker
```

## 建立排程工作（Linux/macOS bash）
先設定變數，再建立帶 OIDC 的 HTTP 目標。
```bash
SERVICE=qrl-trading-api
REGION=asia-southeast1
JOB_NAME=qrl-trading-api-scheduler
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

## 建立排程工作（Windows PowerShell）
```powershell
$SERVICE="qrl-trading-api"
$REGION="asia-southeast1"
$JOB_NAME="qrl-trading-api-scheduler"
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

## 驗證與測試
- 檢查 IAM：`gcloud run services get-iam-policy qrl-trading-api --region=asia-southeast1`。
- 執行單次觸發：`gcloud scheduler jobs run qrl-trading-api-scheduler --location=asia-southeast1`。
- 在 Cloud Run 日誌確認 `/tasks/allocation` 回應 200/504，並確認 Scheduler 會對 504 重試。

## 疑難排解
- 401/403：確認排程服務帳戶具備 `roles/run.invoker`，且 audience 與服務 URL 相符。
- 404：確認服務 URL 與 `/tasks/allocation` 路由已在部署版本中存在。
- 逾時：讓 Scheduler 嘗試截止時間與應用程式逾時（含 `TASK_TIMEOUT_SECONDS`）一致；Cloud Run 逾時請設定 ≥ Scheduler 截止時間。
- 冷啟動：在 Cloud Run 設定少量最小執行個體以降低啟動延遲。
