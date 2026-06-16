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
- **Built for agent handoff.** The end state is not a recording. It is a reusable AI Skill you can hand to Codex, Cowork, or Cursor to replay live.

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
Approved AI Skill (workflow steps)
      ↓
Upload to Codex / Cowork / Cursor + Computer Use
      ↓
Agent recreates the workflow live (open tabs, click, type, navigate)
      ↓
InsForge workflow memory (optional team sharing)
```

1. Start recording from BuddyBar.
2. Perform the workflow normally.
3. Activity is captured locally.
4. The system generates chunks and summaries.
5. Final pseudocode and workflow steps are produced.
6. The user reviews the preview.
7. Export or copy the workflow steps into an AI agent with Computer Use.
8. The agent recreates the captured actions on a live desktop or browser.
9. Optionally sync the approved summary to InsForge for team reuse.

## Replay the Workflow with an AI Agent

This is the end state most people care about: **you do the work once, then an AI agent does it again for you.**

After a session finishes, BuddyBar shows a **Generated Steps Preview** — numbered workflow steps distilled from everything that was captured (apps opened, tabs switched, buttons clicked, fields filled, exports run, and anything you narrated out loud). Those steps are the handoff artifact. They are not a video replay; they are instructions an agent can follow.

### What you get

| Output | Where it lives | What it contains |
|--------|----------------|------------------|
| **Workflow steps preview** | BuddyBar UI after Stop | Plain-text numbered steps ready to copy |
| **Session export** | `data/exports/session_<id>_summary.md` | Pseudocode, plain-text steps, automation suggestions |
| **Computer Use executor skill** | `src/tracker/skills/SKILL.md` | Agent instructions for live desktop/browser control |

The bundled `SKILL.md` tells the agent *how* to execute step-by-step workflows safely (observe screen, click, type, verify each step, pause for approvals). Your captured session provides *what* to do.

### How to recreate the workflow

1. **Capture once** — Start BuddyBar, perform the workflow, Stop, and review the generated steps. Edit anything that looks wrong before handing off.
2. **Export the steps** (optional but recommended):

   ```bash
   python -m tracker.cli export --session-id <session_id>
   ```

   Or copy the preview text directly from BuddyBar.

3. **Open Codex, Cowork, Cursor Agent, or any tool with Computer Use** — the agent needs the ability to observe the screen and perform clicks, typing, and navigation (OpenAI Computer Use, desktop control, browser control, or equivalent).
4. **Upload or paste both artifacts:**
   - Your exported workflow steps (`session_<id>_summary.md` or the BuddyBar preview)
   - The executor skill at `src/tracker/skills/SKILL.md` (or install it as a Cursor Agent Skill)
5. **Prompt the agent**, for example:

   > Follow the workflow steps in the attached summary. Use Computer Use to recreate each action in order — open the same apps, switch to the right tabs, click the same controls, fill the same fields, and verify each step before moving on.

6. **The agent runs the workflow live** — opening tabs, clicking menus, typing into forms, exporting files, and reporting progress step by step. It adapts if the UI has changed slightly, and pauses before sensitive actions (passwords, payments, MFA).

That is the full loop: **human performs once → system extracts structured steps → AI agent replays on a real machine.**

### Example

You capture a Friday report workflow: open an internal dashboard, export a CSV, clean it in a spreadsheet, cross-check totals, paste into a slide deck.

The generated steps might look like:

```text
1. Open Chrome and navigate to the ops dashboard.
2. Export the weekly metrics CSV from the Reports panel.
3. Open the spreadsheet and remove duplicate rows in column A.
4. Verify totals in the Summary tab match the dashboard.
5. Paste the final table into the weekly report slide.
```

Upload those steps plus `SKILL.md` to Codex or Cowork. The agent opens Chrome, finds the dashboard, clicks Export, switches to the spreadsheet app, and continues through the list — the same actions you tracked, now executed by the agent.

### Team reuse

Sync the approved workflow to InsForge so teammates can download the same steps and run them on their own machine with their own Codex, Cowork, or Cursor session. One person captures; everyone can replay.

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
6. Export or copy the steps, then upload them to Codex, Cowork, or Cursor with Computer Use to recreate the workflow (see [Replay the Workflow with an AI Agent](#replay-the-workflow-with-an-ai-agent)).

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
- `src/tracker/skills/SKILL.md` - Computer Use executor skill for agent replay
- `src/tracker/storage/local_sqlite.py` - local persistence
- `src/tracker/storage/insforge_client.py` - InsForge sync client
- `insforge_schema.sql` - backend schema reference

## Closing

**Replace Your Human with AI Skill is not a screen recorder. It is a workflow memory layer for turning human work into reusable AI skills — and replaying them with Codex, Cowork, or any Computer Use agent.**
