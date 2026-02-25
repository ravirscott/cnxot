from __future__ import annotations

import math
import random
import subprocess
import time
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class DevicePing:
    source: str
    name: str
    address: str
    rssi: int
    distance_m: float
    x: float
    y: float
    movement: float
    seen_at: float


def _run_command(cmd: list[str], timeout: int = 4) -> str:
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode != 0:
            return ""
        return proc.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _distance_from_rssi(rssi: int, tx_power: int = -55, path_loss: float = 2.2) -> float:
    exponent = (tx_power - rssi) / (10 * path_loss)
    return round(max(0.5, min(30.0, 10**exponent)), 2)


def _position_from_signal(rssi: int, name: str) -> tuple[float, float]:
    seed = abs(hash(name)) % 10000
    random.seed(seed + int(time.time() // 3))
    angle = random.uniform(0, math.tau)
    radius = min(95, max(8, 105 + rssi))
    x = 50 + radius * math.cos(angle)
    y = 50 + radius * math.sin(angle)
    return round(x, 2), round(y, 2)


def _movement_score(rssi: int, prev_rssi: int | None) -> float:
    if prev_rssi is None:
        return 0.1
    return round(min(1.0, abs(rssi - prev_rssi) / 10.0), 2)


def scan_wifi(prev: dict[str, int]) -> list[DevicePing]:
    output = _run_command(["nmcli", "-t", "-f", "SSID,SIGNAL,BSSID", "dev", "wifi", "list", "--rescan", "yes"])
    if not output:
        return []

    pings: list[DevicePing] = []
    for line in output.splitlines()[:25]:
        parts = line.split(":")
        if len(parts) < 3:
            continue
        ssid, signal, bssid = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if not signal.isdigit():
            continue
        signal_pct = int(signal)
        rssi = int(-95 + (signal_pct / 100) * 55)
        x, y = _position_from_signal(rssi, ssid or bssid)
        pings.append(
            DevicePing(
                source="wifi",
                name=ssid or "Hidden WiFi",
                address=bssid,
                rssi=rssi,
                distance_m=_distance_from_rssi(rssi),
                x=x,
                y=y,
                movement=_movement_score(rssi, prev.get(bssid)),
                seen_at=time.time(),
            )
        )
    return pings


def scan_bluetooth(prev: dict[str, int]) -> list[DevicePing]:
    device_lines = _run_command(["bluetoothctl", "devices"])
    if not device_lines:
        return []

    pings: list[DevicePing] = []
    for line in device_lines.splitlines()[:20]:
        parts = line.split(maxsplit=2)
        if len(parts) < 3:
            continue
        address = parts[1]
        name = parts[2]
        info = _run_command(["bluetoothctl", "info", address], timeout=3)
        rssi = None
        for info_line in info.splitlines():
            if "RSSI:" in info_line:
                try:
                    rssi = int(info_line.split("RSSI:")[1].strip())
                except ValueError:
                    rssi = None
        if rssi is None:
            rssi = random.randint(-85, -45)
        x, y = _position_from_signal(rssi, name)
        pings.append(
            DevicePing(
                source="bluetooth",
                name=name,
                address=address,
                rssi=rssi,
                distance_m=_distance_from_rssi(rssi, tx_power=-59, path_loss=2.0),
                x=x,
                y=y,
                movement=_movement_score(rssi, prev.get(address)),
                seen_at=time.time(),
            )
        )
    return pings


def synthetic_pings() -> list[DevicePing]:
    demo_names = ["Phone-A", "Watch-1", "Laptop-Guest", "Earbuds-Pro"]
    pings: list[DevicePing] = []
    now = time.time()
    for i, name in enumerate(demo_names):
        wobble = math.sin(now * (0.7 + i * 0.15))
        rssi = int(-60 - i * 6 + wobble * 5)
        x = 20 + i * 18 + wobble * 3
        y = 35 + (i % 2) * 25 + math.cos(now * 0.8 + i) * 4
        pings.append(
            DevicePing(
                source="synthetic",
                name=name,
                address=f"DE:MO:{i:02d}:AA:BB:CC",
                rssi=rssi,
                distance_m=_distance_from_rssi(rssi),
                x=round(x, 2),
                y=round(y, 2),
                movement=round(min(1.0, abs(wobble)), 2),
                seen_at=now,
            )
        )
    return pings


def collect_snapshot(prev_rssi: dict[str, int]) -> dict[str, Any]:
    wifi = scan_wifi(prev_rssi)
    bluetooth = scan_bluetooth(prev_rssi)
    devices = wifi + bluetooth

    if not devices:
        devices = synthetic_pings()
        mode = "synthetic"
    else:
        mode = "live"

    for dev in devices:
        prev_rssi[dev.address] = dev.rssi

    moving = [d for d in devices if d.movement > 0.3]
    motion_level = round(sum(d.movement for d in devices) / max(1, len(devices)), 2)

    return {
        "mode": mode,
        "timestamp": time.time(),
        "device_count": len(devices),
        "moving_count": len(moving),
        "motion_level": motion_level,
        "entities": [asdict(d) for d in devices],
    }
