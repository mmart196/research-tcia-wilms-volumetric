#!/usr/bin/env python3
"""Locked post-audit matched-target analysis of current TCIA renal annotations.

Run --prepare-verification to create candidate target/object lists without computing
outcomes. Final output requires a locked amendment and source verification manifest.
The endpoint is archived intended-ROI volume, not clinical treatment response.
"""
from __future__ import annotations
import argparse, hashlib, json, platform, re
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import scipy
from scipy import stats

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/revision/metadata'
OUT=ROOT/'data/revision/output'
COLLECTIONS=['AREN0532','AREN0533','AREN0534']
CURRENT={
 'AREN0532':'Metadata_Report_AREN0532_2025-12-03-1.csv',
 'AREN0533':'Metadata_Report_AREN0533_2025-12-19.csv',
 'AREN0534':'Metadata_Report_AREN0534_2025-12-22.csv',
}
REASONS=[
 ('no_baseline_modality_annotation','No baseline renal segmentation in selected modality'),
 ('no_followup1_modality_annotation','No follow-up #1 renal segmentation in selected modality'),
 ('historical_postoperative_recurrence_conflict','Historical postoperative/recurrence label conflict'),
 ('invalid_required_metadata_or_volume','Missing/invalid identity, date, source, label or positive volume'),
 ('ambiguous_examination','Multiple source examinations/dates in a selected visit'),
 ('repeated_target_annotation','Repeated target annotation within a selected visit'),
 ('unmatched_target_set_or_labels','Different renal tracking sets or incompatible target labels'),
 ('nonpositive_examination_interval','Follow-up examination not after baseline'),
 ('source_object_not_verified','Source ROI identity/volume verification unresolved'),
 ('included','Included matched-target pair'),
]

def textcol(df,col):
 return df[col].fillna('').astype(str).str.strip()

def canonical_patient(x):
 x=str(x).strip()
 if x=='AREN0532-PAURIYAREN0532-PAURIY':return 'AREN0532-PAURIY'
 return x

def parse_date(x):
 """Preserve archive 19xx two-digit shifted dates; no OS century pivot."""
 s=str(x).strip()
 try:
  parts=s.split('/')
  if len(parts)!=3:return pd.NaT
  if len(parts[0])==4:y,m,d=map(int,parts)
  else:
   m,d,y=map(int,parts)
   if y<100:y+=1900
  return pd.Timestamp(y,m,d)
 except (ValueError,OverflowError):return pd.NaT

def normalized_label(x):
 s=str(x).upper().strip()
 s=re.sub(r'\b(?:LEFT|LT|L)\b','LEFT',s)
 s=re.sub(r'\b(?:RIGHT|RT|R)\b','RIGHT',s)
 return ' '.join(re.findall(r'[A-Z]+|\d+',s))

def raw_roi_label_compatible(raw_name,tracking_label):
 roi=normalized_label(raw_name)
 if roi==tracking_label:return True
 bare=re.fullmatch(r'(LEFT|RIGHT) KIDNEY',roi)
 numbered=re.fullmatch(r'(LEFT|RIGHT) KIDNEY (\d+)',tracking_label)
 return bool(bare and numbered and bare.group(1)==numbered.group(1))

def side(x):
 s=normalized_label(x)
 l=bool(re.search(r'\bLEFT\b',s));r=bool(re.search(r'\bRIGHT\b',s))
 return 'bilateral' if l and r else 'left' if l else 'right' if r else 'unspecified'

