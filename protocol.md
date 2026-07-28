# Protocol — Volumetric Response of Wilms Tumor to Neoadjuvant Chemotherapy (TCIA AREN0532/0533/0534)

**Study type:** Original research, retrospective analysis of public imaging annotations.
**Analysis plan locked:** 2026-07-26, before any data were touched (see below).

---

## Question

How does Wilms tumor volume respond to neoadjuvant chemotherapy in children, measured on
radiologist-reviewed 3D segmentations from COG trials AREN0532/0533/0534?

## Rationale

- Tumor response in Wilms tumor is usually reported categorically or by unidimensional
  measurement. Volumetric response has not been quantified at cohort scale on these trials.
- The three TCIA collections carry **radiologist-reviewed 3D tumor segmentations**, so volumes
  can be derived from expert contours rather than from new, unvalidated segmentation.
- The collections are public and the pipeline is fully scripted, so every reported number is
  independently regenerable — the contribution is a reproducible benchmark as much as a result.

## Scope decision (2026-07-26)

The analysis is restricted to **paired RTSTRUCT contour volumetry**. Trial stage, histology and
clinical outcomes are out of scope: those covariates are not distributed with the public
collections and obtaining them would require a separate data application. This bounds the study
to what the public data can actually support.

## Data source (verified 2026-07-26 — see `data/clinical-availability.md`)

The three public NBIA collections contain **RTSTRUCT annotation objects only** (9,355 series;
AIM tool exports). Each RTSTRUCT carries closed-planar 3D tumor contours referencing a source
imaging study. Source images are **not publicly downloadable** — analysis is contour-based
volumetry (no radiomics, no image-overlay figures; 3D contour renders are possible).

- Annotation metadata (committed: `data/Metadata_Report_AREN05{32,33,34}.csv`) gives per-series
  `ClinicalTrialTimePointID` (Pre-dose, Post-chemotherapy #1–#4, Post-operative, Recurrence),
  annotation type, and structure label.
- Verified by direct inspection: sample RTSTRUCT = 21-slice closed-planar kidney tumor contour
  set referencing CT Image Storage. Source modality is predominantly CT (some MR, esp. AREN0534);
  each RTSTRUCT records its referenced SOP class — enforced at extraction.
- Age and sex are present in RTSTRUCT headers. StudyDate is de-identification-shifted (unusable);
  relative timing comes from `ClinicalTrialTimePointID`.

## Analysis plan (LOCKED 2026-07-26 before touching data)

1. **Inclusion:** subjects with ≥1 kidney tumor **Segmentation** annotation (excl. seed points /
   no-findings) at **Pre-dose** AND at ≥1 **Post-chemotherapy** timepoint. Expected n≈330
   (AREN0532: 25, AREN0533: 83, AREN0534: 222 — from metadata; final n from flow diagram).
2. **Modality rule:** restrict primary analysis to segmentations referencing **CT Image Storage**
   (`ReferencedSOPClassUID` in each RTSTRUCT). MR-referenced segmentations are reported
   separately (sensitivity/stratification), not pooled.
3. **Measurements:** tumor volume per ROI per timepoint = Σ over slices (closed-planar polygon
   area via Newell's method × inter-slice spacing), mL. Per subject per timepoint: sum of kidney
   tumor ROIs (multi-lesion labels e.g. "RT KIDNEY - 1/-2"; bilateral in AREN0534).
   Covariates: age, sex (RTSTRUCT headers), laterality (structure label), collection (= trial
   stratum: 0532 low-stage FH, 0533 stage III–IV, 0534 bilateral).
4. **Outcomes:** primary = **% volume change** Pre-dose → first Post-chemotherapy timepoint;
   secondary = absolute change, volume trajectories across all timepoints (AREN0534 has up to 6).
5. **Stats:** descriptive volumes by timepoint; paired comparison **Wilcoxon signed-rank** on %
   change; subgroup descriptives by collection/laterality. Because the three trials use different
   chemotherapy schedules and response intervals, results are reported **per trial**, with a
   pooled estimate as secondary and explicitly not treated as a between-trial comparison.
6. **Reproducibility:** all numbers and figures derive from `code/` in this repository, re-run
   before release. `volumes.py` output is the single source of truth for every Results number.
7. **Figures:** waterfall plot of % volume change; volume-time trajectories.

## Deviations from the locked plan

None to date. Any deviation is recorded here with its date and reason.

## Ethics

Public, de-identified imaging-derived annotations (TCIA / COG trial data). The manuscript
includes a data-source ethics statement and TCIA/COG data citations. Per TCIA's data-use terms
and 45 CFR 46, analysis of these public de-identified data does not constitute human subjects
research requiring institutional review board approval.
