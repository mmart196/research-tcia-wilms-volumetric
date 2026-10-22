"""Step 1b (execution): tumor volume extraction from RTSTRUCT contours.

v2 — rewritten for RTSTRUCT (the TCIA Wilms collections contain RTSTRUCT annotation
objects, not DICOM SEG pixel data; see data/clinical-availability.md). v1 parsed
SEG pixel arrays and does not apply to this dataset.

Repaired contour method (2026-09-22; not the original locked implementation):

    slice area  = area of disjoint CLOSED_PLANAR polygons, or CLOSEDPLANAR_XOR
    volume (mL) = sum(unique-plane areas) x uniform inter-plane spacing / 1000

This is a slab approximation, including a half-spacing extension at each end.
It is not an image-based segmentation validation. Ambiguous topology, invalid
polygons, nonparallel planes, and irregular spacing are rejected, not repaired.
The historical committed CSV predates these safeguards; a fresh raw-data run is
required before describing any volumes as recalculated with this implementation.

Usage:

    python code/volumes.py                  # current verified intended-ROI diagnostic
    python code/volumes.py --help           # raw/source/output directory options
    python code/volumes.py --legacy         # historical all-ROI extraction only

Joins each series to data/cohort_series.csv (from download.py) for timepoint/label.
Extracts age/sex from RTSTRUCT headers, source modality from the referenced SOP class.
This optional contour sensitivity pipeline is separate from the primary analysis
of the archive-reported ROI volumes. It does not validate the clinical contours.
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pydicom
from shapely.geometry import Polygon

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
    right = bool(re.search(r"\b(R|RT|RIGHT)\b", u))
    left = bool(re.search(r"\b(L|LT|LEFT)\b", u))
    if right and left:
        return "unknown"  # Conflicting tokens do not establish bilateral anatomy.
    if right:
        return "right"
    if left:
        return "left"
    return "unknown"


def source_class(ds):
    """Inspect every image reference; do not infer a modality from the first one.

    Return CT, MR, mixed (conflicting SOP classes), or unknown. Both the source
    series references and per-contour image references are checked. This is an
    object-level check; a mixed object needs ROI-specific inspection before use.
    """
    uids = set()

    def record(images):
        for image in images:
            uids.add(str(getattr(image, "ReferencedSOPClassUID", "")))

    for ref in ds.get("ReferencedFrameOfReferenceSequence", []):
        for rs in ref.get("RTReferencedStudySequence", []):
            for rser in rs.get("RTReferencedSeriesSequence", []):
                record(rser.get("ContourImageSequence", []))
    for roi in ds.get("ROIContourSequence", []):
        for contour in roi.get("ContourSequence", []):
            record(contour.get("ContourImageSequence", []))
    if len(uids) > 1:
        return "mixed"
    return SOP_CLASS.get(next(iter(uids)), "unknown") if uids else "unknown"


def roi_volume_ml(contour_seq):
    """Return (mL, unique-plane count, QC flag); reject an unsafe ROI in full.

    Coordinates are millimetres. Planarity/plane grouping tolerance is 0.001 mm;
    parallel normals must agree within 1e-6 in absolute dot product. Spacing
    must be uniform within 1% plus 0.001 mm. These are numerical QC tolerances,
    not evidence that all intervening image slices have contours.

    DICOM PS3.3 C.8.8.6 requires an ROI using CLOSEDPLANAR_XOR to use that type
    throughout. XOR implements holes explicitly. For ordinary CLOSED_PLANAR,
    separate disjoint polygons on the same plane are summed; nesting/overlap
    is rejected rather than guessed to represent a hole. A valid simple
    keyhole polygon is accepted; self-touching/invalid keyholes are not repaired.
    https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.8.6.html
    """
    contours = list(contour_seq)
    if not contours:
        return None, 0, "no_closed_planar_contours"
    kinds = {str(getattr(c, "ContourGeometricType", "")) for c in contours}
    if "CLOSEDPLANAR_XOR" in kinds and kinds != {"CLOSEDPLANAR_XOR"}:
        return None, 0, "mixed_xor_contour_types"
    if not kinds <= {"CLOSED_PLANAR", "CLOSEDPLANAR_XOR"}:
        return None, 0, "unsupported_contour_type"

    tolerance = 0.001
    records = []
    for c in contours:
        try:
            pts = np.asarray(c.ContourData, dtype=float).reshape(-1, 3)
        except (AttributeError, TypeError, ValueError):
            return None, 0, "malformed_contour_data"
        if len(pts) < 3 or not np.isfinite(pts).all():
            return None, 0, "invalid_contour_points"
        if hasattr(c, "NumberOfContourPoints"):
            try:
                if int(c.NumberOfContourPoints) != len(pts):
                    return None, 0, "contour_point_count_mismatch"
            except (TypeError, ValueError):
                return None, 0, "contour_point_count_mismatch"
        centre = pts.mean(axis=0)
        centred = pts - centre
        nvec = np.cross(centred, np.roll(centred, -1, axis=0)).sum(axis=0)
        norm = float(np.linalg.norm(nvec))
        if not np.isfinite(norm) or norm <= 1e-12:
            return None, 0, "degenerate_contour"
        normal = nvec / norm
        if np.max(np.abs(centred @ normal)) > tolerance:
            return None, 0, "nonplanar_contour"
        records.append((pts, centre, normal))

    axis = records[0][2]
    if any(abs(float(np.dot(axis, normal))) < 1 - 1e-6 for _, _, normal in records):
        return None, 0, "nonparallel_contour_planes"
    # A shared orthonormal frame avoids orientation- or winding-dependent areas.
    helper = np.eye(3)[int(np.argmin(np.abs(axis)))]
    u = np.cross(axis, helper)
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    origin = records[0][1]
    projected = []
    for pts, centre, _ in records:
        # Also validate against the common axis, not just each contour's normal.
        if np.max(np.abs((pts - centre) @ axis)) > tolerance:
            return None, 0, "nonparallel_contour_planes"
        xy = np.column_stack(((pts - origin) @ u, (pts - origin) @ v))
        polygon = Polygon(xy)
        if not polygon.is_valid or polygon.area <= 1e-12:
            return None, 0, "invalid_polygon"
        projected.append((float(np.dot(centre - origin, axis)), polygon))

    planes = []
    for position, polygon in sorted(projected, key=lambda item: item[0]):
        if planes and abs(position - planes[-1][0]) <= tolerance:
            planes[-1][1].append(polygon)
        else:
            planes.append((position, [polygon]))
    n_slices = len(planes)
    if n_slices < 2:
        return None, n_slices, "single_slice"

    areas = []
    for _, polygons in planes:
        if kinds == {"CLOSEDPLANAR_XOR"}:
            combined = polygons[0]
            for polygon in polygons[1:]:
                combined = combined.symmetric_difference(polygon)
            areas.append(float(combined.area))
        else:
            for i, polygon in enumerate(polygons):
                if any(polygon.intersection(other).area > 1e-9 for other in polygons[:i]):
                    return None, n_slices, "overlapping_or_nested_closed_planar"
            areas.append(float(sum(polygon.area for polygon in polygons)))
    gaps = np.diff([position for position, _ in planes])
    spacing = float(np.median(gaps))
    if not np.allclose(gaps, spacing, rtol=0.01, atol=tolerance):
        return None, n_slices, "irregular_plane_spacing"
    vol = float(sum(areas) * spacing / 1000.0)
    if not np.isfinite(vol) or vol <= 0:
        return None, n_slices, "nonpositive_or_nonfinite_volume"
    return vol, n_slices, ""


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
    if "--legacy" in sys.argv[1:]:
        sys.argv.remove("--legacy")
        main()
    else:
        # The imported geometry functions remain available, but the default CLI
        # must not overwrite historical all-ROI totals as if they were current.
        arguments = sys.argv[1:]
        defaults = {
            "--verification": DATA / "revision" / "source" / "verification.csv",
            "--raw-dir": DATA / "revision" / "raw",
            "--output-dir": DATA / "revision" / "source",
        }
        for flag, value in defaults.items():
            if not any(arg == flag or arg.startswith(flag + "=") for arg in arguments):
                arguments.extend([flag, str(value)])
        sys.argv = [sys.argv[0], *arguments]
        from validate_geometry import main as current_main
        current_main()
