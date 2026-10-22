"""Validate current metadata against intended tracked ROIs in current RTSTRUCTs.

Checks metadata provenance/identity. Does not validate CT/MR image segmentation quality.
ROIVolume is used as archive-reported volume; contour-derived volumes are not substituted.
"""
import argparse,csv,json,math,re
from collections import Counter
from datetime import datetime
from pathlib import Path
import pydicom

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/revision/source'
RAW=ROOT/'data/revision/raw'
ID_MAP={'AREN0532-PAURIYAREN0532-PAURIY':'AREN0532-PAURIY'}
SOPS={'1.2.840.10008.5.1.4.1.1.2':'CT','1.2.840.10008.5.1.4.1.1.2.1':'CT',
      '1.2.840.10008.5.1.4.1.1.4':'MR','1.2.840.10008.5.1.4.1.1.4.1':'MR'}

def text(v):return '' if v is None else str(v).strip()
def date(v):
    s=text(v)
    if re.fullmatch(r'\d{8}',s):return datetime.strptime(s,'%Y%m%d').date().isoformat()
    if re.match(r'^\d{4}/',s):return datetime.strptime(s,'%Y/%m/%d').date().isoformat()
    # These TCIA dates are normalized around 1960, not a rolling Python %y pivot.
    month,day,year=(int(x) for x in s.split('/'))
    return datetime(1900+year,month,day).date().isoformat()

def label(v):
    words=re.findall(r'[A-Z]+|\d+',text(v).upper())
    trans={'RT':'RIGHT','R':'RIGHT','LT':'LEFT','L':'LEFT'}
    # LYMPH is optional in the same nonrenal NODE naming convention; no anatomy
    # synonym ever maps ABDOMEN or other sites to KIDNEY.
    return ' '.join(trans.get(w,w) for w in words if w!='LYMPH')

def refs(ds):
    series=set();sops=set()
    for frame in ds.get('ReferencedFrameOfReferenceSequence',[]):
        for study in frame.get('RTReferencedStudySequence',[]):
            for ser in study.get('RTReferencedSeriesSequence',[]):
                if ser.get('SeriesInstanceUID'):series.add(text(ser.SeriesInstanceUID))
                for image in ser.get('ContourImageSequence',[]):
                    if image.get('ReferencedSOPClassUID'):sops.add(text(image.ReferencedSOPClassUID))
    return series,sops

