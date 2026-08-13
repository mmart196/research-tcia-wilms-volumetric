"""Feasibility probe for the proposed bilateral-discordance follow-up study.

EXPLORATORY. Written 2026-08-13 to answer one question: is there enough within-child
paired data to support a study of how differently the two synchronous tumors of a
bilateral Wilms patient respond to the same chemotherapy?

This is NOT analysis code and nothing it prints may be quoted in a manuscript. It reads
the committed volumes.csv, does no QC, and deliberately keeps outliers visible. If the
study gets past Gate 1 it needs a real analysis script with a protocol behind it, contour
QC on the extremes, and laterality established as something better than a parse of the
ROI label string.

Run from the manuscript folder:  python3 code/explore_bilateral_discordance.py
"""

import collections
import csv
import statistics as st

FIRST_POST = [
    "Post-chemotherapy #1",
    "Post-chemotherapy",
    "Post-chemotherapy #2",
    "Post-chemotherapy #3",
    "Post-chemotherapy #4",
]


def normalize_timepoint(label):
    """volumes.csv carries both 'Post-chemotherapy #2' and 'Post-Chemotherapy #2'."""
    return label.replace("Post-Chemotherapy", "Post-chemotherapy")


def load_volumes(path="data/volumes.csv"):
    """Sum CT-referenced ROI volumes per (patient, timepoint, side)."""
    totals = collections.defaultdict(float)
    with open(path) as fh:
        for row in csv.DictReader(fh):
            if row["source_class"] != "CT" or not row["volume_ml"].strip():
                continue
            key = (row["patient_id"], normalize_timepoint(row["timepoint"]), row["laterality"])
            totals[key] += float(row["volume_ml"])

    patients = collections.defaultdict(lambda: collections.defaultdict(dict))
    for (patient, timepoint, side), volume in totals.items():
        patients[patient][timepoint][side] = volume
    return patients


def pct_change(pre, post):
    return (post - pre) / pre * 100


def bilateral_pairs(patients):
    """Children with both kidneys contoured at Pre-dose and at one post-chemo timepoint."""
    pairs = []
    for patient, timepoints in patients.items():
        pre = timepoints.get("Pre-dose", {})
        if not {"left", "right"} <= set(pre):
            continue
        for label in FIRST_POST:
            post = timepoints.get(label, {})
            if {"left", "right"} <= set(post):
                left = pct_change(pre["left"], post["left"])
                right = pct_change(pre["right"], post["right"])
                pairs.append((patient, left, right, abs(left - right)))
                break
    return pairs


def serial_triples(patients):
    """Subjects with Pre-dose plus two successive post-chemotherapy timepoints."""
    triples = []
    for timepoints in patients.values():
        pre = sum(timepoints.get("Pre-dose", {}).values())
        first = timepoints.get("Post-chemotherapy #1") or timepoints.get("Post-chemotherapy")
        second = timepoints.get("Post-chemotherapy #2")
        if pre and first and second:
            triples.append((pre, sum(first.values()), sum(second.values())))
    return triples


def main():
    patients = load_volumes()

    pairs = bilateral_pairs(patients)
    gaps = sorted(pair[3] for pair in pairs)
    print(f"A) Bilateral, both kidneys paired on CT: n = {len(pairs)}")
    print(f"   median within-child |left - right| response gap: {st.median(gaps):.1f} pct pts")
    print(f"   IQR {gaps[len(gaps) // 4]:.1f} - {gaps[3 * len(gaps) // 4]:.1f}, max {gaps[-1]:.1f}")
    opposite = sum(1 for _, left, right, _ in pairs if (left > 0) != (right > 0))
    print(f"   one tumor grew while the other shrank: {opposite}")
    print(f"   gap > 30 pct pts: {sum(g > 30 for g in gaps)}, > 50: {sum(g > 50 for g in gaps)}")
    print("   NOTE: the maximum is large enough that the tail is probably contour error,")
    print("   not biology. QC before believing it.")

    triples = serial_triples(patients)
    incremental = [pct_change(first, second) for _, first, second in triples]
    print(f"\nB) Serial Pre-dose + post #1 + post #2 on CT: n = {len(triples)}")
    by_first = [pct_change(pre, first) for pre, first, _ in triples]
    by_second = [pct_change(pre, second) for pre, _, second in triples]
    print(f"   median change by post #1: {st.median(by_first):.1f}%")
    print(f"   median change by post #2: {st.median(by_second):.1f}%")
    print(f"   median incremental change, post #1 to post #2: {st.median(incremental):.1f}%")
    print(f"   volume rose between post #1 and post #2 in {sum(x > 0 for x in incremental)}")


if __name__ == "__main__":
    main()
