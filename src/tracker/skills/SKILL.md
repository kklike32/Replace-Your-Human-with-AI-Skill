---
name: computer-use-executor
description: Execute user-provided or file-provided step-by-step workflows live through the OpenAI Computer Use plugin or an explicitly available Computer Use desktop/browser-control tool. Use when Codex needs to read a runbook, checklist, generated report, "steps of execution," SOP, QA script, browser task, GUI workflow, or similar instructions and perform the actions interactively by observing the screen, clicking, typing, navigating, verifying each step, handling approvals, and reporting progress.
---

# Computer Use Executor

## Overview

Use this skill to turn written execution steps into a live, verified computer-control run. Prefer the OpenAI Computer Use plugin whenever it is available; do not silently substitute unrelated automation tools unless the user explicitly permits that fallback.

## Tool Gate

Before acting, locate the Computer Use capability:

1. Inspect the active tools for an OpenAI Computer Use, computer-use, desktop-control, browser-control, screenshot/click/type, or equivalent tool.
2. If deferred tool discovery is available, search for `OpenAI Computer Use`, `computer use`, `desktop control`, `screenshot click type`, and the target surface name.
3. If no Computer Use-capable tool is available, tell the user the required plugin/tool is unavailable and ask them to enable or install it. Do not proceed with shell scripts, generic web browsing, or a different plugin as a substitute unless the user approves that change.

## Execution Workflow

1. Read the source steps from the user message, attached artifact, generated report, web page, document, spreadsheet, or local file the user identifies.
2. Extract the actionable sequence. Preserve order, group tiny substeps when useful, and call out missing prerequisites such as target URL, app name, account, files, or required credentials.
3. Make a short runbook before acting when the workflow has more than a few steps or includes risk. Include assumptions, likely checkpoints, and any actions requiring approval.
4. Open or focus the target surface with Computer Use. Observe the screen before the first action and after each meaningful action.
5. Execute one atomic action at a time: click, type, select, scroll, navigate, drag, upload, download, or wait.
6. Verify completion after each step using the latest observation. Prefer visible UI state, page text, confirmation messages, file existence, or explicit success indicators.
7. Adapt when the UI differs from the steps. Reconcile visible state with the intended outcome, then continue using the smallest reasonable correction.
8. Keep concise progress notes for the user, especially at decision points, failures, completed milestones, and final outcome.

## Human Approval Points

Pause and ask the user before:

- Entering, exposing, saving, or transmitting passwords, API keys, recovery codes, or private tokens. Let the user type secrets directly whenever possible.
- Passing MFA, CAPTCHA, security prompts, identity checks, or consent screens.
- Making purchases, payments, trades, account changes, deletions, irreversible edits, production deploys, or messages sent to real people.
- Accepting legal terms, changing privacy/security settings, or acting on high-stakes medical, legal, financial, or employment decisions.
- Downloading or uploading sensitive files when the destination or access level is unclear.

## Failure Handling

If a step fails, observe the current screen, name the mismatch, and try at most two targeted corrections before asking for help. If the Computer Use tool cannot access the target app, loses session state, or cannot interact with a required control, report the blocker with the last verified completed step.

## Completion

Finish with:

- Steps completed.
- Steps skipped or blocked, with reasons.
- Artifacts created, changed, downloaded, or submitted.
- Any manual follow-up the user must perform.
