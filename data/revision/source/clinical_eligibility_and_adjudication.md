# Revised source and clinical interpretation rules

Date: 2026-09-22. This revision follows discovery of source-version, identity, timing and volume-aggregation defects in the earlier analysis. It is a new, documented retrospective analysis; do not label it prospectively preregistered or claim the earlier lock was preserved.

## What the endpoint can mean

Use **archive-reported volume of consistently tracked annotated renal lesions**, summed once per target within one imaging study at each of two archive-labeled visits. The comparison is `Pre-Dose` to `Post-Chemotherapy #1`, with the observed interval reported. This describes selected persistent/evaluable annotated lesions in COG imaging collections. It does not verify malignant histology, chemotherapy regimen, surgical status, or a causal treatment effect. It is not total renal tumor burden, because annotation protocols selected at most two lesions per organ and five per scan. It cannot estimate complete response: absent follow-up segmentation is not a documented zero volume.

The AREN0534 collection includes a trial with bilateral Wilms tumor, predisposed/multicentric unilateral tumor, and diffuse hyperplastic perilobar nephroblastomatosis arms. The arms did not all use the same regimen. Do not relabel this entire collection as bilateral disease or as uniform three-drug neoadjuvant treatment. Individual clinical arm and pathology are unavailable to this analysis.

## Source retrieval and volume authority

Current version 2 metadata were retrieved from official TCIA sources (release dates 2025-12-03, 2025-12-19 and 2025-12-22). The current raw RTSTRUCTs are publicly downloadable through the official NBIA `getImage` endpoint. Retrieval manifest, SHA-256 hashes and outcomes are retained in this directory. The selected intended ROI is determined through a unique `TrackingUID` match, crosschecked against `TrackingID`, ROI anatomy/name and source study metadata. DICOM ROI Volume `(3006,002C)` is the primary volume, with units cubic centimeters (equivalent to mL); the metadata value must agree within the documented rounding tolerance. No numerical substitution is made from an unrelated ROI or from a hand-picked contour calculation.

Matching metadata and raw tags establishes internal source consistency, not clinical accuracy or independent validation. Original CT/MR images could not be visually inspected: an official current API probe returned HTTP 400 with the explanation that the referenced source CT is not in the public domain (`source_CT_probe.json`). Official current collection pages also mark original images unavailable under changed controlled-access arrangements. Do not imply radiologist rereview of these source images.

Official ROI units: https://dicom.nema.org/medical/Dicom/2024e/output/chtml/part03/sect_C.8.8.5.html

## Conservative cohort rule agreed before revised outcome calculation

1. Eligible objects must be current metadata renal segmentations at the exact two selected visits; seed points, negative assessments, nonrenal targets and other visit labels are not substituted.
2. The primary modality is CT at both visits. A separately identified MRI analysis may use the same rules. Mixed-modality pairs are not pooled into the CT primary.
3. Every selected visit must correspond to exactly one `StudyInstanceUID` and one shifted `StudyDate`. Multiple sequences within that same study/date can contribute different targets; repeated annotations of one target cannot be summed or chosen by size.
4. Each target must occur once per visit. The complete baseline and follow-up `TrackingUID` sets and normalized anatomy/laterality labels must match. A disappearing target, newly appearing target or untracked additional ROI cannot be silently assigned zero, dropped or added.
5. Stored volumes must be finite and positive; dates must be parseable and follow-up must occur after baseline. Retain observed intervals and report them. Wide intervals are not automatically equivalent to six-week response. The revised statistical plan specifies an interval of at most 90 days as a sensitivity analysis around the usual six-/twelve-week assessment context; do not introduce additional cutoffs based on revised outcome results.
6. Exclude old postoperative/recurrence phase conflicts, unverifiable identity, unresolved source contradictions and intended ROIs that fail the locked source structural checks. The structural checks include a unique intended ROI, its matching contour sequence, closed-planar contour type and enough coordinates to form a polygon. The complete source verification reasons are machine-readable.
7. Raw verification is required for every included intended ROI, including source study/date, canonical subject, referenced series/modality, tracking fields, anatomy name and stored volume.
8. Exclusions follow a declared first-failure hierarchy. Preserve all additional flags for audit. Analyze subjects, not correlated lesion-timepoint observations, as the primary independent units.

