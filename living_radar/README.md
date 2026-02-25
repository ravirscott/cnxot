# Living Radar (WiFi + Bluetooth)

Ye project aapke **normal laptop** par chalne ke liye banaya gaya hai:

- WiFi + Bluetooth device scan karta hai.
- RSSI se approx distance estimate karta hai.
- Browser me **god-level radar visualization** dikhata hai:
  - Tens of thousands moving dots
  - Moving entities ke red pulse rings
  - Live side panel with source/RSSI/motion

> Important: Ye **direct human body** detect nahi karta. Ye nearby active devices detect karta hai.

## Quick start

```bash
cd living_radar
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open: http://localhost:8000

## How detection works

- `scanner.py`:
  - WiFi scan: `nmcli`
  - Bluetooth scan: `bluetoothctl`
  - RSSI -> distance conversion
  - Motion score from RSSI change over time
- Agar live scan available nahi ho, app synthetic demo mode me chalti hai.

## Upgrade path (real device-free human detection)

Agar bina phone/device living being detect karna hai:

1. Raspberry Pi + CSI-supported WiFi card
2. ya PIR / mmWave sensors add karo
3. sensor fusion backend me merge karo

## Beginner roadmap

1. Is app ko run karo.
2. Radar UI samjho.
3. `scanner.py` me filters add karo (sirf mobile devices etc.).
4. CSV/DB logging add karo.
5. Later hardware sensors plugin model me add karo.
