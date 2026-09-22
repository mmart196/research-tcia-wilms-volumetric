# Longitudinal Volumetry of Annotated Renal Target Lesions in Three Children's Oncology Group Trial Archives

Rachel Velasco¹ and Michael Martinez²

¹ Medical School, Washington University of Health and Science, San Pedro, Belize

² Transitional Year Residency Program, TidalHealth Peninsula Regional, Salisbury, Maryland, USA

Corresponding author: Michael Martinez, michael13414@gmail.com

## Abstract

**Background:** Public tumor annotations permit secondary measurement studies, but longitudinal analyses require consistent lesion identity, examination selection, and data provenance.

**Objective:** To describe changes in the recorded volumes of matched renal target lesions in three Children's Oncology Group trial archives.

**Materials and Methods:** We analyzed the corrected version 2 annotation releases for AREN0532, AREN0533, and AREN0534. The primary analysis required computed tomography (CT) at baseline and the first numbered follow-up, one examination per visit, identical renal tracking identifiers and compatible labels, and verification of each intended region against its source annotation object. The endpoint was percentage change in summed archive-reported target volume. Collection-specific medians and nonparametric 95% confidence intervals (CIs) were calculated. Magnetic resonance imaging (MRI) pairs and CT pairs separated by no more than 90 days were evaluated separately.

**Results:** @@ABSTRACT_RESULTS@@

**Conclusions:** The retained annotation pairs showed substantial decreases in recorded renal target volume. These measurements describe selected matched lesions; clinical response, treatment efficacy, and prognostic utility require source-image and clinical validation.

**Keywords:** renal tumor volumetry; Wilms tumor; pediatric radiology; lesion tracking; imaging annotations; longitudinal imaging

## Introduction

Wilms tumor treatment combines surgery and systemic therapy, with the sequence and intensity determined by the clinical setting [[wilms_review]]. The Children's Oncology Group studies AREN0532, AREN0533, and AREN0534 represent different treatment populations. AREN0532 included patients with stage III favorable-histology disease, some of whom underwent delayed nephrectomy, whereas AREN0533 investigated treatment strategies for higher-risk disease, including response-adapted management of pulmonary metastases [[aren0532_stage3,aren0533_lung]]. AREN0534 included bilateral Wilms tumor, multicentric or bilaterally predisposed unilateral tumors, and diffuse hyperplastic perilobar nephroblastomatosis [[aren0534_bilateral,aren0534_predisposed,aren0534_dhpln]]. Membership in one of these archives therefore does not by itself establish an individual patient's diagnosis, treatment regimen, surgical status, or response-assessment interval.

Paired tumor-volume measurements before and after preoperative chemotherapy have previously been reported in both large cooperative-group cohorts and smaller institutional studies. The SIOP 93-01 analysis included 594 patients and reported tumor volume at diagnosis and after preoperative chemotherapy [[siop9301]]. Studies of 52 patients with Wilms tumor, 68 patients with bilateral disease, and 56 patients with unilateral disease further examined volume change in relation to histology [[taskinen,duncan,benlhachemi]]. Measurement methods differ: dimensions-based estimates and segmentation-derived volumes need not agree, as demonstrated in a pediatric Wilms tumor MRI study [[buser_volume]]. These reports establish an existing literature on volumetric change rather than a previously unstudied phenomenon.

The Cancer Imaging Archive provides a separate opportunity to examine expert annotations in a reproducible secondary analysis [[tcia]]. Its AREN0532, AREN0533, and AREN0534 annotation datasets contain renal target-lesion contours created in a later annotation project and distributed with structured metadata [[annotation0532,annotation0533,annotation0534]]. We evaluated longitudinal changes in annotated renal target-lesion volume using the current metadata and annotation releases, with explicit checks of lesion selection, timepoint labels, and computational measurement. The aim was to describe the information supported by these archives and its limitations, rather than estimate treatment efficacy or validate a clinical response threshold.

## Materials and Methods

### Design and source data

