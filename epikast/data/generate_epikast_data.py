"""
Generate synthetic Epikast-style pharma operations data.
Star schema: 5 fact tables + 5 dimension tables + 1 calendar + 1 experiment dim.
Covers HCP engagement, patient support, rep performance, MSL Partner usage,
A/B experiment tracking, and program financials.

Adapted for the powerbi-code-first-dashboards repo:
  - OUT writes into this script's own data/ folder (portable, no hard-coded path)
  - Connection / meaningful outcomes are now driven by AIFollowed, Script, rep
    tenure and channel, so the AI Impact, A/B Test and Workforce dashboards show
    real, visible lift instead of statistical noise. All emitted columns are
    unchanged. Search "REALISM FIX" for the edited blocks.
"""

import csv
import random
import os
from datetime import datetime, timedelta

random.seed(42)
OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

# ─── HELPERS ──────────────────────────────────────────────────
def write_csv(filename, rows, headers):
    with open(os.path.join(OUT, filename), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
    print(f"  {filename}: {len(rows)} rows")

def rand_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def rand_time_evening():
    """Athens evening = US business hours: 16:00-00:00 Athens"""
    h = random.randint(16, 23)
    m = random.randint(0, 59)
    return f"{h:02d}:{m:02d}"

# ─── PARAMETERS ───────────────────────────────────────────────
START = datetime(2025, 7, 1)
END = datetime(2026, 4, 30)
N_REPS = 25
N_HCPS = 500
N_PATIENTS = 2000
N_CALLS = 15000
N_PATIENT_CASES = 3000
THERAPY_AREAS = ["Oncology", "Cardiology", "Neurology", "Immunology", "Rare Disease"]
SPECIALTIES = ["Oncologist", "Cardiologist", "Neurologist", "Immunologist", "General Practitioner", "Internist", "Pulmonologist"]
US_STATES = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI",
             "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI"]
US_REGIONS = {"CA": "West", "TX": "South", "NY": "Northeast", "FL": "South",
              "IL": "Midwest", "PA": "Northeast", "OH": "Midwest", "GA": "South",
              "NC": "South", "MI": "Midwest", "NJ": "Northeast", "VA": "South",
              "WA": "West", "AZ": "West", "MA": "Northeast", "TN": "South",
              "IN": "Midwest", "MO": "Midwest", "MD": "Northeast", "WI": "Midwest"}
INSURANCE_TYPES = ["Commercial", "Medicare", "Medicaid", "VA", "Self-Pay"]
CALL_OUTCOMES = ["Connected", "Voicemail", "No Answer", "Gatekeeper Block", "Wrong Number"]
INTERACTION_TYPES = ["Scientific Discussion", "Product Info", "Clinical Data Review",
                     "Patient Case Discussion", "Follow-up Scheduling", "Brief Check-in"]
SCRIPTS = ["Script A - Empathetic", "Script B - Direct"]
PA_STATUSES = ["Approved", "Denied", "Pending", "Appeal"]
CASE_STATUSES = ["Open", "In Progress", "Resolved", "Abandoned"]
ABANDONMENT_REASONS = ["Insurance Delay", "Patient Lost Contact", "Cost Concerns",
                       "Side Effect Concerns", "Switched Therapy", "Patient Deceased", "Unknown"]
DRUGS = ["DrugAlpha-100mg", "DrugBeta-50mg", "DrugGamma-200mg", "NeuroX-75mg", "CardioPlus-25mg"]

print("Generating Epikast synthetic data...")

# ─── DIM: CALENDAR ────────────────────────────────────────────
print("\n[DimCalendar]")
cal_rows = []
d = START
while d <= END:
    cal_rows.append({
        "Date": d.strftime("%Y-%m-%d"),
        "Year": d.year,
        "Quarter": f"Q{(d.month - 1) // 3 + 1}",
        "Month": d.strftime("%B"),
        "MonthNum": d.month,
        "YearMonth": d.strftime("%Y-%m"),
        "WeekNum": d.isocalendar()[1],
        "DayOfWeek": d.strftime("%A"),
        "DayOfWeekNum": d.isoweekday(),
        "IsWeekend": 1 if d.isoweekday() >= 6 else 0
    })
    d += timedelta(days=1)
write_csv("DimCalendar.csv", cal_rows, list(cal_rows[0].keys()))

