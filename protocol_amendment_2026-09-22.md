# Post-audit analysis amendment — locked before revised outcome calculation

Date: 22 September 2026. This amendment supersedes the original 26 July 2026 plan for this revision. The original aggregate findings have already been seen. This is therefore a post-analysis correction, not an original prespecification. The revised outcomes below will not be examined until the eligibility/aggregation rules are finalized and this document is locked. Raw source records and the original outcomes have already been inspected, including the eligibility problems motivating these rules.

## Reason and revised estimand

The audit demonstrated duplicate target measurements, nonrenal contamination, unresolved lesion identity, incomplete computed totals, and missing dates/target identifiers. Current TCIA version-2 annotations provide source-study dates, stable tracking identifiers, and stored annotation volumes. The revision will estimate **within-patient change in summed archive-reported volumes of the same annotated renal target lesions from baseline to the first numbered follow-up**. It does not estimate chemotherapy efficacy, total renal tumor burden, histologic response, or change before surgery. Clinical treatment and surgery dates are not linked.

The volume endpoint changes from custom polygon integration to the annotation object's stored ROI volume in mL (DICOM cm³). This must be prominently disclosed. If raw ROI mappings cannot be verified, conflicted records are excluded rather than repaired by choosing plausible values. Source images are not assumed available.

## Source versions and outcome-neutral normalization

Use the December 2025 corrected TCIA annotation metadata for AREN0532, AREN0533 and AREN0534, with retrieval provenance and SHA-256 hashes. Retain old metadata solely for historical-label conflict checks and provenance, not as a source for substitute measurements. Strip whitespace in identifiers. Normalize the documented repeated AREN0532-PAURIY patient string to the single identifier only with recorded old/new series concordance. Preserve all unnormalized source fields. Parse two-digit shifted years as 19xx, as explicitly documented by their source values, not a locale-dependent current-century pivot.

A candidate renal target is a segmentation annotation whose TrackingID names a kidney; records must additionally have an explicit TrackingUID, compatible target labels/laterality and a stored positive finite ROI volume to pass the primary selection. Seed points, nodes, lung lesions and generic negative assessments do not contribute a volume. Negative assessments remain in the screening audit; a missing positive target cannot be assigned zero.

## Primary CT cohort

Unit: patient. Screen every patient with at least one current renal segmentation. Apply the following ordered, mutually exclusive first-failure exclusions, with totals by collection:

1. No baseline CT renal segmentation (alternative MRI series are not added to CT totals).
2. No Post-Chemotherapy #1 CT renal segmentation.
3. A required annotation shares a source identifier with an old postoperative or recurrence record.
4. Missing/malformed dates, source StudyInstanceUID, source SeriesInstanceUID, TrackingUID, renal target label or stored volume; nonfinite/nonpositive volume.
5. More than one imaging StudyInstanceUID or StudyDate among the selected CT annotations at either visit.
6. More than one selected segmentation row for a TrackingUID within a visit, including repeated acquisitions or exports. No mean, maximum, minimum or last export is chosen according to volume.
7. Different TrackingUID sets or incompatible target labels/laterality across baseline and follow-up.
8. Follow-up StudyDate not strictly after baseline.
9. Source-object verification incomplete or unresolved: raw intended ROI tracking/anatomy, patient, examination/date, referenced source/modality and stored ROI volume must be consistent with the current metadata. The intended target must contain closed-planar segmentation contours with at least three points per contour; seed-only, nonclosed, malformed or anatomically conflicting targets fail structural source verification. Whole-object multi-ROI ambiguity is not resolved by a matching series label alone.

For a retained patient, every selected visit represents one verified source examination/date. Distinct CT source series within that examination may contribute different targets, provided each target has exactly one annotation and source/target identity is verified; the same target cannot be added twice. Retain a per-target source table and validation status. One patient's contribution is the sum of the same target set at each visit.

