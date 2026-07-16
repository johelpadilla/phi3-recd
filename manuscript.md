# Integrating Φ₃ (excess³) into RECD Dynamics: From Parallel Metric to Structural Clock Contribution

**Author:** Johel Padilla-Villanueva  
**Affiliation:** Department of Environmental Health, University of Puerto Rico — Medical Sciences Campus  
**ORCID:** 0000-0002-5797-6931  
**Contact:** joel.padilla2@upr.edu · johelpadilla@gmail.com  
**Date:** July 2026  
**Keywords:** Systemic Tau, RECD, excess³, ordinal synergy, early warning signals, Feigenbaum universality, nested conjunctions, complex systems

---

## Abstract

The Systemic Tau (\(\tau_s\)) framework and the Discrete Extramental Clock (RECD) identify critical transitions through ordinal relational reorganization rather than through growth in univariate magnitude. A three-level hierarchy of ordinal conjunctions—Φ₁ (coincidence), Φ₂ (persistent relation), and Φ₃ (irreducible synergistic surplus, operationalized by the continuous proxy excess³)—has been formalized and validated on synthetic systems. This work bridges the gap between the nested theoretical hierarchy and the legacy operational pipelines used in epidemiological and cardiac surveillance. In these pipelines, excess³ has typically remained a **parallel** diagnostic: it contributes to early-warning scores and nested mass fractions but does not systematically enter the discrete-time update.

We address it in two complementary ways. **Proposal 1** multiplies the *existing* RECD increment by a surplus-gated gain \(\Gamma_3\): the change is minimal, so that any modification of the clock can be attributed to Φ₃ by setting \(\beta=0\). **Proposal 2** rebuilds the advance as two additive channels and lets Φ₃ also deepen Feigenbaum compression: it is more expressive, but harder to audit in the field, and is therefore treated as experimental. Both proposals share the same hardened activation gate \(A_3\), because the main practical risk is not “too little Φ₃” but *trivial* activation whenever the system sits in the chaos band for long stretches (hyper-persistence).

The analysis proceeds as follows: (i) diagnose why parallel deployment of Φ₃ leaves the emergence hierarchy dynamically incomplete; (ii) define Proposal 1 and Proposal 2; (iii) specify activation rules that require surplus *change*, residual synergy, and dual-scale persistence; (iv) validate on synthetic suites S0–S2 with pre-specified metrics (\(A_3\) rates, \(T_{\mathrm{final}}\), \(\rho_3\), \(\mathrm{corr}(\Gamma_3-1,f_3)\), noise robustness); and (v) run **paired empirical analyses** on SDDB/NSRDB Holter recordings and DengAI San Juan/Iquitos series—two domains that share chronic band-C occupancy but differ in timescale and proxy structure. Interpreted jointly, the hardened \(A_3\) gate controls hyper-persistence in both domains; legacy \(\Delta T\) advances only when chaos-band occupancy permits movement of \(\Delta t^{\mathrm{base}}\); and event- and outbreak-level specificity under fixed thresholds remains to be demonstrated. Proposal 1 is the operational default; Proposal 2 is retained for synthetic structural comparison.

excess³ is retained throughout as a pre-specified hybrid proxy (0.6 Syn + 0.4 Surp) rather than as a complete partial-information decomposition. Causal claims are restricted to dynamical influence on the discrete clock index.

---

## 1. Structural incompleteness of parallel Level-3 deployment

### 1.1 Operational synthesis of the 2026 framework

The present analysis sits on the Systemic Tau / RECD framework developed in prior preprints [1, 5], with excess³ as the continuous Level-3 proxy [2]. Let \(X(t)\in\mathbb{R}^{d}\) denote a multivariate series with \(d\ge 2\). In successive windows of length \(W\), Systemic Tau is the mean pairwise Kendall rank correlation [8]:

\[
\tau_s(k)=\frac{2}{N(N-1)}\sum_{i<j}\tau_K\!\left(r_i^{(k)},r_j^{(k)}\right)\in[-1,1].
\]

Operational thresholds are motivated by the asymptotic variance of Kendall’s \(\tau\) under independence and by Feigenbaum universality [6, 7] (\(\delta\approx 4.6692016091\)):

| Regime | Condition | Operational interpretation |
|--------|-----------|----------------------------|
| **S** | \(\tau_s\ge +0.50\) | Strong ordinal coherence |
| **C** | \(\lvert\tau_s\rvert<0.41\) | Chaos band / elevated ordinal volatility |
| **A** | \(\tau_s\le -0.41\) | Strong antisynchronization |

Equation (1) and equation (2) answer different questions [1]. Equation (1) is the operational clock used in dengue, Holter, and RQA pipelines [3, 4, 13]: it advances \(t_k\) from \(\tau_s\), a gate, and a state factor. Equation (2) is the theoretical mass decomposition of the conjunction hierarchy across Φ₁–Φ₃ [1]. Nothing forces them to agree. In practice they often do not: \(f_3\) can be large in (2) while (1) never multiplies or adds a Φ₃ term. That mismatch—not a preference for one formalism—is the starting point of the present analysis.

| | **Legacy equation (1)** | **Nested equation (2)** |
|--|-------------------------|---------------------------|
| Role | Operational pipeline (epidemiology, RQA, cardiology) | Theoretical level-mass representation |
| Question it answers | How does discrete time advance in the field? | How is the increment partitioned across Φ₁–Φ₃? |
| Increment | \(\Delta t_k\cdot g(\tau_s)\cdot\alpha(\mathrm{state})\) | \(\sum_\ell\alpha_\ell(\lambda)\,\Phi_\ell^\ast\) |
| Role of Φ₃ | Absent from \(\Delta t_k\) (or present only as an adjunct) | As mass \(f_3\), with \(\lambda\) typically constructed from \(\tau_s\) alone |
| Integration path | **Modulation of (1) by Φ₃** via \(\Gamma_3\) or a dual channel | Compatible; \(f_3\) reported in parallel |

The classical RECD construction advances cumulative discrete time from a base interval \(\Delta t_k\), a gate \(g(\tau_s)\), and a state factor \(\alpha(\mathrm{state})\):

\[
t_{k+1}=t_k+\Delta t_k\cdot g(\tau_s(k))\cdot\alpha(\text{state}_k). \tag{1}
\]

In the nested theoretical formulation, the increment is a weighted sum of conjunctions:

\[
\Delta\mathrm{RECD}(t)=\alpha_1(\lambda)\,\Phi_1(t)+\alpha_2(\lambda)\,\Phi_2(t)+\alpha_3(\lambda)\,\Phi_3^\ast(t), \tag{2}
\]

where \(\Phi_3^\ast\) denotes the binary indicator Φ₃ or the continuous proxy excess³, and \(\lambda\) is a regime cue (for example, a transform of \(\lvert\tau_s\rvert\)).

Replacing equation (1) with equation (2) everywhere is not viable for applications: field pipelines, historical comparisons, and RQA couplings are already written against (1). A wholesale replacement would break continuity with published dengue and Holter series and would mix a change of *theory* with a change of *implementation*. Proposal 1 therefore **does not replace** equation (2): it defines a map \(F\) acting on equation (1) and conditioned on surplus evidence, so that the operational clock and nested mass fractions can be compared side by side. Equation (2) remains the diagnostic mass decomposition; equation (1) remains the deployed clock, now optionally Φ₃-aware.

excess³ is defined *a priori* as

\[
\mathrm{excess}^3(t)=0.6\cdot\mathrm{Syn}(t)+0.4\cdot\mathrm{Surp}(t), \tag{3}
\]

where Syn denotes the multiinformation residual relative to a pairwise baseline and Surp denotes the log-ratio surprise under independence of ordinal symbols (Bandt–Pompe permutation entropy [9]). The hybrid weights 0.6/0.4 and the continuous proxy construction follow the pre-specified excess³ protocol [2]; they are not a complete partial-information decomposition in the sense of Williams and Beer [12]. The weights are fixed and are not re-estimated on the target dataset.

### 1.2 Parallel versus dynamical deployment of Φ₃

Three distinct roles of Level 3 appear in the 2026 framework [1, 2]:

