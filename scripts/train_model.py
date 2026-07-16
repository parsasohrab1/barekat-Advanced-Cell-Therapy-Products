#!/usr/bin/env python3
"""Train response prediction model from synthetic data."""

import argparse
from pathlib import Path

import pandas as pd

from barekat_cell_therapy.ml.trainer import train_response_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CAR-T response model")
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/synthetic_patients.csv",
        help="Training CSV path",
    )
    parser.add_argument("--output-dir", type=str, default="data/models")
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        raise SystemExit(f"Input not found: {path}. Run scripts/generate_data.py first.")

    df = pd.read_csv(path)
    metrics = train_response_model(df, output_dir=args.output_dir)
    print("Training complete:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