# ─── DIM: REPS ────────────────────────────────────────────────
print("\n[DimRep]")
first_names = ["Maria", "Eleni", "Katerina", "Nikos", "Giorgos", "Anna", "Dimitris",
               "Sofia", "Panagiotis", "Christina", "Alexandros", "Ioanna", "Vasilis",
               "Eirini", "Kostas", "Despoina", "Thanasis", "Antigoni", "Stavros",
               "Foteini", "Michalis", "Chrysa", "Yannis", "Panagiota", "Andreas"]
last_names = ["Papadopoulos", "Nikolaou", "Georgiou", "Dimitriou", "Konstantinou",
              "Ioannou", "Vasileiou", "Alexiou", "Christodoulou", "Athanasiadis",
              "Karagiannis", "Makris", "Papageorgiou", "Theodorou", "Stavridis",
              "Economou", "Angelopoulos", "Fotiadis", "Kalogeropoulos", "Tsakiris",
              "Panagiotidis", "Giannopoulos", "Liakopoulos", "Deligiannis", "Manolopoulos"]
rep_roles = ["MSL", "Patient Support Specialist", "HCP Engagement Rep"]

reps = []
for i in range(N_REPS):
    # hire window runs close to END so some reps are genuinely new (<6mo tenure)
    # — needed for the workforce ramp-up / deviation-by-tenure analysis
    hire_date = rand_date(datetime(2022, 1, 1), datetime(2026, 3, 1))
    reps.append({
        "RepID": f"REP-{i+1:03d}",
        "RepName": f"{first_names[i]} {last_names[i]}",
        "Role": random.choice(rep_roles),
        "Team": random.choice(["Team Alpha", "Team Beta", "Team Gamma"]),
        "TherapyArea": random.choice(THERAPY_AREAS),
        "HireDate": hire_date.strftime("%Y-%m-%d"),
        "TenureMonths": (END - hire_date).days // 30,
        "IsActive": 1
    })
write_csv("DimRep.csv", reps, list(reps[0].keys()))
REP_BY_ID = {r["RepID"]: r for r in reps}

# ─── DIM: HCPs ────────────────────────────────────────────────
print("\n[DimHCP]")
hcp_first = ["James", "Robert", "Michael", "William", "David", "Richard", "Joseph",
             "Thomas", "Charles", "Christopher", "Sarah", "Jennifer", "Lisa", "Karen",
             "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Dorothy"]
hcp_last = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor", "Thomas", "Moore",
            "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]
hcp_tiers = ["Tier 1 - High Value", "Tier 2 - Medium Value", "Tier 3 - Low Value"]
tier_weights = [0.15, 0.35, 0.50]

hcps = []
for i in range(N_HCPS):
    state = random.choice(US_STATES)
    specialty = random.choice(SPECIALTIES)
    therapy = random.choice(THERAPY_AREAS)
    tier = random.choices(hcp_tiers, weights=tier_weights, k=1)[0]
    hcps.append({
        "HCPID": f"HCP-{i+1:04d}",
        "HCPName": f"Dr. {random.choice(hcp_first)} {random.choice(hcp_last)}",
        "Specialty": specialty,
        "TherapyArea": therapy,
        "State": state,
        "Region": US_REGIONS[state],
        "Tier": tier,
        "PrePeriodRxVolume": random.randint(0, 50) if "Tier 1" in tier else random.randint(0, 20),
        "IsTarget": 1 if random.random() < 0.7 else 0
    })
write_csv("DimHCP.csv", hcps, list(hcps[0].keys()))
# REALISM FIX: reps work a defined target pool, so a slice of HCPs is never
# engaged — keeps "HCP Reach" below 100% and gives "Rx from non-engaged HCPs" > 0.
callable_hcps = [h for h in hcps if h["IsTarget"] == 1 or random.random() < 0.35]

# ─── DIM: PATIENTS ─────────────────────────────────────────────
print("\n[DimPatient]")
age_groups = ["18-34", "35-49", "50-64", "65+"]
age_weights = [0.10, 0.25, 0.35, 0.30]