1. **Parallel early-warning statistic.** \(\Delta\mathrm{excess}^3\) between a baseline window and an approach window (for example, pre-ventricular-fibrillation intervals in SDDB [4, 14]; synthetic G0–G3 contrasts), in the broader early-warning tradition of critical-transition indicators [10].
2. **Mass / increment fraction** in equation (2): \(f_3=\alpha_3\Phi_3^\ast/\sum_\ell\alpha_\ell\Phi_\ell^\ast\).
3. **Structural contribution to the operational interval** \(\Delta t_k\) in equation (1) and to hyper-persistence pipelines (RQA, six-mode consensus) [3, 13].

Roles (1) and (2) are comparatively well developed. Role (3) remains **without a single, unified specification**:

- In epidemiological surveillance and RQA refinement, the clock and associated signals are constructed from \(\tau_s\), persistence \(P(k)\), \(g(\tau_s)\), LAM/TT/DET, and states C/D/T. excess³ enters as an additional mode or adjunct metric, not as a canonical modulator of \(\Delta t_k\).
- In equation (2), \(\alpha_3(\lambda)\) elevates Level-3 mass when \(\lambda\) indicates chaos, yet \(\lambda\) is typically constructed from \(\tau_s\) (or from a known control parameter \(r\)). Consequently, the weight of Φ₃ depends on the \(\tau_s\) regime rather than on the **observed irreducibility** of excess³ within that window. A system may occupy band C with low excess³ (pair-dominated chaos) or with high excess³ (chaos carrying order-\(\ge 3\) surplus). These regimes warrant distinct clocks if the conjunction hierarchy is to govern the discrete-time construction.
- Without a Φ₃ → clock channel, the hierarchy Φ₁ ⊂ Φ₂ ⊂ Φ₃ remains descriptive in terms of mass and predictive as an early-warning signal, but is not generative of the discrete time index used in operational pipelines.

### 1.3 Dynamical closure of the hierarchy

**Definition (dynamical closure).** The conjunction hierarchy is dynamically closed if there exists a family of implementable maps \(F\) such that

\[
\Delta t_k = F\bigl(\Delta t_k^{\mathrm{base}},\,g(\tau_s),\,\alpha(\mathrm{state}),\,\Phi_1,\Phi_2,\mathrm{excess}^3;\,\theta\bigr)
\]

with pre-specified parameters \(\theta\), and if there exist falsifiable predictions on \(T_{\mathrm{RECD}}\), lead times, and mass fractions that fail when the Φ₃ channel is ablated (\(F\) independent of excess³).

Incorporation of Φ₃ into \(F\) is required so that:

1. **Ordinal depth and the clock remain distinguishable.** Without Φ₃ in \(F\), two trajectories sharing \(\tau_s(k)\) and \(P(k)\) yield identical clocks even when their order-3 surplus differs.
2. **Marginal contribution is testable.** Comparison of RECD with and without the Φ₃ channel constitutes a controlled ablation experiment.
3. **Nested theory (2) and pipeline (1) are aligned.** The two coexisting formalisms are thereby unified without reformulating the RECD construction from its foundations.

This requirement does not imply that excess³ constitutes a complete partial-information atom, nor that the discrete clock represents physical time. It requires only that the index \(t_k\) respond to the structural layer that the framework treats as deepest.

### 1.4 Design constraints inherited from the framework

Any admissible construction must:

- preserve the thresholds \(\tau_{\mathrm{ch}}=0.41\), \(\tau_{\mathrm{st}}=0.50\), and the constant \(\delta\);
- leave the 0.6/0.4 excess³ weights unaltered on target data;
- remain computable for short windows (\(W\sim 13\)) and moderate dimension \(d\);
- admit phase-shuffle nulls that destroy cross-dependence while preserving marginal spectra;
- avoid trivial activation of Φ₃ throughout band C (tropical hyper-persistence: 69–87% of time in the hyper-persistent core);
- remain compatible with RQA as a signal refinement rather than as a substitute for the clock.

### 1.5 Two proposals rather than one

A single map from Φ₃ into \(t_k\) is not uniquely determined by the framework. Two design pressures pull in opposite directions:

1. **Minimal change and auditability.** Surveillance pipelines require a drop-in factor on the clock already in use, with a one-parameter off-switch (\(\beta=0\)) that recovers baseline behaviour exactly. That pressure yields **Proposal 1**: multiply the existing increment by \(\Gamma_3\ge 1\).
2. **Structural fidelity to nested mass.** The hierarchy claims that Level 3 is not merely “more of Level 2”: it can change *how deep* renormalization goes, not only *how large* the step is. That pressure yields **Proposal 2**: a separate surplus channel with its own Feigenbaum depth \(R_3\), and an optional jump term.

Proposal 1 is the candidate for deployment: conservative, ablatable, and computationally cheap. Proposal 2 is the candidate for *structural* comparison with equation (2), testing whether a dual-channel geometry aligns better with nested \(f_3\) on controlled synthetic systems. If Proposal 1 fails to help under real hyper-persistence, there is no operational case for the more aggressive Proposal 2. If Proposal 1 helps but still under-represents Level-3 geometry, Proposal 2 is the natural next experiment rather than a first field change. Sections 3–4 formalize both constructions; Section 5 freezes the shared activation logic; Section 8 states the operational priority.

---

## 2. Shared base notation

The **legacy base increment** (without Level 3) is defined by

\[
\Delta t_k^{\mathrm{base}}
=
\begin{cases}
\delta^{-k_{\mathrm{run}}}\cdot\lvert\tau_s(k)\rvert\cdot\Delta t_0
  & \text{if }\lvert\tau_s(k)\rvert<\tau_{\mathrm{ch}},\\[4pt]
\Delta t_{\mathrm{out}}
  & \text{otherwise (unit or null advance, pipeline-dependent),}
\end{cases}
\tag{4}
\]

where \(k_{\mathrm{run}}\) is the depth of the current chaotic run (or a bounded local renormalization counter). The gate \(g\) may be piecewise or sigmoidal; the generic form \(g(\tau_s)\in[-1,1]\) is retained.

**Normalization of excess³** (for numerical stability across datasets):

\[
\widetilde{e}_3(k)
=
\frac{\mathrm{excess}^3(k)-\mu_{e,B}}{\sigma_{e,B}+\varepsilon},
\tag{5}
\]

with \((\mu_{e,B},\sigma_{e,B})\) estimated **exclusively** on a baseline window \(B\) fixed *a priori* (or on a calibration set that does not overlap the evaluation event). \(\varepsilon>0\) is a small stabilizer. A rank-based alternative (more robust under heavy tails) is

