#!/usr/bin/env python3
"""
Synthetic validation S0–S2 for Φ₃–RECD preprint v0.2.

Produces:
  - figures/fig_S0_S1_S2_overview.png
  - figures/fig_A3_rates.png
  - figures/fig_noise_robustness.png
  - figures/results_table.md  (and .csv)

Run from project root or src/:
  python validate_synthetic.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

# allow import when run from src/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from phi3_recd import (  # noqa: E402
    ActivationConfig,
    P1Config,
    add_noise_to_series,
    gen_s0_null,
    gen_s1_latent,
    gen_s2_coupled_logistic,
    recd_base,
    recd_p1,
    recd_p2,
    summarize_run,
)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Hardened defaults (manuscript v0.2)
ACT = ActivationConfig()
# Optional stricter hard gate for rate reporting
ACT_HARD = ActivationConfig(soft=False)


def run_all_arms(seed_base: int = 10) -> list[dict]:
    rows = []
    arms = [
        gen_s0_null(seed=seed_base + 0),
        gen_s1_latent(seed=seed_base + 1),
        gen_s2_coupled_logistic(seed=seed_base + 2, regime="prechaos"),
        gen_s2_coupled_logistic(seed=seed_base + 3, regime="chaos"),
    ]
    for data in arms:
        soft = summarize_run(data, act_cfg=ACT, hard_act=False)
        hard = summarize_run(data, act_cfg=ACT_HARD, hard_act=True)
        row = {
            "arm": data["name"],
            **{f"soft_{k}": v for k, v in soft.items()},
            "hard_A3_rate": hard["A3_rate"],
            "hard_A3_mean": hard["A3_mean"],
        }
        rows.append(row)
    return rows


def noise_sweep(noise_levels=(0.0, 0.05, 0.10, 0.15), seed: int = 20) -> list[dict]:
    """Robustness on S1 and S2_chaos."""
    rows = []
    bases = [
        gen_s1_latent(seed=seed),
        gen_s2_coupled_logistic(seed=seed + 1, regime="chaos"),
        gen_s0_null(seed=seed + 2),
    ]
    for base in bases:
        for nl in noise_levels:
            data = add_noise_to_series(base, nl, seed=seed + int(100 * nl))
            # restore clean baseline name stem
            stem = base["name"]
            m = summarize_run(data, act_cfg=ACT)
            rows.append({
                "arm": stem,
                "noise": nl,
                "A3_rate": m["A3_rate"],
                "A3_mean": m["A3_mean"],
                "T_P1": m["T_P1"],
                "T_base": m["T_base"],
                "delta_T_P1": m["delta_T_P1"],
                "mean_Gamma3": m["mean_Gamma3"],
                "corr_Gamma_f3": m["corr_Gamma_f3"],
            })
    return rows


def write_tables(rows: list[dict], noise_rows: list[dict]) -> Path:
    md_path = FIG / "results_table.md"
    csv_path = FIG / "results_S0_S2.csv"
    noise_csv = FIG / "results_noise.csv"

    keys = [
        "arm", "soft_T_base", "soft_T_P1", "soft_T_P2",
        "soft_A3_rate", "hard_A3_rate", "soft_A3_mean",
        "soft_mean_Gamma3", "soft_mean_rho3_P2", "soft_mean_rho3_marg_P1",
        "soft_corr_Gamma_f3", "soft_delta_T_P1", "soft_delta_T_P2",
    ]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    with noise_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(noise_rows[0].keys()))
        w.writeheader()
        w.writerows(noise_rows)

    def fmt(x, nd=3):
        if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))):
            return "—"
        if isinstance(x, float):
            return f"{x:.{nd}f}"
        return str(x)

    lines = [
        "# Synthetic validation results (v0.2, hardened A₃)",
        "",
        "Defaults: `ActivationConfig` v0.2 (require_change, residual C, dual-scale, adaptive θ_e).",
        "",
        "## S0–S2 summary",
        "",
        "| Arm | T_base | T_P1 | T_P2 | A3 rate (soft>0.5) | A3 rate hard | mean Γ₃ | ρ₃ P2 | ρ₃_marg P1 | corr(Γ−1, f₃) | ΔT_P1 |",
        "|-----|--------|------|------|--------------------|--------------|---------|-------|------------|---------------|-------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['arm']} | {fmt(r['soft_T_base'], 2)} | {fmt(r['soft_T_P1'], 2)} | {fmt(r['soft_T_P2'], 2)} "
            f"| {fmt(r['soft_A3_rate'])} | {fmt(r['hard_A3_rate'])} | {fmt(r['soft_mean_Gamma3'])} "
            f"| {fmt(r['soft_mean_rho3_P2'])} | {fmt(r['soft_mean_rho3_marg_P1'])} "
            f"| {fmt(r['soft_corr_Gamma_f3'])} | {fmt(r['soft_delta_T_P1'], 2)} |"
        )

    lines += [
        "",
        "## Noise robustness (A3 rate soft>0.5)",
        "",
        "| Arm | noise | A3_rate | mean Γ₃ | ΔT_P1 | corr(Γ−1,f₃) |",
        "|-----|-------|---------|---------|-------|--------------|",
    ]
    for r in noise_rows:
        lines.append(
            f"| {r['arm']} | {int(100 * r['noise'])}% | {fmt(r['A3_rate'])} | {fmt(r['mean_Gamma3'])} "
            f"| {fmt(r['delta_T_P1'], 2)} | {fmt(r['corr_Gamma_f3'])} |"
        )

    lines += [
        "",
        "## Interpretation checklist",
        "",
        "- **S0:** A3 hard rate should be near 0; soft rate low; ΔT_P1 small.",
        "- **S1:** A3 higher than S0; |Δẽ₃| drives activation despite surplus *drop*.",
        "- **S2 chaos vs prechaos:** Γ₃, ρ₃, A3 higher in chaos.",
        "- **Noise:** graceful degradation, not collapse of discrimination.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def _try_import_matplotlib():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except Exception as e:
        print(f"[warn] matplotlib unavailable ({e}); skipping PNG figures.")
        return None


def plot_overview(plt, seed: int = 10) -> None:
    arms = [
        gen_s0_null(seed=seed),
        gen_s1_latent(seed=seed + 1),
        gen_s2_coupled_logistic(seed=seed + 3, regime="chaos"),
    ]
    fig, axes = plt.subplots(len(arms), 3, figsize=(11, 2.6 * len(arms)), sharex=False)
    if len(arms) == 1:
        axes = np.array([axes])

    for i, data in enumerate(arms):
        base = recd_base(data["tau"])
        p1 = recd_p1(
            data["tau"], data["e3"], data["baseline"],
            phi1=data["phi1"], phi2=data["phi2"], n_vars=4, act_cfg=ACT,
        )
        p2 = recd_p2(
            data["tau"], data["e3"], data["baseline"],
            phi1=data["phi1"], phi2=data["phi2"], f3=data["f3"], n_vars=4, act_cfg=ACT,
        )
        t_idx = np.arange(len(data["tau"]))

        ax = axes[i, 0]
        ax.plot(t_idx, data["tau"], color="#444", lw=0.9, label=r"$\tau_s$")
        ax.axhline(0.41, color="C1", ls="--", lw=0.7)
        ax.axhline(-0.41, color="C1", ls="--", lw=0.7)
        ax.set_ylabel(data["name"])
        if i == 0:
            ax.set_title(r"$\tau_s$")
        ax.legend(loc="upper right", fontsize=7)

        ax = axes[i, 1]
        ax.plot(t_idx, data["e3"], color="C0", lw=0.9, label="excess³")
        ax2 = ax.twinx()
        ax2.plot(t_idx, p1["A3"], color="C3", lw=0.9, alpha=0.85, label="A3")
        ax2.set_ylim(-0.05, 1.05)
        if i == 0:
            ax.set_title("excess³ and A₃")
        ax.legend(loc="upper left", fontsize=7)
        ax2.legend(loc="upper right", fontsize=7)

        ax = axes[i, 2]
        ax.plot(base["t"], label="base", color="#666", lw=1.0)
        ax.plot(p1["t"], label="P1", color="C2", lw=1.0)
        ax.plot(p2["t"], label="P2", color="C4", lw=1.0)
        if i == 0:
            ax.set_title(r"$T_{\mathrm{RECD}}$")
        ax.legend(loc="upper left", fontsize=7)

    fig.suptitle("S0 / S1 / S2-chaos — hardened $A_3$", fontsize=12, y=1.01)
    fig.tight_layout()
    out = FIG / "fig_S0_S1_S2_overview.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def plot_a3_rates(plt, rows: list[dict]) -> None:
    arms = [r["arm"] for r in rows]
    soft = [r["soft_A3_rate"] for r in rows]
    hard = [r["hard_A3_rate"] for r in rows]
    x = np.arange(len(arms))
    w = 0.35
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x - w / 2, soft, w, label="soft A3 > 0.5", color="C0")
    ax.bar(x + w / 2, hard, w, label="hard A3", color="C3")
    ax.axhline(0.05, color="k", ls="--", lw=0.8, label="5% target (S0)")
    ax.set_xticks(x)
    ax.set_xticklabels(arms, rotation=15, ha="right")
    ax.set_ylabel("Activation rate")
    ax.set_title("$A_3$ activation rates by regime")
    ax.legend(fontsize=8)
    ax.set_ylim(0, max(0.2, max(soft + hard) * 1.25))
    fig.tight_layout()
    out = FIG / "fig_A3_rates.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"wrote {out}")


def plot_noise(plt, noise_rows: list[dict]) -> None:
    arms = sorted(set(r["arm"] for r in noise_rows))
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for arm in arms:
        sub = [r for r in noise_rows if r["arm"] == arm]
        sub = sorted(sub, key=lambda r: r["noise"])
        xs = [100 * r["noise"] for r in sub]
        axes[0].plot(xs, [r["A3_rate"] for r in sub], "o-", label=arm)
        axes[1].plot(xs, [r["delta_T_P1"] for r in sub], "s-", label=arm)
    axes[0].set_xlabel("Noise (%)")
    axes[0].set_ylabel("A3 rate (soft>0.5)")
    axes[0].set_title("Activation vs noise")
    axes[0].legend(fontsize=7)
    axes[1].set_xlabel("Noise (%)")
    axes[1].set_ylabel(r"$\Delta T_{P1}$")
    axes[1].set_title("Clock gain vs noise")
    axes[1].legend(fontsize=7)
    fig.suptitle("Noise robustness (5–15%)", fontsize=11)
    fig.tight_layout()
    out = FIG / "fig_noise_robustness.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"wrote {out}")


def plot_clock_bars(plt, rows: list[dict]) -> None:
    arms = [r["arm"] for r in rows]
    x = np.arange(len(arms))
    w = 0.25
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x - w, [r["soft_T_base"] for r in rows], w, label="base", color="#888")
    ax.bar(x, [r["soft_T_P1"] for r in rows], w, label="P1", color="C2")
    ax.bar(x + w, [r["soft_T_P2"] for r in rows], w, label="P2", color="C4")
    ax.set_xticks(x)
    ax.set_xticklabels(arms, rotation=15, ha="right")
    ax.set_ylabel(r"$T_{\mathrm{final}}$")
    ax.set_title("Final RECD time: base vs P1 vs P2")
    ax.legend()
    fig.tight_layout()
    out = FIG / "fig_T_final.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    print("Running S0–S2 synthetic validation (v0.2)...")
    rows = run_all_arms()
    noise_rows = noise_sweep()
    md = write_tables(rows, noise_rows)
    print(f"wrote {md}")

    # print compact console summary
    print("\n=== Summary ===")
    for r in rows:
        print(
            f"{r['arm']:14s}  A3_soft={r['soft_A3_rate']:.3f}  A3_hard={r['hard_A3_rate']:.3f}  "
            f"Γ={r['soft_mean_Gamma3']:.3f}  ΔT_P1={r['soft_delta_T_P1']:+.2f}  "
            f"ρ3={r['soft_mean_rho3_P2']:.3f}  corr={r['soft_corr_Gamma_f3']}"
        )

    # sanity gates (soft warnings, not hard fails)
    s0 = next(r for r in rows if r["arm"] == "S0")
    s2c = next(r for r in rows if r["arm"] == "S2_chaos")
    s2p = next(r for r in rows if r["arm"] == "S2_prechaos")
    ok_s0 = s0["hard_A3_rate"] <= 0.08
    ok_s2 = s2c["soft_mean_Gamma3"] > s2p["soft_mean_Gamma3"]
    print(f"\nGate S0 hard A3 ≲ 8%: {'PASS' if ok_s0 else 'CHECK'} ({s0['hard_A3_rate']:.3f})")
    print(f"Gate S2 chaos Γ > prechaos Γ: {'PASS' if ok_s2 else 'CHECK'}")

    plt = _try_import_matplotlib()
    if plt is not None:
        plot_overview(plt)
        plot_a3_rates(plt, rows)
        plot_noise(plt, noise_rows)
        plot_clock_bars(plt, rows)
    print("\nDone.")


if __name__ == "__main__":
    main()
