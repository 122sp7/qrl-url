---
title: "gcloud CLI Commands Reference"
status: "runbook"
updated: "2026-04-05"
tags: ["gcloud", "cloud-run", "cloud-scheduler", "ops"]
---

# gcloud CLI Commands Reference

Common operational commands for maintaining the `qrl-trading-api` Cloud Run service.

---

## Cloud Run — Revisions

### List all revisions

```powershell
gcloud run revisions list `
  --service=qrl-trading-api `
  --region=asia-southeast1 `
  --format="value(metadata.name)"
```

### Delete all revisions except the active one

```powershell
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
```

Replace `qrl-trading-api-00280-6jx` with the current active revision name.

---

## Cloud Scheduler — Rebalance Job

### Create the rebalance scheduler job

```bash
gcloud scheduler jobs create http rebalance-qrl \
  --schedule="*/5 * * * *" \
  --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/rebalance" \
  --oidc-service-account-email=scheduler@qrl-api.iam.gserviceaccount.com \
  --oidc-token-audience="https://qrl-trading-api-545492969490.asia-southeast1.run.app" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"profile":"default-qrl","dry_run":true}' \
  --location="asia-southeast1"
```

Runs every 5 minutes. Set `dry_run: false` to enable live execution.

---

## Related Runbooks

- [cloud-scheduler-oidc.md](cloud-scheduler-oidc.md) — Full OIDC setup for Cloud Scheduler → Cloud Run
