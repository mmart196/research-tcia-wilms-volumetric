# Volumetric Response of Wilms Tumor to Neoadjuvant Chemotherapy Across Three Children's Oncology Group Trials

Rachel Velasco ^1^, Michael Martinez, MD ^2^

1. Washington University of Health and Science, San Pedro, Belize
2. Transitional Year Residency Program, TidalHealth Peninsula Regional, Salisbury, MD, USA

**Corresponding author:** Michael Martinez, MD, michael13414@gmail.com

## Abstract

**Background:** Wilms tumor response to neoadjuvant chemotherapy is usually summarized categorically or by single diameters rather than by three-dimensional volume.

**Objective:** To quantify volumetric response of Wilms tumor to neoadjuvant chemotherapy using publicly available three-dimensional tumor segmentations, reported separately for the three trials in which segmentations are available.

**Materials and Methods:** We used radiologist-reviewed kidney tumor segmentations from three Children's Oncology Group trials (AREN0532, AREN0533, AREN0534) on The Cancer Imaging Archive. Subjects with a pre- and at least one post-chemotherapy segmentation were included; volumes were computed from closed-planar contours and cross-validated against the annotation tool's measurements. Results are reported per trial because chemotherapy schedules differ, with a pooled estimate as secondary.

**Results:** Of 1047 subjects with any kidney segmentation, 259 had computable computed-tomography (CT)-referenced volumes at both timepoints. Median volume change was -86.0% in AREN0532 (delayed-nephrectomy subset, n = 24), -79.9% in AREN0533 (stage III–IV, n = 83), and -71.7% in AREN0534 (bilateral, n = 152); these profiles are not directly comparable because response intervals differ. Pooled, median volume fell from 550.8 mL to 109.7 mL (median change -78.2%; Hodges–Lehmann estimate -71.6%, 95% confidence interval -75.4% to -66.9%), decreasing in 240 of 259 subjects.

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

For each region of interest, slice area was computed from closed-planar contour vertices by the Newell polygon method and multiplied by the median inter-slice spacing; slice volumes were summed to yield tumor volume in milliliters. This is the standard contour-integration approach used in radiotherapy planning and requires no access to source images. As an internal validation, computed volumes were compared with the annotation tool's own per-ROI volume field (DICOM ROI Volume, tag 3006,002C), available for 1141 contoured lesions: agreement was near-perfect (Spearman ρ = 0.998; median absolute difference 4.0%). Crucially, the signed difference was centered at zero in both phases (median 0.7% pre-chemotherapy, 0.4% post-chemotherapy); the larger absolute spread post-chemotherapy (5.6% vs 2.7%) reflects small-lesion spacing sensitivity rather than directional bias, so percent-change estimates are not systematically distorted. Segmentation-based volumetry has previously been shown to be more reproducible than diameter-based measurement in Wilms tumor [25].

### Statistical analysis

Percent volume change was defined as (post − pre)/pre × 100%. Because trial chemotherapy schedules differ and exact intervals are unrecoverable from de-identified data, the primary analysis is descriptive per trial (median, IQR); a pooled Wilcoxon signed-rank comparison with a Hodges–Lehmann estimate and 95% confidence interval is reported secondarily. Prespecified subgroups were the three trials (AREN0532: delayed-nephrectomy subset of a predominantly upfront-surgery trial; AREN0533: stage III–IV disease; AREN0534: bilateral disease). Analyses used Python 3.12 (pydicom, NumPy, pandas, SciPy, matplotlib). A two-sided p < 0.05 was considered significant.

### Reproducibility

The cohort manifest, extraction code, analysis code, and the rendering pipeline that transfers every result statistic from machine-generated output into this manuscript are public (Code Availability); every number in Results regenerates from the public annotation metadata and code. Trials are cited per archive requirements [1-9]. Large-language-model coding assistants were used to write the analysis code and to assist with manuscript drafting, under direct human supervision; all statistics were machine-generated from the public dataset by the published pipeline, and every citation was resolved against PubMed records and verified by the authors, who take full responsibility for the content.

## Results

### Cohort