patients = []
for i in range(N_PATIENTS):
    state = random.choice(US_STATES)
    patients.append({
        "PatientID": f"PAT-{i+1:05d}",
        "AgeGroup": random.choices(age_groups, weights=age_weights, k=1)[0],
        "Gender": random.choice(["Male", "Female"]),
        "State": state,
        "Region": US_REGIONS[state],
        "InsuranceType": random.choices(INSURANCE_TYPES, weights=[0.45, 0.25, 0.15, 0.05, 0.10], k=1)[0],
        "TherapyArea": random.choice(THERAPY_AREAS),
        "Drug": random.choice(DRUGS),
        "EnrollmentDate": rand_date(START, END).strftime("%Y-%m-%d")
    })
write_csv("DimPatient.csv", patients, list(patients[0].keys()))

# ─── DIM: DRUGS ────────────────────────────────────────────────
print("\n[DimDrug]")
drugs = [
    {"DrugID": "DRG-001", "DrugName": "DrugAlpha-100mg", "TherapyArea": "Oncology", "LaunchDate": "2024-03-15", "IsSpecialty": 1},
    {"DrugID": "DRG-002", "DrugName": "DrugBeta-50mg", "TherapyArea": "Cardiology", "LaunchDate": "2023-09-01", "IsSpecialty": 0},
    {"DrugID": "DRG-003", "DrugName": "DrugGamma-200mg", "TherapyArea": "Immunology", "LaunchDate": "2025-01-10", "IsSpecialty": 1},
    {"DrugID": "DRG-004", "DrugName": "NeuroX-75mg", "TherapyArea": "Neurology", "LaunchDate": "2024-11-20", "IsSpecialty": 1},
    {"DrugID": "DRG-005", "DrugName": "CardioPlus-25mg", "TherapyArea": "Cardiology", "LaunchDate": "2025-06-01", "IsSpecialty": 0},
]
write_csv("DimDrug.csv", drugs, list(drugs[0].keys()))

# ─── FACT: HCP CALLS ──────────────────────────────────────────
print("\n[FactHCPCalls]")
calls = []
for i in range(N_CALLS):
    call_date = rand_date(START, END)
    rep = random.choice(reps)
    hcp = random.choice(callable_hcps)
    script = random.choice(SCRIPTS)

    # AI recommendation / acceptance (independent of connect — these are inputs)
    ai_recommended = random.random() < 0.6
    ai_followed = ai_recommended and random.random() < 0.7

    channel = random.choices(["Phone", "Email", "Video"], weights=[0.70, 0.20, 0.10], k=1)[0]
    tenure = rep["TenureMonths"]

    # ── REALISM FIX: connection is now driven by AI guidance, script, tenure,
    #    channel — so AI lift, A/B differences and the ramp-up curve are real.
    base_connect = 0.30
    tenure_adj = -0.05 if tenure < 6 else (0.0 if tenure < 18 else 0.04)
    script_adj = 0.03 if "Empathetic" in script else 0.0
    ai_adj = 0.09 if ai_followed else 0.0
    channel_adj = {"Phone": 0.0, "Email": 0.05, "Video": 0.10}[channel]
    connect_p = min(0.95, max(0.05, base_connect + tenure_adj + script_adj + ai_adj + channel_adj))
    connected = random.random() < connect_p
    if connected:
        outcome = "Connected"
    else:
        outcome = random.choices(["Voicemail", "No Answer", "Gatekeeper Block", "Wrong Number"],
                                 weights=[0.35, 0.30, 0.22, 0.13], k=1)[0]

    # Duration depends on outcome and script
    if connected:
        if "Empathetic" in script:
            duration = random.gauss(12, 4)  # empathetic tends longer
        else:
            duration = random.gauss(8, 3)
        duration = max(1, min(45, duration))
        # ── REALISM FIX: meaningful lifted by AI guidance + empathetic script
        meaningful_p = 0.55 + (0.12 if ai_followed else 0.0) + (0.08 if "Empathetic" in script else 0.0)
        meaningful = duration > 5 and random.random() < min(0.95, meaningful_p)
        interaction_type = random.choice(INTERACTION_TYPES)
    else:
        duration = random.uniform(0.1, 1.5)
        meaningful = False
        interaction_type = "N/A"

    # Post-call work
    after_call_work = random.gauss(3, 1.5) if connected else random.gauss(0.5, 0.3)
    after_call_work = max(0.2, min(15, after_call_work))

    # Scheduled vs actual
    scheduled_time = rand_time_evening()
    adherence = random.random() < 0.85

    # Compliance: script deviation (higher for new reps, lower for experienced)
    if tenure < 6:
        script_deviation = random.random() < 0.20  # new reps deviate more
    elif tenure < 18:
        script_deviation = random.random() < 0.10
    else:
        script_deviation = random.random() < 0.05

    # QA call quality score (1-10), correlated with meaningful + deviation
    if connected:
        base_quality = 5 + (1 if meaningful else -1) + random.gauss(0, 1.5)
        if script_deviation:
            base_quality -= 1.5  # deviation hurts quality
        call_quality = max(1, min(10, round(base_quality, 1)))
    else:
        call_quality = None

    # Adverse event flagged (rare, ~2% of connected calls)
    ae_flagged = connected and random.random() < 0.02

    calls.append({
        "CallID": f"CALL-{i+1:06d}",
        "CallDate": call_date.strftime("%Y-%m-%d"),
        "CallTime": rand_time_evening(),
        "RepID": rep["RepID"],
        "HCPID": hcp["HCPID"],
        "CallOutcome": outcome,
        "IsConnected": 1 if connected else 0,
        "DurationMinutes": round(duration, 1),
        "AfterCallWorkMinutes": round(after_call_work, 1),
        "AHT_Minutes": round(duration + after_call_work, 1),
        "IsMeaningfulInteraction": 1 if meaningful else 0,
        "InteractionType": interaction_type,
        "Script": script,
        "AIRecommended": 1 if ai_recommended else 0,
        "AIFollowed": 1 if ai_followed else 0,
        "ScheduledTime": scheduled_time,
        "IsScheduleAdherent": 1 if adherence else 0,
        "Drug": random.choice(DRUGS),
        "TherapyArea": hcp["TherapyArea"],
        "NotesTaken": 1 if connected and random.random() < 0.9 else 0,
        "FollowUpScheduled": 1 if meaningful and random.random() < 0.5 else 0,
        "HCPSentimentScore": round(random.uniform(1, 5), 1) if connected else None,
        "Channel": channel,
        "ScriptDeviation": 1 if script_deviation else 0,
        "CallQualityScore": call_quality,
        "AdverseEventFlagged": 1 if ae_flagged else 0
    })
