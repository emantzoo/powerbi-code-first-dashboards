"""Generate sample Finance/Budgeting CSV data."""
import csv, random, os

random.seed(42)
OUT = os.path.dirname(os.path.abspath(__file__))

# --- DimDepartment ---
departments = [
    ("DEPT01", "Finance", "Sarah Chen", 45),
    ("DEPT02", "Engineering", "James Wilson", 120),
    ("DEPT03", "Marketing", "Maria Lopez", 35),
    ("DEPT04", "Sales", "Robert Kim", 80),
    ("DEPT05", "HR", "Emma Davis", 25),
    ("DEPT06", "Operations", "David Brown", 90),
    ("DEPT07", "Legal", "Patricia Moore", 15),
    ("DEPT08", "Product", "Michael Zhang", 55),
]
with open(os.path.join(OUT, "DimDepartment.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["department_id","department_name","department_head","headcount"])
    for r in departments: w.writerow(r)

# --- DimAccount ---
accounts = [
    ("ACC001", "Salaries & Wages", "Personnel", "Compensation"),
    ("ACC002", "Benefits & Insurance", "Personnel", "Compensation"),
    ("ACC003", "Travel & Entertainment", "Operating", "Travel"),
    ("ACC004", "Software Licenses", "Operating", "Technology"),
    ("ACC005", "Office Supplies", "Operating", "Facilities"),
    ("ACC006", "Marketing Spend", "Operating", "Services"),
    ("ACC007", "Utilities", "Administrative", "Facilities"),
    ("ACC008", "Rent & Facilities", "Administrative", "Facilities"),
    ("ACC009", "Training & Development", "Operating", "Services"),
    ("ACC010", "Professional Services", "Operating", "Services"),
    ("ACC011", "Depreciation", "Capital", "Facilities"),
    ("ACC012", "Maintenance", "Administrative", "Facilities"),
    ("ACC013", "Telecommunications", "Operating", "Technology"),
    ("ACC014", "Contracted Services", "Operating", "Services"),
    ("ACC015", "Miscellaneous", "Administrative", "Services"),
]
with open(os.path.join(OUT, "DimAccount.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["account_id","account_name","account_type","account_group"])
    for r in accounts: w.writerow(r)

# --- DimCostCenter ---
regions = ["North", "South", "East", "West"]
cc_types = ["Direct", "Indirect", "Overhead"]
cc_names = [
    "Marketing Operations", "IT Infrastructure", "Sales West", "Sales East",
    "Finance Core", "HR Services", "Engineering Platform", "Engineering Data",
    "Product Design", "Product Analytics", "Operations Logistics", "Operations Support",
    "Legal Compliance", "Legal Contracts", "Marketing Digital", "Sales North",
    "Finance Planning", "HR Recruiting", "Engineering Mobile", "Operations Warehouse"
]
# Map cost centers to departments
cc_dept_map = {
    "CC001": "DEPT03", "CC002": "DEPT02", "CC003": "DEPT04", "CC004": "DEPT04",
    "CC005": "DEPT01", "CC006": "DEPT05", "CC007": "DEPT02", "CC008": "DEPT02",
    "CC009": "DEPT08", "CC010": "DEPT08", "CC011": "DEPT06", "CC012": "DEPT06",
    "CC013": "DEPT07", "CC014": "DEPT07", "CC015": "DEPT03", "CC016": "DEPT04",
    "CC017": "DEPT01", "CC018": "DEPT05", "CC019": "DEPT02", "CC020": "DEPT06",
}
cost_centers = []
with open(os.path.join(OUT, "DimCostCenter.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["cost_center_id","cost_center_name","region","cost_center_type","department_id"])
    for i, name in enumerate(cc_names):
        ccid = f"CC{i+1:03d}"
        row = (ccid, name, regions[i % 4], cc_types[i % 3], cc_dept_map[ccid])
        cost_centers.append(row)
        w.writerow(row)

# Amount ranges by account (Salaries are high, Office Supplies are low)
account_ranges = {
    "ACC001": (80000, 200000), "ACC002": (20000, 60000), "ACC003": (3000, 25000),
    "ACC004": (5000, 40000), "ACC005": (1000, 8000), "ACC006": (10000, 80000),
    "ACC007": (2000, 12000), "ACC008": (15000, 50000), "ACC009": (2000, 15000),
    "ACC010": (5000, 35000), "ACC011": (3000, 20000), "ACC012": (1000, 10000),
    "ACC013": (1000, 8000), "ACC014": (5000, 30000), "ACC015": (500, 5000),
}

# --- FactBudget ---
budget_rows = []
bid = 1
months = [f"2023-{m:02d}-01" for m in range(1, 13)] + [f"2024-{m:02d}-01" for m in range(1, 13)]
with open(os.path.join(OUT, "FactBudget.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["budget_id","cost_center_id","account_id","department_id","budget_month","budget_amount"])
    for cc in cost_centers:
        ccid, _, _, _, dept = cc
        # Each cost center has 6-10 accounts budgeted
        cc_accounts = random.sample([a[0] for a in accounts], random.randint(6, 10))
        for acc in cc_accounts:
            lo, hi = account_ranges[acc]
            base = random.uniform(lo, hi)
            for month in months:
                # Budget is stable with slight monthly variation
                amt = round(base * random.uniform(0.9, 1.1), 2)
                w.writerow([bid, ccid, acc, dept, month, amt])
                budget_rows.append((ccid, acc, dept, month, amt))
                bid += 1

# --- FactActuals ---
vendors = ["Acme Corp", "TechVentures", "GlobalServ", "PrimeSoft", "DataPro",
           "CloudBase", "NetWorks Inc", "BrightPath", "CoreLogic", "AlphaServices",
           "OmniTech", "SwiftHire", "GreenLight", "BlueWave", "RedPoint"]
aid = 1
with open(os.path.join(OUT, "FactActuals.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["actual_id","cost_center_id","account_id","department_id","transaction_date","amount","vendor"])
    for ccid, acc, dept, month, budget_amt in budget_rows:
        # Actuals vary from budget: -20% to +30% (slight overspend bias)
        variance = random.uniform(-0.20, 0.30)
        actual_amt = round(budget_amt * (1 + variance), 2)
        # Sometimes split into 1-3 transactions per month
        n_txns = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
        for _ in range(n_txns):
            txn_amt = round(actual_amt / n_txns * random.uniform(0.8, 1.2), 2)
            day = random.randint(1, 28)
            txn_date = month[:8] + f"{day:02d}"
            w.writerow([aid, ccid, acc, dept, txn_date, txn_amt, random.choice(vendors)])
            aid += 1

print(f"Generated {len(departments)} departments, {len(accounts)} accounts, {len(cost_centers)} cost centers")
print(f"Generated {len(budget_rows)} budget rows, {aid-1} actual transactions")
print(f"Files written to: {OUT}")
