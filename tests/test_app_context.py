from tracker.app_context import _normalize_text, _pygetwindow_fallback
from tracker.privacy import is_sensitive_window_title


class _CallableTitleWindow:
    def title(self) -> str:
        return "1Password Vault"


class _PyGetWindowModule:
    @staticmethod
    def getActiveWindow():
        return _CallableTitleWindow()


def test_normalize_text_calls_zero_arg_callables() -> None:
    assert _normalize_text(lambda: "Safari") == "Safari"


def test_pygetwindow_fallback_handles_callable_title(monkeypatch) -> None:
    monkeypatch.setitem(__import__("sys").modules, "pygetwindow", _PyGetWindowModule())

    app_name, window_title = _pygetwindow_fallback()

    assert app_name is None
    assert window_title == "1Password Vault"
    assert is_sensitive_window_title(window_title) is True


def test_sensitive_window_title_accepts_non_string_values() -> None:
    assert is_sensitive_window_title(str.upper) is False
