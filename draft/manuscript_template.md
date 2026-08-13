# Volumetric Response of Wilms Tumor to Neoadjuvant Chemotherapy Across Three Children's Oncology Group Trials

Rachel Velasco ^1^, Michael Martinez, MD ^2^

1. Washington University of Health and Science, San Pedro, Belize
2. Transitional Year Residency Program, TidalHealth Peninsula Regional, Salisbury, MD, USA

**Corresponding author:** Michael Martinez, MD, michael13414@gmail.com

## Abstract

**Background:** Wilms tumor response to neoadjuvant chemotherapy is usually summarized categorically or by single diameters rather than by three-dimensional volume.

**Objective:** To quantify volumetric response of Wilms tumor to neoadjuvant chemotherapy using publicly available three-dimensional tumor segmentations, reported separately for the three trials in which segmentations are available.

**Materials and Methods:** We used radiologist-reviewed kidney tumor segmentations from three Children's Oncology Group trials (AREN0532, AREN0533, AREN0534) on The Cancer Imaging Archive. Subjects with a pre- and at least one post-chemotherapy segmentation were included; volumes were computed from closed-planar contours and cross-validated against the annotation tool's measurements. Results are reported per trial because chemotherapy schedules differ, with a pooled estimate as secondary.

**Results:** Of {F_META_ANY} subjects with any kidney segmentation, {F_PAIRED} had computable computed-tomography (CT)-referenced volumes at both timepoints. Median volume change was {S0532_MED}% in AREN0532 (delayed-nephrectomy subset, n = {S0532_N}), {S0533_MED}% in AREN0533 (stage III–IV, n = {S0533_N}), and {S0534_MED}% in AREN0534 (bilateral, n = {S0534_N}); these profiles are not directly comparable because response intervals differ. Pooled, median volume fell from {PRE_MED} mL to {POST_MED} mL (median change {PCT_MED}%; Hodges–Lehmann estimate {HL_EST}%, 95% confidence interval {HL_LO}% to {HL_HI}%), decreasing in {N_DEC} of {N} subjects.

**Conclusions:** Volumetric measurement of publicly available expert segmentations shows substantial, protocol-dependent tumor volume reduction with neoadjuvant chemotherapy across three Children's Oncology Group trials, providing quantitative benchmarks for response-adapted trial design in Wilms tumor.

**Keywords:** Wilms tumor; neoadjuvant chemotherapy; tumor volumetry; nephroblastoma; pediatric oncology; The Cancer Imaging Archive

---

## Introduction

Wilms tumor (nephroblastoma) is the most common primary malignant renal tumor of childhood, accounting for the large majority of pediatric renal neoplasms, with most diagnoses made in early childhood [10,15]. Two cooperative philosophies dominate its management: the Children's Oncology Group (COG) approach of upfront nephrectomy followed by adjuvant therapy for most unilateral tumors, and the International Society of Paediatric Oncology (SIOP) approach of preoperative chemotherapy for nearly all patients [11,12]. Within COG protocols, however, neoadjuvant chemotherapy is central for defined subgroups: bilateral disease (AREN0534), stage IV disease with pulmonary metastases (AREN0533), and selected very-low-risk or inoperable presentations [2,3,5,6]. Response to this chemotherapy determines subsequent surgical timing, the feasibility of nephron-sparing surgery, and, in SIOP-inspired frameworks, postoperative treatment intensity [6,19].

Despite the centrality of tumor response, its radiologic quantification remains coarse. Trial-level assessments have largely relied on categorical response criteria or unidimensional measurements, even though volumetric methods capture tumor burden change more sensitively than diameter-based approaches in pediatric solid tumors [18]. Volumetric Wilms data do exist at scale for the post-treatment timepoint: the SIOP WT 2001 study analyzed prospectively collected tumor volumes from more than 3,000 patients (complete blastema-volume data in 1,802) to derive residual blastema volume [19]. But paired, imaging-level quantification of the response itself (pre- versus during chemotherapy) is limited to small series and recent secondary analyses, the nearest being a 56-patient single-institution cohort measuring pre/post-chemotherapy volume in unilateral disease [27], including segmentation-based volumetry studies and early efforts to predict response computationally [20,25].

The Cancer Imaging Archive (TCIA) hosts the imaging annotation output of COG trials AREN0532, AREN0533, and AREN0534 as publicly downloadable radiotherapy structure sets containing radiologist-reviewed, three-dimensional tumor contours with defined trial timepoints [1-9]. We used these data to fill the gap described above: cohort-scale, protocol-stratified volumetric quantification of Wilms tumor response to neoadjuvant chemotherapy, reported separately by trial because chemotherapy schedules and response intervals differ. Because the underlying segmentations are public and our analysis pipeline is fully scripted, every number in this report is independently reproducible from the same public source data, a methodological strength of the measurement, not its purpose.

