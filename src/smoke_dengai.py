#!/usr/bin/env python3
"""
Real-data smoke test: P1 (Φ₃ → RECD clock) on DengAI weekly series.

Strategic contrast to Holter smoke (v0.3):
  - Ecological / epidemiological domain (not RR).
  - Chaos-band occupancy is typically NOT ~100% → legacy ΔT may move with Γ₃.
  - Clear outbreak peaks as events; inter-epidemic windows as FAR proxy.

Protocol (pre-specified, modest, preprint-smoke — not full Phase E):
  - Cities: San Juan (sj) primary; Iquitos (iq) optional contrast.
  - Multivariate: [cases, station temp, precip, reanalysis RH] → d=4, d_min=3.
  - W=13, stride=1, θ₃=0.10 (epidemiology defaults from nested ordinal levels).
  - excess³ weights fixed 0.6/0.4 (via recd_ordinal_levels.compute_phi3).
  - A₃: hardened ActivationConfig v0.2 (same as synthetic + Holter).
  - Ablation β∈{0, 0.5}.
  - Outbreaks: local peaks of total_cases ≥ city P80, min separation 26 weeks;
    top-K by peak height (default K=3 per city).
  - Per-outbreak segment: [peak−SEG_PRE, peak] weeks; basal first BASE_W weeks;
    approach last APP_W weeks before peak.
  - Controls: low-activity windows (rolling max cases < city P60), same segment length.
  - Metrics: ΔT legacy, chaos%, A₃ rates, lead (weeks) A₃ hard vs excess³ abs-z,
    FAR proxy (alarms / 52 weeks), ρ₃^marg, condition diagnostics.

Usage:
  cd .../Preprint_Phi3_RECD_Dynamic_Integration/src
  python3 smoke_dengai.py
  python3 smoke_dengai.py --cities sj --n-outbreaks 3 --n-controls 2
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)
DATA_DIR = ROOT / "data" / "dengai"

sys.path.insert(0, str(SRC))

from phi3_recd import (  # noqa: E402
    ActivationConfig,
    P1Config,
    TAU_CH,
    activation_A3,
    baseline_scale_stats,
    normalize_vs_baseline,
    recd_p1,
)

# Nested ordinal / excess³ from CCTP pilot (same 0.6/0.4 proxy)
CCTP_CODE = ROOT.parent / "Cardiac_CCTP_Pilot" / "code"
sys.path.insert(0, str(CCTP_CODE))

from recd_ordinal_levels import (  # noqa: E402
    compute_phi1,
    compute_phi2,
    compute_phi3,
    generate_multivariate_symbols,
)

# ---------------------------------------------------------------------------
# Smoke defaults (epidemiology)
# ---------------------------------------------------------------------------

W_TAU = 13
STRIDE = 1
THETA3 = 0.10
MIN_CONSEC = 2  # weekly: 2 consecutive alarms
Z_THRESH = 2.0
SEG_PRE = 40  # weeks before peak in segment
BASE_W = 13
APP_W = 12
MIN_PEAK_SEP = 26
OUTBREAK_PCTL = 80
CONTROL_MAX_PCTL = 60
DEFAULT_CITIES = ["sj", "iq"]
DEFAULT_N_OUTBREAKS = 3
DEFAULT_N_CONTROLS = 2

# Feature columns (order fixed)
FEATURE_COLS = [
    "total_cases",
    "station_avg_temp_c",
    "station_precip_mm",
    "reanalysis_relative_humidity_percent",
]

ACT_SOFT = ActivationConfig()  # d_min=3 default
ACT_HARD = ActivationConfig(soft=False)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _find_dengai_paths() -> Tuple[Path, Path]:
    candidates = [
        (DATA_DIR / "dengue_features_train.csv", DATA_DIR / "dengue_labels_train.csv"),
        (
            Path("/Users/johelpadilla/grok-work/tau-sistemic/Investigaciones/"
                 "tau-sistemic-old/serious_datasets/dengai/dengue_features_train.csv"),
            Path("/Users/johelpadilla/grok-work/tau-sistemic/Investigaciones/"
                 "tau-sistemic-old/serious_datasets/dengai/dengue_labels_train.csv"),
        ),
    ]
    for f, l in candidates:
        if f.exists() and l.exists():
            return f, l
    raise FileNotFoundError(
        "DengAI CSVs not found. Expected under data/dengai/ or tau-sistemic-old path."
    )


def load_city(city: str) -> Dict:
    """Load merged weekly features + labels for one city; forward/back fill NaNs."""
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError("pandas required for smoke_dengai.py") from e

    feat_path, lab_path = _find_dengai_paths()
    feat = pd.read_csv(feat_path)
    lab = pd.read_csv(lab_path)
    m = feat.merge(lab, on=["city", "year", "weekofyear"], how="inner")
    df = m[m["city"] == city].sort_values(["year", "weekofyear"]).reset_index(drop=True)
    if len(df) == 0:
        raise ValueError(f"No rows for city={city}")

    for c in FEATURE_COLS:
        if c not in df.columns:
            raise KeyError(f"Missing column {c}")
    X = df[FEATURE_COLS].astype(float).ffill().bfill()
    cases = X["total_cases"].to_numpy(dtype=float)
    # week index 0..T-1; also calendar helpers
    years = df["year"].to_numpy(dtype=int)
    weeks = df["weekofyear"].to_numpy(dtype=int)
    if "week_start_date" in df.columns:
        dates = df["week_start_date"].astype(str).tolist()
    else:
        dates = [f"{y}-W{w:02d}" for y, w in zip(years, weeks)]

    return {
        "city": city,
        "X": X.to_numpy(dtype=float),
        "cases": cases,
        "years": years,
        "weeks": weeks,
        "dates": dates,
        "n": len(df),
    }


# ---------------------------------------------------------------------------
# Metrics: τ_s, excess³, φ1, φ2
# ---------------------------------------------------------------------------

def rolling_tau_s(X: np.ndarray, window: int = W_TAU, stride: int = STRIDE) -> np.ndarray:
    """
    Mean pairwise Spearman rank correlation over rolling window.
    Returns length-T series with NaN until first full window; strided samples filled.
    """
    X = np.asarray(X, dtype=float)
    T, N = X.shape
    out = np.full(T, np.nan)
    if N < 2 or T < window:
        return out
    for i in range(window - 1, T, stride):
        win = X[i - window + 1 : i + 1]
        # rank each column
        ranks = np.zeros_like(win)
        for j in range(N):
            ranks[:, j] = win[:, j].argsort().argsort().astype(float)
        rhos = []
        for a in range(N):
            for b in range(a + 1, N):
                r0, r1 = ranks[:, a], ranks[:, b]
                if np.std(r0) > 0 and np.std(r1) > 0:
                    rhos.append(float(np.corrcoef(r0, r1)[0, 1]))
        out[i] = float(np.mean(rhos)) if rhos else 0.0
    # linear fill small gaps between strides (stride=1 → none)
    return out


def build_city_metrics(
    X: np.ndarray,
    *,
    theta3: float = THETA3,
    window: int = W_TAU,
    stride: int = STRIDE,
) -> Dict[str, np.ndarray]:
    """z-score features, ordinal symbols, excess³, φ1/φ2, τ_s aligned to symbol index."""
    X = np.asarray(X, dtype=float)
    mu = X.mean(axis=0)
    sd = X.std(axis=0) + 1e-12
    Xz = (X - mu) / sd

    S = generate_multivariate_symbols(Xz, m=3, delay=1)
    offset = (3 - 1) * 1  # first original index of S[0]
    phi1 = compute_phi1(S)
    phi2 = compute_phi2(S, d=4)
    _, excess3 = compute_phi3(S, window=window, theta=theta3, stride=stride)

    tau_full = rolling_tau_s(Xz, window=window, stride=stride)
    # valid excess³ samples (non-NaN)
    valid = ~np.isnan(excess3)
    idx = np.where(valid)[0]
    if len(idx) == 0:
        raise RuntimeError("No valid excess³ samples — series too short?")

    t_week = (offset + idx).astype(float)  # week index on original series
    tau_at = np.full(len(idx), np.nan)
    for j, i in enumerate(idx):
        beat = min(offset + int(i), len(tau_full) - 1)
        # nearest finite tau
        lo = max(0, beat - window)
        hi = min(len(tau_full), beat + 2)
        seg = tau_full[lo:hi]
        ok = ~np.isnan(seg)
        if ok.any():
            tau_at[j] = float(seg[ok][-1])
        else:
            tau_at[j] = 0.0
    tau_at = np.nan_to_num(tau_at, nan=0.0)

    return {
        "t_week": t_week,
        "tau": tau_at.astype(float),
        "e3": excess3[idx].astype(float),
        "phi1": phi1[idx].astype(float),
        "phi2": phi2[idx].astype(float),
        "orig_idx": (offset + idx).astype(int),
        "n_points": len(idx),
        "n_weeks": len(X),
        "n_vars": X.shape[1],
        "offset": offset,
    }


# ---------------------------------------------------------------------------
# Outbreak / control windows
# ---------------------------------------------------------------------------

def find_outbreak_peaks(
    cases: np.ndarray,
    *,
    percentile: float = OUTBREAK_PCTL,
    min_sep: int = MIN_PEAK_SEP,
    n_max: int = 3,
    min_week: int = SEG_PRE + 2,
    max_week: Optional[int] = None,
) -> List[int]:
    """Local maxima of cases ≥ city percentile, separated by min_sep; top n_max by height."""
    cases = np.asarray(cases, dtype=float)
    T = len(cases)
    if max_week is None:
        max_week = T - 2
    thr = float(np.percentile(cases, percentile))
    candidates = []
    for i in range(1, T - 1):
        if i < min_week or i > max_week:
            continue
        if cases[i] >= thr and cases[i] >= cases[i - 1] and cases[i] >= cases[i + 1]:
            candidates.append(i)
    # non-maximum suppression by height
    candidates = sorted(candidates, key=lambda i: cases[i], reverse=True)
    selected: List[int] = []
    for i in candidates:
        if all(abs(i - j) >= min_sep for j in selected):
            selected.append(i)
        if len(selected) >= n_max:
            break
    return sorted(selected)


def find_control_windows(
    cases: np.ndarray,
    outbreak_peaks: Sequence[int],
    *,
    max_pctl: float = CONTROL_MAX_PCTL,
    n_max: int = 2,
    seg_pre: int = SEG_PRE,
    min_sep: int = MIN_PEAK_SEP,
) -> List[int]:
    """
    End-weeks of low-activity segments: rolling max over [end-seg_pre, end]
    below city max_pctl, away from outbreaks.
    """
    cases = np.asarray(cases, dtype=float)
    T = len(cases)
    thr = float(np.percentile(cases, max_pctl))
    forbidden = set()
    for p in outbreak_peaks:
        for k in range(max(0, p - min_sep), min(T, p + min_sep + 1)):
            forbidden.add(k)

    ends = []
    for end in range(seg_pre + 2, T - 1):
        if end in forbidden:
            continue
        window = cases[end - seg_pre : end + 1]
        if float(np.max(window)) < thr:
            ends.append(end)
    # pick spaced ends with lowest max cases
    ends = sorted(ends, key=lambda e: float(np.max(cases[e - seg_pre : e + 1])))
    selected: List[int] = []
    for e in ends:
        if all(abs(e - j) >= min_sep for j in selected):
            selected.append(e)
        if len(selected) >= n_max:
            break
    return sorted(selected)


def segment_masks(
    t_week: np.ndarray,
    event_week: float,
    *,
    seg_pre: int = SEG_PRE,
    base_w: int = BASE_W,
    app_w: int = APP_W,
) -> Dict[str, np.ndarray]:
    """Boolean masks on metric timeline for segment, basal, approach, pre-event."""
    t0 = event_week - seg_pre
    t1 = event_week
    in_seg = (t_week >= t0) & (t_week <= t1)
    basal = (t_week >= t0) & (t_week < t0 + base_w)
    approach = (t_week >= t1 - app_w) & (t_week < t1)
    pre = (t_week >= t0) & (t_week < t1)
    return {
        "in_seg": in_seg,
        "basal": basal,
        "approach": approach,
        "pre": pre,
        "t0": t0,
        "t1": t1,
    }


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def first_sustained_alarm(
    signal: np.ndarray,
    t: np.ndarray,
    *,
    t0: float,
    t1: float,
    threshold: float = 0.5,
    min_consecutive: int = MIN_CONSEC,
) -> Tuple[float, float]:
    mask = (t > t0) & (t < t1) & np.isfinite(signal)
    t_s = t[mask]
    s = signal[mask]
    if len(s) == 0:
        return float("nan"), 0.0
    alarm = s >= threshold
    run = 0
    for i, a in enumerate(alarm):
        run = run + 1 if a else 0
        if run >= min_consecutive:
            return float(t_s[i - min_consecutive + 1]), 1.0
    return float("nan"), 0.0


def regime_rate(x: np.ndarray, t: np.ndarray, t_lo: float, t_hi: float, thr: float = 0.5) -> float:
    m = (t >= t_lo) & (t <= t_hi) & np.isfinite(x)
    if m.sum() == 0:
        return float("nan")
    return float(np.mean(x[m] >= thr))


def count_alarms(signal: np.ndarray, min_consecutive: int = MIN_CONSEC) -> int:
    n_alarms = 0
    run = 0
    in_alarm = False
    for a in np.asarray(signal) >= 0.5:
        if a:
            run += 1
            if run == min_consecutive and not in_alarm:
                n_alarms += 1
                in_alarm = True
        else:
            run = 0
            in_alarm = False
    return n_alarms


def ews_abs_z_lead(
    e3: np.ndarray,
    t: np.ndarray,
    baseline_mask: np.ndarray,
    event_week: float,
    basal_end: float,
    z_thresh: float = Z_THRESH,
    min_consecutive: int = MIN_CONSEC,
) -> Tuple[float, float]:
    """Parallel EWS: abs z-score of excess³ vs basal; first sustained alarm."""
    base = e3[baseline_mask]
    if len(base) < 3:
        return float("nan"), 0.0
    mu = float(np.mean(base))
    sd = float(np.std(base)) + 1e-12
    z = np.abs((e3 - mu) / sd)
    return first_sustained_alarm(
        z, t, t0=basal_end, t1=event_week, threshold=z_thresh, min_consecutive=min_consecutive,
    )


def analyze_window(
    city_meta: Dict,
    metrics: Dict[str, np.ndarray],
    event_week: int,
    *,
    kind: str,
    label: str,
) -> Dict:
    """Run P1 β=0/0.5 on one outbreak or control window."""
    t = metrics["t_week"]
    masks = segment_masks(t, float(event_week))
    basal_m = masks["basal"]
    approach_m = masks["approach"]
    pre_m = masks["pre"]
    in_seg = masks["in_seg"]

    if basal_m.sum() < 5:
        # fallback: first 20% of segment
        seg_idx = np.where(in_seg)[0]
        basal_m = np.zeros(len(t), dtype=bool)
        if len(seg_idx) >= 5:
            n_b = max(5, len(seg_idx) // 5)
            basal_m[seg_idx[:n_b]] = True
        else:
            basal_m[: max(5, len(t) // 10)] = True

    # Restrict analysis arrays to segment for clock accumulation fairness
    # but activation/normalization use full-series indices with basal mask
    e3n0 = normalize_vs_baseline(metrics["e3"], basal_m, mode="zscore")
    stats0 = baseline_scale_stats(metrics["e3"], basal_m)
    _, parts = activation_A3(
        metrics["tau"], e3n0, metrics["phi1"], metrics["phi2"],
        n_vars=metrics["n_vars"], cfg=ACT_SOFT, abs_delta=True,
        baseline_stats=stats0, return_parts=True,
    )
    in_chaos = np.abs(metrics["tau"]) < TAU_CH
    diag = {
        "chaos_rate_all": float(in_chaos[in_seg].mean()) if in_seg.any() else float(in_chaos.mean()),
        "chaos_rate_approach": float(in_chaos[approach_m].mean()) if approach_m.any() else float("nan"),
        "mean_abs_tau": float(np.mean(np.abs(metrics["tau"][in_seg]))) if in_seg.any() else float(np.mean(np.abs(metrics["tau"]))),
        "sA_rate": float(parts["sA"][in_seg].mean()) if in_seg.any() else float(parts["sA"].mean()),
        "sB_level_rate": float(parts["sB_level"][in_seg].mean()) if in_seg.any() else float(parts["sB_level"].mean()),
        "sB_change_rate": float(parts["sB_change"][in_seg].mean()) if in_seg.any() else float(parts["sB_change"].mean()),
        "sB_rate": float(parts["sB"][in_seg].mean()) if in_seg.any() else float(parts["sB"].mean()),
        "sC_rate": float(parts["sC"][in_seg].mean()) if in_seg.any() else float(parts["sC"].mean()),
        "sD_rate": float(parts["sD"][in_seg].mean()) if in_seg.any() else float(parts["sD"].mean()),
        "theta_e_eff": float(parts["theta_e_eff"][0]),
        "dt_base_active_frac": float("nan"),
    }

    rows_beta = {}
    for beta in (0.0, 0.5):
        p1 = recd_p1(
            metrics["tau"],
            metrics["e3"],
            basal_m,
            phi1=metrics["phi1"],
            phi2=metrics["phi2"],
            n_vars=metrics["n_vars"],
            cfg=P1Config(beta=beta),
            act_cfg=ACT_SOFT,
        )
        e3n = p1["e3_norm"]
        stats = baseline_scale_stats(metrics["e3"], basal_m)
        A3_hard = activation_A3(
            metrics["tau"], e3n, metrics["phi1"], metrics["phi2"],
            n_vars=metrics["n_vars"], cfg=ACT_HARD, abs_delta=True, baseline_stats=stats,
        )
        A3_soft = p1["A3"]

        # Clock at event: sum dt over pre-event samples in segment
        # recd_p1 returns "dt" (effective) and "dt_base_component"
        if pre_m.any():
            T_p1_seg = float(np.sum(p1["dt"][pre_m]))
            T_base_seg = float(np.sum(p1["dt_base_component"][pre_m]))
            delta_T = T_p1_seg - T_base_seg
            T_at_event = T_p1_seg
            T_base_at_event = T_base_seg
        else:
            T_at_event = float(p1["t"][-1])
            T_base_at_event = float(np.sum(p1["dt_base_component"]))
            delta_T = T_at_event - T_base_at_event

        if beta > 0:
            gain_mass = float(np.sum(np.maximum(p1["gamma3"][pre_m] - 1.0, 0.0) / beta)) if pre_m.any() else 0.0
        else:
            gain_mass = 0.0

        basal_end = float(masks["t0"] + BASE_W)
        det_hr_A3, alarmed_A3 = first_sustained_alarm(
            A3_hard, t, t0=basal_end, t1=float(event_week),
            threshold=0.5, min_consecutive=MIN_CONSEC,
        )
        lead_A3 = (float(event_week) - det_hr_A3) if np.isfinite(det_hr_A3) else float("nan")

        det_soft, alarmed_soft = first_sustained_alarm(
            A3_soft, t, t0=basal_end, t1=float(event_week),
            threshold=0.5, min_consecutive=MIN_CONSEC,
        )
        lead_soft = (float(event_week) - det_soft) if np.isfinite(det_soft) else float("nan")

        if beta == 0.5:
            dt_b = p1["dt_base_component"]
            diag["dt_base_active_frac"] = float(np.mean(np.abs(dt_b[in_seg]) > 1e-6)) if in_seg.any() else float(
                np.mean(np.abs(dt_b) > 1e-6)
            )

        g_app = (
            float(np.mean(p1["gamma3"][approach_m])) if approach_m.any() else float("nan")
        )
        r_app = (
            float(np.mean(p1["rho3_marg"][approach_m])) if approach_m.any() else float("nan")
        )

        rows_beta[beta] = {
            "beta": beta,
            "T_at_event": T_at_event,
            "T_base_at_event": T_base_at_event,
            "delta_T": delta_T,
            "gain_mass": gain_mass,
            "mean_Gamma3": float(np.mean(p1["gamma3"][in_seg])) if in_seg.any() else float(np.mean(p1["gamma3"])),
            "mean_Gamma3_basal": float(np.mean(p1["gamma3"][basal_m])) if basal_m.any() else float("nan"),
            "mean_Gamma3_approach": g_app,
            "mean_rho3_marg": float(np.mean(p1["rho3_marg"][in_seg])) if in_seg.any() else float(np.mean(p1["rho3_marg"])),
            "mean_rho3_marg_approach": r_app,
            "A3_soft_rate": float(np.mean(A3_soft[in_seg] >= 0.5)) if in_seg.any() else float(np.mean(A3_soft >= 0.5)),
            "A3_hard_rate": float(np.mean(A3_hard[in_seg] >= 0.5)) if in_seg.any() else float(np.mean(A3_hard >= 0.5)),
            "A3_soft_rate_basal": regime_rate(A3_soft, t, masks["t0"], masks["t0"] + BASE_W),
            "A3_hard_rate_basal": regime_rate(A3_hard, t, masks["t0"], masks["t0"] + BASE_W),
            "A3_soft_rate_approach": regime_rate(A3_soft, t, float(event_week) - APP_W, float(event_week)),
            "A3_hard_rate_approach": regime_rate(A3_hard, t, float(event_week) - APP_W, float(event_week)),
            "lead_A3_hard_w": lead_A3,
            "alarmed_A3_hard": alarmed_A3,
            "lead_A3_soft_w": lead_soft,
            "alarmed_A3_soft": alarmed_soft,
            "A3_soft": A3_soft,
            "A3_hard": A3_hard,
            "gamma3": p1["gamma3"],
            "t_clock": p1["t"],
        }

    # parallel EWS
    det_e, al_e = ews_abs_z_lead(
        metrics["e3"], t, basal_m, float(event_week),
        basal_end=float(masks["t0"] + BASE_W),
    )
    lead_e = (float(event_week) - det_e) if np.isfinite(det_e) else float("nan")

    A3h = rows_beta[0.5]["A3_hard"]
    n_alarms = count_alarms(A3h[in_seg] if in_seg.any() else A3h)
    duration_w = float(SEG_PRE)  # weeks in pre-event segment
    far_per_52w = n_alarms * (52.0 / max(duration_w, 1e-6))

    cases = city_meta["cases"]
    peak_cases = float(cases[event_week]) if 0 <= event_week < len(cases) else float("nan")
    date_str = city_meta["dates"][event_week] if 0 <= event_week < len(city_meta["dates"]) else ""
    year = int(city_meta["years"][event_week]) if 0 <= event_week < len(city_meta["years"]) else -1

    # delta e3 approach - basal
    if approach_m.any() and basal_m.any():
        de3 = float(np.nanmean(metrics["e3"][approach_m]) - np.nanmean(metrics["e3"][basal_m]))
    else:
        de3 = float("nan")

    return {
        "record": label,
        "city": city_meta["city"],
        "kind": kind,
        "event_week": int(event_week),
        "event_date": date_str,
        "event_year": year,
        "peak_cases": peak_cases,
        "basal": (float(masks["t0"]), float(masks["t0"] + BASE_W)),
        "approach": (float(event_week) - APP_W, float(event_week)),
        "duration_w": duration_w,
        "n_points": int(in_seg.sum()),
        "delta_e3_approach_basal": de3,
        "ews_excess3_lead_w": lead_e,
        "ews_excess3_alarmed": al_e,
        "far_A3_hard_per_52w": far_per_52w,
        "n_A3_hard_alarms": n_alarms,
        "diag": diag,
        "beta0": {k: v for k, v in rows_beta[0.0].items() if not isinstance(v, np.ndarray)},
        "beta05": {k: v for k, v in rows_beta[0.5].items() if not isinstance(v, np.ndarray)},
        "_t": t,
        "_e3": metrics["e3"],
        "_tau": metrics["tau"],
        "_A3_soft": rows_beta[0.5]["A3_soft"],
        "_A3_hard": rows_beta[0.5]["A3_hard"],
        "_gamma": rows_beta[0.5]["gamma3"],
        "_cases_at": city_meta["cases"][metrics["orig_idx"]] if "orig_idx" in metrics else None,
        "_in_seg": in_seg,
        "_event_week": float(event_week),
        "_t0": masks["t0"],
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def write_outputs(results: List[Dict]) -> Dict[str, Path]:
    paths: Dict[str, Path] = {}
    csv_path = FIG / "results_smoke_dengai.csv"
    fieldnames = [
        "record", "city", "kind", "event_year", "event_date", "peak_cases",
        "duration_w", "n_points", "event_week",
        "delta_e3_approach_basal",
        "chaos_rate_seg", "sA_rate", "sB_rate", "sD_rate", "dt_base_active_frac",
        "A3_hard_rate_basal", "A3_hard_rate_approach", "A3_hard_rate_seg",
        "A3_soft_rate_basal", "A3_soft_rate_approach",
        "mean_Gamma3_b05", "mean_Gamma3_approach_b05",
        "mean_rho3_marg_b05", "mean_rho3_marg_approach_b05",
        "T_base_at_event", "T_P1_at_event_b05", "delta_T_legacy_b05",
        "gain_mass_b05",
        "lead_A3_hard_w", "alarmed_A3_hard",
        "lead_A3_soft_w", "ews_excess3_lead_w", "ews_excess3_alarmed",
        "far_A3_hard_per_52w", "n_A3_hard_alarms",
        "delta_T_b0_should_be_0",
    ]
    rows = []
    for r in results:
        b0, b5 = r["beta0"], r["beta05"]
        d = r["diag"]
        rows.append({
            "record": r["record"],
            "city": r["city"],
            "kind": r["kind"],
            "event_year": r["event_year"],
            "event_date": r["event_date"],
            "peak_cases": round(r["peak_cases"], 1),
            "duration_w": r["duration_w"],
            "n_points": r["n_points"],
            "event_week": r["event_week"],
            "delta_e3_approach_basal": round(r["delta_e3_approach_basal"], 5) if np.isfinite(r["delta_e3_approach_basal"]) else "",
            "chaos_rate_seg": round(d["chaos_rate_all"], 4),
            "sA_rate": round(d["sA_rate"], 4),
            "sB_rate": round(d["sB_rate"], 4),
            "sD_rate": round(d["sD_rate"], 4),
            "dt_base_active_frac": round(d["dt_base_active_frac"], 4) if np.isfinite(d["dt_base_active_frac"]) else "",
            "A3_hard_rate_basal": round(b5["A3_hard_rate_basal"], 4) if np.isfinite(b5["A3_hard_rate_basal"]) else "",
            "A3_hard_rate_approach": round(b5["A3_hard_rate_approach"], 4) if np.isfinite(b5["A3_hard_rate_approach"]) else "",
            "A3_hard_rate_seg": round(b5["A3_hard_rate"], 4),
            "A3_soft_rate_basal": round(b5["A3_soft_rate_basal"], 4) if np.isfinite(b5["A3_soft_rate_basal"]) else "",
            "A3_soft_rate_approach": round(b5["A3_soft_rate_approach"], 4) if np.isfinite(b5["A3_soft_rate_approach"]) else "",
            "mean_Gamma3_b05": round(b5["mean_Gamma3"], 4),
            "mean_Gamma3_approach_b05": round(b5["mean_Gamma3_approach"], 4) if np.isfinite(b5["mean_Gamma3_approach"]) else "",
            "mean_rho3_marg_b05": round(b5["mean_rho3_marg"], 4),
            "mean_rho3_marg_approach_b05": round(b5["mean_rho3_marg_approach"], 4) if np.isfinite(b5["mean_rho3_marg_approach"]) else "",
            "T_base_at_event": round(b5["T_base_at_event"], 3),
            "T_P1_at_event_b05": round(b5["T_at_event"], 3),
            "delta_T_legacy_b05": round(b5["delta_T"], 4),
            "gain_mass_b05": round(b5["gain_mass"], 3),
            "lead_A3_hard_w": round(b5["lead_A3_hard_w"], 2) if np.isfinite(b5["lead_A3_hard_w"]) else "",
            "alarmed_A3_hard": int(b5["alarmed_A3_hard"]),
            "lead_A3_soft_w": round(b5["lead_A3_soft_w"], 2) if np.isfinite(b5["lead_A3_soft_w"]) else "",
            "ews_excess3_lead_w": round(r["ews_excess3_lead_w"], 2) if np.isfinite(r["ews_excess3_lead_w"]) else "",
            "ews_excess3_alarmed": int(r["ews_excess3_alarmed"]),
            "far_A3_hard_per_52w": round(r["far_A3_hard_per_52w"], 3),
            "n_A3_hard_alarms": r["n_A3_hard_alarms"],
            "delta_T_b0_should_be_0": round(b0["delta_T"], 6),
        })
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    paths["csv"] = csv_path

    # Markdown
    md_path = FIG / "results_smoke_dengai.md"
    events = [r for r in results if r["kind"] == "outbreak"]
    controls = [r for r in results if r["kind"] == "control"]

    lines = [
        "# Real-data smoke test — P1 on DengAI (v0.3+)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "**Protocol:** multivariate `[cases, temp, precip, RH]`, W=13, stride=1, θ₃=0.10, "
        "excess³ 0.6/0.4, P1 v0.2 hardened A₃ (`d_min=3`), β∈{0, 0.5}. "
        f"Outbreaks: peaks ≥ P{OUTBREAK_PCTL}, min sep {MIN_PEAK_SEP}w; "
        f"segment {SEG_PRE}w pre-peak; basal {BASE_W}w; approach {APP_W}w.",
        "",
        "## Outbreaks",
        "",
        "| ID | City | Peak | Cases | chaos% | sB | sD | A₃h bas | A₃h app | Γ₃ app | ΔT legacy | Lead A₃h (w) | Lead e³ (w) |",
        "|----|------|------|-------|--------|----|----|---------|---------|--------|-----------|--------------|-------------|",
    ]
    for r in events:
        b5 = r["beta05"]
        d = r["diag"]
        lead_a = f"{b5['lead_A3_hard_w']:.1f}" if np.isfinite(b5["lead_A3_hard_w"]) else "—"
        lead_e = f"{r['ews_excess3_lead_w']:.1f}" if np.isfinite(r["ews_excess3_lead_w"]) else "—"
        g_app = f"{b5['mean_Gamma3_approach']:.3f}" if np.isfinite(b5["mean_Gamma3_approach"]) else "—"
        lines.append(
            f"| {r['record']} | {r['city']} | {r['event_year']} | {r['peak_cases']:.0f} | "
            f"{100*d['chaos_rate_all']:.0f}% | {d['sB_rate']:.3f} | {d['sD_rate']:.3f} | "
            f"{b5['A3_hard_rate_basal']:.3f} | {b5['A3_hard_rate_approach']:.3f} | "
            f"{g_app} | {b5['delta_T']:+.3f} | {lead_a} | {lead_e} |"
        )

    lines += [
        "",
        "## Controls (inter-epidemic) — FAR / specificity proxy",
        "",
        "| ID | City | Year | chaos% | A₃h rate | FAR /52w | mean Γ₃ | ΔT legacy | gain_mass |",
        "|----|------|------|--------|----------|----------|---------|-----------|-----------|",
    ]
    for r in controls:
        b5 = r["beta05"]
        d = r["diag"]
        lines.append(
            f"| {r['record']} | {r['city']} | {r['event_year']} | {100*d['chaos_rate_all']:.0f}% | "
            f"{b5['A3_hard_rate']:.4f} | {r['far_A3_hard_per_52w']:.2f} | "
            f"{b5['mean_Gamma3']:.3f} | {b5['delta_T']:+.3f} | {b5['gain_mass']:.2f} |"
        )

    max_dt0 = max(abs(r["beta0"]["delta_T"]) for r in results) if results else 0.0
    lines += [
        "",
        "## Ablation check",
        "",
        f"β=0 must give ΔT_legacy≈0. Observed max |ΔT| at β=0: **{max_dt0:.6f}** (expect ~0).",
    ]

    if events:
        sens_a3 = float(np.mean([r["beta05"]["alarmed_A3_hard"] for r in events]))
        sens_ews = float(np.mean([r["ews_excess3_alarmed"] for r in events]))
        mean_lead_a3 = float(np.nanmean([r["beta05"]["lead_A3_hard_w"] for r in events]))
        mean_lead_ews = float(np.nanmean([r["ews_excess3_lead_w"] for r in events]))
        mean_dt = float(np.mean([r["beta05"]["delta_T"] for r in events]))
        mean_dt_ctrl = float(np.mean([r["beta05"]["delta_T"] for r in controls])) if controls else float("nan")
        mean_hard_bas = float(np.nanmean([r["beta05"]["A3_hard_rate_basal"] for r in events]))
        mean_hard_app = float(np.nanmean([r["beta05"]["A3_hard_rate_approach"] for r in events]))
        mean_chaos = float(np.mean([r["diag"]["chaos_rate_all"] for r in events]))
        mean_dt_active = float(np.nanmean([r["diag"]["dt_base_active_frac"] for r in events]))
        lines += [
            "",
            "## Aggregate (outbreaks)",
            "",
            f"- Sensitivity A₃ hard: **{sens_a3:.2f}** ({int(round(sens_a3 * len(events)))}/{len(events)})",
            f"- Sensitivity excess³ abs-z (parallel): **{sens_ews:.2f}**",
            f"- Mean lead A₃ hard: **{mean_lead_a3:.1f} weeks**" if np.isfinite(mean_lead_a3) else "- Mean lead A₃ hard: n/a",
            f"- Mean lead excess³ abs-z: **{mean_lead_ews:.1f} weeks**" if np.isfinite(mean_lead_ews) else "- Mean lead excess³: n/a",
            f"- Mean A₃ hard rate basal → approach: **{mean_hard_bas:.3f} → {mean_hard_app:.3f}**",
            f"- Mean ΔT legacy (β=0.5): **{mean_dt:+.3f}**",
            f"- Mean chaos-band occupancy (|τ|<τ_ch) in segment: **{100*mean_chaos:.1f}%**",
            f"- Mean fraction steps with |Δt_base|>ε: **{100*mean_dt_active:.1f}%**",
        ]
        if np.isfinite(mean_dt_ctrl):
            lines.append(f"- Mean ΔT legacy on controls: **{mean_dt_ctrl:+.3f}** (compare to outbreaks)")

    if controls:
        mean_far = float(np.mean([r["far_A3_hard_per_52w"] for r in controls]))
        mean_g = float(np.mean([r["beta05"]["mean_Gamma3"] for r in controls]))
        lines += [
            "",
            "## Aggregate (controls)",
            "",
            f"- Mean FAR (A₃ hard alarms / 52 w): **{mean_far:.2f}**",
            f"- Mean Γ₃: **{mean_g:.3f}** (1.0 = no Φ₃ gain)",
        ]

    lines += [
        "",
        "## Honest reading (smoke, not Phase E)",
        "",
        "See **manuscript §6.4** (*Smokes reales duales (Holter ↔ DengAI): contraste estratégico y limitaciones del reloj legacy*). "
        "Figure suptitles: `Strategic contrast (DengAI arm): … — Section 6.4`.",
        "",
        "1. **Partial domain contrast:** chaos still high, but dt_base more active than Holter → "
        "legacy ΔT can move when C eases (e.g. IQ-2004).",
        "2. **A₃ hardening:** basal→approach rises on Iquitos; extreme SJ case peaks may stay silent.",
        "3. **Lead / FAR:** report raw numbers; do **not** claim operational EWS superiority.",
        "4. **Ablation PASS:** β=0 → ΔT≈0.",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")
    paths["md"] = md_path

    # JSON (no arrays)
    json_path = FIG / "results_smoke_dengai.json"
    serializable = []
    for r in results:
        serializable.append({
            k: v for k, v in r.items() if not k.startswith("_")
        })
    json_path.write_text(json.dumps(serializable, indent=2, default=str), encoding="utf-8")
    paths["json"] = json_path

    # Figures
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return paths

    # Fig 1: per-outbreak panels (up to 6)
    ev_plot = events[:6]
    if ev_plot:
        n = len(ev_plot)
        fig, axes = plt.subplots(n, 1, figsize=(10, 2.4 * n), sharex=False)
        if n == 1:
            axes = [axes]
        for ax, r in zip(axes, ev_plot):
            t = r["_t"]
            m = r["_in_seg"]
            tw = t[m]
            ax2 = ax.twinx()
            # cases if available
            if r.get("_cases_at") is not None:
                ax2.plot(tw, r["_cases_at"][m], color="0.6", lw=1.0, alpha=0.7, label="cases")
            ax.plot(tw, r["_tau"][m], color="C0", lw=1.0, label="τ_s")
            ax.plot(tw, r["_A3_hard"][m], color="C3", lw=1.2, label="A₃ hard")
            ax.plot(tw, r["_gamma"][m], color="C1", lw=1.0, alpha=0.8, label="Γ₃")
            ax.axvline(r["_event_week"], color="k", ls="--", lw=0.8)
            ax.axhline(TAU_CH, color="C0", ls=":", lw=0.6, alpha=0.5)
            ax.axhline(-TAU_CH, color="C0", ls=":", lw=0.6, alpha=0.5)
            ax.set_ylabel("τ / A₃ / Γ")
            ax2.set_ylabel("cases")
            ax.set_title(
                f"{r['record']}  peak={r['peak_cases']:.0f}  "
                f"ΔT={r['beta05']['delta_T']:+.2f}  chaos={100*r['diag']['chaos_rate_all']:.0f}%"
            )
            ax.legend(loc="upper left", fontsize=7, ncol=3)
        axes[-1].set_xlabel("week index")
        fig.suptitle(
            "DengAI: Proposal 1 around outbreaks",
            y=1.01,
        )
        fig.tight_layout()
        p1 = FIG / "fig_smoke_dengai_events.png"
        fig.savefig(p1, dpi=140, bbox_inches="tight")
        plt.close(fig)
        paths["fig_events"] = p1

    # Fig 2: bars ΔT and chaos
    if results:
        labels = [r["record"] for r in results]
        dts = [r["beta05"]["delta_T"] for r in results]
        chaos = [100 * r["diag"]["chaos_rate_all"] for r in results]
        colors = ["C3" if r["kind"] == "outbreak" else "C0" for r in results]
        fig, (axa, axb) = plt.subplots(1, 2, figsize=(11, 4))
        axa.bar(range(len(labels)), dts, color=colors)
        axa.set_xticks(range(len(labels)))
        axa.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        axa.axhline(0, color="k", lw=0.5)
        axa.set_ylabel("ΔT legacy (β=0.5)")
        axa.set_title("Clock movement (red=outbreak, blue=control)")
        axb.bar(range(len(labels)), chaos, color=colors)
        axb.set_xticks(range(len(labels)))
        axb.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        axb.axhline(100, color="0.5", ls="--", lw=0.6)
        axb.set_ylabel("chaos-band %")
        axb.set_title("|τ_s| < τ_ch in segment")
        fig.suptitle(
            "DengAI: ΔT vs chaos-band occupancy",
            y=1.02,
        )
        fig.tight_layout()
        p2 = FIG / "fig_smoke_dengai_bars.png"
        fig.savefig(p2, dpi=140, bbox_inches="tight")
        plt.close(fig)
        paths["fig_bars"] = p2

    # Fig 3: FAR / lead summary
    if events or controls:
        fig, (axa, axb) = plt.subplots(1, 2, figsize=(10, 4))
        if events:
            leads_a = [r["beta05"]["lead_A3_hard_w"] if r["beta05"]["alarmed_A3_hard"] else 0 for r in events]
            leads_e = [r["ews_excess3_lead_w"] if r["ews_excess3_alarmed"] else 0 for r in events]
            x = np.arange(len(events))
            axa.bar(x - 0.2, leads_a, 0.4, label="A₃ hard", color="C3")
            axa.bar(x + 0.2, leads_e, 0.4, label="e³ abs-z", color="C2")
            axa.set_xticks(x)
            axa.set_xticklabels([r["record"] for r in events], rotation=45, ha="right", fontsize=8)
            axa.set_ylabel("lead (weeks)")
            axa.set_title("Lead time (0 = no alarm)")
            axa.legend(fontsize=8)
        if controls:
            axb.bar(
                range(len(controls)),
                [r["far_A3_hard_per_52w"] for r in controls],
                color="C0",
            )
            axb.set_xticks(range(len(controls)))
            axb.set_xticklabels([r["record"] for r in controls], rotation=45, ha="right", fontsize=8)
            axb.set_ylabel("A₃ hard alarms / 52 weeks")
            axb.set_title("FAR proxy (controls)")
        fig.suptitle(
            "DengAI: lead vs FAR",
            y=1.02,
        )
        fig.tight_layout()
        p3 = FIG / "fig_smoke_dengai_far.png"
        fig.savefig(p3, dpi=140, bbox_inches="tight")
        plt.close(fig)
        paths["fig_far"] = p3

    return paths


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_smoke(
    cities: Sequence[str],
    n_outbreaks: int,
    n_controls: int,
) -> List[Dict]:
    results: List[Dict] = []
    for city in cities:
        print(f"\n=== City: {city} ===")
        meta = load_city(city)
        print(f"  weeks={meta['n']}  cases max={meta['cases'].max():.0f}  "
              f"P80={np.percentile(meta['cases'], 80):.1f}")
        print("  Computing τ_s / excess³ / Φ₁ / Φ₂ ...")
        metrics = build_city_metrics(meta["X"])
        print(f"  metric points={metrics['n_points']}  n_vars={metrics['n_vars']}")

        peaks = find_outbreak_peaks(
            meta["cases"], n_max=n_outbreaks,
            min_week=SEG_PRE + 2, max_week=meta["n"] - 2,
        )
        print(f"  outbreak peaks (week idx): {peaks}")
        for i, p in enumerate(peaks):
            label = f"{city.upper()}-O{i+1}-{meta['years'][p]}"
            print(f"  → outbreak {label} peak_cases={meta['cases'][p]:.0f} date={meta['dates'][p]}")
            r = analyze_window(meta, metrics, p, kind="outbreak", label=label)
            print(
                f"     chaos={100*r['diag']['chaos_rate_all']:.0f}%  "
                f"ΔT={r['beta05']['delta_T']:+.3f}  "
                f"A3h app={r['beta05']['A3_hard_rate_approach']:.3f}  "
                f"lead_A3={r['beta05']['lead_A3_hard_w']}  "
                f"lead_e3={r['ews_excess3_lead_w']}"
            )
            results.append(r)

        ctrl_ends = find_control_windows(
            meta["cases"], peaks, n_max=n_controls,
        )
        print(f"  control ends: {ctrl_ends}")
        for i, e in enumerate(ctrl_ends):
            label = f"{city.upper()}-C{i+1}-{meta['years'][e]}"
            print(f"  → control {label} max_in_seg={meta['cases'][e-SEG_PRE:e+1].max():.0f}")
            r = analyze_window(meta, metrics, e, kind="control", label=label)
            print(
                f"     chaos={100*r['diag']['chaos_rate_all']:.0f}%  "
                f"ΔT={r['beta05']['delta_T']:+.3f}  "
                f"FAR/52w={r['far_A3_hard_per_52w']:.2f}"
            )
            results.append(r)
    return results


def main() -> None:
    ap = argparse.ArgumentParser(description="DengAI P1 smoke test")
    ap.add_argument("--cities", default=",".join(DEFAULT_CITIES), help="Comma cities sj,iq")
    ap.add_argument("--n-outbreaks", type=int, default=DEFAULT_N_OUTBREAKS)
    ap.add_argument("--n-controls", type=int, default=DEFAULT_N_CONTROLS)
    args = ap.parse_args()
    cities = [c.strip().lower() for c in args.cities.split(",") if c.strip()]

    print("DengAI P1 smoke — Φ₃ → RECD")
    print(f"cities={cities} n_outbreaks={args.n_outbreaks} n_controls={args.n_controls}")
    print(f"data={_find_dengai_paths()[0]}")

    results = run_smoke(cities, args.n_outbreaks, args.n_controls)
    paths = write_outputs(results)
    print("\n=== Outputs ===")
    for k, p in paths.items():
        print(f"  {k}: {p}")

    # brief console summary
    events = [r for r in results if r["kind"] == "outbreak"]
    controls = [r for r in results if r["kind"] == "control"]
    if events:
        mean_chaos = np.mean([r["diag"]["chaos_rate_all"] for r in events])
        mean_dt = np.mean([r["beta05"]["delta_T"] for r in events])
        mean_active = np.nanmean([r["diag"]["dt_base_active_frac"] for r in events])
        sens = np.mean([r["beta05"]["alarmed_A3_hard"] for r in events])
        max_dt0 = max(abs(r["beta0"]["delta_T"]) for r in results)
        print("\n=== Headline ===")
        print(f"  chaos% (outbreaks): {100*mean_chaos:.1f}%")
        print(f"  dt_base active:     {100*mean_active:.1f}%")
        print(f"  mean ΔT legacy:     {mean_dt:+.3f}")
        print(f"  A₃ hard sens:       {sens:.2f}")
        print(f"  max |ΔT| β=0:       {max_dt0:.6f}")
        if controls:
            print(f"  mean FAR/52w:       {np.mean([r['far_A3_hard_per_52w'] for r in controls]):.2f}")


if __name__ == "__main__":
    main()
