#!/usr/bin/env python3
"""Evaluate response prediction model."""

import argparse
from pathlib import Path

import pandas as pd

from barekat_cell_therapy.ml.evaluation import evaluate_response_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CAR-T response model")
    parser.add_argument("--input", default="data/raw/synthetic_patients.csv")
    args = parser.parse_args()
    path = Path(args.input)
    if not path.exists():
        raise SystemExit(f"Not found: {path}")
    result = evaluate_response_model(pd.read_csv(path))
    for k, v in result.items():
        if k != "feature_columns":
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
