"""
Generate synthetic AIS data for Piraeus port — ~5,000 rows, 31 vessels, 3 days.
Output: piraeus_ais.csv + piraeus_zones.csv

Run once:  python data/generate_piraeus_data.py
"""

import csv
import random
import datetime
import os

random.seed(42)

# ── Vessel definitions ─────────────────────────────────────────────────────
VESSELS = [
    # (mmsi, vessel_name, vessel_type, flag)
    ("241001001", "AEGEAN STAR", "Container", "Greece"),
    ("241001002", "PIRAEUS EXPRESS", "Container", "Greece"),
    ("241001003", "OLYMPIC CARRIER", "Container", "Greece"),
    ("356001001", "PANAMA TRADER", "Container", "Panama"),
    ("356001002", "CANAL BRIDGE", "Bulk Carrier", "Panama"),
    ("477001001", "HONG KONG SPIRIT", "Container", "Hong Kong"),
    ("477001002", "ORIENT WAVE", "Tanker", "Hong Kong"),
    ("636001001", "LIBERIA FORTUNE", "Tanker", "Liberia"),
    ("636001002", "MONROVIA STAR", "Bulk Carrier", "Liberia"),
    ("538001001", "MARSHALL DAWN", "Tanker", "Marshall Islands"),
    ("538001002", "PACIFIC MARSHAL", "Bulk Carrier", "Marshall Islands"),
    ("256001001", "MALTA BREEZE", "Container", "Malta"),
    ("256001002", "VALLETTA SUN", "Ro-Ro", "Malta"),
    ("209001001", "CYPRUS WAVE", "Passenger", "Cyprus"),
    ("209001002", "LIMASSOL FERRY", "Passenger", "Cyprus"),
    ("241002001", "ATHENA GLORY", "Tanker", "Greece"),
    ("241002002", "POSEIDON BULK", "Bulk Carrier", "Greece"),
    ("241002003", "CRETE RUNNER", "Ro-Ro", "Greece"),
    ("241002004", "MYKONOS JET", "Passenger", "Greece"),
    ("241002005", "RHODES CARRIER", "Container", "Greece"),
    ("356002001", "BALBOA QUEEN", "Tanker", "Panama"),
    ("356002002", "GATUN BULK", "Bulk Carrier", "Panama"),
    ("636002001", "LIBERIA COAST", "Ro-Ro", "Liberia"),
    ("538002001", "MAJURO TIDE", "Container", "Marshall Islands"),
    ("256002001", "GOZO SPIRIT", "Bulk Carrier", "Malta"),
    ("371001001", "ISTANBUL BRIDGE", "Container", "Turkey"),
    ("371001002", "BOSPHORUS WIND", "Tanker", "Turkey"),
    ("247001001", "GENOVA EXPRESS", "Ro-Ro", "Italy"),
    ("247001002", "NAPOLI STAR", "Passenger", "Italy"),
    ("215001001", "RABAT CARGO", "Bulk Carrier", "Morocco"),
    ("622001001", "ALEXANDRIA SUN", "Container", "Egypt"),
]

# ── Geographic zones ───────────────────────────────────────────────────────
# Port berths (lat 37.935–37.960, lon 23.595–23.650)
BERTH_LAT = (37.935, 37.955)
BERTH_LON = (23.600, 23.648)

# Anchorage — Saronic Gulf south of port entrance (open water)
ANCH_LAT = (37.880, 37.930)
ANCH_LON = (23.580, 23.640)

# Approach / transit — further south in the Saronic Gulf
APPR_LAT = (37.830, 37.880)
APPR_LON = (23.570, 23.630)


def rand_in(low, high):
    return round(random.uniform(low, high), 6)