write_csv("FactHCPCalls.csv", calls, list(calls[0].keys()))

# ─── FACT: PATIENT CASES ──────────────────────────────────────
print("\n[FactPatientCases]")
support_reps = [r for r in reps if r["Role"] == "Patient Support Specialist"] or reps
cases = []
for i in range(N_PATIENT_CASES):
    patient = random.choice(patients)
    rep = random.choice(support_reps)
    rx_date = rand_date(START, END)
    insurance = patient["InsuranceType"]

    # PA submission timing
    pa_submit_delay = random.randint(1, 7)
    pa_submit_date = rx_date + timedelta(days=pa_submit_delay)

    # PA decision timing depends on insurance type
    if insurance == "Commercial":
        pa_decision_delay = random.randint(3, 21)
    elif insurance == "Medicare":
        pa_decision_delay = random.randint(5, 30)
    elif insurance == "Medicaid":
        pa_decision_delay = random.randint(7, 45)
    else:
        pa_decision_delay = random.randint(2, 14)

    pa_decision_date = pa_submit_date + timedelta(days=pa_decision_delay)

    # PA outcome
    if insurance == "Commercial":
        pa_status = random.choices(PA_STATUSES, weights=[0.70, 0.15, 0.05, 0.10], k=1)[0]
    elif insurance in ["Medicare", "Medicaid"]:
        pa_status = random.choices(PA_STATUSES, weights=[0.55, 0.25, 0.08, 0.12], k=1)[0]
    else:
        pa_status = random.choices(PA_STATUSES, weights=[0.80, 0.10, 0.05, 0.05], k=1)[0]

    # First contact timing (decided early — drives abandonment via the 48h effect)
    first_contact_delay = random.choices([1, 2, 3, 4, 5, 6, 7],
                                          weights=[0.25, 0.25, 0.20, 0.12, 0.08, 0.05, 0.05], k=1)[0]
    first_contact_date = rx_date + timedelta(days=first_contact_delay)

    # Abandonment — worse on adverse PA outcomes, better when contacted within 48h
    if pa_status == "Denied":
        aband_p = 0.60
    elif pa_status == "Pending":
        aband_p = 0.40
    elif pa_status == "Appeal":
        aband_p = 0.35
    else:
        aband_p = 0.10
    if first_contact_delay <= 2:
        aband_p *= 0.7   # fast contact reduces abandonment (EXP-004 narrative)
    abandoned = random.random() < aband_p

    # Abandonment stage consistent with where the case stood
    if abandoned:
        if pa_status == "Pending":
            aband_stage = random.choice(["Pre-PA", "During PA"])
        elif pa_status == "Denied":
            aband_stage = random.choice(["During PA", "Post-PA"])
        elif pa_status == "Appeal":
            aband_stage = "During PA"
        else:
            aband_stage = random.choice(["Post-PA", "Post-Fulfillment"])
    else:
        aband_stage = None

    # Fulfillment and therapy start
    if pa_status == "Approved" and not abandoned:
        fulfillment_delay = random.randint(1, 10)
        fulfillment_date = pa_decision_date + timedelta(days=fulfillment_delay)
        first_dose_delay = random.randint(0, 5)
        first_dose_date = fulfillment_date + timedelta(days=first_dose_delay)
        time_to_therapy = (first_dose_date - rx_date).days
        case_status = "Resolved"
    elif abandoned:
        fulfillment_date = None
        first_dose_date = None
        time_to_therapy = None
        case_status = "Abandoned"
    else:
        fulfillment_date = None
        first_dose_date = None
        time_to_therapy = None
        case_status = random.choice(["Open", "In Progress"])

    # Number of touches
    n_touches = random.randint(1, 12) if not abandoned else random.randint(0, 4)

    # FCR
    first_call_resolved = random.random() < 0.35 if case_status == "Resolved" else False

    # Adherence (30/60/90 day checks) — only for patients who started therapy
    if first_dose_date and case_status == "Resolved":
        adherent_30 = random.random() < 0.85
        adherent_60 = random.random() < 0.72 if adherent_30 else random.random() < 0.30
        adherent_90 = random.random() < 0.65 if adherent_60 else random.random() < 0.20
    else:
        adherent_30 = None
        adherent_60 = None
        adherent_90 = None

    cases.append({
        "CaseID": f"CASE-{i+1:05d}",
        "PatientID": patient["PatientID"],
        "RepID": rep["RepID"],
        "Drug": patient["Drug"],
        "TherapyArea": patient["TherapyArea"],
        "InsuranceType": insurance,
        "RxDate": rx_date.strftime("%Y-%m-%d"),
        "FirstContactDate": first_contact_date.strftime("%Y-%m-%d"),
        "FirstContactDelayDays": first_contact_delay,
        "PASubmitDate": pa_submit_date.strftime("%Y-%m-%d"),
        "PADecisionDate": pa_decision_date.strftime("%Y-%m-%d") if pa_decision_date <= END else None,
        "PAStatus": pa_status,
        "PADecisionDelayDays": pa_decision_delay,
        "FulfillmentDate": fulfillment_date.strftime("%Y-%m-%d") if fulfillment_date else None,
        "FirstDoseDate": first_dose_date.strftime("%Y-%m-%d") if first_dose_date else None,
        "TimeToTherapyDays": time_to_therapy,
        "CaseStatus": case_status,
        "IsAbandoned": 1 if abandoned else 0,
        "AbandonmentReason": random.choice(ABANDONMENT_REASONS) if abandoned else None,
        "AbandonmentStage": aband_stage,
        "NumberOfTouches": n_touches,
        "FirstCallResolved": 1 if first_call_resolved else 0,
        "Adherent30": 1 if adherent_30 else (0 if adherent_30 is not None else None),
        "Adherent60": 1 if adherent_60 else (0 if adherent_60 is not None else None),
        "Adherent90": 1 if adherent_90 else (0 if adherent_90 is not None else None),
        "CaseResolutionDays": (pa_decision_date - rx_date).days if case_status == "Resolved" else None
    })