Only the unique intended tracked renal ROI contributes from each selected annotation object. Other nonrenal or untracked ROIs in the same object are ignored, never added to a renal target; disagreement between intended tracking identity and the raw anatomic ROI name remains unresolved and excludes that patient. Raw annotation verification can resolve an audit flag only through documented ROI number/name/TrackingUID identity and source metadata. All overrides require a reason/evidence, never the size or direction of the resulting response. If source data contradict current metadata, do not silently mix versions. State exactly which ROI field was used and whether the archive metadata were corrected.

## Secondary analyses

- MRI→MRI using the same visit, completeness, source and target rules; report separately, never pool CT and MRI.
- CT subset with examination interval ≤90 days, selected without reference to volume changes. The 90-day window is an outcome-independent sensitivity around commonly used six- and twelve-week assessment contexts; it is not asserted to be a uniform or clinically verified chemotherapy duration. This is a scan-interval sensitivity, not a claim of 90-day treatment duration. Report all interval distributions and outlying intervals transparently.
- Matched-target volume change remains primary; no unmatched target is discarded while calling the remaining sum complete. If a broader per-target sensitivity is subsequently needed, add another dated amendment before looking at its results.
- Geometric recomputation sensitivity: apply the repaired contour integrator to the exact source ROI numbers/TrackingUIDs already selected. Report the independently computable paired subset, QC flags and paired changes relative to stored-volume results. This is a numerical-method check, not independent clinical segmentation validation; stored ROI volume remains the primary endpoint regardless of agreement or direction.
- No routine cross-trial hypothesis tests and no adjustment for clinical covariates absent from source data.

## Summaries and uncertainty

Report trial-specific n, baseline/follow-up volume median and IQR, paired percentage-change median and IQR, absolute-change median and IQR, interval median/IQR/range, target counts, annotated laterality, and numbers of numerical decreases/increases/unchanged. A positive percentage is a numerical increase, not a clinical progression diagnosis.

Use two-sided nonparametric order-statistic confidence intervals for the patient-level median percentage change, selecting the narrowest central interval with exact binomial coverage at least 95%. State the actual confidence coverage where discreteness matters. If sample size cannot support a finite 95% interval, mark it not estimable. Confidence intervals characterize uncertainty under independent-patient sampling assumptions; archive selection bias remains unaddressed. Pooled results are secondary descriptive summaries only. Do not present a pooled signed-rank p-value as validation or a treatment-effect estimate.

Figures: per-trial waterfall of patient-level percentage changes with paired n; baseline/follow-up trajectories only for retained pairs; interval-versus-percentage scatter as descriptive timing context, without causal trend claims. Use data-derived axis limits that show all observations, and label any nonlinear scale.

## Disclosure and limitations

This revision follows observed errors and changes the endpoint, dataset version, matching rules and statistical presentation. It must not claim no deviations or original prospective registration. Same-target positive segmentation requirements can preferentially omit complete responders represented only by negative/missing annotations. Clinical treatment, surgery, histology and outcomes are not verified. Without source images or independent readers, source contour accuracy cannot be established.

## Lock record

Eligibility, endpoint, primary and secondary summaries, and the numerical-method sensitivity above were finalized before calculating any revised patient-level change. Original results, current source records and metadata eligibility counts had already been examined. The source checks may identify exclusion reasons under these fixed rules; no target, timepoint, volume or statistical method will be chosen because its result is more favorable. Finalization timestamp and document SHA-256 are recorded in lock_record.json and the analysis output.

## Source-name normalization addendum — 2026-09-22T11:08:21.687047+00:00

Before revised outcome calculations, raw-object review identified a harmless omitted ROIName target-number suffix (for example, LT KIDNEY versus tracked LEFT KIDNEY 1). Permit only this omission when (a) the raw intended ROI has the unique exact TrackingUID required by current metadata, (b) raw and metadata TrackingID match exactly after the existing abbreviation/whitespace normalization, and (c) ROIName identifies the same KIDNEY and explicitly known LEFT or RIGHT side. Do not infer unknown laterality, change a contradictory number, map ABDOMEN to KIDNEY, or relax longitudinal TrackingUID/TrackingID completeness. Log every application in the source manifest. This naming addendum was approved after inspecting the source record and before any revised aggregate or patient-level changes were calculated. All other endpoint and selection rules remain as recorded above.
