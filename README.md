# Protocol-Defined Volumetric Response Profiles in Wilms Tumor

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21608440.svg)](https://doi.org/10.5281/zenodo.21608440)


**Reproducibility package** for the manuscript:

> Velasco R, Martinez M. *Protocol-Defined Volumetric Response Profiles in Wilms Tumor:
> A Reproducible Analysis of Public Three-Dimensional Segmentations From COG Trials
> AREN0532, AREN0533, and AREN0534.* (submitted)

Every number in the manuscript regenerates from the public data and the code in this
repository. The headline result: median Wilms tumor volume reduction at the first
post-chemotherapy assessment was **−86.0%** (AREN0532, delayed-nephrectomy subset, n=24),
**−79.9%** (AREN0533, stage III–IV, n=83), and **−71.7%** (AREN0534, bilateral, n=152),
with 240 of 259 subjects showing a decrease.

## Data sources (all public)

- **The Cancer Imaging Archive (TCIA):** collections AREN0532, AREN0533, AREN0534 —
  radiotherapy structure sets (RTSTRUCT) with expert 3D tumor contours and trial
  timepoints. Source images are not distributed; analysis is contour-based.
- Annotation metadata reports (committed here under `data/Metadata_Report_*.csv`).
- References: every citation resolved against live PubMed (`draft/references.json`).

## Reproduce

```bash
pip install -r code/requirements.txt

cd code
python download.py      # builds paired cohort, downloads RTSTRUCT series (TCIA, resumable)
python volumes.py       # contour volumetry -> ../data/volumes.csv + qc-summary.md
python analysis.py      # locked analysis -> ../data/results.json + ../draft/figures/
python render_draft.py  # injects every statistic from results.json into ../draft/manuscript.md
```

`download.py` requires network access to TCIA (`services.cancerimagingarchive.net`).
Everything after it is offline. Re-running the full chain reproduces
`draft/manuscript.md` byte-for-byte.

## Layout

```
code/        download, extraction, analysis, render pipeline (Python)
data/        annotation metadata, cohort manifest, derived volumes, results.json, QC
draft/       manuscript.md (rendered), references.json, figures, review report
protocol.md  locked analysis plan
submission/  cover letter
```

## Method notes

- Volume per ROI: Newell polygon area × median inter-slice spacing (RTSTRUCT contours),
  cross-validated against the annotation tool's own DICOM ROI Volume (3006,002C):
  Spearman ρ = 0.998 across 1,141 lesions, no directional bias (signed difference
  +0.8% pre-chemotherapy, +0.4% post-chemotherapy).
- Trials are not time-aligned (de-identified date shifting), so per-trial profiles are
  primary and the pooled estimate is explicitly secondary.

## License / citation

Code: MIT (see LICENSE). Derived data remain subject to TCIA terms of use — cite the
TCIA collections per their requirements (see `draft/manuscript.md` references 1–9).

**Reusing this work:** this package is our published research, shared so others can
verify and build on it. You are welcome to use the code, adapt the pipeline, and run
your own analyses — that's the point of posting it. All we ask is scholarly courtesy:
if you use it (or the derived data, or the cohort definitions) in your own work, cite
the manuscript and this repository rather than republishing them as your own. The
citation is in CITATION.cff (and on the Zenodo archived release).