This retrospective secondary analysis used publicly available, de-identified annotation objects and metadata retrieved on September 22, 2026. The corrected metadata releases were dated December 3, December 19, and December 22, 2025, for AREN0532, AREN0533, and AREN0534, respectively. The source files, retrieval addresses, and checksums were retained. The analysis plan was amended after a data-quality review of an earlier implementation whose results had already been examined. The dated amendment specified the revised endpoint, matching rules, and statistical presentation before the revised aggregate outcomes were calculated; it was not a prospectively registered protocol.

The analysis used version 2 of the AREN0532-Tumor-Annotations, AREN0533-Tumor-Annotations, and AREN0534-Tumor-Annotations datasets [[annotation0532,annotation0533,annotation0534]]. These annotations were created after the underlying trials to augment the archived imaging collections [[image0532,image0533,image0534]]. The dataset documentation describes initial annotation by radiologists followed by secondary review by US board-certified radiologists. The stated target-selection protocol allowed up to five lesions per scan and no more than two per organ, with longitudinal annotation of the selected targets. The endpoint is therefore the volume of selected annotated renal lesions, not the total volume of all renal disease. The archive's annotation protocol used RECIST 1.1 principles for target selection, but our volume-change endpoint is not a RECIST response classification [[recist]].

No participants were recruited or contacted, and no identifiable private information was accessed. No institutional review board reviewed this secondary analysis, and no institutional approval or exemption number was issued. Source CT/MRI voxel images were not accessed, so no image-based rereading or independent confirmation of segmentation boundaries was performed.

### Examination and target selection

All subjects with at least one renal segmentation in the current metadata were screened. The primary analysis used CT-referenced renal segmentations at Pre-Dose and Post-Chemotherapy #1. Later numbered visits were not substituted when the first follow-up was missing. Eligibility required one source StudyInstanceUID and date at each visit, a strictly positive interval, and the same complete set of renal TrackingUIDs with compatible normalized target labels and laterality. Multiple CT series from one examination could contribute distinct targets, but each tracked target could contribute only one annotation per visit. Repeated target measurements and examinations from different dates were not summed.

Eligibility was checked against current RTSTRUCT objects. A unique intended region of interest (ROI) was located by its TrackingUID. The ROI name and tracking label had to be compatible with the metadata, and the patient identifier, source examination/date, referenced image series and modality, and stored ROI volume had to agree. An omitted numeric suffix in an ROI name was allowed only when its unique TrackingUID and explicitly stated kidney side matched; conflicting anatomy, sides, or numeric suffixes were not reconciled by inference. Unrelated or untracked ROIs in the same object were ignored. Seed-only objects, malformed intended contour-coordinate records, unresolved anatomical labels, and source-identity conflicts were excluded. Coordinate checks rejected nonclosed contours, fewer than three points, nonfinite or nonnumeric coordinates, and inconsistent declared point counts. Single-plane segmentations with a valid stored ROI volume could enter the primary analysis; they were not assigned an inferred slice thickness for geometric recomputation. One duplicated patient-identifier string was normalized using the matching raw patient header and retained series identifiers.

Historical metadata were used to detect annotation or source-series identifiers previously labeled postoperative or recurrent. Such conflicts were excluded from the required visits. Mutually exclusive first-failure exclusions were recorded for each patient. A missing annotation, a negative assessment, or a failed measurement was never assigned zero volume. All retained baseline targets had to be represented at follow-up; the endpoint therefore concerns persistent, evaluable target sets and may omit complete responders. The archive's shifted dates preserve longitudinal relationships, but calculated examination intervals were not interpreted as treatment duration. Treatment initiation, actual regimen, pathology, and surgical dates were not linked.

### Volume measurements and sensitivity analyses

The primary measurement was the intended ROI's archived DICOM ROI Volume value (tag 3006,002C), expressed in cubic centimeters, equivalent to milliliters. Its value was checked against the current metadata. For each retained patient, the same renal target set was summed at both visits. Percentage change was calculated as 100 × (follow-up volume − baseline volume) / baseline volume. A numerical increase was not classified as clinical progression, and these volumetric changes were not assigned RECIST response categories.

