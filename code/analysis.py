"""Step 2 (execution): locked analysis — volumetric response to neoadjuvant chemo.

Reads data/volumes.csv (from volumes.py) and produces:
  - data/results.json      every number cited in the manuscript (spec R4)
  - draft/figures/waterfall.png     % volume change per subject, sorted
  - draft/figures/trajectories.png  per-subject volume trajectories over timepoints

Plan (protocol.md, locked 2026-07-26):
  inclusion  = usable rows (computable volume, CT-referenced), kidney ROIs
  pairing    = Pre-dose vs FIRST post-chemotherapy timepoint per subject
  primary    = % volume change; Wilcoxon signed-rank (two-sided)
  subgroups  = collection (= trial stratum), laterality
"""
import json
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parent.parent / "data"
FIGS = Path(__file__).resolve().parent.parent / "draft" / "figures"

TP_ORDER = {
    "Pre-dose": 0,
    "Post-chemotherapy": 1, "Post-chemotherapy #1": 1, "Post-Chemotherapy #1": 1,
    "Post-chemotherapy #2": 2, "Post-Chemotherapy #2": 2,
    "Post-chemotherapy #3": 3, "Post-Chemotherapy #3": 3,
    "Post-chemotherapy #4": 4, "Post-Chemotherapy #4": 4,
    "Post-operative": 90,
    "Recurrence": 99,
}


def iqr(s):
    q = np.percentile(s, [25, 75])
    return float(q[0]), float(q[1])


