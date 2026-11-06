import tomllib
from pathlib import Path

import pytest

from class_notes.__main__ import main
from class_notes.config import DEFAULTS, EXAMPLE_FILE, ConfigError, load_config


def test_example_file_matches_defaults():
    with EXAMPLE_FILE.open("rb") as f:
        assert tomllib.load(f) == DEFAULTS


def test_missing_config_is_created_with_defaults(tmp_path):
    path = tmp_path / "config.toml"
    cfg = load_config(path)
    assert path.exists()
    assert cfg.classes == ["Class 1", "Class 2"]
    assert cfg.chunk_minutes == 5
    assert cfg.whisper_model == "base.en"
    assert cfg.claude_model == "claude-sonnet-5-5"
    assert cfg.data_folder == Path.home() / "Documents" / "Class Notes"


def test_user_settings_override_defaults(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('classes = ["Biology 101"]\nchunk_minutes = 2\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.classes == ["Biology 101"]
    assert cfg.chunk_minutes == 2
    assert cfg.max_recording_hours == 4  # default kept


def test_unknown_setting_gives_warning(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("colour = 'blue'\n", encoding="utf-8")
    assert "colour" in load_config(path).warnings[0]


@pytest.mark.parametrize(
    "text",
    [
        "classes = []",
        'classes = ["A", "A"]',
        'chunk_minutes = "five"',
        "chunk_minutes = 0",
        "delete_audio_after_days = 1.5",
        'auto_notes = "yes"',
        "classes = [",  # broken TOML
    ],
)
def test_bad_values_are_rejected(tmp_path, text):
    path = tmp_path / "config.toml"
    path.write_text(text + "\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)


def test_status_command_prints_settings(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLASS_NOTES_CONFIG", str(tmp_path / "config.toml"))
    assert main(["status"]) == 0
    out = capsys.readouterr().out
    assert "Class Notes Recorder" in out
    assert "Class 1, Class 2" in out
    assert "not recording" in out
