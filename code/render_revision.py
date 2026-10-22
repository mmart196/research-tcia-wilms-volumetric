#!/usr/bin/env python3
"""Render the revised Cureus manuscript from verified analysis outputs.

No outcome values are hardcoded. Citation numbers follow first mention. The DOCX
contains real tables, separate reference paragraphs and calculation-derived figures.
"""
from pathlib import Path
import argparse, json, re, shutil
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT=Path(__file__).resolve().parents[1]
COLS=['AREN0532','AREN0533','AREN0534']
WORDS=['zero','one','two','three','four','five','six','seven','eight','nine']
def number(n):return WORDS[n] if isinstance(n,int) and 0<=n<10 else str(n)
def f(x,d=1):return f'{x:.{d}f}'
def iq(s,key,unit=''):
 q=s[key];return f"{f(q['median'])}{unit} (IQR {f(q['q1'])} to {f(q['q3'])}{unit})"
def ci(s):
 q=s['median_percent_change_ci95']
 return 'not estimable' if q['lower'] is None else f"{f(q['lower'])}% to {f(q['upper'])}%"
def mdtable(header,rows):return '\n'.join(['| '+' | '.join(header)+' |','|'+'|'.join(['---']*len(header))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rows])

def build_tokens(r,output,code_url):
 ct=r['ct_primary'];p=ct['pooled_descriptive'];flow=r['ct_flow'];reasons=flow['mutually_exclusive_first_failure'];total=flow['screened_any_renal_segmentation']['overall'];n=p['n']
 by=ct['by_collection'];short='; '.join(f"{c}: {f(by[c]['percent_change']['median'])}% (95% CI {ci(by[c])}; n = {by[c]['n']})" for c in COLS if by[c]['n'])
 tokens={}
 tokens['ABSTRACT_RESULTS']=f"Of {total} subjects with renal segmentations, {n} met all primary criteria. Median percentage changes were {short}. Median examination intervals were "+', '.join(f"{f(by[c]['interval_days']['median'],0)} days" for c in COLS)+f", respectively. Recorded volume decreased in {p['n_numerical_decrease']} of {n} patients. "+f"The MRI analysis included {r['mr_sensitivity']['pooled_descriptive']['n']} patients. Clinical treatment, surgical timing, and outcomes were not linked."
 tokens['CODE_AVAILABILITY']=f'The revised code, metadata snapshots, verification records, analysis outputs, and manuscript source are available at {code_url}. The package identifies the precise dataset versions and records checksums for downloaded annotation objects. Earlier archived releases contain superseded analyses and are not the source of the revised results.'
 baseline=total-reasons['no_baseline_modality_annotation']['overall'];both=baseline-reasons['no_followup1_modality_annotation']['overall']
 tokens['COHORT_RESULTS']=f"The current metadata contained {total} subjects with at least one renal segmentation. Of these, {baseline} had a baseline CT-referenced renal segmentation, and {both} had CT renal segmentations at both required visit labels. After examination, target-matching, chronology, and source-object checks, {n} patients remained: "+', '.join(f"{by[c]['n']} from {c}" for c in COLS)+f". These patients contributed {p['n_targets']} matched renal targets, each represented at both visits. Table 1 reports mutually exclusive exclusions. The selection rules excluded complete pairs when any required target was unresolved; missing targets were not replaced with zero."
 rows=[['Subjects with any renal segmentation']+[str(flow['screened_any_renal_segmentation'][c]) for c in COLS]+[str(total)]]
 for val in reasons.values():rows.append([val['label']]+[str(val[c]) for c in COLS]+[str(val['overall'])])
 tokens['FLOW_TABLE']=mdtable(['Stage or first failed criterion']+COLS+['Total'],rows)
 tokens['PRIMARY_RESULTS']='Collection-specific median percentage changes were as follows: '+short+'. '+f"Median examination intervals were "+'; '.join(f"{c}, {iq(by[c],'interval_days',' days')}" for c in COLS)+'. Table 2 provides volumes, changes, intervals, and target counts. Figure 1 displays every patient-level percentage change, and Figure 2 shows paired volumes for the same retained target sets.'
 rows=[]
 for label,key in [('Baseline volume, mL','baseline_volume_ml'),('Follow-up volume, mL','followup_volume_ml'),('Absolute change, mL','absolute_change_ml'),('Percentage change, %','percent_change'),('Examination interval, days','interval_days')]:
  rows.append([label]+[f"{f(by[c][key]['median'])} ({f(by[c][key]['q1'])} to {f(by[c][key]['q3'])})" for c in COLS])
 rows.append(['95% CI for median change, %']+[ci(by[c]).replace('%','') for c in COLS])
 rows.append(['Decrease / increase / unchanged']+[f"{by[c]['n_numerical_decrease']} / {by[c]['n_numerical_increase']} / {by[c]['n_unchanged']}" for c in COLS])
 rows.append(['Matched renal targets']+[str(by[c]['n_targets']) for c in COLS])
 for side in ['right','left','bilateral','unspecified','mixed_unspecified']:
  if any(by[c]['annotated_laterality_counts'].get(side,0) for c in COLS):rows.append([f'Annotated laterality: {side.replace("_"," ")}']+[str(by[c]['annotated_laterality_counts'].get(side,0)) for c in COLS])
 tokens['PRIMARY_TABLE']=mdtable(['Characteristic']+[f"{c} (n = {by[c]['n']})" for c in COLS],rows)
 tokens['POOLED_RESULTS']=f"In the pooled descriptive summary, baseline volume was {iq(p,'baseline_volume_ml',' mL')} and follow-up volume was {iq(p,'followup_volume_ml',' mL')}. Median patient-level percentage change was {iq(p,'percent_change','%')} (95% CI {ci(p)}). Recorded volume decreased in {p['n_numerical_decrease']} patients, increased in {number(p['n_numerical_increase'])}, and was unchanged in {number(p['n_unchanged'])}. These measurements combine heterogeneous collection populations and are not estimates of a common treatment effect."
 tokens['FIGURE1']='![Figure 1](figures/figure1_ct_waterfall.png)'
 tokens['FIGURE2']='![Figure 2](figures/figure2_ct_pairs.png)'
 ninety=r['ct_interval_le90_days']['pooled_descriptive'];mr=r['mr_sensitivity']['pooled_descriptive'];interval=p['interval_days']
 tokens['SENSITIVITY_RESULTS']=f"The primary cohort's recorded examination intervals ranged from {f(interval['min'],0)} to {f(interval['max'],0)} days; {number(p['n_interval_over_90_days'])} patients had intervals longer than 90 days. Restricting the analysis to intervals of 90 days or less retained {ninety['n']} CT pairs. The separate MRI analysis retained {mr['n']} pairs; {number(r['ct_mr_patient_overlap_n'])} patients contributed to both modality cohorts. Collection-specific sensitivity estimates are shown in Table 3. These analyses do not establish equivalent acquisition or treatment conditions across collections. A supplementary scatter plot displays examination interval against percentage change."
 rows=[]
 for title,key in [('CT, interval ≤90 days','ct_interval_le90_days'),('MRI, matched targets','mr_sensitivity')]:
  for c in COLS:
   s=r[key]['by_collection'][c]
   rows.append([title,c,str(s['n']),f"{f(s['percent_change']['median'])} ({f(s['percent_change']['q1'])} to {f(s['percent_change']['q3'])})" if s['n'] else 'Not estimable',ci(s).replace('%','') if s['n'] else 'Not estimable'])
 tokens['SENSITIVITY_TABLE']=mdtable(['Analysis','Collection','n','Change, % (IQR)','95% CI'],rows)
 if 'geometry_sensitivity' not in r:raise RuntimeError('Final selected-cohort geometry analysis is required')
 geom=r['geometry_sensitivity'];agreement=geom['roi_agreement'];gp=geom['geometry_on_complete_subset']['pooled_descriptive'];sp=geom['primary_on_complete_subset']['pooled_descriptive'];delta=geom['paired_percentage_difference'];adelta=geom['absolute_paired_percentage_difference']
 reason_labels={'invalid_polygon':'unsupported polygon topology','irregular_plane_spacing':'irregular plane spacing','single_slice':'single plane','overlapping_or_nested_closed_planar':'overlapping or nested ordinary closed planar polygons'}
 reasons_text=', '.join(f"{reason_labels.get(name,name.replace('_',' '))} (n = {count})" for name,count in agreement['qc_flag_counts'].items()) or 'none'
 tokens['GEOMETRY_RESULTS']=f"Contour recomputation was possible for {agreement['computed_roi_n']} of {agreement['eligible_selected_roi_n']} selected ROI-timepoint observations. Reasons for unavailable geometric measurements were {reasons_text}. Among computable observations, median absolute relative difference from the archived ROI volume was {f(agreement['absolute_relative_error_pct']['median'])}%; {agreement['n_absolute_relative_error_over_10pct']} observations differed by more than 10%. These are repeated ROI-timepoint observations, not independent patients or independent segmentation validations. Complete geometric measurements at both visits were available for {geom['complete_geometry_n']} of {geom['eligible_primary_n']} patients. In that same subset, the pooled median percentage change was {f(sp['percent_change']['median'])}% using archived volumes and {f(gp['percent_change']['median'])}% using recomputed volumes. The median absolute patient-level difference was {f(adelta['median'])} percentage points, with signed differences ranging from {f(delta['min'])} to {f(delta['max'])} percentage points. The numerical direction of change differed in {number(geom['numerical_sign_discordance_n'])} patients. No partial target sums were substituted for uncomputable complete pairs."
 tokens['DISCUSSION_FINDING']=f"The revised matched-target analysis retained {n} CT pairs and found substantial decreases in recorded renal lesion volume within each collection. Sensitivity analyses examined the effects of interval restrictions, modality, and volume computation, while eligibility checks restricted which archive records could support a paired measurement. The clinical significance of the measured changes cannot be established from the annotation data alone."
 return tokens

