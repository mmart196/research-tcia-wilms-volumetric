# Current source and analysis quality checks

The revised analysis is documented in data/revision/output/results.json and the dated post-audit amendment. Historical pre-revision QC counts are archived under archive/pre-revision/.

- Current RTSTRUCT source retrieval: 1,143 of 1,143 requested objects succeeded.
- Source-object checks: 1,128 verified intended regions; 15 unresolved records excluded from eligible pairs by the analysis rules.
- Primary CT analysis: 227 patients with 349 matched renal targets (698 ROI-timepoint observations).
- Separate MRI sensitivity: 39 patients; no overlap with the CT cohort.
- Conservative geometric recomputation: 432 of 698 primary ROI-timepoint observations; complete target sets at both visits in 57 of 227 patients.

These checks establish object/metadata consistency and computational sensitivity. They do not independently establish source-image anatomy, complete clinical disease burden, or clinical response. Unsupported polygon topology is a computation limitation, not proof of anatomical segmentation error. All counts regenerate from the committed revision tables and source manifests.