Source-label addendum, approved before revised aggregate outcomes: an ROIName may omit the numeric lesion suffix only when a unique exact TrackingUID identifies the intended ROI and the ROIName and TrackingID specify the same kidney and known side. This does not permit unknown-to-known side inference, contradictory numbers, or any nonrenal-to-renal reinterpretation. AREN0534-PAVMYW provided the outcome-blind source example: raw ROIName `LT KIDNEY`, raw/metadata TrackingID `LEFT KIDNEY - 1`, exact unique tracked UID. The normalization is logged per object in `roi_name_normalization_note`; longitudinal TrackingID/UID matching remains strict.

## Clinical phase and dates

TCIA explicitly preserves within-subject date intervals while shifting calendar dates. This supports an interval derived from mutually consistent source StudyDate fields; it does not validate a specific chemotherapy start date. The revision therefore calls it imaging interval, not treatment duration. Source: https://wiki.cancerimagingarchive.net/display/Public/National%2BClinical%2BTrials%2BNetwork%2B%28NCTN%29%2BDate%2BHandling

Current raw and metadata labels cannot alone prove preoperative status. Two direct probes show that an old AREN0534 postoperative series now carries both `Post-Chemotherapy #3` and a generic post-chemotherapy code in the current RTSTRUCT; an old AREN0533 recurrence series similarly carries `Post-Chemotherapy #2`. Preserve historical phase conflicts when reconciling versions. Restricting to exact #1 avoids these observed later-label changes but does not establish surgery-free status for all selected patients.

## Case adjudication based on current raw objects

| Case | Confirmed source facts | Conservative decision |
|---|---|---|
| AREN0533-PARUTG | Node object includes a separately tracked node and an extra kidney ROI lacking TrackingUID; dedicated renal object has the intended tracked kidney | Ignore node object and untracked duplicate; dedicated renal pair can qualify if all general rules pass |
| AREN0533-PARMKA | Baseline intended TrackingUID maps to ROIName `ABDOMEN - 1` with 75.197435 mL; another untracked kidney ROI is 541.534952 mL | Exclude patient for unresolved anatomy. Do not switch to the larger volume on plausibility alone |
| AREN0532-PAURIY | All relevant raw headers use `AREN0532-PAURIY`; current metadata duplicates the string. Two baseline studies/dates contain the same tracked kidney | Exact patient-ID correction is validated and logged; still exclude the ambiguous baseline study/duplicate-target comparison |
| AREN0532-PATTED | Two baseline studies/dates repeat two right-sided targets; available later selected target is left-sided #3 at post-chemo #2 | No exact #1 primary pair; do not sum baseline scans or compare different target sets |
| AREN0534-PAPYAR | Baseline left lesion belongs to a 1956 study; right lesions to a 1959 study; follow-up contains right targets only. Some intended contours have single-point closed-planar entries | Exclude for study/date/target inconsistencies; no clinical interpretation of apparent shrinkage |
| AREN0532-PATYFE | Available renal follow-up is #3, approximately 198 days later; additional different kidney target appears | Excluded by exact #1 rule; no substitution of later follow-up |
| AREN0534-PAUTBY | Eight replacement current objects retrieve the formerly failed case. Same #1 label spans multiple studies/dates, including one day after baseline and two later dates | Exclude ambiguous visit rather than aggregate scans or select the smallest/largest volume |

These are data adjudications, not image-based clinical diagnoses. No curator, patient or other person was contacted, and no unavailable information was fabricated.

## Primary clinical sources supporting corrected trial framing

- AREN0534 unilateral-arm report: https://pmc.ncbi.nlm.nih.gov/articles/PMC7769115/
- AREN0534 nephroblastomatosis report: https://pmc.ncbi.nlm.nih.gov/articles/PMC9254258/
- AREN0534 bilateral-arm report: https://pmc.ncbi.nlm.nih.gov/articles/PMC5629006/
- AREN0533 metastatic-trial report, including nephrectomy recommendations: https://pmc.ncbi.nlm.nih.gov/articles/PMC6075846/
- AREN0532 very-low-risk nephrectomy-only report: https://pmc.ncbi.nlm.nih.gov/articles/PMC5145762/

Required annotation dataset attribution must use Rozenfeld/Jordan and the actual version: AREN0532 `10.7937/KJA4-1Z76`; AREN0533 `10.7937/WFCC-DA41`; AREN0534 `10.7937/N930-BM78`.
