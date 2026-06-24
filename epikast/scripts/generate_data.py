"""
Generate synthetic Epikast-style pharma operations data.
Star schema: 6 fact tables + 5 dimension tables + 1 calendar + 1 experiment dim.
Covers HCP engagement, patient support, rep performance, MSL Partner usage,
A/B experiment tracking, and program financials.
"""

import csv
import random
import os
from datetime import datetime, timedelta

random.seed(42)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
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
# CSO clients — each team is dedicated to one pharma client
TEAM_CLIENT = {
    "Team Alpha": "PharmaClient A",
    "Team Beta":  "PharmaClient B",
    "Team Gamma": "PharmaClient C",
}

reps = []
for i in range(N_REPS):
    hire_date = rand_date(datetime(2022, 1, 1), datetime(2025, 6, 30))
    team = random.choice(["Team Alpha", "Team Beta", "Team Gamma"])
    reps.append({
        "RepID": f"REP-{i+1:03d}",
        "RepName": f"{first_names[i]} {last_names[i]}",
        "Role": random.choice(rep_roles),
        "Team": team,
        "Client": TEAM_CLIENT[team],
        "TherapyArea": random.choice(THERAPY_AREAS),
        "HireDate": hire_date.strftime("%Y-%m-%d"),
        "TenureMonths": (END - hire_date).days // 30,
        "IsActive": 1
    })
write_csv("DimRep.csv", reps, list(reps[0].keys()))

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

# ─── DIM: PATIENTS ─────────────────────────────────────────────
print("\n[DimPatient]")
pat_first = ["John", "Emily", "Daniel", "Jessica", "Matthew", "Amanda", "Anthony",
             "Stephanie", "Mark", "Nicole", "Steven", "Michelle", "Paul", "Laura",
             "Andrew", "Kimberly", "Joshua", "Megan", "Kevin", "Rachel"]
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
    hcp = random.choice(hcps)
    outcome = random.choices(CALL_OUTCOMES, weights=[0.30, 0.25, 0.20, 0.15, 0.10], k=1)[0]
    connected = outcome == "Connected"
    script = random.choice(SCRIPTS)

    # Duration depends on outcome and script
    if connected:
        if "Empathetic" in script:
            duration = random.gauss(12, 4)  # empathetic tends longer
        else:
            duration = random.gauss(8, 3)
        duration = max(1, min(45, duration))
        meaningful = duration > 5 and random.random() < 0.65
        interaction_type = random.choice(INTERACTION_TYPES)
    else:
        duration = random.uniform(0.1, 1.5)
        meaningful = False
        interaction_type = "N/A"

    # AI recommendation
    ai_recommended = random.random() < 0.6
    ai_followed = ai_recommended and random.random() < 0.7

    # Post-call work
    after_call_work = random.gauss(3, 1.5) if connected else random.gauss(0.5, 0.3)
    after_call_work = max(0.2, min(15, after_call_work))

    # Scheduled vs actual
    scheduled_time = rand_time_evening()
    adherence = random.random() < 0.85

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
        "HCPSentimentScore": round(random.uniform(1, 5), 1) if connected else None
    })
write_csv("FactHCPCalls.csv", calls, list(calls[0].keys()))