write_csv("FactPatientCases.csv", cases, list(cases[0].keys()))

# ─── FACT: RX (PRESCRIPTIONS) ─────────────────────────────────
print("\n[FactRx]")
# REALISM FIX: HCPs that get engaged (will be called) prescribe more & more NBRx,
# so the "Rx from engaged HCPs" comparison is meaningful.
engaged_hcp_ids = set(c["HCPID"] for c in calls if c["IsConnected"] == 1)
rx_rows = []
rx_id = 0
for hcp in hcps:
    base = random.randint(0, hcp["PrePeriodRxVolume"] + 10)
    if hcp["HCPID"] in engaged_hcp_ids:
        base = int(base * random.uniform(1.2, 1.8))   # engagement lifts Rx
        nbrx_p = 0.32
    else:
        nbrx_p = 0.15
    for _ in range(base):
        rx_id += 1
        rx_date = rand_date(START, END)
        rx_rows.append({
            "RxID": f"RX-{rx_id:06d}",
            "HCPID": hcp["HCPID"],
            "RxDate": rx_date.strftime("%Y-%m-%d"),
            "Drug": random.choice(DRUGS),
            "TherapyArea": hcp["TherapyArea"],
            "IsNewToBrand": 1 if random.random() < nbrx_p else 0,
            "Quantity": random.choice([30, 60, 90]),
            "State": hcp["State"],
            "Region": hcp["Region"]
        })
