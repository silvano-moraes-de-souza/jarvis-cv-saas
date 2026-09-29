"""Chart the ATS score composition straight from api/app/config.py.

    python scripts/chart_ats_weights.py   ->  docs/ats_weights.png
"""

import ast
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
tree = ast.parse((ROOT / "api" / "app" / "config.py").read_text(encoding="utf-8"))
weights = next(
    ast.literal_eval(node.value)
    for node in ast.walk(tree)
    if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "ats_weights"
)
labels = {
    "keyword_match": "Keyword match",
    "skill_density": "Skill density",
    "structure_quality": "Structure",
    "seniority_alignment": "Seniority alignment",
    "experience_relevance": "Experience relevance",
    "format_ats_compatibility": "ATS-safe format",
}
items = sorted(weights.items(), key=lambda kv: kv[1])
fig, ax = plt.subplots(figsize=(8, 3.6), dpi=150)
for f in (fig, ax):
    f.set_facecolor("#fcfcfb")
y = range(len(items))
ax.barh(y, [v * 100 for _, v in items], height=0.55, color="#2a78d6", zorder=2)
for yi, (_, v) in zip(y, items, strict=True):
    ax.text(v * 100 + 0.6, yi, f"{v:.0%}", va="center", fontsize=9, color="#0b0b0b")
ax.set_yticks(list(y), [labels.get(k, k) for k, _ in items], fontsize=9, color="#0b0b0b")
ax.set_xlim(0, 36)
ax.set_xlabel("Weight in the 0-100 score (%)", color="#52514e", fontsize=9)
ax.tick_params(axis="x", colors="#52514e", labelsize=8)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color="#e4e3df", linewidth=0.8, zorder=0)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color("#e4e3df")
ax.set_title("How the ATS score is built (deterministic, computed in Python)", loc="left",
             fontsize=10, color="#0b0b0b", pad=10)  # fmt: skip
fig.tight_layout()
out = ROOT / "docs" / "ats_weights.png"
fig.savefig(out, facecolor="#fcfcfb")
print(out)
