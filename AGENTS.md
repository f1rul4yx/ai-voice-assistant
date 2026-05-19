# AGENTS.md

## Project

Nova — voice-activated AI assistant for Linux (Arch/Manjaro). Runs as a systemd user service, activated by Ctrl+Alt+Space hotkey. Pipeline: hotkey → record → STT → LLM → TTS → floating UI.

## Architecture

All Python modules are flat (no packages). Each file is one component:

- `main.py` — Entry point. `Assistant` (pipeline orchestrator), `HotkeyListener`, Qt event loop
- `config.py` — All configuration. Change settings here, not scattered in other files
- `audio.py` — `AudioRecorder` using sounddevice. Auto-detects default mic, resamples to 16kHz
- `stt.py` — `STT` using faster-whisper. Lazy-loads model on first call
- `llm.py` — `LLM` calls `opencode run` CLI with `--format json --dangerously-skip-permissions`. System prompt is injected as message prefix
- `tts.py` — `TTS` uses edge-tts to generate MP3, then ffplay to play. No fallback players
- `ui.py` — `Window` PyQt6 frameless floating widget. Catppuccin-themed. Auto-hides 3s after idle

## Key conventions

- UI strings, system prompt, and all tunables are in `config.py` — never hardcode elsewhere
- `config.HOTKEY` is a `set` of key names (pynput naming: `"ctrl"`, `"alt"`, `"space"`)
- `WHISPER_LANGUAGE = None` means auto-detect (bilingual es/en)
- opencode CLI is expected at `~/.opencode/bin/opencode`
- The app runs as a daemon with no initial window — window appears only on hotkey press
- All signal-slot connections use `QueuedConnection` for thread safety

## Running

```bash
# Install (Arch/Manjaro only)
./install.sh

# Service management
systemctl --user start nova
systemctl --user stop nova
systemctl --user restart nova
journalctl --user -u nova -f

# Manual run (for debugging)
.venv/bin/python main.py
```

## System dependencies

`install.sh` installs: python, python-pip, portaudio, ffmpeg, pipewire-pulse

`alsa-utils` was removed — not needed since we use PipeWire directly via sounddevice.

## Gotchas

- `pipewire-pulse` replaces `pulseaudio-utils` on Arch — do not add pulseaudio-utils to install.sh
- `pulsectl` was removed from requirements.txt — mic detection now uses sounddevice defaults
- TTS audio playback requires `ffmpeg` (ffplay) — no alternative players are tried
- opencode is called with `--dangerously-skip-permissions` — the system prompt restricts behavior instead
- The systemd service uses `DISPLAY=:0` and `XDG_RUNTIME_DIR` — required for PyQt6 and hotkey listener