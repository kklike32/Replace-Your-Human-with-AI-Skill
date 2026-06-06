from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class TrackerConfig:
    db_path: Path = Path("data/local_tracker.db")
    screenshot_dir: Path = Path("data/screenshots")
    export_dir: Path = Path("data/exports")
    screenshot_interval_seconds: int = 5
    ocr_enabled: bool = True
    local_only_mode: bool = True
    enable_cloud_sync: bool = False
    enable_screenshot_upload: bool = False
    insforge_base_url: str | None = None
    insforge_project_id: str | None = None
    insforge_api_key: str | None = None
    insforge_auth_token: str | None = None
    insforge_storage_bucket: str = "session-screenshots"

    @classmethod
    def from_env(cls) -> TrackerConfig:
        load_dotenv()

        def as_bool(value: str | None, default: bool) -> bool:
            if value is None:
                return default
            return value.strip().lower() in {"1", "true", "yes", "on"}

        return cls(
            db_path=Path(os.getenv("LOCAL_DB_PATH", "data/local_tracker.db")),
            enable_cloud_sync=as_bool(os.getenv("ENABLE_CLOUD_SYNC"), False),
            enable_screenshot_upload=as_bool(os.getenv("ENABLE_SCREENSHOT_UPLOAD"), False),
            insforge_base_url=os.getenv("INSFORGE_BASE_URL"),
            insforge_project_id=os.getenv("INSFORGE_PROJECT_ID"),
            insforge_api_key=os.getenv("INSFORGE_API_KEY"),
            insforge_auth_token=os.getenv("INSFORGE_AUTH_TOKEN"),
            insforge_storage_bucket=os.getenv(
                "INSFORGE_STORAGE_BUCKET",
                "session-screenshots",
            ),
        )

    def has_insforge_credentials(self) -> bool:
        return bool(self.insforge_base_url and self.insforge_api_key and self.insforge_project_id)

    def ensure_directories(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)
