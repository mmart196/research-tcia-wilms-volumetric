"""Compare verified intended-ROI archive volumes with conservative contour slabs.

This diagnostic does not change the primary archive-reported volume endpoint.
It requires the source verifier's CSV and independently downloaded RTSTRUCTs.
Neither correlated values nor close agreement validate clinical segmentation.
"""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pydicom
from scipy.stats import spearmanr

from volumes import roi_volume_ml


def validate(row, raw_dir):
    result = {name: row.get(name, "") for name in (
        "series_uid", "metadata_tracking_uid", "canonical_patient_id", "raw_timepoint",
        "raw_study_uid", "raw_study_date", "raw_source_modalities", "raw_roi_number",
        "raw_roi_name", "raw_tracking_id", "raw_roi_volume_ml")}
    result.update(source_sha256="", contour_volume_ml="", n_unique_planes="",
                  n_contours="", qc_flag="", signed_difference_ml="",
                  signed_difference_pct="", absolute_difference_pct="")
    try:
        uid = row["series_uid"]
        if not uid or any(c not in "0123456789." for c in uid):
            raise ValueError("invalid SeriesInstanceUID")
        raw = (raw_dir / f"{uid}.dcm").read_bytes()
        result["source_sha256"] = hashlib.sha256(raw).hexdigest()
        dataset = pydicom.dcmread(io.BytesIO(raw))
        if str(dataset.get("SeriesInstanceUID", "")) != uid:
            result["qc_flag"] = "series_identity_changed"
            return result
        descriptors = [roi for roi in dataset.get("StructureSetROISequence", [])
                       if int(roi.ROINumber) == int(row["raw_roi_number"])]
        if (len(descriptors) != 1 or
                str(descriptors[0].get("TrackingUID", "")) != row["metadata_tracking_uid"]):
            result["qc_flag"] = "intended_roi_identity_changed"
            return result
        archive = float(row["raw_roi_volume_ml"])
        if not np.isclose(float(descriptors[0].get("ROIVolume", np.nan)), archive,
                          rtol=1e-9, atol=1e-6):
            result["qc_flag"] = "archive_comparator_changed"
            return result
        rois = [roi for roi in dataset.get("ROIContourSequence", [])
                if int(roi.ReferencedROINumber) == int(row["raw_roi_number"])]
        if len(rois) != 1:
            result["qc_flag"] = "intended_roi_contours_not_unique"
            return result
        contours = rois[0].get("ContourSequence", [])
        result["n_contours"] = len(contours)
        volume, planes, flag = roi_volume_ml(contours)
        result.update(n_unique_planes=planes, qc_flag=flag)
        if volume is not None:
            if not np.isfinite(archive) or archive <= 0:
                result["qc_flag"] = "invalid_archive_comparator"
                return result
            result.update(contour_volume_ml=volume, signed_difference_ml=volume - archive,
                          signed_difference_pct=100 * (volume - archive) / archive,
                          absolute_difference_pct=100 * abs(volume - archive) / archive)
    except Exception as exc:
        result["qc_flag"] = f"geometry_read_error:{type(exc).__name__}:{exc}"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verification", required=True, type=Path)
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    with args.verification.open(newline="", encoding="utf-8") as handle:
        verified = [r for r in csv.DictReader(handle) if r["status"] == "verified"]
    if not verified:
        raise SystemExit("No source-verified rows; geometry validation cannot run.")
    keys = [(r["series_uid"], r["metadata_tracking_uid"]) for r in verified]
    if len(keys) != len(set(keys)):
        raise SystemExit("Duplicate intended-ROI identity in verification input.")
    results = [validate(row, args.raw_dir) for row in verified]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "geometry_validation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    usable = [r for r in results if not r["qc_flag"] and r["contour_volume_ml"] != ""]
    summary = {
        "purpose": "Supporting arithmetic sensitivity; no replacement of archive-reported endpoints.",
        "denominator": "All source-verified intended ROIs supplied to this diagnostic; final-cohort subset is a separate join.",
        "input_verified_rows": len(verified), "usable_geometry_rows": len(usable),
        "eligible_roi_n": len(verified), "computed_roi_n": len(usable),
        "qc_flag_counts": dict(Counter(r["qc_flag"] or "usable" for r in results)),
        "unique_patients": len({r["canonical_patient_id"] for r in results}),
        "greater_than_20_percent_rows": [
            {k: r[k] for k in ("series_uid", "metadata_tracking_uid", "canonical_patient_id",
                               "raw_timepoint", "raw_roi_volume_ml", "contour_volume_ml",
                               "absolute_difference_pct")}
            for r in usable if r["absolute_difference_pct"] > 20],
    }
    if usable:
        signed = np.array([r["signed_difference_pct"] for r in usable])
        summary.update(
            median_signed_difference_pct=float(np.median(signed)),
            median_absolute_difference_pct=float(np.median(np.abs(signed))),
            median_signed_relative_error_pct=float(np.median(signed)),
            median_absolute_relative_error_pct=float(np.median(np.abs(signed))),
            signed_difference_percentiles_2_5_97_5=np.percentile(signed, [2.5, 97.5]).tolist(),
            n_gt_10pct=int(np.sum(np.abs(signed) > 10)),
            n_greater_than_20_percent=int(np.sum(np.abs(signed) > 20)),
        )
        if len(usable) > 1:
            rho = spearmanr([float(r["raw_roi_volume_ml"]) for r in usable],
                            [r["contour_volume_ml"] for r in usable]).statistic
            summary["spearman_rho"] = float(rho) if np.isfinite(rho) else None
    (args.output_dir / "geometry_validation_summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "greater_than_20_percent_rows"}, indent=2))


if __name__ == "__main__":
    main()
