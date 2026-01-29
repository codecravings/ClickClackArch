#!/usr/bin/env python3
"""
Mechanical Keyboard Sound Simulator - Wayland Compatible
Uses evdev for direct keyboard input capture.
"""

import os
import sys
import wave
import random
import subprocess
import tempfile
import numpy as np
from evdev import InputDevice, categorize, ecodes, list_devices

SOUND_DIR = tempfile.mkdtemp(prefix="mechkeys_")

def generate_click(filename, variation=0, volume=0.7):
    """Generate realistic Cherry MX Blue style click with bottom-out thock."""
    sr = 44100
    duration = 0.08
    n = int(sr * duration)
    t = np.linspace(0, duration, n)
    sound = np.zeros(n)

    # Variation parameters
    pitch_var = 1.0 + (variation * 0.08)
    timing_var = int(abs(variation) * 10)

    # 1. SWITCH CLICK - the sharp metallic click from the mechanism (Cherry MX Blue style)
    click_start = max(0, 5 + timing_var)
    click_dur = 0.003
    click_len = int(sr * click_dur)
    click_end = min(click_start + click_len, n)
    actual_click_len = click_end - click_start
    if actual_click_len > 0:
        click_t = np.linspace(0, click_dur, actual_click_len)
        click_freq = 4500 * pitch_var
        click = (
            0.6 * np.sin(2 * np.pi * click_freq * click_t) +
            0.3 * np.sin(2 * np.pi * click_freq * 1.5 * click_t) +
            0.1 * np.sin(2 * np.pi * click_freq * 2.2 * click_t)
        )
        click_env = np.exp(-click_t * 1500)
        sound[click_start:click_end] += click * click_env * 0.5

    # 2. BOTTOM-OUT THOCK - when key hits the plate
    thock_start = max(0, int(sr * 0.008) + timing_var)
    thock_dur = 0.045
    thock_len = int(sr * thock_dur)
    thock_end = min(thock_start + thock_len, n)
    actual_thock_len = thock_end - thock_start
    if actual_thock_len > 0:
        thock_t = np.linspace(0, thock_dur, actual_thock_len)
        base_freq = (280 + variation * 20) * pitch_var
        thock = (
            0.5 * np.sin(2 * np.pi * base_freq * thock_t) +
            0.25 * np.sin(2 * np.pi * base_freq * 1.8 * thock_t) +
            0.15 * np.sin(2 * np.pi * base_freq * 3.2 * thock_t) +
            0.1 * np.random.uniform(-1, 1, actual_thock_len)
        )
        thock_env = np.exp(-thock_t * 80) * (1 - np.exp(-thock_t * 800))
        sound[thock_start:thock_end] += thock * thock_env * 0.7

    # 3. CASE RESONANCE - the hollow sound from the keyboard body
    res_len = min(int(sr * 0.05), n)
    res_t = np.linspace(0, 0.05, res_len)
    res_freq = (180 + variation * 10) * pitch_var
    resonance = (
        0.4 * np.sin(2 * np.pi * res_freq * res_t) +
        0.3 * np.sin(2 * np.pi * res_freq * 1.5 * res_t)
    )
    res_env = np.exp(-res_t * 60)
    sound[:res_len] += resonance * res_env * 0.25

    # 4. Initial transient pop
    pop_len = min(int(sr * 0.001), n)
    pop = np.random.uniform(-1, 1, pop_len) * np.exp(-np.linspace(0, 8, pop_len))
    sound[:pop_len] += pop * 0.4

    # Normalize and apply volume
    sound = sound / (np.max(np.abs(sound)) + 0.001) * volume
    audio = (np.clip(sound, -1, 1) * 32767).astype(np.int16)

    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(audio.tobytes())

def generate_release(filename, variation=0, volume=0.45):
    """Generate realistic key release - spring return + reset click."""
    sr = 44100
    duration = 0.05
    n = int(sr * duration)
    t = np.linspace(0, duration, n)
    sound = np.zeros(n)

    pitch_var = 1.0 + (variation * 0.06)

    # 1. SPRING RETURN - higher pitched than press
    spring_len = int(sr * 0.015)
    spring_t = np.linspace(0, 0.015, spring_len)
    spring_freq = 3200 * pitch_var
    spring = (
        0.4 * np.sin(2 * np.pi * spring_freq * spring_t) +
        0.3 * np.sin(2 * np.pi * spring_freq * 0.7 * spring_t)
    )
    spring_env = np.exp(-spring_t * 400)
    sound[:spring_len] += spring * spring_env * 0.3

    # 2. RESET CLICK - softer than the press click
    click_start = int(sr * 0.003)
    click_len = int(sr * 0.008)
    if click_start + click_len < n:
        click_t = np.linspace(0, 0.008, click_len)
        click_freq = 2800 * pitch_var
        click = (
            0.5 * np.sin(2 * np.pi * click_freq * click_t) +
            0.3 * np.sin(2 * np.pi * click_freq * 1.3 * click_t) +
            0.2 * np.random.uniform(-1, 1, click_len)
        )
        click_env = np.exp(-click_t * 300)
        sound[click_start:click_start + click_len] += click * click_env * 0.4

    # 3. Soft thump from key returning
    thump_len = int(sr * 0.02)
    thump_t = np.linspace(0, 0.02, thump_len)
    thump = np.sin(2 * np.pi * 200 * pitch_var * thump_t) * np.exp(-thump_t * 150)
    sound[:thump_len] += thump * 0.2

    sound = sound / (np.max(np.abs(sound)) + 0.001) * volume
    audio = (np.clip(sound, -1, 1) * 32767).astype(np.int16)

    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(audio.tobytes())

