# Real-data smoke test — P1 on DengAI (v0.3+)

Generated: 2026-07-16T17:00:35.858519+00:00

**Protocol:** multivariate `[cases, temp, precip, RH]`, W=13, stride=1, θ₃=0.10, excess³ 0.6/0.4, P1 v0.2 hardened A₃ (`d_min=3`), β∈{0, 0.5}. Outbreaks: peaks ≥ P80, min sep 26w; segment 40w pre-peak; basal 13w; approach 12w.

## Outbreaks

| ID | City | Peak | Cases | chaos% | sB | sD | A₃h bas | A₃h app | Γ₃ app | ΔT legacy | Lead A₃h (w) | Lead e³ (w) |
|----|------|------|-------|--------|----|----|---------|---------|--------|-----------|--------------|-------------|
| SJ-O1-1994 | sj | 1994 | 461 | 100% | 0.146 | 0.000 | 0.000 | 0.000 | 1.112 | +0.000 | — | — |
| SJ-O2-1998 | sj | 1998 | 329 | 98% | 0.000 | 0.000 | 0.000 | 0.000 | 1.025 | +0.000 | — | — |
| SJ-O3-2007 | sj | 2007 | 170 | 100% | 0.244 | 0.146 | 0.071 | 0.231 | 1.396 | +0.000 | — | 4.0 |
| IQ-O1-2004 | iq | 2004 | 116 | 88% | 0.390 | 0.073 | 0.000 | 0.154 | 1.387 | +1.240 | 11.0 | 23.0 |
| IQ-O2-2008 | iq | 2008 | 58 | 100% | 0.390 | 0.268 | 0.000 | 0.615 | 2.381 | +0.000 | 25.0 | 26.0 |
| IQ-O3-2008 | iq | 2008 | 63 | 100% | 0.439 | 0.268 | 0.000 | 0.692 | 2.376 | +0.000 | 10.0 | 15.0 |

## Controls (inter-epidemic) — FAR / specificity proxy

| ID | City | Year | chaos% | A₃h rate | FAR /52w | mean Γ₃ | ΔT legacy | gain_mass |
|----|------|------|--------|----------|----------|---------|-----------|-----------|
| SJ-C1-2002 | sj | 2002 | 100% | 0.2439 | 2.60 | 1.562 | +0.001 | 42.35 |
| SJ-C2-2003 | sj | 2003 | 100% | 0.0976 | 2.60 | 1.299 | +0.000 | 24.55 |
| IQ-C1-2001 | iq | 2001 | 100% | 0.1034 | 1.30 | 1.344 | +0.000 | 17.33 |
| IQ-C2-2001 | iq | 2001 | 95% | 0.0000 | 0.00 | 1.121 | +0.000 | 9.93 |

## Ablation check

β=0 must give ΔT_legacy≈0. Observed max |ΔT| at β=0: **0.000000** (expect ~0).

## Aggregate (outbreaks)

- Sensitivity A₃ hard: **0.50** (3/6)
- Sensitivity excess³ abs-z (parallel): **0.67**
- Mean lead A₃ hard: **15.3 weeks**
- Mean lead excess³ abs-z: **17.0 weeks**
- Mean A₃ hard rate basal → approach: **0.012 → 0.282**
- Mean ΔT legacy (β=0.5): **+0.207**
- Mean chaos-band occupancy (|τ|<τ_ch) in segment: **97.6%**
- Mean fraction steps with |Δt_base|>ε: **7.3%**
- Mean ΔT legacy on controls: **+0.000** (compare to outbreaks)

## Aggregate (controls)

- Mean FAR (A₃ hard alarms / 52 w): **1.62**
- Mean Γ₃: **1.332** (1.0 = no Φ₃ gain)

## Honest reading (smoke, not Phase E)

See **manuscript §6.4** (*Smokes reales duales (Holter ↔ DengAI): contraste estratégico y limitaciones del reloj legacy*). Figure suptitles: `Strategic contrast (DengAI arm): … — Section 6.4`.

1. **Partial domain contrast:** chaos still high, but dt_base more active than Holter → legacy ΔT can move when C eases (e.g. IQ-2004).
2. **A₃ hardening:** basal→approach rises on Iquitos; extreme SJ case peaks may stay silent.
3. **Lead / FAR:** report raw numbers; do **not** claim operational EWS superiority.
4. **Ablation PASS:** β=0 → ΔT≈0.
