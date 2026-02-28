import sys
import subprocess
import re

if sys.platform != "linux":
    print("This program only runs on Linux.")
    sys.exit(1)

def check_pactl():
    try:
        subprocess.run(["pactl", "--version"],
                       capture_output=True, check=True)
        return True
    except FileNotFoundError:
        print("Error: 'pactl' not found. Install it with:")
        print("  Arch Linux:      sudo pacman -S pipewire pipewire-pulse")
        print("  Debian/Ubuntu:   sudo apt install pulseaudio-utils")
        print("  RHEL/Fedora:     sudo dnf install pulseaudio-utils")
        print("  openSUSE:        sudo zypper install pulseaudio-utils")
        return False
    except subprocess.CalledProcessError:
        return False

def run_pactl(*args):
    result = subprocess.run(
        ["pactl"] + list(args),
        capture_output=True, text=True
    )
    return result.stdout

def parse_sink_inputs(raw):
    sessions = []
    current = {}

    for line in raw.splitlines():
        m = re.match(r"^Sink Input #(\d+)", line)
        if m:
            if current:
                sessions.append(current)
            current = {"index": m.group(1), "name": None, "volume": 1.0}
            continue

        m = re.search(r'application\.name\s*=\s*"(.+?)"', line)
        if m and current and not current["name"]:
            current["name"] = m.group(1)
            continue

        m = re.search(r'media\.name\s*=\s*"(.+?)"', line)
        if m and current and not current["name"]:
            current["name"] = m.group(1)
            continue

        m = re.search(r'application\.process\.binary\s*=\s*"(.+?)"', line)
        if m and current and not current["name"]:
            current["name"] = m.group(1)
            continue

        if "Volume:" in line:
            m = re.search(r"(\d+)%", line)
            if m and current:
                current["volume"] = int(m.group(1)) / 100.0
            continue

    if current:
        sessions.append(current)

    result = []
    for s in sessions:
        if s.get("index") is not None:
            if not s["name"]:
                s["name"] = f"Sink Input #{s['index']}"
            result.append(s)

    return result

def collect_sessions():
    raw = run_pactl("list", "sink-inputs")
    return parse_sink_inputs(raw)

def set_volume(index, percent):
    run_pactl("set-sink-input-volume", str(index), f"{percent}%")

def vol_bar(fraction, width=20):
    fraction = max(0.0, min(1.0, fraction))
    filled = round(fraction * width)
    return "[" + "█" * filled + "░" * (width - filled) + "]"

def print_sessions(sessions):
    print()
    print(f"  {'#':<4} {'Application':<30} {'Volume':>7}  ")
    print("  " + "-" * 60)
    for i, s in enumerate(sessions, 1):
        pct = round(s["volume"] * 100)
        bar = vol_bar(s["volume"])
        print(f"  {i:<4} {s['name'][:29]:<30} {pct:>5}%  {bar}")
    print()

def prompt_change(sessions):
    raw = input("  Select app number to adjust (or 'q' to quit): ").strip()
    if raw.lower() == "q":
        return False

    if not raw.isdigit() or not (1 <= int(raw) <= len(sessions)):
        print("  Invalid selection.\n")
        return True

    idx = int(raw) - 1
    s   = sessions[idx]
    print(f"  Current volume for {s['name']}: {round(s['volume'] * 100)}%")
    new_raw = input("  New volume (0-100): ").strip()

    if not new_raw.isdigit() or not (0 <= int(new_raw) <= 100):
        print("  Invalid value - enter a number between 0 and 100.\n")
        return True

    set_volume(s["index"], int(new_raw))
    s["volume"] = int(new_raw) / 100.0
    print(f"  Done! {s['name']} set to {new_raw}%\n")
    return True

def main():
    print("=" * 64)
    print("              LINUX TERMINAL VOLUME MIXER")
    print("          (PulseAudio / PipeWire via pactl)")
    print("=" * 64)

    if not check_pactl():
        sys.exit(1)

    sessions = collect_sessions()

    if not sessions:
        print("\n  No active audio sessions found.")
        print("  Play some audio in an application and run again.\n")
        return

    while True:
        print_sessions(sessions)
        if not prompt_change(sessions):
            break

    print("\n  Bye!\n")

if __name__ == "__main__":
    main()
