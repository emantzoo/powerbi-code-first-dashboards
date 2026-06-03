"""
Epikast Engagement Dashboard — deterministic sample data generator.

Produces a star-schema dataset for a technology-enabled biopharma services
company (HCP engagement, MSL/inside-sales activity, patient support &
adherence, quality/compliance, per-client campaign health).

Run:  python generate_epikast_data.py
Writes 6 CSVs next to this script. Uses only the Python stdlib.
"""

import csv
import os
import random
from datetime import date, timedelta

random.seed(42)
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

START = date(2024, 1, 1)
END = date(2025, 6, 30)
SPAN_DAYS = (END - START).days


def rand_date(start=START, end=END):
    return start + timedelta(days=random.randint(0, (end - start).days))


def write_csv(name, header, rows):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")


# ── DimClient — biopharma clients Epikast delivers services for ─────────────
CLIENTS = [
    ("CL01", "Helix Therapeutics",  "Oncology",     "Oncoxar",   "Hybrid Field + Inside"),
    ("CL02", "Aurora BioPharma",    "Immunology",   "Immunova",  "Inside Sales"),
    ("CL03", "Meridian Oncology",   "Oncology",     "Kytruva",   "MSL Medical Affairs"),
    ("CL04", "Caduceus Pharma",     "Cardiology",   "Cardvex",   "Omnichannel"),
    ("CL05", "Vantage Biologics",   "Rare Disease", "Raravia",   "Patient Support"),
    ("CL06", "NordStar Sciences",   "Neurology",    "Neurolin",  "Hybrid Field + Inside"),
    ("CL07", "Cardinal Immuno",     "Immunology",   "Cimzera",   "Omnichannel"),
    ("CL08", "Lumen Rare Disease",  "Rare Disease", "Lumvera",   "Patient Support"),
]
TA_BY_CLIENT = {c[0]: c[3] for c in CLIENTS}
write_csv(
    "DimClient.csv",
    ["client_id", "client_name", "therapeutic_area", "brand", "engagement_model", "contract_start"],
    [[c[0], c[1], c[2], c[3], c[4], rand_date(date(2023, 1, 1), date(2024, 6, 1)).isoformat()] for c in CLIENTS],
)

# ── DimAgent — Epikast delivery talent (reps, MSLs, navigators) ─────────────
ROLES = ["Inside Sales Rep", "MSL", "Patient Navigator", "Medical Information Specialist"]
ROLE_WEIGHTS = [0.40, 0.25, 0.25, 0.10]
CRED_BY_ROLE = {
    "Inside Sales Rep": ["BSc", "BSc", "PharmD", "MSc"],
    "MSL": ["PhD", "PharmD", "MD", "PhD"],
    "Patient Navigator": ["RN", "RN", "BSc", "MSW"],
    "Medical Information Specialist": ["PharmD", "PharmD", "MSc", "RN"],
}
HUBS = ["Athens", "Athens", "Thessaloniki", "Remote-EU", "Remote-US"]
TEAMS = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]
FIRST = ["Maria", "Nikos", "Elena", "Yannis", "Sofia", "Dimitris", "Katerina", "Andreas",
         "Christina", "Petros", "Anna", "Giorgos", "Eleni", "Kostas", "Despina", "Vasilis",
         "Ioanna", "Stelios", "Marina", "Thanasis", "Olga", "Michalis", "Foteini", "Alexis"]
LAST = ["Papadopoulos", "Georgiou", "Nikolaou", "Vlachos", "Antoniou", "Makris", "Pappas",
        "Dimitriou", "Konstantinou", "Ioannou", "Petrou", "Christou", "Stavrou", "Lambrou"]

agents = []
for i in range(1, 61):
    role = random.choices(ROLES, ROLE_WEIGHTS)[0]
    name = f"{random.choice(FIRST)} {random.choice(LAST)}"
    cred = random.choice(CRED_BY_ROLE[role])
    agents.append([
        f"AG{i:03d}", name, role, cred,
        random.choice(TEAMS), random.choice(HUBS), random.randint(3, 84),
    ])
write_csv("DimAgent.csv",
          ["agent_id", "agent_name", "role", "credential", "team", "hub_location", "tenure_months"],
          agents)
AGENTS_BY_ROLE = {}
for a in agents:
    AGENTS_BY_ROLE.setdefault(a[2], []).append(a[0])

