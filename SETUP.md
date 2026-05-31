# AirPlay Receiver — Setup Guide (Windows 11)

## Architecture

```
iPad Screen Mirroring
        │
        ▼
  mDNS Discovery (zeroconf/Python)  ← makes iPad "see" the PC
        │
        ▼
  UxPlay (open-source binary)       ← handles AirPlay/FairPlay protocol
        │
        ▼
  GStreamer                          ← decodes H.264 and renders video
        │
        ▼
  PyQt6 GUI                         ← control panel / settings
```

## Step 1 — Install Apple Bonjour (mDNS)

Bonjour is required for mDNS to work on Windows.

**Option A** — Install iTunes from the Microsoft Store (includes Bonjour).

**Option B** — Install Bonjour Print Services standalone:
https://support.apple.com/kb/DL999

Verify it's running:
```powershell
Get-Service -Name "Bonjour Service"
```

## Step 2 — Install GStreamer

UxPlay uses GStreamer for video rendering. Download the **MSVC 64-bit** runtime + development installers:

1. Go to https://gstreamer.freedesktop.org/download/
2. Download both:
   - `gstreamer-1.0-msvc-x86_64-X.XX.X.msi` (runtime)
   - `gstreamer-1.0-devel-msvc-x86_64-X.XX.X.msi` (development)
3. Install both to `C:\gstreamer`
4. Add to your PATH:
```powershell
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\gstreamer\1.0\msvc_x86_64\bin", "User")
[Environment]::SetEnvironmentVariable("GST_PLUGIN_PATH", "C:\gstreamer\1.0\msvc_x86_64\lib\gstreamer-1.0", "User")
```
5. Verify:
```powershell
gst-launch-1.0 --version
```

## Step 3 — Get UxPlay

UxPlay is the open-source AirPlay mirror server that handles FairPlay DRM.

**Option A — Pre-built binary (easiest):**

Check https://github.com/FDH2/UxPlay/releases for Windows builds.
Place `uxplay.exe` in the `bin/` folder of this project.

**Option B — Build from source via MSYS2:**

```bash
# In MSYS2 UCRT64 shell:
pacman -S mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-gcc
pacman -S mingw-w64-ucrt-x86_64-openssl mingw-w64-ucrt-x86_64-libplist
pacman -S mingw-w64-ucrt-x86_64-gstreamer mingw-w64-ucrt-x86_64-gst-plugins-base
pacman -S mingw-w64-ucrt-x86_64-gst-plugins-good mingw-w64-ucrt-x86_64-gst-plugins-bad
pacman -S mingw-w64-ucrt-x86_64-gst-libav

git clone https://github.com/FDH2/UxPlay.git
cd UxPlay
mkdir build && cd build
cmake ..
cmake --build .
```

Copy the resulting `uxplay.exe` into this project's `bin/` folder.

## Step 4 — Install Python dependencies

```powershell
cd C:\Users\abdulmalik\airplay-receiver
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Step 5 — Test mDNS discovery

```powershell
python main.py --mdns --name "My-PC"
```

Then on your iPad: **Settings → Control Center → Screen Mirroring**.
You should see "My-PC" in the list. (Tapping it won't complete mirroring
until UxPlay is in place — this step just validates network discovery.)

## Step 6 — Run the full receiver

Once UxPlay is in `bin/`:

```powershell
python main.py
```

Click "Start Receiver" in the GUI. On your iPad, open Screen Mirroring
and tap your PC's name. UxPlay will open a GStreamer video window
showing your iPad's screen.

## Troubleshooting

| Problem | Fix |
|---|---|
| iPad doesn't see PC | Check Windows Firewall — allow UDP 5353 (mDNS) and TCP 7000 inbound. Ensure Bonjour service is running. |
| mDNS works but mirroring fails | UxPlay binary missing or GStreamer not installed. Check the log panel. |
| Video is choppy | Lower resolution to 1280x720 in the GUI. Ensure both devices are on the same Wi-Fi (not bridged via Ethernet). |
| "No module named zeroconf" | Activate the venv: `.venv\Scripts\Activate.ps1` |
