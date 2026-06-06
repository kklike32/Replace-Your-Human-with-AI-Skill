# InsForge Setup for computer-usage-tracker

## 1) Configure environment

Copy `.env.example` to `.env` and set:

- `INSFORGE_BASE_URL`
- `INSFORGE_PROJECT_ID`
- `INSFORGE_API_KEY`
- `INSFORGE_AUTH_TOKEN` (optional)
- `INSFORGE_STORAGE_BUCKET=session-screenshots`

## 2) Create database schema

Run SQL from `insforge_schema.sql` in your InsForge Postgres instance.

## 3) Create storage bucket

Create bucket: `session-screenshots`

## 4) Run the tracker locally first

```bash
tracker start
```

## 5) Enable sync when ready

```bash
ENABLE_CLOUD_SYNC=true tracker sync
```

To upload screenshots too:

```bash
ENABLE_CLOUD_SYNC=true ENABLE_SCREENSHOT_UPLOAD=true tracker sync
```

## Notes

- The app always writes to local SQLite first.
- Sync to InsForge is a second step for resilience when offline.
- Screenshot upload is disabled by default for privacy.
