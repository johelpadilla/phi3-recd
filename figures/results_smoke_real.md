# Real-data smoke test — P1 on SDDB + NSRDB (v0.3)

Generated: 2026-07-16T17:01:26.187395+00:00

**Protocol:** bivariate proxy `[z(RR), z(|ΔRR|)]`, W=101, stride=5, θ₃=0.08, P1 defaults v0.2 (`β∈{0, 0.5}`, hardened A₃, `d_min=2` for Holter bivariate).

## Event Holters (SDDB)

| Rec | Δe₃ | chaos% | sB | sD | A₃h bas | A₃h app | Γ₃ app | ΔT legacy | ΔT Holter | Lead A₃h | Lead e³ abs-z |
|-----|-----|--------|----|----|---------|---------|--------|-----------|-----------|----------|---------------|
| 30 | -0.0052 | 100% | 0.009 | 0.000 | 0.000 | 0.000 | 1.012 | +0.001 | +89 | — | 3.07 |
| 31 | -0.0220 | 100% | 0.014 | 0.001 | 0.001 | 0.000 | 1.014 | +0.001 | +197 | — | 6.91 |
| 35 | +0.0044 | 100% | 0.047 | 0.004 | 0.004 | 0.003 | 1.054 | +0.000 | +625 | 4.96 | 7.96 |

## Controls (NSRDB) — FAR / specificity proxy

| Rec | h | chaos% | A₃h rate | FAR /24h | mean Γ₃ | ΔT Holter | gain_mass |
|-----|---|--------|----------|----------|---------|-----------|-----------|
| 16265 | 22.2 | 100% | 0.0141 | 21.58 | 1.118 | +1402 | 4712 |
| 16272 | 23.4 | 100% | 0.0188 | 25.59 | 1.134 | +1491 | 4705 |

## Ablation check

β=0 must give ΔT_legacy≈0 and ΔT_Holter≈0 (Γ₃≡1). Observed max |ΔT_legacy| at β=0:
**legacy 0.0000**, **Holter 0.0000** (expect ~0).

## Aggregate (events)

- Sensitivity A₃ hard: **0.33** (1/3)
- Sensitivity excess³ abs-z (parallel): **1.00**
- Mean lead A₃ hard: **4.96 h**
- Mean lead excess³ abs-z: **5.98 h**
- Mean A₃ hard rate basal → approach: **0.002 → 0.001**
- Mean ΔT Holter (β=0.5): **+304**
- Mean chaos-band occupancy (|τ|<τ_ch): **100.0%**
- Mean fraction of steps with |Δt_base|>ε (legacy): **0.10%**

## Aggregate (controls)

- Mean FAR (A₃ hard alarms / 24 h): **23.59**
- Mean Γ₃: **1.126** (1.0 = no Φ₃ gain)
- Mean ΔT Holter: **+1446** (compare to events)

## Honest reading (smoke, not Phase E)

See **manuscript §6.4** (*Smokes reales duales (Holter ↔ DengAI): contraste estratégico y limitaciones del reloj legacy*). Figure suptitles: `Strategic contrast (Holter arm): … — Section 6.4`.

1. **Hyperpersistence of band C, not of A₃:** `|τ_s| < τ_ch` almost always → (A) always on; A₃ hard stays sparse via (B)∩(D).
2. **Legacy ΔT ≈ 0:** Feigenbaum freezes Δt_base (~0.1% steps active). ΔT Holter (no depth) is diagnostic only.
3. **Sensitivity trade-off:** A₃ hard stricter than parallel e³ abs-z (lower hit rate).
4. **Specificity not won:** NSRDB FAR high; do not claim clinical FAR improvement.
5. **Ablation PASS:** β=0 → Γ≡1. `d_min=2` intentional (bivariate CCTP).
