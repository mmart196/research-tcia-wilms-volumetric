#!/usr/bin/env python3
"""Predeclared geometry check of exactly the source-verified primary CT target set.
No unavailable geometry is replaced and no partial target sum is used.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from analyze_revision import stratify,quantiles,file_sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parents[1]/'data/revision/output');ap.add_argument('--geometry',type=Path,required=True);args=ap.parse_args();out=args.output_dir
 selected=pd.read_csv(out/'selected_targets_ct.csv',dtype={'series_uid':str,'tracking_uid':str});primary=pd.read_csv(out/'paired_patients_ct.csv');g=pd.read_csv(args.geometry,dtype={'series_uid':str,'metadata_tracking_uid':str})
 selected['roi_key']=pd.to_numeric(selected.verification_raw_roi_number).astype('Int64').astype(str);g['roi_key']=pd.to_numeric(g.raw_roi_number).astype('Int64').astype(str)
 keys=['series_uid','tracking_uid','roi_key'];g=g.rename(columns={'metadata_tracking_uid':'tracking_uid'})
 if g.duplicated(keys).any():raise ValueError('Ambiguous geometry rows for intended target')
 joined=selected.merge(g,on=keys,how='left',suffixes=('','_geometry'),validate='one_to_one')
 joined['geometry_usable']=pd.to_numeric(joined.contour_volume_ml,errors='coerce').gt(0)&np.isfinite(pd.to_numeric(joined.contour_volume_ml,errors='coerce'))&joined.qc_flag.fillna('').eq('')
 joined['geometry_reason']=joined.qc_flag.fillna('')
 joined.loc[joined.contour_volume_ml.isna()&joined.geometry_reason.eq(''),'geometry_reason']='geometry_missing'
 joined.loc[~joined.geometry_usable&joined.geometry_reason.eq(''),'geometry_reason']='nonpositive_or_nonfinite_geometry'
 joined.to_csv(out/'geometry_selected_targets.csv',index=False)
 records=[];omitted=[]
 for pid,q in joined.groupby('patient_id'):
  if not q.geometry_usable.all():
   omitted.append({'patient_id':pid,'collection':q.collection.iloc[0],'reasons':';'.join(sorted(set(q.loc[~q.geometry_usable,'geometry_reason']))),'n_failed_targets':int((~q.geometry_usable).sum())});continue
  a=q[q.timepoint.eq(0)];b=q[q.timepoint.eq(1)];pre=float(a.contour_volume_ml.sum());post=float(b.contour_volume_ml.sum());r=primary[primary.patient_id.eq(pid)].iloc[0].to_dict()
  r['primary_baseline_volume_ml']=r['baseline_volume_ml'];r['primary_followup_volume_ml']=r['followup_volume_ml'];r['primary_percent_change']=r['percent_change']
  r['baseline_volume_ml']=pre;r['followup_volume_ml']=post;r['absolute_change_ml']=post-pre;r['percent_change']=100*(post-pre)/pre;r['difference_percentage_points']=r['percent_change']-r['primary_percent_change'];records.append(r)
 complete=pd.DataFrame(records);omitted=pd.DataFrame(omitted);complete.to_csv(out/'geometry_complete_pairs.csv',index=False);omitted.to_csv(out/'geometry_omitted_pairs.csv',index=False)
 subset=primary[primary.patient_id.isin(complete.patient_id)] if not complete.empty else primary.iloc[:0]
 def diffs(x):
  q1,med,q3=quantiles(x);return {'median':med,'q1':q1,'q3':q3,'min':float(x.min()) if len(x) else None,'max':float(x.max()) if len(x) else None}
 valid_roi=joined[joined.geometry_usable].copy();valid_roi['signed_relative_error_pct']=100*(valid_roi.contour_volume_ml-valid_roi.volume_ml)/valid_roi.volume_ml
 roi_agreement={'eligible_selected_roi_n':len(joined),'computed_roi_n':len(valid_roi),'unavailable_roi_n':int((~joined.geometry_usable).sum()),'qc_flag_counts':{str(k):int(v) for k,v in joined.loc[~joined.geometry_usable,'geometry_reason'].value_counts().items()},'signed_relative_error_pct':diffs(valid_roi.signed_relative_error_pct),'absolute_relative_error_pct':diffs(valid_roi.signed_relative_error_pct.abs()),'n_absolute_relative_error_over_10pct':int(valid_roi.signed_relative_error_pct.abs().gt(10).sum())}
 results=json.loads((out/'results.json').read_text());results['geometry_sensitivity']={'scope':'Numerical recomputation of identical source-verified primary targets; only complete computable pairs; stored archive volume remains primary','geometry_source_sha256':file_sha(args.geometry),'eligible_primary_n':len(primary),'complete_geometry_n':len(complete),'excluded_geometry_n':len(primary)-len(complete),'omitted_patient_reasons':omitted.to_dict('records'),'primary_on_complete_subset':stratify(subset),'geometry_on_complete_subset':stratify(complete),'paired_percentage_difference':diffs(complete.difference_percentage_points) if len(complete) else None,'absolute_paired_percentage_difference':diffs(complete.difference_percentage_points.abs()) if len(complete) else None,'numerical_sign_discordance_n':int((np.sign(complete.percent_change)!=np.sign(complete.primary_percent_change)).sum()) if len(complete) else None,'selected_roi_n':len(joined),'geometry_usable_roi_n':int(joined.geometry_usable.sum()),'roi_agreement':roi_agreement,'geometry_comparison_code_sha256':file_sha(Path(__file__))}
 (out/'results.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'primary_n':len(primary),'geometry_complete_n':len(complete),'geometry_omitted_n':len(primary)-len(complete)}))

if __name__=='__main__':main()
