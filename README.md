# Volumetric response of Wilms tumor to neoadjuvant chemotherapy

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21608439.svg)](https://doi.org/10.5281/zenodo.21608439)

Reproducibility package for an analysis of tumor volume change on radiologist-reviewed 3D
segmentations publicly released with Children's Oncology Group trials **AREN0532, AREN0533 and
AREN0534** on The Cancer Imaging Archive.

**Every number in the manuscript regenerates from the public data and the code in this
repository.**

## What is here

| Path | Contents |
|---|---|
| `protocol.md` | The analysis plan, locked 2026-07-26 before any data were touched |
| `code/` | The full pipeline: cohort assembly, contour volumetry, analysis, figures |
| `data/` | Derived data — cohort manifest, per-lesion volumes, analysis output |
| `draft/` | Manuscript and figures |

## Method in one paragraph

The three public collections distribute RTSTRUCT annotation objects — closed-planar 3D tumor
contours produced under radiologist review — but not the source images. Tumor volume is therefore
computed directly from the contours: per slice, polygon area by Newell's method, multiplied by
inter-slice spacing, summed across slices and across kidney tumor ROIs for each subject and
timepoint. The primary outcome is percent volume change from the pre-treatment timepoint to the
first post-chemotherapy timepoint. Because the three trials use different chemotherapy schedules
and response intervals, results are reported per trial rather than pooled as a comparison.

## Validation

Computed volumes were cross-validated against the annotation tool's own DICOM ROI Volume field
across 1,141 lesions (Spearman ρ = 0.998). The check is in the pipeline and re-runs with it.

## Reproducing the results

The derived data in `data/` are sufficient to regenerate every statistic and figure. Regenerating
from source additionally requires downloading the RTSTRUCT collections from TCIA; see
`protocol.md` for the collection identifiers and the inclusion rule.

## Data source

The Cancer Imaging Archive, collections AREN0532, AREN0533 and AREN0534 — public, de-identified
imaging annotations from COG trials. Please cite TCIA and the collections as well as this work;
identifiers are in the manuscript's data availability statement.

## Citation

See `CITATION.cff`. Archived on Zenodo — cite the concept DOI **10.5281/zenodo.21608439**,
which always resolves to the most recent archived version.

## Licence

MIT (see `LICENSE`). The underlying TCIA collections carry their own data-use terms.