write_csv("FactRx.csv", rx_rows, list(rx_rows[0].keys()))

# ─── FACT: MSL PARTNER USAGE ──────────────────────────────────
print("\n[FactMSLPartnerUsage]")
msl_reps = [r for r in reps if r["Role"] == "MSL"] or reps[:5]

MSL_TOPICS = [
    "Mechanism of Action", "Clinical Trial Data", "Dosing Guidelines",
    "Adverse Events / Safety", "Patient Selection Criteria", "Drug Interactions",
    "Competitor Comparison", "Real-World Evidence", "Guidelines / Protocols",
    "Biomarker Data", "Pharmacokinetics", "Off-label Evidence Request",
    "Combination Therapy", "Subgroup Analysis", "Long-term Outcomes"
]
MSL_QUERY_TYPES = ["Pre-Meeting Prep", "Live During HCP Call", "Post-Call Follow-up", "Self-Study"]
MSL_ANSWER_QUALITY = ["Fully Answered", "Partially Answered", "No Answer Found", "Redirected to Medical"]

msl_usage = []
usage_id = 0
for d_offset in range((END - START).days + 1):
    current_date = START + timedelta(days=d_offset)
    if current_date.isoweekday() >= 6:  # skip weekends
        continue
    for msl in msl_reps:
        n_queries = random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8],
                                   weights=[0.05, 0.10, 0.15, 0.25, 0.20, 0.12, 0.07, 0.04, 0.02], k=1)[0]
        for _ in range(n_queries):
            usage_id += 1
            topic = random.choice(MSL_TOPICS)
            query_type = random.choices(MSL_QUERY_TYPES, weights=[0.35, 0.25, 0.20, 0.20], k=1)[0]
            answer_quality = random.choices(MSL_ANSWER_QUALITY, weights=[0.65, 0.20, 0.08, 0.07], k=1)[0]
            if answer_quality == "Fully Answered":
                time_to_answer_sec = random.gauss(8, 3)
            elif answer_quality == "Partially Answered":
                time_to_answer_sec = random.gauss(15, 5)
            else:
                time_to_answer_sec = random.gauss(25, 8)
            time_to_answer_sec = max(1, min(120, time_to_answer_sec))

            used_in_interaction = (query_type in ["Pre-Meeting Prep", "Live During HCP Call"]
                                   and answer_quality in ["Fully Answered", "Partially Answered"]
                                   and random.random() < 0.75)

            if answer_quality == "Fully Answered":
                satisfaction = random.choices([4, 5], weights=[0.30, 0.70], k=1)[0]
            elif answer_quality == "Partially Answered":
                satisfaction = random.choices([2, 3, 4], weights=[0.15, 0.50, 0.35], k=1)[0]
            else:
                satisfaction = random.choices([1, 2, 3], weights=[0.40, 0.40, 0.20], k=1)[0]

            if answer_quality in ["Fully Answered", "Partially Answered"]:
                time_saved_min = max(2, min(45, random.gauss(12, 5)))
            else:
                time_saved_min = 0

            msl_usage.append({
                "UsageID": f"MSL-{usage_id:06d}",
                "UsageDate": current_date.strftime("%Y-%m-%d"),
                "RepID": msl["RepID"],
                "Drug": random.choice(DRUGS),
                "TherapyArea": msl["TherapyArea"],
                "Topic": topic,
                "QueryType": query_type,
                "AnswerQuality": answer_quality,
                "TimeToAnswerSec": round(time_to_answer_sec, 1),
                "TimeSavedMinutes": round(time_saved_min, 1),
                "UsedInHCPInteraction": 1 if used_in_interaction else 0,
                "UserSatisfaction": satisfaction,
                "HCPID": random.choice(hcps)["HCPID"] if used_in_interaction else None
            })
