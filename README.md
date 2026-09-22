# Longitudinal volumetry of annotated renal target lesions

Reproducibility package for **Longitudinal Volumetry of Annotated Renal Target Lesions in Three Children's Oncology Group Trial Archives**.

The September 22, 2026 revision analyzes corrected version-2 TCIA annotation releases for AREN0532, AREN0533, and AREN0534. The endpoint is change in **summed archive-reported volumes of the same verified renal target lesions** between Pre-Dose and Post-Chemotherapy #1. It is a descriptive measurement of selected annotations. It is not total renal tumor burden, a validated clinical response category, or an estimate of treatment efficacy.

The original results and methods have been superseded. The dated amendment openly records that earlier aggregate outcomes were already known before these corrections. The original `protocol.md` is retained for provenance; it is not the current analysis plan.

## What is in the package

| Path | Purpose |
|---|---|
| `protocol_amendment_2026-09-22.md` | Revised endpoint, selection rules, sensitivities, uncertainty estimates, and limitations |
| `lock_record.json` | Recorded amendment hash and finalization time, preserved next to the active amendment |
| `data/revision/metadata/` | Current source metadata snapshots and historical snapshots used to flag label conflicts |
| `data/revision/source/` | Source-object manifest, retrieval provenance, checksums, verification decisions, and contour diagnostic results |
| `data/revision/output/` | Patient exclusions, exact selected targets, paired data, summaries, and figures |
| `code/analyze_revision.py` | Patient selection, aggregation, statistical summaries, and figures |
| `code/validate_geometry.py` | Intended-ROI contour recomputation from downloaded RTSTRUCTs |
| `code/geometry_sensitivity.py` | Comparison on the exact primary targets and complete computable patient pairs |
| `code/render_revision.py` | Manuscript generation with numbered references, Word tables, and figures |
| `draft/manuscript_template.md` | Manuscript source; edit this rather than generated manuscript files |
| `draft/citation_library.json` | Verified source records used to generate first-appearance citation numbering |
| `tests/` | Analytic geometry, target-selection, and formatting regression checks |

Raw DICOM objects are obtained separately from TCIA and are not committed. TCIA terms apply to source data. The software license is in `LICENSE`.

## Reproduce the revised results from the included derived records

Use Python 3.12. The exact tested environment was Python 3.12.14 on Linux x86_64. Both direct and transitive dependency versions are pinned. From the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r code/requirements-lock.txt
.venv/bin/python -m unittest discover -s tests -v

.venv/bin/python code/analyze_revision.py \
  --data-dir data/revision/metadata \
  --verification data/revision/source/verification.csv \
  --amendment protocol_amendment_2026-09-22.md \
  --output-dir data/revision/output

.venv/bin/python code/geometry_sensitivity.py \
  --geometry data/revision/source/geometry_validation.csv \
  --output-dir data/revision/output

.venv/bin/python code/render_revision.py \
  --output-dir data/revision/output \
  --template draft/manuscript_template.md \
  --library draft/citation_library.json \
  --docx draft/manuscript.docx
```

The first analysis rebuilds patient eligibility and all primary and timing/MRI summaries. The geometry step joins the exact selected target identities, retains only complete computable patient pairs, and adds sensitivity results. The renderer builds the manuscript from those outputs. Generated timestamps and environment/path records can differ on another run; numerical results should agree when the same source snapshot, verification records, software, and methods are used.

These commands start with the included source-verification and contour diagnostic records. They do not themselves download or independently verify the raw annotation objects.

## Source verification and optional contour recomputation

The source-verification pipeline checks each selected annotation against its downloaded RTSTRUCT: patient/examination identity, date, referenced image series and modality, intended TrackingUID and ROI number/name, contour presence, and stored ROI Volume. An unrelated ROI in the same object is not added to a renal target. A missing target is not assigned zero volume. Complete matched target sets, unique source examinations, and chronological ordering are required. CT and MRI are analyzed separately.

To repeat raw retrieval, identity verification, and supporting contour recomputation in a separate temporary directory:

```bash
WILMS_RECHECK_DIR="$(mktemp -d)"
.venv/bin/python code/retrieve_annotations.py \
  --metadata-dir data/revision/metadata \
  --raw-dir "$WILMS_RECHECK_DIR/raw" \
  --output-dir "$WILMS_RECHECK_DIR/source"

.venv/bin/python code/verify_annotations.py --final \
  --manifest "$WILMS_RECHECK_DIR/source/current_raw_manifest.csv" \
  --raw-dir "$WILMS_RECHECK_DIR/raw" \
  --output-dir "$WILMS_RECHECK_DIR/source"

.venv/bin/python code/validate_geometry.py \
  --verification "$WILMS_RECHECK_DIR/source/verification.csv" \
  --raw-dir "$WILMS_RECHECK_DIR/raw" \
  --output-dir "$WILMS_RECHECK_DIR/source"
```

Retain that run's download log and checksums. To analyze the rechecked inputs, pass its `verification.csv` to `code/analyze_revision.py` and its `geometry_validation.csv` to `code/geometry_sensitivity.py`. Use a separate output directory to compare against the committed results without replacing their provenance.

The diagnostic produces `geometry_validation.csv` and `geometry_validation_summary.json`. Pass that new CSV to `code/geometry_sensitivity.py` to recalculate the comparison on the exact selected primary targets. The all-object diagnostic summary may include extra phases or subsequently excluded patients; manuscript agreement estimates use the selected-target join, not that broader denominator.

The repaired integrator groups contours by unique physical plane, handles explicit DICOM exclusive-or topology, and rejects ambiguous overlapping ordinary contours, invalid polygons, nonparallel planes, and irregular spacing. It uses a uniform slab approximation with half-spacing extensions at both ends. Single-plane objects have no inferred thickness. Unavailable geometry does not remove an otherwise eligible archive-reported volume from the primary analysis, and geometry values are never substituted for the primary endpoint.

Close agreement between two calculations from the same annotations does not validate the original segmentation boundaries. Source CT/MRI voxel images, independent clinical rereading, and linked treatment/pathology/outcome data were not used in this analysis.

## Version and citation

Use the corrected [revision branch](https://github.com/mmart196/research-tcia-wilms-volumetric/tree/revision/cureus-data-corrections-2026-09-22) and record the commit used. The code availability statement in the revised manuscript identifies this corrected package.

The existing [Zenodo concept DOI](https://doi.org/10.5281/zenodo.21608439) resolves, but its current v1.0.2 archive contains the **superseded analysis** and does not fully render the current manuscript. It is not the archival source of the corrected results. This revision does not claim a new Zenodo release or DOI. A future archive must include the complete source template, data snapshots, verification records, dependency lock, and code, and must be tested from the downloaded release artifact.

Cite TCIA and the specific imaging and annotation dataset versions as well as the analysis. Dataset references are generated from `draft/citation_library.json` into the manuscript reference list.