def generate_space(filename, volume=0.75):
    """Deep spacebar thock with stabilizer rattle."""
    sr = 44100
    duration = 0.12
    n = int(sr * duration)
    t = np.linspace(0, duration, n)
    sound = np.zeros(n)

    # 1. MAIN THOCK - deeper than regular keys
    thock_len = int(sr * 0.07)
    thock_t = np.linspace(0, 0.07, thock_len)
    thock = (
        0.5 * np.sin(2 * np.pi * 150 * thock_t) +
        0.3 * np.sin(2 * np.pi * 220 * thock_t) +
        0.15 * np.sin(2 * np.pi * 380 * thock_t) +
        0.05 * np.random.uniform(-1, 1, thock_len)
    )
    thock_env = np.exp(-thock_t * 45) * (1 - np.exp(-thock_t * 600))
    sound[:thock_len] += thock * thock_env * 0.8

    # 2. STABILIZER CLICK - the wire stabilizers make a distinct sound
    stab_start = int(sr * 0.002)
    stab_len = int(sr * 0.012)
    if stab_start + stab_len < n:
        stab_t = np.linspace(0, 0.012, stab_len)
        stab = (
            0.4 * np.sin(2 * np.pi * 2200 * stab_t) +
            0.3 * np.sin(2 * np.pi * 3100 * stab_t) +
            0.3 * np.random.uniform(-1, 1, stab_len)
        )
        stab_env = np.exp(-stab_t * 250)
        sound[stab_start:stab_start + stab_len] += stab * stab_env * 0.35

    # 3. CASE BOOM - larger key = more case resonance
    boom_len = int(sr * 0.08)
    boom_t = np.linspace(0, 0.08, boom_len)
    boom = (
        0.6 * np.sin(2 * np.pi * 100 * boom_t) +
        0.4 * np.sin(2 * np.pi * 160 * boom_t)
    )
    boom_env = np.exp(-boom_t * 40)
    sound[:boom_len] += boom * boom_env * 0.3

    # 4. Initial impact
    pop_len = int(sr * 0.002)
    pop = np.random.uniform(-1, 1, pop_len) * np.exp(-np.linspace(0, 6, pop_len))
    sound[:pop_len] += pop * 0.5

    sound = sound / (np.max(np.abs(sound)) + 0.001) * volume
    audio = (np.clip(sound, -1, 1) * 32767).astype(np.int16)

    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(audio.tobytes())

def find_keyboard():
    """Find keyboard device - prefer real keyboard over mouse keyboards."""
    devices = [InputDevice(path) for path in list_devices()]
    keyboards = []
    for dev in devices:
        caps = dev.capabilities()
        if ecodes.EV_KEY in caps:
            keys = caps[ecodes.EV_KEY]
            if ecodes.KEY_A in keys and ecodes.KEY_Z in keys:
                keyboards.append(dev)

    # Prefer "AT Translated" or keyboards without "mouse" in name
    for kbd in keyboards:
        name_lower = kbd.name.lower()
        if "at translated" in name_lower or ("keyboard" in name_lower and "mouse" not in name_lower):
            return kbd

    return keyboards[0] if keyboards else None

def play(filepath):
    """Play sound via paplay."""
    env = os.environ.copy()
    env["PULSE_SERVER"] = f"unix:/run/user/1000/pulse/native"
    subprocess.Popen(["paplay", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)

def main():
    print("Generating sounds...")

    # Generate variations for natural sound
    clicks = []
    for i in range(8):
        f = os.path.join(SOUND_DIR, f"click{i}.wav")
        generate_click(f, variation=random.uniform(-1, 1))
        clicks.append(f)

    releases = []
    for i in range(5):
        f = os.path.join(SOUND_DIR, f"rel{i}.wav")
        generate_release(f, variation=random.uniform(-1, 1))
        releases.append(f)

    space_f = os.path.join(SOUND_DIR, "space.wav")
    generate_space(space_f)

    print("Finding keyboard...")
    kbd = find_keyboard()

    if not kbd:
        print("ERROR: No keyboard found. Make sure you have permission to read /dev/input/")
        print("Try: sudo usermod -aG input $USER  (then log out and back in)")
        print("Or run this script with sudo")
        sys.exit(1)

    print(f"Using: {kbd.name}")
    print("""
╔════════════════════════════════════════════╗
║   MECHANICAL KEYBOARD - WAYLAND EDITION    ║
╠════════════════════════════════════════════╣
║   Type anywhere - sounds will play!        ║
║   Press Ctrl+C here to stop                ║
╚════════════════════════════════════════════╝
""")

    try:
        for event in kbd.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)

                if key_event.keystate == 1:  # Key down
                    if key_event.scancode == ecodes.KEY_SPACE:
                        play(space_f)
                    else:
                        play(random.choice(clicks))

                elif key_event.keystate == 0:  # Key up
                    play(random.choice(releases))

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        import shutil
        shutil.rmtree(SOUND_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()
