"""Data preprocessing and feature engineering for electricity theft detection."""

from typing import Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FEATURE_COLUMNS = [
    "monthly_consumption",
    "previous_month_consumption",
    "billing_amount",
    "area_average_consumption",
    "meter_reading_difference",
    "consumption_change",
    "usage_vs_area_average",
    "peak_load_kw",
    "power_factor",
    "sanctioned_load_kw",
    "outstanding_balance",
]

CATEGORICAL_COLUMNS = ["region", "connection_type", "meter_type", "payment_status"]


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = FEATURE_COLUMNS + CATEGORICAL_COLUMNS + ["label"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing columns: {missing}")
    return df


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), FEATURE_COLUMNS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
        ]
    )


def split_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    x = df[FEATURE_COLUMNS + CATEGORICAL_COLUMNS]
    y = df["label"].map({"Normal": 0, "Theft": 1})
    return x, y


def record_to_feature_row(record: dict) -> dict:
    consumption_change = record["monthly_consumption"] - record["previous_month_consumption"]
    usage_vs_area = record["monthly_consumption"] - record["area_average_consumption"]
    return {
        **record,
        "consumption_change": consumption_change,
        "usage_vs_area_average": usage_vs_area,
    }
