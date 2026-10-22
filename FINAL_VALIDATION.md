# Computational validation — September 22, 2026

The revised calculations and manuscript were reproduced in a separate project copy using a clean Python 3.12.14 environment installed from `code/requirements-lock.txt`. The environment had no inherited system packages; `pip check` reported no broken requirements.

## Checks completed

- All 17 analytic and regression tests passed. They cover multiple contours on one plane, oblique orientation and winding, explicit XOR holes/islands, conservative geometry exclusions, laterality and conflicting image references, exact intended-ROI selection, and Word reference formatting.
- `analyze_revision.py` rebuilt patient selection, matched-target volumes, intervals, flow tables, exact median confidence intervals, and figures from the committed metadata and source-verification records.
- `geometry_sensitivity.py` rebuilt the comparison using the exact selected primary targets and complete computable patient pairs.
- `render_revision.py` regenerated a byte-identical Markdown manuscript. The regenerated Word document matched the delivered candidate's paragraph text/styles, tables, and embedded images. Newly calculated figure PNGs were also byte-identical to the figures supplied to the manuscript.
- Every scientific result matched: 227 CT pairs, 39 separate MRI pairs, and 57 complete CT pairs in the contour-method sensitivity. The rendered candidate has 20 references, three tables, two figures, and a 1,758-character abstract.
- The immutable active amendment lock was restored beside the amendment. Canonical analysis and sensitivity outputs were then refreshed using the clean environment, preserving every scientific and lock-record value while recording the hashes of the integrated public scripts. `data/results.json` and `data/revision/output/results.json` were synchronized.

The primary reproduction used included derived verification records. Separately, the repaired geometry diagnostic was executed against the downloaded current RTSTRUCTs for all 1,128 source-verified intended ROIs. It did not substitute computed values for the primary stored ROI volumes. The diagnostic records a SHA-256 checksum for every processed raw file.

## Interpretation and remaining limits

The primary endpoint is the archive-reported volume of matched annotated renal targets. The checks establish computational consistency and traceable target selection, not anatomical segmentation accuracy or chemotherapy efficacy. No source CT/MRI voxel images or linked treatment, pathology, surgical timing, or clinical outcomes were reviewed.

Geometric measurements were computable for 432 of 698 selected CT ROI-timepoint observations; only 57 of 227 patients had complete computable pairs. The median absolute relative difference was approximately 4.0%, but 126 computable observations differed by more than 10%. Most unavailable measurements involved polygon topology unsupported by the conservative routine. Such flags do not establish anatomical inaccuracy. The restricted sensitivity subset does not validate all primary patients.

The existing Zenodo v1.0.2 archive is superseded and incomplete for the corrected manuscript. No new archived release or DOI is claimed. A future release should be tested from its downloaded archive, including the template, metadata, verification records, lockfiles, and code.

This record documents computational verification. It does not change journal-submission gate status or record author approval.
