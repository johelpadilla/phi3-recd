# Preprint: Dynamic Integration of Level-3 Ordinal Synergy into the RECD

**Working title:** *Integrating Φ₃ (excess³) into RECD Dynamics: From Parallel Metric to Structural Clock Contribution*

**Author:** Johel Padilla-Villanueva  
**Status:** Draft **v0.5** — methods + synthetic S0–S2 + dual-domain real-data smoke, unified contrast narrative (July 2026)  
**Python package:** [`phi3-recd`](https://pypi.org/project/phi3-recd/) **v0.5.0** (optional coupling layer; NumPy only)  
**Repository:** https://github.com/johelpadilla/phi3-recd

## Preprint PDFs (v0.5)

| Language | File | Pages |
|----------|------|-------|
| English | [`Phi3_RECD_Dynamic_Integration_v0.5.pdf`](Phi3_RECD_Dynamic_Integration_v0.5.pdf) | 30 |
| Spanish | [`Phi3_RECD_Integracion_Dinamica_ES_v0.5.pdf`](Phi3_RECD_Integracion_Dinamica_ES_v0.5.pdf) | 31 |

Sources: `manuscript.md` (EN), `manuscript_es.md` (ES). Rebuild:

```bash
python3 scripts/build_pdf.py          # English
python3 scripts/build_pdf.py --lang es  # Spanish
```

## Purpose

Close a structural gap in the Systemic Tau / RECD programme: `excess³` (Level Φ₃) is a strong continuous proxy for irreducible ordinal surplus, but in most operational pipelines it remains a **parallel** early-warning readout. This preprint proposes **falsifiable, implementable** ways to let Φ₃ modify the discrete clock update itself — linking the 2026 nested hierarchy to legacy surveillance pipelines.

## Package (`phi3-recd`)

This is a **clock-map** library, not a new ordinal-metric suite. It does **not** recompute \(\tau_s\) or excess³; those come from prior work (e.g. [`nested-recd`](https://github.com/johelpadilla/nested-recd) or Systemic Tau pipelines). What it ships:

| Symbol | Role |
|--------|------|
| Hardened \(A_3\) | Level-3 activation gate (conditions A–D) |
| \(\Gamma_3\) / **P1** | Multiplicative surplus gain on legacy \(\Delta t\) (default) |
| **P2** | Dual-channel experimental map |
| \(\rho_3\), \(\rho_3^{\mathrm{marg}}\) | Contribution diagnostics for ablation / validation |

### Install

```bash
pip install phi3-recd
# or editable from this repo:
python3 -m pip install -e ".[dev]"
python3 -m phi3_recd          # synthetic demo
pytest -q                     # contract tests
```

Optional extras: `pip install -e ".[ordinal]"` pulls `nested-recd` for excess³ upstream; `.[full]` adds plotting/pandas for the preprint smokes.

### Minimal API

```python
import numpy as np
from phi3_recd import ActivationConfig, P1Config, recd_base, recd_p1

# tau_s, excess3: precomputed series; baseline: bool mask for normalization
tau = np.asarray(...)
e3 = np.asarray(...)
baseline = np.zeros(len(tau), dtype=bool)
baseline[:50] = True

base = recd_base(tau)
p1 = recd_p1(tau, e3, baseline, n_vars=4, cfg=P1Config(beta=0.5),
             act_cfg=ActivationConfig())
# audit: P1Config(beta=0.0) recovers base["t"] exactly
```

## Contents

| Path | Description |
|------|-------------|
| `manuscript.md` | Full research preprint (English), **v0.5** |
| `manuscript_es.md` | Full academic translation (Spanish), **v0.5** |
| `Phi3_RECD_*_v0.5.pdf` | Built PDFs (EN + ES) |
| `src/phi3_recd/` | Installable package: hardened A₃, P1, P2 |
| `src/validate_synthetic.py` | S0–S2 synthetic validation + figure export |
| `src/smoke_real_sddb.py` | Real-data smoke: SDDB events + NSRDB controls |
| `src/smoke_dengai.py` | Real-data smoke: DengAI San Juan / Iquitos |
| `tests/` | Package contract tests |
| `pyproject.toml` | `phi3-recd` packaging metadata |
| `data/dengai/` | DengAI train features + labels (DrivenData) |
| `refs/references.bib` | Bibliography (15 entries, in-text cites) |
| `figures/` | Synthetic + smoke figures and result tables |
| `scripts/build_pdf.py` | Dual-language pandoc + xelatex PDF pipeline |

## Quick run

```bash
# package demo (after pip install -e .)
python3 -m phi3_recd

# preprint validation scripts
cd src
python3 validate_synthetic.py  # S0–S2 tables + PNG figures
python3 smoke_real_sddb.py     # needs ../Cardiac_CCTP_Pilot/data/
python3 smoke_dengai.py        # uses ../data/dengai/
```

## v0.5 highlights (vs v0.4)

- **Narrative:** Holter + DengAI smokes merged into one §6.4 strategic contrast (protocol table + joint comparison + four defensible conclusions)
- **Density:** removed duplicated “honest reading” lists; single message across domains
- **Consistency:** soft_offset \(s_0=3.25\) + soft_floor aligned with `phi3_recd.py`; Appendix A → v0.5
- **No new empirical runs** — numbers same as v0.3–v0.4

## v0.4 highlights (kept)

- **DengAI smoke:** SJ + IQ; IQ-2004 ΔT legacy +1.24; A₃ sens 3/6; control FAR ~1.6/52w
- Chaos-band still high (~98%) with 4-var proxy; dt_base active ~7% vs ~0.1% Holter

## v0.3 highlights (kept)

- **Holter smoke:** SDDB 30/31/35 + NSRDB; Feigenbaum freeze; A₃ sparse under hyperpersist
- P2 experimental; Holter-path diagnostic clock reported alongside legacy T

## v0.2 highlights (kept)

- Hardened A₃; synthetic S0–S2 gates; corr(Γ−1, f₃) ≈ 0.99 on S1

## Scope

**Is:** mathematical coupling of Φ₃ into `Δt_k`; two graded designs (P1 recommended, P2 experimental); activation; synthetic results; dual-domain real-data smokes with limitations  
**Is not:** strong ontology; full PID; operational EWS claim (smokes do not support FAR superiority)

## Recommended citation (placeholder)

Padilla-Villanueva, J. (2026). *Integrating Φ₃ (excess³) into RECD Dynamics: From Parallel Metric to Structural Clock Contribution* (Preprint draft v0.5).
