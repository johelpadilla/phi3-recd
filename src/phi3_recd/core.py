"""
Core maps: integrate Φ₃ (excess³) into RECD clock updates.

Proposals (preprint v0.5):
  (P1) Conservative multiplicative gain Γ₃ on legacy RECD increment
  (P2) Dual-channel advance with optional depth compression (J=0 by default)

Hardened activation A₃:
  - (B) level + change (|Δẽ₃|)
  - (C) residual synergistic fraction (not bare ratio)
  - (D) dual-scale: short detection + medium persistence
  - optional adaptive θ_e from baseline MAD/CV
  - rank-based normalization and abs-delta forms explicit

Self-contained (NumPy only). This module does **not** recompute excess³;
pass precomputed τ_s / excess³ (and optional Φ₁, Φ₂) from nested-recd or
an equivalent pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

import numpy as np

DELTA_FEIGENBAUM = 4.6692016091
TAU_CH = 0.41
TAU_ST = 0.50
ALPHA_SYN = 0.6
ALPHA_SURP = 0.4
EPS = 1e-12


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------

def softplus(x: np.ndarray | float) -> np.ndarray | float:
    x = np.asarray(x, dtype=float)
    return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0.0)


def logistic(x: np.ndarray | float) -> np.ndarray | float:
    x = np.asarray(x, dtype=float)
    return 1.0 / (1.0 + np.exp(-x))


def gate_piecewise(tau_s: float, tau_ch: float = TAU_CH, tau_st: float = TAU_ST) -> float:
    """Legacy piecewise gate g(τ_s)."""
    if tau_s >= tau_st:
        return 1.0
    if tau_s <= -tau_ch:
        return -1.0
    if abs(tau_s) < tau_ch:
        return ((DELTA_FEIGENBAUM - 1.0) / DELTA_FEIGENBAUM) * (tau_ch - abs(tau_s)) / tau_ch
    return 0.5


def base_interval(
    tau_s: float,
    run_depth: int,
    delta_t0: float = 1.0,
    tau_ch: float = TAU_CH,
    delta: float = DELTA_FEIGENBAUM,
    max_depth: int = 8,
) -> float:
    """Δt_base with Feigenbaum compression in chaotic band."""
    k = int(np.clip(run_depth, 0, max_depth))
    if abs(tau_s) < tau_ch:
        return (delta ** (-k)) * abs(tau_s) * delta_t0
    return delta_t0


def normalize_vs_baseline(
    e3: np.ndarray,
    baseline_mask: np.ndarray,
    mode: str = "zscore",
) -> np.ndarray:
    """
    Normalize excess³ series using baseline window only.

    mode:
      "zscore" — (x − μ_B) / σ_B
      "rank"   — 2 F̂_B(x) − 1  (robust to non-Gaussian tails)
      "mad"    — (x − med_B) / (1.4826 · MAD_B)
    """
    e3 = np.asarray(e3, dtype=float)
    b = np.asarray(baseline_mask, dtype=bool)
    if b.sum() < 3:
        med = np.nanmedian(e3)
        mad = np.nanmedian(np.abs(e3 - med)) + EPS
        return (e3 - med) / (1.4826 * mad)

    base = e3[b]
    mode = mode.lower()
    if mode == "rank":
        sorted_base = np.sort(base)
        n = len(sorted_base)
        idx = np.searchsorted(sorted_base, e3, side="right")
        return 2.0 * (idx / max(n, 1)) - 1.0
    if mode == "mad":
        med = float(np.nanmedian(base))
        mad = float(np.nanmedian(np.abs(base - med))) + EPS
        return (e3 - med) / (1.4826 * mad)
    # zscore (default)
    mu = float(np.nanmean(base))
    sd = float(np.nanstd(base)) + EPS
    return (e3 - mu) / sd


def baseline_scale_stats(e3: np.ndarray, baseline_mask: np.ndarray) -> Dict[str, float]:
    """Baseline μ, σ, MAD, CV for adaptive thresholds."""
    e3 = np.asarray(e3, dtype=float)
    b = np.asarray(baseline_mask, dtype=bool)
    if b.sum() < 3:
        x = e3
    else:
        x = e3[b]
    mu = float(np.nanmean(x))
    sd = float(np.nanstd(x)) + EPS
    med = float(np.nanmedian(x))
    mad = float(np.nanmedian(np.abs(x - med))) + EPS
    cv = sd / (abs(mu) + EPS)
    return {"mu": mu, "sd": sd, "med": med, "mad": mad, "cv": cv}


def run_depth_series(in_chaos: np.ndarray) -> np.ndarray:
    """Consecutive depth counter while in chaotic band."""
    in_chaos = np.asarray(in_chaos, dtype=bool)
    depth = np.zeros(len(in_chaos), dtype=int)
    d = 0
    for i, flag in enumerate(in_chaos):
        if flag:
            d += 1
        else:
            d = 0
        depth[i] = d
    return depth


def persistence_series(in_chaos: np.ndarray) -> np.ndarray:
    """Current run length P(k) while in chaos (same as depth here)."""
    return run_depth_series(in_chaos)


def rolling_count(mask: np.ndarray, window: int) -> np.ndarray:
    """Number of True values in [k−window+1, k] (causal)."""
    mask = np.asarray(mask, dtype=float)
    T = len(mask)
    out = np.zeros(T, dtype=float)
    csum = np.cumsum(mask)
    for k in range(T):
        lo = max(0, k - window + 1)
        out[k] = csum[k] - (csum[lo - 1] if lo > 0 else 0.0)
    return out


def abs_delta_series(e3_norm: np.ndarray, ref: Optional[float] = None) -> np.ndarray:
    """
    |Δẽ₃| series: absolute first difference of normalized excess³.
    If ref is given, also return |ẽ₃ − ref| as level-vs-baseline abs form.
    """
    e3_norm = np.asarray(e3_norm, dtype=float)
    de = np.zeros_like(e3_norm)
    de[0] = 0.0
    de[1:] = np.abs(np.diff(e3_norm))
    return de


# ---------------------------------------------------------------------------
# Activation A3 (hardened v0.2)
# ---------------------------------------------------------------------------

@dataclass
class ActivationConfig:
    """Hardened defaults: fewer false positives under hyper-persistence."""

    p_arm: int = 3
    # (B) level
    theta_e: float = 1.25
    # (B′) change — |Δẽ₃|
    theta_delta: float = 0.40
    require_change: bool = True
    # (C) residual synergistic fraction ẽ / (ẽ + Φ1+Φ2)
    theta_residual: float = 0.20
    # legacy ratio (optional secondary; kept for ablation)
    theta_ratio: float = 0.25
    use_residual_c: bool = True
    # (D) dual-scale
    L_short: int = 3          # detection window
    L_min_short: int = 2
    L_med: int = 7            # surplus persistence
    L_min_med: int = 4
    # soft gate
    soft: bool = True
    soft_offset: float = 3.25  # higher → less soft leakage on nulls
    # soft A3 below this floor contributes 0 to Γ₃ / channel-3 (reduces S0 ΔT)
    soft_floor: float = 0.25
    d_min: int = 3
    # adaptive θ_e from baseline noise
    adaptive_theta: bool = True
    adaptive_k: float = 0.5
    # backwards-compat aliases (mapped if set via L / L_min)
    L: Optional[int] = None
    L_min: Optional[int] = None

    def __post_init__(self) -> None:
        if self.L is not None:
            self.L_med = int(self.L)
        if self.L_min is not None:
            self.L_min_med = int(self.L_min)


def _effective_theta_e(
    cfg: ActivationConfig,
    stats: Dict[str, float],
) -> float:
    """Widen level threshold when baseline excess³ is noisy."""
    if not cfg.adaptive_theta:
        return cfg.theta_e
    # CV- and MAD-relative expansion (bounded)
    expand = 1.0 + cfg.adaptive_k * min(float(stats["cv"]), 2.0)
    return cfg.theta_e * expand


def residual_synergy_score(
    score_B: np.ndarray,
    phi1: Optional[np.ndarray],
    phi2: Optional[np.ndarray],
) -> np.ndarray:
    """
    Approximate residual synergistic mass fraction:
        r = s_B / (s_B + Φ1 + Φ2 + ε)  ∈ (0, 1)

    When Φ1/Φ2 unavailable, fall back to s_B / (s_B + 1) so the score
    still lives in (0,1) and remains comparable across series.
    """
    score_B = np.asarray(score_B, dtype=float)
    if phi1 is not None and phi2 is not None:
        phi12 = np.asarray(phi1, dtype=float) + np.asarray(phi2, dtype=float)
        phi12 = np.maximum(phi12, 0.0)
    else:
        phi12 = np.ones_like(score_B)
    return score_B / (score_B + phi12 + EPS)


def activation_A3(
    tau_s: np.ndarray,
    e3_norm: np.ndarray,
    phi1: Optional[np.ndarray] = None,
    phi2: Optional[np.ndarray] = None,
    n_vars: int = 3,
    cfg: Optional[ActivationConfig] = None,
    abs_delta: bool = True,
    baseline_stats: Optional[Dict[str, float]] = None,
    return_parts: bool = False,
) -> np.ndarray | Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """
    Level-3 activation gate A3 ∈ {0,1} or soft (0,1). Hardened v0.2.

    Conditions (manuscript §5):
      (A)  chaotic / armed persistence
      (B)  surplus level vs baseline (ẽ₃)
      (B′) change: |Δẽ₃| above threshold (required if require_change)
      (C)  residual synergistic fraction (stronger than bare ratio)
      (D)  dual-scale persistence: short detection + medium surplus hold
    """
    cfg = cfg or ActivationConfig()
    tau_s = np.asarray(tau_s, dtype=float)
    e3_norm = np.asarray(e3_norm, dtype=float)
    T = len(tau_s)
    if n_vars < cfg.d_min:
        z = np.zeros(T, dtype=float)
        if return_parts:
            return z, {}
        return z

    if baseline_stats is None:
        baseline_stats = {"mu": 0.0, "sd": 1.0, "med": 0.0, "mad": 1.0, "cv": 0.0}
    theta_e_eff = _effective_theta_e(cfg, baseline_stats)

    in_chaos = np.abs(tau_s) < TAU_CH
    P = persistence_series(in_chaos)

    # (A)
    sA = (in_chaos | (P >= cfg.p_arm)).astype(float)

    # (B) level score
    if abs_delta:
        # |ẽ₃| — magnitude of normalized surplus (or rank scale)
        score_level = np.abs(e3_norm)
    else:
        score_level = softplus(e3_norm)
    sB_level = (score_level > theta_e_eff).astype(float)

    # (B′) change
    de = abs_delta_series(e3_norm)
    sB_change = (de > cfg.theta_delta).astype(float)
    if cfg.require_change:
        sB = ((sB_level > 0.5) & (sB_change > 0.5)).astype(float)
        score_B = score_level  # for residual C, use level magnitude
    else:
        sB = sB_level
        score_B = score_level

    # (C) residual synergistic fraction
    r_syn = residual_synergy_score(score_B, phi1, phi2)
    if cfg.use_residual_c:
        sC = (r_syn > cfg.theta_residual).astype(float)
        score_C = r_syn
    else:
        if phi1 is not None and phi2 is not None:
            denom = np.asarray(phi1, dtype=float) + np.asarray(phi2, dtype=float) + EPS
            ratio = score_B / denom
            sC = (ratio > cfg.theta_ratio).astype(float)
            score_C = ratio
        else:
            sC = np.ones(T, dtype=float)
            score_C = np.ones(T, dtype=float)

    # Dual-scale (D): short detection of (B∧C), medium persistence of (A∧B∧C)
    pre_bc = (sB > 0.5) & (sC > 0.5)
    pre_all = (sA > 0.5) & pre_bc

    cnt_short = rolling_count(pre_bc, cfg.L_short)
    cnt_med = rolling_count(pre_all, cfg.L_med)
    sD_short = (cnt_short >= cfg.L_min_short).astype(float)
    sD_med = (cnt_med >= cfg.L_min_med).astype(float)
    sD = ((sD_short > 0.5) & (sD_med > 0.5)).astype(float)

    parts = {
        "sA": sA,
        "sB": sB,
        "sB_level": sB_level,
        "sB_change": sB_change,
        "sC": sC,
        "sD": sD,
        "sD_short": sD_short,
        "sD_med": sD_med,
        "r_syn": r_syn,
        "de3": de,
        "score_level": score_level,
        "theta_e_eff": np.full(T, theta_e_eff),
    }

    if not cfg.soft:
        hard = ((sA * sB * sC * sD) > 0.5).astype(float)
        if return_parts:
            return hard, parts
        return hard

    # soft product-of-scores
    cA = sA
    cB_level = logistic(2.0 * (score_level - theta_e_eff))
    cB_change = logistic(4.0 * (de - cfg.theta_delta))
    cB = cB_level * cB_change if cfg.require_change else cB_level
    cC = logistic(8.0 * (score_C - (cfg.theta_residual if cfg.use_residual_c else cfg.theta_ratio)))
    cD = 0.5 * (sD_short + sD_med)
    soft_A3 = logistic(cA + cB + cC + cD - cfg.soft_offset)
    # floor: values below soft_floor are treated as inactive (cuts null leakage)
    if cfg.soft_floor > 0:
        soft_A3 = np.where(soft_A3 >= cfg.soft_floor, soft_A3, 0.0)
    parts["cA"] = cA
    parts["cB"] = cB
    parts["cC"] = cC
    parts["cD"] = cD
    if return_parts:
        return soft_A3, parts
    return soft_A3


# ---------------------------------------------------------------------------
# Proposal 1 — multiplicative gain
# ---------------------------------------------------------------------------

@dataclass
class P1Config:
    beta: float = 0.5
    # True  → ψ(|ẽ₃|)  or ψ(|Δẽ₃|) depending on psi_mode
    # False → ψ(ẽ₃) signed (softplus of signed z)
    abs_delta: bool = True
    # "level"  → ψ on |ẽ₃| (or signed ẽ₃ if abs_delta=False)
    # "change" → ψ on |Δẽ₃|  (coherent with G1 surplus drops)
    # "both"   → ψ on 0.5*(|ẽ₃| + |Δẽ₃|)
    psi_mode: str = "level"
    delta_t0: float = 1.0
    state_alpha: float = 1.0
    norm_mode: str = "zscore"  # "zscore" | "rank" | "mad"


def recd_p1(
    tau_s: np.ndarray,
    excess3: np.ndarray,
    baseline_mask: np.ndarray,
    phi1: Optional[np.ndarray] = None,
    phi2: Optional[np.ndarray] = None,
    n_vars: int = 3,
    cfg: Optional[P1Config] = None,
    act_cfg: Optional[ActivationConfig] = None,
) -> Dict[str, np.ndarray]:
    """
    (P1) t_{k+1} = t_k + Δt_base * g * α * Γ3
    Γ3 = 1 + β * A3 * ψ(·)

    Also returns ρ3_marg = |dt_P1 − dt_base| / (|dt_P1| + ε), the marginal
    clock contribution of Φ₃ (generalizes P2's ρ₃ for ablation).
    """
    cfg = cfg or P1Config()
    tau_s = np.asarray(tau_s, dtype=float)
    excess3 = np.asarray(excess3, dtype=float)
    T = len(tau_s)
    e3n = normalize_vs_baseline(excess3, baseline_mask, mode=cfg.norm_mode)
    stats = baseline_scale_stats(excess3, baseline_mask)
    A3 = activation_A3(
        tau_s, e3n, phi1, phi2, n_vars=n_vars, cfg=act_cfg,
        abs_delta=cfg.abs_delta, baseline_stats=stats,
    )

    in_chaos = np.abs(tau_s) < TAU_CH
    depth = run_depth_series(in_chaos)
    de = abs_delta_series(e3n)

    t = np.zeros(T + 1, dtype=float)
    dt_eff = np.zeros(T, dtype=float)
    dt_base = np.zeros(T, dtype=float)
    gamma = np.zeros(T, dtype=float)
    g_ser = np.zeros(T, dtype=float)

    for k in range(T):
        g = gate_piecewise(float(tau_s[k]))
        g_ser[k] = g
        dt = base_interval(float(tau_s[k]), int(depth[k]), delta_t0=cfg.delta_t0)
        dt_base[k] = dt * g * cfg.state_alpha

        if cfg.psi_mode == "change":
            # Prefer |Δẽ₃|; signed first-diff only if abs_delta=False
            if cfg.abs_delta:
                psi = softplus(de[k])
            else:
                dsigned = e3n[k] - (e3n[k - 1] if k else 0.0)
                psi = softplus(dsigned)
        elif cfg.psi_mode == "both":
            dsigned = e3n[k] - (e3n[k - 1] if k else 0.0)
            if cfg.abs_delta:
                psi = softplus(0.5 * (abs(e3n[k]) + de[k]))
            else:
                psi = softplus(0.5 * (e3n[k] + dsigned))
        else:  # level
            if cfg.abs_delta:
                psi = softplus(abs(e3n[k]))
            else:
                psi = softplus(e3n[k])

        gamma[k] = 1.0 + cfg.beta * float(A3[k]) * float(psi)
        dt_eff[k] = dt_base[k] * gamma[k]
        t[k + 1] = t[k] + dt_eff[k]

    # marginal Φ₃ contribution to the clock (ablation-friendly)
    rho3_marg = np.abs(dt_eff - dt_base) / (np.abs(dt_eff) + EPS)

    return {
        "t": t,
        "dt": dt_eff,
        "dt_base_component": dt_base,
        "gamma3": gamma,
        "A3": A3,
        "e3_norm": e3n,
        "de3": de,
        "g": g_ser,
        "depth": depth.astype(float),
        "rho3_marg": rho3_marg,
    }


# ---------------------------------------------------------------------------
# Proposal 2 — dual channel
# ---------------------------------------------------------------------------

@dataclass
class P2Config:
    eta: float = 0.35
    gamma_f: float = 0.0
    r_max: int = 3
    kappa: float = 1.0
    jump_J: float = 0.0  # keep 0 until P1 succeeds
    theta_jump: float = 2.0
    theta_delta: float = 0.5
    p_min_jump: int = 5
    delta_t0: float = 1.0
    state_alpha: float = 1.0
    norm_mode: str = "zscore"
    abs_delta: bool = True  # visible; channel-3 uses |ẽ₃|


def recd_p2(
    tau_s: np.ndarray,
    excess3: np.ndarray,
    baseline_mask: np.ndarray,
    phi1: Optional[np.ndarray] = None,
    phi2: Optional[np.ndarray] = None,
    f3: Optional[np.ndarray] = None,
    n_vars: int = 3,
    cfg: Optional[P2Config] = None,
    act_cfg: Optional[ActivationConfig] = None,
) -> Dict[str, np.ndarray]:
    """
    (P2) t += Δt^(12) + Δt^(3) + optional jump
    """
    cfg = cfg or P2Config()
    tau_s = np.asarray(tau_s, dtype=float)
    excess3 = np.asarray(excess3, dtype=float)
    T = len(tau_s)
    e3n = normalize_vs_baseline(excess3, baseline_mask, mode=cfg.norm_mode)
    stats = baseline_scale_stats(excess3, baseline_mask)
    A3 = activation_A3(
        tau_s, e3n, phi1, phi2, n_vars=n_vars, cfg=act_cfg,
        abs_delta=cfg.abs_delta, baseline_stats=stats,
    )

    if f3 is None:
        f3 = np.zeros(T, dtype=float)
    else:
        f3 = np.asarray(f3, dtype=float)

    in_chaos = np.abs(tau_s) < TAU_CH
    depth12 = run_depth_series(in_chaos)
    P = depth12.copy()

    t = np.zeros(T + 1, dtype=float)
    dt12 = np.zeros(T, dtype=float)
    dt3 = np.zeros(T, dtype=float)
    jumps = np.zeros(T, dtype=float)
    R3 = np.zeros(T, dtype=float)
    r = 0

    e3n_prev = 0.0
    for k in range(T):
        g = gate_piecewise(float(tau_s[k]))
        h12 = abs(tau_s[k]) if abs(tau_s[k]) < TAU_CH else 1.0
        k12 = int(np.clip(depth12[k], 0, 8))
        dt12[k] = (DELTA_FEIGENBAUM ** (-k12)) * h12 * g * cfg.state_alpha * cfg.delta_t0

        if A3[k] > 0.5:
            r = min(cfg.r_max, r + 1)
        else:
            r = 0
        R3[k] = r

        mag = abs(e3n[k]) if cfg.abs_delta else float(e3n[k])
        h3 = cfg.eta * float(softplus(mag if cfg.abs_delta else e3n[k])) * (1.0 + cfg.gamma_f * f3[k])
        depth3 = k12 + cfg.kappa * r
        dt3[k] = A3[k] * (DELTA_FEIGENBAUM ** (-depth3)) * h3 * cfg.delta_t0

        de = abs(e3n[k] - e3n_prev)
        if (
            cfg.jump_J > 0
            and A3[k] > 0.5
            and abs(e3n[k]) > cfg.theta_jump
            and de > cfg.theta_delta
            and P[k] >= cfg.p_min_jump
        ):
            jumps[k] = cfg.jump_J * float(softplus(abs(e3n[k])))
        e3n_prev = e3n[k]

        t[k + 1] = t[k] + dt12[k] + dt3[k] + jumps[k]

    denom = np.abs(dt12) + np.abs(dt3) + EPS
    rho3 = np.abs(dt3) / denom

    return {
        "t": t,
        "dt12": dt12,
        "dt3": dt3,
        "jumps": jumps,
        "A3": A3,
        "R3": R3,
        "e3_norm": e3n,
        "rho3": rho3,
        "depth12": depth12.astype(float),
    }


def recd_base(
    tau_s: np.ndarray,
    delta_t0: float = 1.0,
    state_alpha: float = 1.0,
) -> Dict[str, np.ndarray]:
    """Legacy RECD without Φ₃ (ablation reference)."""
    tau_s = np.asarray(tau_s, dtype=float)
    T = len(tau_s)
    in_chaos = np.abs(tau_s) < TAU_CH
    depth = run_depth_series(in_chaos)
    t = np.zeros(T + 1, dtype=float)
    dt = np.zeros(T, dtype=float)
    for k in range(T):
        g = gate_piecewise(float(tau_s[k]))
        dt[k] = base_interval(float(tau_s[k]), int(depth[k]), delta_t0=delta_t0) * g * state_alpha
        t[k + 1] = t[k] + dt[k]
    return {"t": t, "dt": dt, "depth": depth.astype(float)}


# ---------------------------------------------------------------------------
# Synthetic generators (S0–S2 family)
# ---------------------------------------------------------------------------

def gen_s0_null(T: int = 400, seed: int = 1) -> Dict[str, np.ndarray]:
    """
    S0 / G0-like: independent-ish, mostly ordered τ_s, flat low excess³.
    Expectation: low A3 rate (≲ 5–10% soft mean; hard ≪ 5%).
    """
    rng = np.random.default_rng(seed)
    tau = rng.normal(0.58, 0.06, T)
    # occasional brief dips but not sustained chaos
    dip = rng.random(T) < 0.03
    tau[dip] = rng.uniform(-0.2, 0.2, dip.sum())
    tau = np.clip(tau, -0.95, 0.95)
    e3 = rng.normal(1.0, 0.04, T)
    phi1 = rng.uniform(0.4, 0.7, T)
    phi2 = rng.uniform(0.3, 0.5, T)
    # f3 mass proxy low
    f3 = rng.uniform(0.05, 0.15, T)
    baseline = np.zeros(T, dtype=bool)
    baseline[: max(40, T // 8)] = True
    return {"tau": tau, "e3": e3, "phi1": phi1, "phi2": phi2, "f3": f3, "baseline": baseline, "name": "S0"}


def gen_s1_latent(T: int = 400, seed: int = 2) -> Dict[str, np.ndarray]:
    """
    S1 / G1-like: mid-series latent reorg; surplus may drop or spike.
    Uses |Δẽ₃|-sensitive design — absolute change matters.
    """
    rng = np.random.default_rng(seed)
    tau = np.full(T, 0.55)
    # approach chaos then reorg
    tau[100:320] = rng.normal(0.08, 0.10, 220)
    tau = np.clip(tau, -0.9, 0.9)
    e3 = rng.normal(1.05, 0.05, T)
    # G1-style: surplus can *drop* under shared latent (reorg toward redundancy)
    e3[200:260] = rng.normal(0.55, 0.06, 60)  # drop
    # then partial recovery with a secondary spike
    e3[280:310] = rng.normal(1.7, 0.08, 30)
    phi1 = np.full(T, 0.5)
    phi2 = np.full(T, 0.35)
    phi1[200:260] = 0.75  # pairs dominate during drop
    phi2[200:260] = 0.55
    phi1[280:310] = 0.35
    phi2[280:310] = 0.25
    f3 = 0.15 + 0.5 * (np.abs(e3 - 1.05) / (np.max(np.abs(e3 - 1.05)) + EPS))
    f3 = np.clip(f3, 0.05, 0.85)
    baseline = np.zeros(T, dtype=bool)
    baseline[:60] = True
    return {"tau": tau, "e3": e3, "phi1": phi1, "phi2": phi2, "f3": f3, "baseline": baseline, "name": "S1"}


def gen_s2_coupled_logistic(
    T: int = 400,
    seed: int = 3,
    regime: str = "chaos",
) -> Dict[str, np.ndarray]:
    """
    S2: pre-chaos vs chaos ordinal surrogate.
    chaos → lower |τ|, higher excess³ and f3; prechaos opposite.
    """
    rng = np.random.default_rng(seed)
    if regime == "chaos":
        tau = rng.normal(0.05, 0.12, T)
        e3_mu, e3_sd = 1.55, 0.10
        f3_mu = 0.45
    else:  # prechaos
        tau = rng.normal(0.48, 0.08, T)
        e3_mu, e3_sd = 1.05, 0.05
        f3_mu = 0.18
    tau = np.clip(tau, -0.95, 0.95)
    e3 = rng.normal(e3_mu, e3_sd, T)
    # mid reorg only in chaos
    if regime == "chaos":
        e3[150:220] = rng.normal(2.1, 0.12, 70)
    phi1 = rng.uniform(0.3, 0.6, T) if regime == "chaos" else rng.uniform(0.5, 0.8, T)
    phi2 = rng.uniform(0.2, 0.45, T) if regime == "chaos" else rng.uniform(0.4, 0.65, T)
    f3 = np.clip(rng.normal(f3_mu, 0.05, T), 0.02, 0.9)
    if regime == "chaos":
        f3[150:220] = np.clip(f3[150:220] + 0.25, 0, 0.95)
    baseline = np.zeros(T, dtype=bool)
    baseline[:50] = True
    return {
        "tau": tau, "e3": e3, "phi1": phi1, "phi2": phi2, "f3": f3,
        "baseline": baseline, "name": f"S2_{regime}",
    }


def add_noise_to_series(data: Dict[str, np.ndarray], noise_pct: float, seed: int = 0) -> Dict[str, np.ndarray]:
    """Add Gaussian noise as fraction of series std to e3 and small jitter to tau."""
    rng = np.random.default_rng(seed)
    out = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in data.items()}
    for key in ("e3", "phi1", "phi2"):
        if key in out and isinstance(out[key], np.ndarray):
            s = float(np.std(out[key])) + EPS
            out[key] = out[key] + rng.normal(0, noise_pct * s, len(out[key]))
    if "tau" in out:
        out["tau"] = np.clip(out["tau"] + rng.normal(0, noise_pct * 0.05, len(out["tau"])), -0.99, 0.99)
    out["name"] = f"{data.get('name', 'run')}_noise{int(100 * noise_pct)}"
    return out


def summarize_run(
    data: Dict[str, np.ndarray],
    p1_cfg: Optional[P1Config] = None,
    act_cfg: Optional[ActivationConfig] = None,
    hard_act: bool = False,
) -> Dict[str, float]:
    """Key metrics for one synthetic arm."""
    act = act_cfg or ActivationConfig()
    if hard_act:
        act = ActivationConfig(**{**act.__dict__, "soft": False})
    base = recd_base(data["tau"])
    p1 = recd_p1(
        data["tau"], data["e3"], data["baseline"],
        phi1=data.get("phi1"), phi2=data.get("phi2"),
        n_vars=4, cfg=p1_cfg, act_cfg=act,
    )
    p2 = recd_p2(
        data["tau"], data["e3"], data["baseline"],
        phi1=data.get("phi1"), phi2=data.get("phi2"),
        f3=data.get("f3"), n_vars=4, act_cfg=act,
    )
    A3 = p1["A3"]
    # hard-ish rate: fraction of time A3 > 0.5
    a3_rate = float(np.mean(A3 > 0.5))
    a3_mean = float(np.mean(A3))
    g_m1 = p1["gamma3"] - 1.0
    f3 = data.get("f3")
    if f3 is not None:
        # corr only where defined and with variation
        if np.std(g_m1) > EPS and np.std(f3) > EPS:
            corr = float(np.corrcoef(g_m1, f3)[0, 1])
        else:
            corr = float("nan")
    else:
        corr = float("nan")
    return {
        "T_base": float(base["t"][-1]),
        "T_P1": float(p1["t"][-1]),
        "T_P2": float(p2["t"][-1]),
        "A3_rate": a3_rate,
        "A3_mean": a3_mean,
        "mean_Gamma3": float(np.mean(p1["gamma3"])),
        "mean_rho3_P2": float(np.mean(p2["rho3"])),
        "mean_rho3_marg_P1": float(np.mean(p1["rho3_marg"])),
        "corr_Gamma_f3": corr,
        "delta_T_P1": float(p1["t"][-1] - base["t"][-1]),
        "delta_T_P2": float(p2["t"][-1] - base["t"][-1]),
    }


# ---------------------------------------------------------------------------
# Synthetic demo
# ---------------------------------------------------------------------------

def _synthetic_demo(T: int = 400, seed: int = 7) -> None:
    rng = np.random.default_rng(seed)
    tau = np.full(T, 0.55)
    tau[80:320] = rng.normal(0.05, 0.08, 240)
    tau = np.clip(tau, -0.9, 0.9)
    e3 = rng.normal(1.0, 0.05, T)
    e3[180:240] = rng.normal(1.9, 0.08, 60)
    phi1 = np.full(T, 0.45)
    phi2 = np.full(T, 0.30)
    phi1[180:240] = 0.25
    phi2[180:240] = 0.20
    baseline = np.zeros(T, dtype=bool)
    baseline[:60] = True

    act = ActivationConfig()
    base = recd_base(tau)
    p1 = recd_p1(tau, e3, baseline, phi1=phi1, phi2=phi2, n_vars=4, act_cfg=act)
    p2 = recd_p2(tau, e3, baseline, phi1=phi1, phi2=phi2, n_vars=4, act_cfg=act)
    # loose v0.1-like for comparison
    act_loose = ActivationConfig(
        theta_e=1.0, theta_delta=0.0, require_change=False,
        theta_residual=0.0, use_residual_c=False, theta_ratio=0.15,
        L_short=5, L_min_short=1, L_med=5, L_min_med=3,
        soft_offset=2.0, adaptive_theta=False,
    )
    p1_loose = recd_p1(tau, e3, baseline, n_vars=4, act_cfg=act_loose)

    print("=== Φ₃–RECD synthetic demo (phi3-recd v0.5, hardened A3) ===")
    print(f"T={T}")
    print(f"Final T_base = {base['t'][-1]:.4f}")
    print(f"Final T_P1   = {p1['t'][-1]:.4f}  (mean Γ3={p1['gamma3'].mean():.3f}, mean A3={p1['A3'].mean():.3f}, A3>0.5 rate={ (p1['A3']>0.5).mean():.3f})")
    print(f"Final T_P2   = {p2['t'][-1]:.4f}  (mean ρ3={p2['rho3'].mean():.3f}, mean A3={p2['A3'].mean():.3f})")
    print(f"A3 rate chaos core [80:320]:  hardish={(p1['A3'][80:320]>0.5).mean():.3f}  mean={p1['A3'][80:320].mean():.3f}")
    print(f"A3 rate surplus burst [180:240]: hardish={(p1['A3'][180:240]>0.5).mean():.3f}  mean={p1['A3'][180:240].mean():.3f}")
    print(f"Loose v0.1-like A3 mean (same series): {p1_loose['A3'].mean():.3f}  rate={(p1_loose['A3']>0.5).mean():.3f}")
    print(f"mean ρ3_marg (P1): {p1['rho3_marg'].mean():.3f}")
    print("OK — hardened A3 + both proposals ran.")