Annotation metadata contained 1047 subjects with at least one kidney tumor segmentation, of whom 330 had segmentations at both Pre-dose and at least one Post-chemotherapy timepoint. Computable CT-referenced volumes at any timepoint were available for 299 subjects; requiring volumes at both paired timepoints left 259 subjects in the analysis cohort (24 from AREN0532, 83 from AREN0533, 152 from AREN0534). The 71 metadata-paired subjects not analyzed were excluded for prespecified reasons: segmentations referencing only non-CT imaging at a paired timepoint, single-slice or otherwise degenerate contours, annotation series no longer retrievable from the archive (eight series belonging to one subject), and one subject whose only post-treatment segmentation was post-operative rather than post-chemotherapy. Age is not reported as a distribution: on inspection, the archive coarsens DICOM age strings to near-uniform values (predominantly "2Y" in AREN0533 and AREN0534, with per-subject variation between timepoints), making any tabulated age distribution misleading; trial enrollment spanned infancy through adolescence [2,3,6]. 114 subjects were male, 144 female, and one unspecified. By contour labels, 86 subjects had right-sided, 74 left-sided, and 94 bilateral tumor contours; five could not be classified from labels. (Unilateral contours within AREN0534 are expected: that trial also enrolled multicentric and bilaterally predisposed unilateral tumors [5].) Baseline and response characteristics by trial are shown in Table 1.

**Table 1:** Baseline and volumetric response characteristics by trial. Values are median (IQR) unless noted. Age is omitted: archive coarsening makes it uninformative (see text). Laterality was unclassifiable for five subjects and sex unspecified for one, so those rows do not sum to n.

| Characteristic | AREN0532 (n=24) | AREN0533 (n=83) | AREN0534 (n=152) | Overall (n=259) |
|---|---|---|---|---|
| Pre-chemo volume, mL, median (IQR) | 677.6 (443.9–1013.2) | 752.3 (525.7–1035.9) | 380.1 (156.0–667.9) | 550.8 (298.8–864.1) |
| First post-chemo volume, mL, median (IQR) | 91.7 (58.1–192.5) | 160.5 (84.2–276.8) | 83.9 (30.5–221.8) | 109.7 (49.3–251.5) |
| Volume change, %, median (IQR) | -86.0 (-93.5–-73.8) | -79.9 (-86.3–-65.7) | -71.7 (-88.9–-46.4) | -78.2 (-88.7–-54.3) |
| Sex, male/female | 11/13 | 41/42 | 62/89 | 114/144 |
| Laterality, left/right/bilateral | 8/15/1 | 38/42/0 | 28/29/93 | 74/86/94 |

### Response by trial (primary analysis)

The three trials used different chemotherapy regimens and schedules, and the archive's date shifting makes the exact scan interval unrecoverable; the first post-chemotherapy timepoint therefore represents a different treatment duration in each trial. We report response per trial, as three protocol-defined profiles. Median percent volume change was -86.0% in AREN0532 (delayed-nephrectomy subset, n = 24), -79.9% in AREN0533 (stage III–IV disease, n = 83), and -71.7% in AREN0534 (bilateral disease, n = 152) (Table 1). Because 59% of the analysis cohort derives from the bilateral-disease trial and the response intervals differ across protocols in ways the de-identified data cannot recover, these profiles are not directly comparable across trials and should be read as three distinct treatment contexts, not one homogeneous Wilms population.

### Pooled estimate (secondary, descriptive)

Across all 259 subjects, median kidney tumor volume was 550.8 mL (IQR 298.8–864.1) before chemotherapy and 109.7 mL (IQR 49.3–251.5) at the first post-chemotherapy timepoint, a median percent change of -78.2% (IQR -88.7% to -54.3%; Hodges–Lehmann estimate -71.6%, 95% CI -75.4% to -66.9%). Volume decreased in 240 of 259 subjects and increased in 19 (Wilcoxon signed-rank W = 1567, p = 1.1 × 10<sup>-36</sup>). This pooled figure averages over heterogeneous, unmeasured response intervals and a cohort dominated by bilateral disease, and is presented as a descriptive summary only. Figure 1 shows the per-subject waterfall distribution; Figure 2 shows volume trajectories across all available chemotherapy timepoints.

## Discussion

That Wilms tumors shrink under neoadjuvant chemotherapy is among the most firmly established facts in pediatric oncology; it is the premise of the SIOP treatment philosophy. What this study adds is not the observation but the quantification: precise, per-protocol volumetric response profiles (-86.0%, -79.9%, and -71.7% median volume reduction in AREN0532, AREN0533, and AREN0534 respectively), computed from expert 3D segmentations in a fully reproducible public pipeline. Prior volumetric work at scale measured post-treatment volume at surgery [19]; the imaging-level response itself has only been quantified in small series. We are explicit about what the present data cannot answer: without stage, histology, or outcomes linkage, these are measurements of how much tumors shrink, not predictors of who benefits.

