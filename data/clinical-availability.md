# Clinical covariate & annotation availability — TCIA Wilms (AREN0532/0533/0534)

Checked 2026-07-26 by `agent-cli` on Michael's laptop (TCIA reachable locally).
Method: TCIA wiki REST API (collection + annotation pages), NBIA v1 API, and direct
inspection of one downloaded RTSTRUCT series. Sources linked inline.

**This document supersedes the "single-timepoint MR, no CT" interpretation from the
first inventory read. See "Corrected understanding" below.**

## Corrected understanding of the dataset

The three public NBIA collections contain **only RTSTRUCT annotation objects**
(9,355 series total, 100% `Modality=RTSTRUCT`, UID root `1.2.826.0.1.534147...` = AIM
tool exports). No source images (CT or MR) are hosted in these collections.

- The v2 inventory funnel ("0 CT, 0 paired, 1,075 segmented") therefore measured the
  annotation objects, not the imaging. Its "segmented study" count was right; the
  "all MRI" conclusion was wrong.
- Each RTSTRUCT references its source imaging study. Verified by direct download of a
  sample series (`AREN0533-PARFRF`, "LT KIDNEY - 1"): **21 axial slices, 5,087 contour
  points, CLOSED_PLANAR, referencing CT Image Storage** — a true volumetric 3D tumor
  segmentation on CT.
- The paired RTSTRUCT manifest on the wiki
  (`AREN0533_OriginalCTs_SEGSandSeedpoints_manifest_01-31-2023.tcia`, 778 series)
  lists the original CT series, but they are **not downloadable via the public NBIA
  API** (`getImage` → HTTP 400 "Image with given SeriesInstanceUID … not found").
  Treat source images as unavailable; the RTSTRUCT contours alone support volumetric
  analysis (slice area × spacing), but **not** radiomics or image+contour overlay figures.

## Timepoint structure (from annotation metadata reports)

Downloaded from the wiki annotation pages into `data/`:
`Metadata_Report_AREN0532.csv` (2,531 rows), `Metadata_Report_AREN0533.csv` (3,025),
`Metadata_Report_AREN0534.csv` (3,785). Each row = one annotation with
`ClinicalTrialTimePointID` (Pre-dose, Post-chemotherapy #1..#4, Post-operative, Recurrence),
annotation type (Segmentation / Seed point / No findings), and structure label.

Kidney tumor **Segmentation** annotations (excl. seed points / no-findings / lung):

| Collection | Subjects w/ kidney seg | Lesion-timepoints | Pre-dose + Post-chemo paired subjects |
|---|---|---|---|
| AREN0532 | 536 | 687 | 25 |
| AREN0533 | 275 | 379 | 83 |
| AREN0534 | 236 | 1,284 (up to 6 timepoints/subject) | 222 |
| **Total** | **1,047** | **2,350** | **330** |

- **The original paired pre/post-neoadjuvant volumetric design is feasible after all**,
  on RTSTRUCT contours: ~330 subjects with kidney tumor segmentations at both Pre-dose
  and ≥1 Post-chemotherapy timepoint (driven by AREN0534, the bilateral/diffuse
  histology trial with the richest longitudinal follow-up).
- Single-timepoint fallback cohort is even larger: 1,047 subjects.
- Source modality is **predominantly CT** (StudyDescription tabulation), with some MR
  (notably in AREN0534). The definitive per-segmentation source class is recorded in
  each RTSTRUCT (`ReferencedSOPClassUID`) and will be enforced at volume-extraction time
  (restrict to CT-referenced segmentations, or stratify).
- Lung metastasis segmentations also exist (esp. AREN0533, 870 rows) — optional
  secondary analysis.

## Demographics (free, no application)

RTSTRUCT DICOM headers carry `PatientSex` and `PatientAge` (verified: "M", "002Y").
`StudyDate` is de-identification-shifted (1959…) — absolute dates unusable, but
`ClinicalTrialTimePointID` gives relative timing. Age/sex for ~all subjects are
extractable at volume-extraction time.

## Clinical covariates (stage / histology / outcomes) — NOT on TCIA

No clinical CSVs are attached to any of the six TCIA wiki pages (checked all
attachments on the 3 collection pages + 3 annotation pages). Per the collection
pages, patient-level clinical data live in the **NCTN/NCORP Data Archive**
(registration + data access application required; timeline is weeks, not instant):

| Trial | NCTN node | Trial population (per page/pubs) |
|---|---|---|
| AREN0532 | https://nctn-data-archive.nci.nih.gov/node/689 | Stage I–III favorable-histology; 544 pts; LOH 1p/16q, lymph node status, histology, EFS/OS |
| AREN0533 | https://nctn-data-archive.nci.nih.gov/node/737 | Stage III–IV FHWT; lung mets response, LOH 1p/16q, EFS/OS |
| AREN0534 | https://nctn-data-archive.nci.nih.gov/node/728 | Bilateral Wilms; response- and histology-based therapy, EFS/OS |

**Linkage risk (unverified):** joining TCIA `PatientID`s (e.g. `AREN0534-PAUCWN`) to
NCTN subject IDs has not been tested; ID concordance is unknown until an application
is approved.

## Consequences for the pivot decision (input to Gate 1.5)

1. **No pivot to a single-timepoint design is needed.** The original question —
   volumetric tumor response to neoadjuvant chemotherapy — stands, on ~330 paired
   subjects, computed from RTSTRUCT contours. Title/modality wording: predominantly
   CT (stratify or restrict at extraction).
2. **Without NCTN data:** primary analysis = volume trajectory + % change; covariates
   limited to age, sex, laterality (from labels), collection (as trial/stage proxy:
   0532 = low-stage FH, 0533 = stage III–IV, 0534 = bilateral).
3. **With NCTN data (stretch goal):** stage/histology/LOH/outcome correlation.
   Recommend Michael files the NCTN application in parallel — it is free but slow,
   and the manuscript does not block on it.
4. Figures: 3D contour renderings possible; source-image overlays not possible
   (images not public).
