#!/usr/bin/env python3
"""Peer-review addition (post hoc, descriptive): what the archive metadata contain after baseline
for patients excluded because no CT renal segmentation exists at Post-Chemotherapy #1, and a
patient-selection flow diagram for the primary CT cohort.

Uses only the committed current metadata snapshots and patient_flow_ct.csv. No volumes or
outcomes are read, and eligibility is not changed.

Usage:
  python code/revision_followup_flow.py \
    --metadata-dir data/revision/metadata \
    --flow data/revision/output/patient_flow_ct.csv \
    --output-dir data/revision/output
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

COLLECTIONS = ['AREN0532', 'AREN0533', 'AREN0534']
CURRENT = {
    'AREN0532': 'Metadata_Report_AREN0532_2025-12-03-1.csv',
    'AREN0533': 'Metadata_Report_AREN0533_2025-12-19.csv',
    'AREN0534': 'Metadata_Report_AREN0534_2025-12-22.csv',
}
CATEGORIES = [
    ('no_post_baseline_records', 'No annotation record at any post-baseline visit'),
    ('post_baseline_without_renal_segmentation', 'Post-baseline records without renal segmentation'),
    ('renal_segmentation_other_modality_or_visit', 'Renal segmentation only on MRI or at a later visit'),
]


def canonical_patient(x: str) -> str:
    x = str(x).strip()
    return 'AREN0532-PAURIY' if x == 'AREN0532-PAURIYAREN0532-PAURIY' else x


def load_metadata(meta_dir: Path) -> pd.DataFrame:
    frames = []
    for collection, name in CURRENT.items():
        df = pd.read_csv(meta_dir / name, encoding='latin1', dtype=str).fillna('')
        df = df.apply(lambda s: s.str.strip())
        df['collection'] = collection
        df['patient_id'] = df.PatientID.map(canonical_patient)
        frames.append(df)
    m = pd.concat(frames, ignore_index=True)
    m['timepoint'] = m.ClinicalTrialTimePointID.str.lower().map(
        {'pre-dose': 0, **{f'post-chemotherapy #{i}': i for i in range(1, 7)}})
    if m.timepoint.isna().any():
        raise ValueError('Unmapped ClinicalTrialTimePointID values: ' +
                         ', '.join(sorted(m.loc[m.timepoint.isna(), 'ClinicalTrialTimePointID'].unique())))
    m['modality'] = m.ReferencedSeriesModality.str.upper()
    m['annotation'] = m.AnnotationType.str.lower()
    m['is_renal_seg'] = m.annotation.eq('segmentation') & m.TrackingID.str.contains(r'\bKIDNEY\b', case=False)
    return m


def classify(m: pd.DataFrame, flow: pd.DataFrame) -> pd.DataFrame:
    excluded = flow[flow.reason.eq('no_followup1_modality_annotation')]
    rows = []
    for r in excluded.itertuples():
        q = m[m.patient_id.eq(r.patient_id)]
        post = q[q.timepoint >= 1]
        renal_post = post[post.is_renal_seg]
        if post.empty:
            category, detail = 'no_post_baseline_records', ''
        elif renal_post.empty:
            category = 'post_baseline_without_renal_segmentation'
            neg = post.annotation.str.contains('no finding').any()
            nonrenal = (post.annotation.eq('segmentation') & ~post.is_renal_seg).any()
            detail = ('negative_and_nonrenal' if neg and nonrenal else
                      'nonrenal_segmentation_only' if nonrenal else 'negative_assessment_only')
        else:
            category = 'renal_segmentation_other_modality_or_visit'
            if (renal_post.timepoint.eq(1) & renal_post.modality.eq('MR')).any():
                detail = 'mri_at_followup1'
            elif (renal_post.timepoint.ge(2) & renal_post.modality.eq('CT')).any():
                detail = 'ct_at_later_visit_only'
            else:
                detail = 'mri_at_later_visit_only'
        nonrenal_sites = sorted(set(
            post.loc[post.annotation.eq('segmentation') & ~post.is_renal_seg, 'TrackingID']
            .str.replace(r'\s*-\s*\d+$', '', regex=True)
            .str.replace(r'^(LEFT|RIGHT)\s+', '', regex=True)))
        rows.append({'patient_id': r.patient_id, 'collection': r.collection, 'category': category,
                     'detail': detail, 'post_baseline_visits': ';'.join(sorted(set(post.ClinicalTrialTimePointID))),
                     'nonrenal_post_baseline_sites': ';'.join(nonrenal_sites)})
    return pd.DataFrame(rows)


def counts(series_collection: pd.Series) -> dict:
    c = series_collection.value_counts()
    out = {k: int(c.get(k, 0)) for k in COLLECTIONS}
    out['overall'] = int(sum(out.values()))
    return out


def summarize(b: pd.DataFrame, flow: pd.DataFrame) -> dict:
    s = {'n_excluded_no_followup1_ct': counts(b.collection), 'categories': {}, 'details': {}}
    for key, label in CATEGORIES:
        s['categories'][key] = {'label': label, **counts(b.loc[b.category.eq(key), 'collection'])}
    for key in sorted(b.detail.unique()):
        if key:
            s['details'][key] = counts(b.loc[b.detail.eq(key), 'collection'])
    lung = b.nonrenal_post_baseline_sites.fillna('').str.split(';').map(lambda x: 'LUNG' in x)
    s['details']['nonrenal_only_with_lung_lesion'] = counts(
        b.loc[b.detail.eq('nonrenal_segmentation_only') & lung, 'collection'])
    s['flow'] = {reason: counts(flow.loc[flow.reason.eq(reason), 'collection']) for reason in sorted(flow.reason.unique())}
    s['flow']['screened'] = counts(flow.collection)
    s['note'] = ('Post hoc descriptive tabulation added during peer review. Uses metadata only; no volumes or outcomes; '
                 'eligibility unchanged. The archive does not record why follow-up annotations are absent.')
    return s


def fmt(c: dict) -> str:
    return f"{c['overall']} ({c['AREN0532']} / {c['AREN0533']} / {c['AREN0534']})"


def draw(summary: dict, out_png: Path, out_pdf: Path) -> None:
    f = summary['flow']
    zero = {k: 0 for k in COLLECTIONS + ['overall']}
    get = lambda key: f.get(key, zero)
    screened, no_base, no_fu, included = f['screened'], get('no_baseline_modality_annotation'), \
        get('no_followup1_modality_annotation'), get('included')
    late_keys = ['historical_postoperative_recurrence_conflict', 'invalid_required_metadata_or_volume',
                 'ambiguous_examination', 'repeated_target_annotation', 'unmatched_target_set_or_labels',
                 'nonpositive_examination_interval', 'source_object_not_verified']
    later = {k: sum(get(x)[k] for x in late_keys) for k in COLLECTIONS + ['overall']}
    baseline = {k: screened[k] - no_base[k] for k in screened}
    both = {k: baseline[k] - no_fu[k] for k in baseline}
    if any(both[k] - later[k] != included[k] for k in both):
        raise ValueError('flow arithmetic mismatch')
    cat = summary['categories']
    late_rows = [(k, lab) for k, lab in [
        ('historical_postoperative_recurrence_conflict', 'Historical postoperative/recurrence label'),
        ('invalid_required_metadata_or_volume', 'Missing or invalid identity, date, or volume'),
        ('ambiguous_examination', 'Multiple examinations or dates at a visit'),
        ('repeated_target_annotation', 'Repeated target annotation at a visit'),
        ('unmatched_target_set_or_labels', 'Different tracking sets or incompatible labels'),
        ('nonpositive_examination_interval', 'Follow-up not after baseline'),
        ('source_object_not_verified', 'Source ROI identity or volume unresolved')] if get(k)['overall'] > 0]

    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    B, N = 'bold', 'normal'
    boxes = {
        'A': [('Screened: any renal segmentation', B), ('in current metadata', B), (fmt(screened), N)],
        'E1': [('No baseline CT renal segmentation', B), (fmt(no_base), N)],
        'B': [('Baseline CT renal segmentation', B), (fmt(baseline), N)],
        'E2': [('No CT renal segmentation at', B), ('Post-Chemotherapy #1', B), (fmt(no_fu), N),
               ('Archive content after baseline (descriptive):', 'italic'),
               ('\u2022 No later annotation record', N), ('   ' + fmt(cat['no_post_baseline_records']), N),
               ('\u2022 Later records without renal segmentation', N),
               ('   ' + fmt(cat['post_baseline_without_renal_segmentation']), N),
               ('\u2022 Renal segmentation only on MRI or at', N),
               ('   a later visit ' + fmt(cat['renal_segmentation_other_modality_or_visit']), N)],
        'C': [('CT renal segmentation at both visits', B), (fmt(both), N)],
        'E3': [('Failed examination, matching, or', B), ('source checks', B), (fmt(later), N)] +
              [x for k, lab in late_rows for x in (('\u2022 ' + lab, N), ('   ' + fmt(get(k)), N))],
        'D': [('Primary CT cohort', B), (fmt(included), N), ('349 matched renal targets', N)],
    }
    fs = {'A': 9.5, 'B': 9.5, 'C': 9.5, 'D': 9.5, 'E1': 9.0, 'E2': 9.0, 'E3': 9.0}
    pad, gap = 0.10, 0.22
    lh = lambda k: fs[k] / 72 * 1.42
    height = {k: len(v) * lh(k) + 2 * pad for k, v in boxes.items()}
    order = ['A', 'E1', 'B', 'E2', 'C', 'E3', 'D']
    foot_h = 0.42
    H = 0.12 + sum(height[k] for k in order) + gap * (len(order) - 1) + 0.18 + foot_h
    W = 7.75
    mx, mw = 0.12, 3.15
    ex, ew = 3.72, 3.93
    fig = plt.figure(figsize=(W, H), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    face = {'A': '#ffffff', 'B': '#ffffff', 'C': '#ffffff', 'D': '#e6edf7', 'E1': '#f2f2f2', 'E2': '#f2f2f2', 'E3': '#f2f2f2'}
    geom = {}
    y = H - 0.12
    for k in order:
        x, w = (mx, mw) if k in 'ABCD' else (ex, ew)
        h = height[k]
        ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle='round,pad=0,rounding_size=0.06',
                                    linewidth=1.0, edgecolor='#1f1f1f', facecolor=face[k]))
        centered = k in 'ABCD'
        for i, (text, style) in enumerate(boxes[k]):
            ty = y - pad - (i + 0.5) * lh(k)
            ax.text(x + w / 2 if centered else x + 0.12, ty, text, ha='center' if centered else 'left', va='center',
                    fontsize=fs[k], fontweight='bold' if style == B else 'normal',
                    fontstyle='italic' if style == 'italic' else 'normal', color='#111111')
        geom[k] = (x, w, y, y - h)
        y -= h + gap
    cx = mx + mw / 2
    kw = dict(arrowstyle='-|>', lw=1.0, color='#1f1f1f', shrinkA=0, shrinkB=0, mutation_scale=10)
    for a, b in [('A', 'B'), ('B', 'C'), ('C', 'D')]:
        ax.annotate('', xy=(cx, geom[b][2]), xytext=(cx, geom[a][3]), arrowprops=kw)
    for e in ['E1', 'E2', 'E3']:
        x, w, top, bottom = geom[e]
        yc = (top + bottom) / 2
        ax.annotate('', xy=(x, yc), xytext=(cx, yc), arrowprops=kw)
    ax.text(mx, 0.12 + foot_h / 2,
            'Counts are patients: total (AREN0532 / AREN0533 / AREN0534). Each excluded patient is counted once, at the first\n'
            'failed criterion. Categories of archive content after baseline are descriptive and did not affect eligibility.',
            ha='left', va='center', fontsize=7.6, color='#333333')
    fig.savefig(out_png, dpi=300, facecolor='white')
    fig.savefig(out_pdf, facecolor='white')
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--metadata-dir', type=Path, required=True)
    ap.add_argument('--flow', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    m = load_metadata(a.metadata_dir)
    flow = pd.read_csv(a.flow, dtype=str)
    b = classify(m, flow)
    b.to_csv(a.output_dir / 'followup_absence_ct.csv', index=False)
    s = summarize(b, flow)
    (a.output_dir / 'followup_absence_summary.json').write_text(json.dumps(s, indent=1))
    draw(s, a.output_dir / 'figure_flow_ct.png', a.output_dir / 'figure_flow_ct.pdf')
    print(json.dumps({k: v for k, v in s.items() if k != 'flow'}, indent=1))


if __name__ == '__main__':
    main()
