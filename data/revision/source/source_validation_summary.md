# Current annotation retrieval and validation — complete

Verified on 2026-09-22 against the official TCIA NBIA endpoint.

- Requested and retrieved: **1,143 current RTSTRUCT annotation objects**, 183,225,502 bytes; no failed downloads.
- Complete manifest, receipt log and SHA-256 checks: **1,143/1,143**; no missing files and no hash discrepancies.
- Source-object verification: **1,128 verified; 15 unresolved; zero missing/unreadable objects**. These are all retrieved review objects, not the final analysis denominator.
- Unresolved objects: one anatomical conflict (AREN0533-PARMKA) and 14 intended ROIs containing closed-planar contours with fewer than three points. Final cohort exclusions are determined at subject level by the statistics workflow.
- All mapped objects otherwise agreed with their metadata on raw stored volume, study identifier, date, target tracking and referenced modality/series. This verifies source consistency, not the clinical or image-based validity of every segmentation.
- The PAVMYW omitted numeric ROIName suffix is allowed under an explicit rule approved before revised aggregate outcomes; exact tracked identity and known kidney side agree. All uses are logged.
- The PAURIY metadata identifier duplication is corrected only because the raw DICOM headers establish its canonical identifier; the ambiguous multiple-baseline case is still excluded by the cohort rules.
- An original source CT probe returned HTTP 400 stating the image was not in the public domain. No CT/MR image overlay review was performed. Original clinical surgery, treatment regimen and histology were not obtained.

## Principal files

| File | Purpose |
|---|---|
| current_raw_manifest.csv | Version 2 annotation objects requested and their source metadata |
| verification.csv | Per-object intended ROI verification and reasons |
| verification_summary.json | Verification counts |
| raw_file_provenance.csv | Complete DICOM byte size and SHA-256 receipts |
| source_provenance.json | Metadata sources, file hashes, scripts, status and source CT limitation |
| retrieval_log.jsonl | Complete cache-confirmed receipt log |
| retrieval_initial_observed_log.jsonl | Preserved partial log visible during first long-running retrieval |
| first_pass_retrieval_summary.json | First pass reported 1,143 successful downloads |
| retrieval_log_note.json | Explanation of complete cached receipt regeneration without redownload |
| source_CT_probe.json | Direct evidence of source CT access restriction |
| phase_probe_retrieval.json | Current raw probes for old postoperative/recurrence labels |
| clinical_eligibility_and_adjudication.md | Conservative scope, rules and case decisions |

All raw DICOM files remain outside the repository in `revision_work/raw`. Two extra DICOMs are phase probes; they are outside the 1,143-object validation manifest. The additional ZIP is the initial raw-access probe.

## Reproduction

Dependencies: Python 3.12 and pydicom 3.0.2 for source verification. The retriever uses only the Python standard library. Use the exact version 2 CSVs listed in `source_provenance.json`, preserving their file bytes and encoding.

```bash
python retrieve_current_annotations.py --metadata-dir /path/to/metadata --raw-dir /path/to/raw --output-dir /path/to/source
python verify_current_annotations.py --manifest /path/to/source/current_raw_manifest.csv --raw-dir /path/to/raw --output-dir /path/to/source --final
```

The primary endpoint is the intended tracked ROI's archive-reported DICOM volume. Do not substitute a different ROI or a contour-derived value when identity is unresolved. Independent contour geometry checks are a separate validation/sensitivity exercise managed by the analysis workflow.
