"""Retrieve current official TCIA RTSTRUCTs for source validation; no source CT/MR."""
import argparse, csv, hashlib, io, json, time, urllib.parse, urllib.request, zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/revision/source'
RAW = ROOT / 'data/revision/raw'
OLD = ROOT / 'data/revision/metadata'
API = 'https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage'
SPECIAL = {'AREN0533-PARUTG', 'AREN0533-PARMKA', 'AREN0532-PATTED',
           'AREN0532-PAURIY', 'AREN0532-PAURIYAREN0532-PAURIY',
           'AREN0534-PAPYAR', 'AREN0532-PATYFE', 'AREN0534-PAUTBY'}

def manifest(metadata_dir=OLD):
    records=[]
    for collection in ['AREN0532','AREN0533','AREN0534']:
        path=next(metadata_dir.glob(f'Metadata_Report_{collection}_2025*.csv'))
        with path.open(encoding='latin1', newline='') as f:
            allrows=list(csv.DictReader(f))
        renal=[r for r in allrows if r['AnnotationType']=='Segmentation' and
               'KIDNEY' in r['TrackingID'].upper()]
        pre={r['PatientID'] for r in renal if r['ClinicalTrialTimePointID']=='Pre-Dose'}
        post={r['PatientID'] for r in renal if r['ClinicalTrialTimePointID']=='Post-Chemotherapy #1'}
        paired=pre & post
        chosen=[r for r in allrows if r['AnnotationType']=='Segmentation' and (
            (r['PatientID'] in paired and 'KIDNEY' in r['TrackingID'].upper() and
             r['ClinicalTrialTimePointID'] in ['Pre-Dose','Post-Chemotherapy #1']) or
            r['PatientID'] in SPECIAL)]
        for r in chosen:r['collection']=collection
        records.extend(chosen)
    seen=set(); out=[]
    for r in records:
        if r['SeriesInstanceUID'] not in seen:
            seen.add(r['SeriesInstanceUID']);out.append(r)
    out.sort(key=lambda r:(r['PatientID'] not in SPECIAL,r['PatientID'],r['ClinicalTrialTimePointID']))
    return out

def fetch(r):
    uid=r['SeriesInstanceUID']; dest=RAW/f'{uid}.dcm'
    url=API+'?'+urllib.parse.urlencode({'SeriesInstanceUID':uid})
    record={'patient_id':r['PatientID'],'series_uid':uid,'url':url}
    start=time.time()
    for attempt in range(1,3):
        try:
            if dest.exists():
                payload=dest.read_bytes();record['status']='cached'
            else:
                with urllib.request.urlopen(url,timeout=45) as response:
                    content=response.read();record['http_status']=response.status
                archive=zipfile.ZipFile(io.BytesIO(content))
                names=[name for name in archive.namelist() if name.lower().endswith('.dcm')]
                if len(names)!=1:raise ValueError(f'Expected one DICOM, got {len(names)}')
                payload=archive.read(names[0]);dest.write_bytes(payload)
                record.update(status='downloaded',zip_sha256=hashlib.sha256(content).hexdigest())
            record.update(bytes=len(payload),dcm_sha256=hashlib.sha256(payload).hexdigest(),
                          file=str(dest),attempts=attempt,elapsed_seconds=round(time.time()-start,3))
            return record
        except Exception as exc:
            record.update(status='failed',error=repr(exc),attempts=attempt,
                          elapsed_seconds=round(time.time()-start,3))
    return record

def main():
    global RAW,SOURCE
    ap=argparse.ArgumentParser()
    ap.add_argument('--metadata-dir',type=Path,default=OLD)
    ap.add_argument('--raw-dir',type=Path,default=RAW)
    ap.add_argument('--output-dir',type=Path,default=SOURCE)
    ap.add_argument('--workers',type=int,default=8)
    args=ap.parse_args();RAW=args.raw_dir;SOURCE=args.output_dir
    RAW.mkdir(exist_ok=True,parents=True); SOURCE.mkdir(exist_ok=True,parents=True)
    rows=manifest(args.metadata_dir)
    with (SOURCE/'current_raw_manifest.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f'Retrieving {len(rows)} current annotation objects',flush=True)
    logs=[]
    with (SOURCE/'retrieval_log.jsonl').open('w') as log, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(fetch,r) for r in rows]
        for future in as_completed(futures):
            result=future.result();logs.append(result);log.write(json.dumps(result)+'\n');log.flush()
            if len(logs)%100==0 or result['status']=='failed':
                print(json.dumps({'completed':len(logs),'total':len(rows),'failed':sum(l['status']=='failed' for l in logs),'last':result.get('patient_id')}),flush=True)
    summary={'requested':len(rows),'success':sum(l['status']!='failed' for l in logs),
             'failed':sum(l['status']=='failed' for l in logs),'bytes':sum(l.get('bytes',0) for l in logs)}
    (SOURCE/'retrieval_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
