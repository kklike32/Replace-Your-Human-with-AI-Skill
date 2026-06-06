# Privacy-First Backend Setup

## 1) Configure environment

Copy `.env.example` to `.env` and set:

- `INSFORGE_BASE_URL`
- `INSFORGE_PROJECT_ID`
- `INSFORGE_API_KEY`
- `INSFORGE_AUTH_TOKEN` if needed
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_APPLICATION_CREDENTIALS`

## 2) Create schema

Run SQL from `insforge_schema.sql` in your InsForge project.

Remote tables:

- `sessions`
- `chunk_summaries`
- `final_pseudocode`

## 3) Privacy contract

InsForge receives only:

- session metadata
- chunk summaries
- final pseudocode
- optional suggestions

InsForge never receives:

- screenshots
- OCR text
- mouse coordinates
- keyboard events
- raw local event logs

Chunk summaries and final pseudocode remain in local SQLite and are also sent to InsForge when cloud sync is enabled.

## 4) Run tracker

Local-only:

```bash
tracker start --llm-provider mock
```

Cloud summary sync:

```bash
tracker start --cloud-sync --llm-provider vertex_gemini
```
