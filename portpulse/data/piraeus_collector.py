"""
PortPulse AIS Collector — Piraeus
Connects to aisstream.io WebSocket and saves vessel positions to CSV.
Run this for several hours or days to build a real dataset.

Usage:
    export AISSTREAM_API_KEY="your_key_here"
    python piraeus_collector.py
"""

import asyncio
import websockets
import json
import csv
import os
from datetime import datetime

API_KEY = os.environ.get("AISSTREAM_API_KEY", "YOUR_KEY_HERE")
OUTPUT_FILE = "piraeus_ais_live.csv"

# Piraeus + Saronic Gulf approach area
# SW corner: 37.70N, 23.40E  |  NE corner: 37.97N, 23.72E
PIRAEUS_BBOX = [[[37.70, 23.40], [37.97, 23.72]]]

# AIS ship type code to readable name
SHIP_TYPE_MAP = {
    30: "Fishing",
    60: "Passenger", 61: "Passenger", 62: "Passenger", 69: "Passenger",
    70: "Cargo", 71: "Cargo", 72: "Cargo", 73: "Cargo", 74: "Cargo", 79: "Cargo",
    80: "Tanker", 81: "Tanker", 82: "Tanker", 83: "Tanker", 84: "Tanker", 89: "Tanker",
    90: "Other", 91: "Other",
}

# MID (first 3 digits of MMSI) to flag ISO
MID_TO_FLAG = {
    "237": "GRC", "239": "GRC", "240": "GRC", "241": "GRC",
    "247": "ITA", "248": "MLT", "249": "MLT",
    "209": "CYP", "210": "CYP", "212": "CYP",
    "224": "ESP", "225": "ESP",
    "226": "FRA", "227": "FRA",
    "271": "TUR", "351": "PAN", "352": "PAN", "353": "PAN",
    "636": "LBR", "637": "LBR",
    "538": "MHL",
    "477": "HKG",
    "412": "CHN", "413": "CHN", "414": "CHN",
    "563": "SGP",
    "273": "RUS",
    "422": "IRN",
}


def mmsi_to_flag(mmsi_str):
    """Derive flag state from MMSI Maritime Identification Digits."""
    if len(mmsi_str) >= 3:
        return MID_TO_FLAG.get(mmsi_str[:3], "UNK")
    return "UNK"


def init_csv(filepath):
    """Create CSV with headers if it doesn't exist."""
    if not os.path.exists(filepath):
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "mmsi", "vessel_name", "flag",
                "vessel_type", "ship_type_code",
                "lat", "lon", "speed_knots", "course", "heading",
                "nav_status", "destination"
            ])


async def collect():
    """Main collection loop with automatic reconnection."""
    init_csv(OUTPUT_FILE)
    positions_saved = 0

    while True:
        try:
            async with websockets.connect(
                "wss://stream.aisstream.io/v0/stream",
                ping_interval=20,
                ping_timeout=20,
            ) as ws:
                # Subscribe to Piraeus area
                subscribe = {
                    "APIKey": API_KEY,
                    "BoundingBoxes": PIRAEUS_BBOX,
                    "FilterMessageTypes": ["PositionReport", "ShipStaticData"],
                }
                await ws.send(json.dumps(subscribe))
                print(f"[{datetime.utcnow().isoformat()}] Connected — listening for Piraeus vessels...")

                async for raw_msg in ws:
                    try:
                        data = json.loads(raw_msg)
                        msg_type = data.get("MessageType", "")
                        meta = data.get("MetaData", {})
                        mmsi = str(meta.get("MMSI", ""))

                        if msg_type == "PositionReport":
                            pos = data.get("Message", {}).get("PositionReport", {})
                            if not pos:
                                continue

                            row = [
                                datetime.utcnow().isoformat(),
                                mmsi,
                                meta.get("ShipName", "").strip(),
                                mmsi_to_flag(mmsi),
                                SHIP_TYPE_MAP.get(meta.get("ShipType", 0), "Unknown"),
                                meta.get("ShipType", 0),
                                round(meta.get("latitude", 0), 6),
                                round(meta.get("longitude", 0), 6),
                                round(pos.get("Sog", 0) / 10, 1),  # SOG is in 1/10 knot
                                round(pos.get("Cog", 0) / 10, 1),  # COG is in 1/10 degree
                                pos.get("TrueHeading", 511),
                                pos.get("NavigationalStatus", 15),
                                meta.get("Destination", "").strip(),
                            ]

                            with open(OUTPUT_FILE, "a", newline="") as f:
                                csv.writer(f).writerow(row)

                            positions_saved += 1
                            if positions_saved % 100 == 0:
                                print(f"[{datetime.utcnow().isoformat()}] {positions_saved} positions saved | Latest: {meta.get('ShipName', mmsi)}")

                    except (json.JSONDecodeError, KeyError) as e:
                        continue

        except (websockets.ConnectionClosed, ConnectionError, OSError) as e:
            print(f"[{datetime.utcnow().isoformat()}] Connection lost: {e}. Reconnecting in 10s...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"[{datetime.utcnow().isoformat()}] Unexpected error: {e}. Reconnecting in 30s...")
            await asyncio.sleep(30)


if __name__ == "__main__":
    print("=" * 60)
    print("PortPulse AIS Collector — Piraeus")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Bounding box: {PIRAEUS_BBOX}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    asyncio.run(collect())
