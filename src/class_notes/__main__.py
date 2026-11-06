"""Command-line entry point: `class-notes <command>`."""

from __future__ import annotations

import argparse
import platform
import shutil
import sys
from pathlib import Path

from . import __version__
from .config import ConfigError, ensure_config_file, default_config_path, load_config

# Commands from the spec that later phases will fill in.
NOT_BUILT_YET = {
    "start": 2,
    "stop": 2,
    "list": 3,
    "retry": 4,
    "tray": 7,
}


def _free_space_gb(folder: Path) -> float:
    """Free disk space for the drive holding `folder` (or its nearest existing parent)."""
    probe = folder
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    return shutil.disk_usage(probe).free / 1024**3


def cmd_status(_args: argparse.Namespace) -> int:
    path = default_config_path()
    created = ensure_config_file(path)
    try:
        cfg = load_config(path)
    except ConfigError as e:
        print(f"Problem with your settings: {e}")
        print(f"Settings file: {path}")
        return 1

    print(f"Class Notes Recorder {__version__}")
    print(f"Python {platform.python_version()} on {platform.system()} {platform.release()}")
    print()
    if created:
        print("Created a new settings file with default values.")
    folder_note = "" if cfg.data_folder.exists() else "  (created on first recording)"
    rows = [
        ("Settings file", str(cfg.path)),
        ("Data folder", f"{cfg.data_folder}{folder_note}"),
        ("Free space", f"{_free_space_gb(cfg.data_folder):.1f} GB"),
        ("Classes", ", ".join(cfg.classes)),
        ("Microphone", cfg.microphone),
        ("Chunk length", f"{cfg.chunk_minutes} minutes"),
        ("Max recording", f"{cfg.max_recording_hours} hours"),
        ("Whisper model", cfg.whisper_model),
        ("Claude model", cfg.claude_model),
        ("Auto transcribe", "on" if cfg.auto_transcribe else "off"),
        ("Auto notes", "on" if cfg.auto_notes else "off"),
        ("Delete audio", f"after {cfg.delete_audio_after_days} days"),
        ("", ""),
        ("Recording", "not recording"),
    ]
    for label, value in rows:
        print(f"{label + ':':<17} {value}" if label else "")
    for w in cfg.warnings:
        print(f"Warning: {w}")
    return 0


def cmd_not_built(args: argparse.Namespace) -> int:
    phase = NOT_BUILT_YET[args.command]
    print(f"'class-notes {args.command}' isn't built yet. It arrives in Phase {phase}.")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="class-notes",
        description="Record a class, transcribe it, and turn it into notes.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    p = sub.add_parser("start", help="Start recording a class")
    p.add_argument("--class", dest="class_name", required=True, help='Class name, e.g. "Biology 101"')
    p.set_defaults(func=cmd_not_built)

    sub.add_parser("stop", help="Stop the current recording").set_defaults(func=cmd_not_built)
    sub.add_parser("status", help="Show settings and recording status").set_defaults(func=cmd_status)
    sub.add_parser("list", help="List past sessions").set_defaults(func=cmd_not_built)

    p = sub.add_parser("retry", help="Retry the transcript or notes step for a session")
    p.add_argument("session_id")
    p.set_defaults(func=cmd_not_built)

    sub.add_parser("tray", help="Run the system tray app").set_defaults(func=cmd_not_built)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