def census_from_metadata():
    """Flow-diagram upstream counts, recomputed from the committed metadata reports."""
    any_kidney, paired = set(), set()
    tp_by_subj = defaultdict(set)
    for col in ["AREN0532", "AREN0533", "AREN0534"]:
        with (DATA / f"Metadata_Report_{col}.csv").open(newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r["Annotation Type"] != "Segmentation":
                    continue
                lab = r.get("StructureSetLabel") or r.get("SeriesDescription", "")
                if "KIDNEY" not in lab.upper():
                    continue
                any_kidney.add(r["PatientID"])
                tp_by_subj[r["PatientID"]].add(r["ClinicalTrialTimePointID"])
    paired = {p for p, t in tp_by_subj.items()
              if any("Pre" in t for t in t) and any("Post" in t for t in t)}
    return len(any_kidney), len(paired)


def main():
    n_any_kidney, n_paired_meta = census_from_metadata()
    df = pd.read_csv(DATA / "volumes.csv")
    df = df[(df["volume_ml"].notna()) & (df["source_class"] == "CT")].copy()
    df["tp_idx"] = df["timepoint"].map(TP_ORDER)
    if df["tp_idx"].isna().any():
        bad = df.loc[df["tp_idx"].isna(), "timepoint"].unique()
        raise SystemExit(f"unmapped timepoints: {bad} — extend TP_ORDER")

    # per subject x timepoint: total kidney tumor volume (sum of ROIs)
    st = (df.groupby(["patient_id", "collection", "timepoint", "tp_idx"],
                     as_index=False)
            .agg(volume_ml=("volume_ml", "sum"),
                 n_rois=("roi_name", "count"),
                 age_years=("age_years", "max"),
                 sex=("sex", "first")))

    wide = st.pivot_table(index=["patient_id", "collection"], columns="tp_idx",
                          values="volume_ml")
    paired = wide[wide.index.isin(wide.dropna(subset=[0]).index)]
    # first post-chemo timepoint with a volume (1..4)
    post_cols = [c for c in (1, 2, 3, 4) if c in paired.columns]
    first_post = paired[post_cols].apply(lambda r: r.dropna().iloc[0] if r.dropna().size else np.nan, axis=1)
    first_post_idx = paired[post_cols].apply(lambda r: r.dropna().index[0] if r.dropna().size else np.nan, axis=1)
    pair = pd.DataFrame({"pre": paired[0], "post": first_post, "post_tp": first_post_idx}).dropna()
    pair = pair[pair["pre"] > 0].reset_index()  # patient_id, collection become columns
    pair["pct_change"] = (pair["post"] - pair["pre"]) / pair["pre"] * 100.0

    w = stats.wilcoxon(pair["pre"], pair["post"])
    pc = pair["pct_change"].to_numpy()

    # Hodges-Lehmann estimate + 95% CI for the median % change, from the same
    # Walsh-average distribution (signed-rank normal approximation for the ranks):
    # pseudomedian = median of (x_i+x_j)/2 over i<=j; CI = [w_(k), w_(M+1-k)]
    iu = np.triu_indices(len(pc))
    w_avgs = np.sort((pc[iu[0]] + pc[iu[1]]) / 2.0)
    M = len(w_avgs)
    hl = float(np.median(w_avgs))
    n_ = len(pc)
    mu, sigma = n_ * (n_ + 1) / 4.0, np.sqrt(n_ * (n_ + 1) * (2 * n_ + 1) / 24.0)
    k = int(np.floor(mu - 1.96 * sigma))
    k = min(max(k, 1), M)
    lo, hi = float(w_avgs[k - 1]), float(w_avgs[M - k])

    # subgroup: collection (already a column after reset_index)
    subgroups = {}
    for col, g in pair.groupby("collection"):
        subgroups[col] = {
            "n": int(len(g)),
            "median_pct_change": float(g["pct_change"].median()),
            "iqr_pct_change": list(iqr(g["pct_change"].to_numpy())),
        }

    # covariates of paired cohort
    demo = (df[df["patient_id"].isin(pair["patient_id"])]
            .groupby("patient_id").agg(age=("age_years", "max"), sex=("sex", "first")))
    lat = (df[df["patient_id"].isin(pair["patient_id"])]
           .groupby("patient_id")["laterality"]
           .agg(lambda s: "bilateral" if {"left", "right"} <= set(s) else next(iter(s), "unknown")))

    # cross-validation vs the annotation tool's own ROI volumes (DICOM 3006,002C)
    both = df[(df["volume_ml"].notna()) & (df["dicom_roi_volume_ml"].notna())
              & (df["dicom_roi_volume_ml"] > 0)].copy()
    vol_val = {"n_rois": int(len(both))}
    if len(both) >= 10:
        both["signed_pct"] = (both["volume_ml"] - both["dicom_roi_volume_ml"]) / both["dicom_roi_volume_ml"] * 100
        both["abs_pct"] = both["signed_pct"].abs()
        both["phase"] = both["timepoint"].str.contains("Pre").map({True: "pre", False: "post"})
        rho = stats.spearmanr(both["volume_ml"], both["dicom_roi_volume_ml"]).statistic
        vol_val.update({
            "spearman_rho": float(rho),
            "median_abs_pct_diff": float(both["abs_pct"].median()),
            "iqr_abs_pct_diff": list(iqr(both["abs_pct"].to_numpy())),
            "size_corr_absdiff": float(stats.spearmanr(both["abs_pct"], both["dicom_roi_volume_ml"]).statistic),
        })
        for ph in ("pre", "post"):
            g = both[both["phase"] == ph]
            if len(g) >= 5:
                vol_val[f"{ph}_n"] = int(len(g))
                vol_val[f"{ph}_signed_median_pct"] = float(g["signed_pct"].median())
                vol_val[f"{ph}_abs_median_pct"] = float(g["abs_pct"].median())
                vol_val[f"{ph}_median_tool_vol_ml"] = float(g["dicom_roi_volume_ml"].median())

    # subjects excluded because their only post-treatment volume is post-operative/recurrence
    meta_wide = (df.assign(is_pre=df["timepoint"].str.contains("Pre"),
                           is_chemo=df["timepoint"].str.contains("chemo", case=False),
                           is_other_post=df["timepoint"].str.contains("Post") & ~df["timepoint"].str.contains("chemo", case=False))
                   .groupby("patient_id")[["is_pre", "is_chemo", "is_other_post"]].any())
    postop_only = int(((meta_wide["is_pre"]) & (~meta_wide["is_chemo"]) & (meta_wide["is_other_post"])).sum())

    # Table 1 — baseline by trial
    t1_rows = ["| Characteristic | AREN0532 (n={}) | AREN0533 (n={}) | AREN0534 (n={}) | Overall (n={}) |".format(
        subgroups.get("AREN0532", {}).get("n", 0), subgroups.get("AREN0533", {}).get("n", 0),
        subgroups.get("AREN0534", {}).get("n", 0), len(pair)),
        "|---|---|---|---|---|"]
    def _c(col, fn):
        g = pair[pair["collection"] == col] if col else pair
        return fn(g)
    def _med_iqr(g, v):
        if len(g) == 0: return "—"
        q = iqr(g[v].to_numpy())
        return f"{g[v].median():.1f} ({q[0]:.1f}–{q[1]:.1f})"
    t1_rows.append("| Pre-chemo volume, mL, median (IQR) | " + " | ".join(
        _med_iqr(pair[pair["collection"] == c], "pre") for c in ["AREN0532", "AREN0533", "AREN0534"]) +
        " | " + _med_iqr(pair, "pre") + " |")
    t1_rows.append("| First post-chemo volume, mL, median (IQR) | " + " | ".join(
        _med_iqr(pair[pair["collection"] == c], "post") for c in ["AREN0532", "AREN0533", "AREN0534"]) +
        " | " + _med_iqr(pair, "post") + " |")
    t1_rows.append("| Volume change, %, median (IQR) | " + " | ".join(
        _med_iqr(pair[pair["collection"] == c], "pct_change") for c in ["AREN0532", "AREN0533", "AREN0534"]) +
        " | " + _med_iqr(pair, "pct_change") + " |")
    # Age intentionally omitted: archive coarsening renders it near-uniform (see text).
    def sexcell(col):
        ids = pair.loc[pair["collection"] == col, "patient_id"] if col else pair["patient_id"]
        s = demo.loc[demo.index.intersection(ids), "sex"]
        return f"{(s == 'M').sum()}/{(s == 'F').sum()}"
    t1_rows.append("| Sex, male/female | " + " | ".join(
        sexcell(c) for c in ["AREN0532", "AREN0533", "AREN0534"]) + " | " + sexcell(None) + " |")
    def latcell(col):
        ids = pair.loc[pair["collection"] == col, "patient_id"] if col else pair["patient_id"]
        l = lat.loc[lat.index.intersection(ids)]
        return f"{(l == 'left').sum()}/{(l == 'right').sum()}/{(l == 'bilateral').sum()}"
    t1_rows.append("| Laterality, left/right/bilateral | " + " | ".join(
        latcell(c) for c in ["AREN0532", "AREN0533", "AREN0534"]) + " | " + latcell(None) + " |")
    table1_md = "\n".join(t1_rows)

    results = {
        "flow": {
            "metadata_subjects_any_kidney_seg": n_any_kidney,
            "metadata_paired_pre_post": n_paired_meta,
            "extracted_subjects_any_usable_ct_volume": int(st["patient_id"].nunique()),
            "paired_analyzed": int(len(pair)),
            "excluded_no_pre_or_post_volume": int(n_paired_meta - len(pair)),
        },
        "cohort": {
            "n": int(len(pair)),
            "age_median": float(demo["age"].median()),
            "age_iqr": list(iqr(demo["age"].dropna().to_numpy())),
            "age_min": float(demo["age"].min()),
            "age_max": float(demo["age"].max()),
            "sex_counts": {k: int(v) for k, v in demo["sex"].value_counts().items()},
            "laterality_counts": {k: int(v) for k, v in lat.value_counts().items()},
            "collection_counts": {k: int(v) for k, v in pair["collection"].value_counts().items()},
        },
        "primary": {
            "pre_median_ml": float(pair["pre"].median()), "pre_iqr_ml": list(iqr(pair["pre"].to_numpy())),
            "post_median_ml": float(pair["post"].median()), "post_iqr_ml": list(iqr(pair["post"].to_numpy())),
            "first_post_timepoint_counts": {str(int(k)): int(v) for k, v in pair["post_tp"].value_counts().items()},
            "pct_change_median": float(np.median(pc)),
            "pct_change_iqr": list(iqr(pc)),
            "pct_change_mean": float(pc.mean()),
            "hl_pseudomedian": hl,
            "hl_ci_95": [lo, hi],
            "n_decreased": int((pc < 0).sum()),
            "n_increased": int((pc > 0).sum()),
            "n_unchanged": int((pc == 0).sum()),
            "wilcoxon_statistic": float(w.statistic),
            "wilcoxon_p": float(w.pvalue),
        },
        "subgroups_by_collection": subgroups,
        "volume_validation": vol_val,
        "table1_md": table1_md,
        "flow_postop_only_excluded": postop_only,
    }

    # ---- figures ----
    FIGS.mkdir(parents=True, exist_ok=True)
    order = np.argsort(pc)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(range(len(pc)), pc[order], width=1.0,
           color=["#b2182b" if v > 0 else "#2166ac" for v in pc[order]])
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel(f"Subjects (n={len(pc)}, sorted)")
    ax.set_ylabel("Tumor volume change, pre → first post-chemo (%)")
    ax.set_title("Waterfall plot — volumetric response to neoadjuvant chemotherapy")
    fig.tight_layout()
    fig.savefig(FIGS / "waterfall.png", dpi=1200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 5))
    traj = st[st["patient_id"].isin(pair["patient_id"]) & st["tp_idx"].between(0, 4)]
    for pid, g in traj.groupby("patient_id"):
        g = g.sort_values("tp_idx")
        ax.plot(g["tp_idx"], g["volume_ml"], "-o", ms=2, lw=0.5, alpha=0.25, color="#999999")
    # per-trial median lines (trials are NOT time-aligned; no pooled median by design)
    trial_style = {"AREN0532": ("#1b9e77", "AREN0532 (delayed nephrectomy)"),
                   "AREN0533": ("#7570b3", "AREN0533 (stage III–IV)"),
                   "AREN0534": ("#d95f02", "AREN0534 (bilateral)")}
    col_of = wide.reset_index()[["patient_id", "collection"]].drop_duplicates().set_index("patient_id")["collection"]
    traj = traj.assign(collection=traj["patient_id"].map(col_of))
    cnt = traj.groupby("tp_idx")["patient_id"].nunique()
    for col, (color, label) in trial_style.items():
        med = traj[traj["collection"] == col].groupby("tp_idx")["volume_ml"].median()
        if len(med):
            ax.plot(med.index, med.values, "-o", color=color, lw=2, ms=4, label=label)
    ax.set_yscale("log")
    ax.set_xticks(sorted(cnt.index))
    labels = []
    for c in sorted(cnt.index):
        name = "Pre-dose" if c == 0 else f"Post-chemo #{int(c)}"
        labels.append(f"{name}\n(n={int(cnt[c])})")
    ax.set_xticklabels(labels)
    ax.set_ylabel("Kidney tumor volume (mL, log scale)")
    ax.set_title("Volume trajectories by trial (no pooled median: trials are not time-aligned)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGS / "trajectories.png", dpi=1200)
    plt.close(fig)

    with (DATA / "results.json").open("w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))
    print(f"\nWrote data/results.json, draft/figures/waterfall.png, draft/figures/trajectories.png")


if __name__ == "__main__":
    main()
