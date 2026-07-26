# Protocol — Volumetric Response of Wilms Tumor to Neoadjuvant Chemotherapy (TCIA AREN0532/0533/0534)

**Manuscript type:** Original article (database study) — Cureus route: **FREE** (≤10 authors, ≤30 refs)
**Stage:** execution | **First author:** wife | **Senior author:** michael
**Validation score: 96/100 (GREEN)** — 0 prior reviews, 37 primary studies (5y), TCIA instant access
**Gate 1.5 CONFIRMED 2026-07-26 (michael, recorded in research_approvals):** paired RTSTRUCT
contour volumetry, ~330 paired subjects, NO NCTN application (stage/histology/outcomes out of scope).

---

## Question

How does Wilms tumor volume respond to neoadjuvant chemotherapy in children, measured on
radiologist-reviewed 3D segmentations from COG trials AREN0532/0533/0534?

## Why this topic won

- Pediatric oncologic imaging — serves **both** her radiology target and pediatrics backup
- TCIA Wilms collections include **radiologist-reviewed 3D tumor segmentations** — no segmentation labor
- Zero prior reviews on the exact question; 37 related primary studies = feasible + uncrowded
- Original research = the strongest ERAS "meaningful scholarly work" tier; $0 at Cureus

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
   change; subgroup descriptives by collection/laterality (no NCTN covariates — Gate 1.5 decision).
6. **Reproducibility:** all numbers/figures from `code/` in this folder; code re-run at QA gate.
   `volumes.py` output is the single source of truth for every Results number (spec R4).
7. **Figures:** waterfall plot of % volume change; volume-time trajectories; 3D contour renders
   of example cases (no image overlays — source images not public).

## Ethics

Public, de-identified imaging-derived annotations (TCIA / COG trial data). Manuscript includes a
data-source ethics statement and TCIA/COG data citations (collection DOIs pulled at drafting
time). No IRB pathway required.

## Milestones (~10 weeks)

- [x] Week 1: inventory collections; dataset verification; Gate 1.5 confirm (paired design, no NCTN)
- [ ] Weeks 2–4: RTSTRUCT volume extraction (`volumes.py`) + QC of the paired cohort
- [ ] Weeks 5–6: analysis + figures/tables
- [ ] Weeks 7–8: full draft (Cureus original-article structure)
- [ ] Week 9: automated QA → GATE 2 (both humans)
- [ ] Week 10: package → GATE 3 (wife submits)
