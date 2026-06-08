# Replace Your Human with AI Skill

**Do the work once. Turn it into a reusable AI Skill.**

A native macOS workflow-capture product that records real desktop work, captures voice context, and turns repetitive tasks into structured, shareable AI skills.

> Winner of the Agentic Dev Tools Hackathon in San Francisco.

![Platform](https://img.shields.io/badge/platform-macOS-111827)
![Privacy](https://img.shields.io/badge/privacy-local--first-0f766e)
![Backend](https://img.shields.io/badge/backend-InsForge-1d4ed8)

This repository contains the native macOS app, local workflow tracker, voice-aware capture pipeline, and InsForge sync layer for turning human workflows into reusable team skills.

## The Problem

Companies lose operational knowledge every day.

People click through dashboards, clean spreadsheets, answer tickets, move data between tools, and generate reports. That work is valuable, repetitive, and often automation-ready, but the process usually disappears the moment the task is done.

Teams then pay for the same knowledge again through SOP writing, retraining, shadowing, and repeated manual execution.

## The Product

**Replace Your Human with AI Skill** turns real desktop work into reusable AI-ready skills.

It captures on-screen activity, app context, OCR, mouse and keyboard events, and optional voice narration locally on the Mac. After the session ends, it generates structured workflow steps, pseudocode, automation hints, and a handoff-ready skill that can be reviewed before syncing.

The result is not a screen recording. It is a reusable workflow artifact that a teammate or future AI agent can understand and execute.

## What Makes It Different

- **Native macOS menubar experience.** Fast to launch, easy to keep running.
- **One-click capture.** Start the workflow and work normally.
- **Voice-aware capture.** Spoken context can be recorded alongside the workflow.
- **Local-first privacy.** Sensitive raw activity stays on-device.
- **Review before sync.** Nothing approved for cloud memory unless the user chooses it.
- **Structured workflow knowledge.** Output is useful workflow logic, not raw surveillance footage.
- **InsForge-backed memory.** Approved workflows can be stored, searched, and shared through [InsForge](https://insforge.dev).
- **Team collaboration layer.** Skills can be shared, accessed, and reused across a team.
- **Built for agent handoff.** The end state is not a recording. It is a reusable AI Skill.

## Product Flow

```text
Human workflow
      ↓
BuddyBar local capture
      ↓
Screenshots + OCR + app context + events + voice
      ↓
Chunk summaries
      ↓
Final workflow pseudocode
      ↓
Review preview
      ↓
Approved AI Skill
      ↓
InsForge workflow memory
```

1. Start recording from BuddyBar.
2. Perform the workflow normally.
3. Activity is captured locally.
4. The system generates chunks and summaries.
5. Final pseudocode and workflow steps are produced.
6. The user reviews the preview.
7. The approved summary can sync to InsForge.
8. The workflow becomes a reusable AI Skill.

## Demo Use Case

Imagine an operations worker building the same weekly report every Friday.

They open internal dashboards, export data, clean a spreadsheet, cross-check values, narrate what they are doing, and paste results into a final report. Replace Your Human with AI Skill captures the workflow locally, extracts the structure, and outputs a reusable skill with:

- workflow steps
- pseudocode
- automation hints
- handoff-ready records

That makes the value obvious for SOP generation, onboarding, operations documentation, and future AI agent automation.

## Privacy, Clearly

Local only:

- screenshots
- voice/audio recordings
- OCR text
- keyboard and mouse events
- raw logs
- SQLite DB

Syncable only after review:

- session metadata
- chunk summaries
- final pseudocode
- workflow insights
- reusable templates
- agent handoff records

Sync is explicit. It is never automatic.

## BuddyBar

`BuddyBar` is the main product surface and lives in `macos/BuddyBar`.

It is a native macOS menubar app that lets the user:

- start capture
- stop and save a session
- review generated workflow steps
- capture spoken narration during the workflow
- sync an approved result to InsForge
- open local data and exports

The capture engine runs through the local Python tracker underneath, but the user experience is designed around the Mac menu bar.

## Team Skills Layer

[InsForge](https://insforge.dev) is the backend for approved workflow memory, search, and sharing.

Approved skills can be synced to the team workspace, where teammates can discover, download, and reuse workflow skills across machines.

That means one person can perform a workflow once, review the generated skill, publish it, and let another teammate run that same skill on their own machine.

- Live app: <https://r34ir5jz.insforge.site/sign-in?redirect=%2F>
- Frontend/backend code: [replaceyourhuman-back](https://github.com/Alcray/replaceyourhuman-back/tree/main)

Sync remains explicit. Only reviewed, structured workflow outputs are eligible to sync.

## Quick Start

### 1. Create the environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Optional Vertex support:

```bash
python -m pip install -e '.[vertex]'
```

### 2. Install Tesseract

```bash
brew install tesseract
```

### 3. Create `.env`

```bash
cp .env.example .env
```

### 4. Launch BuddyBar

```bash
cd macos/BuddyBar
swift run
```

On first launch, macOS will ask for **Screen Recording** and **Accessibility** permissions.

## Usage

### Local-only flow

1. Launch BuddyBar.
2. Click **Start**.
3. Perform the workflow normally, with optional voice narration.
4. Click **Stop**.
5. Review the generated workflow preview.

### InsForge sync flow

Add the relevant InsForge values to `.env`:

```bash
INSFORGE_BASE_URL=
INSFORGE_PROJECT_ID=
INSFORGE_API_KEY=
INSFORGE_AUTH_TOKEN=
INSFORGE_CURRENT_USER_ID=
```

Then complete a session and use **Sync Preview to InsForge** from BuddyBar.

For team workflows, approved skills can then be accessed through the web app, shared across the team, and reused on another machine.

## CLI

BuddyBar is the main product experience. The CLI is available as the underlying control surface when you want direct access.

Start capture:

```bash
python -m tracker.cli start
```

Start with explicit cloud sync enabled:

```bash
python -m tracker.cli start --cloud-sync --visibility private
```

Generate the final summary:

```bash
python -m tracker.cli summarize
```

Export a session:

```bash
python -m tracker.cli export --session-id <session_id>
```

Sync unsynced records:

```bash
python -m tracker.cli sync
```

## Project Layout

- `macos/BuddyBar` - native macOS menubar app
- `desktop` - Tauri desktop dashboard
- `src/tracker/cli.py` - CLI entrypoint
- `src/tracker/recorder.py` - capture loop and workflow generation pipeline
- `src/tracker/storage/local_sqlite.py` - local persistence
- `src/tracker/storage/insforge_client.py` - InsForge sync client
- `insforge_schema.sql` - backend schema reference

## Closing

**Replace Your Human with AI Skill is not a screen recorder. It is a workflow memory layer for turning human work into reusable AI skills.**
