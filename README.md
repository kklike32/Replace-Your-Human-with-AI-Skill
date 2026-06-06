# computer-usage-tracker

`computer-usage-tracker` is a privacy-first Python desktop prototype that:

- Tracks local computer usage during a work session
- Stores structured events and screenshot metadata
- Generates readable workflow pseudocode
- Suggests useful next steps

The app is local-first by design and can sync to InsForge as the backend of record.

## Why InsForge

InsForge is used for:

- PostgreSQL database for sessions/events/summaries
- Auth integration for future multi-user flows
- S3-compatible object storage for screenshots
- Future edge/serverless backend functions and AI gateway integration

For hackathon:
Use InsForge Cloud because it is faster to set up, easier to demo, and avoids local infrastructure issues.

For long-term:
Keep the code backend-agnostic through environment variables and the `InsForgeClient` abstraction. If privacy or cost becomes important, switch to the open-source self-hosted InsForge deployment without changing the app architecture.

## Architecture

- Local tracker runs on user machine
- Local SQLite is always written first
- InsForge sync is second (`tracker sync` or auto-sync when enabled)
- Screenshot files are kept locally and uploaded only if explicitly enabled

Core modules:

- `tracker.recorder`: keyboard/mouse listeners, app/window tracking, screenshot loop, pause/resume
- `tracker.storage.local_sqlite`: local fallback and primary write path
- `tracker.storage.insforge_client`: InsForge API wrapper
- `tracker.sync`: upload unsynced sessions/events/screenshots/summaries
- `tracker.pseudocode`: deterministic rule-based pseudocode generator
- `tracker.suggestions`: deterministic rule-based suggestion engine
- `tracker.agent`: future explicit-consent action agent placeholder

## Privacy Defaults

- `ENABLE_CLOUD_SYNC=false`
- `ENABLE_SCREENSHOT_UPLOAD=false`
- Tracks keyboard events (printable and special keys) with privacy filters
- Tries to avoid sensitive windows/password-like contexts
- Pause/resume tracking with `Ctrl+Shift+P`

This tool is intended for personal use with user consent.

## Setup

### Requirements

- Python 3.11+
- Tesseract OCR installed locally
  - macOS: `brew install tesseract`

### Install

```bash
pip install -e .
pip install -e .[dev]
```

### Environment

Copy `.env.example` to `.env` and edit values as needed.

```bash
INSFORGE_BASE_URL=
INSFORGE_PROJECT_ID=
INSFORGE_API_KEY=
INSFORGE_AUTH_TOKEN=
INSFORGE_STORAGE_BUCKET=session-screenshots
ENABLE_CLOUD_SYNC=false
ENABLE_SCREENSHOT_UPLOAD=false
LOCAL_DB_PATH=data/local_tracker.db
```

## CLI

Initialize backend setup artifacts:

```bash
tracker init-backend
```

Start tracking session:

```bash
tracker start
```

Stop running session (best effort):

```bash
tracker stop
```

Summarize latest session:

```bash
tracker summarize
```

Sync unsynced data to InsForge:

```bash
tracker sync
```

Export markdown summary:

```bash
tracker export --session-id <id> --format markdown
```

## Data Model

InsForge schema targets these tables:

- `users`
- `sessions`
- `events`
- `screenshots`
- `summaries`

Supported event types:

- `session_start`
- `session_stop`
- `mouse_click`
- `keyboard_shortcut`
- `active_window`
- `screenshot`
- `ocr_text`
- `pseudocode_generated`
- `suggestion_generated`

Screenshot object path format:

`users/{user_id_or_anonymous}/sessions/{session_id}/{timestamp}.png`

## Cloud vs Self-Hosted

- Hackathon: use InsForge Cloud
- Long-term: switch to self-hosted InsForge by updating environment variables; app architecture remains the same

## Tests

```bash
pytest
```

## Roadmap

- Improve platform-specific active window/process fidelity
- Add dashboard and backend function examples
- Add optional LLM adapters for pseudocode/suggestions
- Implement explicit-consent action execution layer in `tracker.agent`