## Materials and Methods

### Data source

We used the TCIA collections AREN0532, AREN0533, and AREN0534, which contain imaging annotations from the corresponding COG trials [1-9]. The public collections consist of annotation objects (DICOM radiotherapy structure sets, RTSTRUCT) containing closed-planar tumor contours generated with expert review; each object references the source imaging study and is labeled with a clinical trial timepoint (Pre-dose; Post-chemotherapy #1–#4; Post-operative; Recurrence) in the collections' published metadata. Source images are not distributed with the public collections; the analysis is therefore contour-based. Patient sex was extracted from annotation headers; standard DICOM de-identification profiles retain PatientSex while modifying dates and ages, which is why sex, but not age, is usable here. DICOM age strings were also extracted but found to be archive-coarsened to near-uniform values (predominantly "2Y" in two of the three collections, with within-subject variation across timepoints); age is therefore not analyzed or reported as a distribution. Dates are shifted by the archive's de-identification process, so absolute scan intervals were unavailable and relative timing was taken from the trial timepoint labels.

### Treatment context: who received neoadjuvant chemotherapy

The three trials differ in how subjects came to be scanned before and after chemotherapy, and this defines each subgroup. AREN0534 (bilateral Wilms tumor) mandated three-drug preoperative chemotherapy for all subjects, with further therapy guided by response and histology; its subjects therefore form a uniform protocol-driven neoadjuvant cohort [6,23]. AREN0533 enrolled stage III–IV favorable-histology disease, in which renal tumor response accompanied protocol-specified chemotherapy and reassessment (stage IV disease with pulmonary metastases was assessed for pulmonary response at week 6) [3,8]. AREN0532 was primarily an upfront-nephrectomy trial for very-low- and standard-risk disease; however, a substantial minority, 123 of 535 patients (23%) with stage III disease in the trial report, underwent delayed nephrectomy after preoperative chemotherapy, generally for surgeon-assessed inoperability at presentation [2,22]. The AREN0532 subjects in our paired cohort represent this delayed-nephrectomy subset rather than the trial's main upfront-surgery population, and findings for that subgroup should be read accordingly.

### Cohort definition

Subjects were eligible if annotation metadata showed at least one kidney tumor segmentation (excluding seed-point-only and "no findings" annotations) at the Pre-dose timepoint and at least one Post-chemotherapy timepoint. For the primary analysis we further required computable volumes from contours referencing CT at both timepoints; segmentations referencing other modalities (a minority, predominantly in AREN0534) were excluded from pooling. When a subject had multiple kidney tumor regions of interest at one timepoint (e.g., bilateral disease), volumes were summed. The paired measurement was Pre-dose versus the first available post-chemotherapy timepoint.

### Volume computation

For each region of interest, slice area was computed from closed-planar contour vertices by the Newell polygon method and multiplied by the median inter-slice spacing; slice volumes were summed to yield tumor volume in milliliters. This is the standard contour-integration approach used in radiotherapy planning and requires no access to source images. As an internal validation, computed volumes were compared with the annotation tool's own per-ROI volume field (DICOM ROI Volume, tag 3006,002C), available for {VVOL_N} contoured lesions: agreement was near-perfect (Spearman ρ = {VVOL_RHO}; median absolute difference {VVOL_MEDDIFF}%). Crucially, the signed difference was centered at zero in both phases (median {VVOL_PRE_SIGNED}% pre-chemotherapy, {VVOL_POST_SIGNED}% post-chemotherapy); the larger absolute spread post-chemotherapy ({VVOL_POST_ABS}% vs {VVOL_PRE_ABS}%) reflects small-lesion spacing sensitivity rather than directional bias, so percent-change estimates are not systematically distorted. Segmentation-based volumetry has previously been shown to be more reproducible than diameter-based measurement in Wilms tumor [25].

### Statistical analysis

Percent volume change was defined as (post − pre)/pre × 100%. Because trial chemotherapy schedules differ and exact intervals are unrecoverable from de-identified data, the primary analysis is descriptive per trial (median, IQR); a pooled Wilcoxon signed-rank comparison with a Hodges–Lehmann estimate and 95% confidence interval is reported secondarily. Prespecified subgroups were the three trials (AREN0532: delayed-nephrectomy subset of a predominantly upfront-surgery trial; AREN0533: stage III–IV disease; AREN0534: bilateral disease). Analyses used Python 3.12 (pydicom, NumPy, pandas, SciPy, matplotlib). A two-sided p < 0.05 was considered significant.

### Reproducibility

The cohort manifest, extraction code, analysis code, and the rendering pipeline that transfers every result statistic from machine-generated output into this manuscript are public (Code Availability); every number in Results regenerates from the public annotation metadata and code. Trials are cited per archive requirements [1-9]. Large-language-model coding assistants were used to write the analysis code and to assist with manuscript drafting, under direct human supervision; all statistics were machine-generated from the public dataset by the published pipeline, and every citation was resolved against PubMed records and verified by the authors, who take full responsibility for the content.

## Results

### Cohort

Annotation metadata contained {F_META_ANY} subjects with at least one kidney tumor segmentation, of whom {F_META_PAIRED} had segmentations at both Pre-dose and at least one Post-chemotherapy timepoint. Computable CT-referenced volumes at any timepoint were available for {F_EXTRACTED} subjects; requiring volumes at both paired timepoints left {F_PAIRED} subjects in the analysis cohort ({C_0532} from AREN0532, {C_0533} from AREN0533, {C_0534} from AREN0534). The {F_EXCLUDED} metadata-paired subjects not analyzed were excluded for prespecified reasons: segmentations referencing only non-CT imaging at a paired timepoint, single-slice or otherwise degenerate contours, annotation series no longer retrievable from the archive (eight series belonging to one subject), and {F_POSTOP_W} subject whose only post-treatment segmentation was post-operative rather than post-chemotherapy. Age is not reported as a distribution: on inspection, the archive coarsens DICOM age strings to near-uniform values (predominantly "2Y" in AREN0533 and AREN0534, with per-subject variation between timepoints), making any tabulated age distribution misleading; trial enrollment spanned infancy through adolescence [2,3,6]. {SEX_M} subjects were male, {SEX_F} female, and {SEX_O_W} unspecified. By contour labels, {LAT_R} subjects had right-sided, {LAT_L} left-sided, and {LAT_B} bilateral tumor contours; {LAT_U_W} could not be classified from labels. (Unilateral contours within AREN0534 are expected: that trial also enrolled multicentric and bilaterally predisposed unilateral tumors [5].) Baseline and response characteristics by trial are shown in Table 1.

**Table 1:** Baseline and volumetric response characteristics by trial. Values are median (IQR) unless noted. Age is omitted: archive coarsening makes it uninformative (see text). Laterality was unclassifiable for {LAT_U_W} subjects and sex unspecified for {SEX_O_W}, so those rows do not sum to n.

{TABLE1_MD}

### Response by trial (primary analysis)

The three trials used different chemotherapy regimens and schedules, and the archive's date shifting makes the exact scan interval unrecoverable; the first post-chemotherapy timepoint therefore represents a different treatment duration in each trial. We report response per trial, as three protocol-defined profiles. Median percent volume change was {S0532_MED}% in AREN0532 (delayed-nephrectomy subset, n = {S0532_N}), {S0533_MED}% in AREN0533 (stage III–IV disease, n = {S0533_N}), and {S0534_MED}% in AREN0534 (bilateral disease, n = {S0534_N}) (Table 1). Because {BILAT_SHARE}% of the analysis cohort derives from the bilateral-disease trial and the response intervals differ across protocols in ways the de-identified data cannot recover, these profiles are not directly comparable across trials and should be read as three distinct treatment contexts, not one homogeneous Wilms population.

### Pooled estimate (secondary, descriptive)

Across all {N} subjects, median kidney tumor volume was {PRE_MED} mL (IQR {PRE_Q1}–{PRE_Q3}) before chemotherapy and {POST_MED} mL (IQR {POST_Q1}–{POST_Q3}) at the first post-chemotherapy timepoint, a median percent change of {PCT_MED}% (IQR {PCT_Q1}% to {PCT_Q3}%; Hodges–Lehmann estimate {HL_EST}%, 95% CI {HL_LO}% to {HL_HI}%). Volume decreased in {N_DEC} of {N} subjects and increased in {N_INC} (Wilcoxon signed-rank W = {W_STAT}, p {W_P}). This pooled figure averages over heterogeneous, unmeasured response intervals and a cohort dominated by bilateral disease, and is presented as a descriptive summary only. Figure 1 shows the per-subject waterfall distribution; Figure 2 shows volume trajectories across all available chemotherapy timepoints.

## Discussion

That Wilms tumors shrink under neoadjuvant chemotherapy is among the most firmly established facts in pediatric oncology; it is the premise of the SIOP treatment philosophy. What this study adds is not the observation but the quantification: precise, per-protocol volumetric response profiles ({S0532_MED}%, {S0533_MED}%, and {S0534_MED}% median volume reduction in AREN0532, AREN0533, and AREN0534 respectively), computed from expert 3D segmentations in a fully reproducible public pipeline. Prior volumetric work at scale measured post-treatment volume at surgery [19]; the imaging-level response itself has only been quantified in small series. We are explicit about what the present data cannot answer: without stage, histology, or outcomes linkage, these are measurements of how much tumors shrink, not predictors of who benefits.

The magnitude of shrinkage is consistent with the chemosensitivity that underlies both the SIOP preoperative-chemotherapy model and COG's use of neoadjuvant therapy in bilateral and metastatic disease [3,6,11,12]. Histopathologic response after preoperative chemotherapy, the SIOP risk axis, is known to correlate with outcome in bilateral disease, residual tumor volume at nephrectomy has recently been linked to clinical outcomes, and response magnitude itself has been shown to vary with histologic subtype [6,19,23,24]; our imaging-level volumetric response measure is the natural antecedent of these pathology-level observations. Quantitative early response could eventually inform response-adapted strategies, including identification of candidates for nephron-sparing surgery in bilateral disease and early recognition of non-responders [19-21,23].

Two cohort features are worth noting on their own terms. AREN0534 subjects contribute the richest longitudinal series in the dataset, with up to six annotated timepoints per subject under that trial's response-adapted design [6,7]. And AREN0533's renal tumor response accompanies the pulmonary response assessments around which that trial was designed, making its volumetric profile a natural companion to the trial's lung-metastasis endpoints [3,8].

This study has limitations. First, source images are not distributed with the public collections, so analyses requiring voxel data (radiomics, enhancement characteristics, image-contour overlay review) were not possible; volumes derive solely from expert contours. Our cross-validation against the tool-reported DICOM ROI Volume confirms the polygon arithmetic, but it cannot validate the segmentations themselves: contour quality, completeness, and inter-reader consistency are taken on trust from the trials' review process. This matters most for the {N_INC} subjects whose measured volume increased; we cannot distinguish true progression from a differently drawn or incompletely contoured lesion, and we therefore report that subgroup descriptively without biological interpretation. Second, response is indexed to trial timepoints, not time: archive date shifting makes exact scan intervals unrecoverable, intervals almost certainly differ systematically across the three protocols, and we accordingly de-emphasize the pooled estimate. Third, the analyzed cohort is not representative of Wilms tumor generally: {BILAT_SHARE}% of subjects come from the bilateral-disease trial, contouring was performed for trial review rather than randomly, and pre/post pairs may be enriched for cases where response was clinically salient. Fourth, clinical covariates (stage, histology, loss of heterozygosity at 1p/16q, outcomes) are held in the NCI's NCTN/NCORP Data Archive under an application process and were not linked here; trial collection serves as a coarse risk proxy, and the reported associations are descriptive. Fifth, whether the same reader contoured a subject's pre- and post-chemotherapy timepoints is not knowable from the public metadata. Finally, segmentations referencing MRI were excluded from the primary analysis; because these cluster in AREN0534, this exclusion selectively thins the largest subgroup.

Future work should link these volumetric trajectories to the NCTN clinical datasets to test imaging response against stage, histology, and event-free survival, and should evaluate automated segmentation on this benchmark-scale contour library [17,20,26]. Whether imaging non-response, the volume increase seen in {N_INC} subjects, flags unfavorable biology such as anaplasia or blastemal predominance is a hypothesis that only such a linked analysis can test [7,9,24].

## Conclusions

Neoadjuvant chemotherapy produced a substantial reduction in renal tumor volume in each of the three Children's Oncology Group cohorts examined, and the reduction was near-universal: volume fell in the large majority of children and rose in only a small minority. Those three figures are best read as three separate protocol-defined response profiles rather than as one estimate of how Wilms tumor responds. The trials differ in regimen, in schedule, and in the clinical reason preoperative chemotherapy was given at all, and because de-identification makes the interval between scans unrecoverable, the profiles are not directly comparable with one another.

The contribution is a quantitative reference point rather than a new biological claim. Volumetric response measured on imaging is the antecedent of the pathology-level response measures that already guide therapy in bilateral and advanced disease, and expressing it as absolute volume rather than as a response category or a single diameter gives response-adapted trial design something concrete to anchor to. Because the underlying segmentations are public and the analysis is fully scripted, these profiles can be recomputed, criticized, and extended by any reader, and they are a baseline for the linkage to stage, histology, and outcome that the trials' clinical datasets would make possible.



## Code Availability

The complete analysis and rendering pipeline (cohort construction, contour volumetry, statistical analysis, and the renderer that transfers every result statistic from machine output into this manuscript) is publicly available at https://github.com/mmart196/research-tcia-wilms-volumetric and archived at Zenodo (DOI: 10.5281/zenodo.21608439).

## References

{REFERENCES}

---

## Figure Captions

**Fig. 1** Waterfall plot of percent tumor volume change from Pre-dose to the first post-chemotherapy timepoint (n = {N}). Each bar is one subject; bars below zero indicate volume reduction.

**Fig. 2** Kidney tumor volume trajectories on a logarithmic scale across trial timepoints. Each grey line is one subject; the red line is the cohort median.