# ─── FACT: PATIENT CASES ──────────────────────────────────────
print("\n[FactPatientCases]")
cases = []
for i in range(N_PATIENT_CASES):
    patient = random.choice(patients)
    rep = random.choice([r for r in reps if r["Role"] == "Patient Support Specialist"] or [random.choice(reps)])
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

    # Abandonment
    if pa_status == "Denied":
        abandoned = random.random() < 0.60
    elif pa_status == "Pending":
        abandoned = random.random() < 0.40
    elif pa_status == "Appeal":
        abandoned = random.random() < 0.35
    else:
        abandoned = random.random() < 0.10

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

    # First contact timing
    first_contact_delay = random.choices([1, 2, 3, 4, 5, 6, 7],
                                          weights=[0.25, 0.25, 0.20, 0.12, 0.08, 0.05, 0.05], k=1)[0]
    first_contact_date = rx_date + timedelta(days=first_contact_delay)

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
        "AbandonmentStage": random.choice(["Pre-PA", "During PA", "Post-PA", "Post-Fulfillment"]) if abandoned else None,
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
rx_rows = []
rx_id = 0
for hcp in hcps:
    # Each HCP writes some prescriptions over the period
    n_rx = random.randint(0, hcp["PrePeriodRxVolume"] + 10)
    for _ in range(n_rx):
        rx_id += 1
        rx_date = rand_date(START, END)
        drug = random.choice(DRUGS)
        is_new_to_brand = random.random() < 0.25
        rx_rows.append({
            "RxID": f"RX-{rx_id:06d}",
            "HCPID": hcp["HCPID"],
            "RxDate": rx_date.strftime("%Y-%m-%d"),
            "Drug": drug,
            "TherapyArea": hcp["TherapyArea"],
            "IsNewToBrand": 1 if is_new_to_brand else 0,
            "Quantity": random.choice([30, 60, 90]),
            "State": hcp["State"],
            "Region": hcp["Region"]
        })
write_csv("FactRx.csv", rx_rows, list(rx_rows[0].keys()))

