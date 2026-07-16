#!/usr/bin/env python3
"""
Real-data smoke test: P1 (Φ₃ → RECD clock) on SDDB Holter + NSRDB controls.

Protocol (pre-specified, modest, preprint-smoke — not full Phase E):
  - Event records: SDDB analytic subset (default 30, 31, 35).
  - Controls: NSRDB cleaned RR (default 16265, 16272).
  - Metrics: same bivariate proxy + excess³ pipeline as CCTP pilot.
  - Run P1 with β=0 (ablation / base clock) vs β=0.5 (v0.2 default).
  - Report:
      * A₃ rates in basal vs approach (events) and full-record (controls)
      * mean Γ₃, ρ₃^marg, ΔT = T_P1 − T_base
      * lead time of first sustained hard A₃ alarm vs abs-z excess³
      * control FAR proxy: hard-A₃ alarms per 24 h

Note on d_obs=2:
  Holter uses the CCTP bivariate proxy [z(RR), z(|ΔRR|)]. Classical 3-variable
  PID is not claimed. A₃ is enabled with d_min=2 because Level-3 here is the
  nested ordinal surplus (excess³) already validated on this proxy, not a
  three-way PID atom.

Usage:
  cd .../Preprint_Phi3_RECD_Dynamic_Integration/src
  python3 smoke_real_sddb.py
  python3 smoke_real_sddb.py --events 30,31 --controls 16265 --quick
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SRC))

from phi3_recd import (  # noqa: E402
    ActivationConfig,
    P1Config,
    activation_A3,
    normalize_vs_baseline,
    baseline_scale_stats,
    gate_piecewise,
    recd_p1,
    TAU_CH,
)

# CCTP pilot paths
CCTP = ROOT.parent / "Cardiac_CCTP_Pilot"
CCTP_CODE = CCTP / "code"
CCTP_DATA = CCTP / "data"
CCTP_EXT = CCTP_DATA / "rr_external"

sys.path.insert(0, str(CCTP_CODE))

from cctp_metrics_core import (  # noqa: E402
    STRIDE,
    W_TAU,
    build_bivariate_proxy,
    detect_lead_time,
    get_event_and_windows,
)
from recd_ordinal_levels import (  # noqa: E402
    compute_phi1,
    compute_phi2,
    compute_phi3,
    generate_multivariate_symbols,
)

# Smoke defaults
THETA3 = 0.08  # CCTP recalibrated for real RR
MIN_CONSEC = 3
Z_THRESH = 2.0
DEFAULT_EVENTS = ["30", "31", "35"]
DEFAULT_CONTROLS = ["16265", "16272"]

# Bivariate Holter: allow A3 (see module docstring)
ACT_SOFT = ActivationConfig(d_min=2)
ACT_HARD = ActivationConfig(d_min=2, soft=False)


# ---------------------------------------------------------------------------
# Series construction
# ---------------------------------------------------------------------------

def compute_tau_series(rr: np.ndarray) -> np.ndarray:
    """τ_s series (systemictau if available; else rolling Spearman on proxy)."""
    try:
        from _bootstrap import import_systemictau_core

        compute_taus, _, has = import_systemictau_core()
        if has and compute_taus is not None:
            X = build_bivariate_proxy(rr)
            taus, _ = compute_taus(X, window_size=W_TAU, stride=STRIDE)
            return np.asarray(taus, dtype=float)
    except Exception:
        pass

    X = build_bivariate_proxy(rr)
    n = len(rr)
    out = np.full(n, np.nan)
    for i in range(W_TAU - 1, n, STRIDE):
        win = X[i - W_TAU + 1 : i + 1]
        r0 = win[:, 0].argsort().argsort().astype(float)
        r1 = win[:, 1].argsort().argsort().astype(float)
        if np.std(r0) > 0 and np.std(r1) > 0:
            out[i] = float(np.corrcoef(r0, r1)[0, 1])
    return out


def build_aligned_metrics(
    rr: np.ndarray,
    t_hr: np.ndarray,
    *,
    theta3: float = THETA3,
    max_points: Optional[int] = None,
) -> Dict[str, np.ndarray]:
    """
    Compute tau, excess3, phi1, phi2 and align to valid excess3 samples.
    Optionally decimate to max_points for speed (--quick).
    """
    X = build_bivariate_proxy(rr)
    S = generate_multivariate_symbols(X, m=3, delay=1)
    offset = (3 - 1) * 1
    t_sym = t_hr[offset : offset + len(S)]

    phi1 = compute_phi1(S)
    phi2 = compute_phi2(S, d=4)
    _, excess3 = compute_phi3(S, window=W_TAU, theta=theta3, stride=STRIDE)

    tau_full = compute_tau_series(rr)
    # excess3 is NaN-padded length of S; take valid strided points
    valid = ~np.isnan(excess3)
    idx = np.where(valid)[0]
    if max_points is not None and len(idx) > max_points:
        step = int(np.ceil(len(idx) / max_points))
        idx = idx[::step]

    # align tau to symbol index + beat offset
    tau_at = np.full(len(idx), np.nan)
    for j, i in enumerate(idx):
        beat = min(offset + int(i), len(tau_full) - 1)
        # nearest non-nan tau in a small neighborhood
        lo = max(0, beat - STRIDE * 2)
        hi = min(len(tau_full), beat + STRIDE * 2 + 1)
        seg = tau_full[lo:hi]
        ok = ~np.isnan(seg)
        if ok.any():
            tau_at[j] = float(seg[ok][np.argmin(np.abs(np.where(ok)[0] - (beat - lo)))])
        else:
            tau_at[j] = 0.0  # neutral if missing

    # fill any remaining nan tau with 0
    tau_at = np.nan_to_num(tau_at, nan=0.0)

    return {
        "t_hr": t_sym[idx].astype(float),
        "tau": tau_at.astype(float),
        "e3": excess3[idx].astype(float),
        "phi1": phi1[idx].astype(float),
        "phi2": phi2[idx].astype(float),
        "n_points": len(idx),
        "n_beats": len(rr),
    }


def load_event(rec: str) -> Dict:
    npz = CCTP_DATA / f"rr_{rec}_clean.npz"
    if not npz.exists():
        raise FileNotFoundError(npz)
    d = np.load(npz)
    rr = d["rr_ms"].astype(float)
    t_sec = d["t_sec"].astype(float)
    vfon_sec = float(d["vfon_sec"])
    t_hr = t_sec / 3600.0
    vfon_hr = vfon_sec / 3600.0
    event_hr, basal, approach = get_event_and_windows(rec, t_hr, vfon_hr)
    return {
        "record": rec,
        "kind": "event",
        "rr": rr,
        "t_hr_beat": t_hr,
        "event_hr": event_hr,
        "basal": basal,
        "approach": approach,
        "duration_h": float(t_hr[-1] - t_hr[0]) if len(t_hr) else 0.0,
    }


def load_control(rec: str) -> Dict:
    npz = CCTP_EXT / f"nsrdb_{rec}_clean.npz"
    if not npz.exists():
        raise FileNotFoundError(npz)
    d = np.load(npz)
    rr = d["rr_ms"].astype(float)
    t_sec = d["t_sec"].astype(float)
    t_hr = t_sec / 3600.0
    duration = float(d["total_hours"]) if "total_hours" in d.files else float(t_hr[-1])
    # basal = first 3 h; "approach" = last 3 h (no event — for regime comparison only)
    basal = (0.5, 3.5)
    approach = (max(0.5, duration - 3.0), duration)
    return {
        "record": rec,
        "kind": "control",
        "rr": rr,
        "t_hr_beat": t_hr,
        "event_hr": duration,
        "basal": basal,
        "approach": approach,
        "duration_h": duration,
    }


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def first_sustained_alarm(
    signal: np.ndarray,
    t_hr: np.ndarray,
    *,
    t0: float,
    t1: float,
    threshold: float = 0.5,
    min_consecutive: int = MIN_CONSEC,
) -> Tuple[float, float]:
    """First time signal >= threshold for min_consecutive samples in (t0, t1)."""
    mask = (t_hr > t0) & (t_hr < t1) & np.isfinite(signal)
    t_s = t_hr[mask]
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


def regime_rate(x: np.ndarray, t: np.ndarray, win: Tuple[float, float], thr: float = 0.5) -> float:
    m = (t >= win[0]) & (t <= win[1]) & np.isfinite(x)
    if m.sum() == 0:
        return float("nan")
    return float(np.mean(x[m] >= thr))


def holter_clock_accumulate(
    tau_s: np.ndarray,
    gamma: np.ndarray,
    delta_t0: float = 1.0,
) -> np.ndarray:
    """
    Domain-aware clock when |τ_s| < τ_ch is nearly continuous (Holter).

    Legacy RECD applies Feigenbaum depth compression in the chaos band; under
    chronic low-|τ| that freezes Δt≈0 so Γ₃ cannot move T. This path uses
    Δt = Δt0 · g(τ) · Γ only (no depth), for diagnostic ΔT comparison.
    """
    tau_s = np.asarray(tau_s, dtype=float)
    gamma = np.asarray(gamma, dtype=float)
    t = np.zeros(len(tau_s) + 1, dtype=float)
    for k in range(len(tau_s)):
        g = gate_piecewise(float(tau_s[k]))
        t[k + 1] = t[k] + delta_t0 * g * float(gamma[k])
    return t


def analyze_record(
    meta: Dict,
    *,
    theta3: float,
    max_points: Optional[int],
) -> Dict:
    m = build_aligned_metrics(meta["rr"], meta["t_hr_beat"], theta3=theta3, max_points=max_points)
    t = m["t_hr"]
    basal = meta["basal"]
    approach = meta["approach"]
    event_hr = meta["event_hr"]

    baseline_mask = (t >= basal[0]) & (t <= basal[1])
    if baseline_mask.sum() < 5:
        # fallback: first 20% of series
        n = len(t)
        baseline_mask = np.zeros(n, dtype=bool)
        baseline_mask[: max(5, n // 5)] = True

    # condition diagnostics (once, soft path with return_parts)
    e3n0 = normalize_vs_baseline(m["e3"], baseline_mask, mode="zscore")
    stats0 = baseline_scale_stats(m["e3"], baseline_mask)
    _, parts = activation_A3(
        m["tau"], e3n0, m["phi1"], m["phi2"],
        n_vars=2, cfg=ACT_SOFT, abs_delta=True, baseline_stats=stats0, return_parts=True,
    )
    in_chaos = np.abs(m["tau"]) < TAU_CH
    app_m = (t >= approach[0]) & (t < approach[1])
    diag = {
        "chaos_rate_all": float(in_chaos.mean()),
        "chaos_rate_approach": float(in_chaos[app_m].mean()) if app_m.any() else float("nan"),
        "mean_abs_tau": float(np.mean(np.abs(m["tau"]))),
        "sA_rate": float(parts["sA"].mean()),
        "sB_level_rate": float(parts["sB_level"].mean()),
        "sB_change_rate": float(parts["sB_change"].mean()),
        "sB_rate": float(parts["sB"].mean()),
        "sC_rate": float(parts["sC"].mean()),
        "sD_rate": float(parts["sD"].mean()),
        "theta_e_eff": float(parts["theta_e_eff"][0]),
        "dt_base_active_frac": float("nan"),  # filled after first p1
    }

    rows_beta = {}
    for beta in (0.0, 0.5):
        p1 = recd_p1(
            m["tau"],
            m["e3"],
            baseline_mask,
            phi1=m["phi1"],
            phi2=m["phi2"],
            n_vars=2,
            cfg=P1Config(beta=beta),
            act_cfg=ACT_SOFT,
        )
        # hard A3 for rates / lead
        e3n = p1["e3_norm"]
        stats = baseline_scale_stats(m["e3"], baseline_mask)
        A3_hard = activation_A3(
            m["tau"], e3n, m["phi1"], m["phi2"],
            n_vars=2, cfg=ACT_HARD, abs_delta=True, baseline_stats=stats,
        )
        A3_soft = p1["A3"]

        T_final = float(p1["t"][-1])
        # T at event (last sample before event_hr)
        pre = t < event_hr
        if pre.any():
            k_ev = int(np.where(pre)[0][-1])
            T_at_event = float(p1["t"][k_ev + 1])
        else:
            T_at_event = T_final
            k_ev = len(t) - 1

        # base component clock (same for both betas when β=0 path; recompute from dt_base)
        T_base_at_event = float(np.sum(p1["dt_base_component"][pre])) if pre.any() else float(np.sum(p1["dt_base_component"]))

        # Holter-aware clock (no Feigenbaum depth)
        ones = np.ones_like(p1["gamma3"])
        T_h_base = holter_clock_accumulate(m["tau"], ones)
        T_h_p1 = holter_clock_accumulate(m["tau"], p1["gamma3"])
        T_h_base_ev = float(T_h_base[k_ev + 1])
        T_h_p1_ev = float(T_h_p1[k_ev + 1])

        # Φ₃ gain mass independent of clock: sum(A3 * (Γ-1)/β) ≈ sum(A3·ψ) when β>0
        if beta > 0:
            gain_mass = float(np.sum(np.maximum(p1["gamma3"] - 1.0, 0.0) / beta))
        else:
            gain_mass = 0.0

        det_hr_A3, alarmed_A3 = first_sustained_alarm(
            A3_hard, t, t0=basal[1], t1=event_hr, threshold=0.5, min_consecutive=MIN_CONSEC,
        )
        lead_A3 = (event_hr - det_hr_A3) if np.isfinite(det_hr_A3) else float("nan")

        # soft A3 lead (A3 soft > 0.5)
        det_hr_soft, alarmed_soft = first_sustained_alarm(
            A3_soft, t, t0=basal[1], t1=event_hr, threshold=0.5, min_consecutive=MIN_CONSEC,
        )
        lead_soft = (event_hr - det_hr_soft) if np.isfinite(det_hr_soft) else float("nan")

        if beta == 0.5:
            diag["dt_base_active_frac"] = float(np.mean(np.abs(p1["dt_base_component"]) > 1e-6))

        rows_beta[beta] = {
            "beta": beta,
            "T_final": T_final,
            "T_at_event": T_at_event,
            "T_base_at_event": T_base_at_event,
            "delta_T": T_at_event - T_base_at_event,
            "T_holter_base": T_h_base_ev,
            "T_holter_p1": T_h_p1_ev,
            "delta_T_holter": T_h_p1_ev - T_h_base_ev,
            "gain_mass": gain_mass,
            "mean_Gamma3": float(np.mean(p1["gamma3"])),
            "mean_Gamma3_basal": float(np.mean(p1["gamma3"][baseline_mask])) if baseline_mask.any() else float("nan"),
            "mean_Gamma3_approach": float(np.mean(p1["gamma3"][(t >= approach[0]) & (t < approach[1])]))
            if np.any((t >= approach[0]) & (t < approach[1])) else float("nan"),
            "mean_rho3_marg": float(np.mean(p1["rho3_marg"])),
            "mean_rho3_marg_approach": float(np.mean(p1["rho3_marg"][(t >= approach[0]) & (t < approach[1])]))
            if np.any((t >= approach[0]) & (t < approach[1])) else float("nan"),
            "A3_soft_rate": float(np.mean(A3_soft >= 0.5)),
            "A3_hard_rate": float(np.mean(A3_hard >= 0.5)),
            "A3_soft_rate_basal": regime_rate(A3_soft, t, basal),
            "A3_hard_rate_basal": regime_rate(A3_hard, t, basal),
            "A3_soft_rate_approach": regime_rate(A3_soft, t, approach),
            "A3_hard_rate_approach": regime_rate(A3_hard, t, approach),
            "lead_A3_hard_h": lead_A3,
            "alarmed_A3_hard": alarmed_A3,
            "lead_A3_soft_h": lead_soft,
            "alarmed_A3_soft": alarmed_soft,
            "A3_soft": A3_soft,
            "A3_hard": A3_hard,
            "gamma3": p1["gamma3"],
            "t_clock": p1["t"],
            "e3_norm": e3n,
        }

    # parallel EWS lead on raw excess3 (abs-z), same as CCTP leadtime script
    ews = detect_lead_time(
        m["e3"], t, event_hr, basal,
        z_threshold=Z_THRESH, min_consecutive=MIN_CONSEC, use_abs=True,
    )

    # FAR proxy for controls: hard A3 alarms per 24 h
    # Count runs of hard A3 >= 0.5 with min_consecutive, divide by duration
    A3h = rows_beta[0.5]["A3_hard"]
    n_alarms = 0
    run = 0
    in_alarm = False
    for a in A3h >= 0.5:
        if a:
            run += 1
            if run == MIN_CONSEC and not in_alarm:
                n_alarms += 1
                in_alarm = True
        else:
            run = 0
            in_alarm = False
    duration_h = max(meta["duration_h"], 1e-6)
    far_per_24h = n_alarms * (24.0 / duration_h)

    out = {
        "record": meta["record"],
        "kind": meta["kind"],
        "event_hr": event_hr,
        "basal": basal,
        "approach": approach,
        "duration_h": duration_h,
        "n_points": m["n_points"],
        "n_beats": m["n_beats"],
        "delta_e3_approach_basal": float(
            np.nanmean(m["e3"][(t >= approach[0]) & (t < approach[1])])
            - np.nanmean(m["e3"][baseline_mask])
        ) if baseline_mask.any() else float("nan"),
        "ews_excess3_lead_h": ews["lead_time_h"],
        "ews_excess3_alarmed": ews["alarmed"],
        "far_A3_hard_per_24h": far_per_24h,
        "n_A3_hard_alarms": n_alarms,
        "diag": diag,
        "beta0": {k: v for k, v in rows_beta[0.0].items() if not isinstance(v, np.ndarray)},
        "beta05": {k: v for k, v in rows_beta[0.5].items() if not isinstance(v, np.ndarray)},
        # keep arrays for plotting
        "_t": t,
        "_e3": m["e3"],
        "_tau": m["tau"],
        "_A3_soft": rows_beta[0.5]["A3_soft"],
        "_A3_hard": rows_beta[0.5]["A3_hard"],
        "_gamma": rows_beta[0.5]["gamma3"],
        "_t_clock_b0": rows_beta[0.0]["t_clock"],
        "_t_clock_b05": rows_beta[0.5]["t_clock"],
    }
    return out


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def write_outputs(results: List[Dict]) -> Dict[str, Path]:
    paths = {}
    # CSV summary
    csv_path = FIG / "results_smoke_real.csv"
    fieldnames = [
        "record", "kind", "duration_h", "n_points", "event_hr",
        "delta_e3_approach_basal",
        "chaos_rate_all", "sA_rate", "sB_rate", "sD_rate", "dt_base_active_frac",
        "A3_hard_rate_basal", "A3_hard_rate_approach", "A3_hard_rate_all",
        "A3_soft_rate_basal", "A3_soft_rate_approach",
        "mean_Gamma3_b05", "mean_Gamma3_approach_b05",
        "mean_rho3_marg_b05", "mean_rho3_marg_approach_b05",
        "T_base_at_event", "T_P1_at_event_b05", "delta_T_legacy_b05",
        "T_holter_base", "T_holter_p1", "delta_T_holter_b05", "gain_mass_b05",
        "lead_A3_hard_h", "alarmed_A3_hard",
        "lead_A3_soft_h", "ews_excess3_lead_h", "ews_excess3_alarmed",
        "far_A3_hard_per_24h", "n_A3_hard_alarms",
        "delta_T_b0_should_be_0",
    ]
    rows = []
    for r in results:
        b0, b5 = r["beta0"], r["beta05"]
        d = r["diag"]
        rows.append({
            "record": r["record"],
            "kind": r["kind"],
            "duration_h": round(r["duration_h"], 3),
            "n_points": r["n_points"],
            "event_hr": round(r["event_hr"], 3),
            "delta_e3_approach_basal": round(r["delta_e3_approach_basal"], 5),
            "chaos_rate_all": round(d["chaos_rate_all"], 4),
            "sA_rate": round(d["sA_rate"], 4),
            "sB_rate": round(d["sB_rate"], 4),
            "sD_rate": round(d["sD_rate"], 4),
            "dt_base_active_frac": round(d["dt_base_active_frac"], 4) if np.isfinite(d["dt_base_active_frac"]) else "",
            "A3_hard_rate_basal": round(b5["A3_hard_rate_basal"], 4),
            "A3_hard_rate_approach": round(b5["A3_hard_rate_approach"], 4),
            "A3_hard_rate_all": round(b5["A3_hard_rate"], 4),
            "A3_soft_rate_basal": round(b5["A3_soft_rate_basal"], 4),
            "A3_soft_rate_approach": round(b5["A3_soft_rate_approach"], 4),
            "mean_Gamma3_b05": round(b5["mean_Gamma3"], 4),
            "mean_Gamma3_approach_b05": round(b5["mean_Gamma3_approach"], 4) if np.isfinite(b5["mean_Gamma3_approach"]) else "",
            "mean_rho3_marg_b05": round(b5["mean_rho3_marg"], 4),
            "mean_rho3_marg_approach_b05": round(b5["mean_rho3_marg_approach"], 4) if np.isfinite(b5["mean_rho3_marg_approach"]) else "",
            "T_base_at_event": round(b5["T_base_at_event"], 2),
            "T_P1_at_event_b05": round(b5["T_at_event"], 2),
            "delta_T_legacy_b05": round(b5["delta_T"], 4),
            "T_holter_base": round(b5["T_holter_base"], 1),
            "T_holter_p1": round(b5["T_holter_p1"], 1),
            "delta_T_holter_b05": round(b5["delta_T_holter"], 1),
            "gain_mass_b05": round(b5["gain_mass"], 1),
            "lead_A3_hard_h": round(b5["lead_A3_hard_h"], 3) if np.isfinite(b5["lead_A3_hard_h"]) else "",
            "alarmed_A3_hard": int(b5["alarmed_A3_hard"]),
            "lead_A3_soft_h": round(b5["lead_A3_soft_h"], 3) if np.isfinite(b5["lead_A3_soft_h"]) else "",
            "ews_excess3_lead_h": round(r["ews_excess3_lead_h"], 3) if np.isfinite(r["ews_excess3_lead_h"]) else "",
            "ews_excess3_alarmed": int(r["ews_excess3_alarmed"]),
            "far_A3_hard_per_24h": round(r["far_A3_hard_per_24h"], 3),
            "n_A3_hard_alarms": r["n_A3_hard_alarms"],
            "delta_T_b0_should_be_0": round(b0["delta_T"], 4),
        })
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    paths["csv"] = csv_path

    # Markdown table
    md_path = FIG / "results_smoke_real.md"
    events = [r for r in results if r["kind"] == "event"]
    controls = [r for r in results if r["kind"] == "control"]

    lines = [
        "# Real-data smoke test — P1 on SDDB + NSRDB (v0.3)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "**Protocol:** bivariate proxy `[z(RR), z(|ΔRR|)]`, W=101, stride=5, θ₃=0.08, "
        "P1 defaults v0.2 (`β∈{0, 0.5}`, hardened A₃, `d_min=2` for Holter bivariate).",
        "",
        "## Event Holters (SDDB)",
        "",
        "| Rec | Δe₃ | chaos% | sB | sD | A₃h bas | A₃h app | Γ₃ app | ΔT legacy | ΔT Holter | Lead A₃h | Lead e³ abs-z |",
        "|-----|-----|--------|----|----|---------|---------|--------|-----------|-----------|----------|---------------|",
    ]
    for r in events:
        b5 = r["beta05"]
        d = r["diag"]
        lead_a = f"{b5['lead_A3_hard_h']:.2f}" if np.isfinite(b5["lead_A3_hard_h"]) else "—"
        lead_e = f"{r['ews_excess3_lead_h']:.2f}" if np.isfinite(r["ews_excess3_lead_h"]) else "—"
        g_app = f"{b5['mean_Gamma3_approach']:.3f}" if np.isfinite(b5["mean_Gamma3_approach"]) else "—"
        lines.append(
            f"| {r['record']} | {r['delta_e3_approach_basal']:+.4f} | "
            f"{100*d['chaos_rate_all']:.0f}% | {d['sB_rate']:.3f} | {d['sD_rate']:.3f} | "
            f"{b5['A3_hard_rate_basal']:.3f} | {b5['A3_hard_rate_approach']:.3f} | "
            f"{g_app} | {b5['delta_T']:+.3f} | {b5['delta_T_holter']:+.0f} | {lead_a} | {lead_e} |"
        )

    lines += [
        "",
        "## Controls (NSRDB) — FAR / specificity proxy",
        "",
        "| Rec | h | chaos% | A₃h rate | FAR /24h | mean Γ₃ | ΔT Holter | gain_mass |",
        "|-----|---|--------|----------|----------|---------|-----------|-----------|",
    ]
    for r in controls:
        b5 = r["beta05"]
        d = r["diag"]
        lines.append(
            f"| {r['record']} | {r['duration_h']:.1f} | {100*d['chaos_rate_all']:.0f}% | "
            f"{b5['A3_hard_rate']:.4f} | {r['far_A3_hard_per_24h']:.2f} | "
            f"{b5['mean_Gamma3']:.3f} | {b5['delta_T_holter']:+.0f} | {b5['gain_mass']:.0f} |"
        )

    # Aggregate interpretation block
    lines += [
        "",
        "## Ablation check",
        "",
        "β=0 must give ΔT_legacy≈0 and ΔT_Holter≈0 (Γ₃≡1). Observed max |ΔT_legacy| at β=0:",
    ]
    max_dt0 = max(abs(r["beta0"]["delta_T"]) for r in results)
    max_dth0 = max(abs(r["beta0"]["delta_T_holter"]) for r in results)
    lines.append(f"**legacy {max_dt0:.4f}**, **Holter {max_dth0:.4f}** (expect ~0).")

    if events:
        mean_lead_a3 = np.nanmean([r["beta05"]["lead_A3_hard_h"] for r in events])
        mean_lead_ews = np.nanmean([r["ews_excess3_lead_h"] for r in events])
        sens_a3 = np.mean([r["beta05"]["alarmed_A3_hard"] for r in events])
        sens_ews = np.mean([r["ews_excess3_alarmed"] for r in events])
        mean_dth = np.mean([r["beta05"]["delta_T_holter"] for r in events])
        mean_hard_bas = np.nanmean([r["beta05"]["A3_hard_rate_basal"] for r in events])
        mean_hard_app = np.nanmean([r["beta05"]["A3_hard_rate_approach"] for r in events])
        mean_chaos = np.mean([r["diag"]["chaos_rate_all"] for r in events])
        mean_dt_active = np.nanmean([r["diag"]["dt_base_active_frac"] for r in events])
        lines += [
            "",
            "## Aggregate (events)",
            "",
            f"- Sensitivity A₃ hard: **{sens_a3:.2f}** ({int(round(sens_a3 * len(events)))}/{len(events)})",
            f"- Sensitivity excess³ abs-z (parallel): **{sens_ews:.2f}**",
            f"- Mean lead A₃ hard: **{mean_lead_a3:.2f} h**" if np.isfinite(mean_lead_a3) else "- Mean lead A₃ hard: n/a (mostly no alarm)",
            f"- Mean lead excess³ abs-z: **{mean_lead_ews:.2f} h**" if np.isfinite(mean_lead_ews) else "- Mean lead excess³: n/a",
            f"- Mean A₃ hard rate basal → approach: **{mean_hard_bas:.3f} → {mean_hard_app:.3f}**",
            f"- Mean ΔT Holter (β=0.5): **{mean_dth:+.0f}**",
            f"- Mean chaos-band occupancy (|τ|<τ_ch): **{100*mean_chaos:.1f}%**",
            f"- Mean fraction of steps with |Δt_base|>ε (legacy): **{100*mean_dt_active:.2f}%**",
        ]
    if controls:
        mean_far = np.mean([r["far_A3_hard_per_24h"] for r in controls])
        mean_g = np.mean([r["beta05"]["mean_Gamma3"] for r in controls])
        mean_dth_c = np.mean([r["beta05"]["delta_T_holter"] for r in controls])
        lines += [
            "",
            "## Aggregate (controls)",
            "",
            f"- Mean FAR (A₃ hard alarms / 24 h): **{mean_far:.2f}**",
            f"- Mean Γ₃: **{mean_g:.3f}** (1.0 = no Φ₃ gain)",
            f"- Mean ΔT Holter: **{mean_dth_c:+.0f}** (compare to events)",
        ]

    lines += [
        "",
        "## Honest reading (smoke, not Phase E)",
        "",
        "See **manuscript §6.4** (*Smokes reales duales (Holter ↔ DengAI): contraste estratégico y limitaciones del reloj legacy*). "
        "Figure suptitles: `Strategic contrast (Holter arm): … — Section 6.4`.",
        "",
        "1. **Hyperpersistence of band C, not of A₃:** `|τ_s| < τ_ch` almost always → (A) always on; "
        "A₃ hard stays sparse via (B)∩(D).",
        "2. **Legacy ΔT ≈ 0:** Feigenbaum freezes Δt_base (~0.1% steps active). "
        "ΔT Holter (no depth) is diagnostic only.",
        "3. **Sensitivity trade-off:** A₃ hard stricter than parallel e³ abs-z (lower hit rate).",
        "4. **Specificity not won:** NSRDB FAR high; do not claim clinical FAR improvement.",
        "5. **Ablation PASS:** β=0 → Γ≡1. `d_min=2` intentional (bivariate CCTP).",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    paths["md"] = md_path

    # JSON (scalars only)
    json_path = FIG / "results_smoke_real.json"
    serial = []
    for r in results:
        serial.append({
            "record": r["record"],
            "kind": r["kind"],
            "duration_h": r["duration_h"],
            "n_points": r["n_points"],
            "event_hr": r["event_hr"],
            "basal": list(r["basal"]),
            "approach": list(r["approach"]),
            "delta_e3_approach_basal": r["delta_e3_approach_basal"],
            "ews_excess3_lead_h": r["ews_excess3_lead_h"] if np.isfinite(r["ews_excess3_lead_h"]) else None,
            "ews_excess3_alarmed": r["ews_excess3_alarmed"],
            "far_A3_hard_per_24h": r["far_A3_hard_per_24h"],
            "n_A3_hard_alarms": r["n_A3_hard_alarms"],
            "diag": r["diag"],
            "beta0": r["beta0"],
            "beta05": {
                k: (None if isinstance(v, float) and not np.isfinite(v) else v)
                for k, v in r["beta05"].items()
            },
        })
    json_path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "params": {
            "theta3": THETA3,
            "W_TAU": W_TAU,
            "stride": STRIDE,
            "beta": [0.0, 0.5],
            "d_min": 2,
            "act": "ActivationConfig v0.2 hardened",
            "z_threshold_ews": Z_THRESH,
            "min_consecutive": MIN_CONSEC,
        },
        "records": serial,
    }, indent=2, default=_json_default), encoding="utf-8")
    paths["json"] = json_path
    return paths


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def make_figures(results: List[Dict]) -> List[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    paths = []
    events = [r for r in results if r["kind"] == "event"]
    controls = [r for r in results if r["kind"] == "control"]

    # --- Overview panel: one row per event ---
    n = max(len(events), 1)
    fig, axes = plt.subplots(n, 1, figsize=(12, 3.2 * n), squeeze=False)
    for ax, r in zip(axes[:, 0], events):
        t = r["_t"]
        ax.plot(t, r["_e3"], color="#8e44ad", lw=0.8, alpha=0.85, label="excess³")
        ax2 = ax.twinx()
        ax2.fill_between(t, 0, r["_A3_hard"], color="#e74c3c", alpha=0.35, label="A₃ hard", step="mid")
        ax2.plot(t, r["_gamma"], color="#27ae60", lw=0.9, alpha=0.8, label="Γ₃ (β=0.5)")
        ax2.set_ylim(-0.05, max(2.5, float(np.nanmax(r["_gamma"])) * 1.05))
        ax.axvspan(r["basal"][0], r["basal"][1], color="#1f77b4", alpha=0.12)
        ax.axvspan(r["approach"][0], r["approach"][1], color="red", alpha=0.10)
        ax.axvline(r["event_hr"], color="#c0392b", ls="--", lw=1.5)
        ax.set_ylabel("excess³")
        ax2.set_ylabel("A₃ / Γ₃")
        ax.set_title(
            f"SDDB {r['record']}  |  lead A₃ hard="
            f"{r['beta05']['lead_A3_hard_h']:.2f}h" if np.isfinite(r["beta05"]["lead_A3_hard_h"])
            else f"SDDB {r['record']}  |  A₃ hard no alarm",
            fontsize=11,
        )
        ax.grid(True, alpha=0.25)
        # combined legend
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8)
    if events:
        axes[-1, 0].set_xlabel("Time (hours)")
    fig.suptitle(
        "Holter (SDDB): Proposal 1 on pre-VF series",
        fontsize=11,
        y=1.01,
    )
    fig.tight_layout()
    p = FIG / "fig_smoke_sddb_events.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths.append(p)

    # --- Bar comparison ---
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    if events:
        labels = [r["record"] for r in events]
        x = np.arange(len(labels))
        bas = [r["beta05"]["A3_hard_rate_basal"] for r in events]
        app = [r["beta05"]["A3_hard_rate_approach"] for r in events]
        w = 0.35
        axes[0].bar(x - w / 2, bas, w, label="basal", color="#3498db")
        axes[0].bar(x + w / 2, app, w, label="approach", color="#e74c3c")
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(labels)
        axes[0].set_ylabel("A₃ hard rate")
        axes[0].set_title("A₃ hard: basal vs approach")
        axes[0].legend(fontsize=8)
        axes[0].grid(True, axis="y", alpha=0.3)

        leads_a = [r["beta05"]["lead_A3_hard_h"] if np.isfinite(r["beta05"]["lead_A3_hard_h"]) else 0 for r in events]
        leads_e = [r["ews_excess3_lead_h"] if np.isfinite(r["ews_excess3_lead_h"]) else 0 for r in events]
        axes[1].bar(x - w / 2, leads_a, w, label="A₃ hard", color="#e67e22")
        axes[1].bar(x + w / 2, leads_e, w, label="excess³ abs-z", color="#8e44ad")
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(labels)
        axes[1].set_ylabel("Lead time (h)")
        axes[1].set_title("Lead time (0 = no alarm)")
        axes[1].legend(fontsize=8)
        axes[1].grid(True, axis="y", alpha=0.3)

        dts = [r["beta05"]["delta_T_holter"] for r in events]
        axes[2].bar(x, dts, color="#27ae60")
        axes[2].set_xticks(x)
        axes[2].set_xticklabels(labels)
        axes[2].set_ylabel("ΔT Holter (no Feigenbaum depth)")
        axes[2].set_title("Clock inflation Holter-path (β=0.5)")
        axes[2].axhline(0, color="k", lw=0.8)
        axes[2].grid(True, axis="y", alpha=0.3)
    fig.suptitle(
        "Holter: A₃ rates, lead, and diagnostic clock without Feigenbaum depth",
        fontsize=11,
        y=1.02,
    )
    fig.tight_layout()
    p2 = FIG / "fig_smoke_sddb_bars.png"
    fig.savefig(p2, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths.append(p2)

    # --- FAR bars ---
    if controls or events:
        fig, ax = plt.subplots(figsize=(8, 4))
        labs, vals, colors = [], [], []
        for r in events:
            labs.append(f"E{r['record']}")
            vals.append(r["far_A3_hard_per_24h"])
            colors.append("#e74c3c")
        for r in controls:
            labs.append(f"C{r['record']}")
            vals.append(r["far_A3_hard_per_24h"])
            colors.append("#3498db")
        ax.bar(labs, vals, color=colors)
        ax.set_ylabel("A₃ hard alarms / 24 h")
        ax.set_title(
            "Holter: FAR proxy — events (red) vs NSRDB controls (blue)"
        )
        ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout()
        p3 = FIG / "fig_smoke_far.png"
        fig.savefig(p3, dpi=140, bbox_inches="tight")
        plt.close(fig)
        paths.append(p3)

    return paths


def main():
    ap = argparse.ArgumentParser(description="P1 real-data smoke (SDDB + NSRDB)")
    ap.add_argument("--events", default=",".join(DEFAULT_EVENTS))
    ap.add_argument("--controls", default=",".join(DEFAULT_CONTROLS))
    ap.add_argument("--theta3", type=float, default=THETA3)
    ap.add_argument("--quick", action="store_true", help="Cap metric points per record (~2500)")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    if not CCTP_DATA.exists():
        raise SystemExit(f"CCTP data not found at {CCTP_DATA}")

    events = [e.strip() for e in args.events.split(",") if e.strip()]
    controls = [c.strip() for c in args.controls.split(",") if c.strip()]
    max_pts = 2500 if args.quick else None

    print("=" * 60)
    print("P1 real-data smoke — SDDB events + NSRDB controls")
    print(f"events={events} controls={controls} theta3={args.theta3} quick={args.quick}")
    print(f"A₃: d_min=2 (bivariate Holter), hardened v0.2 defaults")
    print("=" * 60)

    results: List[Dict] = []
    for rec in events:
        print(f"\n[event {rec}] loading…")
        meta = load_event(rec)
        print(f"  beats={len(meta['rr'])} event_hr={meta['event_hr']:.2f} basal={meta['basal']}")
        r = analyze_record(meta, theta3=args.theta3, max_points=max_pts)
        b5 = r["beta05"]
        d = r["diag"]
        print(
            f"  chaos={100*d['chaos_rate_all']:.0f}% sB={d['sB_rate']:.3f} sD={d['sD_rate']:.3f} "
            f"A3h bas/app={b5['A3_hard_rate_basal']:.3f}/{b5['A3_hard_rate_approach']:.3f} "
            f"Γ_app={b5['mean_Gamma3_approach']:.3f} "
            f"ΔT_leg={b5['delta_T']:+.3f} ΔT_h={b5['delta_T_holter']:+.0f} "
            f"lead_A3={b5['lead_A3_hard_h'] if np.isfinite(b5['lead_A3_hard_h']) else 'nan'} "
            f"lead_e3={r['ews_excess3_lead_h'] if np.isfinite(r['ews_excess3_lead_h']) else 'nan'}"
        )
        results.append(r)

    for rec in controls:
        print(f"\n[control {rec}] loading…")
        meta = load_control(rec)
        print(f"  beats={len(meta['rr'])} duration={meta['duration_h']:.2f}h")
        r = analyze_record(meta, theta3=args.theta3, max_points=max_pts)
        b5 = r["beta05"]
        print(
            f"  A3 hard rate={b5['A3_hard_rate']:.4f} FAR/24h={r['far_A3_hard_per_24h']:.2f} "
            f"meanΓ={b5['mean_Gamma3']:.3f} ΔT_h={b5['delta_T_holter']:+.0f}"
        )
        results.append(r)

    paths = write_outputs(results)
    print("\nWrote:", paths["csv"])
    print("Wrote:", paths["md"])
    print("Wrote:", paths["json"])

    if not args.no_plot:
        figs = make_figures(results)
        for p in figs:
            print("Wrote:", p)

    print("\nDone. See figures/results_smoke_real.md for interpretation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
