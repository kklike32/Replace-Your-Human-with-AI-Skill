# computer-usage-tracker

`computer-usage-tracker` is a local-first Python desktop prototype that captures computer activity, summarizes short activity windows with an LLM, and produces a final pseudocode workflow for the full session.

## Architecture

Core flow:

- local screenshots every 2 seconds
- local mouse, keyboard, app/window, and OCR capture
- 6-second chunk builder
- LLM chunk summarization
- local summary persistence
- optional InsForge sync for chunk summaries only
- final session pseudocode generation
- optional InsForge sync for final pseudocode only

Relevant modules:

- `tracker.recorder`: session lifecycle, capture loop, chunk summarization, finalization
- `tracker.chunker`: in-memory 6-second chunk assembly
- `tracker.llm`: provider abstraction, mock provider, Vertex Gemini provider
- `tracker.summarization`: prompt-safe orchestration helpers
- `tracker.storage.local_sqlite`: local persistence for raw data and summaries
- `tracker.storage.insforge_client`: summary-only InsForge API wrapper
- `tracker.sync`: summary-only sync service

## Privacy-First Backend Design

- Raw data stays local in SQLite and the local screenshot directory.
- Screenshots are used only transiently for local chunk summarization.
- Gemini / Vertex may receive screenshots and local context for model analysis.
- InsForge receives only session metadata, detailed chunk summaries, final pseudocode, and optional suggestions.
- InsForge never receives screenshots, raw mouse coordinates, raw keyboard events, full OCR text, local event logs, or raw app/window streams.
- Users can disable cloud sync with `ENABLE_CLOUD_SYNC=false` or `tracker start --no-cloud-sync`.
- Users can switch away from Vertex/Gemini by implementing the `LLMClient` interface and selecting another provider.

## Setup

### Requirements

- Python 3.11+
- Tesseract OCR installed locally
  - macOS: `brew install tesseract`

### Install

```bash
python -m pip install -e .[dev]
python -m pip install -e .[vertex]
```

Install the `vertex` extra only when using `tracker start --llm-provider vertex_gemini`.

### Environment

Copy `.env.example` to `.env`.

Key variables:

```bash
SCREENSHOT_INTERVAL_SECONDS=2
CHUNK_INTERVAL_SECONDS=6
ENABLE_CLOUD_SYNC=false
UPLOAD_ONLY_SUMMARIES=true
LLM_PROVIDER=vertex_gemini
LLM_MODEL=gemini-1.5-pro
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=
INSFORGE_BASE_URL=
INSFORGE_PROJECT_ID=
INSFORGE_API_KEY=
INSFORGE_AUTH_TOKEN=
INSFORGE_SUMMARIES_TABLE=chunk_summaries
INSFORGE_FINAL_TABLE=final_pseudocode
LOCAL_DB_PATH=data/local_tracker.db
```

## CLI

Initialize backend artifacts:

```bash
tracker init-backend
```

Start tracking:

```bash
tracker start --llm-provider mock
tracker start --cloud-sync --llm-provider vertex_gemini
```

Generate final pseudocode from stored chunk summaries:

```bash
tracker summarize-final --session-id <session_id>
```

Sync summary-only records:

```bash
tracker sync-summaries --session-id <session_id>
tracker sync
```

Export final pseudocode:

```bash
tracker export --session-id <session_id>
```

## Remote Schema

InsForge stores only these tables:

- `sessions`
- `chunk_summaries`
- `final_pseudocode`

Use [`insforge_schema.sql`](/Users/keenan/Documents/AIPent/insforge_schema.sql) to create them.

## Tests

```bash
python -m pytest -q
```
