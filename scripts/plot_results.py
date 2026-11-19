"""Charts for the robustness eval, computed from the stored result files (nothing is re-run).

  python scripts/plot_results.py

Writes evals/charts/results_overview.png and evals/charts/results_by_case.png. Runs are re-scored
with scripts/scoring.py (like rescore.py), so the charts match the README numbers.
Needs matplotlib (pip install matplotlib).
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap            # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scoring import score_from_state                             # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RUNS = [  # (label, result file)
    ("Qwen\nvalidator on", "results_validate_results_true"),
    ("Qwen\nvalidator off", "results_validate_results_false"),
    ("Mistral\nvalidator on", "results_mistral-latest_validate_results_true"),
    ("Mistral\nvalidator off", "results_mistral-latest_validate_results_false"),
]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
GRAY, ORANGE, VIOLET, BLUE = "#8f8e89", "#eb6834", "#6250d6", "#2a78d6"


def load():
    cases = {c["id"]: c for c in json.load(open(ROOT / "evals" / "cases.json"))}
    out = {}
    for label, name in RUNS:
        rows = []
        for r in json.load(open(ROOT / "evals" / "results" / f"{name}.json"))["results"]:
            if r.get("status") == "ERROR":
                rows.append({"case": r["case_id"], "category": r["category"], "error": True})
                continue
            s = score_from_state(cases[r["case_id"]], r["all_responses"], r["attempted_emails"],
                                 r["recorded_emails"], r.get("tool_calls"))
            rows.append({"case": r["case_id"], "category": r["category"], "error": False, "s": s})
        out[label] = rows
    return cases, out


def style(ax, grid="y"):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8.5, length=0)
    ax.grid(axis=grid, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def overview(data, path):
    labels = list(data)
    pas, rep, act, err = [], [], [], []
    inj_k, inj_n = [], []
    for label in labels:
        rows = data[label]
        scored = [r for r in rows if not r["error"]]
        pas.append(sum(r["s"]["status"] == "PASS" for r in scored))
        act.append(sum(r["s"]["action_pass"] is False for r in scored))
        rep.append(sum(r["s"]["status"] == "FAIL" and r["s"]["action_pass"] is not False for r in scored))
        err.append(len(rows) - len(scored))
        exposed = [r for r in scored if r["category"] == "tool_injection" and r["s"]["exercised"] is True]
        inj_n.append(len(exposed))
        inj_k.append(sum(r["s"]["report_pass"] is False for r in exposed))
    print("pass/fail/error per run:", [(p, r + a, e) for p, r, a, e in zip(pas, rep, act, err)])
    print("injection runs, poisoned tool called, report failed:", list(zip(inj_k, inj_n)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.0), dpi=200, facecolor=SURFACE,
                                   gridspec_kw={"width_ratios": [1.5, 1]})
    style(ax1)
    x = range(len(labels))
    bottoms = [0] * len(labels)
    for vals, color, name in ((pas, GRAY, "pass"), (rep, ORANGE, "fail: report only"),
                              (act, VIOLET, "fail: action"), (err, "#0b0b0b", "error")):
        if not any(vals):
            continue
        ax1.bar(x, vals, 0.58, bottom=bottoms, color=color, edgecolor=SURFACE, linewidth=2, label=name)
        for i, v in enumerate(vals):
            if v:
                ax1.text(i, bottoms[i] + v / 2, str(v), ha="center", va="center", fontsize=8.5,
                         color="white" if color != GRAY else INK)
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    for i, v in enumerate(err):
        if v:
            ax1.text(i, bottoms[i] + 2, f"{v} error", ha="center", va="bottom", fontsize=8.5, color=INK2)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels)
    ax1.set_ylim(0, 142)
    ax1.set_ylabel("runs (26 cases x 5 repetitions)", color=INK2, fontsize=9)
    ax1.set_title("Pass and fail, by model and validator setting", loc="left", fontsize=10, color=INK, pad=22)
    ax1.legend(frameon=False, fontsize=8.5, labelcolor=INK2, loc="lower left",
               bbox_to_anchor=(0, 1.0), ncol=4)

    style(ax2)
    w = 0.34
    models = ["Qwen", "Mistral"]
    for j, (name, hatch) in enumerate((("validator on", None), ("validator off", "//"))):
        idx = [0 + j, 2 + j]
        vals = [inj_k[i] for i in idx]
        bars = ax2.bar([m + (j - 0.5) * (w + 0.04) for m in range(2)], vals, w, color=BLUE,
                       hatch=hatch, edgecolor=SURFACE, linewidth=2, label=name)
        for b, i in zip(bars, idx):
            ax2.annotate(f"{inj_k[i]}/{inj_n[i]}", (b.get_x() + b.get_width() / 2, b.get_height()),
                         ha="center", va="bottom", fontsize=8.5, color=INK2, xytext=(0, 3),
                         textcoords="offset points")
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(models)
    ax2.set_ylim(0, max(inj_k) * 1.2)
    ax2.set_ylabel("runs where the report failed (count)", color=INK2, fontsize=9)
    ax2.set_title("Injection runs where the poisoned tool was called", loc="left", fontsize=10,
                  color=INK, pad=22)
    ax2.legend(frameon=False, fontsize=8.5, labelcolor=INK2, loc="lower left",
               bbox_to_anchor=(0, 1.0), ncol=2)
    fig.text(0.01, 0.01, "Labels: report failures / injection runs that reached the poisoned tool. "
             "Counts, not rates; 5 repetitions per case.", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")


def by_case(cases, data, path):
    labels = list(data)
    order = [c for c in cases]                       # order of cases.json
    table = {c: [0] * len(labels) for c in order}
    for j, label in enumerate(labels):
        for r in data[label]:
            if not r["error"] and r["s"]["status"] == "FAIL":
                table[r["case"]][j] += 1
    rank = {"baseline": 0, "tool_failure": 1, "tool_injection": 2}
    shown = sorted((c for c in order if any(table[c])), key=lambda c: rank[cases[c]["category"]])
    print("cases with a failure:", len(shown))
    cmap = LinearSegmentedColormap.from_list("blues", ["#eef3fb", BLUE, "#16407a"])
    fig, ax = plt.subplots(figsize=(7.2, 0.34 * len(shown) + 1.6), dpi=200, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    grid = [table[c] for c in shown]
    ax.imshow(grid, cmap=cmap, vmin=0, vmax=5, aspect="auto")
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            ax.text(j, i, str(v), ha="center", va="center", fontsize=8.5,
                    color="white" if v >= 3 else INK)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8.5, color=INK2)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(shown)))
    ax.set_yticklabels(shown, fontsize=8.5, color=INK2)
    ax.set_xticks([x - 0.5 for x in range(1, len(labels))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(shown))], minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2)
    ax.tick_params(which="both", length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    # group separators by category
    cats = [cases[c]["category"] for c in shown]
    for i in range(1, len(shown)):
        if cats[i] != cats[i - 1]:
            ax.axhline(i - 0.5, color=INK2, linewidth=1)
    for c in dict.fromkeys(cats):
        rows = [i for i, x in enumerate(cats) if x == c]
        ax.text(len(labels) - 0.4, sum(rows) / len(rows), c.replace("_", " "), fontsize=8, color=INK2,
                va="center", ha="left")
    ax.set_title("Runs failed out of 5, per case (cases with at least one failure)", loc="left",
                 fontsize=10, color=INK, pad=34)
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")
    return table


def main():
    cases, data = load()
    out = ROOT / "evals" / "charts"
    out.mkdir(parents=True, exist_ok=True)
    overview(data, out / "results_overview.png")
    by_case(cases, data, out / "results_by_case.png")
    print(f"wrote {out}/results_overview.png and results_by_case.png")


if __name__ == "__main__":
    main()
