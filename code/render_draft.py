"""Render draft/manuscript.md from manuscript_template.md + data/results.json.

The template contains no results numbers — every statistic is a {token} filled
from results.json (itself written by analysis.py). This is the spec-R4 contract:
the manuscript literally cannot state a number the pipeline did not produce.

    python render_draft.py        # after analysis.py has run
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def fmt(x, nd=1):
    return f"{x:.{nd}f}"


def fmt_p(p):
    if p < 0.001:
        exp = math.floor(math.log10(p))
        mant = p / 10 ** exp
        return f"{mant:.1f} × 10<sup>{exp}</sup>"
    return f"{p:.3f}"


def main():
    res = json.load((DATA / "results.json").open())
    refs = json.load((ROOT / "draft" / "references.json").open())

    flow, coh, prim, subs = res["flow"], res["cohort"], res["primary"], res["subgroups_by_collection"]

    t = {
        # flow
        "F_META_ANY": flow["metadata_subjects_any_kidney_seg"],
        "F_META_PAIRED": flow["metadata_paired_pre_post"],
        "F_EXTRACTED": flow["extracted_subjects_any_usable_ct_volume"],
        "F_PAIRED": flow["paired_analyzed"],
        "F_EXCLUDED": flow["excluded_no_pre_or_post_volume"],
        # cohort
        "N": coh["n"],
        "AGE_MED": fmt(coh["age_median"]),
        "AGE_Q1": fmt(coh["age_iqr"][0]),
        "AGE_Q3": fmt(coh["age_iqr"][1]),
        "AGE_MIN": fmt(coh["age_min"]),
        "AGE_MAX": fmt(coh["age_max"]),
        "SEX_M": coh["sex_counts"].get("M", 0),
        "SEX_F": coh["sex_counts"].get("F", 0),
        "SEX_O": coh["sex_counts"].get("O", 0),
        "LAT_L": coh["laterality_counts"].get("left", 0),
        "LAT_R": coh["laterality_counts"].get("right", 0),
        "LAT_B": coh["laterality_counts"].get("bilateral", 0),
        "LAT_U": coh["laterality_counts"].get("unknown", 0),
        "C_0532": coh["collection_counts"].get("AREN0532", 0),
        "C_0533": coh["collection_counts"].get("AREN0533", 0),
        "C_0534": coh["collection_counts"].get("AREN0534", 0),
        # primary
        "PRE_MED": fmt(prim["pre_median_ml"]),
        "PRE_Q1": fmt(prim["pre_iqr_ml"][0]),
        "PRE_Q3": fmt(prim["pre_iqr_ml"][1]),
        "POST_MED": fmt(prim["post_median_ml"]),
        "POST_Q1": fmt(prim["post_iqr_ml"][0]),
        "POST_Q3": fmt(prim["post_iqr_ml"][1]),
        "PCT_MED": fmt(prim["pct_change_median"]),
        "PCT_Q1": fmt(prim["pct_change_iqr"][0]),
        "PCT_Q3": fmt(prim["pct_change_iqr"][1]),
        "N_DEC": prim["n_decreased"],
        "N_INC": prim["n_increased"],
        "W_STAT": fmt(prim["wilcoxon_statistic"], 0),
        "W_P": fmt_p(prim["wilcoxon_p"]),
        # subgroups
        "S0532_N": subs.get("AREN0532", {}).get("n", 0),
        "S0532_MED": fmt(subs.get("AREN0532", {}).get("median_pct_change", float("nan"))),
        "S0533_N": subs.get("AREN0533", {}).get("n", 0),
        "S0533_MED": fmt(subs.get("AREN0533", {}).get("median_pct_change", float("nan"))),
        "S0534_N": subs.get("AREN0534", {}).get("n", 0),
        "S0534_MED": fmt(subs.get("AREN0534", {}).get("median_pct_change", float("nan"))),
        # v2 additions
        "HL_EST": fmt(prim["hl_pseudomedian"]),
        "HL_LO": fmt(prim["hl_ci_95"][0]),
        "HL_HI": fmt(prim["hl_ci_95"][1]),
        "BILAT_SHARE": round(100 * subs.get("AREN0534", {}).get("n", 0) / max(coh["n"], 1)),
        "TABLE1_MD": res["table1_md"],
        "VVOL_N": res["volume_validation"]["n_rois"],
        "VVOL_RHO": fmt(res["volume_validation"].get("spearman_rho", float("nan")), 3),
        "VVOL_MEDDIFF": fmt(res["volume_validation"].get("median_abs_pct_diff", float("nan"))),
        "VVOL_PRE_SIGNED": fmt(res["volume_validation"].get("pre_signed_median_pct", float("nan"))),
        "VVOL_POST_SIGNED": fmt(res["volume_validation"].get("post_signed_median_pct", float("nan"))),
        "VVOL_PRE_ABS": fmt(res["volume_validation"].get("pre_abs_median_pct", float("nan"))),
        "VVOL_POST_ABS": fmt(res["volume_validation"].get("post_abs_median_pct", float("nan"))),
        "F_POSTOP": res["flow_postop_only_excluded"],
    }

    # Vancouver-style numbered reference list (all records PubMed-resolved)
    ref_lines = []
    for i, r in enumerate(refs, 1):
        auth = ", ".join(r["authors"][:6]) + (" et al" if len(r["authors"]) > 6 else "")
        vi = f";{r['volume']}" if r["volume"] else ""
        if r["issue"]:
            vi += f"({r['issue']})"
        pg = f":{r['pages']}" if r["pages"] else ""
        doi = f" doi:{r['doi']}" if r["doi"] else ""
        ref_lines.append(f"{i}. {auth}. {r['title']} {r['journal']}. {r['year']}{vi}{pg}.{doi} "
                         f"PMID: {r['pmid']}")
    t["REFERENCES"] = "\n".join(ref_lines)

    tpl = (ROOT / "draft" / "manuscript_template.md").read_text(encoding="utf-8")
    out = tpl
    missing = []
    for k, v in t.items():
        tag = "{" + k + "}"
        if tag not in out and k != "REFERENCES" or (k == "REFERENCES" and "{REFERENCES}" not in out):
            missing.append(k)
        out = out.replace(tag, str(v))
    leftover = [tok for tok in out.split("{")[1:] if "}" in tok and tok.split("}")[0].isupper()]
    if leftover:
        raise SystemExit(f"template tokens left unfilled: {[t.split('}')[0] for t in leftover]}")
    if missing:
        print(f"note: tokens defined but not used in template: {missing}")

    dest = ROOT / "draft" / "manuscript.md"
    dest.write_text(out, encoding="utf-8")
    print(f"Wrote {dest} ({len(out)} chars)")


if __name__ == "__main__":
    main()