def render_citations(s,library):
 order=[]
 def replace(m):
  keys=[x.strip() for x in m.group(1).split(',')]
  for key in keys:
   if key not in library:raise ValueError('Unknown citation key '+key)
   if key not in order:order.append(key)
  return '['+', '.join(str(order.index(k)+1) for k in keys)+']'
 s=re.sub(r'\[\[([a-z0-9_,]+)\]\]',replace,s)
 refs='\n\n'.join(f"{i}. {library[key]['cureus_reference']}" for i,key in enumerate(order,1))
 return s.replace('@@REFERENCES@@',refs),order

def add_runs(p,s):
 for part in re.split(r'(\*\*.*?\*\*)',s):
  r=p.add_run(part[2:-2] if part.startswith('**') else part)
  r.bold=part.startswith('**')

def set_repeat(row):
 prop=row._tr.get_or_add_trPr();x=OxmlElement('w:tblHeader');prop.append(x)

def create_docx(markdown,dest,draft_dir):
 doc=Document();sec=doc.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11);sec.top_margin=sec.bottom_margin=Inches(.75);sec.left_margin=sec.right_margin=Inches(.75)
 normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(11);normal.paragraph_format.line_spacing=1.12;normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.widow_control=True
 for name,size in [('Title',19),('Heading 1',14),('Heading 2',11.5)]:
  style=doc.styles[name];style.font.name='Arial';style.font.size=Pt(size);style.font.color.rgb=RGBColor(0,0,0);style.font.bold=True;style.paragraph_format.space_before=Pt(10);style.paragraph_format.space_after=Pt(6);style.paragraph_format.keep_with_next=True
  pp=style.element.find(qn('w:pPr'))
  if pp is not None:
   for border in list(pp.findall(qn('w:pBdr'))):pp.remove(border)
 footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
 field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
 lines=markdown.splitlines();i=0;in_references=False
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r'[:\-]+',c) for c in cells):rows.append(cells)
    i+=1
   widths=([2.5,1.5,1.5,1.5] if len(rows[0])==4 else [3.65,.85,.85,.85,.8] if rows[0][-1]=='Total' else [1.35,1.0,.45,2.2,2.0])
   t=doc.add_table(rows=len(rows),cols=len(rows[0]));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
   props=t._tbl.tblPr;borders=OxmlElement('w:tblBorders')
   for edge in ['top','left','bottom','right','insideH','insideV']:
    el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
   props.append(borders)
   for c,w in zip(t.columns,widths):c.width=Inches(w)
   for ri,vals in enumerate(rows):
    trp=t.rows[ri]._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trp.append(cant)
    if ri==0:set_repeat(t.rows[ri])
    for ci,val in enumerate(vals):
     cell=t.cell(ri,ci);cell.width=Inches(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;cp=cell._tc.get_or_add_tcPr()
     margins=OxmlElement('w:tcMar')
     for edge in ['top','bottom','left','right']:
      el=OxmlElement('w:'+edge);el.set(qn('w:w'),'80');el.set(qn('w:type'),'dxa');margins.append(el)
     cp.append(margins)
     if ri==0:
      sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E8EEF3');cp.append(sh)
     p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(2);p.paragraph_format.line_spacing=1.0;p.alignment=WD_ALIGN_PARAGRAPH.LEFT if ci==0 else WD_ALIGN_PARAGRAPH.CENTER
     r=p.add_run(val);r.font.size=Pt(9.5);r.bold=ri==0
   doc.add_paragraph();continue
  m=re.fullmatch(r'!\[([^]]+)\]\(([^)]+)\)',line)
  if m:
   p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;r=p.add_run();shape=r.add_picture(str(draft_dir/m.group(2)),width=Inches(6.7));shape._inline.docPr.set('descr',m.group(1));i+=1;continue
  if line.startswith('# '):p=doc.add_paragraph(style='Title');add_runs(p,line[2:])
  elif line.startswith('## '):
   in_references=line[3:]=='References';p=doc.add_paragraph(style='Heading 1');add_runs(p,line[3:])
  elif line.startswith('### '):p=doc.add_paragraph(style='Heading 2');add_runs(p,line[4:])
  else:
   p=doc.add_paragraph();add_runs(p,line)
   if line.startswith('**Table ') or line.startswith('**Figure '):p.paragraph_format.keep_with_next=True
   if in_references:
    p.paragraph_format.space_after=Pt(6)
    for run in p.runs:run.font.size=Pt(10)
  i+=1
 doc.core_properties.title=markdown.splitlines()[0][2:];doc.core_properties.author='Rachel Velasco; Michael Martinez';doc.core_properties.subject='Retrospective secondary analysis of public renal lesion annotations'
 dest.parent.mkdir(parents=True,exist_ok=True);doc.save(dest)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=ROOT/'data/revision/output');ap.add_argument('--template',type=Path,default=ROOT/'draft/manuscript_template.md');ap.add_argument('--library',type=Path,default=ROOT/'draft/citation_library.json');ap.add_argument('--docx',type=Path,default=ROOT/'draft/manuscript.docx');ap.add_argument('--code-url',default='https://github.com/mmart196/research-tcia-wilms-volumetric/tree/revision/cureus-data-corrections-2026-09-22');args=ap.parse_args()
 r=json.loads((args.output_dir/'results.json').read_text());library=json.loads(args.library.read_text());s=args.template.read_text();tokens=build_tokens(r,args.output_dir,args.code_url)
 for k,v in tokens.items():s=s.replace('@@'+k+'@@',v)
 s,order=render_citations(s,library)
 left=re.findall(r'@@[A-Z_0-9]+@@',s)
 if left:raise ValueError('Unresolved tokens '+str(left))
 if '—' in s:raise ValueError('Em dash prohibited in this manuscript')
 abstract=s.split('## Abstract\n',1)[1].split('**Keywords:**',1)[0].strip();plain=re.sub(r'\*\*','',abstract)
 if len(plain)>3500:raise ValueError(f'Abstract exceeds 3500 characters: {len(plain)}')
 out=ROOT/'draft'
 (out/'figures').mkdir(parents=True,exist_ok=True)
 for name in ['figure1_ct_waterfall.png','figure2_ct_pairs.png','figureS1_interval_scatter.png']:
  source=args.output_dir/name
  destination=out/'figures'/name
  if source.resolve()!=destination.resolve():shutil.copyfile(source,destination)
 (out/'manuscript.md').write_text(s);refs=[dict(library[k],number=i) for i,k in enumerate(order,1)];(out/'references.json').write_text(json.dumps(refs,indent=2));(out/'reference_order.json').write_text(json.dumps(order,indent=2));create_docx(s,args.docx,out)
 manifest={'title':s.splitlines()[0][2:],'abstract_characters':len(plain),'references':len(order),'tables':3,'figures':2,'docx':str(args.docx),'source_analysis':str(args.output_dir/'results.json')};(out/'render_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest))
if __name__=='__main__':main()