write_csv("FactMSLPartnerUsage.csv", msl_usage, list(msl_usage[0].keys()))

# ─── DIM: EXPERIMENTS ─────────────────────────────────────────
print("\n[DimExperiment]")
experiments = [
    {"ExperimentID": "EXP-001", "ExperimentName": "Script Tone Test",
     "Hypothesis": "Empathetic opening script increases meaningful interaction rate vs. direct script",
     "PrimaryKPI": "Meaningful Interaction Rate", "GuardrailKPI": "Avg Call Duration (cost)",
     "StartDate": "2025-08-01", "EndDate": "2025-09-15", "Status": "Concluded - Winner",
     "Winner": "Script A - Empathetic", "SampleSizeTarget": 2000, "SampleSizeActual": 2134,
     "ConfidenceLevel": 0.95, "ObservedLift": 0.12, "TherapyArea": "All", "TargetPopulation": "All HCPs"},
    {"ExperimentID": "EXP-002", "ExperimentName": "Call Timing Optimization",
     "Hypothesis": "Afternoon calls (2-5pm ET) have higher connect rate than morning calls (9-12pm ET)",
     "PrimaryKPI": "Connect Rate", "GuardrailKPI": "Meaningful Interaction Rate",
     "StartDate": "2025-09-01", "EndDate": "2025-10-31", "Status": "Concluded - Winner",
     "Winner": "Afternoon (2-5pm ET)", "SampleSizeTarget": 3000, "SampleSizeActual": 3247,
     "ConfidenceLevel": 0.95, "ObservedLift": 0.08, "TherapyArea": "All", "TargetPopulation": "All HCPs"},
    {"ExperimentID": "EXP-003", "ExperimentName": "AI Call Prioritization v2",
     "Hypothesis": "Updated AI model improves connect rate vs. v1 model",
     "PrimaryKPI": "Connect Rate", "GuardrailKPI": "AI Acceptance Rate",
     "StartDate": "2025-11-01", "EndDate": "2026-01-15", "Status": "Concluded - No Significant Difference",
     "Winner": None, "SampleSizeTarget": 4000, "SampleSizeActual": 3891,
     "ConfidenceLevel": 0.95, "ObservedLift": 0.02, "TherapyArea": "All", "TargetPopulation": "Target HCPs only"},
    {"ExperimentID": "EXP-004", "ExperimentName": "Patient 48h Contact",
     "Hypothesis": "Contacting patients within 48h of Rx reduces abandonment vs. standard 5-day window",
     "PrimaryKPI": "Abandonment Rate", "GuardrailKPI": "First Call Resolution Rate",
     "StartDate": "2025-10-01", "EndDate": "2025-12-31", "Status": "Concluded - Winner",
     "Winner": "48h Contact", "SampleSizeTarget": 500, "SampleSizeActual": 523,
     "ConfidenceLevel": 0.95, "ObservedLift": -0.18, "TherapyArea": "All", "TargetPopulation": "New patients"},
    {"ExperimentID": "EXP-005", "ExperimentName": "MSL Partner Live Assist",
     "Hypothesis": "MSLs using MSL Partner during live HCP calls have higher HCP satisfaction",
     "PrimaryKPI": "HCP Sentiment Score", "GuardrailKPI": "Call Duration",
     "StartDate": "2026-01-15", "EndDate": "2026-03-15", "Status": "Concluded - Winner",
     "Winner": "With MSL Partner", "SampleSizeTarget": 1000, "SampleSizeActual": 987,
     "ConfidenceLevel": 0.95, "ObservedLift": 0.15, "TherapyArea": "Oncology", "TargetPopulation": "Tier 1 HCPs"},
    {"ExperimentID": "EXP-006", "ExperimentName": "Oncology Multi-touch Sequence",
     "Hypothesis": "3-touch sequence (call-email-call) outperforms 2-touch (call-call) for oncologists",
     "PrimaryKPI": "Follow Up Rate", "GuardrailKPI": "Cost per Engagement",
     "StartDate": "2026-02-01", "EndDate": None, "Status": "Running",
     "Winner": None, "SampleSizeTarget": 600, "SampleSizeActual": 342,
     "ConfidenceLevel": 0.95, "ObservedLift": None, "TherapyArea": "Oncology", "TargetPopulation": "Oncologists"},
    {"ExperimentID": "EXP-007", "ExperimentName": "PA Submission Quality Check",
     "Hypothesis": "Adding a pre-submission checklist reduces PA denial rate",
     "PrimaryKPI": "PA Approval Rate", "GuardrailKPI": "PA Submission Delay",
     "StartDate": "2026-03-01", "EndDate": None, "Status": "Running",
     "Winner": None, "SampleSizeTarget": 400, "SampleSizeActual": 187,
     "ConfidenceLevel": 0.95, "ObservedLift": None, "TherapyArea": "All", "TargetPopulation": "All patients"},
    {"ExperimentID": "EXP-008", "ExperimentName": "Cardiology Personalized Messaging",
     "Hypothesis": "AI-personalized content per HCP profile improves meaningful interaction rate",
     "PrimaryKPI": "Meaningful Interaction Rate", "GuardrailKPI": "Connect Rate",
     "StartDate": "2026-04-01", "EndDate": None, "Status": "Planned",
     "Winner": None, "SampleSizeTarget": 800, "SampleSizeActual": 0,
     "ConfidenceLevel": 0.95, "ObservedLift": None, "TherapyArea": "Cardiology", "TargetPopulation": "Cardiologists"},
]
write_csv("DimExperiment.csv", experiments, list(experiments[0].keys()))

