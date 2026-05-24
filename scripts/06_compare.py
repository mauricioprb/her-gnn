"""Compare ETR vs SchNet from results/ only — never trains.

Usage:
    uv run python scripts/06_compare.py

Reads results/summary.json + each run's predictions.parquet (+ SchNet
embeddings.npy) and writes results/comparison_table.md and results/figures/.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger("compare")

RESULTS = Path("results")
FIG_DIR = RESULTS / "figures"


def latest_run(summary: list[dict], name_contains: str) -> dict | None:
    runs = [e for e in summary if name_contains in e["name"]]
    return max(runs, key=lambda e: e["timestamp"]) if runs else None


def _fmt(v) -> str:
    return f"{v:.3f}" if isinstance(v, (int, float)) and v is not None else "—"


def comparison_table(entries: list[dict]) -> str:
    header = "| Modelo | R² test | MAE test | RMSE test | # params | Tempo (s) |\n"
    header += "|---|---|---|---|---|---|\n"
    rows = []
    for e in entries:
        params = e.get("n_params")
        rows.append(
            f"| {e['name']} | {_fmt(e.get('r2_test'))} | {_fmt(e.get('mae_test'))} | "
            f"{_fmt(e.get('rmse_test'))} | {params if params else '—'} | "
            f"{_fmt(e.get('elapsed_sec'))} |"
        )
    return header + "\n".join(rows) + "\n"


def load_test_preds(entry: dict) -> pd.DataFrame:
    df = pd.read_parquet(Path(entry["run_dir"]) / "predictions.parquet")
    return df[df["split"] == "test"]


def plot_scatter(etr: pd.DataFrame, schnet: pd.DataFrame) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    for ax, df, title, color in [
        (axes[0], etr, "ETR", "#4c72b0"),
        (axes[1], schnet, "SchNet", "#dd8452"),
    ]:
        ax.scatter(df["y_true"], df["y_pred"], s=12, alpha=0.5, color=color, edgecolors="none")
        lo = min(df["y_true"].min(), df["y_pred"].min())
        hi = max(df["y_true"].max(), df["y_pred"].max())
        ax.plot([lo, hi], [lo, hi], "--", color="0.3", lw=1)
        r2 = 1 - ((df["y_true"] - df["y_pred"]) ** 2).sum() / (
            (df["y_true"] - df["y_true"].mean()) ** 2).sum()
        ax.set_title(f"{title}  ($R^2$={r2:.3f})")
        ax.set_xlabel(r"DFT $\Delta G_H$ (eV)")
        ax.set_ylabel(r"pred $\Delta G_H$ (eV)")
        ax.set_aspect("equal", "box")
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_error_hist(etr: pd.DataFrame, schnet: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(etr["y_pred"] - etr["y_true"], bins=50, alpha=0.6, label="ETR", color="#4c72b0")
    ax.hist(schnet["y_pred"] - schnet["y_true"], bins=50, alpha=0.6, label="SchNet", color="#dd8452")
    ax.set_xlabel(r"erro: pred - DFT (eV)")
    ax.set_ylabel("count")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    return fig


def plot_umap(schnet_entry: dict) -> plt.Figure | None:
    emb_path = Path(schnet_entry["run_dir"]) / "embeddings.npy"
    if not emb_path.exists():
        logger.warning("no embeddings.npy, skipping UMAP")
        return None
    try:
        import umap
    except ImportError:
        logger.warning("umap-learn not installed, skipping UMAP")
        return None
    emb = np.load(emb_path)
    y = np.load(emb_path.with_name("embeddings_y.npy"))
    coords = umap.UMAP(random_state=42).fit_transform(emb)
    fig, ax = plt.subplots(figsize=(6, 5))
    sc = ax.scatter(coords[:, 0], coords[:, 1], c=y, cmap="viridis", s=14, alpha=0.8)
    fig.colorbar(sc, label=r"$\Delta G_H$ (eV)")
    ax.set_title("UMAP dos embeddings SchNet")
    ax.set_xlabel("UMAP-1")
    ax.set_ylabel("UMAP-2")
    return fig


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    summary = json.loads((RESULTS / "summary.json").read_text())

    etr = latest_run(summary, "etr")
    schnet = latest_run(summary, "schnet")
    entries = [e for e in (etr, schnet) if e]
    if not entries:
        logger.error("no runs in summary.json")
        return

    table = comparison_table(entries)
    (RESULTS / "comparison_table.md").write_text(table)
    print(table)

    if etr and schnet:
        etr_p, schnet_p = load_test_preds(etr), load_test_preds(schnet)
        plot_scatter(etr_p, schnet_p).savefig(FIG_DIR / "scatter_etr_vs_schnet.png", dpi=300)
        plot_error_hist(etr_p, schnet_p).savefig(FIG_DIR / "error_hist.png", dpi=300)
    if schnet:
        fig = plot_umap(schnet)
        if fig is not None:
            fig.savefig(FIG_DIR / "umap_schnet_embeddings.png", dpi=300)
    logger.info("comparison written to %s", RESULTS)


if __name__ == "__main__":
    main()
