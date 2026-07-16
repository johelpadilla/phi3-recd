# Synthetic validation results (v0.2, hardened A₃)

Defaults: `ActivationConfig` v0.2 (require_change, residual C, dual-scale, adaptive θ_e).

## S0–S2 summary

| Arm | T_base | T_P1 | T_P2 | A3 rate (soft>0.5) | A3 rate hard | mean Γ₃ | ρ₃ P2 | ρ₃_marg P1 | corr(Γ−1, f₃) | ΔT_P1 |
|-----|--------|------|------|--------------------|--------------|---------|-------|------------|---------------|-------|
| S0 | 365.62 | 369.82 | 368.72 | 0.003 | 0.000 | 1.015 | 0.016 | 0.011 | 0.020 | 4.21 |
| S1 | 180.02 | 181.86 | 181.33 | 0.230 | 0.200 | 1.893 | 0.201 | 0.207 | 0.988 | 1.85 |
| S2_prechaos | 250.41 | 251.73 | 252.76 | 0.000 | 0.000 | 1.026 | 0.064 | 0.020 | -0.013 | 1.32 |
| S2_chaos | 0.02 | 0.02 | 0.02 | 0.195 | 0.165 | 1.421 | 0.322 | 0.187 | 0.821 | 0.00 |

## Noise robustness (A3 rate soft>0.5)

| Arm | noise | A3_rate | mean Γ₃ | ΔT_P1 | corr(Γ−1,f₃) |
|-----|-------|---------|---------|-------|--------------|
| S1 | 0% | 0.263 | 2.002 | 3.62 | 0.984 |
| S1 | 5% | 0.237 | 1.984 | 2.18 | 0.982 |
| S1 | 10% | 0.240 | 1.853 | 2.44 | 0.979 |
| S1 | 15% | 0.223 | 1.753 | 1.89 | 0.978 |
| S2_chaos | 0% | 0.163 | 1.321 | 0.00 | 0.808 |
| S2_chaos | 5% | 0.158 | 1.323 | 0.00 | 0.812 |
| S2_chaos | 10% | 0.172 | 1.319 | 0.00 | 0.811 |
| S2_chaos | 15% | 0.182 | 1.364 | 0.00 | 0.809 |
| S0 | 0% | 0.000 | 1.010 | 2.44 | 0.060 |
| S0 | 5% | 0.000 | 1.009 | 1.96 | 0.086 |
| S0 | 10% | 0.003 | 1.009 | 1.57 | 0.065 |
| S0 | 15% | 0.003 | 1.011 | 2.52 | 0.064 |

## Interpretation checklist

- **S0:** A3 hard rate should be near 0; soft rate low; ΔT_P1 small.
- **S1:** A3 higher than S0; |Δẽ₃| drives activation despite surplus *drop*.
- **S2 chaos vs prechaos:** Γ₃, ρ₃, A3 higher in chaos.
- **Noise:** graceful degradation, not collapse of discrimination.
