# Project Notes for Agents

## Overview
- This is a Windows desktop Python utility for instant translation to Turkish.
- Main entry point: `translator_app.py`.
- The app uses a global hotkey (`ctrl+alt+t`), clipboard access, mouse selection detection, a CustomTkinter popup, and a system tray icon.

## Run
- Install dependencies with: `python -m pip install -r requirements.txt`
- Start the app with: `python translator_app.py`
- In this Codex workspace, the bundled Python may be available at:
  `C:\Users\sxkare\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

## Notes
- The app needs a desktop session because it creates GUI windows and listens for global keyboard/mouse events.
- Translation uses `deep-translator` / Google Translator, so internet access is required at runtime.
- Some existing Markdown files appear to contain mojibake text; avoid rewriting them unless explicitly asked.
