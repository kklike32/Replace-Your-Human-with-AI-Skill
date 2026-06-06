from __future__ import annotations

import platform
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from .app_context import get_active_app_context
from .chunker import ActivityChunker
from .config import TrackerConfig
from .events import ChunkSummary, Event, EventType, FinalPseudocode, ScreenshotRecord, Session
from .llm.base import LLMClient
from .ocr import OCRProcessor
from .privacy import (
    is_sensitive_ocr_text,
    is_sensitive_window_title,
    redact_text,
    should_capture_shortcut,
)
from .screenshot import capture_screenshot
from .storage.insforge_client import InsForgeClient
from .storage.local_sqlite import LocalSQLiteRepository
from .summarization import generate_final_pseudocode, summarize_activity_chunk
from .workflows import build_workflow_artifacts


@dataclass(slots=True)
class RecorderState:
    running: bool = False
    paused: bool = False
    session_id: str | None = None
    pressed_modifiers: set[str] = field(default_factory=set)


class SessionRecorder:
    def __init__(
        self,
        config: TrackerConfig,
        repository: LocalSQLiteRepository,
        llm_client: LLMClient,
        insforge_client: InsForgeClient | None = None,
    ) -> None:
        self.config = config
        self.repository = repository
        self.llm_client = llm_client
        self.insforge_client = insforge_client
        self.ocr = OCRProcessor(enabled=config.ocr_enabled)
        self.state = RecorderState()
        self._keyboard_listener = None
        self._mouse_listener = None
        self._chunker: ActivityChunker | None = None

    def run(self) -> str:
        self.config.ensure_directories()
        session = Session(
            sync_enabled=self.config.enable_cloud_sync,
            device_name=platform.node() or None,
            os_name=platform.system(),
        )
        session = self.repository.create_session(session)
        self.state.session_id = session.id
        self.state.running = True
        self._chunker = ActivityChunker(
            session_id=session.id,
            screenshot_interval_seconds=self.config.screenshot_interval_seconds,
            chunk_interval_seconds=self.config.chunk_interval_seconds,
        )

        if self.insforge_client and self.config.enable_cloud_sync:
            self._create_remote_session(session)

        app_name, window_title = get_active_app_context()
        start_event = self.repository.save_event(
            Event(
                session_id=session.id,
                event_type=EventType.SESSION_START,
                app_name=app_name,
                window_title=window_title,
                metadata={
                    "local_only_mode": self.config.local_only_mode,
                    "ocr_enabled": self.config.ocr_enabled,
                    "enable_cloud_sync": self.config.enable_cloud_sync,
                },
            )
        )
        self._chunker.add_event(start_event)
        self._start_input_listeners()

        try:
            while self.state.running:
                if self.state.paused:
                    time.sleep(0.1)
                    continue

                current = datetime.now(timezone.utc)
                if self._chunker.should_capture_screenshot(current):
                    self._record_snapshot(current)
                self._process_due_chunk(current)
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.state.running = False
        finally:
            self._shutdown()

        return str(session.id)

    def _create_remote_session(self, session: Session) -> None:
        try:
            created = self.insforge_client.create_session(
                {
                    "id": session.id,
                    "user_id": session.user_id,
                    "started_at": session.started_at.isoformat(),
                    "ended_at": None,
                    "session_name": session.session_name,
                    "device_name": session.device_name,
                    "os_name": session.os_name,
                }
            )
        except Exception:
            return
        session.cloud_id = created.get("id", session.id)
        session.synced = True
        self.repository.update_session(session)

    def _start_input_listeners(self) -> None:
        from pynput import keyboard, mouse

        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._mouse_listener = mouse.Listener(on_click=self._on_click)
        self._keyboard_listener.start()
        self._mouse_listener.start()

    def _shutdown(self) -> None:
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        if self._mouse_listener:
            self._mouse_listener.stop()

        if self.state.session_id is None:
            return

        app_name, window_title = get_active_app_context()
        stop_event = self.repository.save_event(
            Event(
                session_id=self.state.session_id,
                event_type=EventType.SESSION_STOP,
                app_name=app_name,
                window_title=window_title,
                metadata={"reason": "user_interrupt_or_stop"},
            )
        )
        if self._chunker:
            self._chunker.add_event(stop_event)
        self._flush_pending_chunk()

        summaries = self.repository.get_chunk_summaries(self.state.session_id)
        if summaries:
            final = self._save_final_pseudocode(
                generate_final_pseudocode(self.llm_client, summaries)
            )
            if self.insforge_client and self.config.enable_cloud_sync:
                self._upload_final_pseudocode(final)
            self._finalize_workflow_artifacts(final, summaries)
            self._purge_expired_raw_data(datetime.now(timezone.utc))

        session = self.repository.get_session(self.state.session_id)
        if session:
            session.ended_at = session.ended_at or datetime.now(timezone.utc)
            session.status = "stopped"
            self.repository.update_session(session)

    def _record_snapshot(self, current: datetime) -> None:
        assert self.state.session_id is not None
        assert self._chunker is not None

        app_name, window_title = get_active_app_context()
        window_event = self.repository.save_event(
            Event(
                session_id=self.state.session_id,
                event_type=EventType.ACTIVE_WINDOW,
                app_name=app_name,
                window_title=window_title,
                metadata={},
                timestamp=current,
            )
        )
        self._chunker.add_event(window_event)

        if is_sensitive_window_title(window_title):
            self._chunker.skip_screenshot(current)
            return

        image_path = capture_screenshot(self.config.screenshot_dir, self.state.session_id)
        screenshot_event = self.repository.save_event(
            Event(
                session_id=self.state.session_id,
                event_type=EventType.SCREENSHOT,
                app_name=app_name,
                window_title=window_title,
                metadata={"path": str(image_path), "uploaded": False},
                timestamp=current,
            )
        )
        screenshot_record = self.repository.save_screenshot(
            ScreenshotRecord(
                session_id=self.state.session_id,
                event_id=screenshot_event.id,
                local_path=str(image_path),
                captured_at=current,
            )
        )
        self._chunker.add_event(screenshot_event)
        self._chunker.mark_screenshot_captured(screenshot_record, current)

        text = self.ocr.extract_text(image_path)
        if text:
            screenshot_record.ocr_text = redact_text(text, max_len=500)
            self.repository.save_screenshot(screenshot_record)

        if text and not is_sensitive_ocr_text(text):
            ocr_event = self.repository.save_event(
                Event(
                    session_id=self.state.session_id,
                    event_type=EventType.OCR_TEXT,
                    app_name=app_name,
                    window_title=window_title,
                    metadata={"text": redact_text(text, max_len=500)},
                    timestamp=current,
                )
            )
            self._chunker.add_event(ocr_event)

    def _process_due_chunk(self, current: datetime) -> None:
        assert self._chunker is not None
        chunk = self._chunker.build_chunk(current)
        if chunk is None:
            return
        summary = self._save_chunk_summary(summarize_activity_chunk(self.llm_client, chunk))
        if self.insforge_client and self.config.enable_cloud_sync:
            self._upload_chunk_summary(summary)
        self._chunker.reset_chunk_buffer(current)
        self._purge_expired_raw_data(current)

    def _flush_pending_chunk(self) -> None:
        if not self._chunker:
            return
        current = datetime.now(timezone.utc)
        chunk = self._chunker.build_chunk(current, force=True)
        if chunk is None:
            return
        summary = self._save_chunk_summary(summarize_activity_chunk(self.llm_client, chunk))
        if self.insforge_client and self.config.enable_cloud_sync:
            self._upload_chunk_summary(summary)
        self._chunker.reset_chunk_buffer(current)
        self._purge_expired_raw_data(current)

    def _save_chunk_summary(self, summary: ChunkSummary) -> ChunkSummary:
        return self.repository.save_chunk_summary(summary)

    def _save_final_pseudocode(self, final: FinalPseudocode) -> FinalPseudocode:
        return self.repository.save_final_pseudocode(final)

    def _finalize_workflow_artifacts(
        self,
        final: FinalPseudocode,
        summaries: list[ChunkSummary],
    ) -> None:
        if not self.config.enable_workflow_insights:
            return
        artifacts = build_workflow_artifacts(
            final,
            summaries,
            enable_template_creation=self.config.enable_workflow_template_creation,
            enable_agent_handoff_drafts=self.config.enable_agent_handoff_drafts,
            handoff_threshold=self.config.agent_handoff_automation_score_threshold,
        )
        insight = self.repository.save_workflow_insight(artifacts.insight)
        if self.insforge_client and self.config.enable_cloud_sync:
            self._upload_workflow_insight(insight)

        if artifacts.template is not None:
            template = self.repository.save_workflow_template(artifacts.template)
            if self.insforge_client and self.config.enable_cloud_sync:
                self._upload_workflow_template(template)
            artifacts.search_index.template_id = template.id

        search_record = self.repository.save_workflow_search_index(artifacts.search_index)
        if self.insforge_client and self.config.enable_cloud_sync:
            self._upload_workflow_search_index_record(search_record)

        if artifacts.handoff_draft is not None:
            draft = self.repository.save_agent_handoff_draft(artifacts.handoff_draft)
            if self.insforge_client and self.config.enable_cloud_sync:
                self._upload_agent_handoff_draft(draft)

    def _upload_chunk_summary(self, summary: ChunkSummary) -> None:
        try:
            created = self.insforge_client.upload_chunk_summary(
                {
                    "id": summary.id,
                    "session_id": summary.session_id,
                    "chunk_index": summary.chunk_index,
                    "started_at": summary.started_at,
                    "ended_at": summary.ended_at,
                    "summary": summary.summary,
                    "observed_apps": summary.observed_apps,
                    "confidence": summary.confidence,
                }
            )
        except Exception:
            return
        self.repository.mark_chunk_summary_synced(summary.id, created.get("id"))

    def _upload_final_pseudocode(self, final: FinalPseudocode) -> None:
        try:
            created = self.insforge_client.upload_final_pseudocode(
                {
                    "id": final.id,
                    "session_id": final.session_id,
                    "pseudocode": final.pseudocode,
                    "plain_text": final.plain_text,
                    "suggestions": final.suggestions,
                }
            )
        except Exception:
            return
        self.repository.mark_final_pseudocode_synced(final.id, created.get("id"))

    def _upload_workflow_insight(self, insight) -> None:
        try:
            created = self.insforge_client.upload_workflow_insight(
                {
                    "id": insight.id,
                    "session_id": insight.session_id,
                    "summary": insight.summary,
                    "main_apps": insight.main_apps,
                    "detected_task_type": insight.detected_task_type,
                    "tags": insight.tags,
                    "automation_score": insight.automation_score,
                    "automation_reason": insight.automation_reason,
                    "recommended_next_action": insight.recommended_next_action,
                }
            )
        except Exception:
            return
        self.repository.mark_workflow_insight_synced(insight.id, created.get("id"))

    def _upload_workflow_template(self, template) -> None:
        try:
            created = self.insforge_client.upload_workflow_template(
                {
                    "id": template.id,
                    "session_id": template.session_id,
                    "title": template.title,
                    "description": template.description,
                    "category": template.category,
                    "tags": template.tags,
                    "pseudocode": template.pseudocode,
                    "plain_text": template.plain_text,
                    "created_from": template.created_from,
                }
            )
        except Exception:
            return
        self.repository.mark_workflow_template_synced(template.id, created.get("id"))

    def _upload_agent_handoff_draft(self, draft) -> None:
        try:
            created = self.insforge_client.upload_agent_handoff_draft(
                {
                    "id": draft.id,
                    "session_id": draft.session_id,
                    "template_id": draft.template_id,
                    "status": draft.status,
                    "proposed_action": draft.proposed_action,
                    "action_plan": draft.action_plan,
                    "requires_user_approval": draft.requires_user_approval,
                    "approved_at": draft.approved_at.isoformat() if draft.approved_at else None,
                    "executed_at": draft.executed_at.isoformat() if draft.executed_at else None,
                }
            )
        except Exception:
            return
        self.repository.mark_agent_handoff_draft_synced(draft.id, created.get("id"))

    def _upload_workflow_search_index_record(self, record) -> None:
        try:
            created = self.insforge_client.upload_search_index_record(
                {
                    "id": record.id,
                    "session_id": record.session_id,
                    "template_id": record.template_id,
                    "searchable_text": record.searchable_text,
                    "tags": record.tags,
                }
            )
        except Exception:
            return
        self.repository.mark_workflow_search_index_record_synced(record.id, created.get("id"))

    def _purge_expired_raw_data(self, current: datetime) -> None:
        if self.state.session_id is None:
            return
        cutoff = current - timedelta(seconds=self.config.raw_data_ttl_seconds)
        self.repository.purge_expired_raw_data(self.state.session_id, cutoff)

    def _normalize_key_name(self, key: object) -> str | None:
        key_str = str(key).replace("Key.", "").lower()
        if key_str.startswith("'") and key_str.endswith("'"):
            return key_str.strip("'")

        modifier_map = {
            "ctrl_l": "ctrl",
            "ctrl_r": "ctrl",
            "cmd": "cmd",
            "cmd_l": "cmd",
            "cmd_r": "cmd",
            "alt_l": "alt",
            "alt_r": "alt",
            "shift_l": "shift",
            "shift_r": "shift",
        }
        return modifier_map.get(key_str, key_str)

    def _on_key_press(self, key: object) -> None:
        key_name = self._normalize_key_name(key)
        if key_name in {"ctrl", "cmd", "alt", "shift"}:
            self.state.pressed_modifiers.add(key_name)
            return

        if key_name == "p" and {"ctrl", "shift"}.issubset(self.state.pressed_modifiers):
            self.state.paused = not self.state.paused
            if self.state.session_id is not None:
                session = self.repository.get_session(self.state.session_id)
                if session:
                    session.status = "paused" if self.state.paused else "running"
                    self.repository.update_session(session)

    def _on_key_release(self, key: object) -> None:
        key_name = self._normalize_key_name(key)
        if key_name in {"ctrl", "cmd", "alt", "shift"}:
            self.state.pressed_modifiers.discard(key_name)
            if self.state.paused or not self.state.session_id:
                return
            self._record_keyboard_key(
                key_name=key_name,
                kind="modifier",
                action="release",
            )
            return

        if self.state.paused or not self.state.session_id:
            return

        app_name, window_title = get_active_app_context()
        if is_sensitive_window_title(window_title):
            return

        kind = "printable" if key_name and len(key_name) == 1 else "special"
        event = self.repository.save_event(
            Event(
                session_id=self.state.session_id,
                event_type=EventType.KEYBOARD_KEY,
                app_name=app_name,
                window_title=window_title,
                metadata={
                    "key": key_name or "unknown",
                    "kind": kind,
                    "action": "release",
                    "modifiers": sorted(self.state.pressed_modifiers),
                },
            )
        )
        if self._chunker:
            self._chunker.add_event(event)

        if should_capture_shortcut(self.state.pressed_modifiers, key_name):
            shortcut_parts = sorted(self.state.pressed_modifiers) + [key_name or "unknown"]
            shortcut_event = self.repository.save_event(
                Event(
                    session_id=self.state.session_id,
                    event_type=EventType.KEYBOARD_SHORTCUT,
                    app_name=app_name,
                    window_title=window_title,
                    metadata={"shortcut": "+".join(shortcut_parts)},
                )
            )
            if self._chunker:
                self._chunker.add_event(shortcut_event)

    def _record_keyboard_key(self, key_name: str | None, kind: str, action: str) -> None:
        if self.state.session_id is None:
            return
        app_name, window_title = get_active_app_context()
        if is_sensitive_window_title(window_title):
            return
        event = self.repository.save_event(
            Event(
                session_id=self.state.session_id,
                event_type=EventType.KEYBOARD_KEY,
                app_name=app_name,
                window_title=window_title,
                metadata={
                    "key": key_name or "unknown",
                    "kind": kind,
                    "action": action,
                    "modifiers": sorted(self.state.pressed_modifiers),
                },
            )
        )
        if self._chunker:
            self._chunker.add_event(event)

    def _on_click(self, x: int, y: int, button: object, pressed: bool) -> None:
        if not pressed or self.state.paused or not self.state.session_id:
            return

        app_name, window_title = get_active_app_context()
        if is_sensitive_window_title(window_title):
            return

        event = self.repository.save_event(
            Event(
                session_id=self.state.session_id,
                event_type=EventType.MOUSE_CLICK,
                app_name=app_name,
                window_title=window_title,
                metadata={"x": x, "y": y, "button": str(button)},
            )
        )
        if self._chunker:
            self._chunker.add_event(event)
