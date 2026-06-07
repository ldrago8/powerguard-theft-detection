"""Generate large-scale synthetic electricity consumer dataset for theft detection."""

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

RANDOM_SEED = 42
NUM_RECORDS = 15000

REGIONS = {
    "Islamabad": {"cities": ["Islamabad", "Rawalpindi", "Murree"], "company": "IESCO", "tariff_base": 22},
    "Karachi": {"cities": ["Karachi", "Malir", "Korangi"], "company": "K-Electric", "tariff_base": 24},
    "Lahore": {"cities": ["Lahore", "Gujranwala", "Sheikhupura"], "company": "LESCO", "tariff_base": 21},
    "Peshawar": {"cities": ["Peshawar", "Mardan", "Abbottabad"], "company": "PESCO", "tariff_base": 20},
    "Quetta": {"cities": ["Quetta", "Zhob", "Sibi"], "company": "QESCO", "tariff_base": 19},
    "Multan": {"cities": ["Multan", "Bahawalpur", "Sahiwal"], "company": "MEPCO", "tariff_base": 21},
    "Hyderabad": {"cities": ["Hyderabad", "Sukkur", "Larkana"], "company": "HESCO", "tariff_base": 20},
    "Faisalabad": {"cities": ["Faisalabad", "Jhang", "Toba Tek Singh"], "company": "FESCO", "tariff_base": 21},
}

FIRST_NAMES = [
    "Ahmed", "Ali", "Hassan", "Usman", "Bilal", "Sara", "Ayesha", "Fatima", "Zainab",
    "Hamza", "Omar", "Imran", "Kamran", "Nadia", "Hina", "Rashid", "Tariq", "Sana",
    "Faisal", "Kashif", "Maria", "Asad", "Danish", "Rabia", "Shahid", "Nabeel", "Amna",
]

LAST_NAMES = [
    "Khan", "Malik", "Sheikh", "Butt", "Chaudhry", "Raza", "Hussain", "Iqbal", "Akram",
    "Siddiqui", "Mirza", "Ansari", "Qureshi", "Hashmi", "Jamal", "Baig", "Shah", "Ali",
]

CONNECTION_TYPES = ["Residential", "Commercial", "Industrial"]
METER_TYPES = ["Smart", "Digital", "Analog"]
PAYMENT_STATUSES = ["Paid", "Paid", "Paid", "Partial", "Overdue"]
ACCOUNT_STATUSES = ["Active", "Active", "Active", "Suspended", "Under Review"]
TARIFF_CATEGORIES = {
    "Residential": ["Domestic", "Domestic", "Protected"],
    "Commercial": ["Commercial A", "Commercial B"],
    "Industrial": ["Industrial", "Industrial B"],
}


def random_cnic() -> str:
    part1 = random.randint(10000, 99999)
    part2 = random.randint(1000000, 9999999)
    part3 = random.randint(1, 9)
    return f"{part1}-{part2}-{part3}"


def random_phone() -> str:
    prefix = random.choice(["300", "301", "302", "303", "321", "322", "333", "345"])
    return f"+92-{prefix}-{random.randint(1000000, 9999999)}"


def random_date(start_year: int = 2015, end_year: int = 2023) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


def generate_consumption_history(base: float, is_theft: bool) -> list[float]:
    history = []
    current = base
    for _ in range(6):
        if is_theft:
            drift = random.uniform(-15, 8)
            spike = random.uniform(0.35, 0.85) if random.random() < 0.35 else random.uniform(0.9, 1.15)
        else:
            drift = random.uniform(-8, 12)
            spike = random.uniform(0.88, 1.12)
        current = max(25, current * spike + drift)
        history.append(round(current, 2))
    return history


