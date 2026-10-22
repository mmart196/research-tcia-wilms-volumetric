# Source and clinical data availability for the revised analysis

Updated September 22, 2026. The corrected study uses version 2 TCIA metadata and current raw RTSTRUCT annotation objects. Current raw annotation retrieval succeeded in this revision; old claims that cloud retrieval is impossible are superseded.

Raw objects support checks of intended TrackingUID/ROI identity, stored volume, source study/date, referenced series/modality, and contour structure. They do not permit an independent anatomical reread without the referenced CT/MRI voxel images. Source images were not accessed, and the official API rejected a representative source CT request as not in the public domain.

Shifted dates are retained and can preserve longitudinal intervals. The analysis checks chronology but does not equate examination intervals with chemotherapy duration. Patient-level stage, pathology, actual regimen, treatment initiation, surgical dates and outcomes were not linked. Age headers were not treated as a validated clinical age distribution.

The resulting endpoint is change in summed archive-reported volumes of the same evaluable annotated renal target set. It is not total disease volume or a clinical response classification. Full source checks and case-level exclusions are under data/revision/.