# ── DimHCP — physicians targeted across client brands ───────────────────────
SPECIALTIES = ["Oncology", "Cardiology", "Immunology", "Neurology", "Endocrinology", "Rheumatology"]
SEGMENTS = ["KOL", "High Value", "Mid Value", "Emerging"]
SEG_WEIGHTS = [0.10, 0.25, 0.40, 0.25]
# (region, city, lat, lng)
GEO = [
    ("Northeast", "New York", 40.7128, -74.0060), ("Northeast", "Boston", 42.3601, -71.0589),
    ("Northeast", "Philadelphia", 39.9526, -75.1652), ("Southeast", "Atlanta", 33.7490, -84.3880),
    ("Southeast", "Miami", 25.7617, -80.1918), ("Southeast", "Charlotte", 35.2271, -80.8431),
    ("Midwest", "Chicago", 41.8781, -87.6298), ("Midwest", "Minneapolis", 44.9778, -93.2650),
    ("Midwest", "Columbus", 39.9612, -82.9988), ("West", "Los Angeles", 34.0522, -118.2437),
    ("West", "San Francisco", 37.7749, -122.4194), ("West", "Seattle", 47.6062, -122.3321),
    ("Southwest", "Houston", 29.7604, -95.3698), ("Southwest", "Phoenix", 33.4484, -112.0740),
    ("Southwest", "Dallas", 32.7767, -96.7970),
]
DOC_FIRST = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
             "David", "Barbara", "William", "Susan", "Richard", "Karen", "Joseph", "Lisa",
             "Raj", "Priya", "Wei", "Mei", "Carlos", "Sofia", "Ahmed", "Fatima"]
DOC_LAST = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Patel", "Nguyen", "Kim", "Chen",
            "Cohen", "Murphy", "Wright", "Adams"]

hcps = []
for i in range(1, 301):
    region, city, lat, lng = random.choice(GEO)
    seg = random.choices(SEGMENTS, SEG_WEIGHTS)[0]
    decile = {"KOL": random.randint(9, 10), "High Value": random.randint(7, 9),
              "Mid Value": random.randint(4, 6), "Emerging": random.randint(1, 3)}[seg]
    hcps.append([
        f"HCP{i:04d}", f"Dr. {random.choice(DOC_FIRST)} {random.choice(DOC_LAST)}",
        random.choice(SPECIALTIES), seg, decile, region,
        f"{region[:2].upper()}-{random.randint(1, 9):02d}",
        round(lat + random.uniform(-0.4, 0.4), 4), round(lng + random.uniform(-0.4, 0.4), 4),
    ])
write_csv("DimHCP.csv",
          ["hcp_id", "hcp_name", "specialty", "segment", "decile", "region", "territory", "latitude", "longitude"],
          hcps)
HCP_IDS = [h[0] for h in hcps]

# ── DimPatient — patients enrolled in support programs ──────────────────────
AGE_GROUPS = ["18-34", "35-49", "50-64", "65-74", "75+"]
GENDERS = ["Female", "Male"]
INSURANCE = ["Commercial", "Medicare", "Medicaid", "Uninsured"]
INS_WEIGHTS = [0.45, 0.30, 0.18, 0.07]
patients = []
for i in range(1, 1501):
    region = random.choice(GEO)[0]
    patients.append([
        f"PT{i:05d}", random.choice(AGE_GROUPS), random.choice(GENDERS),
        region, random.choices(INSURANCE, INS_WEIGHTS)[0],
    ])
write_csv("DimPatient.csv",
          ["patient_id", "age_group", "gender", "region", "insurance_type"],
          patients)
PATIENT_IDS = [p[0] for p in patients]

# ── FactInteractions — HCP engagement events (calls/emails/video/portal) ────
CHANNELS = ["Phone", "Email", "Video", "Portal"]
CHANNEL_WEIGHTS = [0.42, 0.30, 0.16, 0.12]
ITYPES = ["Scientific Exchange", "Promotional", "Follow-up", "Onboarding"]
ITYPE_WEIGHTS = [0.30, 0.34, 0.26, 0.10]
NBA = ["Schedule Follow-up", "Send Clinical Data", "Sample Drop", "No Action",
       "Escalate to MSL", "Invite to Webinar"]
OUTCOMES = ["Connected", "No Answer", "Declined", "Voicemail"]