# ─── FACT: FINANCIALS (MONTHLY GRAIN) ─────────────────────────
print("\n[FactFinancials]")
financials = []
fin_id = 0
d = START
while d <= END:
    year_month = d.strftime("%Y-%m")
    month_start = d
    if d.month == 12:
        next_month = datetime(d.year + 1, 1, 1)
    else:
        next_month = datetime(d.year, d.month + 1, 1)

    month_index = (d.year - START.year) * 12 + d.month - START.month
    growth_factor = 1 + month_index * 0.02  # 2% monthly growth

    n_active_reps = N_REPS
    avg_rep_monthly_cost = 3500  # Athens salary + overhead in EUR
    total_rep_cost = round(n_active_reps * avg_rep_monthly_cost * growth_factor)
    tech_cost = round(random.gauss(18000, 2000) * growth_factor)
    mgmt_cost = round(random.gauss(12000, 1500))
    total_cost = total_rep_cost + tech_cost + mgmt_cost

    base_monthly_fee = 120000  # USD
    month_calls = sum(1 for c in calls if c["CallDate"][:7] == year_month)
    month_cases = sum(1 for c in cases if c["RxDate"][:7] == year_month)
    per_engagement_rev = month_calls * random.uniform(8, 12)
    per_case_rev = month_cases * random.uniform(45, 65)
    total_revenue = round(base_monthly_fee + per_engagement_rev + per_case_rev)

    cost_per_call = round(total_cost / max(month_calls, 1), 2)
    cost_per_case = round(total_cost / max(month_cases, 1), 2) if month_cases > 0 else None

    fin_id += 1
    financials.append({
        "FinancialID": f"FIN-{fin_id:03d}",
        "YearMonth": year_month,
        "MonthDate": month_start.strftime("%Y-%m-%d"),
        "RepHeadcount": n_active_reps,
        "RepCost_EUR": total_rep_cost,
        "TechCost_EUR": tech_cost,
        "MgmtCost_EUR": mgmt_cost,
        "TotalCost_EUR": total_cost,
        "BaseRevenue_USD": base_monthly_fee,
        "EngagementRevenue_USD": round(per_engagement_rev),
        "CaseRevenue_USD": round(per_case_rev),
        "TotalRevenue_USD": total_revenue,
        "TotalCalls": month_calls,
        "TotalCases": month_cases,
        "CostPerCall_EUR": cost_per_call,
        "CostPerCase_EUR": cost_per_case,
        "GrossMargin_USD": round(total_revenue - total_cost * 1.1),  # rough EUR→USD
        "GrossMarginPct": round((total_revenue - total_cost * 1.1) / max(total_revenue, 1), 3)
    })
    d = next_month
write_csv("FactFinancials.csv", financials, list(financials[0].keys()))

# ─── SUMMARY ──────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"DONE. All files in: {OUT}")
print(f"Period: {START.strftime('%Y-%m-%d')} to {END.strftime('%Y-%m-%d')}")