The magnitude of shrinkage is consistent with the chemosensitivity that underlies both the SIOP preoperative-chemotherapy model and COG's use of neoadjuvant therapy in bilateral and metastatic disease [3,6,11,12]. Histopathologic response after preoperative chemotherapy, the SIOP risk axis, is known to correlate with outcome in bilateral disease, residual tumor volume at nephrectomy has recently been linked to clinical outcomes, and response magnitude itself has been shown to vary with histologic subtype [6,19,23,24]; our imaging-level volumetric response measure is the natural antecedent of these pathology-level observations. Quantitative early response could eventually inform response-adapted strategies, including identification of candidates for nephron-sparing surgery in bilateral disease and early recognition of non-responders [19-21,23].

Two cohort features are worth noting on their own terms. AREN0534 subjects contribute the richest longitudinal series in the dataset, with up to six annotated timepoints per subject under that trial's response-adapted design [6,7]. And AREN0533's renal tumor response accompanies the pulmonary response assessments around which that trial was designed, making its volumetric profile a natural companion to the trial's lung-metastasis endpoints [3,8].

This study has limitations. First, source images are not distributed with the public collections, so analyses requiring voxel data (radiomics, enhancement characteristics, image-contour overlay review) were not possible; volumes derive solely from expert contours. Our cross-validation against the tool-reported DICOM ROI Volume confirms the polygon arithmetic, but it cannot validate the segmentations themselves: contour quality, completeness, and inter-reader consistency are taken on trust from the trials' review process. This matters most for the 19 subjects whose measured volume increased; we cannot distinguish true progression from a differently drawn or incompletely contoured lesion, and we therefore report that subgroup descriptively without biological interpretation. Second, response is indexed to trial timepoints, not time: archive date shifting makes exact scan intervals unrecoverable, intervals almost certainly differ systematically across the three protocols, and we accordingly de-emphasize the pooled estimate. Third, the analyzed cohort is not representative of Wilms tumor generally: 59% of subjects come from the bilateral-disease trial, contouring was performed for trial review rather than randomly, and pre/post pairs may be enriched for cases where response was clinically salient. Fourth, clinical covariates (stage, histology, loss of heterozygosity at 1p/16q, outcomes) are held in the NCI's NCTN/NCORP Data Archive under an application process and were not linked here; trial collection serves as a coarse risk proxy, and the reported associations are descriptive. Fifth, whether the same reader contoured a subject's pre- and post-chemotherapy timepoints is not knowable from the public metadata. Finally, segmentations referencing MRI were excluded from the primary analysis; because these cluster in AREN0534, this exclusion selectively thins the largest subgroup.

Future work should link these volumetric trajectories to the NCTN clinical datasets to test imaging response against stage, histology, and event-free survival, and should evaluate automated segmentation on this benchmark-scale contour library [17,20,26]. Whether imaging non-response, the volume increase seen in 19 subjects, flags unfavorable biology such as anaplasia or blastemal predominance is a hypothesis that only such a linked analysis can test [7,9,24].

## Conclusions

Neoadjuvant chemotherapy produced a substantial reduction in renal tumor volume in each of the three Children's Oncology Group cohorts examined, and the reduction was near-universal: volume fell in the large majority of children and rose in only a small minority. Those three figures are best read as three separate protocol-defined response profiles rather than as one estimate of how Wilms tumor responds. The trials differ in regimen, in schedule, and in the clinical reason preoperative chemotherapy was given at all, and because de-identification makes the interval between scans unrecoverable, the profiles are not directly comparable with one another.

The contribution is a quantitative reference point rather than a new biological claim. Volumetric response measured on imaging is the antecedent of the pathology-level response measures that already guide therapy in bilateral and advanced disease, and expressing it as absolute volume rather than as a response category or a single diameter gives response-adapted trial design something concrete to anchor to. Because the underlying segmentations are public and the analysis is fully scripted, these profiles can be recomputed, criticized, and extended by any reader, and they are a baseline for the linkage to stage, histology, and outcome that the trials' clinical datasets would make possible.



## Code Availability

The complete analysis and rendering pipeline (cohort construction, contour volumetry, statistical analysis, and the renderer that transfers every result statistic from machine output into this manuscript) is publicly available at https://github.com/mmart196/research-tcia-wilms-volumetric and archived at Zenodo (DOI: 10.5281/zenodo.21608439).

## References

