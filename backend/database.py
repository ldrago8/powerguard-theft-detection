"""SQLite database layer for consumer records and prediction history."""

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "storage" / "consumers.db"
DATASET_PATH = ROOT / "data" / "electricity_consumption.csv"

CONSUMER_COLUMNS = [
    "consumer_id", "full_name", "cnic", "phone", "email", "address", "city", "region",
    "distribution_company", "meter_number", "meter_type", "connection_type",
    "tariff_category", "account_status", "registration_date", "sanctioned_load_kw",
    "monthly_consumption", "previous_month_consumption", "consumption_month_3",
    "consumption_month_4", "consumption_month_5", "consumption_month_6",
    "billing_amount", "previous_billing_amount", "payment_status", "outstanding_balance",
    "area_average_consumption", "meter_reading_difference", "consumption_change",
    "usage_vs_area_average", "peak_load_kw", "power_factor", "label",
]


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consumers (
                consumer_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                cnic TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                city TEXT,
                region TEXT,
                distribution_company TEXT,
                meter_number TEXT,
                meter_type TEXT,
                connection_type TEXT,
                tariff_category TEXT,
                account_status TEXT,
                registration_date TEXT,
                sanctioned_load_kw REAL,
                monthly_consumption REAL,
                previous_month_consumption REAL,
                consumption_month_3 REAL,
                consumption_month_4 REAL,
                consumption_month_5 REAL,
                consumption_month_6 REAL,
                billing_amount REAL,
                previous_billing_amount REAL,
                payment_status TEXT,
                outstanding_balance REAL,
                area_average_consumption REAL,
                meter_reading_difference REAL,
                consumption_change REAL,
                usage_vs_area_average REAL,
                peak_load_kw REAL,
                power_factor REAL,
                label TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_consumers_region ON consumers(region)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_consumers_name ON consumers(full_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_consumers_meter ON consumers(meter_number)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_consumers_label ON consumers(label)")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consumer_id TEXT NOT NULL,
                region TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_level TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def import_csv_if_needed(force: bool = False) -> int:
    if not DATASET_PATH.exists():
        return 0

    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM consumers").fetchone()[0]
        csv_mtime = DATASET_PATH.stat().st_mtime
        db_mtime = DB_PATH.stat().st_mtime if DB_PATH.exists() else 0

        if count > 0 and not force and csv_mtime <= db_mtime:
            return count

        df = pd.read_csv(DATASET_PATH)
        conn.execute("DELETE FROM consumers")
        df[CONSUMER_COLUMNS].to_sql("consumers", conn, if_exists="append", index=False)
        return len(df)


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def get_consumer_by_id(consumer_id: str) -> dict[str, Any] | None:
    normalized = consumer_id.strip().upper()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM consumers WHERE UPPER(consumer_id) = ?",
            (normalized,),
        ).fetchone()
    return row_to_dict(row) if row else None


def search_consumers(
    query: str = "",
    region: str | None = None,
    label: str | None = None,
    connection_type: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict[str, Any]:
    conditions = []
    params: list[Any] = []

    if query:
        conditions.append(
            "(consumer_id LIKE ? OR full_name LIKE ? OR meter_number LIKE ? OR cnic LIKE ? OR phone LIKE ?)"
        )
        term = f"%{query.strip()}%"
        params.extend([term, term, term, term, term])

    if region:
        conditions.append("region = ?")
        params.append(region)

    if label:
        conditions.append("label = ?")
        params.append(label)

    if connection_type:
        conditions.append("connection_type = ?")
        params.append(connection_type)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    offset = (page - 1) * page_size

    with get_connection() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM consumers {where}", params
        ).fetchone()[0]
        rows = conn.execute(
            f"""
            SELECT consumer_id, full_name, region, city, connection_type,
                   monthly_consumption, billing_amount, payment_status, label, account_status
            FROM consumers {where}
            ORDER BY consumer_id
            LIMIT ? OFFSET ?
            """,
            [*params, page_size, offset],
        ).fetchall()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "results": [row_to_dict(r) for r in rows],
    }


