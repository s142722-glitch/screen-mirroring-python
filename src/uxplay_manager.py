"""
Manages the UxPlay binary process — the open-source AirPlay mirror server
that handles FairPlay handshakes, RTSP negotiation, and H.264 stream reception.

UxPlay renders video via GStreamer. This module launches it as a subprocess
and pipes its output for status monitoring.
"""

import os
import signal
import subprocess
import threading
from pathlib import Path
from typing import Callable


UXPLAY_BIN = os.environ.get(
    "UXPLAY_PATH",
    str(Path(__file__).resolve().parent.parent / "bin" / "uxplay.exe"),
)

# MSYS2 UCRT64 GStreamer path — needed so uxplay.exe can find GStreamer DLLs
MSYS2_BIN = r"C:\msys64\ucrt64\bin"
MSYS2_GST_PLUGINS = r"C:\msys64\ucrt64\lib\gstreamer-1.0"


def _build_env() -> dict[str, str]:
    """Return a modified environment with MSYS2 GStreamer on PATH."""
    env = os.environ.copy()
    path = env.get("PATH", "")
    if MSYS2_BIN.lower() not in path.lower():
        env["PATH"] = MSYS2_BIN + os.pathsep + path
    env["GST_PLUGIN_PATH"] = MSYS2_GST_PLUGINS
    return env


class UxPlayManager:
    def __init__(
        self,
        name: str = "PC-AirPlay",
        port: int = 7000,
        resolution: str = "1920x1080",
        fps: int = 30,
        on_log: Callable[[str], None] | None = None,
    ):
        self.name = name
        self.port = port
        self.resolution = resolution
        self.fps = fps
        self.on_log = on_log or (lambda _: None)
        self._proc: subprocess.Popen | None = None
        self._reader_thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def _build_command(self) -> list[str]:
        w, h = self.resolution.split("x")
        cmd = [
            UXPLAY_BIN,
            "-n", self.name,
            "-s", f"{w}x{h}",
            "-fps", str(self.fps),
            "-p",
        ]
        return cmd

    def start(self):
        if self.is_running:
            return

        if not Path(UXPLAY_BIN).exists():
            raise FileNotFoundError(
                f"UxPlay binary not found at {UXPLAY_BIN}. "
                "Set UXPLAY_PATH env var or place uxplay.exe in the bin/ folder. "
                "See SETUP.md for build instructions."
            )

        cmd = self._build_command()
        self.on_log(f"Starting: {' '.join(cmd)}")

        env = _build_env()
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
        self._reader_thread.start()

    def _read_output(self):
        assert self._proc and self._proc.stdout
        for line in self._proc.stdout:
            stripped = line.rstrip()
            if stripped:
                self.on_log(stripped)

    def stop(self):
        if not self._proc:
            return
        try:
            self._proc.terminate()
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._proc.kill()
        finally:
            self._proc = None
