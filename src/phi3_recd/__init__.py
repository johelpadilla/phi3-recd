"""
phi3-recd
=========

Optional coupling of Φ₃ (excess³) into RECD discrete-time updates.

This is a **clock map** layer, not a new ordinal metric. It assumes
excess³ / τ_s (or proxies) are already available from prior work
(e.g. ``nested-recd``, Systemic Tau pipelines).

Reference implementation for the preprint:

    Padilla-Villanueva, J. (2026). *Integrating Φ₃ (excess³) into RECD
    Dynamics: From Parallel Metric to Structural Clock Contribution*
    (draft v0.5).

Public API
----------
- ``ActivationConfig``, ``activation_A3`` — hardened Level-3 gate
- ``P1Config``, ``recd_p1`` — multiplicative gain Γ₃ (operational default)
- ``P2Config``, ``recd_p2`` — dual-channel map (experimental)
- ``recd_base`` — legacy RECD without Φ₃ (ablation baseline)
"""

from __future__ import annotations

__version__ = "0.5.0"

from .core import (
    ALPHA_SURP,
    ALPHA_SYN,
    DELTA_FEIGENBAUM,
    EPS,
    TAU_CH,
    TAU_ST,
    ActivationConfig,
    P1Config,
    P2Config,
    abs_delta_series,
    activation_A3,
    add_noise_to_series,
    base_interval,
    baseline_scale_stats,
    gate_piecewise,
    gen_s0_null,
    gen_s1_latent,
    gen_s2_coupled_logistic,
    logistic,
    normalize_vs_baseline,
    persistence_series,
    recd_base,
    recd_p1,
    recd_p2,
    residual_synergy_score,
    run_depth_series,
    softplus,
    summarize_run,
)

__all__ = [
    "__version__",
    "ALPHA_SURP",
    "ALPHA_SYN",
    "DELTA_FEIGENBAUM",
    "EPS",
    "TAU_CH",
    "TAU_ST",
    "ActivationConfig",
    "P1Config",
    "P2Config",
    "abs_delta_series",
    "activation_A3",
    "add_noise_to_series",
    "base_interval",
    "baseline_scale_stats",
    "gate_piecewise",
    "gen_s0_null",
    "gen_s1_latent",
    "gen_s2_coupled_logistic",
    "logistic",
    "normalize_vs_baseline",
    "persistence_series",
    "recd_base",
    "recd_p1",
    "recd_p2",
    "residual_synergy_score",
    "run_depth_series",
    "softplus",
    "summarize_run",
]
