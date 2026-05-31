"""
Broadcasts an AirPlay service via mDNS/Bonjour so iOS devices
can discover this PC in Control Center > Screen Mirroring.
"""

import socket
import hashlib
from zeroconf import Zeroconf, ServiceInfo


AIRPLAY_SERVICE_TYPE = "_airplay._tcp.local."
RAOP_SERVICE_TYPE = "_raop._tcp.local."


def _get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def _generate_device_id(name: str) -> str:
    h = hashlib.md5(name.encode()).hexdigest()[:12]
    return ":".join(h[i:i+2] for i in range(0, 12, 2))


class AirPlayMDNSService:
    """Registers AirPlay + RAOP mDNS services on the local network."""

    def __init__(self, name: str = "PC-AirPlay", port: int = 7000):
        self.name = name
        self.port = port
        self.device_id = _generate_device_id(name)
        self.zeroconf: Zeroconf | None = None
        self._airplay_info: ServiceInfo | None = None
        self._raop_info: ServiceInfo | None = None

    def start(self) -> str:
        local_ip = _get_local_ip()
        parsed_ip = socket.inet_aton(local_ip)

        airplay_props = {
            "deviceid": self.device_id,
            "features": "0x5A7FFFF7,0x1E",
            "flags": "0x44",
            "model": "AppleTV3,2",
            "pi": "2e388006-13ba-4041-9a67-25dd4a43d536",
            "pk": "b07727d6f6cd6e08b58ede525ec3cdeaa252ad9f683feb212ef8a205246554e7",
            "srcvers": "220.68",
            "vv": "2",
        }

        self._airplay_info = ServiceInfo(
            AIRPLAY_SERVICE_TYPE,
            f"{self.name}.{AIRPLAY_SERVICE_TYPE}",
            addresses=[parsed_ip],
            port=self.port,
            properties=airplay_props,
            server=f"{self.name.replace(' ', '-')}.local.",
        )

        raop_name = f"{self.device_id.replace(':', '')}@{self.name}"
        raop_props = {
            "am": "AppleTV3,2",
            "cn": "0,1,2,3",
            "da": "true",
            "et": "0,3,5",
            "ft": "0x5A7FFFF7,0x1E",
            "md": "0,1,2",
            "pw": "false",
            "sf": "0x44",
            "sr": "44100",
            "ss": "16",
            "sv": "false",
            "tp": "UDP",
            "vs": "220.68",
            "vn": "65537",
        }

        self._raop_info = ServiceInfo(
            RAOP_SERVICE_TYPE,
            f"{raop_name}.{RAOP_SERVICE_TYPE}",
            addresses=[parsed_ip],
            port=self.port,
            properties=raop_props,
            server=f"{self.name.replace(' ', '-')}.local.",
        )

        self.zeroconf = Zeroconf()
        self.zeroconf.register_service(self._airplay_info)
        self.zeroconf.register_service(self._raop_info)
        return local_ip

    def stop(self):
        if self.zeroconf:
            if self._airplay_info:
                self.zeroconf.unregister_service(self._airplay_info)
            if self._raop_info:
                self.zeroconf.unregister_service(self._raop_info)
            self.zeroconf.close()
            self.zeroconf = None


if __name__ == "__main__":
    import time

    service = AirPlayMDNSService(name="My-PC-Display")
    ip = service.start()
    print(f"AirPlay service broadcasting on {ip}:{service.port}")
    print(f"Device ID: {service.device_id}")
    print("Your iPad should now see 'My-PC-Display' in Screen Mirroring.")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
        print("\nService stopped.")
