# Real-data smoke test — P1 on DengAI (v0.3+)

Generated: 2026-09-26T01:53:16.555082+00:00

**Protocol:** multivariate `[cases, temp, precip, RH]`, W=13, stride=1, θ₃=0.10, excess³ 0.6/0.4, P1 v0.2 hardened A₃ (`d_min=3`), β∈{0, 0.5}. Outbreaks: peaks ≥ P80, min sep 26w; segment 40w pre-peak; basal 13w; approach 12w.

## Outbreaks

| ID | City | Peak | Cases | chaos% | sB | sD | A₃h bas | A₃h app | Γ₃ app | ΔT legacy | Lead A₃h (w) | Lead e³ (w) |
|----|------|------|-------|--------|----|----|---------|---------|--------|-----------|--------------|-------------|
| SJ-O1-1994 | sj | 1994 | 461 | 100% | 0.098 | 0.000 | 0.000 | 0.000 | 1.015 | +0.000 | — | — |
| SJ-O2-1998 | sj | 1998 | 329 | 98% | 0.244 | 0.000 | 0.000 | 0.000 | 1.177 | +0.000 | — | — |
| SJ-O3-2007 | sj | 2007 | 170 | 100% | 0.488 | 0.415 | 0.000 | 0.615 | 1.586 | +0.000 | 16.0 | 22.0 |
| IQ-O1-2004 | iq | 2004 | 116 | 88% | 0.220 | 0.000 | 0.000 | 0.000 | 1.122 | +0.348 | — | 7.0 |
| IQ-O2-2008 | iq | 2008 | 58 | 100% | 0.439 | 0.341 | 0.071 | 0.692 | 2.964 | +0.000 | 7.0 | 23.0 |
| IQ-O3-2008 | iq | 2008 | 63 | 100% | 0.634 | 0.561 | 0.000 | 0.846 | 4.046 | +0.000 | 23.0 | 23.0 |

## Controls (inter-epidemic) — FAR / specificity proxy

| ID | City | Year | chaos% | A₃h rate | FAR /52w | mean Γ₃ | ΔT legacy | gain_mass |
|----|------|------|--------|----------|----------|---------|-----------|-----------|
| SJ-C1-2002 | sj | 2002 | 100% | 0.1463 | 1.30 | 1.347 | +0.000 | 26.21 |
| SJ-C2-2003 | sj | 2003 | 100% | 0.0488 | 1.30 | 1.198 | +0.000 | 16.22 |
| IQ-C1-2001 | iq | 2001 | 100% | 0.1034 | 1.30 | 1.377 | +0.000 | 19.50 |
| IQ-C2-2001 | iq | 2001 | 95% | 0.0000 | 0.00 | 1.122 | +0.000 | 10.01 |

## Ablation check

β=0 must give ΔT_legacy≈0. Observed max |ΔT| at β=0: **0.000000** (expect ~0).

## Aggregate (outbreaks)

- Sensitivity A₃ hard: **0.50** (3/6)
- Sensitivity excess³ abs-z (parallel): **0.67**
- Mean lead A₃ hard: **15.3 weeks**
- Mean lead excess³ abs-z: **18.8 weeks**
- Mean A₃ hard rate basal → approach: **0.012 → 0.359**
- Mean ΔT legacy (β=0.5): **+0.058**
- Mean chaos-band occupancy (|τ|<τ_ch) in segment: **97.6%**
- Mean fraction steps with |Δt_base|>ε: **7.3%**
- Mean ΔT legacy on controls: **+0.000** (compare to outbreaks)

## Aggregate (controls)

- Mean FAR (A₃ hard alarms / 52 w): **0.98**
- Mean Γ₃: **1.261** (1.0 = no Φ₃ gain)

## Honest reading (smoke, not Phase E)

See **manuscript §6.4** (*Smokes reales duales (Holter ↔ DengAI): contraste estratégico y limitaciones del reloj legacy*). Figure suptitles: `Strategic contrast (DengAI arm): … — Section 6.4`.

1. **Partial domain contrast:** chaos still high, but dt_base more active than Holter → legacy ΔT can move when C eases (e.g. IQ-2004).
2. **A₃ hardening:** basal→approach rises on Iquitos; extreme SJ case peaks may stay silent.
3. **Lead / FAR:** report raw numbers; do **not** claim operational EWS superiority.
4. **Ablation PASS:** β=0 → ΔT≈0.
