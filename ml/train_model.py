"""Train and evaluate electricity theft detection models."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from ml.preprocess import build_preprocessor, load_dataset, split_features_target

MODELS = {
    "decision_tree": DecisionTreeClassifier(
        max_depth=6,
        min_samples_leaf=25,
        random_state=42,
    ),
    "random_forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
    ),
    "logistic_regression": LogisticRegression(max_iter=1000, random_state=42),
}


def train_and_evaluate(
    dataset_path: str,
    model_name: str = "decision_tree",
) -> dict:
    df = load_dataset(dataset_path)
    x, y = split_features_target(df)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", MODELS[model_name]),
        ]
    )
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    metrics = {
        "model": model_name,
        "accuracy": round(accuracy_score(y_test, predictions) * 100, 2),
        "precision": round(precision_score(y_test, predictions, zero_division=0) * 100, 2),
        "recall": round(recall_score(y_test, predictions, zero_division=0) * 100, 2),
        "f1_score": round(f1_score(y_test, predictions, zero_division=0) * 100, 2),
        "train_samples": len(x_train),
        "test_samples": len(x_test),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "classification_report": classification_report(
            y_test, predictions, target_names=["Normal", "Theft"], output_dict=True
        ),
    }
    return pipeline, metrics


def save_artifacts(pipeline, metrics: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_dir / "theft_detection_model.pkl")
    with open(output_dir / "model_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def main() -> None:
    root = ROOT
    dataset_path = root / "data" / "electricity_consumption.csv"
    output_dir = root / "ml" / "artifacts"

    if not dataset_path.exists():
        from data.generate_dataset import generate_dataset

        generate_dataset().to_csv(dataset_path, index=False)

    all_metrics = {}
    best_pipeline = None
    best_f1 = -1.0

    for model_name in MODELS:
        pipeline, metrics = train_and_evaluate(str(dataset_path), model_name)
        all_metrics[model_name] = metrics
        if metrics["f1_score"] > best_f1:
            best_f1 = metrics["f1_score"]
            best_pipeline = pipeline
            best_metrics = metrics

    save_artifacts(best_pipeline, best_metrics, output_dir)

    comparison_path = output_dir / "model_comparison.json"
    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"Best model: {best_metrics['model']}")
    print(json.dumps(best_metrics, indent=2))


if __name__ == "__main__":
    main()