def get_analytics() -> dict[str, Any]:
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM consumers").fetchone()[0]
        theft = conn.execute("SELECT COUNT(*) FROM consumers WHERE label = 'Theft'").fetchone()[0]
        normal = total - theft

        by_region = conn.execute(
            """
            SELECT region, COUNT(*) as count,
                   SUM(CASE WHEN label = 'Theft' THEN 1 ELSE 0 END) as theft_count
            FROM consumers GROUP BY region ORDER BY count DESC
            """
        ).fetchall()

        by_connection = conn.execute(
            """
            SELECT connection_type, COUNT(*) as count,
                   ROUND(AVG(monthly_consumption), 2) as avg_consumption
            FROM consumers GROUP BY connection_type
            """
        ).fetchall()

        by_company = conn.execute(
            """
            SELECT distribution_company, COUNT(*) as count
            FROM consumers GROUP BY distribution_company ORDER BY count DESC
            """
        ).fetchall()

        payment_breakdown = conn.execute(
            """
            SELECT payment_status, COUNT(*) as count FROM consumers GROUP BY payment_status
            """
        ).fetchall()

        avg_consumption = conn.execute(
            "SELECT ROUND(AVG(monthly_consumption), 2) FROM consumers"
        ).fetchone()[0]

        avg_billing = conn.execute(
            "SELECT ROUND(AVG(billing_amount), 2) FROM consumers"
        ).fetchone()[0]

        overdue = conn.execute(
            "SELECT COUNT(*) FROM consumers WHERE payment_status IN ('Overdue', 'Partial')"
        ).fetchone()[0]

    return {
        "total_consumers": total,
        "theft_cases": theft,
        "normal_cases": normal,
        "theft_percentage": round(theft / total * 100, 2) if total else 0,
        "avg_monthly_consumption": avg_consumption,
        "avg_billing_amount": avg_billing,
        "overdue_accounts": overdue,
        "by_region": [row_to_dict(r) for r in by_region],
        "by_connection_type": [row_to_dict(r) for r in by_connection],
        "by_distribution_company": [row_to_dict(r) for r in by_company],
        "payment_breakdown": [row_to_dict(r) for r in payment_breakdown],
    }


def save_prediction(
    consumer_id: str,
    region: str,
    prediction: str,
    confidence: float,
    risk_level: str,
    created_at: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO predictions (consumer_id, region, prediction, confidence, risk_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (consumer_id, region, prediction, confidence, risk_level, created_at),
        )


def get_prediction_history(limit: int = 50) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [row_to_dict(r) for r in rows]


def autocomplete_search(
    query: str,
    search_type: str = "all",
    limit: int = 12,
) -> list[dict[str, Any]]:
    q = query.strip()
    if len(q) < 1:
        return []

    conditions_map = {
        "id": ("consumer_id LIKE ?", [f"%{q.upper()}%"]),
        "name": ("full_name LIKE ?", [f"%{q}%"]),
        "cnic": ("cnic LIKE ?", [f"%{q}%"]),
        "meter": ("meter_number LIKE ?", [f"%{q.upper()}%"]),
        "phone": ("phone LIKE ?", [f"%{q}%"]),
    }

    if search_type in conditions_map:
        where, params = conditions_map[search_type]
    else:
        where = "(consumer_id LIKE ? OR full_name LIKE ? OR cnic LIKE ? OR meter_number LIKE ? OR phone LIKE ?)"
        term = f"%{q}%"
        id_term = f"%{q.upper()}%"
        params = [id_term, term, term, id_term, term]

    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT consumer_id, full_name, region, city, meter_number, cnic,
                   connection_type, label, monthly_consumption, billing_amount
            FROM consumers
            WHERE {where}
            ORDER BY
                CASE WHEN UPPER(consumer_id) = ? THEN 0
                     WHEN UPPER(consumer_id) LIKE ? THEN 1
                     ELSE 2 END,
                consumer_id
            LIMIT ?
            """,
            [*params, q.upper(), f"{q.upper()}%", limit],
        ).fetchall()

    return [row_to_dict(r) for r in rows]
