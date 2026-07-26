# Protocol — Volumetric CT Response of Wilms Tumor to Neoadjuvant Chemotherapy (TCIA AREN0533)

**Manuscript type:** Original article (database study) — Cureus route: **FREE** (≤10 authors, ≤30 refs)
**Stage:** protocol | **First author:** wife | **Senior author:** michael
**Validation score: 96/100 (GREEN)** — 0 prior reviews, 37 primary studies (5y), TCIA instant access

---

## Question

Can volumetric CT measurements track Wilms tumor response to neoadjuvant chemotherapy in children?

## Why this topic won

- Pediatric oncologic imaging — serves **both** her radiology target and pediatrics backup
- TCIA Wilms tumor collections (Children's Oncology Group trials AREN0532 / AREN0533 / AREN0534)
  include **radiologist-reviewed 3D tumor segmentations** — no segmentation labor
- Zero prior reviews on the exact question; 37 related primary studies = feasible + uncrowded
- Original research = the strongest ERAS "meaningful scholarly work" tier; $0 at Cureus

## Data plan

| Collection | Contents | Access |
|---|---|---|
| TCIA Wilms Tumor (AREN0532/0533/0534) | CT with 3D tumor segmentations, trial subjects | Instant download |

**Step 0 (execution):** inventory subjects with (a) baseline CT, (b) follow-up CT after neoadjuvant
chemotherapy, (c) usable segmentations for both timepoints. Record inclusion/exclusion counts (flow diagram).

**Clinical covariates verification step:** stage, histology, and outcomes may be limited in the public
collection. If unavailable publicly, the core volumetric analysis stands alone (volume trajectory);
clinical correlation (COG data request) is a stretch goal, NOT a blocker.

## Analysis plan (LOCKED before touching data)

1. **Inclusion:** paired pre-/post-neoadjuvant CT with segmentations
2. **Measurements:** tumor volume per timepoint from provided segmentations; absolute and % change;
   time between scans; laterality
3. **Outcomes:** primary = % volume reduction; secondary = trajectory patterns (early vs late responders)
4. **Stats:** descriptive volumes by timepoint; paired comparisons (Wilcoxon signed-rank);
   if clinical covariates available: volume response vs stage/histology (Kruskal–Wallis), Spearman correlation
5. **Reproducibility:** all numbers/figures from `code/` in this repo; code re-run at QA gate
6. **Figures:** waterfall plot of % volume change; volume-time trajectories; example segmentation overlays

## Ethics

Public, de-identified imaging (TCIA / COG trial data). Manuscript includes a data-source ethics statement
and TCIA/COG data citations. No IRB pathway required.

## Milestones (~10 weeks)

- [ ] Week 1: inventory collections; lock inclusion counts
- [ ] Weeks 2–4: volume extraction code + QC of segmentations
- [ ] Weeks 5–6: analysis + figures/tables
- [ ] Weeks 7–8: full draft (Cureus original-article structure)
- [ ] Week 9: automated QA → GATE 2 (both humans)
- [ ] Week 10: package → GATE 3 (wife submits)
