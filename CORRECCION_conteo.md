# Corrección de conteo en el humo DengAI (25 sep 2026)

`src/smoke_dengai.py` importa `recd_ordinal_levels.py` del piloto CCTP. Esa copia tenía el error de nested-recd ≤ 0.2.2: `np.unique` sobre una lista de tuplas aplana los símbolos. DengAI usa cuatro series (casos, temperatura, precipitación, humedad), así que `excess3`, la compuerta A3 y los adelantos `ews_excess3` cambian. Las suites sintéticas que simulan excess³ con un normal, y el brazo SDDB de dos series, no cambian por este error.

La función vendida ya cuenta filas, igual que nested-recd 0.2.3 (https://doi.org/10.5281/zenodo.22970079).

El humo se volvió a correr el 25 sep 2026 con los mismos brotes. El CSV anterior queda en `figures/results_smoke_dengai_pooled_0.2.2.csv`. Cambian, entre otros:

| evento | excess³ lead, conteo viejo | excess³ lead, conteo nuevo | Δ excess³ approach−basal, viejo | nuevo |
|---|---:|---:|---:|---:|
| SJ-O3-2007 | 4 | 22 | 0.053 | 0.222 |
| IQ-O1-2004 | 23 | 7 | −0.155 | −0.193 |
| IQ-O2-2008 | 26 | 23 | −0.239 | −0.457 |
| IQ-O3-2008 | 15 | 23 | −0.281 | −0.558 |

Los PDF v0.5 depositados en https://doi.org/10.5281/zenodo.21400599 siguen citando el humo anterior. Esta nota y los archivos `figures/results_smoke_dengai.*` son la corrida corregida.