def generate_vessel_track(mmsi, name, vtype, flag, start_time, behaviour):
    """Generate a sequence of AIS positions for one vessel over ~3 days."""
    rows = []
    t = start_time + datetime.timedelta(minutes=random.randint(0, 120))

    if behaviour == "berthed":
        # Vessel sits at berth for most of the period
        lat = rand_in(*BERTH_LAT)
        lon = rand_in(*BERTH_LON)
        n_positions = random.randint(140, 200)
        for _ in range(n_positions):
            speed = round(random.uniform(0.0, 0.4), 1)
            rows.append((mmsi, t, lat + rand_in(-0.001, 0.001), lon + rand_in(-0.001, 0.001), speed, vtype, name, flag))
            t += datetime.timedelta(minutes=random.randint(15, 25))

    elif behaviour == "waiting":
        # Vessel waits at anchorage, then moves to berth
        lat = rand_in(*ANCH_LAT)
        lon = rand_in(*ANCH_LON)
        wait_positions = random.randint(80, 160)
        for _ in range(wait_positions):
            speed = round(random.uniform(0.0, 0.8), 1)
            rows.append((mmsi, t, lat + rand_in(-0.002, 0.002), lon + rand_in(-0.002, 0.002), speed, vtype, name, flag))
            t += datetime.timedelta(minutes=random.randint(15, 25))
        # Then move to berth
        berth_lat = rand_in(*BERTH_LAT)
        berth_lon = rand_in(*BERTH_LON)
        for i in range(10):
            frac = i / 10
            cur_lat = lat + (berth_lat - lat) * frac
            cur_lon = lon + (berth_lon - lon) * frac
            speed = round(random.uniform(2.0, 6.0), 1)
            rows.append((mmsi, t, cur_lat, cur_lon, speed, vtype, name, flag))
            t += datetime.timedelta(minutes=random.randint(5, 10))
        # Berthed
        for _ in range(random.randint(20, 40)):
            speed = round(random.uniform(0.0, 0.3), 1)
            rows.append((mmsi, t, berth_lat + rand_in(-0.001, 0.001), berth_lon + rand_in(-0.001, 0.001), speed, vtype, name, flag))
            t += datetime.timedelta(minutes=random.randint(15, 25))

    elif behaviour == "transit":
        # Vessel approaches, passes through, leaves
        lat = rand_in(*APPR_LAT)
        lon = rand_in(*APPR_LON)
        target_lat = rand_in(*BERTH_LAT)
        target_lon = rand_in(*BERTH_LON)
        n_positions = random.randint(30, 60)
        for i in range(n_positions):
            frac = i / n_positions
            cur_lat = lat + (target_lat - lat) * frac
            cur_lon = lon + (target_lon - lon) * frac
            speed = round(random.uniform(5.0, 14.0), 1)
            rows.append((mmsi, t, cur_lat, cur_lon, speed, vtype, name, flag))
            t += datetime.timedelta(minutes=random.randint(5, 15))

    elif behaviour == "mixed":
        # Some waiting, some maneuvering, some transit
        # Start approaching
        lat = rand_in(*APPR_LAT)
        lon = rand_in(*APPR_LON)
        for _ in range(random.randint(15, 25)):
            speed = round(random.uniform(3.0, 8.0), 1)
            lat += rand_in(0.001, 0.003)
            lon += rand_in(0.001, 0.003)
            rows.append((mmsi, t, lat, lon, speed, vtype, name, flag))
            t += datetime.timedelta(minutes=random.randint(10, 20))
        # Wait at anchorage
        anch_lat = rand_in(*ANCH_LAT)
        anch_lon = rand_in(*ANCH_LON)
        for _ in range(random.randint(40, 80)):
            speed = round(random.uniform(0.0, 0.9), 1)
            rows.append((mmsi, t, anch_lat + rand_in(-0.002, 0.002), anch_lon + rand_in(-0.002, 0.002), speed, vtype, name, flag))
            t += datetime.timedelta(minutes=random.randint(15, 25))
        # Maneuver to berth
        berth_lat = rand_in(*BERTH_LAT)
        berth_lon = rand_in(*BERTH_LON)
        for _ in range(random.randint(15, 25)):
            speed = round(random.uniform(1.0, 4.0), 1)
            anch_lat += (berth_lat - anch_lat) * 0.1
            anch_lon += (berth_lon - anch_lon) * 0.1
            rows.append((mmsi, t, anch_lat, anch_lon, speed, vtype, name, flag))
            t += datetime.timedelta(minutes=random.randint(5, 15))

    return rows


def main():
    start_time = datetime.datetime(2026, 3, 30, 0, 0, 0)

    # Assign behaviours to vessels
    behaviours = (
        ["berthed"] * 8 +
        ["waiting"] * 10 +
        ["transit"] * 6 +
        ["mixed"] * 7
    )
    random.shuffle(behaviours)

    all_rows = []
    for i, (mmsi, name, vtype, flag) in enumerate(VESSELS):
        behaviour = behaviours[i]
        track = generate_vessel_track(mmsi, name, vtype, flag, start_time, behaviour)
        all_rows.extend(track)

    # Sort by timestamp
    all_rows.sort(key=lambda r: r[1])

    # Write piraeus_ais.csv
    out_dir = os.path.dirname(os.path.abspath(__file__))
    ais_path = os.path.join(out_dir, "piraeus_ais.csv")

    with open(ais_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["mmsi", "timestamp", "lat", "lon", "speed_knots",
                     "vessel_type", "vessel_name", "flag", "hour", "day_of_week", "date"])
        for mmsi, ts, lat, lon, speed, vtype, name, flag in all_rows:
            w.writerow([
                mmsi,
                ts.strftime("%Y-%m-%d %H:%M:%S"),
                round(lat, 6),
                round(lon, 6),
                speed,
                vtype,
                name,
                flag,
                ts.hour,
                ts.strftime("%A"),
                ts.strftime("%Y-%m-%d"),
            ])

    # Write piraeus_zones.csv
    zones_path = os.path.join(out_dir, "piraeus_zones.csv")
    with open(zones_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["zone", "lat", "lon", "type"])
        w.writerow(["Container Terminal (PCT)", 37.940, 23.610, "berth"])
        w.writerow(["Passenger Terminal", 37.948, 23.638, "berth"])
        w.writerow(["Car Terminal (Drapetsona)", 37.950, 23.620, "berth"])
        w.writerow(["Anchorage South", 37.890, 23.600, "anchorage"])
        w.writerow(["Anchorage Central", 37.910, 23.615, "anchorage"])

    print(f"Generated {len(all_rows)} AIS positions for {len(VESSELS)} vessels")
    print(f"  {ais_path}")
    print(f"  {zones_path}")


if __name__ == "__main__":
    main()
