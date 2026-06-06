from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from .config import TrackerConfig
from .events import Event, EventType, Summary
from .pseudocode import PseudocodeGenerator
from .recorder import SessionRecorder
from .storage.insforge_client import InsForgeClient
from .storage.local_sqlite import LocalSQLiteRepository
from .suggestions import SuggestionEngine
from .sync import SyncService

app = typer.Typer(help="Track desktop usage sessions and summarize workflows.")
console = Console()


def _build_config(db_path: str | None) -> TrackerConfig:
    config = TrackerConfig.from_env()
    if db_path:
        config.db_path = Path(db_path)
    config.ensure_directories()
    return config


def _get_session_id(repository: LocalSQLiteRepository, session_id: str | None) -> str:
    if session_id:
        return session_id
    latest = repository.get_latest_session()
    chosen = latest.id if latest else None
    if chosen is None:
        raise typer.BadParameter("No sessions found.")
    return chosen


def _maybe_client(config: TrackerConfig) -> InsForgeClient | None:
    if not (config.enable_cloud_sync and config.has_insforge_credentials()):
        return None
    return InsForgeClient(
        base_url=str(config.insforge_base_url),
        api_key=str(config.insforge_api_key),
        auth_token=config.insforge_auth_token,
    )


def _schema_sql() -> str:
    return """-- InsForge schema for computer-usage-tracker
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,
    user_id UUID NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ NULL,
    session_name TEXT NULL,
    device_name TEXT NULL,
    os_name TEXT NULL,
    sync_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id),
    timestamp TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL,
    app_name TEXT NULL,
    window_title TEXT NULL,
    metadata JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS screenshots (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id),
    event_id UUID NULL REFERENCES events(id),
    storage_path TEXT NOT NULL,
    ocr_text TEXT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS summaries (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id),
    pseudocode TEXT NOT NULL,
    suggestions JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def _setup_markdown() -> str:
    return """# InsForge Setup

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
"""


@app.command("init-backend")
def init_backend(
    db_path: str | None = typer.Option(None, help="Path to local SQLite DB."),
) -> None:
    """Generate InsForge backend setup artifacts and print expected schema."""
    config = _build_config(db_path)
    schema = _schema_sql()
    setup_doc = _setup_markdown()

    Path("insforge_schema.sql").write_text(schema, encoding="utf-8")
    Path("INSFORGE_SETUP.md").write_text(setup_doc, encoding="utf-8")

    console.print(Panel.fit(schema, title="Expected InsForge Schema"))
    if config.has_insforge_credentials():
        console.print(
            "[green]InsForge env vars found.[/green] "
            "Automatic remote provisioning is backend-specific, so schema/setup files were generated."
        )
    else:
        console.print(
            "[yellow]Missing InsForge env vars.[/yellow] Generated `insforge_schema.sql` and `INSFORGE_SETUP.md`."
        )


@app.command()
def start(
    db_path: str | None = typer.Option(None, help="Path to local SQLite DB."),
    screenshot_interval: int = typer.Option(
        5,
        min=1,
        help="Screenshot interval in seconds.",
    ),
    ocr: bool = typer.Option(True, "--ocr/--no-ocr", help="Toggle OCR."),
    local_only: bool = typer.Option(
        True,
        "--local-only/--allow-remote",
        help="Local-only mode for this prototype.",
    ),
) -> None:
    """Start a new tracking session and record until Ctrl+C."""
    config = _build_config(db_path)
    config.screenshot_interval_seconds = screenshot_interval
    config.ocr_enabled = ocr
    config.local_only_mode = local_only
    repository = LocalSQLiteRepository(config.db_path)
    client = _maybe_client(config)
    recorder = SessionRecorder(config, repository, insforge_client=client)

    console.print("[bold green]Tracking started.[/bold green] Press Ctrl+C to stop.")
    session_id = recorder.run()
    console.print(f"[bold]Session stopped:[/bold] {session_id}")

    if client:
        result = SyncService(repository, client, config).sync_all()
        console.print(f"[green]Cloud sync complete:[/green] {result}")


@app.command()
def stop(
    session_id: str | None = typer.Option(None, help="Session ID to stop."),
    db_path: str | None = typer.Option(None, help="Path to local SQLite DB."),
) -> None:
    """Stop a running session by ID (best effort)."""
    config = _build_config(db_path)
    repository = LocalSQLiteRepository(config.db_path)
    active = repository.get_active_session()
    target_session_id = session_id or (active.id if active else None)

    if target_session_id is None:
        console.print("[yellow]No running session found.[/yellow]")
        raise typer.Exit(0)

    repository.save_event(
        Event(
            session_id=target_session_id,
            event_type=EventType.SESSION_STOP,
            metadata={"reason": "manual_stop_command"},
        )
    )

    session = repository.get_session(target_session_id)
    if session:
        session.status = "stopped"
        session.ended_at = datetime.now(timezone.utc)
        repository.update_session(session)
    console.print(f"[bold]Marked session as stopped:[/bold] {target_session_id}")


@app.command()
def summarize(
    session_id: str | None = typer.Option(None, help="Session ID to summarize."),
    db_path: str | None = typer.Option(None, help="Path to local SQLite DB."),
) -> None:
    """Summarize a session into pseudocode and suggestions."""
    config = _build_config(db_path)
    repository = LocalSQLiteRepository(config.db_path)
    chosen_session_id = _get_session_id(repository, session_id)

    events = repository.get_events(chosen_session_id)
    pseudocode = PseudocodeGenerator().generate(events)
    suggestions = SuggestionEngine().suggest(events, pseudocode)
    summary = Summary(
        session_id=chosen_session_id,
        pseudocode=pseudocode,
        suggestions=suggestions,
    )
    repository.save_summary(summary)
    repository.save_event(
        Event(session_id=chosen_session_id, event_type=EventType.PSEUDOCODE_GENERATED)
    )
    repository.save_event(
        Event(session_id=chosen_session_id, event_type=EventType.SUGGESTION_GENERATED)
    )

    console.print(Panel.fit(pseudocode, title=f"Session {chosen_session_id} Pseudocode"))
    suggestion_text = "\n".join(
        f"Suggestion {idx}: {suggestion}"
        for idx, suggestion in enumerate(suggestions, start=1)
    )
    console.print(Panel.fit(suggestion_text, title="Suggestions"))

    client = _maybe_client(config)
    if client:
        result = SyncService(repository, client, config).sync_all()
        console.print(f"[green]Cloud sync complete:[/green] {result}")


@app.command()
def sync(
    db_path: str | None = typer.Option(None, help="Path to local SQLite DB."),
) -> None:
    """Upload unsynced local data to InsForge."""
    config = _build_config(db_path)
    if not config.enable_cloud_sync:
        console.print("[yellow]Cloud sync is disabled. Set ENABLE_CLOUD_SYNC=true.[/yellow]")
        raise typer.Exit(0)

    client = _maybe_client(config)
    if client is None:
        raise typer.BadParameter("Missing InsForge credentials in environment.")

    repository = LocalSQLiteRepository(config.db_path)
    result = SyncService(repository, client, config).sync_all()
    console.print(f"[bold green]Sync complete:[/bold green] {result}")


@app.command()
def export(
    session_id: str = typer.Option(..., help="Session ID to export."),
    format: str = typer.Option("markdown", help="Export format."),
    db_path: str | None = typer.Option(None, help="Path to local SQLite DB."),
    output: str | None = typer.Option(None, help="Output path override."),
) -> None:
    """Export session summary to markdown."""
    config = _build_config(db_path)
    repository = LocalSQLiteRepository(config.db_path)

    if format.lower() != "markdown":
        raise typer.BadParameter("Only markdown export is supported in this prototype.")

    summary = repository.get_summary(session_id)
    if summary is None:
        events = repository.get_events(session_id)
        pseudocode = PseudocodeGenerator().generate(events)
        suggestions = SuggestionEngine().suggest(events, pseudocode)
    else:
        pseudocode = summary.pseudocode
        suggestions = summary.suggestions

    if output:
        output_path = Path(output)
    else:
        output_path = config.export_dir / f"session_{session_id}_summary.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    suggestion_lines = "\n".join(
        f"- Suggestion {idx}: {text}" for idx, text in enumerate(suggestions, start=1)
    )
    markdown = (
        f"# Session {session_id} Summary\n\n"
        f"## Pseudocode\n\n{pseudocode}\n\n"
        f"## Suggestions\n\n{suggestion_lines}\n"
    )
    output_path.write_text(markdown, encoding="utf-8")
    console.print(f"[bold green]Exported:[/bold green] {output_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
