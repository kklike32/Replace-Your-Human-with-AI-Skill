from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .config import TrackerConfig
from .llm import build_llm_client
from .recorder import SessionRecorder
from .storage.insforge_client import InsForgeClient
from .storage.local_sqlite import LocalSQLiteRepository
from .summarization import generate_final_pseudocode
from .sync import SyncService

app = typer.Typer(help="Track desktop usage sessions and summarize workflows.")
console = Console()


def _build_config(
    db_path: Optional[str],
    cloud_sync: Optional[bool] = None,
    llm_provider: Optional[str] = None,
    screenshot_interval: Optional[int] = None,
    chunk_interval: Optional[int] = None,
) -> TrackerConfig:
    config = TrackerConfig.from_env()
    if db_path:
        config.db_path = Path(db_path)
    if cloud_sync is not None:
        config.enable_cloud_sync = cloud_sync
    if llm_provider:
        config.llm_provider = llm_provider
    if screenshot_interval is not None:
        config.screenshot_interval_seconds = screenshot_interval
    if chunk_interval is not None:
        config.chunk_interval_seconds = chunk_interval
    config.ensure_directories()
    return config


def _get_session_id(repository: LocalSQLiteRepository, session_id: Optional[str]) -> str:
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
    return InsForgeClient.from_config(config)


def _schema_sql() -> str:
    return """create table if not exists sessions (
  id uuid primary key,
  user_id uuid nullable,
  started_at timestamptz not null,
  ended_at timestamptz nullable,
  session_name text nullable,
  device_name text nullable,
  os_name text nullable,
  created_at timestamptz default now()
);

create table if not exists chunk_summaries (
  id uuid primary key,
  session_id uuid references sessions(id),
  chunk_index integer not null,
  started_at timestamptz not null,
  ended_at timestamptz not null,
  summary text not null,
  observed_apps jsonb nullable,
  confidence text nullable,
  created_at timestamptz default now()
);

create table if not exists final_pseudocode (
  id uuid primary key,
  session_id uuid references sessions(id),
  pseudocode jsonb not null,
  plain_text text not null,
  suggestions jsonb nullable,
  created_at timestamptz default now()
);
"""


def _setup_markdown() -> str:
    return """# Privacy-First Backend Setup

## Remote data model

InsForge stores only:

- session metadata
- 6-second chunk summaries
- final pseudocode
- optional suggestions in final pseudocode

InsForge does not store raw screenshots, OCR text, mouse events, keyboard events, or local event logs.

## Environment

Copy `.env.example` to `.env` and set the InsForge and Vertex values you need.

## Schema

Run SQL from `insforge_schema.sql` in your InsForge project.

## Usage

Start local capture:

```bash
tracker start --llm-provider mock
```

Enable remote summary sync:

```bash
tracker start --cloud-sync --llm-provider vertex_gemini
```
"""


@app.command("init-backend")
def init_backend(
    db_path: Optional[str] = typer.Option(None, help="Path to local SQLite DB."),
) -> None:
    """Generate InsForge backend setup artifacts and print expected schema."""
    config = _build_config(db_path)
    Path("insforge_schema.sql").write_text(_schema_sql(), encoding="utf-8")
    Path("INSFORGE_SETUP.md").write_text(_setup_markdown(), encoding="utf-8")

    console.print(Panel.fit(_schema_sql(), title="Expected InsForge Schema"))
    if config.has_insforge_credentials():
        console.print("[green]InsForge env vars found.[/green] Setup artifacts regenerated.")
    else:
        console.print("[yellow]Missing InsForge env vars.[/yellow] Setup artifacts regenerated.")


@app.command()
def start(
    db_path: Optional[str] = typer.Option(None, help="Path to local SQLite DB."),
    screenshot_interval: Optional[int] = typer.Option(
        None,
        min=1,
        help="Screenshot interval in seconds. Defaults to env.",
    ),
    chunk_interval: Optional[int] = typer.Option(
        None,
        min=1,
        help="Chunk interval in seconds. Defaults to env.",
    ),
    ocr: bool = typer.Option(True, "--ocr/--no-ocr", help="Toggle OCR."),
    cloud_sync: bool = typer.Option(False, "--cloud-sync", help="Enable cloud sync for this run."),
    no_cloud_sync: bool = typer.Option(
        False,
        "--no-cloud-sync",
        help="Disable cloud sync for this run.",
    ),
    llm_provider: Optional[str] = typer.Option(
        None,
        help="LLM provider override, for example `vertex_gemini` or `mock`.",
    ),
) -> None:
    """Start a new tracking session and record until Ctrl+C."""
    cloud_sync_override: Optional[bool] = None
    if cloud_sync and no_cloud_sync:
        raise typer.BadParameter("Choose either --cloud-sync or --no-cloud-sync.")
    if cloud_sync:
        cloud_sync_override = True
    if no_cloud_sync:
        cloud_sync_override = False
    config = _build_config(
        db_path,
        cloud_sync=cloud_sync_override,
        llm_provider=llm_provider,
        screenshot_interval=screenshot_interval,
        chunk_interval=chunk_interval,
    )
    config.ocr_enabled = ocr
    repository = LocalSQLiteRepository(config.db_path)
    client = _maybe_client(config)
    llm_client = build_llm_client(config, config.llm_provider)
    recorder = SessionRecorder(
        config,
        repository,
        llm_client=llm_client,
        insforge_client=client,
    )

    console.print("[bold green]Tracking started.[/bold green] Press Ctrl+C to stop.")
    session_id = recorder.run()
    console.print(f"[bold]Session stopped:[/bold] {session_id}")

    final = repository.get_final_pseudocode(session_id)
    if final:
        console.print(Panel.fit(final.plain_text, title=f"Session {session_id} Final Pseudocode"))


