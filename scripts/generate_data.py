#!/usr/bin/env python3
"""Generate synthetic cell therapy patient data."""

import argparse
from pathlib import Path

from barekat_cell_therapy.data.synthetic import generate_cell_therapy_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic CAR-T patient data")
    parser.add_argument("--patients", type=int, default=300, help="Number of patients")
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/synthetic_patients.csv",
        help="Output CSV path",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = generate_cell_therapy_data(n_patients=args.patients, seed=args.seed)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} patients to {out}")
    print(f"CAR types:\n{df['CAR_Type'].value_counts().to_string()}")
    print(f"Response rate: {df['Treatment_Response'].mean():.2%}")


if __name__ == "__main__":
    main()