interactions = []
for i in range(1, 12001):
    agent = random.choice(agents)
    agent_id, role = agent[0], agent[2]
    hcp_id = random.choice(HCP_IDS)
    client_id = random.choice(CLIENTS)[0]
    channel = random.choices(CHANNELS, CHANNEL_WEIGHTS)[0]
    # MSLs lean scientific; reps lean promotional
    if role == "MSL":
        itype = random.choices(ITYPES, [0.55, 0.05, 0.30, 0.10])[0]
    elif role == "Inside Sales Rep":
        itype = random.choices(ITYPES, [0.12, 0.50, 0.28, 0.10])[0]
    else:
        itype = random.choices(ITYPES, ITYPE_WEIGHTS)[0]
    # connection depends on channel (email/portal usually "delivered" = connected)
    if channel in ("Email", "Portal"):
        connected = "Yes" if random.random() < 0.92 else "No"
    else:
        connected = "Yes" if random.random() < 0.58 else "No"
    if connected == "Yes":
        outcome = "Connected"
        duration = max(2, int(random.gauss(14, 7))) if channel in ("Phone", "Video") else random.randint(1, 4)
        sentiment = round(min(1.0, max(0.0, random.gauss(0.64, 0.18))), 2)
        adherence = round(min(1.0, max(0.55, random.gauss(0.91, 0.07))), 2)
    else:
        outcome = random.choice(["No Answer", "Declined", "Voicemail"])
        duration = 0
        sentiment = round(min(1.0, max(0.0, random.gauss(0.45, 0.15))), 2)
        adherence = round(min(1.0, max(0.55, random.gauss(0.88, 0.08))), 2)
    compliance = "Pass" if adherence >= 0.75 and random.random() < 0.985 else "Review"
    adverse = "Yes" if random.random() < 0.018 else "No"
    interactions.append([
        f"INT{i:06d}", rand_date().isoformat(), agent_id, hcp_id, client_id,
        channel, itype, duration, connected, outcome,
        random.choice(NBA), sentiment, adherence, compliance, adverse,
    ])
write_csv("FactInteractions.csv",
          ["interaction_id", "interaction_date", "agent_id", "hcp_id", "client_id",
           "channel", "interaction_type", "duration_minutes", "connected", "outcome",
           "next_best_action", "sentiment_score", "script_adherence_pct", "compliance_status",
           "adverse_event_flagged"],
          interactions)

# ── FactPatientSupport — patient adherence / navigation records ─────────────
STATUS = ["Enrolled", "Active", "On Therapy", "Discontinued"]
STATUS_WEIGHTS = [0.12, 0.30, 0.40, 0.18]
BARRIERS = ["Cost / Access", "Prior Authorization", "Side Effects", "Logistics", "None"]
BARRIER_WEIGHTS = [0.22, 0.24, 0.16, 0.10, 0.28]
PAYER = ["Approved", "Pending", "Denied", "Appeal Won"]
PAYER_WEIGHTS = [0.62, 0.16, 0.12, 0.10]
nav_agents = AGENTS_BY_ROLE.get("Patient Navigator", [a[0] for a in agents])
support = []
used_patients = random.sample(PATIENT_IDS, 1400)
for i, pid in enumerate(used_patients, start=1):
    client_id = random.choices([c[0] for c in CLIENTS], [0.10, 0.08, 0.10, 0.10, 0.24, 0.10, 0.08, 0.20])[0]
    status = random.choices(STATUS, STATUS_WEIGHTS)[0]
    enroll = rand_date(START, date(2025, 4, 30))
    ttt = max(1, int(random.gauss(18, 9)))               # time to therapy (days)
    if status == "Discontinued":
        adherence = round(min(1.0, max(0.20, random.gauss(0.58, 0.16))), 2)
        persistence = random.randint(20, 160)
    elif status == "Enrolled":
        adherence = round(min(1.0, max(0.40, random.gauss(0.72, 0.12))), 2)
        persistence = random.randint(5, 60)
    else:
        adherence = round(min(1.0, max(0.50, random.gauss(0.86, 0.10))), 2)
        persistence = random.randint(60, 480)
    barrier = random.choices(BARRIERS, BARRIER_WEIGHTS)[0]
    barrier_resolved = "N/A" if barrier == "None" else ("Yes" if random.random() < 0.78 else "No")
    payer = random.choices(PAYER, PAYER_WEIGHTS)[0]
    nps = random.choices(range(0, 11),
                         [1, 1, 1, 2, 2, 4, 6, 9, 16, 22, 35])[0]  # skew positive
    support.append([
        f"PS{i:05d}", pid, random.choice(nav_agents), client_id,
        enroll.isoformat(), status, ttt, adherence, persistence,
        barrier, barrier_resolved, payer, nps,
    ])
write_csv("FactPatientSupport.csv",
          ["support_id", "patient_id", "agent_id", "client_id", "enrollment_date",
           "status", "time_to_therapy_days", "adherence_pct", "persistence_days",
           "barrier_type", "barrier_resolved", "payer_status", "nps_score"],
          support)

print("Done!")