def generate_consumer_record(consumer_id: str, region: str, is_theft: bool) -> dict:
    meta = REGIONS[region]
    city = random.choice(meta["cities"])
    connection_type = random.choices(
        CONNECTION_TYPES, weights=[0.72, 0.20, 0.08], k=1
    )[0]
    tariff = random.choice(TARIFF_CATEGORIES[connection_type])
    area_avg = random.uniform(160, 480)
    if connection_type == "Commercial":
        area_avg *= random.uniform(1.8, 3.2)
    elif connection_type == "Industrial":
        area_avg *= random.uniform(4.0, 9.0)

    base_consumption = area_avg * random.uniform(0.75, 1.15)
    history = generate_consumption_history(base_consumption, is_theft)
    monthly_consumption = history[0]
    previous_month_consumption = history[1]
    noise = random.uniform(-30, 30)

    if is_theft:
        billing_rate = random.uniform(7, 16)
        meter_reading_diff = random.uniform(-95, 40)
        if random.random() < 0.10:
            monthly_consumption = random.uniform(area_avg * 0.65, area_avg * 1.05)
    else:
        billing_rate = meta["tariff_base"] + random.uniform(-2, 4)
        meter_reading_diff = random.uniform(-22, 22)

    billing_amount = max(350, monthly_consumption * billing_rate + random.uniform(-300, 300))
    previous_billing = max(350, previous_month_consumption * billing_rate + random.uniform(-250, 250))
    consumption_change = monthly_consumption - previous_month_consumption
    usage_vs_area_avg = monthly_consumption - area_avg
    sanctioned_load = round(random.uniform(2, 25 if connection_type == "Industrial" else 8), 1)
    peak_load = round(min(sanctioned_load * 1.1, monthly_consumption / 30 * random.uniform(0.8, 1.4)), 2)
    power_factor = round(random.uniform(0.78, 0.99 if not is_theft else 0.94), 2)
    outstanding = 0.0 if random.random() > 0.18 else round(random.uniform(500, 25000), 2)

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    street_num = random.randint(1, 999)
    sector = random.choice(["G-", "F-", "H-", "I-", "D-", "E-"]) + str(random.randint(6, 15))

    return {
        "consumer_id": consumer_id,
        "full_name": f"{first} {last}",
        "cnic": random_cnic(),
        "phone": random_phone(),
        "email": f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@email.com",
        "address": f"House {street_num}, Sector {sector}, {city}",
        "city": city,
        "region": region,
        "distribution_company": meta["company"],
        "meter_number": f"MTR-{random.randint(100000, 999999)}",
        "meter_type": random.choices(METER_TYPES, weights=[0.45, 0.35, 0.20], k=1)[0],
        "connection_type": connection_type,
        "tariff_category": tariff,
        "account_status": "Under Review" if is_theft and random.random() < 0.4 else random.choice(ACCOUNT_STATUSES),
        "registration_date": random_date(),
        "sanctioned_load_kw": sanctioned_load,
        "monthly_consumption": round(monthly_consumption + noise * 0.15, 2),
        "previous_month_consumption": round(previous_month_consumption, 2),
        "consumption_month_3": history[2],
        "consumption_month_4": history[3],
        "consumption_month_5": history[4],
        "consumption_month_6": history[5],
        "billing_amount": round(billing_amount, 2),
        "previous_billing_amount": round(previous_billing, 2),
        "payment_status": "Overdue" if is_theft and random.random() < 0.35 else random.choice(PAYMENT_STATUSES),
        "outstanding_balance": outstanding,
        "area_average_consumption": round(area_avg, 2),
        "meter_reading_difference": round(meter_reading_diff, 2),
        "consumption_change": round(consumption_change, 2),
        "usage_vs_area_average": round(usage_vs_area_avg, 2),
        "peak_load_kw": peak_load,
        "power_factor": power_factor,
        "label": "Theft" if is_theft else "Normal",
    }


def generate_dataset(num_records: int = NUM_RECORDS) -> pd.DataFrame:
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    regions = list(REGIONS.keys())
    records = []
    theft_ratio = 0.21

    for i in range(num_records):
        consumer_id = f"CONS-{10001 + i:05d}"
        region = random.choice(regions)
        is_theft = random.random() < theft_ratio
        records.append(generate_consumer_record(consumer_id, region, is_theft))

    return pd.DataFrame(records)


def main() -> None:
    output_path = Path(__file__).parent / "electricity_consumption.csv"
    df = generate_dataset()
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df):,} consumer records -> {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    print("\nLabel distribution:")
    print(df["label"].value_counts())
    print("\nRegion distribution:")
    print(df["region"].value_counts())


if __name__ == "__main__":
    main()
