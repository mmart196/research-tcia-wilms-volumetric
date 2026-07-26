"""Step 0 (execution): TCIA Wilms tumor collection inventory.

v2 — timepoints keyed on StudyInstanceUID (one per scan session, always present).
v1 keyed on SeriesDate, which NBIA often returns blank -> collapsed every subject
to "0 timepoints". Do not trust v1 output.

Produces data/inventory.csv and prints the inclusion funnel used for the
manuscript's flow diagram:

    subjects with any CT study
      -> subjects with >=2 CT studies (baseline + follow-up)
        -> subjects with >=2 CT studies that also have segmentations

Run locally (the agent sandbox cannot reach TCIA — egress blocked):

    pip install -r requirements.txt
    python inventory.py                      # auto-detects Wilms/AREN collections
    python inventory.py --collection "AREN0533"
"""
import argparse
import csv
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests

BASE = "https://services.cancerimagingarchive.net/nbia-api/services/v1"
OUT_DIR = Path(__file__).resolve().parent.parent / "data"
TIMEOUT = 60
SEG_MODALITIES = {"SEG", "RTSTRUCT"}  # DICOM segmentation objects + radiotherapy contours


def get(service, **params):
    params["format"] = "json"
    for attempt in range(3):
        try:
            r = requests.get(f"{BASE}/{service}", params=params, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"  retry {attempt + 1}/3 {service}: {e}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise SystemExit(f"TCIA unreachable after 3 attempts: {service}")


def find_wilms_collections():
    cols = [c["Collection"] for c in get("getCollectionValues")]
    hits = [c for c in cols if "wilms" in c.lower() or "aren" in c.lower()]
    if not hits:
        raise SystemExit(f"No Wilms/AREN collections found on TCIA. Available: {cols}")
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collection", help="Exact TCIA collection name (default: auto-detect Wilms/AREN)")
    args = ap.parse_args()
    collections = [args.collection] if args.collection else find_wilms_collections()
    OUT_DIR.mkdir(exist_ok=True)

    rows = []
    for col in collections:
        patients = get("getPatient", Collection=col)
        series = get("getSeries", Collection=col)
        print(f"{col}: {len(patients)} subjects, {len(series)} series")

        # patient -> study (StudyInstanceUID) -> set of modalities in that study
        studies = defaultdict(lambda: defaultdict(set))
        blank_dates = 0
        for s in series:
            pid = s.get("PatientID")
            uid = s.get("StudyInstanceUID")
            mod = s.get("Modality", "")
            if not s.get("SeriesDate"):
                blank_dates += 1
            if pid and uid:
                studies[pid][uid].add(mod)

        if blank_dates:
            print(f"  QC note: {blank_dates}/{len(series)} series have blank SeriesDate (why v1 failed)")

        for pid, studs in studies.items():
            ct_studies = {u for u, m in studs.items() if "CT" in m}
            mr_studies = {u for u, m in studs.items() if "MR" in m}
            seg_studies = {u for u, m in studs.items() if m & SEG_MODALITIES}
            ct_seg_studies = ct_studies & seg_studies
            rows.append({
                "collection": col,
                "patient_id": pid,
                "n_studies": len(studs),
                "n_ct_studies": len(ct_studies),
                "n_mr_studies": len(mr_studies),
                "n_seg_studies": len(seg_studies),
                "n_ct_seg_studies": len(ct_seg_studies),
                "paired_ct": len(ct_studies) >= 2,
                "paired_ct_seg": len(ct_seg_studies) >= 2,
            })

    # Inclusion funnel (protocol: paired pre/post-neoadjuvant CT with segmentations)
    n0 = sum(r["n_ct_studies"] >= 1 for r in rows)
    n1 = sum(r["paired_ct"] for r in rows)
    n2 = sum(r["paired_ct_seg"] for r in rows)
    n3 = sum(r["n_seg_studies"] >= 1 for r in rows)
    print("\nINCLUSION FUNNEL (keyed on StudyInstanceUID)")
    print(f"  subjects with >=1 CT study:              {n0}")
    print(f"  subjects with >=2 CT studies (paired):   {n1}   <- longitudinal cohort candidate")
    print(f"  ...of which SEG on >=2 CT studies:       {n2}   <- analysis cohort (paired volumetrics)")
    print(f"  subjects with >=1 segmented study:       {n3}   <- fallback cohort (single-timepoint)")

    out = OUT_DIR / "inventory.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["collection"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {out} ({len(rows)} subjects)")

    if n2 > 0:
        print("Next: download the paired-cohort series (NBIA Data Retriever), then run volumes.py")
    else:
        print("Next: no paired cohort -> consider single-timepoint pivot before downloading anything")


if __name__ == "__main__":
    main()