# ─── FACT: MSL PARTNER USAGE ──────────────────────────────────
print("\n[FactMSLPartnerUsage]")
msl_reps = [r for r in reps if r["Role"] == "MSL"]
if not msl_reps:
    # ensure at least some MSL reps exist
    msl_reps = reps[:5]

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
        # Each MSL makes 0-8 queries per working day
        n_queries = random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8],
                                    weights=[0.05, 0.10, 0.15, 0.25, 0.20, 0.12, 0.07, 0.04, 0.02], k=1)[0]
        for _ in range(n_queries):
            usage_id += 1
            topic = random.choice(MSL_TOPICS)
            query_type = random.choices(MSL_QUERY_TYPES,
                                         weights=[0.35, 0.25, 0.20, 0.20], k=1)[0]

            # Time to answer varies by quality
            answer_quality = random.choices(MSL_ANSWER_QUALITY,
                                             weights=[0.65, 0.20, 0.08, 0.07], k=1)[0]
            if answer_quality == "Fully Answered":
                time_to_answer_sec = random.gauss(8, 3)
            elif answer_quality == "Partially Answered":
                time_to_answer_sec = random.gauss(15, 5)
            else:
                time_to_answer_sec = random.gauss(25, 8)
            time_to_answer_sec = max(1, min(120, time_to_answer_sec))

            # Was the answer used in an HCP interaction?
            used_in_interaction = (query_type in ["Pre-Meeting Prep", "Live During HCP Call"]
                                   and answer_quality in ["Fully Answered", "Partially Answered"]
                                   and random.random() < 0.75)

            # User satisfaction
            if answer_quality == "Fully Answered":
                satisfaction = random.choices([4, 5], weights=[0.30, 0.70], k=1)[0]
            elif answer_quality == "Partially Answered":
                satisfaction = random.choices([2, 3, 4], weights=[0.15, 0.50, 0.35], k=1)[0]
            else:
                satisfaction = random.choices([1, 2, 3], weights=[0.40, 0.40, 0.20], k=1)[0]

            # Time saved estimate (minutes) — compared to manual literature search
            if answer_quality in ["Fully Answered", "Partially Answered"]:
                time_saved_min = random.gauss(12, 5)
                time_saved_min = max(2, min(45, time_saved_min))
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
    {
        "ExperimentID": "EXP-001",
        "ExperimentName": "Script Tone Test",
        "Hypothesis": "Empathetic opening script increases meaningful interaction rate vs. direct script",
        "PrimaryKPI": "Meaningful Interaction Rate",
        "GuardrailKPI": "Avg Call Duration (cost)",
        "StartDate": "2025-08-01",
        "EndDate": "2025-09-15",
        "Status": "Concluded - Winner",
        "Winner": "Script A - Empathetic",
        "SampleSizeTarget": 2000,
        "SampleSizeActual": 2134,
        "ConfidenceLevel": 0.95,
        "ObservedLift": 0.12,
        "TherapyArea": "All",
        "TargetPopulation": "All HCPs"
    },
    {
        "ExperimentID": "EXP-002",
        "ExperimentName": "Call Timing Optimization",
        "Hypothesis": "Afternoon calls (2-5pm ET) have higher connect rate than morning calls (9-12pm ET)",
        "PrimaryKPI": "Connect Rate",
        "GuardrailKPI": "Meaningful Interaction Rate",
        "StartDate": "2025-09-01",
        "EndDate": "2025-10-31",
        "Status": "Concluded - Winner",
        "Winner": "Afternoon (2-5pm ET)",
        "SampleSizeTarget": 3000,
        "SampleSizeActual": 3247,
        "ConfidenceLevel": 0.95,
        "ObservedLift": 0.08,
        "TherapyArea": "All",
        "TargetPopulation": "All HCPs"
    },
    {
        "ExperimentID": "EXP-003",
        "ExperimentName": "AI Call Prioritization v2",
        "Hypothesis": "Updated AI model improves connect rate vs. v1 model",
        "PrimaryKPI": "Connect Rate",
        "GuardrailKPI": "AI Acceptance Rate",
        "StartDate": "2025-11-01",
        "EndDate": "2026-01-15",
        "Status": "Concluded - No Significant Difference",
        "Winner": None,
        "SampleSizeTarget": 4000,
        "SampleSizeActual": 3891,
        "ConfidenceLevel": 0.95,
        "ObservedLift": 0.02,
        "TherapyArea": "All",
        "TargetPopulation": "Target HCPs only"
    },
    {
        "ExperimentID": "EXP-004",
        "ExperimentName": "Patient 48h Contact",
        "Hypothesis": "Contacting patients within 48h of Rx reduces abandonment vs. standard 5-day window",
        "PrimaryKPI": "Abandonment Rate",
        "GuardrailKPI": "First Call Resolution Rate",
        "StartDate": "2025-10-01",
        "EndDate": "2025-12-31",
        "Status": "Concluded - Winner",
        "Winner": "48h Contact",
        "SampleSizeTarget": 500,
        "SampleSizeActual": 523,
        "ConfidenceLevel": 0.95,
        "ObservedLift": -0.18,
        "TherapyArea": "All",
        "TargetPopulation": "New patients"
    },
    {
        "ExperimentID": "EXP-005",
        "ExperimentName": "MSL Partner Live Assist",
        "Hypothesis": "MSLs using MSL Partner during live HCP calls have higher HCP satisfaction",
        "PrimaryKPI": "HCP Sentiment Score",
        "GuardrailKPI": "Call Duration",
        "StartDate": "2026-01-15",
        "EndDate": "2026-03-15",
        "Status": "Concluded - Winner",
        "Winner": "With MSL Partner",
        "SampleSizeTarget": 1000,
        "SampleSizeActual": 987,
        "ConfidenceLevel": 0.95,
        "ObservedLift": 0.15,
        "TherapyArea": "Oncology",
        "TargetPopulation": "Tier 1 HCPs"
    },
    {
        "ExperimentID": "EXP-006",
        "ExperimentName": "Oncology Multi-touch Sequence",
        "Hypothesis": "3-touch sequence (call-email-call) outperforms 2-touch (call-call) for oncologists",
        "PrimaryKPI": "Follow Up Rate",
        "GuardrailKPI": "Cost per Engagement",
        "StartDate": "2026-02-01",
        "EndDate": None,
        "Status": "Running",
        "Winner": None,
        "SampleSizeTarget": 600,
        "SampleSizeActual": 342,
        "ConfidenceLevel": 0.95,
        "ObservedLift": None,
        "TherapyArea": "Oncology",
        "TargetPopulation": "Oncologists"
    },
    {
        "ExperimentID": "EXP-007",
        "ExperimentName": "PA Submission Quality Check",
        "Hypothesis": "Adding a pre-submission checklist reduces PA denial rate",
        "PrimaryKPI": "PA Approval Rate",
        "GuardrailKPI": "PA Submission Delay",
        "StartDate": "2026-03-01",
        "EndDate": None,
        "Status": "Running",
        "Winner": None,
        "SampleSizeTarget": 400,
        "SampleSizeActual": 187,
        "ConfidenceLevel": 0.95,
        "ObservedLift": None,
        "TherapyArea": "All",
        "TargetPopulation": "All patients"
    },
    {
        "ExperimentID": "EXP-008",
        "ExperimentName": "Cardiology Personalized Messaging",
        "Hypothesis": "AI-personalized content per HCP profile improves meaningful interaction rate",
        "PrimaryKPI": "Meaningful Interaction Rate",
        "GuardrailKPI": "Connect Rate",
        "StartDate": "2026-04-01",
        "EndDate": None,
        "Status": "Planned",
        "Winner": None,
        "SampleSizeTarget": 800,
        "SampleSizeActual": 0,
        "ConfidenceLevel": 0.95,
        "ObservedLift": None,
        "TherapyArea": "Cardiology",
        "TargetPopulation": "Cardiologists"
    },
]
write_csv("DimExperiment.csv", experiments, list(experiments[0].keys()))

