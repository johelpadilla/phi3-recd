"""Smoke and contract tests for phi3-recd (clock maps, not new metrics)."""

from __future__ import annotations

import numpy as np
import pytest

from phi3_recd import (
    ALPHA_SURP,
    ALPHA_SYN,
    DELTA_FEIGENBAUM,
    TAU_CH,
    ActivationConfig,
    P1Config,
    __version__,
    activation_A3,
    gen_s0_null,
    gen_s1_latent,
    normalize_vs_baseline,
    recd_base,
    recd_p1,
    recd_p2,
    residual_synergy_score,
    summarize_run,
)


def test_version():
    assert __version__ == "0.5.0"


def test_constants_match_preprint():
    assert ALPHA_SYN == 0.6
    assert ALPHA_SURP == 0.4
    assert abs(ALPHA_SYN + ALPHA_SURP - 1.0) < 1e-12
    assert TAU_CH == 0.41
    assert abs(DELTA_FEIGENBAUM - 4.6692016091) < 1e-9


def test_beta0_ablation_exact():
    """β=0 recovers the base clock exactly (manuscript audit claim)."""
    data = gen_s1_latent(seed=11)
    base = recd_base(data["tau"])
    p1 = recd_p1(
        data["tau"],
        data["e3"],
        data["baseline"],
        phi1=data["phi1"],
        phi2=data["phi2"],
        n_vars=4,
        cfg=P1Config(beta=0.0),
    )
    assert np.allclose(base["t"], p1["t"], rtol=0, atol=1e-12)
    assert np.allclose(p1["gamma3"], 1.0, rtol=0, atol=1e-12)
    assert float(np.max(np.abs(p1["t"] - base["t"]))) == 0.0


def test_s0_hardened_gate_stays_quiet():
    """Null arm: hardish A₃ rate near zero under hardened defaults."""
    data = gen_s0_null(seed=10)
    summary = summarize_run(data, act_cfg=ActivationConfig(), hard_act=False)
    assert summary["A3_rate"] < 0.05
    assert summary["mean_Gamma3"] < 1.1


def test_s1_gamma_tracks_f3():
    data = gen_s1_latent(seed=12)
    summary = summarize_run(data)
    assert summary["A3_rate"] > 0.05
    assert summary["corr_Gamma_f3"] > 0.5 or np.isnan(summary["corr_Gamma_f3"])


def test_p1_shapes_and_gamma_bounds():
    data = gen_s0_null(seed=1)
    out = recd_p1(
        data["tau"],
        data["e3"],
        data["baseline"],
        phi1=data["phi1"],
        phi2=data["phi2"],
        n_vars=4,
    )
    T = len(data["tau"])
    # cumulative index includes t[0]=0 → length T+1; per-step series length T
    assert out["t"].shape == (T + 1,)
    assert out["gamma3"].shape == (T,)
    assert out["A3"].shape == (T,)
    assert np.all(out["gamma3"] >= 1.0 - 1e-12)
    assert np.all(np.diff(out["t"]) >= -1e-12)


def test_p2_rho3_in_unit_interval():
    data = gen_s1_latent(seed=3)
    out = recd_p2(
        data["tau"],
        data["e3"],
        data["baseline"],
        phi1=data["phi1"],
        phi2=data["phi2"],
        f3=data["f3"],
        n_vars=4,
    )
    assert np.all(out["rho3"] >= -1e-12)
    assert np.all(out["rho3"] <= 1.0 + 1e-12)


def test_residual_synergy_score_bounds():
    sB = np.array([0.0, 0.5, 2.0])
    phi1 = np.array([0.3, 0.3, 0.3])
    phi2 = np.array([0.2, 0.2, 0.2])
    r = residual_synergy_score(sB, phi1, phi2)
    assert np.all(r >= 0.0)
    assert np.all(r <= 1.0 + 1e-12)


def test_activation_requires_change_by_default():
    T = 80
    tau = np.full(T, 0.05)  # chaos band
    e3 = np.full(T, 3.0)  # elevated flat surplus
    baseline = np.zeros(T, dtype=bool)
    baseline[:20] = True
    e3n = normalize_vs_baseline(e3, baseline)
    cfg = ActivationConfig(require_change=True, soft=False)
    a3 = activation_A3(tau, e3n, n_vars=4, cfg=cfg, abs_delta=True)
    # Flat elevated surplus should not fully open a hard gate
    assert float(np.mean(a3[30:])) < 0.5
