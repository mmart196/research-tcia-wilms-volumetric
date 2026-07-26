"""Step 1a (execution): build the paired cohort and download its RTSTRUCT series.

Cohort (protocol, locked 2026-07-26): subjects with >=1 kidney tumor *Segmentation*
annotation at Pre-dose AND at >=1 Post-chemotherapy timepoint, per the annotation
metadata reports (data/Metadata_Report_AREN05*.csv).

Downloads each cohort series as a zip via NBIA getImage and stores the contained
RTSTRUCT as data/rtstruct/<SeriesInstanceUID>.dcm (flat layout, resumable —
existing files are skipped). Also writes data/cohort_series.csv (the manifest
joining series -> patient, timepoint, label, collection).

Run locally (TCIA unreachable from cloud sandboxes):

    python download.py            # full cohort
    python download.py --limit 5  # smoke test
"""
import argparse
import csv
import io
import sys
import time
import zipfile
from collections import defaultdict
from pathlib import Path

import requests

BASE = "https://services.cancerimagingarchive.net/nbia-api/services/v1"
DATA = Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "rtstruct"
TIMEOUT = 120


def label_of(row):
    """Structure label: explicit column (0533/0534) or parsed from SeriesDescription (0532)."""
    if row.get("StructureSetLabel"):
        return row["StructureSetLabel"].strip()
    # "Pre-dose,  RT KIDNEY - 2 - SEED POINT" -> "RT KIDNEY - 2"
    desc = row.get("SeriesDescription", "")
    parts = [p.strip() for p in desc.split(",")]
    lab = parts[-1] if parts else ""
    for suffix in ("- SEED POINT",):
        if lab.upper().endswith(suffix):
            lab = lab[: -len(suffix)].strip()
    return lab


def build_cohort():
    """Return (series_rows, cohort_ids): kidney Segmentation series for paired subjects."""
    series_rows = []
    subj_tp = defaultdict(set)
    for col in ["AREN0532", "AREN0533", "AREN0534"]:
        with (DATA / f"Metadata_Report_{col}.csv").open(newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r["Annotation Type"] != "Segmentation":
                    continue
                lab = label_of(r)
                if "KIDNEY" not in lab.upper():
                    continue
                series_rows.append({
                    "collection": col,
                    "patient_id": r["PatientID"],
                    "series_uid": r["SeriesInstanceUID"],
                    "timepoint": r["ClinicalTrialTimePointID"],
                    "label": lab,
                    "study_description": r.get("StudyDescription", ""),
                })
                subj_tp[r["PatientID"]].add(r["ClinicalTrialTimePointID"])
    cohort = {pid for pid, tps in subj_tp.items()
              if any("Pre" in t for t in tps) and any("Post" in t for t in tps)}
    return [r for r in series_rows if r["patient_id"] in cohort], cohort


def fetch_series(series_uid, dest):
    for attempt in range(3):
        try:
            r = requests.get(f"{BASE}/getImage", params={"SeriesInstanceUID": series_uid},
                             timeout=TIMEOUT)
            r.raise_for_status()
            z = zipfile.ZipFile(io.BytesIO(r.content))
            dcms = [n for n in z.namelist() if n.lower().endswith(".dcm")]
            if len(dcms) != 1:
                return f"unexpected zip contents: {z.namelist()}"
            dest.write_bytes(z.read(dcms[0]))
            return None
        except Exception as e:
            err = str(e)
            time.sleep(2 * (attempt + 1))
    return err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="Only download first N series (smoke test)")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    rows, cohort = build_cohort()
    # dedupe by series uid (metadata can list a series once per annotation row)
    seen, series = set(), []
    for r in rows:
        if r["series_uid"] not in seen:
            seen.add(r["series_uid"])
            series.append(r)

    with (DATA / "cohort_series.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"cohort: {len(cohort)} paired subjects, {len(series)} unique kidney-seg series "
          f"({len(rows)} annotation rows) -> data/cohort_series.csv")

    todo = series[: args.limit] if args.limit else series
    done = failed = skipped = 0
    failures = []
    for i, r in enumerate(todo, 1):
        dest = OUT / f"{r['series_uid']}.dcm"
        if dest.exists():
            skipped += 1
            continue
        err = fetch_series(r["series_uid"], dest)
        if err:
            failed += 1
            failures.append((r["series_uid"], r["patient_id"], err))
            print(f"  FAIL {r['patient_id']} {r['series_uid']}: {err}", file=sys.stderr)
        else:
            done += 1
        if i % 50 == 0:
            print(f"  progress {i}/{len(todo)} (ok={done} skip={skipped} fail={failed})")

    print(f"\nDownloaded {done}, skipped {skipped} existing, failed {failed} (of {len(todo)})")
    if failures:
        with (DATA / "download_failures.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["series_uid", "patient_id", "error"])
            w.writerows(failures)
        print(f"failures logged to data/download_failures.csv")
    print("Next: python volumes.py")


if __name__ == "__main__":
    main()
