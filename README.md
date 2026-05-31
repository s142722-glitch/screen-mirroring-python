# Screen Mirroring - Python AirPlay Receiver

A Python-based AirPlay screen mirroring receiver that allows wireless display from iOS/macOS devices (iPad, iPhone, Mac) to a Windows PC.

## Architecture

```
iPad Screen Mirroring
        |
        v
  mDNS Discovery (zeroconf/Python)  <-- makes iPad "see" the PC
        |
        v
  UxPlay (open-source binary)       <-- handles AirPlay/FairPlay protocol
        |
        v
  GStreamer                          <-- decodes H.264 and renders video
        |
        v
  PyQt6 GUI                         <-- control panel / settings
```

## Features

- **Wireless Screen Mirroring** - Mirror your iPad/iPhone/Mac screen to Windows PC
- **PyQt6 GUI Dashboard** - Start/stop controls, status display, and log viewer
- **mDNS Discovery** - Automatic device discovery using Zeroconf
- **Configurable Settings:**
  - Custom device name
  - Resolution selection (1080p, 720p, 4K)
- **UxPlay Integration** - Handles AirPlay protocol and FairPlay DRM
- **GStreamer Video Rendering** - Hardware-accelerated H.264 decoding
- **Headless Mode** - Run mDNS broadcast only for testing (`--mdns` flag)

## Requirements

- Python 3.10+
- Windows 11
- Apple Bonjour (via iTunes or standalone)
- GStreamer (MSVC 64-bit)
- UxPlay binary

## Installation

```powershell
# Clone the repo
git clone https://github.com/s142722-glitch/screen-mirroring-python.git
cd screen-mirroring-python

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Usage

```powershell
# Launch the GUI
python main.py

# Test mDNS discovery only
python main.py --mdns --name "My-PC"
```

1. Click **Start Receiver** in the GUI
2. On your iPad/iPhone, open **Screen Mirroring**
3. Tap your PC's name to start mirroring

## Project Structure

```
airplay-receiver/
  main.py              # Entry point
  requirements.txt     # Python dependencies
  SETUP.md             # Detailed setup guide
  src/
    gui.py             # PyQt6 control panel
    mdns_service.py    # Zeroconf mDNS broadcaster
    uxplay_manager.py  # UxPlay process manager
  bin/
    uxplay.exe         # AirPlay server binary
```

## Tech Stack

- **Python** - Core application
- **PyQt6** - GUI framework
- **Zeroconf** - mDNS/DNS-SD service discovery
- **UxPlay** - Open-source AirPlay mirror server
- **GStreamer** - Multimedia framework for video rendering

## Troubleshooting

| Problem | Fix |
|---------|-----|
| iPad doesn't see PC | Check Windows Firewall - allow UDP 5353 (mDNS) and TCP 7000 inbound |
| mDNS works but mirroring fails | UxPlay binary missing or GStreamer not installed |
| Video is choppy | Lower resolution to 720p. Ensure both devices on same Wi-Fi |