MRI-to-MRI pairs were analyzed separately using the same rules. A CT sensitivity analysis was restricted to examination intervals of 90 days or less, chosen before revised outcome calculation to assess the influence of longer intervals around the six- and 12-week assessment schedules described in the source trials [[aren0533_lung,aren0534_bilateral]]. This restriction did not establish when treatment began or whether surgery occurred.

A computational sensitivity analysis compared archived volumes with volumes recomputed from the verified intended ROI contours. Polygons were projected onto a common plane basis and grouped by physical plane. Disjoint closed planar polygons were summed; explicit DICOM exclusive-or contours were combined using the corresponding topology. Ordinary overlapping/nested polygons, polygon topology unsupported by the conservative routine, nonparallel planes, and irregular plane spacing were excluded from recomputation. Unsupported topology can include self-intersecting or keyhole encodings and does not establish anatomical inaccuracy of the supplied segmentation. For uniformly spaced valid planes, summed areas were multiplied by spacing, including a half-spacing end extension at each end. This is a slab approximation. Comparisons included absolute and relative volume differences and patient-level percentage-change differences, restricted to patients whose complete matched target set was computable. These checks assess computational consistency within supplied annotations and do not validate their anatomical accuracy.

### Statistical analysis and reproducibility

The patient was the analysis unit. Results were reported separately for each collection as medians and interquartile ranges (IQRs). Nonparametric confidence intervals for median percentage change used central order statistics with exact binomial coverage of at least 95%; finite intervals were reported as not estimable when sample size was insufficient. These intervals assume independent patient observations and do not account for archive selection bias. Pooled results were descriptive. No between-collection treatment-effect tests or outcome-prediction models were fitted. Neither a pooled significance test nor correlation between volume methods was used as evidence of clinical validity. Age, stage, histology, and clinical outcomes were not analyzed because reliable patient-level clinical data were not linked.

The analysis used Python with NumPy, pandas, SciPy, pydicom, Shapely, and matplotlib. Exact software versions, the dated amendment, source verification records, patient-level inclusion/exclusion tables, and reproducible calculations accompany the analysis. @@CODE_AVAILABILITY@@

Large-language-model assistants were used in developing the analysis code and manuscript. This revision used ChatGPT and OpenAI Codex (OpenAI) for literature retrieval, code review and revision, source-data checks, statistical scripting, and manuscript drafting. Bibliographic identities were checked against PubMed and DataCite, and quantitative results were generated by scripted calculations. These procedures do not constitute independent clinical review or image-based confirmation of lesion identity. Responsibility for scientific decisions and final content remains with the human authors.

## Results

### Cohort selection

@@COHORT_RESULTS@@

**Table 1. Selection of the primary CT cohort.** Each excluded patient is counted once, at the first failed eligibility step. CT, computed tomography; ROI, region of interest.

@@FLOW_TABLE@@

### Matched renal target volumes

@@PRIMARY_RESULTS@@

**Table 2. Matched renal target volume changes by collection.** Values are median (IQR) unless indicated. Confidence intervals refer to the median of patient-level percentage changes. Pooled estimates are descriptive. CT, computed tomography; CI, confidence interval; IQR, interquartile range.

@@PRIMARY_TABLE@@

@@POOLED_RESULTS@@

**Figure 1. Percentage changes in matched renal target volume in the primary CT cohort.** Each bar represents one patient, sorted within collection. Negative values indicate a decrease in recorded volume. The full observed range is displayed. Collection sample sizes are shown above each panel. CT, computed tomography.

@@FIGURE1@@

**Figure 2. Paired renal target volumes in the primary CT cohort.** Each colored line connects the baseline and first numbered follow-up volumes for one patient with the same target set at both visits. The black line and diamond markers show the marginal median at each visit. The vertical axis is logarithmic. These are two observations per patient, not trajectories through intermediate visits. CT, computed tomography.

@@FIGURE2@@

### Timing and measurement sensitivities

@@SENSITIVITY_RESULTS@@

**Table 3. Sensitivity analyses by collection.** CT pairs within 90 days are a subset of the primary cohort. MRI pairs were selected independently with the same matching and verification rules. Values are median (IQR) unless indicated. CI, confidence interval; CT, computed tomography; IQR, interquartile range; MRI, magnetic resonance imaging.