@app.command("summarize-final")
def summarize_final(
    session_id: Optional[str] = typer.Option(None, help="Session ID to summarize."),
    db_path: Optional[str] = typer.Option(None, help="Path to local SQLite DB."),
    llm_provider: Optional[str] = typer.Option(None, help="LLM provider override."),
) -> None:
    """Generate final pseudocode from stored chunk summaries."""
    config = _build_config(db_path, llm_provider=llm_provider)
    repository = LocalSQLiteRepository(config.db_path)
    chosen_session_id = _get_session_id(repository, session_id)
    summaries = repository.get_chunk_summaries(chosen_session_id)
    if not summaries:
        raise typer.BadParameter(f"No chunk summaries found for session {chosen_session_id}.")

    final = generate_final_pseudocode(build_llm_client(config, config.llm_provider), summaries)
    repository.save_final_pseudocode(final)

    client = _maybe_client(config)
    if client:
        SyncService(repository, client, config).sync_session(chosen_session_id)
    console.print(Panel.fit(final.plain_text, title=f"Session {chosen_session_id} Final Pseudocode"))


@app.command()
def summarize(
    session_id: Optional[str] = typer.Option(None, help="Session ID to summarize."),
    db_path: Optional[str] = typer.Option(None, help="Path to local SQLite DB."),
    llm_provider: Optional[str] = typer.Option(None, help="LLM provider override."),
) -> None:
    """Backward-compatible alias for summarize-final."""
    summarize_final(session_id=session_id, db_path=db_path, llm_provider=llm_provider)


@app.command("sync-summaries")
def sync_summaries(
    session_id: str = typer.Option(..., help="Session ID to sync."),
    db_path: Optional[str] = typer.Option(None, help="Path to local SQLite DB."),
) -> None:
    """Upload chunk summaries and final pseudocode for one session."""
    config = _build_config(db_path, cloud_sync=True)
    client = _maybe_client(config)
    if client is None:
        raise typer.BadParameter("Missing InsForge credentials in environment.")
    repository = LocalSQLiteRepository(config.db_path)
    result = SyncService(repository, client, config).sync_session(session_id)
    console.print(f"[bold green]Summary sync complete:[/bold green] {result}")


@app.command()
def sync(
    db_path: Optional[str] = typer.Option(None, help="Path to local SQLite DB."),
) -> None:
    """Upload unsynced sessions, chunk summaries, and final pseudocode."""
    config = _build_config(db_path, cloud_sync=True)
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
    db_path: Optional[str] = typer.Option(None, help="Path to local SQLite DB."),
    output: Optional[str] = typer.Option(None, help="Output path override."),
) -> None:
    """Export final pseudocode summary to markdown."""
    config = _build_config(db_path)
    repository = LocalSQLiteRepository(config.db_path)

    if format.lower() != "markdown":
        raise typer.BadParameter("Only markdown export is supported in this prototype.")

    final = repository.get_final_pseudocode(session_id)
    if final is None:
        raise typer.BadParameter(f"No final pseudocode found for session {session_id}.")

    output_path = Path(output) if output else config.export_dir / f"session_{session_id}_summary.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suggestion_lines = "\n".join(
        f"- Suggestion {idx}: {text}" for idx, text in enumerate(final.suggestions, start=1)
    )
    markdown = (
        f"# Session {session_id} Summary\n\n"
        f"## Pseudocode\n\n{final.plain_text}\n\n"
        f"## Suggestions\n\n{suggestion_lines or '- None'}\n"
    )
    output_path.write_text(markdown, encoding="utf-8")
    console.print(f"[bold green]Exported:[/bold green] {output_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