def file_sha(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_metadata():
 frames=[];manifest=[];crosswalk=[]
 for collection,name in CURRENT.items():
  p=DATA/name;df=pd.read_csv(p,encoding='latin1')
  manifest.append({'collection':collection,'filename':name,'sha256':file_sha(p),'rows':len(df)})
  df['collection']=collection
  for col in ['PatientID','SeriesInstanceUID','StudyInstanceUID','StudyDate','TrackingID','TrackingUID','ClinicalTrialTimePointID','AnnotationType','ReferencedSeriesInstanceUID','ReferencedSeriesModality']:
   df[col]=textcol(df,col)
  df['patient_id_original']=df.PatientID
  df['patient_id']=df.PatientID.map(canonical_patient)
  crosswalk.extend(df.loc[df.patient_id!=df.PatientID,['collection','patient_id_original','patient_id','SeriesInstanceUID']].to_dict('records'))
  df['series_uid']=df.SeriesInstanceUID
  df['tracking_uid']=df.TrackingUID
  df['tracking_label']=df.TrackingID.map(normalized_label)
  df['laterality']=df.TrackingID.map(side)
  df['scan_date']=df.StudyDate.map(parse_date)
  df['modality']=df.ReferencedSeriesModality.str.upper()
  df['timepoint']=df.ClinicalTrialTimePointID.str.lower().str.strip().map({'pre-dose':0,**{f'post-chemotherapy #{i}':i for i in range(1,7)}})
  df['stored_metadata_volume_ml']=pd.to_numeric(df.ROIVolume,errors='coerce')
  frames.append(df)
 m=pd.concat(frames,ignore_index=True)
 m['is_renal_seg']=m.AnnotationType.str.lower().eq('segmentation')&m.TrackingID.str.contains(r'\bKIDNEY\b',case=False,na=False)
 # Preserve historical conflicts both for the annotation object and same patient/source series.
 conflict_series=set();conflict_source=set()
 for collection in COLLECTIONS:
  old=pd.read_csv(DATA/f'historical_Metadata_Report_{collection}.csv')
  bad=old.ClinicalTrialTimePointID.str.contains('operative|recurrence',case=False,na=False)
  for r in old.loc[bad].itertuples():
   conflict_series.add(str(r.SeriesInstanceUID).strip())
   conflict_source.add((canonical_patient(r.PatientID),str(r.ReferencedSeriesInstanceUID).strip()))
 m['historical_conflict']=[r.series_uid in conflict_series or (r.patient_id,r.ReferencedSeriesInstanceUID) in conflict_source for r in m.itertuples()]
 return m,manifest,crosswalk

def load_verification(path):
 if not path.exists():return {}
 v=pd.read_csv(path,dtype=str).fillna('')
 required={'series_uid','metadata_tracking_uid','status','raw_roi_volume_ml','raw_roi_number'}
 if not required<=set(v.columns):raise ValueError(f'verification missing columns: {required-set(v.columns)}')
 if v.duplicated(['series_uid','metadata_tracking_uid']).any():raise ValueError('Duplicate verification keys require explicit source review')
 return {(r['series_uid'].strip(),r['metadata_tracking_uid'].strip()):r for r in v.to_dict('records')}

def verify_rows(q,verification):
 validated=[];failures=[]
 for _,r in q.iterrows():
  key=(r.series_uid,r.tracking_uid);vr=verification.get(key)
  if vr is None:failures.append(f'{r.series_uid}:missing_source_check');continue
  if vr.get('status','')!='verified':failures.append(f"{r.series_uid}:{vr.get('status')}:{vr.get('reasons','')}");continue
  try:rawvol=float(vr['raw_roi_volume_ml'])
  except ValueError:rawvol=np.nan
  if not np.isfinite(rawvol) or rawvol<=0 or not np.isclose(rawvol,r.stored_metadata_volume_ml,rtol=1e-9,atol=1e-6):
   failures.append(f'{r.series_uid}:stored_volume_disagreement');continue
  # Source verifier checks morphology, raw/metadata identity, date, modality and references.
  # Repeat identity checks here to prevent a manifest belonging to a different data snapshot.
  if canonical_patient(vr.get('raw_patient_id',''))!=r.patient_id:
   failures.append(f'{r.series_uid}:raw_patient_mismatch');continue
  if vr.get('raw_study_uid','').strip()!=r.StudyInstanceUID:
   failures.append(f'{r.series_uid}:raw_study_mismatch');continue
  if vr.get('raw_study_date','').strip()!=r.scan_date.strftime('%Y-%m-%d'):
   failures.append(f'{r.series_uid}:raw_date_mismatch');continue
  if vr.get('raw_tracking_uid','').strip()!=r.tracking_uid:
   failures.append(f'{r.series_uid}:raw_tracking_mismatch');continue
  if {x.strip() for x in vr.get('raw_source_modalities','').split(';') if x.strip()}!={r.modality}:
   failures.append(f'{r.series_uid}:raw_modality_mismatch');continue
  if {x.strip() for x in vr.get('raw_referenced_series_uids','').split(';') if x.strip()}!={r.ReferencedSeriesInstanceUID}:
   failures.append(f'{r.series_uid}:raw_source_series_mismatch');continue
  if normalized_label(vr.get('raw_tracking_id',''))!=r.tracking_label or not raw_roi_label_compatible(vr.get('raw_roi_name',''),r.tracking_label):
   failures.append(f'{r.series_uid}:raw_target_anatomy_label_mismatch');continue
  if vr.get('raw_timepoint','').strip().lower()!=r.ClinicalTrialTimePointID.lower():
   failures.append(f'{r.series_uid}:raw_timepoint_mismatch');continue
  rr=r.to_dict();rr['volume_ml']=rawvol
  for name,value in vr.items():rr['verification_'+name]=value
  validated.append(rr)
 return pd.DataFrame(validated),failures

def screen(m,modality,verification=None,prepare=False):
 universe=m[m.is_renal_seg][['patient_id','collection']].drop_duplicates().sort_values(['collection','patient_id'])
 if universe.patient_id.duplicated().any():raise ValueError('Patient belongs to multiple collections')
 renal=m[m.is_renal_seg & m.modality.eq(modality)&m.timepoint.isin([0,1])].copy()
 flow=[];candidates=[];selected=[]
 for person in universe.itertuples(index=False):
  q=renal[renal.patient_id.eq(person.patient_id)].copy();pre=q[q.timepoint.eq(0)];post=q[q.timepoint.eq(1)]
  reason='included';detail=''
  if pre.empty:reason='no_baseline_modality_annotation'
  elif post.empty:reason='no_followup1_modality_annotation'
  elif q.historical_conflict.any():reason='historical_postoperative_recurrence_conflict'
  else:
   required=['StudyInstanceUID','ReferencedSeriesInstanceUID','tracking_uid','tracking_label','series_uid']
   invalid=q[required].eq('').any(axis=1)|q.scan_date.isna()|~np.isfinite(q.stored_metadata_volume_ml)|q.stored_metadata_volume_ml.le(0)
   if invalid.any():reason='invalid_required_metadata_or_volume'
   elif any(g.StudyInstanceUID.nunique()!=1 or g.scan_date.nunique()!=1 for g in [pre,post]):reason='ambiguous_examination'
   elif any(g.tracking_uid.duplicated().any() for g in [pre,post]):reason='repeated_target_annotation'
   elif set(pre.tracking_uid)!=set(post.tracking_uid):reason='unmatched_target_set_or_labels';detail='different_tracking_sets'
   elif pre.set_index('tracking_uid').tracking_label.to_dict()!=post.set_index('tracking_uid').tracking_label.to_dict():reason='unmatched_target_set_or_labels';detail='incompatible_tracking_labels'
   elif post.scan_date.iloc[0]<=pre.scan_date.iloc[0]:reason='nonpositive_examination_interval'
   else:
    candidates.append(q)
    if not prepare:
     checked,failures=verify_rows(q,verification or {})
     if failures:reason='source_object_not_verified';detail=';'.join(failures)
     else:selected.append(checked)
  flow.append({'patient_id':person.patient_id,'collection':person.collection,'modality':modality,'reason':reason,'details':detail,'n_pre_candidate_rows':len(pre),'n_post_candidate_rows':len(post)})
 f=pd.DataFrame(flow);c=pd.concat(candidates,ignore_index=True) if candidates else pd.DataFrame();s=pd.concat(selected,ignore_index=True) if selected else pd.DataFrame()
 return f,c,s

def quantiles(a):
 x=np.asarray(a,dtype=float);return [float(v) for v in np.quantile(x,[.25,.5,.75])] if len(x) else [None,None,None]

def median_ci(a,level=.95):
 x=np.sort(np.asarray(a,dtype=float));n=len(x)
 candidates=[k for k in range(1,n//2+1) if 1-2*stats.binom.cdf(k-1,n,.5)>=level]
 if not candidates:return {'lower':None,'upper':None,'coverage':None,'rank':None,'method':'central order-statistic; finite interval unavailable'}
 k=max(candidates)
 return {'lower':float(x[k-1]),'upper':float(x[n-k]),'coverage':float(1-2*stats.binom.cdf(k-1,n,.5)),'rank':k,'method':'central order-statistic exact binomial'}

def make_pairs(selected,modality):
 records=[]
 if selected.empty:return pd.DataFrame()
 for pid,g in selected.groupby('patient_id'):
  a=g[g.timepoint.eq(0)];b=g[g.timepoint.eq(1)];pre=float(a.volume_ml.sum());post=float(b.volume_ml.sum());sides=set(a.laterality)
  lat='bilateral' if {'left','right'}<=sides else next(iter(sides)) if len(sides)==1 else 'mixed_unspecified'
  records.append({'patient_id':pid,'collection':a.collection.iloc[0],'modality':modality,'baseline_date':a.scan_date.iloc[0].date().isoformat(),'followup_date':b.scan_date.iloc[0].date().isoformat(),'interval_days':int((b.scan_date.iloc[0]-a.scan_date.iloc[0]).days),'baseline_study_uid':a.StudyInstanceUID.iloc[0],'followup_study_uid':b.StudyInstanceUID.iloc[0],'n_targets':len(a),'annotated_laterality':lat,'baseline_volume_ml':pre,'followup_volume_ml':post,'absolute_change_ml':post-pre,'percent_change':100*(post-pre)/pre,'baseline_source_series_count':a.ReferencedSeriesInstanceUID.nunique(),'followup_source_series_count':b.ReferencedSeriesInstanceUID.nunique()})
 return pd.DataFrame(records).sort_values(['collection','patient_id'])

def summarize(p):
 if p.empty:return {'n':0}
 result={'n':len(p),'n_targets':int(p.n_targets.sum()),'target_count_distribution':{str(k):int(v) for k,v in p.n_targets.value_counts().sort_index().items()},'annotated_laterality_counts':{str(k):int(v) for k,v in p.annotated_laterality.value_counts().items()},'n_numerical_decrease':int(p.percent_change.lt(0).sum()),'n_numerical_increase':int(p.percent_change.gt(0).sum()),'n_unchanged':int(p.percent_change.eq(0).sum())}
 for col in ['baseline_volume_ml','followup_volume_ml','absolute_change_ml','percent_change','interval_days']:
  q1,med,q3=quantiles(p[col]);result[col]={'median':med,'q1':q1,'q3':q3,'min':float(p[col].min()),'max':float(p[col].max())}
 result['median_percent_change_ci95']=median_ci(p.percent_change)
 result['n_interval_over_90_days']=int(p.interval_days.gt(90).sum())
 return result

def stratify(p):
 return {'pooled_descriptive':summarize(p),'by_collection':{c:summarize(p[p.collection.eq(c)]) if not p.empty else {'n':0} for c in COLLECTIONS}}

def flow_summary(f):
 counts={}
 for code,label in REASONS:
  g=f[f.reason.eq(code)];counts[code]={'label':label,'overall':len(g),**{c:int(g.collection.eq(c).sum()) for c in COLLECTIONS}}
 return {'screened_any_renal_segmentation':{'overall':len(f),**{c:int(f.collection.eq(c).sum()) for c in COLLECTIONS}},'mutually_exclusive_first_failure':counts}

def draw_figures(p):
 if p.empty:return
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
 palette={'AREN0532':'#2B6CB0','AREN0533':'#2F855A','AREN0534':'#805AD5'}
 fig,axes=plt.subplots(1,3,figsize=(8.2,4.2),sharey=True)
 for ax,c in zip(axes,COLLECTIONS):
  g=p[p.collection.eq(c)].sort_values('percent_change');ax.bar(range(len(g)),g.percent_change,width=.85,color=palette[c]);ax.axhline(0,color='#444444',lw=.8);ax.set_title(f'{c} (n={len(g)})');ax.set_xlabel('Patients, sorted');ax.set_xticks([])
 axes[0].set_ylabel('Matched annotated volume change (%)');fig.tight_layout();fig.savefig(OUT/'figure1_ct_waterfall.png',dpi=300);fig.savefig(OUT/'figure1_ct_waterfall.pdf');plt.close(fig)
 fig,axes=plt.subplots(1,3,figsize=(8.2,4.4),sharey=True)
 for ax,c in zip(axes,COLLECTIONS):
  g=p[p.collection.eq(c)]
  for row in g.itertuples():ax.plot([0,1],[row.baseline_volume_ml,row.followup_volume_ml],color=palette[c],alpha=.32,lw=.7,marker='o',markersize=2)
  if len(g):ax.plot([0,1],[g.baseline_volume_ml.median(),g.followup_volume_ml.median()],color='#111111',lw=2.2,marker='D',markersize=5,label='Marginal median')
  ax.set_xticks([0,1],['Baseline','Follow-up #1']);ax.set_title(f'{c} (n={len(g)})');ax.set_yscale('log')
 axes[0].set_ylabel('Matched annotated volume (mL, log scale)');axes[-1].legend(frameon=False,loc='upper right',fontsize=8.5);fig.tight_layout();fig.savefig(OUT/'figure2_ct_pairs.png',dpi=300);fig.savefig(OUT/'figure2_ct_pairs.pdf');plt.close(fig)
 fig,ax=plt.subplots(figsize=(7.2,4.6))
 for c in COLLECTIONS:
  g=p[p.collection.eq(c)];ax.scatter(g.interval_days,g.percent_change,s=25,alpha=.7,color=palette[c],label=c)
 ax.axhline(0,color='#666666',lw=.7);ax.set_xlabel('Days between source examinations');ax.set_ylabel('Matched annotated volume change (%)');ax.legend(frameon=False);fig.tight_layout();fig.savefig(OUT/'figureS1_interval_scatter.png',dpi=300);fig.savefig(OUT/'figureS1_interval_scatter.pdf');plt.close(fig)

def markdown_tables(results):
 def val(x):return '—' if x is None else f'{x:.1f}'
 def mi(s,col):
  if not s.get('n'):return '—'
  q=s[col];return f"{val(q['median'])} ({val(q['q1'])} to {val(q['q3'])})"
 def ci(s):
  if not s.get('n'):return '—'
  q=s['median_percent_change_ci95'];return 'Not estimable' if q['lower'] is None else f"{q['lower']:.1f} to {q['upper']:.1f}"
 ct=results['ct_primary'];cols=[ct['by_collection'][c] for c in COLLECTIONS]+[ct['pooled_descriptive']]
 rows=['| Characteristic | '+' | '.join(f"{c} (n={s['n']})" for c,s in zip(COLLECTIONS+['Pooled descriptive'],cols))+' |','|---|---:|---:|---:|---:|']
 for label,col in [('Baseline volume, mL','baseline_volume_ml'),('Follow-up #1 volume, mL','followup_volume_ml'),('Absolute change, mL','absolute_change_ml'),('Percentage change, %','percent_change'),('Examination interval, days','interval_days')]:rows.append('| '+label+' | '+' | '.join(mi(s,col) for s in cols)+' |')
 rows.append('| 95% CI for median percentage change | '+' | '.join(ci(s) for s in cols)+' |')
 rows.append('| Numerical decrease / increase / unchanged | '+' | '.join(f"{s.get('n_numerical_decrease',0)}/{s.get('n_numerical_increase',0)}/{s.get('n_unchanged',0)}" for s in cols)+' |')
 rows.append('| Matched renal targets | '+' | '.join(str(s.get('n_targets',0)) for s in cols)+' |')
 (OUT/'table1_ct_primary.md').write_text('\n'.join(rows)+'\n')
 for modality,key in [('CT','ct_flow'),('MR','mr_flow')]:
  f=results[key];rows=['| Screening stage / first-failure reason | AREN0532 | AREN0533 | AREN0534 | Overall |','|---|---:|---:|---:|---:|'];n=f['screened_any_renal_segmentation'];rows.append('| Any renal segmentation | '+' | '.join(str(n[c]) for c in COLLECTIONS+['overall'])+' |')
  for code,label in REASONS:
   n=f['mutually_exclusive_first_failure'][code];rows.append('| '+label+' | '+' | '.join(str(n[c]) for c in COLLECTIONS+['overall'])+' |')
  (OUT/f'table_flow_{modality.lower()}.md').write_text('\n'.join(rows)+'\n')
 sens=[]
 for title,key in [('CT examinations ≤90 days','ct_interval_le90_days'),('MR same-modality matched targets','mr_sensitivity')]:
  ss=results[key];sens+=['### '+title,'','| Collection | n | Median change, % (IQR) | Median 95% CI |','|---|---:|---|---|']
  for c in COLLECTIONS:
   s=ss['by_collection'][c];sens.append(f"| {c} | {s['n']} | {mi(s,'percent_change')} | {ci(s)} |")
  sens.append('')
 (OUT/'tableS1_sensitivities.md').write_text('\n'.join(sens))

def main():
 global DATA,OUT
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-verification',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data/revision/metadata');ap.add_argument('--output-dir',type=Path,default=ROOT/'data/revision/output');ap.add_argument('--verification',type=Path);ap.add_argument('--amendment',type=Path,default=ROOT/'protocol_amendment_2026-09-22.md');args=ap.parse_args();DATA=args.data_dir;OUT=args.output_dir;OUT.mkdir(parents=True,exist_ok=True)
 if args.verification is None:args.verification=ROOT/'data/revision/source/verification.csv'
 m,manifest,crosswalk=load_metadata();pd.DataFrame(crosswalk).to_csv(OUT/'patient_id_normalization.csv',index=False)
 if args.prepare_verification:
  cs=[]
  for modality in ['CT','MR']:
   f,c,_=screen(m,modality,prepare=True);f.to_csv(OUT/f'preverification_screening_{modality.lower()}.csv',index=False)
   if not c.empty:cs.append(c)
  candidates=pd.concat(cs,ignore_index=True) if cs else pd.DataFrame();candidates.to_csv(OUT/'source_verification_candidates.csv',index=False)
  print(json.dumps({'mode':'metadata eligibility only; no revised outcomes calculated','candidate_objects':int(candidates.series_uid.nunique()) if not candidates.empty else 0,'candidate_patients':int(candidates.patient_id.nunique()) if not candidates.empty else 0}))
  return
 amendment=args.amendment
 if not amendment.exists():raise SystemExit('No locked analysis_amendment.md; do not compute outcomes yet')
 if not args.verification.exists():raise SystemExit('Source verification manifest required')
 lock_path=amendment.with_name('lock_record.json')
 if lock_path.exists():
  lock=json.loads(lock_path.read_text())
  if lock.get('sha256')!=file_sha(amendment):raise SystemExit('Amendment hash differs from lock_record.json; document any new dated amendment before running')
 else:lock=None
 verification=load_verification(args.verification)
 results={'analysis_version':'post-audit-v2','generated_utc':datetime.now(timezone.utc).isoformat(),'endpoint':'Change in summed archive-reported volumes of identical annotated renal targets, baseline to Post-Chemotherapy #1','amendment_sha256':file_sha(amendment),'analysis_code_sha256':file_sha(Path(__file__)),'source_verification_sha256':file_sha(args.verification),'source_metadata':manifest,'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__},'scope':'Descriptive archive-derived lesion measurements; treatment/surgical timing and clinical outcomes not linked.'}
 results['analysis_lock_record']=lock
 verification_frame=pd.read_csv(args.verification).fillna('')
 results['source_verification_summary']={'annotation_objects_checked':len(verification_frame),'status_counts':{str(k):int(v) for k,v in verification_frame.status.value_counts().items()},'unresolved_reason_counts':{str(k):int(v) for k,v in verification_frame.loc[verification_frame.status.ne('verified'),'reasons'].value_counts().items()}}
 allpairs={}
 for modality in ['CT','MR']:
  f,c,s=screen(m,modality,verification=verification);f.to_csv(OUT/f'patient_flow_{modality.lower()}.csv',index=False);s.to_csv(OUT/f'selected_targets_{modality.lower()}.csv',index=False);p=make_pairs(s,modality);p.to_csv(OUT/f'paired_patients_{modality.lower()}.csv',index=False);allpairs[modality]=p
  results['ct_primary' if modality=='CT' else 'mr_sensitivity']=stratify(p);results['ct_flow' if modality=='CT' else 'mr_flow']=flow_summary(f)
  assert sum(item['overall'] for item in results['ct_flow' if modality=='CT' else 'mr_flow']['mutually_exclusive_first_failure'].values())==len(f)
 ct=allpairs['CT'];mr=allpairs['MR'];results['ct_interval_le90_days']=stratify(ct[ct.interval_days.le(90)] if not ct.empty else ct)
 results['ct_mr_patient_overlap_n']=len(set(ct.patient_id if not ct.empty else [])&set(mr.patient_id if not mr.empty else []))
 if not ct.empty:
  interval_outliers=ct.loc[ct.interval_days.gt(90),['patient_id','collection','baseline_date','followup_date','interval_days']].sort_values('interval_days',ascending=False)
  interval_outliers.to_csv(OUT/'ct_intervals_over90_days.csv',index=False)
  results['ct_intervals_over90_days']=interval_outliers.to_dict('records')
 else:results['ct_intervals_over90_days']=[]
 # Exclusion context: positive segmentation requirement; absence never becomes zero.
 results['negative_assessment_screening']={'any_negative_assessment_patients':int(m.loc[m.AnnotationType.str.contains('no finding',case=False,na=False),'patient_id'].nunique()),'note':'Negative assessments are not necessarily renal or target-specific. No missing target or absent positive segmentation was recoded as zero.'}
 (OUT/'results.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n');markdown_tables(results);draw_figures(ct)
 print(json.dumps({'ct_n':results['ct_primary']['pooled_descriptive']['n'],'mr_n':results['mr_sensitivity']['pooled_descriptive']['n'],'results_path':str(OUT/'results.json')}))

if __name__=='__main__':main()
