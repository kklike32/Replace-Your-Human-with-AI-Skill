# InsForge Setup

## 1) Configure environment

Copy `.env.example` to `.env` and set:

- `INSFORGE_BASE_URL`
- `INSFORGE_PROJECT_ID`
- `INSFORGE_API_KEY`
- `INSFORGE_AUTH_TOKEN` (optional)
- `INSFORGE_STORAGE_BUCKET=session-screenshots`

## 2) Create schema

Run SQL from `insforge_schema.sql` in your InsForge Postgres project.

## 3) Create storage bucket

Create bucket: `session-screenshots`.

## 4) Run tracker

Use local-first mode by default:

```bash
tracker start
```

Enable cloud sync when ready:

```bash
ENABLE_CLOUD_SYNC=true ENABLE_SCREENSHOT_UPLOAD=true tracker sync
```

## Notes

- This project writes to local SQLite first, then syncs to InsForge.
- Screenshot upload remains disabled unless explicitly enabled.