\[
\widetilde{e}_3^{\mathrm{rk}}(k)
=
2\cdot\widehat{F}_B\!\bigl(\mathrm{excess}^3(k)\bigr)-1\in[-1,1],
\tag{5'}
\]

where \(\widehat{F}_B\) denotes the empirical cumulative distribution function on \(B\).

**Ordinal persistence** (as in the RQA / hyper-persistence literature):

\[
P(k)=\text{length of the current run with }\lvert\tau_s\rvert<\tau_{\mathrm{ch}}.
\tag{6}
\]

**Nested Level-3 mass** (diagnostic; not the sole integration path):

\[
f_3(k)
=
\frac{\alpha_3(\lambda)\,\Phi_3^\ast(k)}
{\sum_{\ell=1}^{3}\alpha_\ell(\lambda)\,\Phi_\ell^\ast(k)+\varepsilon}.
\tag{7}
\]

---

## 3. Proposal 1 (conservative): multiplicative surplus gain

Under Proposal 1, the base advance remains determined by \(\tau_s\), the gate \(g\), and the state factor, as in the legacy pipeline. Φ₃ enters only as a secondary scale factor on that already-decided increment: when irreducible surplus is absent or stagnant, \(\Gamma_3=1\) and the clock is unchanged; when surplus is present and changing, \(\Gamma_3>1\) and the same base step is stretched. Setting \(\beta=0\) is therefore an exact ablation: it removes the surplus factor without altering the primary clock.

### 3.1 Formulation

Equations (1) and (4) are left structurally unchanged. Φ₃ enters solely as a **gain factor** \(\Gamma_3\ge 1\) (or \(\ge 0\) if a braking regime is admitted) applied to the increment already filtered by \(g\) and by the state factor:

\[
\boxed{
t_{k+1}
=
t_k
+
\Delta t_k^{\mathrm{base}}
\cdot
g\bigl(\tau_s(k)\bigr)
\cdot
\alpha(\mathrm{state}_k)
\cdot
\Gamma_3(k)
}
\tag{P1}
\]

### 3.2 Definition of \(\Gamma_3\)

Let \(A_3(k)\in\{0,1\}\) denote the Level-3 **activation gate** (Section 5). Define

\[
\Gamma_3(k)
=
1
+
\beta\cdot A_3(k)\cdot\psi\!\bigl(\widetilde{e}_3(k)\bigr),
\tag{8}
\]

where \(\beta\ge 0\) is a sensitivity hyperparameter (default range \(\beta\in[0.25,1.0]\), fixed *a priori*) and \(\psi\) is a monotone bounded map, for example

\[
\psi(x)=\mathrm{softplus}(x)=\log\bigl(1+e^{x}\bigr),
\quad\text{or}\quad
\psi(x)=\max(0,x).
\tag{9}
\]

**Argument of \(\psi\):**

| Mode | Argument of \(\psi\) | Intended regime |
|------|----------------------|-----------------|
| `level` (default) | \(\lvert\widetilde{e}_3\rvert\) if absolute form; signed softplus otherwise | Elevated surplus magnitude |
| `change` | \(\lvert\Delta\widetilde{e}_3\rvert\) (or signed first difference) | Reorganization with a **decrease** in surplus (G1) |
| `both` | mean of level and change arguments | Compromise under mixed dynamics |

The **absolute-delta** form adopted as default (consistent with G1, in which surplus may decrease) is

\[
\Gamma_3^{\mathrm{abs}}(k)
=
1
+
\beta\cdot A_3(k)\cdot\psi\!\bigl(\lvert\Delta\widetilde{e}_3(k)\rvert\bigr)
\quad\text{or}\quad
\psi\!\bigl(\lvert\widetilde{e}_3(k)-\widetilde{e}_3^{\mathrm{ref}}\rvert\bigr),
\tag{8'}
\]

where \(\widetilde{e}_3^{\mathrm{ref}}\) is the baseline median. Absolute-delta privileges **change** in surplus over chronic level: in hyper-persistent stretches, excess³ can remain elevated without marking a transition, whereas reorganization—including some G1 paths—often appears as a *movement* of surplus (sometimes a drop). The implementation exposes the absolute-delta switch and \(\texttt{psi\_mode}\in\{\texttt{level},\texttt{change},\texttt{both}\}\) so that sensitivity to this choice remains transparent.

### 3.3 Modulation of the Φ₃ weight

| Quantity | Role |
|----------|------|
| \(\mathrm{excess}^3(k)\) | Continuous proxy for Φ₃ (equation 3) |
| \(\widetilde{e}_3(k)\) or \(\lvert\Delta\widetilde{e}_3\rvert\) | Dimensionless scale |
| \(A_3(k)\) | Suppresses trivial activation under hyper-persistence |
| \(\beta\) | Global channel intensity (single pre-specified scalar) |
| \(\alpha_3(\lambda)\) (optional) | May enter \(A_3\) or a compound weight \(\beta_{\mathrm{eff}}=\beta\cdot\alpha_3(\lambda)/\alpha_{3,0}\) |

**Compatibility with equation (2).** Proposal 1 does not replace nested RECD; it defines a map \(F\) on the legacy pipeline. Optionally, one may report in parallel

\[
\Delta\mathrm{RECD}^{\mathrm{nested}}(k)
=
\sum_{\ell=1}^{3}\alpha_\ell(\lambda)\,\Phi_\ell^\ast(k)
\]

and require positive correlation between \(\Gamma_3(k)-1\) and \(f_3(k)\) in synthetic chaotic regimes.

**Marginal contribution of Φ₃ to the clock** (generalization of \(\rho_3\) from Proposal 2 to Proposal 1):

\[
\rho_3^{\mathrm{marg}}(k)
=
\frac{\lvert\Delta t_k^{(P1)}-\Delta t_k^{\mathrm{base}}\rvert}
{\lvert\Delta t_k^{(P1)}\rvert+\varepsilon}
=
\frac{\lvert\Gamma_3(k)-1\rvert\cdot\lvert\Delta t_k^{\mathrm{base}}\,g\,\alpha\rvert}
{\lvert\Delta t_k^{(P1)}\rvert+\varepsilon}.
\tag{8''}
\]

This quantity supports ablation and direct comparison with \(\rho_3\) under Proposal 2.

### 3.4 Predicted dynamical consequences

1. **Selective acceleration.** In regime C with \(A_3=1\) and elevated surplus (or large \(\lvert\Delta e_3\rvert\)), \(t_k\) advances more rapidly than base RECD at equal \(\tau_s\).
2. **Absence of discontinuous jumps** when \(\psi\) and \(\widetilde{e}_3\) are smooth: the clock remains piecewise absolutely continuous (only the local slope changes).
3. **Improved pre-critical discrimination.** In cardiac series, if \(\Delta\mathrm{excess}^3\) precedes \(\tau_s\), \(\Gamma_3\) may advance critical-mass accumulation and improve lead time on \(T_{\mathrm{RECD}}\).
4. **Exact ablation.** Setting \(\beta=0\) or \(A_3\equiv 0\) recovers the legacy RECD exactly.

### 3.5 Implementation (pseudocode)

```text
for k in time:
    tau = systemic_tau(window_k)
    e3  = excess3(window_k)          # fixed 0.6/0.4
    e3n = normalize_vs_baseline(e3)
    dt  = base_interval(tau, run_depth)
    g   = gate(tau)
    a   = state_factor(state_k)      # C/D/T
    A3  = activation_level3(...)     # Section 5
    Gamma = 1 + beta * A3 * softplus(e3n)   # or abs-delta form
    t[k+1] = t[k] + dt * g * a * Gamma
```

Computational cost is of the same order as excess³ evaluation per window and is already incurred whenever excess³ is computed for early warning.

---

## 4. Proposal 2 (experimental): dual channel with depth-dependent compression

Proposal 1 only *scales* a step already fixed by \(\tau_s\). Proposal 2 allows Φ₃ to contribute an additive component of the step and to change the renormalization depth of that component. Channel \(C_{12}\) is the pair-relational advance of the standard construction; channel \(C_3\) is discrete time attributable to irreducible surplus, compressed more aggressively the longer surplus remains active. That geometry is closer in spirit to nested equation (2), but it is also easier to overfit and harder to reverse-engineer in operational code. Hence the experimental status: evaluate on synthetic systems first; do not deploy until Proposal 1 has shown domain benefit.

### 4.1 Formulation

Clock advance is decomposed into **two additive channels**:

- **Pair-relational channel** \(C_{12}\): governed by \(\tau_s\), \(P\), Φ₁, and Φ₂ (as in the standard construction).
- **Surplus channel** \(C_3\): governed by excess³ and active only under the strict criteria of Section 5.

When channel 3 is active, the effective **renormalization depth** increases (stronger Feigenbaum compression), and optional bounded **structural jumps** may be admitted.

\[
\boxed{
\begin{aligned}
\Delta t_k^{(12)}
&=
\delta^{-k_{12}}\cdot h_{12}\!\bigl(\tau_s(k),\Phi_1(k),\Phi_2(k)\bigr)
\cdot g\bigl(\tau_s(k)\bigr)
\cdot\alpha(\mathrm{state}_k),\\[6pt]
\Delta t_k^{(3)}
&=
A_3(k)\cdot
\delta^{-(k_{12}+\kappa\cdot R_3(k))}\cdot
h_3\!\bigl(\widetilde{e}_3(k),f_3(k)\bigr),\\[6pt]
t_{k+1}
&=
t_k
+
\Delta t_k^{(12)}
+
\Delta t_k^{(3)}
+
A_3(k)\cdot J\cdot\mathbf{1}\{\text{jump condition}\}.
\end{aligned}
}
\tag{P2}
\]

### 4.2 Components

**Surplus depth** (bounded accumulator, not a free exponent):

\[
R_3(k+1)
=
\min\!\Bigl(
R_{\max},\;
\bigl(R_3(k)+1\bigr)\cdot A_3(k)
\Bigr),
\quad
R_3\leftarrow 0\text{ if }A_3=0.
\tag{10}
\]

Thus sustained runs of active Level 3 deepen the compression \(\delta^{-(\cdot)}\) analogously to \(k_{\mathrm{run}}\) on channel 12, but **only** when surplus is non-trivial.

**Amplitude of channel 3:**

\[
h_3(\widetilde{e}_3,f_3)
=
\eta\cdot\psi\!\bigl(\lvert\widetilde{e}_3\rvert\bigr)\cdot\bigl(1+\gamma_f f_3\bigr),
\tag{11}
\]

with \(\eta>0\), \(\gamma_f\ge 0\) pre-specified; default \(\gamma_f=0\) if \(f_3\) is unused.

**Structural jump (optional; initially disabled):**

\[
\text{jump condition}
\iff
A_3(k)=1
\;\wedge\;
\widetilde{e}_3(k)>\theta_{\mathrm{jump}}
\;\wedge\;
\Delta\widetilde{e}_3(k)>\theta_{\Delta}
\;\wedge\;
P(k)\ge P_{\min}.
\tag{12}
\]

\(J\ge 0\) is a fixed jump size or \(J=j_0\cdot\psi(\widetilde{e}_3)\). Under a smoothness constraint, \(J=0\).

### 4.3 Modulation of the Φ₃ weight

Under Proposal 2 the weight of Φ₃ is not a single scalar \(\beta\); it enters through

1. the gate \(A_3\) (binary or soft in \([0,1]\));
2. the magnitude \(h_3\);
3. the depth \(R_3\) (nonlinear effect via \(\delta^{-R_3}\));
4. optionally the nested mass \(f_3\).

Level 3 may therefore dominate the **mathematical regime** of the clock (irregularity, scale jumps), not only its local slope.

### 4.4 Predicted dynamical consequences

1. **Temporal bimodality.** Intervals governed solely by \(C_{12}\) (pair-dominated chaos) versus intervals governed by \(C_{12}+C_3\) (chaos with surplus), with distinct speed and roughness of \(T_{\mathrm{RECD}}\).
2. **Additional hierarchical compression** on runs of active Φ₃: shorter intervals as \(R_3\) grows (up to \(R_{\max}\)).
3. **Jumps** (if \(J>0\)): discrete clock events aligned with surplus transitions—candidates for Level-3 ticks in early-warning applications.
4. **Increased robustness to unstructured hyper-persistence.** If \(A_3=0\) during a long hyper-persistent core with stagnant excess³, the clock does not accumulate spurious Φ₃ contribution; if excess³ reorganizes within the core, \(C_3\) activates (a natural complement to RQA).

### 4.5 Relation to the nested equation (2)

Proposal 2 may be interpreted as a **nonlinear realization** of equation (2):

- \(C_{12}\) corresponds to the terms \(\alpha_1\Phi_1+\alpha_2\Phi_2\) after gating and Feigenbaum compression;
- \(C_3\) corresponds to the term \(\alpha_3\Phi_3^\ast\) with an independent renormalization schedule.

**Consistency prediction.** On coupled logistic maps (pre-chaos versus chaos), the fraction

\[
\rho_3
=
\frac{\sum_k\lvert\Delta t_k^{(3)}\rvert}
{\sum_k\bigl(\lvert\Delta t_k^{(12)}\rvert+\lvert\Delta t_k^{(3)}\rvert\bigr)}
\]

is expected to rise in chaos analogously to \(f_3\) in the 2026 framework (on the order of \(+0.25\) absolute under the reference protocol, subject to re-estimation).

---

## 5. Hardened Level-3 activation criteria

**Objective.** Φ₃ influences the clock **only** when non-trivial surplus is present **and** the regime context is compatible.

In tropical dengue series and in many Holter recordings, the system spends a large fraction of time in band C (hyper-persistence). If \(A_3\) fired whenever \(\lvert\tau_s\rvert<\tau_{\mathrm{ch}}\), then \(\Gamma_3>1\) almost continuously: the gain would stop carrying information about *transitions* and would become a permanent rescaling of the clock. Synthetic checks confirm the risk: a permissive gate can activate on more than half of a null series (Section 6.3). Hardened activation is therefore required to keep Φ₃ from collapsing into a synonym of band C.

The criteria below implement four requirements: (A) chaotic or approach context; (B) surplus that is high *and moving*; (C) surplus not reducible to pairwise coincidence; (D) confirmation at two timescales so that a single noisy spike cannot open the channel.

### 5.1 Primary gate \(A_3(k)\)

Set \(A_3(k)=1\) if and only if **all** of the following conditions hold (strict version; the soft version combines scores in \([0,1]\)):

**(A) Chaotic or approach regime**

\[
\lvert\tau_s(k)\rvert<\tau_{\mathrm{ch}}
\quad\text{or}\quad
P(k)\ge P_{\mathrm{arm}}
\quad\text{or}\quad
\mathrm{state}_k\in\{\mathrm{C},\mathrm{T}\}.
\tag{A}
\]

\(P_{\mathrm{arm}}\) (default 3) is smaller than the hyper-persistent core threshold (\(P\ge 7\)).

**(B) Surplus level and (B′) change (both required by default)**

\[
\lvert\widetilde{e}_3(k)\rvert>\theta_e^{\mathrm{eff}}
\quad\text{and}\quad
\lvert\Delta\widetilde{e}_3(k)\rvert>\theta_{\Delta}.
\tag{B+B'}
\]

The **change** condition is essential: in synthetic G1, surplus may **decrease** under a shared latent factor; a level-only gate would fail or activate in the wrong regime. Defaults: \(\theta_e=1.25\) (z-score units), \(\theta_{\Delta}=0.40\); change is required.

**Adaptive threshold** (noisy series):

\[
\theta_e^{\mathrm{eff}}
=
\theta_e\cdot\bigl(1+\kappa\cdot\min(\mathrm{CV}_B,2)\bigr),
\tag{B_{\mathrm{adapt}}}
\]

with \(\mathrm{CV}_B=\sigma_B/(\lvert\mu_B\rvert+\varepsilon)\) estimated **only** on baseline and \(\kappa=0.5\) by default. This construction reduces false positives when baseline excess³ is highly variable.

**(C) Residual synergy fraction**

Rather than the bare ratio \(\mathrm{excess}^3/(\Phi_1+\Phi_2)\), an **approximate residual fraction** of Level-3 mass is used:

\[
r_{\mathrm{syn}}(k)
=
\frac{s_B(k)}{s_B(k)+\Phi_1(k)+\Phi_2(k)+\varepsilon}
\in(0,1),
\qquad
r_{\mathrm{syn}}(k)>\theta_{\mathrm{res}},
\tag{C}
\]

where \(s_B=\lvert\widetilde{e}_3\rvert\) (or signed softplus). Default \(\theta_{\mathrm{res}}=0.20\). If Φ₁ and Φ₂ are unavailable, the proxy \(\Phi_1+\Phi_2\equiv 1\) may be substituted (same functional form; recalibratable). Optionally, \(f_3>\theta_f\) may also be required.

**(D) Dual scale: short detection and medium persistence**

\[
\begin{aligned}
\#\{j\in[k-L_s+1,k]:\text{(B) and (C)}\}&\ge L_{s,\min},\\
\#\{j\in[k-L_m+1,k]:\text{(A),(B),(C)}\}&\ge L_{m,\min}.
\end{aligned}
\tag{D}
\]

Defaults: \(L_s=3\), \(L_{s,\min}=2\) (detection); \(L_m=7\), \(L_{m,\min}=4\) (surplus persistence). Neither a single spike nor a brief noisy excursion is sufficient.

**(E) Optional — RQA consensus under hyper-persistence**

On datasets with a hyper-persistent core (SJU-3, DengAI San Juan):

\[
A_3^{\mathrm{RQA}}(k)
=
A_3(k)\cdot\mathbf{1}\{\mathrm{LAM}_{\mathrm{core}}(k)>\lambda_{\mathrm{LAM}}
\;\vee\;
\Delta\mathrm{TT}(k)>\theta_{\mathrm{TT}}\}.
\tag{E}
\]

### 5.2 Soft gate (operational default for Proposal 1)

\[
A_3^{\mathrm{soft}}(k)
=
\sigma\!\bigl(c_A+c_B+c_C+c_D-s_0\bigr)\in(0,1),
\tag{13}
\]

where \(c_B\) is the **product** of level and change scores, \(c_C\) is a logistic transform of \(r_{\mathrm{syn}}\), \(c_D\) averages the two temporal scales, and \(s_0=3.25\) (logistic offset). Soft values below \(0.25\) are set to zero to suppress residual activation under the null.

### 5.3 Exclusion rules

Φ₃ must **not** activate under any of the following conditions:

- occupancy of the entire C regime solely because \(\lvert\tau_s\rvert<0.41\);
- a single excess³ spike without dual-scale confirmation (D);
- elevated excess³ level **without** change (low \(\lvert\Delta\widetilde{e}_3\rvert\))—characteristic of “flat” hyper-persistence;
- pure pairwise coincidence: low \(r_{\mathrm{syn}}\) even when \(\lvert\tau_s\rvert\) lies in the chaos band;
- windows with \(d=2\): channel 3 is disabled and the disability is reported;
- threshold calibration on the same event used for evaluation (data leakage).

---

## 6. Validation design and results

### 6.1 Principles

1. **Ablation first.** Proposal 1 or Proposal 2 is compared with base RECD (\(\beta=0\) / \(A_3\equiv 0\)).
2. **Phase-shuffle nulls** are applied to the primary statistic \(\lvert\Delta T\rvert\) or lead time, not solely to isolated excess³.
3. **Pre-registration of hyperparameters** (\(\beta,\theta_e,L_{\min},\ldots\)) precedes inspection of outbreak or ventricular-fibrillation labels.
4. **Detection improvement** (lead, precision, false-alarm rate) is reported separately from **change in clock geometry** (fractal dimension of \(T\), roughness, \(\rho_3\)).

### 6.2 Synthetic validation design

Synthetic arms exist to answer questions that real data cannot isolate cleanly. S0 asks: *does the gate stay quiet when there is no true surplus structure?* S1 asks: *when reorganization is known, does the gain track nested mass even if surplus falls?* S2 asks: *does chaos elevate Φ₃ contribution relative to pre-chaos?* S3–S4 tighten specificity against pairwise-only coupling and flat hyper-persistence.

| Arm | Design | Primary prediction | Human question |
|-----|--------|--------------------|----------------|
| **S0** | Independent channels / G0-like | Hard \(A_3\approx 0\); low soft rate; non-spurious \(\Delta T_{P1}\) | Does the null stay null? |
| **S1** | Latent factor + reorganization (G1; surplus may decrease) | \(\lvert\Delta e_3\rvert\) drives \(A_3\); high \(\mathrm{corr}(\Gamma_3-1,f_3)\) | Does change-based activation catch true reorg? |
| **S2** | Pre-chaos versus chaos | \(\mathbb{E}[\Gamma_3]\), \(\rho_3\), and \(A_3\) elevated in chaos | Is Level 3 selective for chaos? |
| **S3** | Pairwise coupling only (G3) | Intermediate activation; must not exceed S1 | Pairs alone must not look like Φ₃ |
| **S4** | Flat hyper-persistence versus reorganization | Discrimination via (B′) and (D); (E) reduces false alarms | Flat chaos ≠ reorganizing chaos |

**Metrics.** \(A_3\) rate (soft \(>0.5\) and hard); \(T_{\mathrm{final}}\) under base / P1 / P2; mean \(\Gamma_3\); \(\rho_3\) (P2) and \(\rho_3^{\mathrm{marg}}\) (P1); \(\mathrm{corr}(\Gamma_3-1,f_3)\); noise robustness at 5–15%. Soft \(A_3\) is the operational continuous score used inside \(\Gamma_3\); hard \(A_3\) is the binary gate used for lead/FAR tables—two views of the same criteria, not two competing theories.

### 6.3 Synthetic results

Synthetic runs employ the shared activation defaults listed in Appendix A.

| Arm | A₃ soft>0.5 | A₃ hard | mean \(\Gamma_3\) | \(\rho_3\) P2 | \(\rho_3^{\mathrm{marg}}\) P1 | corr(\(\Gamma-1,f_3\)) | \(\Delta T_{P1}\) |
|-----|-------------|---------|-------------------|---------------|-------------------------------|------------------------|------------------|
| **S0** | **0.003** | **0.000** | **1.015** | 0.016 | 0.01 | 0.02 | **+4.2** |
| **S1** | 0.230 | 0.200 | 1.893 | 0.201 | 0.18 | **0.988** | +1.9 |
| **S2 prechaos** | 0.000 | 0.000 | 1.026 | 0.064 | 0.02 | −0.01 | +1.3 |
| **S2 chaos** | 0.195 | 0.165 | **1.421** | **0.322** | 0.21 | **0.821** | ~0† |

†In chaos, \(\Delta t^{\mathrm{base}}\) is already Feigenbaum-compressed: absolute \(\Delta T\) is small; \(\rho_3\) and \(\Gamma_3\) capture the Φ₃ contribution.  
Full numerical tables and \(T_{\mathrm{final}}\) series use seed base \(=10\).

**Interpretation.**

1. **S0 (null).** Hard \(A_3=0\), soft rate \(\approx 0.3\%\), mean \(\Gamma_3\approx 1.02\), \(\Delta T_{P1}\approx +4\) (\(\sim 1\%\) of the base clock). The hardened gate respects the null. A more permissive configuration (without surplus-change or residual-synergy requirements) raised mean \(A_3\) to \(\sim 0.55\) on the same series, which motivates the present hardening.
2. **S1 (latent / change).** Selective activation (\(\sim 20\)–\(23\%\)) and near-unit correlation between \(\Gamma_3-1\) and \(f_3\). The Φ₃ channel aligns with nested mass under true reorganization, including a **decrease** in surplus.
3. **S2.** The chaotic regime elevates \(\Gamma_3\) (1.42 versus 1.03) and \(\rho_3\) (0.32 versus 0.06). Pre-chaos does not activate \(A_3\).
4. **Noise (5–15%).** Gradual degradation without collapse of the ordering S0 ≪ S1 / S2-chaos (Figure, noise-robustness panel).

**Pre-specified acceptance criteria.**

| Criterion | Observed result |
|-----------|-----------------|
| S0 hard \(A_3\lesssim 8\%\) | Met (0.000) |
| S0 mean \(\Gamma_3\) near 1 | Met (1.015) |
| S2 chaos \(\mathbb{E}[\Gamma_3]\) > pre-chaos | Met (1.421 > 1.026) |

On a contrast series with a surplus *burst* superimposed on a chaotic core, the rate \(A_3>0.5\) reaches \(\approx 0.95\) inside the burst and falls to \(\approx 0.25\) on the burst-free core (versus \(\approx 0.72\) under a globally permissive gate). The hardened gate therefore discriminates local reorganization from flat chaos.

### 6.4 Paired empirical analyses (Holter and DengAI): limits of the legacy clock

The empirical design is *paired*: the same Proposal 1 core and \(\beta\) run on Holter recordings from the PhysioNet Sudden Cardiac Death Holter Database (SDDB) and Normal Sinus Rhythm Database (NSRDB) [4, 14] (seconds-to-hours, RR, pre-VF) and on DengAI San Juan/Iquitos weekly climate–incidence series [15] (outbreak peaks). The systems are not physically similar; the comparison tests whether *operational* failure modes of the legacy clock are domain-specific or generic.

These limitations are largely generic across domains. Both the Holter and DengAI series spend most of the evaluation window in band C. Under equation (4), long chaotic runs deepen Feigenbaum compression \(\delta^{-k_{\mathrm{run}}}\), so \(\Delta t^{\mathrm{base}}\) collapses toward zero. Multiplying a near-zero base by \(\Gamma_3>1\) still yields a near-zero step: **the gain cannot inflate a clock that the legacy construction has already frozen.** Many Holter and DengAI rows therefore show \(\Delta T\approx 0\) even when \(A_3\) or excess³ move. The exception (Iquitos 2004) is instructive: chaos occupancy falls to \(\approx 88\%\), active \(\Delta t^{\mathrm{base}}\) reappears, and legacy \(\Delta T=+1.24\).

The paired design therefore evaluates two operational questions: whether hardened \(A_3\) remains selective under real hyper-persistence (alarm behaviour), and under what conditions \(\Gamma_3\) can displace the legacy index \(T\) (clock behaviour).

Proposal 1 uses the same activation core and \(\beta\) in both domains. Sample sizes are small relative to a full cohort study (Section 6.5). Thresholds for \(A_3\) were fixed *a priori* from synthetic S0 and one-at-a-time sensitivity analyses, and were **not** re-optimized on ventricular-fibrillation or outbreak labels.

#### 6.4.1 Contrastive protocol

| | **Holter (cardiology)** | **DengAI (epidemiology)** |
|--|-------------------------|---------------------------|
| Data | SDDB 30/31/35 + NSRDB 16265/16272 | San Juan and Iquitos training series; top-3 peaks \(\ge\) P80, separation \(\ge 26\) weeks |
| Proxy / \(W\) / \(d_{\min}\) | \([z(\mathrm{RR}),z(\lvert\Delta\mathrm{RR}\rvert)]\), \(W{=}101\), stride 5, \(\theta_3{=}0.08\), \(d_{\min}{=}2\) | \([\mathrm{cases},T,\mathrm{precip},\mathrm{RH}]\), \(W{=}13\), stride 1, \(\theta_3{=}0.10\), \(d_{\min}{=}3\) |
| Events / controls | pre-VF versus NSRDB | 40 weeks pre-peak (basal 13 + approach 12) versus inter-epidemic maxima \(<\) P60 |
| P1 / ablation | Hardened activation; \(\beta\in\{0,\,0.5\}\) | identical |

**Figures.** Holter pre-event series, baseline→approach rates and lead, and false-alarm rate; DengAI analogues with weekly time axis and outbreak peaks marked (Appendix D).

#### 6.4.2 Results by domain

**Holter — events and controls**

| Rec | type | chaos% | A₃ hard bas→app | Γ₃ app | ΔT legacy | ΔT Holter† | Lead A₃ / e³ |
|-----|------|--------|-----------------|--------|-----------|------------|--------------|
| 30 | event | 100% | 0.000 → 0.000 | 1.012 | ≈0 | +89 | — / 3.1 h |
| 31 | event | 100% | 0.001 → 0.000 | 1.014 | ≈0 | +197 | — / 6.9 h |
| 35 | event | 100% | 0.004 → 0.003 | 1.054 | ≈0 | +625 | 5.0 h / 8.0 h |
| 16265 | control | 100% | rate 0.014 | 1.118 | ≈0 | +1402 | FAR ≈21.6/24h |
| 16272 | control | 100% | rate 0.019 | 1.134 | ≈0 | +1491 | FAR ≈25.6/24h |

†**ΔT Holter** denotes a *diagnostic* clock \(\Delta t=\Delta t_0\,g(\tau)\,\Gamma_3\) **without** Feigenbaum depth; it is **not** the default of equation (1). It is reported only as a counterfactual: the displacement \(\Gamma_3\) would produce if the base interval were not compressed to zero. The operational claim about legacy \(\Delta T\) uses the full equation (4) construction.  
**Holter aggregates.** Hard \(A_3\) sensitivity **1/3** versus absolute-\(z\) excess³ **3/3**; active \(\Delta t^{\mathrm{base}}\) **\(\sim 0.1\%\)**.

**DengAI — outbreaks and controls**

| ID | type | Peak | chaos% | A₃ hard bas→app | Γ₃ app | ΔT legacy | Lead A₃ / e³ |
|----|------|------|--------|-----------------|--------|-----------|--------------|
| SJ-O1-1994 | outbreak | 461 | 100% | 0.00 → 0.00 | 1.11 | ≈0 | — / — |
| SJ-O2-1998 | outbreak | 329 | 98% | 0.00 → 0.00 | 1.03 | ≈0 | — / — |
| SJ-O3-2007 | outbreak | 170 | 100% | 0.07 → 0.23 | 1.40 | ≈0 | — / 4 w |
| IQ-O1-2004 | outbreak | 116 | **88%** | 0.00 → 0.15 | 1.39 | **+1.24** | **11 w** / 23 w |
| IQ-O2-2008 | outbreak | 58 | 100% | 0.00 → 0.62 | 2.38 | ≈0 | 25 w / 26 w |
| IQ-O3-2008 | outbreak | 63 | 100% | 0.00 → 0.69 | 2.38 | ≈0 | 10 w / 15 w |
| controls (4) | inter-ep. | — | 95–100% | rate 0–0.24 | 1.12–1.56 | ≈0 | mean FAR **1.62**/52w |

**DengAI aggregates.** Hard \(A_3\) sensitivity **3/6** (all Iquitos) versus excess³ **4/6**; mean legacy \(\Delta T\) **\(+0.207\)** (driven by IQ-2004); active \(\Delta t^{\mathrm{base}}\) **\(\sim 7.3\%\)**; mean outbreak chaos **97.6%**.

#### 6.4.3 Cross-domain synthesis

| | **Holter** | **DengAI** | **Cross-domain interpretation** |
|--|------------|------------|--------------------------------|
| Band C → legacy \(\Delta T\) | chaos **100%**; \(\Delta t^{\mathrm{base}}\) **\(\sim 0.1\%\)**; \(\Delta T\) **\(\approx 0\)** | chaos **\(\sim 98\%\)**; \(\Delta t^{\mathrm{base}}\) **\(\sim 7\%\)**; \(\Delta T\) **\(\approx 0\)** except **IQ-2004 (\(+1.24\))** | C saturation is not Holter-specific. \(\Gamma_3\) displaces \(T\) **only if** \(\Delta t^{\mathrm{base}}\not\approx 0\). |
| Gate \(A_3\) / lead / FAR | hard \(\lesssim 0.02\); sens. **1/3** vs e³ **3/3**; FAR \(\sim\)**24**/24h | bas→app in Iquitos; sens. **3/6** vs e³ **4/6**; FAR \(\sim\)**1.6**/52w | (B)∩(D) restrict activation; \(A_3\) is stricter than excess³; event/outbreak specificity remains to be demonstrated. |
| Ablation \(\beta{=}0\) | \(\max\lvert\Delta T\rvert=0\) | \(\max\lvert\Delta T\rvert=0\) | The Φ₃ channel is ablatable in both domains. |

**Cross-domain conclusions.**

1. **Proposal 1 is implementable and auditable** in two empirical domains with a shared computational core and parameters fixed *a priori*.
2. **Hardened \(A_3\) functions as a selectivity gate.** Hyper-persistence of *regime C* does not imply hyper-persistence of Φ₃ *alarms*. On Holter recordings, hard activation remains scarce. In Iquitos, activation discriminates baseline from approach when surplus and dual-scale persistence are jointly present.
3. **The legacy clock is not a universal vehicle for lead time.** Under sustained occupancy of band C, Feigenbaum compression drives \(\Delta t^{\mathrm{base}}\) toward zero; multiplication by \(\Gamma_3\) then leaves \(T\) unchanged. IQ-2004 illustrates the conditional mechanism: chaos 88%, active \(\Delta t^{\mathrm{base}}\) about 24%, \(\Delta T=+1.24\), \(A_3\) lead 11 weeks. On Holter data, \(A_3\) primarily supplies a **conditioned alarm** rather than inflation of \(T\). The clock without Feigenbaum depth is reported only as an auxiliary diagnostic index.
4. **Neither reduction in false-alarm rate nor operational superiority is established.** Under the fixed thresholds used, controls activated as often as—or more often than—events or outbreaks. Extreme *case-count* peaks (San Juan 1994 and 1998) do not activate hard \(A_3\): multivariate ordinal surplus is not reducible to univariate incidence magnitude.

**Further empirical extensions** include a domain-specific clock or redefinition of condition (A); DengAI proxy-sensitivity analyses; an SDDB cohort with \(N\ge 10\) and surrogates; SJU-3; and RQA condition (E) once the domain clock is stabilized.

### 6.5 Extended empirical validation

| Dataset | Validation objective |
|---------|----------------------|
| **DengAI (extension)** | Additional peaks; surrogates; covariate-proxy sensitivity; outbreak threshold |
| **SJU-3 (12 traps)** | Effect of Φ₃ on the clock under core hyper-persistence (\(\sim 69.6\%\) occupancy) |
| **SDDB Holter (\(N\approx 10\) high-quality)** | Cohort lead and FAR; domain clock versus legacy; surrogates |
| **Negative control** | Full NSRDB; temporal label shuffle; long DengAI baseline periods |

**Comparison protocol (per event).**

1. Compute \(T^{\mathrm{base}}\), \(T^{(P1)}\), and (optional diagnostic) a clock without Feigenbaum depth.
2. Define alarms on hard and soft \(A_3\) and, in parallel, on the absolute \(z\)-score of excess³.
3. Report lead, false-alarm rate, and phase-shuffle \(p\)-values.
4. Ablation: \(\beta=0\); removal of (B), (C), or (D) individually.

### 6.6 Pre-specified success criteria

**Operational success of Proposal 1** is declared if, in at least two of three domains (synthetic S2, dengue, cardiology),

1. the median lead of \(T^{(P1)}\) is at least that of \(T^{\mathrm{base}}\) with false-alarm non-inferiority (\(+{\le}5\) absolute percentage points), **or**
2. the false-alarm rate is significantly lower at comparable lead, **and**
3. on S0, the \(A_3\) activation rate is bounded and \(T^{(P1)}\) exhibits no spurious superiority.

**Results relative to these criteria.** Criterion (3) is met on synthetic S0. Criteria (1)–(2) are not satisfied by the paired empirical analyses of Section 6.4. Those analyses do establish: (i) selectivity of \(A_3\) under real hyper-persistence; (ii) dependence of legacy \(\Delta T\) on escape from band C; (iii) exact \(\beta=0\) ablation; (iv) event- and outbreak-level specificity under fixed thresholds remains to be demonstrated.

**Structural success of Proposal 2** further requires that \(\rho_3\) separate S2 regimes consistently with nested \(f_3\). Proposal 2 is assessed on synthetic S2 only.

---

## 7. Risks and limitations

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Double counting** | excess³ correlated with \(\tau_s\); Φ₃ may add no new clock information | Condition (C); ablation; report \(I(\Gamma_3;\tau_s)\) |
| **Hyper-persistence** | Near-continuous activation under chronic band C | (D)+(E); \(A_3\) on \(\Delta e_3\); (B)∩(D) (Section 6.4) |
| **Feigenbaum / band C** | Chronic \(\lvert\tau\rvert<\tau_{\mathrm{ch}}\) freezes \(\Delta t^{\mathrm{base}}\approx 0\); legacy \(\Delta T\) uninformative | Domain clock without depth; redefine (A); non-saturating proxy; lead via alarms |
| **Threshold overfitting** | Multiplicity of \(\theta\) | Fixed defaults; one-at-a-time sensitivity; no fit on test events |
| **Degenerate \(d=2\)** | Order-3 surplus ill-defined | Disable channel 3 if \(d<3\) |
| **Surrogate cost** | Online \(p\)-values for (B) are expensive | Online \(z\)-score / baseline CDF; offline surrogates |
| **Sign of \(\Delta e_3\)** | G1 can yield \(\Delta e_3<0\) under true reorganization | Prefer absolute-delta (8') for early warning |
| **\(R_3\) instability** (P2) | Over-aggressive exponential compression | Low \(R_{\max}\) (2–4); \(J=0\) initially |
| **Partial-information confusion** | excess³ misread as a complete causal atom | Pre-specified hybrid proxy, not complete PID |
| **Two formalisms** | Legacy (1) versus nested (2) | Report both; P1 as minimal bridge |
| **Jump parameters** | \(J>0\) may appear ad hoc | Keep \(J=0\) until S4 and extended criteria are met |

**Conceptual limitation.** excess³ is not a complete partial-information decomposition. Its incorporation into the clock improves the **dynamics of the index**; it does not convert the proxy into an axiomatic theory of synergistic information. Causal interpretation of the data-generating process remains deliberately cautious.

---

## 8. Operational priority

### 8.1 Operational default (Proposal 1)

**Proposal 1 (conservative) is adopted as the default upgrade of the operational pipeline**, with:

- the **absolute-delta** form (8') as the default gain;
- the soft gate (13) with conditions (A)–(D);
- optional extension (E) on hyper-persistent datasets;
- pre-specified \(\beta\) (for example, \(0.5\)) and sensitivity sweep \(\beta\in\{0,0.25,0.5,1.0\}\).

The default is motivated by five properties:

1. **Dynamical closure with minimal structural change.** Φ₃ is no longer confined to a parallel diagnostic: it modifies \(\Delta t_k\) explicitly and in an ablatable manner.
2. **Falsifiability.** Setting \(\beta=0\) recovers the standard operational construction without the Φ₃ channel.
3. **Controlled behaviour under hyper-persistence.** When \(A_3\) tracks surplus *change* rather than mere occupancy of band C, trivial activation is limited.
4. **Computational feasibility.** The construction is implementable on existing nested-RECD, dengue, and cardiology pipelines at \(O(1)\) additional cost after excess³ has been computed.
5. **Compatibility.** The proposal is consistent with nested RECD (2) and with six-mode RQA (Φ₃-gain may enter as an additional mode or clock weight, not as a substitute for LAM/TT).

Under chronic band C, Feigenbaum compression can freeze \(\Delta t^{\mathrm{base}}\); \(\Gamma_3\) then cannot displace \(T\) until the base reopens. In that regime, \(A_3\) should be evaluated as a *conditioned alarm*, and a domain clock without depth may be considered (Section 6.4, Section 7). The excess³ weights 0.6/0.4 remain fixed so that clock effects are not confounded with retuning of the proxy on the same evaluation events.

### 8.2 Status of Proposal 2

Proposal 2 is an **experimental** dual-channel extension and is not the operational default. Dual-channel depth and optional jumps change the *shape* of discrete time, not only its scale. That construction is useful for testing consistency with nested \(f_3\), but it multiplies free parameters and makes field failures harder to localize. Proposal 2 is therefore considered only after Proposal 1 shows domain benefit *and* nested mass \(f_3\) still diverges from the operational clock geometry (Section 4; synthetic S2).

- **Structure.** Dual channel \(C_{12}+C_3\), depth \(R_3\), and metric \(\rho_3\) aligned with nested \(f_3\) (evaluated on synthetic suite S2).
- **Scope of evaluation.** Synthetic systems only; \(J=0\) and \(R_{\max}=3\).
- **Condition for further development.** Jumps and deeper compression are considered only after Proposal 1 demonstrates domain benefit under the criteria of Section 6.6.
- **Surveillance applications.** Proposal 2 is not applied to epidemiological or cardiac deployment until those criteria are satisfied.

### 8.3 Relative priority among related developments

| Development | Relative priority |
|-------------|-------------------|
| Integration of Φ₃ into RECD dynamics (P1) | Primary operational priority |
| Adaptive RQA and cross-recurrence communities | Parallel; couples via condition (E) |
| Additional out-of-sample validation of excess³ | Informs thresholds of (B) |
| Complete ordinal partial-information decomposition | Longer-term; independent of P1 deployment |

### 8.4 Open empirical steps

Priority empirical extensions include: an SDDB cohort analysis with a domain-specific clock; DengAI extension with surrogate ensembles [11]; SJU-3; and RQA condition (E) [3, 13] once the domain clock is stabilized in cardiology and dengue. Shared numerical defaults are listed in Appendix A.

---

## 9. Conclusion

Prior work on Systemic Tau and the Discrete Extramental Clock has established ordinal relational metrics and a base discrete-time construction [1, 5], excess³ as a continuous Level-3 proxy [2], Holter evidence of pre-VF ordinal reorganization [4], and recurrence-based refinement under hyper-persistence [3, 13]. The unresolved operational question is how Φ₃ should enter the construction of the index \(t_k\) in equation (1), while remaining consistent with the nested mass representation (2).

We develop two complementary answers because no single map is forced by the theory. **Proposal 1** keeps the legacy clock and multiplies its increment by a surplus-gated gain—the smallest change that makes Φ₃ dynamical and ablatable. **Proposal 2** gives Φ₃ its own channel and depth—the construction needed to test structural alignment with nested mass, but not yet justified for field use. Shared hardened activation criteria prevent band-C hyper-persistence from turning either construction into a permanent rescaling.

The principal results are:

1. a structural diagnosis of the gap between parallel use of Φ₃ and a generative contribution to the operational clock;
2. a multiplicative, ablatable **Proposal 1** suitable for operational pipelines;
3. a dual-channel **Proposal 2** with depth-dependent compression (experimental; synthetic evaluation only);
4. **hardened activation criteria** based on surplus change, residual synergy, dual-scale persistence, and adaptive \(\theta_e\);
5. **synthetic results (S0–S2)** with null \(A_3\) on S0, discrimination of chaos from pre-chaos, and high \(\Gamma_3\leftrightarrow f_3\) alignment on S1;
6. **paired Holter and DengAI analyses:** \(A_3\) limits alarm hyper-persistence; Feigenbaum compression and band-C occupancy restrict legacy \(\Delta T\) in both domains except for partial escape (IQ-2004); event- and outbreak-level specificity under fixed thresholds remains to be demonstrated.

In summary, Proposal 1 is auditable and implementable across domains; the hardened \(A_3\) gate successfully controls hyper-persistence; the legacy clock advances only when there is partial escape from the chaos band; and domain-specific validation remains necessary before any operational claims can be made. Displacement of \(T\) still requires escape from band C (or a domain clock that does not freeze \(\Delta t^{\mathrm{base}}\)). Cohort-scale validation remains a prerequisite for deployment.

excess³ is treated throughout as a pre-specified hybrid proxy rather than as a complete partial-information decomposition. Φ₃ enters the clock solely through falsifiable, ablatable maps \(F\).

---

## Appendix A — Default parameters

| Symbol / field | Default | Notes |
|----------------|---------|-------|
| Synthetic \(W\) | 13 | S0–S2 generators |
| DengAI \(W\) | 13 | stride 1; \(\theta_3=0.10\) |
| Holter \(W\) (CCTP) | 101 | stride 5; \(\theta_3=0.08\) |
| \(m\) (Bandt–Pompe) | 3 | delay 1 |
| \(\tau_{\mathrm{ch}}\) | 0.41 | chaos threshold |
| \(\tau_{\mathrm{st}}\) | 0.50 | strong-coherence threshold |
| \(\delta\) | 4.6692016091 | Feigenbaum constant |
| \(\beta\) (P1) | 0.5 | channel intensity |
| \(\psi\) | softplus | monotone map |
| \(\psi\) mode | `level` | or `change` / `both` |
| absolute-delta | `True` | form (8') |
| normalization | `zscore` | alternative `rank` / `mad` |
| \(P_{\mathrm{arm}}\) | 3 | approach arm length |
| \(\theta_e\) | 1.25 | level threshold |
| \(\theta_{\Delta}\) | 0.40 | change threshold |
| require change | `True` | (B′) |
| \(\theta_{\mathrm{res}}\) | 0.20 | residual synergy; pre-specified via S0 |
| \(L_s,L_{s,\min}\) | 3, 2 | short scale |
| \(L_m,L_{m,\min}\) | 7, 4 | medium scale |
| soft offset \(s_0\) | 3.25 | logistic offset |
| soft floor | 0.25 | \(A_3^{\mathrm{soft}}<\mathrm{floor}\Rightarrow 0\) |
| adaptive \(\theta_e\) | on, \(\kappa=0.5\) | baseline CV inflation |
| \(d_{\min}\) | 3 (default); **2 on bivariate Holter** | bivariate CCTP |
| \(R_{\max}\) (P2) | 3 | synthetic dual-channel |
| \(J\) (P2) | 0 | no jumps |
| \(\eta\) (P2) | 0.35 | synthetic dual-channel |
| α_Syn, α_Surp | 0.6, 0.4 | fixed |

## Appendix B — Relation to the existing nested formalism

Equation (2) of the 2026 framework [1] is already a **linearly weighted** integration of Φ₃ into \(\Delta\mathrm{RECD}\). The present construction does not redefine Φ₃; it:

1. **couples** Level-3 structure to the legacy increment (1) used in applications;
2. **conditions** the weight on surplus evidence (not solely on \(\lambda(\tau_s)\));
3. **specifies** activation, ablation, and validation so that the channel is scientifically auditable.

In unified notation, Proposal 1 is the special case

\[
\Delta t_k
=
\Delta t_k^{\mathrm{base}}\,g\,\alpha\,
\bigl(1+\beta A_3\psi(\cdot)\bigr),
\]

while equation (2) is

\[
\Delta\mathrm{RECD}
=
\sum_\ell\alpha_\ell(\lambda)\Phi_\ell^\ast.
\]

A complete pipeline may report **both** indices: \(T^{\mathrm{legacy+P1}}\) for historical comparability and \(T^{\mathrm{nested}}\) for mass fractions \(f_\ell\).

## Appendix C — Scope boundaries

The following topics are outside the present analysis:

- axiomatic partial-information reformulation of Syn/Surp;
- claims about the ontology of physical time;
- grid-search optimization of \(\beta\) on outbreak or ventricular-fibrillation labels;
- replacement of the six-mode RQA consensus (complemented, not removed).

---

## References

1. Padilla-Villanueva, J. (2026). *Systemic Tau and the RECD Framework: A Relational Theory of Hierarchical Ordinal Conjunctions and Critical Transitions in Complex Systems.* Zenodo. DOI: [10.5281/zenodo.21287252](https://doi.org/10.5281/zenodo.21287252).
2. Padilla-Villanueva, J. (2026). *excess³: a pre-specified continuous proxy for order-3 synergistic surplus — methods, Spanish introduction, and cross-domain notes.* Zenodo. DOI: [10.5281/zenodo.21385937](https://doi.org/10.5281/zenodo.21385937).
3. Padilla-Villanueva, J. (2026). *El Paradigma del Tau Sistémico y la Ley del Reloj Extramental Discreto en Sistemas Complejos (versión ilustrada).* Subtitle: *Integración del Análisis de Recurrencia Cuantitativa (RQA) para la Caracterización de Hiperpersistencia* [illustrated RECD monograph with RQA-based hyper-persistence characterization]. Zenodo. DOI: [10.5281/zenodo.20576241](https://doi.org/10.5281/zenodo.20576241).
4. Padilla-Villanueva, J. (2026). *CCTP/SDDB: Systemic Tau and ordinal RECD before spontaneous ventricular fibrillation* (companion code, cleaned RR series, results, and figures for the manuscript *Context-Dependent Relational Reorganization of Heart Rate Dynamics Precedes Spontaneous Ventricular Fibrillation*). Zenodo. DOI: [10.5281/zenodo.21348295](https://doi.org/10.5281/zenodo.21348295).
5. Padilla-Villanueva, J. (2026). *Systemic Tau: A Topological Framework for Early Warning Signals in Complex Systems* (v5.6.1). Zenodo. DOI: [10.5281/zenodo.21271145](https://doi.org/10.5281/zenodo.21271145).
6. Feigenbaum, M. J. (1978). Quantitative universality for a class of nonlinear transformations. *Journal of Statistical Physics*, 19, 25–52. DOI: [10.1007/BF01020332](https://doi.org/10.1007/BF01020332).
7. Feigenbaum, M. J. (1983). Universal behavior in nonlinear systems. *Physica D*, 7, 16–39. DOI: [10.1016/0167-2789(83)90112-4](https://doi.org/10.1016/0167-2789(83)90112-4).
8. Kendall, M. G. (1938). A new measure of rank correlation. *Biometrika*, 30, 81–93. DOI: [10.2307/2332226](https://doi.org/10.2307/2332226).
9. Bandt, C., & Pompe, B. (2002). Permutation entropy: A natural complexity measure for time series. *Physical Review Letters*, 88, 174102. DOI: [10.1103/PhysRevLett.88.174102](https://doi.org/10.1103/PhysRevLett.88.174102).
10. Scheffer, M., Bascompte, J., Brock, W. A., Brovkin, V., Carpenter, S. R., Dakos, V., Held, H., van Nes, E. H., Rietkerk, M., & Sugihara, G. (2009). Early-warning signals for critical transitions. *Nature*, 461, 53–59. DOI: [10.1038/nature08227](https://doi.org/10.1038/nature08227).
11. Theiler, J., Eubank, S., Longtin, A., Galdrikian, B., & Farmer, J. D. (1992). Testing for nonlinearity in time series: the method of surrogate data. *Physica D*, 58, 77–94. DOI: [10.1016/0167-2789(92)90102-S](https://doi.org/10.1016/0167-2789(92)90102-S).
12. Williams, P. L., & Beer, R. D. (2010). Nonnegative decomposition of multivariate information. arXiv:1004.2515 [cs.IT]. DOI: [10.48550/arXiv.1004.2515](https://doi.org/10.48550/arXiv.1004.2515).
13. Marwan, N., Romano, M. C., Thiel, M., & Kurths, J. (2007). Recurrence plots for the analysis of complex systems. *Physics Reports*, 438, 237–329. DOI: [10.1016/j.physrep.2006.11.001](https://doi.org/10.1016/j.physrep.2006.11.001).
14. Goldberger, A. L., Amaral, L. A. N., Glass, L., Hausdorff, J. M., Ivanov, P. C., Mark, R. G., Mietus, J. E., Moody, G. B., Peng, C.-K., & Stanley, H. E. (2000). PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals. *Circulation*, 101(23), e215–e220. DOI: [10.1161/01.CIR.101.23.e215](https://doi.org/10.1161/01.CIR.101.23.e215).
15. DrivenData. (2017). *DengAI: Predicting disease spread* [Competition dataset; San Juan and Iquitos weekly dengue cases and climate covariates]. https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/
