清除版本:
gcloud run revisions list `
  --service=qrl-trading-api `
  --region=asia-southeast1 `
  --format="value(metadata.name)" |
Where-Object { $_ -ne "qrl-trading-api-00280-6jx" } |
ForEach-Object {
  gcloud run revisions delete $_ `
    --region=asia-southeast1 `
    --quiet
}
