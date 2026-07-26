"""Step 1b (execution): tumor volume extraction from RTSTRUCT contours.

v2 — rewritten for RTSTRUCT (the TCIA Wilms collections contain RTSTRUCT annotation
objects, not DICOM SEG pixel data; see data/clinical-availability.md). v1 parsed
SEG pixel arrays and does not apply to this dataset.

Volume per ROI (protocol, locked 2026-07-26):

    slice area  = 1/2 |sum(p_i x p_{i+1})|   (Newell's method, closed-planar contours)
    volume (mL) = sum(slice areas) x median inter-slice spacing / 1000

Usage:

    python volumes.py                       # reads ../data/rtstruct, writes ../data/volumes.csv
    python volumes.py --limit 20            # smoke test on first N files

Joins each series to data/cohort_series.csv (from download.py) for timepoint/label.
Extracts age/sex from RTSTRUCT headers, source modality from the referenced SOP class.
Every number in Results must regenerate from this script (spec R4).
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pydicom

DATA = Path(__file__).resolve().parent.parent / "data"
SOP_CLASS = {
    "1.2.840.10008.5.1.4.1.1.2": "CT",
    "1.2.840.10008.5.1.4.1.1.4": "MR",
}


def parse_age(s):
    """DICOM AS VR, e.g. '002Y' -> 2.0, '006M' -> 0.5. None if absent/unparseable."""
    m = re.fullmatch(r"(\d+)([YMWD])", (s or "").strip())
    if not m:
        return None
    n = float(m.group(1))
    return {"Y": n, "M": n / 12, "W": n / 52, "D": n / 365}[m.group(2)]


def laterality(name):
    u = name.upper()
    if re.search(r"\b(RT|RIGHT)\b", u):
        return "right"
    if re.search(r"\b(LT|LEFT)\b", u):
        return "left"
    return "unknown"


def source_class(ds):
    """Modality of the imaging this RTSTRUCT references ('CT'/'MR'/other UID/None)."""
    for ref in ds.get("ReferencedFrameOfReferenceSequence", []):
        for rs in ref.get("RTReferencedStudySequence", []):
            for rser in rs.get("RTReferencedSeriesSequence", []):
                imgs = rser.get("ContourImageSequence", [])
                if imgs:
                    uid = str(imgs[0].ReferencedSOPClassUID)
                    return SOP_CLASS.get(uid, uid)
    return None


def roi_volume_ml(contour_seq):
    """(volume_mL, n_slices, flag) for one ROIContourSequence item. None volume if unusable."""
    areas, positions, normals = [], [], []
    for c in contour_seq:
        if getattr(c, "ContourGeometricType", "") != "CLOSED_PLANAR":
            continue
        pts = np.asarray(c.ContourData, dtype=float).reshape(-1, 3)
        if len(pts) < 3:
            continue
        nvec = np.cross(pts, np.roll(pts, -1, axis=0)).sum(axis=0)  # Newell
        norm = np.linalg.norm(nvec)
        if norm == 0:
            continue
        areas.append(norm / 2.0)
        normals.append(nvec / norm)
        positions.append(pts.mean(axis=0))
    if not areas:
        return None, 0, "no_closed_planar_contours"
    if len(areas) == 1:
        return None, 1, "single_slice"

    # vertex winding is arbitrary per slice; align normal signs before summing,
    # otherwise opposing windings cancel and the axis becomes degenerate
    ref = normals[0]
    aligned = [n if float(np.dot(n, ref)) >= 0 else -n for n in normals]
    axis = np.sum(aligned, axis=0)
    axis_norm = np.linalg.norm(axis)
    if axis_norm == 0:
        return None, len(areas), "degenerate_axis"
    axis /= axis_norm
    pos = [float(np.dot(p, axis)) for p in positions]
    order = np.argsort(pos)
    areas = [areas[i] for i in order]
    pos = [pos[i] for i in order]
    spacing = float(np.median(np.diff(pos)))
    if spacing <= 0:
        return None, len(areas), "nonpositive_spacing"
    vol = float(sum(areas) * spacing / 1000.0)  # mm^3 -> mL
    if not np.isfinite(vol):
        return None, len(areas), "non_finite_volume"
    return vol, len(areas), ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    rts_dir = DATA / "rtstruct"
    if not rts_dir.exists():
        raise SystemExit("No data/rtstruct — run download.py first")

    meta = {}
    with (DATA / "cohort_series.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            meta[r["series_uid"]] = r

    files = sorted(rts_dir.glob("*.dcm"))
    if args.limit:
        files = files[: args.limit]

    rows, qc = [], Counter()
    for i, path in enumerate(files, 1):
        try:
            ds = pydicom.dcmread(str(path), force=True)
        except Exception as e:
            qc["unreadable_file"] += 1
            print(f"QC WARNING: {path.name}: {e}", file=sys.stderr)
            continue

        suid = str(ds.SeriesInstanceUID)
        m = meta.get(suid)
        if m is None:
            qc["series_not_in_cohort_manifest"] += 1
            continue
        roi_names = {int(r.ROINumber): str(r.ROIName) for r in ds.get("StructureSetROISequence", [])}
        # annotation tool's own per-ROI volume (DICOM 3006,002C, cm^3 = mL) for cross-validation
        roi_tool_vol = {}
        for r in ds.get("StructureSetROISequence", []):
            v = getattr(r, "ROIVolume", None)
            if v is not None:
                roi_tool_vol[int(r.ROINumber)] = float(v)
        src = source_class(ds)
        age = parse_age(getattr(ds, "PatientAge", ""))

        for c in ds.get("ROIContourSequence", []):
            name = roi_names.get(int(c.ReferencedROINumber), f"ROI-{c.ReferencedROINumber}")
            vol, nslices, flag = roi_volume_ml(c.get("ContourSequence", []))
            flags = [f for f in (flag,
                                 "non_ct_source" if src != "CT" else "",
                                 "missing_age" if age is None else "") if f]
            for f in flags:
                qc[f] += 1
            tool_vol = roi_tool_vol.get(int(c.ReferencedROINumber))
            rows.append({
                "collection": m["collection"],
                "patient_id": m["patient_id"],
                "series_uid": suid,
                "timepoint": m["timepoint"],
                "roi_name": name,
                "laterality": laterality(name),
                "source_class": src or "unknown",
                "n_slices": nslices,
                "volume_ml": round(vol, 2) if vol is not None else "",
                "dicom_roi_volume_ml": round(tool_vol, 2) if tool_vol is not None else "",
                "age_years": age if age is not None else "",
                "sex": getattr(ds, "PatientSex", "") or "",
                "qc_flags": ";".join(flags),
            })
        if i % 100 == 0:
            print(f"  parsed {i}/{len(files)}")

    out = DATA / "volumes.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["empty"])
        w.writeheader()
        w.writerows(rows)

    # ---- QC summary + flow-diagram counts ----
    usable = [r for r in rows if r["volume_ml"] != "" and r["source_class"] == "CT"]
    subj = {r["patient_id"] for r in rows}
    subj_usable = {r["patient_id"] for r in usable}
    tp_by_subj = defaultdict(set)
    for r in usable:
        tp_by_subj[r["patient_id"]].add(r["timepoint"])
    paired = {p for p, t in tp_by_subj.items()
              if any("Pre" in t for t in t) and any("Post" in t for t in t)}
    vols = sorted(float(r["volume_ml"]) for r in usable)

    lines = [
        "# QC summary — RTSTRUCT volume extraction",
        "",
        f"- RTSTRUCT files parsed: {len(files)}",
        f"- ROI volume rows: {len(rows)} (subjects: {len(subj)})",
        f"- Usable rows (volume computable, CT-referenced): {len(usable)} (subjects: {len(subj_usable)})",
        f"- **Paired cohort (usable Pre-dose + Post-chemo, CT): {len(paired)} subjects**",
        f"- QC flags: {dict(qc) or 'none'}",
    ]
    if vols:
        lines.append(f"- Volume (mL): median {vols[len(vols)//2]:.1f}, "
                     f"min {vols[0]:.1f}, p95 {vols[int(len(vols)*0.95)]:.1f}, max {vols[-1]:.1f}")
    summary = "\n".join(lines)
    print("\n" + summary)
    (DATA / "qc-summary.md").write_text(summary + "\n", encoding="utf-8")
    print(f"\nWrote {out} ({len(rows)} rows) and data/qc-summary.md")
    print("Next: analysis.py — pair timepoints per subject, % change, Wilcoxon, waterfall plot")


if __name__ == "__main__":
    main()
