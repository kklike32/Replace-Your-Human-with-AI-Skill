from __future__ import annotations

import json
import sys
from collections.abc import Callable
from datetime import date, datetime
from typing import Any


def _default(value: Any) -> Any:
    if isinstance(value, datetime | date):
        return value.isoformat()
    return str(value)


def build_jsonl_sink() -> Callable[[dict[str, Any]], None]:
    def emit(event: dict[str, Any]) -> None:
        sys.stdout.write(json.dumps(event, default=_default) + "\n")
        sys.stdout.flush()

    return emit