@@SENSITIVITY_TABLE@@

@@GEOMETRY_RESULTS@@

## Discussion

@@DISCUSSION_FINDING@@

This analysis concerns longitudinal measurements of selected annotated renal lesions in trial-derived archives. Its unit of observation and target-selection rules differ from those of a prospective therapeutic study. The findings should be interpreted as changes in recorded target-lesion volume among evaluable annotation pairs. They do not establish how much all renal disease changed, whether a patient achieved a clinical response, or whether one treatment strategy was more effective than another.

The contribution is an auditable secondary measurement analysis. Earlier studies already demonstrated preoperative volume changes in Wilms tumor, including the large SIOP 93-01 cohort and institutional series with histologic information [[siop9301,taskinen,duncan,benlhachemi]]. Differences between those studies and the present analysis include target selection, lesion matching, imaging methods, treatment setting, and timing. Their numerical response estimates should not be compared as estimates of relative treatment efficacy. A public contour-based analysis complements this literature by making eligibility decisions and calculations inspectable; reproducibility alone does not establish clinical validity.

Several features constrain interpretation. First, the annotation protocol selected targets and did not comprehensively delineate every lesion [[annotation0532,annotation0533,annotation0534]]. Requiring a lesion to be evaluable at both timepoints can preferentially retain visible or persistent lesions. An absent annotation cannot be assumed to represent complete resolution. Similarly, adding available lesions at each visit without confirming correspondence can confound biological change with a changing target set. Label-based correspondence is an operational matching rule; it does not independently prove anatomical identity on the original images.

Second, contour-derived volume depends on the segmentation boundaries and on how contour planes are integrated. Agreement with a volume stored by the annotation software checks numerical consistency within the same annotation, not the accuracy of the boundary against anatomy. Rank correlation alone does not measure agreement. Dimensions-based and segmentation-derived measurements have differed in prior Wilms tumor studies, so measurement method must remain explicit when results are compared [[buser_volume]]. The current analysis does not establish interobserver or intraobserver reproducibility. The complete-pair geometric sensitivity subset was substantially smaller than the primary cohort, so its agreement results cannot be generalized to all retained annotations.

Third, the source trials enrolled heterogeneous clinical populations [[aren0532_stage3,aren0533_lung,aren0534_bilateral,aren0534_predisposed,aren0534_dhpln]]. Without patient-level clinical linkage, collection names cannot substitute for stage, histology, regimen, surgical timing, or confirmed bilateral disease. Archive-relative imaging intervals, where available, describe recorded imaging chronology and should not be equated with treatment duration without treatment dates. Comparisons across collections remain descriptive even when scan intervals can be calculated.

Fourth, an increase in recorded volume is not sufficient to identify adverse histology. An earlier bilateral Wilms tumor series associated growth with stromal-predominant tumors, whereas a smaller mixed cohort found anaplasia in two of three tumors that enlarged by more than 10% [[duncan,taskinen]]. Whole-lesion volume also differs from residual viable blastema volume, which combines imaging and pathological information and has been studied as an outcome-associated marker [[residual_blastema]]. The present annotations cannot determine those tissue components or support treatment recommendations.

Further investigation would require source-image review, confirmation of lesion correspondence and completeness, and linkage to clinical treatment, pathology, and outcome data. Such validation should precede any proposed response threshold or use in surgical or treatment planning. Reporting the present measurements with their eligibility rules and limitations provides a basis for that work without treating archive-derived volume change as a validated surrogate endpoint.

## Conclusions

Trial-derived renal target-lesion annotations can support a transparent analysis of longitudinal volumetric measurements when data versions, lesion correspondence, and timepoint definitions are explicit. The resulting endpoint describes selected annotated lesions and cannot be assumed to represent total renal tumor burden or a clinical response category.

Interpretation remains limited by annotation selection and the absence of patient-level treatment, pathology, and outcome linkage. The measurements are suitable for methodological and descriptive research; their clinical significance requires independent validation.

## Acknowledgments

The authors acknowledge the Children's Oncology Group trial investigators, the annotation creators, and The Cancer Imaging Archive for making the research resources available.

## References

@@REFERENCES@@
