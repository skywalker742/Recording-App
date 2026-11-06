"""Loads and checks the settings in config.toml."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# The project folder (the one holding pyproject.toml), when running from source.
PROJECT_DIR = Path(__file__).resolve().parents[2]
EXAMPLE_FILE = PROJECT_DIR / "config.example.toml"

DEFAULTS: dict = {
    "classes": ["Class 1", "Class 2"],
    "data_folder": "~/Documents/Class Notes",
    "microphone": "default",
    "chunk_minutes": 5,
    "max_recording_hours": 4,
    "whisper_model": "base.en",
    "claude_model": "claude-sonnet-5-5",
    "auto_transcribe": True,
    "auto_notes": True,
    "delete_audio_after_days": 30,
}


class ConfigError(Exception):
    """Raised when config.toml can't be read or has a bad value."""


@dataclass
class Config:
    path: Path
    classes: list[str]
    data_folder: Path
    microphone: str
    chunk_minutes: float
    max_recording_hours: float
    whisper_model: str
    claude_model: str
    auto_transcribe: bool
    auto_notes: bool
    delete_audio_after_days: int
    warnings: list[str] = field(default_factory=list)


def default_config_path() -> Path:
    """Where config.toml lives.

    1. The CLASS_NOTES_CONFIG environment variable, if set.
    2. The project folder, when running from the source code (the normal case).
    3. Otherwise, the user's settings folder (%APPDATA% on Windows).
    """
    env = os.environ.get("CLASS_NOTES_CONFIG")
    if env:
        return Path(env).expanduser()
    if (PROJECT_DIR / "pyproject.toml").exists():
        return PROJECT_DIR / "config.toml"
    base = os.environ.get("APPDATA") or Path.home() / ".config"
    return Path(base) / "Class Notes Recorder" / "config.toml"


def _default_text() -> str:
    if EXAMPLE_FILE.exists():
        return EXAMPLE_FILE.read_text(encoding="utf-8")
    lines = []
    for key, value in DEFAULTS.items():
        if isinstance(value, bool):
            lines.append(f"{key} = {'true' if value else 'false'}")
        elif isinstance(value, str):
            lines.append(f'{key} = "{value}"')
        elif isinstance(value, list):
            lines.append(f"{key} = [" + ", ".join(f'"{v}"' for v in value) + "]")
        else:
            lines.append(f"{key} = {value}")
    return "\n".join(lines) + "\n"


def ensure_config_file(path: Path) -> bool:
    """Create config.toml with default settings if it doesn't exist.

    Returns True if a new file was created.
    """
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_default_text(), encoding="utf-8")
    return True


def _check_number(raw: dict, key: str, *, integer: bool = False, minimum: float = 0) -> None:
    value = raw[key]
    ok_types = (int,) if integer else (int, float)
    if isinstance(value, bool) or not isinstance(value, ok_types):
        kind = "a whole number" if integer else "a number"
        raise ConfigError(f"'{key}' must be {kind}, but it is {value!r}.")
    if value <= minimum:
        raise ConfigError(f"'{key}' must be more than {minimum}, but it is {value}.")


def load_config(path: Path | None = None) -> Config:
    """Read config.toml, filling in defaults for missing settings."""
    path = path or default_config_path()
    ensure_config_file(path)

    try:
        with path.open("rb") as f:
            user = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path} has a formatting mistake: {e}") from e

    warnings = [f"Unknown setting '{k}' in config.toml (ignored)." for k in user if k not in DEFAULTS]
    raw = {**DEFAULTS, **{k: v for k, v in user.items() if k in DEFAULTS}}

    classes = raw["classes"]
    if not isinstance(classes, list) or not classes or not all(
        isinstance(c, str) and c.strip() for c in classes
    ):
        raise ConfigError("'classes' must be a list of class names, like [\"Biology 101\"].")
    if len(set(classes)) != len(classes):
        raise ConfigError("'classes' has the same class name more than once.")

    for key in ("data_folder", "microphone", "whisper_model", "claude_model"):
        if not isinstance(raw[key], str) or not raw[key].strip():
            raise ConfigError(f"'{key}' must be text in quotes, like \"{DEFAULTS[key]}\".")
    for key in ("auto_transcribe", "auto_notes"):
        if not isinstance(raw[key], bool):
            raise ConfigError(f"'{key}' must be true or false.")
    _check_number(raw, "chunk_minutes")
    _check_number(raw, "max_recording_hours")
    _check_number(raw, "delete_audio_after_days", integer=True)

    return Config(
        path=path,
        classes=[c.strip() for c in classes],
        data_folder=Path(os.path.expandvars(raw["data_folder"])).expanduser(),
        microphone=raw["microphone"],
        chunk_minutes=raw["chunk_minutes"],
        max_recording_hours=raw["max_recording_hours"],
        whisper_model=raw["whisper_model"],
        claude_model=raw["claude_model"],
        auto_transcribe=raw["auto_transcribe"],
        auto_notes=raw["auto_notes"],
        delete_audio_after_days=raw["delete_audio_after_days"],
        warnings=warnings,
    )
