#!/usr/bin/env python3
"""Run TRL-5 validation; exit 1 if any pre-specified criterion fails."""

import argparse
import sys

from barekat_cell_therapy.validation.runner import run_all


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="docs/validation")
    args = ap.parse_args()
    report = run_all(args.out_dir)
    for c in report["evaluation"]["criteria"]:
        status = "PASS" if c["pass"] else "FAIL"
        print(
            f"{status}  [{c['scope']}] {c['id']} {c['description']}: "
            f"{c['measured']} (need {c['rule']})"
        )
    ok = report["evaluation"]["all_passed"]
    print("\nTRL-5 criteria:", "ALL MET" if ok else "NOT MET")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
