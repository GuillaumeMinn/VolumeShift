VolumeShift
===========

Version: 0.1.0

A terminal-based per-application audio volume controller for Linux.
Control the volume of individual running applications directly from the command line,
using PulseAudio or PipeWire's pactl utility.

Requirements
------------

- Linux (any major distro)
- Python 3.6 or later
- pactl command-line utility (see Installation below)

Dependencies
------------

pactl

pactl is the only dependency. It is part of the PulseAudio utilities package
and works with both PulseAudio and PipeWire (via PipeWire's PulseAudio compatibility layer),
which is the standard audio stack on all major Linux distributions.

Arch Linux / Manjaro
--------------------

PipeWire (recommended for modern Arch installs)
sudo pacman -S pipewire pipewire-pulse

PulseAudio (alternative)
sudo pacman -S pulseaudio

Debian / Ubuntu
---------------

sudo apt update
sudo apt install pulseaudio-utils

RHEL / CentOS
-------------

sudo dnf install pulseaudio-utils

> On older RHEL/CentOS systems using yum:
> bash
> sudo yum install pulseaudio-utils
> 

SUSE / openSUSE
---------------

sudo zypper install pulseaudio-utils

Usage
-----

Open a terminal and run:

python volumemixerlinux.py

You will be presented with a list of all applications currently producing audio,
along with their volume levels. For example:

================================================================
              LINUX TERMINAL VOLUME MIXER
          (PulseAudio / PipeWire via pactl)
================================================================

  #    Application                    Volume
  ------------------------------------------------------------
  1    Spotify                          80%  [████████████████░░░░]
  2    firefox                         100%  [████████████████████]
  3    vlc                              55%  [███████████░░░░░░░░░]

  Select app number to adjust (or 'q' to quit): 1
  Current volume for Spotify: 80%
  New volume (0-100): 50
  Done! Spotify set to 50%

How it Works
------------

The program uses Python's built-in subprocess module to call pactl list sink-inputs
to enumerate all active audio sessions (called sink inputs in PulseAudio/PipeWire).
It parses the output to extract application names and volume levels, then uses
pactl set-sink-input-volume to apply any changes.

No admin privileges are required.

Notes
-----

- Only applications that are currently playing audio will appear in the list.
  If an application is silent, it will not show up.
- Volume changes take effect immediately.
- The list is populated at startup. If you open a new audio application after
  launching the mixer, restart the program to see it.

License
-------

Distributed under the GNU General Public License v3.0.
See LICENSE.txt for details.
