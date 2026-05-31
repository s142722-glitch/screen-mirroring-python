"""
Entry point for the AirPlay Receiver application.

Usage:
    python main.py          — launch the GUI
    python main.py --mdns   — broadcast mDNS only (no GUI, for testing discovery)
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="AirPlay Receiver for Windows")
    parser.add_argument("--mdns", action="store_true", help="Run mDNS broadcast only (headless test mode)")
    parser.add_argument("--name", default="PC-AirPlay", help="Device name shown on iPad")
    args = parser.parse_args()

    if args.mdns:
        import time
        from src.mdns_service import AirPlayMDNSService

        svc = AirPlayMDNSService(name=args.name)
        ip = svc.start()
        print(f"Broadcasting '{args.name}' on {ip}:7000")
        print(f"Device ID: {svc.device_id}")
        print("Check your iPad's Screen Mirroring list. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            svc.stop()
            print("\nStopped.")
    else:
        from src.gui import run_gui
        run_gui()


if __name__ == "__main__":
    main()