# ─── FACT: FINANCIALS (MONTHLY GRAIN) ─────────────────────────
print("\n[FactFinancials]")
financials = []
fin_id = 0

# Monthly data for the program
d = START
while d <= END:
    year_month = d.strftime("%Y-%m")
    month_start = d
    # Move to next month
    if d.month == 12:
        next_month = datetime(d.year + 1, 1, 1)
    else:
        next_month = datetime(d.year, d.month + 1, 1)

    # Base costs grow slightly over time (hiring)
    month_index = (d.year - START.year) * 12 + d.month - START.month
    growth_factor = 1 + month_index * 0.02  # 2% monthly growth

    # Rep costs
    n_active_reps = N_REPS
    avg_rep_monthly_cost = 3500  # Athens salary + overhead in EUR
    total_rep_cost = round(n_active_reps * avg_rep_monthly_cost * growth_factor)

    # Technology costs (platform, AI, infrastructure)
    tech_cost = round(random.gauss(18000, 2000) * growth_factor)

    # Management overhead
    mgmt_cost = round(random.gauss(12000, 1500))

    # Total program cost
    total_cost = total_rep_cost + tech_cost + mgmt_cost

    # Revenue (client contract — monthly fee + per-engagement variable)
    base_monthly_fee = 120000  # USD
    # Count calls and cases this month from generated data
    month_calls = sum(1 for c in calls if c["CallDate"][:7] == year_month)
    month_cases = sum(1 for c in cases if c["RxDate"][:7] == year_month)
    per_engagement_rev = month_calls * random.uniform(8, 12)  # $8-12 per call
    per_case_rev = month_cases * random.uniform(45, 65)  # $45-65 per case

    total_revenue = round(base_monthly_fee + per_engagement_rev + per_case_rev)

    # Cost per engagement
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
        "GrossMargin_USD": round(total_revenue - total_cost * 1.1),  # rough EUR->USD
        "GrossMarginPct": round((total_revenue - total_cost * 1.1) / max(total_revenue, 1), 3)
    })

    d = next_month
write_csv("FactFinancials.csv", financials, list(financials[0].keys()))

# ─── SUMMARY ──────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"DONE. All files in: {OUT}")
print(f"\nDimensions:")
print(f"  DimCalendar, DimRep, DimHCP, DimPatient, DimDrug, DimExperiment")
print(f"\nFacts:")
print(f"  FactHCPCalls, FactPatientCases, FactRx,")
print(f"  FactMSLPartnerUsage, FactFinancials")
print(f"\nPeriod: {START.strftime('%Y-%m-%d')} to {END.strftime('%Y-%m-%d')}")