def verify(m):
    uid=text(m['SeriesInstanceUID']);track=text(m['TrackingUID'])
    row=dict(series_uid=uid,metadata_tracking_uid=track,metadata_patient_id=m['PatientID'],
             canonical_patient_id=ID_MAP.get(m['PatientID'],m['PatientID']),status='error',reasons='',
             raw_patient_id='',raw_study_uid='',raw_study_date='',raw_referenced_series_uids='',
             raw_source_modalities='',raw_roi_number='',raw_roi_name='',raw_tracking_uid='',
             raw_tracking_id='',raw_roi_volume_ml='',metadata_roi_volume_ml=m['ROIVolume'],
             raw_timepoint='',raw_context_phase_codes='',n_rois_in_object='',n_selected_contours='',
             selected_contour_types='',patient_id_normalization_note='',roi_name_normalization_note='',
             file=str(RAW/f'{uid}.dcm'))
    try:
        path=Path(row['file'])
        if not path.exists():row['reasons']='raw_not_downloaded';return row
        d=pydicom.dcmread(path)
        row.update(raw_patient_id=text(d.get('PatientID')),raw_study_uid=text(d.get('StudyInstanceUID')),
                   raw_study_date=date(d.get('StudyDate')),raw_timepoint=text(d.get('ClinicalTrialTimePointID')))
        reasons=[]
        if text(d.get('SeriesInstanceUID'))!=uid:reasons.append('series_uid_mismatch')
        if row['raw_patient_id']!=row['canonical_patient_id']:reasons.append('patient_id_mismatch')
        if m['PatientID'] in ID_MAP:row['patient_id_normalization_note']='exact_v2_duplicate_identifier_corrected_from_raw_header'
        if row['raw_study_uid']!=text(m['StudyInstanceUID']):reasons.append('study_uid_mismatch')
        if row['raw_study_date']!=date(m['StudyDate']):reasons.append('study_date_mismatch')
        if row['raw_timepoint'].lower()!=text(m['ClinicalTrialTimePointID']).lower():reasons.append('timepoint_label_mismatch')
        phases=[]
        for ctx in d.get('AcquisitionContextSequence',[]):
            for code in ctx.get('ConceptCodeSequence',[]):phases.append(text(code.get('CodeValue'))+':'+text(code.get('CodeMeaning')))
        row['raw_context_phase_codes']=';'.join(phases)
        series,sops=refs(d)
        row['raw_referenced_series_uids']=';'.join(sorted(series))
        if series!={text(m['ReferencedSeriesInstanceUID'])}:reasons.append('source_series_mismatch_or_multiple')
        rois=list(d.get('StructureSetROISequence',[]));row['n_rois_in_object']=len(rois)
        matched=[r for r in rois if text(r.get('TrackingUID'))==track and track]
        if len(matched)!=1:
            reasons.append('intended_tracking_uid_not_unique');row.update(status='unresolved',reasons=';'.join(reasons));return row
        r=matched[0]
        row.update(raw_roi_number=int(r.ROINumber),raw_roi_name=text(r.get('ROIName')),
                   raw_tracking_uid=text(r.get('TrackingUID')),raw_tracking_id=text(r.get('TrackingID')),
                   raw_roi_volume_ml=text(r.get('ROIVolume')))
        if label(row['raw_tracking_id'])!=label(m['TrackingID']):reasons.append('tracking_id_mismatch')
        roi_label=label(row['raw_roi_name']);tracking_label=label(m['TrackingID'])
        if roi_label!=tracking_label:
            # Locked, outcome-blind source adjudication: a missing numeric suffix
            # is benign only with exact kidney+known-side identity and a unique
            # TrackingUID match. Do not infer unknown side or change anatomy.
            bare=re.fullmatch(r'(LEFT|RIGHT) KIDNEY',roi_label)
            numbered=re.fullmatch(r'(LEFT|RIGHT) KIDNEY (\d+)',tracking_label)
            if bare and numbered and bare.group(1)==numbered.group(1):
                row['roi_name_normalization_note']='missing_numeric_suffix_unique_tracking_uid_and_same_kidney_side'
            else:reasons.append('roi_name_tracking_anatomy_mismatch')
        try:
            v=float(row['raw_roi_volume_ml']);mv=float(m['ROIVolume'])
            if not math.isfinite(v) or v<=0:reasons.append('raw_volume_nonpositive_or_nonfinite')
            if not math.isclose(v,mv,rel_tol=1e-9,abs_tol=1e-6):reasons.append('raw_metadata_volume_mismatch')
        except (TypeError,ValueError):reasons.append('volume_unreadable')
        rc=[c for c in d.get('ROIContourSequence',[]) if int(c.ReferencedROINumber)==int(r.ROINumber)]
        contours=[c for item in rc for c in item.get('ContourSequence',[])]
        row['n_selected_contours']=len(contours)
        types=sorted({text(c.get('ContourGeometricType')) for c in contours})
        row['selected_contour_types']=';'.join(types)
        if len(rc)!=1 or not contours:reasons.append('intended_contour_sequence_absent_or_ambiguous')
        if not types or any(t not in {'CLOSED_PLANAR','CLOSEDPLANAR_XOR'} for t in types):reasons.append('intended_contours_not_closed_planar_segmentation')
        for c in contours:
            coords=c.get('ContourData',[])
            if len(coords)<9 or len(coords)%3:reasons.append('invalid_contour_coordinates')
            try:
                if any(not math.isfinite(float(value)) for value in coords):reasons.append('nonfinite_contour_coordinates')
            except (TypeError,ValueError,OverflowError):reasons.append('nonnumeric_contour_coordinates')
            try:
                if int(c.NumberOfContourPoints)!=len(coords)//3:reasons.append('contour_point_count_mismatch')
            except (AttributeError,TypeError,ValueError):reasons.append('contour_point_count_missing_or_invalid')
            for im in c.get('ContourImageSequence',[]):
                if im.get('ReferencedSOPClassUID'):sops.add(text(im.ReferencedSOPClassUID))
        modalities={SOPS.get(s,s) for s in sops};row['raw_source_modalities']=';'.join(sorted(modalities))
        if modalities!={text(m['ReferencedSeriesModality'])}:reasons.append('source_modality_mismatch_or_multiple')
        row.update(status='unresolved' if reasons else 'verified',reasons=';'.join(sorted(set(reasons))))
    except Exception as exc:row.update(status='error',reasons='read_error:'+repr(exc))
    return row

def main():
    global SOURCE,RAW
    ap=argparse.ArgumentParser();ap.add_argument('--final',action='store_true')
    ap.add_argument('--manifest',type=Path)
    ap.add_argument('--raw-dir',type=Path,default=RAW)
    ap.add_argument('--output-dir',type=Path,default=SOURCE)
    args=ap.parse_args();SOURCE=args.output_dir;RAW=args.raw_dir
    SOURCE.mkdir(exist_ok=True,parents=True)
    manifest_path=args.manifest or SOURCE/'current_raw_manifest.csv'
    with manifest_path.open(newline='') as f:manifest=list(csv.DictReader(f))
    rows=[verify(m) for m in manifest]
    filename='verification.csv' if args.final else 'verification_in_progress.csv'
    with (SOURCE/filename).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'rows':len(rows),'status_counts':dict(Counter(r['status'] for r in rows)),
             'reason_counts':dict(Counter(reason for r in rows for reason in r['reasons'].split(';') if reason))}
    (SOURCE/(filename.replace('.csv','_summary.json'))).write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
