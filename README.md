# ClickClackArch ⌨️💥

Turn your mushy membrane keyboard into a thunderous mechanical beast. 🦁

## What is this? 🤔

A Python script that plays Cherry MX Blue-style sounds when you type. Because your coworkers weren't annoyed enough already. 😈

## Requirements 📋

- 🐧 **Linux only** (uses evdev - sorry Windows/Mac folks, skill issue)
- 🔊 PulseAudio (for the clicky sounds)
- 🐍 Python 3 with numpy and evdev
- 👥 Your user in the `input` group (or just yolo it with sudo)

## Installation 🛠️

```bash
# Arch btw 🎩
sudo pacman -S python-numpy python-evdev

# Or use a venv like a civilized person 🧐
python -m venv .venv
.venv/bin/pip install numpy evdev
```

## Usage 🚀

```bash
python mechanical_typer.py
# or with venv
.venv/bin/python mechanical_typer.py
```

Then type anywhere. Annoy everyone. You're welcome. 😎

## Permissions 🔐

If it yells about not finding a keyboard:
```bash
sudo usermod -aG input $USER
# Then log out and back in (yes, actually log out) 🚪
```

Or just run with `sudo` if you like living dangerously. 🎰

## Features ✨

- 🔵 Cherry MX Blue click sounds (the superior switch, fight me)
- 💪 Bottom-out thock
- 🏠 Case resonance
- 👾 Spacebar has extra THONK
- 🖥️ Wayland compatible (because it's not 2015 anymore)

## License 📜

Do whatever you want with it. It's a keyboard sound script, not a nuclear reactor. ☢️