1. Clark K, Vendt B, Smith K, Freymann J, Kirby J, Koppel P et al. The Cancer Imaging Archive (TCIA): maintaining and operating a public information repository. J Digit Imaging. 2013;26(6):1045-57. doi:10.1007/s10278-013-9622-7 PMID: 23884657
2. Fernandez CV, Mullen EA, Chi YY, Ehrlich PF, Perlman EJ, Kalapurakal JA et al. Outcome and Prognostic Factors in Stage III Favorable-Histology Wilms Tumor: A Report From the Children's Oncology Group Study AREN0532. J Clin Oncol. 2018;36(3):254-261. doi:10.1200/JCO.2017.73.7999 PMID: 29211618
3. Dix DB, Seibel NL, Chi YY, Khanna G, Gratias E, Anderson JR et al. Treatment of Stage IV Favorable Histology Wilms Tumor With Lung Metastases: A Report From the Children's Oncology Group AREN0533 Study. J Clin Oncol. 2018;36(16):1564-1570. doi:10.1200/JCO.2017.77.1931 PMID: 29659330
4. Dix DB, Fernandez CV, Chi YY, Mullen EA, Geller JI, Gratias EJ et al. Augmentation of Therapy for Combined Loss of Heterozygosity 1p and 16q in Favorable Histology Wilms Tumor: A Children's Oncology Group AREN0532 and AREN0533 Study Report. J Clin Oncol. 2019;37(30):2769-2777. doi:10.1200/JCO.18.01972 PMID: 31449468
5. Ehrlich PF, Chi YY, Chintagumpala MM, Hoffer FA, Perlman EJ, Kalapurakal JA et al. Results of Treatment for Patients With Multicentric or Bilaterally Predisposed Unilateral Wilms Tumor (AREN0534): A report from the Children's Oncology Group. Cancer. 2020;126(15):3516-3525. doi:10.1002/cncr.32958 PMID: 32459384
6. Chintagumpala MM, Perlman EJ, Tornwall B, Chi YY, Kim Y, Hoffer FA et al. Outcomes based on histopathologic response to preoperative chemotherapy in children with bilateral Wilms tumor: A prospective study (COG AREN0534). Cancer. 2022;128(13):2493-2503. doi:10.1002/cncr.34219 PMID: 35383900
7. Romao RLP, Aldrink JH, Renfro LA, Mullen EA, Murphy AJ, Brzezinski J et al. Bilateral Wilms tumor with anaplasia: A report from the Children's Oncology Group Study AREN0534. Pediatr Blood Cancer. 2024;71(7):e30981. doi:10.1002/pbc.30981 PMID: 38637871
8. Dix DB, Khanna G, Renfro LA, Tfirn IC, Smith EA, Artunduaga M et al. Impact of Pulmonary Tumor Burden in Favorable Histology Wilms Tumor Outcomes: A Report From the Children's Oncology Group Study AREN0533. J Clin Oncol. 2025;43(36):3822-3832. doi:10.1200/JCO-25-00532 PMID: 41223336
9. Evageliou N, Renfro LA, Geller J, Perlman E, Kalapurakal J, Paulino A et al. Prognostic impact of lymph node involvement and loss of heterozygosity of 1p or 16q in stage III favorable histology Wilms tumor: A report from Children's Oncology Group Studies AREN03B2 and AREN0532. Cancer. 2024;130(5):792-802. doi:10.1002/cncr.35084 PMID: 37902955
10. Irtan S, Ehrlich PF, Pritchard-Jones K. Wilms tumor: "State-of-the-art" update, 2016. Semin Pediatr Surg. 2016;25(5):250-256. doi:10.1053/j.sempedsurg.2016.09.003 PMID: 27955727
11. Brok J, Treger TD, Gooskens SL, van den Heuvel-Eibrink MM, Pritchard-Jones K. Biology and treatment of renal tumours in childhood. Eur J Cancer. 2016;68:179-195. doi:10.1016/j.ejca.2016.09.005 PMID: 27969569
12. Graf N, Furtwängler R. Preoperative chemotherapy and local stage III in nephroblastoma. Transl Pediatr. 2014;3(1):4-11. doi:10.3978/j.issn.2224-4336.2013.12.02 PMID: 26835317
13. Aldrink JH, Heaton TE, Dasgupta R, Lautz TB, Malek MM, Abdessalam SF et al. Update on Wilms tumor. J Pediatr Surg. 2019;54(3):390-397. doi:10.1016/j.jpedsurg.2018.09.005 PMID: 30270120
14. Benedetti DJ, Cost NG, Ehrlich PF, Evageliou N, Fialkowski E, Parsons LN et al. Updated favourable-histology Wilms tumour risk stratification: rationale for future Children's Oncology Group clinical trials. Nat Rev Urol. 2025;22(11):775-788. doi:10.1038/s41585-025-01055-1 PMID: 40542227
15. Breslow N, Olshan A, Beckwith JB, Green DM. Epidemiology of Wilms tumor. Med Pediatr Oncol. 1993;21(3):172-81. doi:10.1002/mpo.2950210305 PMID: 7680412
16. Brisse HJ, Smets AM, Kaste SC, Owens CM. Imaging in unilateral Wilms tumour. Pediatr Radiol. 2008;38(1):18-29. doi:10.1007/s00247-007-0677-9 PMID: 18038168
17. Jain J, Sutton KS, Hong AL. Progress Update in Pediatric Renal Tumors. Curr Oncol Rep. 2021;23(3):33. doi:10.1007/s11912-021-01016-y PMID: 33591402
18. von Reppert M, Ramakrishnan D, Brüningk SC, Memon F, Abi Fadel S, Maleki N et al. Comparison of volumetric and 2D-based response methods in the PNOC-001 pediatric low-grade glioma clinical trial. Neurooncol Adv. 2024;6(1):vdad172. doi:10.1093/noajnl/vdad172 PMID: 38221978
19. Furtwängler R, Dandis R, van Tinteren H, Welter N, Vokuhl C, Vujanic G et al. Residual Absolute Volume of Blastema as a Predictor of Clinical Outcomes in Patients With Wilms Tumor: A Report From the SIOP WT 2001 Study. J Clin Oncol. 2026;44(13):1238-1248. doi:10.1200/JCO-25-01755 PMID: 41824924
20. Nashat A, Alksas A, Aboulelkheir RT, Elmahdy A, Khater SM, Balaha HM et al. Artificial intelligence can help individualize Wilms tumor treatment by predicting tumor response to preoperative chemotherapy. Investig Clin Urol. 2025;66(1):47-55. doi:10.4111/icu.20240135 PMID: 39791584
21. Mergen M, Graf N, Welter N, Melchior P, Vokuhl C, Schmidt A et al. Efficacy of Preoperative Chemotherapy in Patients With Nephroblastoma and Imaging Findings Suggestive of Preoperative Tumor Rupture. Pediatr Blood Cancer. 2026;73(1):e32111. doi:10.1002/pbc.32111 PMID: 41069077
22. Fernandez CV, Perlman EJ, Mullen EA, Chi YY, Hamilton TE, Gow KW et al. Clinical Outcome and Biological Predictors of Relapse After Nephrectomy Only for Very Low-risk Wilms Tumor: A Report From Children's Oncology Group AREN0532. Ann Surg. 2017;265(4):835-840. doi:10.1097/SLA.0000000000001716 PMID: 27811504
23. Duncan C, Sarvode Mothi S, Santiago TC, Coggins JA, Graetz DE, Bishop MW et al. Response of bilateral Wilms tumor to chemotherapy suggests histologic subtype and guides treatment. J Natl Cancer Inst. 2024;116(8):1230-1237. doi:10.1093/jnci/djae072 PMID: 38539045
24. Taskinen S, Leskinen O, Lohi J, Koskenvuo M, Taskinen M. Effect of Wilms tumor histology on response to neoadjuvant chemotherapy. J Pediatr Surg. 2019;54(4):771-774. doi:10.1016/j.jpedsurg.2018.05.010 PMID: 29887169
25. Buser MAD, van der Steeg AFW, Wijnen MHWA, Fitski M, van Tinteren H, van den Heuvel-Eibrink MM et al. Radiologic versus Segmentation Measurements to Quantify Wilms Tumor Volume on MRI in Pediatric Patients. Cancers (Basel). 2023;15(7). doi:10.3390/cancers15072115 PMID: 37046776
26. Buser MAD, de Groot NT, Simons DC, Littooij AS, Wijnen MHWA, van de Ven CP et al. Deep learning-based Wilms tumor segmentation to create 3D models for surgical planning: Implementation in the clinical workflow. J Pediatr Surg. 2026;61(7):163151. doi:10.1016/j.jpedsurg.2026.163151 PMID: 42044738
27. Benlhachemi S, Khattab M, Hattoufi K, Abouqal R, El Fahime E. Impact of neoadjuvant chemotherapy on tumour volume in unilateral Wilms tumour histotypes: a retrospective study. BMC Cancer. 2025;25(1):1031. doi:10.1186/s12885-025-14177-x PMID: 40597778

---

## Figure Captions

**Fig. 1** Waterfall plot of percent tumor volume change from Pre-dose to the first post-chemotherapy timepoint (n = 259). Each bar is one subject; bars below zero indicate volume reduction.

**Fig. 2** Kidney tumor volume trajectories on a logarithmic scale across trial timepoints. Each grey line is one subject; the red line is the cohort median.
