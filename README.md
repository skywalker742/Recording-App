# Class Notes Recorder

A desktop app that records your class, turns the audio into a transcript on your
own computer, and writes organized notes (key concepts, definitions, assignments,
exam info). Only the transcript text is sent to the Claude API to write the notes.
Audio never leaves your computer.

> **Before you record:** make sure your instructors, your school, and local law
> allow you to record class.

## Build status

| Phase | What | Status |
|---|---|---|
| 1. Setup | Project, settings, `class-notes status` | Done |
| 2. Recorder | Microphone, chunked recording, stop | Not started |
| 3. Session log | SQLite history, `class-notes list` | Not started |
| 4. Transcriber | Local speech-to-text | Not started |
| 5. Note generator | Claude API notes | Not started |
| 6. Full pipeline | One stop command makes every file | Not started |
| 7. Tray app | System tray controls and notifications | Not started |
| 8. Reliability | Crash recovery, retries, disk checks, auto-delete | Not started |
| 9. Daily use | Run at login, setup help | Not started |

## Setup on Windows (first time only)

These steps use **PowerShell**, a window where you type commands. To open it,
press the Windows key, type `PowerShell`, and press Enter.

### 1. Install Python 3.13

Python is the programming language the app is written in.

1. Go to <https://www.python.org/downloads/windows/> and download the latest
   **Python 3.13** "Windows installer (64-bit)".
2. Run the installer. On the first screen, **tick "Add python.exe to PATH"**,
   then click **Install Now**.
3. Close PowerShell and open a new one. Then check that it worked:

   ```powershell
   py -3.13 --version
   ```

   You should see something like `Python 3.13.x`.

Why 3.13 and not 3.11: the speech-to-text library added in Phase 4 needs Python
3.12 or newer on Windows.

### 2. Install Git and download the project

Git is the tool that downloads (clones) the project and tracks changes to it.

1. Install Git from <https://git-scm.com/download/win> (the default options are fine).
2. In a new PowerShell window, run these two commands. The first downloads the
   project into a folder called `Recording-App`; the second moves into that folder.

   ```powershell
   git clone https://github.com/skywalker742/Recording-App.git
   ```

   ```powershell
   cd Recording-App
   ```

### 3. Create a virtual environment

A virtual environment is a private box for this project's libraries, so they
don't mix with anything else on your computer.

```powershell
py -3.13 -m venv .venv
```

Then switch it on:

```powershell
.venv\Scripts\Activate.ps1
```

Your prompt now starts with `(.venv)`. You need to run that second line again
every time you open a new PowerShell window to work on the app.

> If you see "running scripts is disabled on this system", run this once, answer
> `Y`, and then try again:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### 4. Install the app

This installs the app and the testing tool into the virtual environment. The `-e`
means changes to the code take effect without reinstalling.

```powershell
python -m pip install --upgrade pip
```

```powershell
pip install -e ".[dev]"
```

### 5. Check it works

```powershell
class-notes status
```

The first time you run it, the app creates your settings file, `config.toml`, in
the project folder and prints your settings.

## Settings

Open `config.toml` in Notepad to change your settings:

```powershell
notepad config.toml
```

Replace `"Class 1", "Class 2"` with your real classes, for example
`classes = ["Biology 101", "History 210"]`. Every setting is explained in
`config.example.toml`. `config.toml` is personal and is never uploaded to Git.

Your recordings, transcripts, and notes go in `Documents\Class Notes`. If your
Documents folder is synced to OneDrive, set `data_folder` to the full path you
want, for example `data_folder = "C:/Users/you/Class Notes"`. Use forward slashes `/`
in the path.

## Commands

| Command | What it does | Available |
|---|---|---|
| `class-notes status` | Shows settings and whether a recording is running | Now |
| `class-notes start --class "Biology 101"` | Starts recording | Phase 2 |
| `class-notes stop` | Stops recording | Phase 2 |
| `class-notes list` | Lists past sessions | Phase 3 |
| `class-notes retry <session-id>` | Retries a failed transcript or notes step | Phase 4 |
| `class-notes tray` | Runs the system tray app | Phase 7 |

## Running the tests

Automated tests check that the code behaves correctly. With the virtual
environment switched on:

```powershell
pytest
```

All tests should show as passed.
