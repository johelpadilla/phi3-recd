# Integración de Φ₃ (excess³) en la dinámica RECD: de métrica paralela a contribución estructural del reloj

**Autor:** Johel Padilla-Villanueva  
**Afiliación:** Departamento de Salud Ambiental, Universidad de Puerto Rico — Recinto de Ciencias Médicas  
**ORCID:** 0000-0002-5797-6931  
**Contacto:** joel.padilla2@upr.edu · johelpadilla@gmail.com  
**Fecha:** julio de 2026  
**Palabras clave:** Tau Sistémico, RECD, excess³, sinergia ordinal, señales de alerta temprana, universalidad de Feigenbaum, conjunciones anidadas, sistemas complejos

---

## Resumen

El marco del Tau Sistémico (\(\tau_s\)) y del Reloj Extramental Discreto (RECD) identifica transiciones críticas mediante reorganización relacional ordinal, y no mediante el crecimiento de una magnitud univariante. Se ha formalizado y validado en sistemas sintéticos una jerarquía de tres niveles de conjunciones ordinales—Φ₁ (coincidencia), Φ₂ (relación persistente) y Φ₃ (superávit sinérgico irreducible, operacionalizado por el proxy continuo excess³). El presente trabajo salva la distancia entre la jerarquía teórica anidada y los *pipelines* operacionales heredados de la vigilancia epidemiológica y cardíaca. En dichos *pipelines*, excess³ ha permanecido habitualmente como diagnóstico **paralelo**: contribuye a puntuaciones de alerta temprana y a fracciones de masa anidadas, pero no entra de manera sistemática en la actualización del tiempo discreto.

Se abordan dos vías complementarias. La **Propuesta 1** multiplica el incremento RECD *ya existente* por una ganancia \(\Gamma_3\) condicionada al superávit: el cambio es mínimo, de modo que cualquier modificación del reloj puede atribuirse a Φ₃ al fijar \(\beta=0\). La **Propuesta 2** reconstruye el avance en dos canales aditivos y permite, además, que Φ₃ profundice la compresión de Feigenbaum: es más expresiva, pero más difícil de auditar en campo, y por ello se trata como experimental. Ambas propuestas comparten la misma compuerta de activación endurecida \(A_3\), porque el principal riesgo práctico no es «demasiado poco Φ₃», sino la activación *trivial* siempre que el sistema permanece largos tramos en la banda de caos (hiperpersistencia).

El análisis procede así: (i) diagnosticar por qué el despliegue paralelo de Φ₃ deja la jerarquía de emergencia dinámicamente incompleta; (ii) definir las Propuestas 1 y 2; (iii) especificar reglas de activación que exigen *cambio* de superávit, sinergia residual y persistencia a dos escalas; (iv) validar en las suites sintéticas S0–S2 con métricas preespecificadas (tasas de \(A_3\), \(T_{\mathrm{final}}\), \(\rho_3\), \(\mathrm{corr}(\Gamma_3-1,f_3)\), robustez al ruido); y (v) ejecutar **análisis empíricos emparejados** sobre registros Holter SDDB/NSRDB y series DengAI de San Juan/Iquitos—dos dominios que comparten ocupación crónica de la banda C pero difieren en escala temporal y estructura del proxy. Interpretados conjuntamente, la compuerta endurecida \(A_3\) controla la hiperpersistencia de alarmas en ambos dominios; el \(\Delta T\) legado avanza solo cuando la ocupación de la banda de caos permite movimiento de \(\Delta t^{\mathrm{base}}\); y la especificidad a nivel de evento y de brote bajo umbrales fijos queda por demostrar. La Propuesta 1 es el valor operacional por defecto; la Propuesta 2 se retiene para comparación estructural sintética.

A lo largo del trabajo, excess³ se conserva como proxy híbrido preespecificado (0,6 Syn + 0,4 Surp), y no como una descomposición completa de información parcial. Las afirmaciones causales se restringen a la influencia dinámica sobre el índice discreto del reloj.

---

## 1. Incompletitud estructural del despliegue paralelo del Nivel 3

### 1.1 Síntesis operacional del marco de 2026

El presente análisis se asienta sobre el marco Tau Sistémico / RECD desarrollado en preprints previos [1, 5], con excess³ como proxy continuo del Nivel 3 [2]. Sea \(X(t)\in\mathbb{R}^{d}\) una serie multivariante con \(d\ge 2\). En ventanas sucesivas de longitud \(W\), el Tau Sistémico es la correlación de rangos de Kendall media por pares [8]:

\[
\tau_s(k)=\frac{2}{N(N-1)}\sum_{i<j}\tau_K\!\left(r_i^{(k)},r_j^{(k)}\right)\in[-1,1].
\]

Los umbrales operacionales se motivan por la varianza asintótica del \(\tau\) de Kendall bajo independencia y por la universalidad de Feigenbaum [6, 7] (\(\delta\approx 4.6692016091\)):

| Régimen | Condición | Interpretación operacional |
|--------|-----------|----------------------------|
| **S** | \(\tau_s\ge +0.50\) | Coherencia ordinal fuerte |
| **C** | \(\lvert\tau_s\rvert<0.41\) | Banda de caos / volatilidad ordinal elevada |
| **A** | \(\tau_s\le -0.41\) | Antisincronización fuerte |

Las ecuaciones (1) y (2) responden a preguntas distintas [1]. La ecuación (1) es el reloj operacional empleado en *pipelines* de dengue, Holter y RQA [3, 4, 13]: avanza \(t_k\) a partir de \(\tau_s\), de una compuerta y de un factor de estado. La ecuación (2) es la descomposición teórica de masa de la jerarquía de conjunciones Φ₁–Φ₃ [1]. Nada obliga a que coincidan. En la práctica a menudo no lo hacen: \(f_3\) puede ser grande en (2) mientras (1) nunca multiplica ni añade un término Φ₃. Ese desajuste—y no una preferencia formalista—es el punto de partida del presente análisis.

| | **Ecuación legada (1)** | **Ecuación anidada (2)** |
|--|-------------------------|---------------------------|
| Papel | *Pipeline* operacional (epidemiología, RQA, cardiología) | Representación teórica de masas por nivel |
| Pregunta que responde | ¿Cómo avanza el tiempo discreto en campo? | ¿Cómo se particiona el incremento entre Φ₁–Φ₃? |
| Incremento | \(\Delta t_k\cdot g(\tau_s)\cdot\alpha(\mathrm{state})\) | \(\sum_\ell\alpha_\ell(\lambda)\,\Phi_\ell^\ast\) |
| Papel de Φ₃ | Ausente de \(\Delta t_k\) (o solo como adyuvante) | Como masa \(f_3\), con \(\lambda\) construida típicamente solo a partir de \(\tau_s\) |
| Vía de integración | **Modulación de (1) por Φ₃** vía \(\Gamma_3\) o canal dual | Compatible; \(f_3\) se reporta en paralelo |

La construcción clásica del RECD avanza el tiempo discreto acumulado a partir de un intervalo base \(\Delta t_k\), una compuerta \(g(\tau_s)\) y un factor de estado \(\alpha(\mathrm{state})\):

\[
t_{k+1}=t_k+\Delta t_k\cdot g(\tau_s(k))\cdot\alpha(\text{state}_k). \tag{1}
\]

En la formulación teórica anidada, el incremento es una suma ponderada de conjunciones:

\[
\Delta\mathrm{RECD}(t)=\alpha_1(\lambda)\,\Phi_1(t)+\alpha_2(\lambda)\,\Phi_2(t)+\alpha_3(\lambda)\,\Phi_3^\ast(t), \tag{2}
\]

donde \(\Phi_3^\ast\) denota el indicador binario Φ₃ o el proxy continuo excess³, y \(\lambda\) es una pista de régimen (por ejemplo, una transformación de \(\lvert\tau_s\rvert\)).

Sustituir la ecuación (1) por la (2) en todas partes no es viable en aplicaciones: los *pipelines* de campo, las comparaciones históricas y los acoplamientos RQA ya están escritos respecto de (1). Un reemplazo integral rompería la continuidad con series publicadas de dengue y Holter y mezclaría un cambio de *teoría* con un cambio de *implementación*. La Propuesta 1, por tanto, **no reemplaza** la ecuación (2): define un mapa \(F\) que actúa sobre la ecuación (1) y está condicionado a la evidencia de superávit, de modo que el reloj operacional y las fracciones de masa anidadas puedan compararse lado a lado. La ecuación (2) permanece como descomposición diagnóstica de masa; la ecuación (1) permanece como reloj desplegado, ahora opcionalmente consciente de Φ₃.

excess³ se define *a priori* como

\[
\mathrm{excess}^3(t)=0.6\cdot\mathrm{Syn}(t)+0.4\cdot\mathrm{Surp}(t), \tag{3}
\]

donde Syn denota el residual de multiinformación respecto de una línea base por pares y Surp denota la sorpresa en log-razón bajo independencia de símbolos ordinales (entropía de permutación de Bandt–Pompe [9]). Los pesos híbridos 0,6/0,4 y la construcción del proxy continuo siguen el protocolo preespecificado de excess³ [2]; no constituyen una descomposición completa de información parcial en el sentido de Williams y Beer [12]. Los pesos están fijos y no se reestiman sobre el conjunto de datos objetivo.

### 1.2 Despliegue paralelo frente a despliegue dinámico de Φ₃

En el marco de 2026 aparecen tres papeles distintos del Nivel 3 [1, 2]:

1. **Estadístico paralelo de alerta temprana.** \(\Delta\mathrm{excess}^3\) entre una ventana basal y una de aproximación (por ejemplo, intervalos pre-fibrilación ventricular en SDDB [4, 14]; contrastes sintéticos G0–G3), en la tradición más amplia de indicadores de transiciones críticas [10].
2. **Fracción de masa / incremento** en la ecuación (2): \(f_3=\alpha_3\Phi_3^\ast/\sum_\ell\alpha_\ell\Phi_\ell^\ast\).
3. **Contribución estructural al intervalo operacional** \(\Delta t_k\) en la ecuación (1) y a *pipelines* de hiperpersistencia (RQA, consenso de seis modos) [3, 13].

Los papeles (1) y (2) están comparativamente desarrollados. El papel (3) permanece **sin una especificación única y unificada**:

- En vigilancia epidemiológica y refinamiento RQA, el reloj y las señales asociadas se construyen a partir de \(\tau_s\), la persistencia \(P(k)\), \(g(\tau_s)\), LAM/TT/DET y los estados C/D/T. excess³ entra como modo adicional o métrica adyuvante, no como modulador canónico de \(\Delta t_k\).
- En la ecuación (2), \(\alpha_3(\lambda)\) eleva la masa del Nivel 3 cuando \(\lambda\) indica caos; no obstante, \(\lambda\) se construye típicamente a partir de \(\tau_s\) (o de un parámetro de control conocido \(r\)). En consecuencia, el peso de Φ₃ depende del régimen de \(\tau_s\) y no de la **irreducibilidad observada** de excess³ en esa ventana. Un sistema puede ocupar la banda C con excess³ bajo (caos dominado por pares) o con excess³ alto (caos que porta superávit de orden \(\ge 3\)). Estos regímenes exigen relojes distintos si la jerarquía de conjunciones ha de gobernar la construcción del tiempo discreto.
- Sin un canal Φ₃ → reloj, la jerarquía Φ₁ ⊂ Φ₂ ⊂ Φ₃ permanece descriptiva en términos de masa y predictiva como señal de alerta temprana, pero no es generativa del índice de tiempo discreto usado en *pipelines* operacionales.

### 1.3 Cierre dinámico de la jerarquía

**Definición (cierre dinámico).** La jerarquía de conjunciones está dinámicamente cerrada si existe una familia de mapas implementables \(F\) tales que

\[
\Delta t_k = F\bigl(\Delta t_k^{\mathrm{base}},\,g(\tau_s),\,\alpha(\mathrm{state}),\,\Phi_1,\Phi_2,\mathrm{excess}^3;\,\theta\bigr)
\]

con parámetros preespecificados \(\theta\), y si existen predicciones falseables sobre \(T_{\mathrm{RECD}}\), tiempos de anticipación y fracciones de masa que fallan cuando se abla el canal Φ₃ (\(F\) independiente de excess³).

La incorporación de Φ₃ en \(F\) se exige para que:

1. **La profundidad ordinal y el reloj permanezcan distinguibles.** Sin Φ₃ en \(F\), dos trayectorias que compartan \(\tau_s(k)\) y \(P(k)\) producen relojes idénticos aunque su superávit de orden 3 difiera.
2. **La contribución marginal sea contrastable.** La comparación del RECD con y sin el canal Φ₃ constituye un experimento controlado de ablación.
3. **La teoría anidada (2) y el *pipeline* (1) se alineen.** Los dos formalismos coexistentes se unifican así sin reformular el RECD desde sus fundamentos.

Este requisito no implica que excess³ constituya un átomo completo de información parcial, ni que el reloj discreto represente el tiempo físico. Solo exige que el índice \(t_k\) responda a la capa estructural que el marco trata como la más profunda.

### 1.4 Restricciones de diseño heredadas del marco

Toda construcción admisible debe:

- preservar los umbrales \(\tau_{\mathrm{ch}}=0.41\), \(\tau_{\mathrm{st}}=0.50\) y la constante \(\delta\);
- dejar inalterados sobre los datos objetivo los pesos 0,6/0,4 de excess³;
- permanecer computable para ventanas cortas (\(W\sim 13\)) y dimensión moderada \(d\);
- admitir nulos de reordenamiento de fase (*phase-shuffle*) que destruyan la dependencia cruzada preservando los espectros marginales;
- evitar la activación trivial de Φ₃ a lo largo de toda la banda C (hiperpersistencia tropical: 69–87 % del tiempo en el núcleo hiperpersistente);
- permanecer compatible con el RQA como refinamiento de señal y no como sustituto del reloj.

### 1.5 Dos propuestas en lugar de una

Un único mapa de Φ₃ en \(t_k\) no está unívocamente determinado por el marco. Dos presiones de diseño tiran en direcciones opuestas:

1. **Cambio mínimo y auditabilidad.** Los *pipelines* de vigilancia requieren un factor *drop-in* sobre el reloj ya en uso, con un interruptor de un parámetro (\(\beta=0\)) que recupera exactamente el comportamiento basal. Esa presión produce la **Propuesta 1**: multiplicar el incremento existente por \(\Gamma_3\ge 1\).
2. **Fidelidad estructural a la masa anidada.** La jerarquía afirma que el Nivel 3 no es meramente «más del Nivel 2»: puede cambiar *cuán profunda* es la renormalización, y no solo *cuán grande* es el paso. Esa presión produce la **Propuesta 2**: un canal de superávit separado con su propia profundidad de Feigenbaum \(R_3\), y un término opcional de salto.

La Propuesta 1 es la candidata al despliegue: conservadora, ablatable y computacionalmente barata. La Propuesta 2 es la candidata a *comparación estructural* con la ecuación (2), para contrastar si una geometría de canal dual se alinea mejor con \(f_3\) anidada en sistemas sintéticos controlados. Si la Propuesta 1 no ayuda bajo hiperpersistencia real, no hay caso operacional para la Propuesta 2 más agresiva. Si la Propuesta 1 ayuda pero aún subrepresenta la geometría del Nivel 3, la Propuesta 2 es el siguiente experimento natural, no el primer cambio de campo. Las Secciones 3–4 formalizan ambas construcciones; la Sección 5 fija la lógica de activación compartida; la Sección 8 establece la prioridad operacional.

---

## 2. Notación base compartida

El **incremento base legado** (sin Nivel 3) se define por

\[
\Delta t_k^{\mathrm{base}}
=
\begin{cases}
\delta^{-k_{\mathrm{run}}}\cdot\lvert\tau_s(k)\rvert\cdot\Delta t_0
  & \text{si }\lvert\tau_s(k)\rvert<\tau_{\mathrm{ch}},\\[4pt]
\Delta t_{\mathrm{out}}
  & \text{en otro caso (avance unitario o nulo, dependiente del \emph{pipeline}),}
\end{cases}
\tag{4}
\]

donde \(k_{\mathrm{run}}\) es la profundidad de la racha caótica actual (o un contador local acotado de renormalización). La compuerta \(g\) puede ser por tramos o sigmoidea; se retiene la forma genérica \(g(\tau_s)\in[-1,1]\).

**Normalización de excess³** (para estabilidad numérica entre conjuntos de datos):

\[
\widetilde{e}_3(k)
=
\frac{\mathrm{excess}^3(k)-\mu_{e,B}}{\sigma_{e,B}+\varepsilon},
\tag{5}
\]

con \((\mu_{e,B},\sigma_{e,B})\) estimados **exclusivamente** sobre una ventana basal \(B\) fijada *a priori* (o sobre un conjunto de calibración que no solape el evento de evaluación). \(\varepsilon>0\) es un estabilizador pequeño. Una alternativa basada en rangos (más robusta bajo colas pesadas) es

\[
\widetilde{e}_3^{\mathrm{rk}}(k)
=
2\cdot\widehat{F}_B\!\bigl(\mathrm{excess}^3(k)\bigr)-1\in[-1,1],
\tag{5'}
\]

donde \(\widehat{F}_B\) denota la función de distribución empírica en \(B\).

**Persistencia ordinal** (como en la literatura de RQA / hiperpersistencia):

\[
P(k)=\text{longitud de la racha actual con }\lvert\tau_s\rvert<\tau_{\mathrm{ch}}.
\tag{6}
\]

**Masa anidada del Nivel 3** (diagnóstica; no es la única vía de integración):

\[
f_3(k)
=
\frac{\alpha_3(\lambda)\,\Phi_3^\ast(k)}
{\sum_{\ell=1}^{3}\alpha_\ell(\lambda)\,\Phi_\ell^\ast(k)+\varepsilon}.
\tag{7}
\]

---

## 3. Propuesta 1 (conservadora): ganancia multiplicativa de superávit

Bajo la Propuesta 1, el avance base sigue determinado por \(\tau_s\), la compuerta \(g\) y el factor de estado, como en el *pipeline* legado. Φ₃ entra solo como factor de escala secundario sobre ese incremento ya decidido: cuando el superávit irreducible está ausente o estancado, \(\Gamma_3=1\) y el reloj no cambia; cuando el superávit está presente y cambia, \(\Gamma_3>1\) y el mismo paso base se estira. Fijar \(\beta=0\) es, por tanto, una ablación exacta: elimina el factor de superávit sin alterar el reloj primario.

### 3.1 Formulación

Las ecuaciones (1) y (4) se dejan estructuralmente inalteradas. Φ₃ entra únicamente como **factor de ganancia** \(\Gamma_3\ge 1\) (o \(\ge 0\) si se admite un régimen de frenado) aplicado al incremento ya filtrado por \(g\) y por el factor de estado:

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

### 3.2 Definición de \(\Gamma_3\)

Sea \(A_3(k)\in\{0,1\}\) la **compuerta de activación** del Nivel 3 (Sección 5). Se define

\[
\Gamma_3(k)
=
1
+
\beta\cdot A_3(k)\cdot\psi\!\bigl(\widetilde{e}_3(k)\bigr),
\tag{8}
\]

donde \(\beta\ge 0\) es un hiperparámetro de sensibilidad (rango por defecto \(\beta\in[0.25,1.0]\), fijado *a priori*) y \(\psi\) es un mapa monótono acotado, por ejemplo

\[
\psi(x)=\mathrm{softplus}(x)=\log\bigl(1+e^{x}\bigr),
\quad\text{o}\quad
\psi(x)=\max(0,x).
\tag{9}
\]

**Argumento de \(\psi\):**

| Modo | Argumento de \(\psi\) | Régimen pretendido |
|------|----------------------|-----------------|
| `level` (por defecto) | \(\lvert\widetilde{e}_3\rvert\) si forma absoluta; softplus con signo en otro caso | Magnitud elevada de superávit |
| `change` | \(\lvert\Delta\widetilde{e}_3\rvert\) (o primera diferencia con signo) | Reorganización con **disminución** del superávit (G1) |
| `both` | media de los argumentos de nivel y de cambio | Compromiso bajo dinámica mixta |

La forma **delta-absoluta** adoptada por defecto (consistente con G1, en la que el superávit puede disminuir) es

\[
\Gamma_3^{\mathrm{abs}}(k)
=
1
+
\beta\cdot A_3(k)\cdot\psi\!\bigl(\lvert\Delta\widetilde{e}_3(k)\rvert\bigr)
\quad\text{o}\quad
\psi\!\bigl(\lvert\widetilde{e}_3(k)-\widetilde{e}_3^{\mathrm{ref}}\rvert\bigr),
\tag{8'}
\]

donde \(\widetilde{e}_3^{\mathrm{ref}}\) es la mediana basal. El delta-absoluto privilegia el **cambio** del superávit sobre el nivel crónico: en tramos hiperpersistentes, excess³ puede permanecer elevado sin marcar una transición, mientras que la reorganización—incluidas algunas trayectorias G1—aparece a menudo como un *movimiento* del superávit (a veces un descenso). La implementación expone el interruptor de delta-absoluto y \(\texttt{psi\_mode}\in\{\texttt{level},\texttt{change},\texttt{both}\}\) para que la sensibilidad a esta elección permanezca transparente.

### 3.3 Modulación del peso de Φ₃

| Cantidad | Papel |
|----------|------|
| \(\mathrm{excess}^3(k)\) | Proxy continuo de Φ₃ (ecuación 3) |
| \(\widetilde{e}_3(k)\) o \(\lvert\Delta\widetilde{e}_3\rvert\) | Escala adimensional |
| \(A_3(k)\) | Suprime la activación trivial bajo hiperpersistencia |
| \(\beta\) | Intensidad global del canal (escalar único preespecificado) |
| \(\alpha_3(\lambda)\) (opcional) | Puede entrar en \(A_3\) o en un peso compuesto \(\beta_{\mathrm{eff}}=\beta\cdot\alpha_3(\lambda)/\alpha_{3,0}\) |

**Compatibilidad con la ecuación (2).** La Propuesta 1 no reemplaza el RECD anidado; define un mapa \(F\) sobre el *pipeline* legado. Opcionalmente, puede reportarse en paralelo

\[
\Delta\mathrm{RECD}^{\mathrm{nested}}(k)
=
\sum_{\ell=1}^{3}\alpha_\ell(\lambda)\,\Phi_\ell^\ast(k)
\]

y exigirse correlación positiva entre \(\Gamma_3(k)-1\) y \(f_3(k)\) en regímenes caóticos sintéticos.

**Contribución marginal de Φ₃ al reloj** (generalización de \(\rho_3\) de la Propuesta 2 a la Propuesta 1):

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

Esta cantidad soporta ablación y comparación directa con \(\rho_3\) bajo la Propuesta 2.

### 3.4 Consecuencias dinámicas predichas

1. **Aceleración selectiva.** En el régimen C con \(A_3=1\) y superávit elevado (o \(\lvert\Delta e_3\rvert\) grande), \(t_k\) avanza más rápidamente que el RECD base a igual \(\tau_s\).
2. **Ausencia de saltos discontinuos** cuando \(\psi\) y \(\widetilde{e}_3\) son suaves: el reloj permanece absolutamente continuo por tramos (solo cambia la pendiente local).
3. **Mejor discriminación precrítica.** En series cardíacas, si \(\Delta\mathrm{excess}^3\) precede a \(\tau_s\), \(\Gamma_3\) puede adelantar la acumulación de masa crítica y mejorar la anticipación en \(T_{\mathrm{RECD}}\).
4. **Ablación exacta.** Fijar \(\beta=0\) o \(A_3\equiv 0\) recupera exactamente el RECD legado.

### 3.5 Implementación (pseudocódigo)

```text
for k in time:
    tau = systemic_tau(window_k)
    e3  = excess3(window_k)          # 0.6/0.4 fijo
    e3n = normalize_vs_baseline(e3)
    dt  = base_interval(tau, run_depth)
    g   = gate(tau)
    a   = state_factor(state_k)      # C/D/T
    A3  = activation_level3(...)     # Sección 5
    Gamma = 1 + beta * A3 * softplus(e3n)   # o forma delta-absoluta
    t[k+1] = t[k] + dt * g * a * Gamma
```

El coste computacional es del mismo orden que la evaluación de excess³ por ventana y ya se incurre siempre que excess³ se calcula para alerta temprana.

---

## 4. Propuesta 2 (experimental): canal dual con compresión dependiente de la profundidad

La Propuesta 1 solo *escala* un paso ya fijado por \(\tau_s\). La Propuesta 2 permite que Φ₃ contribuya un componente aditivo del paso y que cambie la profundidad de renormalización de ese componente. El canal \(C_{12}\) es el avance relacional de pares de la construcción estándar; el canal \(C_3\) es tiempo discreto atribuible a superávit irreducible, comprimido de forma más agresiva cuanto más tiempo permanece activo el superávit. Esa geometría está más cerca, en espíritu, de la ecuación anidada (2), pero también es más fácil de sobreajustar y más difícil de reverse-ingeniar en código operacional. De ahí el estatus experimental: evaluar primero en sistemas sintéticos; no desplegar hasta que la Propuesta 1 haya mostrado beneficio de dominio.

### 4.1 Formulación

El avance del reloj se descompone en **dos canales aditivos**:

- **Canal relacional de pares** \(C_{12}\): gobernado por \(\tau_s\), \(P\), Φ₁ y Φ₂ (como en la construcción estándar).
- **Canal de superávit** \(C_3\): gobernado por excess³ y activo solo bajo los criterios estrictos de la Sección 5.

Cuando el canal 3 está activo, la **profundidad de renormalización** efectiva aumenta (compresión de Feigenbaum más fuerte), y pueden admitirse **saltos estructurales** acotados opcionales.

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
A_3(k)\cdot J\cdot\mathbf{1}\{\text{condición de salto}\}.
\end{aligned}
}
\tag{P2}
\]

### 4.2 Componentes

**Profundidad de superávit** (acumulador acotado, no un exponente libre):

\[
R_3(k+1)
=
\min\!\Bigl(
R_{\max},\;
\bigl(R_3(k)+1\bigr)\cdot A_3(k)
\Bigr),
\quad
R_3\leftarrow 0\text{ si }A_3=0.
\tag{10}
\]

Así, rachas sostenidas de Nivel 3 activo profundizan la compresión \(\delta^{-(\cdot)}\) de forma análoga a \(k_{\mathrm{run}}\) en el canal 12, pero **solo** cuando el superávit es no trivial.

**Amplitud del canal 3:**

\[
h_3(\widetilde{e}_3,f_3)
=
\eta\cdot\psi\!\bigl(\lvert\widetilde{e}_3\rvert\bigr)\cdot\bigl(1+\gamma_f f_3\bigr),
\tag{11}
\]

con \(\eta>0\), \(\gamma_f\ge 0\) preespecificados; por defecto \(\gamma_f=0\) si no se usa \(f_3\).

**Salto estructural (opcional; inicialmente desactivado):**

\[
\text{condición de salto}
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

\(J\ge 0\) es un tamaño de salto fijo o \(J=j_0\cdot\psi(\widetilde{e}_3)\). Bajo una restricción de suavidad, \(J=0\).

### 4.3 Modulación del peso de Φ₃

Bajo la Propuesta 2 el peso de Φ₃ no es un único escalar \(\beta\); entra a través de

1. la compuerta \(A_3\) (binaria o suave en \([0,1]\));
2. la magnitud \(h_3\);
3. la profundidad \(R_3\) (efecto no lineal vía \(\delta^{-R_3}\));
4. opcionalmente la masa anidada \(f_3\).

El Nivel 3 puede, por tanto, dominar el **régimen matemático** del reloj (irregularidad, saltos de escala), y no solo su pendiente local.

### 4.4 Consecuencias dinámicas predichas

1. **Bimodalidad temporal.** Intervalos gobernados solo por \(C_{12}\) (caos dominado por pares) frente a intervalos gobernados por \(C_{12}+C_3\) (caos con superávit), con distinta velocidad y rugosidad de \(T_{\mathrm{RECD}}\).
2. **Compresión jerárquica adicional** en rachas de Φ₃ activo: intervalos más cortos a medida que crece \(R_3\) (hasta \(R_{\max}\)).
3. **Saltos** (si \(J>0\)): eventos discretos del reloj alineados con transiciones de superávit—candidatos a *ticks* de Nivel 3 en aplicaciones de alerta temprana.
4. **Mayor robustez a la hiperpersistencia no estructurada.** Si \(A_3=0\) durante un núcleo hiperpersistente largo con excess³ estancado, el reloj no acumula contribución espuria de Φ₃; si excess³ se reorganiza dentro del núcleo, \(C_3\) se activa (complemento natural del RQA).

### 4.5 Relación con la ecuación anidada (2)

La Propuesta 2 puede interpretarse como una **realización no lineal** de la ecuación (2):

- \(C_{12}\) corresponde a los términos \(\alpha_1\Phi_1+\alpha_2\Phi_2\) tras la compuerta y la compresión de Feigenbaum;
- \(C_3\) corresponde al término \(\alpha_3\Phi_3^\ast\) con un calendario de renormalización independiente.

**Predicción de consistencia.** En mapas logísticos acoplados (precaos frente a caos), la fracción

\[
\rho_3
=
\frac{\sum_k\lvert\Delta t_k^{(3)}\rvert}
{\sum_k\bigl(\lvert\Delta t_k^{(12)}\rvert+\lvert\Delta t_k^{(3)}\rvert\bigr)}
\]

se espera que aumente en caos de forma análoga a \(f_3\) en el marco de 2026 (del orden de \(+0.25\) en valor absoluto bajo el protocolo de referencia, sujeto a reestimación).

---

## 5. Criterios endurecidos de activación del Nivel 3

**Objetivo.** Φ₃ influye en el reloj **solo** cuando hay superávit no trivial **y** el contexto de régimen es compatible.

En series tropicales de dengue y en muchos registros Holter, el sistema pasa una fracción grande del tiempo en la banda C (hiperpersistencia). Si \(A_3\) se activara siempre que \(\lvert\tau_s\rvert<\tau_{\mathrm{ch}}\), entonces \(\Gamma_3>1\) de forma casi continua: la ganancia dejaría de portar información sobre *transiciones* y se convertiría en un reescalado permanente del reloj. Comprobaciones sintéticas confirman el riesgo: una compuerta permisiva puede activarse en más de la mitad de una serie nula (Sección 6.3). La activación endurecida es, por tanto, necesaria para que Φ₃ no colapse en un sinónimo de la banda C.

Los criterios siguientes implementan cuatro requisitos: (A) contexto caótico o de aproximación; (B) superávit alto *y en movimiento*; (C) superávit no reducible a coincidencia por pares; (D) confirmación a dos escalas temporales para que un único pico ruidoso no abra el canal.

### 5.1 Compuerta primaria \(A_3(k)\)

Se fija \(A_3(k)=1\) si y solo si se cumplen **todas** las condiciones siguientes (versión estricta; la versión suave combina puntuaciones en \([0,1]\)):

**(A) Régimen caótico o de aproximación**

\[
\lvert\tau_s(k)\rvert<\tau_{\mathrm{ch}}
\quad\text{o}\quad
P(k)\ge P_{\mathrm{arm}}
\quad\text{o}\quad
\mathrm{state}_k\in\{\mathrm{C},\mathrm{T}\}.
\tag{A}
\]

\(P_{\mathrm{arm}}\) (por defecto 3) es menor que el umbral del núcleo hiperpersistente (\(P\ge 7\)).

**(B) Nivel de superávit y (B′) cambio (ambos exigidos por defecto)**

\[
\lvert\widetilde{e}_3(k)\rvert>\theta_e^{\mathrm{eff}}
\quad\text{y}\quad
\lvert\Delta\widetilde{e}_3(k)\rvert>\theta_{\Delta}.
\tag{B+B'}
\]

La condición de **cambio** es esencial: en G1 sintético, el superávit puede **disminuir** bajo un factor latente compartido; una compuerta solo de nivel fallaría o se activaría en el régimen incorrecto. Valores por defecto: \(\theta_e=1.25\) (unidades de \(z\)-score), \(\theta_{\Delta}=0.40\); se exige el cambio.

**Umbral adaptativo** (series ruidosas):

\[
\theta_e^{\mathrm{eff}}
=
\theta_e\cdot\bigl(1+\kappa\cdot\min(\mathrm{CV}_B,2)\bigr),
\tag{B_{\mathrm{adapt}}}
\]

con \(\mathrm{CV}_B=\sigma_B/(\lvert\mu_B\rvert+\varepsilon)\) estimado **solo** en la línea base y \(\kappa=0.5\) por defecto. Esta construcción reduce falsos positivos cuando excess³ basal es muy variable.

**(C) Fracción de sinergia residual**

En lugar de la razón bruta \(\mathrm{excess}^3/(\Phi_1+\Phi_2)\), se usa una **fracción residual aproximada** de la masa del Nivel 3:

\[
r_{\mathrm{syn}}(k)
=
\frac{s_B(k)}{s_B(k)+\Phi_1(k)+\Phi_2(k)+\varepsilon}
\in(0,1),
\qquad
r_{\mathrm{syn}}(k)>\theta_{\mathrm{res}},
\tag{C}
\]

donde \(s_B=\lvert\widetilde{e}_3\rvert\) (o softplus con signo). Por defecto \(\theta_{\mathrm{res}}=0.20\). Si Φ₁ y Φ₂ no están disponibles, puede sustituirse el proxy \(\Phi_1+\Phi_2\equiv 1\) (misma forma funcional; recalibrable). Opcionalmente, también puede exigirse \(f_3>\theta_f\).

**(D) Escala dual: detección corta y persistencia media**

\[
\begin{aligned}
\#\{j\in[k-L_s+1,k]:\text{(B) y (C)}\}&\ge L_{s,\min},\\
\#\{j\in[k-L_m+1,k]:\text{(A),(B),(C)}\}&\ge L_{m,\min}.
\end{aligned}
\tag{D}
\]

Valores por defecto: \(L_s=3\), \(L_{s,\min}=2\) (detección); \(L_m=7\), \(L_{m,\min}=4\) (persistencia del superávit). Ni un único pico ni una breve excursión ruidosa bastan.

**(E) Opcional — consenso RQA bajo hiperpersistencia**

En conjuntos de datos con núcleo hiperpersistente (SJU-3, DengAI San Juan):

\[
A_3^{\mathrm{RQA}}(k)
=
A_3(k)\cdot\mathbf{1}\{\mathrm{LAM}_{\mathrm{core}}(k)>\lambda_{\mathrm{LAM}}
\;\vee\;
\Delta\mathrm{TT}(k)>\theta_{\mathrm{TT}}\}.
\tag{E}
\]

### 5.2 Compuerta suave (valor operacional por defecto para la Propuesta 1)

\[
A_3^{\mathrm{soft}}(k)
=
\sigma\!\bigl(c_A+c_B+c_C+c_D-s_0\bigr)\in(0,1),
\tag{13}
\]

donde \(c_B\) es el **producto** de las puntuaciones de nivel y de cambio, \(c_C\) es una transformación logística de \(r_{\mathrm{syn}}\), \(c_D\) promedia las dos escalas temporales y \(s_0=3.25\) (desplazamiento logístico). Los valores suaves por debajo de \(0.25\) se fijan a cero para suprimir activación residual bajo la nula.

### 5.3 Reglas de exclusión

Φ₃ **no** debe activarse bajo ninguna de las condiciones siguientes:

- ocupación de todo el régimen C solo porque \(\lvert\tau_s\rvert<0.41\);
- un único pico de excess³ sin confirmación a escala dual (D);
- nivel elevado de excess³ **sin** cambio (bajo \(\lvert\Delta\widetilde{e}_3\rvert\))—característico de la hiperpersistencia «plana»;
- coincidencia puramente por pares: \(r_{\mathrm{syn}}\) bajo aun cuando \(\lvert\tau_s\rvert\) esté en la banda de caos;
- ventanas con \(d=2\): el canal 3 se desactiva y se reporta la inhabilitación;
- calibración de umbrales sobre el mismo evento usado para la evaluación (fuga de datos).

---

## 6. Diseño de validación y resultados

### 6.1 Principios

1. **Ablación primero.** La Propuesta 1 o la 2 se compara con el RECD base (\(\beta=0\) / \(A_3\equiv 0\)).
2. Los **nulos de reordenamiento de fase** se aplican a la estadística primaria \(\lvert\Delta T\rvert\) o al tiempo de anticipación, y no solo a excess³ aislado.
3. La **preregistración de hiperparámetros** (\(\beta,\theta_e,L_{\min},\ldots\)) precede a la inspección de etiquetas de brote o de fibrilación ventricular.
4. La **mejora de detección** (anticipación, precisión, tasa de falsas alarmas) se reporta por separado del **cambio en la geometría del reloj** (dimensión fractal de \(T\), rugosidad, \(\rho_3\)).

### 6.2 Diseño de la validación sintética

Los brazos sintéticos existen para responder preguntas que los datos reales no pueden aislar con limpieza. S0 pregunta: *¿permanece silenciosa la compuerta cuando no hay estructura verdadera de superávit?* S1 pregunta: *cuando la reorganización es conocida, ¿sigue la ganancia a la masa anidada aunque el superávit caiga?* S2 pregunta: *¿eleva el caos la contribución de Φ₃ respecto del precaos?* S3–S4 endurecen la especificidad frente al acoplamiento solo por pares y a la hiperpersistencia plana.

| Brazo | Diseño | Predicción primaria | Pregunta humana |
|-----|--------|--------------------|----------------|
| **S0** | Canales independientes / tipo G0 | \(A_3\) dura \(\approx 0\); tasa suave baja; \(\Delta T_{P1}\) no espurio | ¿La nula permanece nula? |
| **S1** | Factor latente + reorganización (G1; el superávit puede disminuir) | \(\lvert\Delta e_3\rvert\) impulsa \(A_3\); alta \(\mathrm{corr}(\Gamma_3-1,f_3)\) | ¿La activación por cambio captura la reorg. verdadera? |
| **S2** | Precaos frente a caos | \(\mathbb{E}[\Gamma_3]\), \(\rho_3\) y \(A_3\) elevados en caos | ¿Es el Nivel 3 selectivo para el caos? |
| **S3** | Solo acoplamiento por pares (G3) | Activación intermedia; no debe superar a S1 | Los pares solos no deben parecer Φ₃ |
| **S4** | Hiperpersistencia plana frente a reorganización | Discriminación vía (B′) y (D); (E) reduce falsas alarmas | Caos plano ≠ caos en reorganización |

**Métricas.** Tasa de \(A_3\) (suave \(>0.5\) y dura); \(T_{\mathrm{final}}\) bajo base / P1 / P2; media de \(\Gamma_3\); \(\rho_3\) (P2) y \(\rho_3^{\mathrm{marg}}\) (P1); \(\mathrm{corr}(\Gamma_3-1,f_3)\); robustez al ruido al 5–15 %. La \(A_3\) suave es la puntuación continua operacional usada dentro de \(\Gamma_3\); la \(A_3\) dura es la compuerta binaria de las tablas de anticipación/FAR—dos vistas de los mismos criterios, no dos teorías rivales.

### 6.3 Resultados sintéticos

Las corridas sintéticas emplean los valores por defecto de activación compartidos del Apéndice A.

| Brazo | A₃ suave>0.5 | A₃ dura | media \(\Gamma_3\) | \(\rho_3\) P2 | \(\rho_3^{\mathrm{marg}}\) P1 | corr(\(\Gamma-1,f_3\)) | \(\Delta T_{P1}\) |
|-----|-------------|---------|-------------------|---------------|-------------------------------|------------------------|------------------|
| **S0** | **0.003** | **0.000** | **1.015** | 0.016 | 0.01 | 0.02 | **+4.2** |
| **S1** | 0.230 | 0.200 | 1.893 | 0.201 | 0.18 | **0.988** | +1.9 |
| **S2 precaos** | 0.000 | 0.000 | 1.026 | 0.064 | 0.02 | −0.01 | +1.3 |
| **S2 caos** | 0.195 | 0.165 | **1.421** | **0.322** | 0.21 | **0.821** | ~0† |

†En caos, \(\Delta t^{\mathrm{base}}\) ya está comprimido al estilo Feigenbaum: el \(\Delta T\) absoluto es pequeño; \(\rho_3\) y \(\Gamma_3\) capturan la contribución de Φ₃.  
Las tablas numéricas completas y las series de \(T_{\mathrm{final}}\) usan semilla base \(=10\).

**Interpretación.**

1. **S0 (nula).** \(A_3\) dura \(=0\), tasa suave \(\approx 0{,}3\%\), media de \(\Gamma_3\approx 1{,}02\), \(\Delta T_{P1}\approx +4\) (\(\sim 1\%\) del reloj base). La compuerta endurecida respeta la nula. Una configuración más permisiva (sin requisitos de cambio de superávit ni de sinergia residual) elevó la media de \(A_3\) a \(\sim 0{,}55\) en la misma serie, lo que motiva el endurecimiento actual.
2. **S1 (latente / cambio).** Activación selectiva (\(\sim 20\)–\(23\%\)) y correlación casi unitaria entre \(\Gamma_3-1\) y \(f_3\). El canal Φ₃ se alinea con la masa anidada bajo reorganización verdadera, incluida una **disminución** del superávit.
3. **S2.** El régimen caótico eleva \(\Gamma_3\) (1,42 frente a 1,03) y \(\rho_3\) (0,32 frente a 0,06). El precaos no activa \(A_3\).
4. **Ruido (5–15 %).** Degradación gradual sin colapso del orden S0 ≪ S1 / S2-caos (figura del panel de robustez al ruido).

**Criterios de aceptación preespecificados.**

| Criterio | Resultado observado |
|-----------|-----------------|
| S0 \(A_3\) dura \(\lesssim 8\%\) | Cumplido (0,000) |
| S0 media de \(\Gamma_3\) cercana a 1 | Cumplido (1,015) |
| S2 caos \(\mathbb{E}[\Gamma_3]\) > precaos | Cumplido (1,421 > 1,026) |

En una serie de contraste con un *burst* de superávit superpuesto a un núcleo caótico, la tasa \(A_3>0{,}5\) alcanza \(\approx 0{,}95\) dentro del *burst* y cae a \(\approx 0{,}25\) en el núcleo sin *burst* (frente a \(\approx 0{,}72\) bajo una compuerta globalmente permisiva). La compuerta endurecida discrimina, por tanto, la reorganización local del caos plano.

### 6.4 Análisis empíricos emparejados (Holter y DengAI): límites del reloj legado

El diseño empírico es *emparejado*: el mismo núcleo de Propuesta 1 y el mismo \(\beta\) se ejecutan sobre registros Holter de la Sudden Cardiac Death Holter Database (SDDB) y la Normal Sinus Rhythm Database (NSRDB) de PhysioNet [4, 14] (segundos a horas, RR, pre-FV) y sobre series semanales clima–incidencia DengAI de San Juan/Iquitos [15] (picos de brote). Los sistemas no son físicamente similares; la comparación examina si los modos de *falla operacional* del reloj legado son específicos de dominio o genéricos.

Estas limitaciones son en gran medida genéricas entre dominios. Tanto las series Holter como las DengAI pasan la mayor parte de la ventana de evaluación en la banda C. Bajo la ecuación (4), rachas caóticas largas profundizan la compresión de Feigenbaum \(\delta^{-k_{\mathrm{run}}}\), de modo que \(\Delta t^{\mathrm{base}}\) colapsa hacia cero. Multiplicar una base casi nula por \(\Gamma_3>1\) sigue produciendo un paso casi nulo: **la ganancia no puede inflar un reloj que la construcción legada ya ha congelado.** Muchas filas Holter y DengAI muestran, por tanto, \(\Delta T\approx 0\) incluso cuando \(A_3\) o excess³ se mueven. La excepción (Iquitos 2004) es instructiva: la ocupación caótica cae a \(\approx 88\%\), reaparece \(\Delta t^{\mathrm{base}}\) activo y el \(\Delta T\) legado es \(+1{,}24\).

El diseño emparejado evalúa, por tanto, dos preguntas operacionales: si la \(A_3\) endurecida permanece selectiva bajo hiperpersistencia real (comportamiento de alarma), y bajo qué condiciones \(\Gamma_3\) puede desplazar el índice legado \(T\) (comportamiento del reloj).

La Propuesta 1 usa el mismo núcleo de activación y el mismo \(\beta\) en ambos dominios. Los tamaños muestrales son pequeños respecto de un estudio de cohorte completo (Sección 6.5). Los umbrales de \(A_3\) se fijaron *a priori* a partir de S0 sintético y de análisis de sensibilidad uno-a-uno, y **no** se reoptimizaron sobre etiquetas de fibrilación ventricular o de brote.

#### 6.4.1 Protocolo contrastivo

| | **Holter (cardiología)** | **DengAI (epidemiología)** |
|--|-------------------------|---------------------------|
| Datos | SDDB 30/31/35 + NSRDB 16265/16272 | Series de entrenamiento de San Juan e Iquitos; top-3 picos \(\ge\) P80, separación \(\ge 26\) semanas |
| Proxy / \(W\) / \(d_{\min}\) | \([z(\mathrm{RR}),z(\lvert\Delta\mathrm{RR}\rvert)]\), \(W{=}101\), paso 5, \(\theta_3{=}0.08\), \(d_{\min}{=}2\) | \([\mathrm{cases},T,\mathrm{precip},\mathrm{RH}]\), \(W{=}13\), paso 1, \(\theta_3{=}0.10\), \(d_{\min}{=}3\) |
| Eventos / controles | pre-FV frente a NSRDB | 40 semanas pre-pico (basal 13 + aproximación 12) frente a máximos interepidémicos \(<\) P60 |
| P1 / ablación | Activación endurecida; \(\beta\in\{0,\,0.5\}\) | idéntico |

**Figuras.** Series Holter pre-evento, tasas basal→aproximación y anticipación, y tasa de falsas alarmas; análogos DengAI con eje temporal semanal y picos de brote marcados (Apéndice D).

#### 6.4.2 Resultados por dominio

**Holter — eventos y controles**

| Rec | tipo | caos% | A₃ dura bas→apr | Γ₃ apr | ΔT legado | ΔT Holter† | Anticip. A₃ / e³ |
|-----|------|--------|-----------------|--------|-----------|------------|--------------|
| 30 | evento | 100% | 0.000 → 0.000 | 1.012 | ≈0 | +89 | — / 3,1 h |
| 31 | evento | 100% | 0.001 → 0.000 | 1.014 | ≈0 | +197 | — / 6,9 h |
| 35 | evento | 100% | 0.004 → 0.003 | 1.054 | ≈0 | +625 | 5,0 h / 8,0 h |
| 16265 | control | 100% | tasa 0.014 | 1.118 | ≈0 | +1402 | FAR ≈21,6/24h |
| 16272 | control | 100% | tasa 0.019 | 1.134 | ≈0 | +1491 | FAR ≈25,6/24h |

†**ΔT Holter** denota un reloj *diagnóstico* \(\Delta t=\Delta t_0\,g(\tau)\,\Gamma_3\) **sin** profundidad de Feigenbaum; **no** es el valor por defecto de la ecuación (1). Se reporta solo como contrafactual: el desplazamiento que \(\Gamma_3\) produciría si el intervalo base no estuviera comprimido a cero. La afirmación operacional sobre el \(\Delta T\) legado usa la construcción completa de la ecuación (4).  
**Agregados Holter.** Sensibilidad de \(A_3\) dura **1/3** frente a excess³ en \(z\) absoluto **3/3**; \(\Delta t^{\mathrm{base}}\) activo **\(\sim 0{,}1\%\)**.

**DengAI — brotes y controles**

| ID | tipo | Pico | caos% | A₃ dura bas→apr | Γ₃ apr | ΔT legado | Anticip. A₃ / e³ |
|----|------|------|--------|-----------------|--------|-----------|--------------|
| SJ-O1-1994 | brote | 461 | 100% | 0.00 → 0.00 | 1.11 | ≈0 | — / — |
| SJ-O2-1998 | brote | 329 | 98% | 0.00 → 0.00 | 1.03 | ≈0 | — / — |
| SJ-O3-2007 | brote | 170 | 100% | 0.07 → 0.23 | 1.40 | ≈0 | — / 4 sem |
| IQ-O1-2004 | brote | 116 | **88%** | 0.00 → 0.15 | 1.39 | **+1.24** | **11 sem** / 23 sem |
| IQ-O2-2008 | brote | 58 | 100% | 0.00 → 0.62 | 2.38 | ≈0 | 25 sem / 26 sem |
| IQ-O3-2008 | brote | 63 | 100% | 0.00 → 0.69 | 2.38 | ≈0 | 10 sem / 15 sem |
| controles (4) | interep. | — | 95–100% | tasa 0–0.24 | 1.12–1.56 | ≈0 | FAR media **1,62**/52sem |

**Agregados DengAI.** Sensibilidad de \(A_3\) dura **3/6** (todo Iquitos) frente a excess³ **4/6**; media de \(\Delta T\) legado **\(+0{,}207\)** (impulsada por IQ-2004); \(\Delta t^{\mathrm{base}}\) activo **\(\sim 7{,}3\%\)**; caos medio de brote **97,6 %**.

#### 6.4.3 Síntesis interdominio

| | **Holter** | **DengAI** | **Interpretación interdominio** |
|--|------------|------------|--------------------------------|
| Banda C → \(\Delta T\) legado | caos **100 %**; \(\Delta t^{\mathrm{base}}\) **\(\sim 0{,}1\%\)**; \(\Delta T\) **\(\approx 0\)** | caos **\(\sim 98\%\)**; \(\Delta t^{\mathrm{base}}\) **\(\sim 7\%\)**; \(\Delta T\) **\(\approx 0\)** salvo **IQ-2004 (\(+1{,}24\))** | La saturación en C no es específica de Holter. \(\Gamma_3\) desplaza \(T\) **solo si** \(\Delta t^{\mathrm{base}}\not\approx 0\). |
| Compuerta \(A_3\) / anticip. / FAR | dura \(\lesssim 0{,}02\); sens. **1/3** vs e³ **3/3**; FAR \(\sim\)**24**/24h | bas→apr en Iquitos; sens. **3/6** vs e³ **4/6**; FAR \(\sim\)**1,6**/52sem | (B)∩(D) restringen la activación; \(A_3\) es más estricta que excess³; la especificidad evento/brote queda por demostrar. |
| Ablación \(\beta{=}0\) | \(\max\lvert\Delta T\rvert=0\) | \(\max\lvert\Delta T\rvert=0\) | El canal Φ₃ es ablatable en ambos dominios. |

**Conclusiones interdominio.**

1. **La Propuesta 1 es implementable y auditable** en dos dominios empíricos con un núcleo computacional compartido y parámetros fijados *a priori*.
2. **La \(A_3\) endurecida funciona como compuerta de selectividad.** La hiperpersistencia del *régimen C* no implica hiperpersistencia de *alarmas* Φ₃. En Holter, la activación dura permanece escasa. En Iquitos, la activación discrimina basal de aproximación cuando superávit y persistencia a dos escalas están conjuntamente presentes.
3. **El reloj legado no es un vehículo universal de anticipación.** Bajo ocupación sostenida de la banda C, la compresión de Feigenbaum lleva \(\Delta t^{\mathrm{base}}\) hacia cero; la multiplicación por \(\Gamma_3\) deja entonces \(T\) inalterado. IQ-2004 ilustra el mecanismo condicional: caos 88 %, \(\Delta t^{\mathrm{base}}\) activo ≈24 %, \(\Delta T=+1{,}24\), anticipación de \(A_3\) de 11 semanas. En Holter, \(A_3\) suministra principalmente una **alarma condicionada** más que inflación de \(T\). El reloj sin profundidad de Feigenbaum se reporta solo como índice diagnóstico auxiliar.
4. **No se establece ni reducción de la tasa de falsas alarmas ni superioridad operacional.** Bajo los umbrales fijos usados, los controles se activaron con frecuencia igual o mayor que eventos o brotes. Los picos extremos de *conteo de casos* (San Juan 1994 y 1998) no activan \(A_3\) dura: el superávit ordinal multivariante no es reducible a la magnitud univariante de incidencia.

**Extensiones empíricas ulteriores** incluyen un reloj específico de dominio o una redefinición de la condición (A); análisis de sensibilidad del proxy en DengAI; una cohorte SDDB con \(N\ge 10\) y subrogados; SJU-3; y la condición RQA (E) una vez estabilizado el reloj de dominio.

### 6.5 Validación empírica ampliada

| Conjunto de datos | Objetivo de validación |
|---------|----------------------|
| **DengAI (extensión)** | Picos adicionales; subrogados; sensibilidad al proxy de covariables; umbral de brote |
| **SJU-3 (12 trampas)** | Efecto de Φ₃ sobre el reloj bajo hiperpersistencia de núcleo (\(\sim 69{,}6\%\) de ocupación) |
| **Holter SDDB (\(N\approx 10\) de alta calidad)** | Anticipación y FAR de cohorte; reloj de dominio frente a legado; subrogados |
| **Control negativo** | NSRDB completo; reordenamiento temporal de etiquetas; largos periodos basales DengAI |

**Protocolo de comparación (por evento).**

1. Calcular \(T^{\mathrm{base}}\), \(T^{(P1)}\) y (diagnóstico opcional) un reloj sin profundidad de Feigenbaum.
2. Definir alarmas sobre \(A_3\) dura y suave y, en paralelo, sobre el \(z\)-score absoluto de excess³.
3. Reportar anticipación, tasa de falsas alarmas y \(p\)-valores de reordenamiento de fase.
4. Ablación: \(\beta=0\); eliminación individual de (B), (C) o (D).

### 6.6 Criterios de éxito preespecificados

El **éxito operacional de la Propuesta 1** se declara si, en al menos dos de tres dominios (S2 sintético, dengue, cardiología),

1. la mediana de anticipación de \(T^{(P1)}\) es al menos la de \(T^{\mathrm{base}}\) con no inferioridad en falsas alarmas (\(+{\le}5\) puntos porcentuales absolutos), **o**
2. la tasa de falsas alarmas es significativamente menor a anticipación comparable, **y**
3. en S0, la tasa de activación de \(A_3\) está acotada y \(T^{(P1)}\) no exhibe superioridad espuria.

**Resultados respecto de estos criterios.** El criterio (3) se cumple en S0 sintético. Los criterios (1)–(2) no quedan satisfechos por los análisis empíricos emparejados de la Sección 6.4. Esos análisis sí establecen: (i) selectividad de \(A_3\) bajo hiperpersistencia real; (ii) dependencia del \(\Delta T\) legado respecto del escape de la banda C; (iii) ablación exacta \(\beta=0\); (iv) la especificidad a nivel de evento y de brote bajo umbrales fijos queda por demostrar.

El **éxito estructural de la Propuesta 2** exige, además, que \(\rho_3\) separe regímenes S2 de forma consistente con \(f_3\) anidada. La Propuesta 2 se evalúa solo en S2 sintético.

---

## 7. Riesgos y limitaciones

| Riesgo | Descripción | Mitigación |
|------|-------------|------------|
| **Doble conteo** | excess³ correlacionado con \(\tau_s\); Φ₃ puede no añadir información nueva al reloj | Condición (C); ablación; reportar \(I(\Gamma_3;\tau_s)\) |
| **Hiperpersistencia** | Activación casi continua bajo banda C crónica | (D)+(E); \(A_3\) sobre \(\Delta e_3\); (B)∩(D) (Sección 6.4) |
| **Feigenbaum / banda C** | \(\lvert\tau\rvert<\tau_{\mathrm{ch}}\) crónico congela \(\Delta t^{\mathrm{base}}\approx 0\); \(\Delta T\) legado no informativo | Reloj de dominio sin profundidad; redefinir (A); proxy no saturante; anticipación vía alarmas |
| **Sobreajuste de umbrales** | Multiplicidad de \(\theta\) | Valores por defecto fijos; sensibilidad uno-a-uno; no ajustar sobre eventos de prueba |
| **\(d=2\) degenerado** | Superávit de orden 3 mal definido | Desactivar canal 3 si \(d<3\) |
| **Coste de subrogados** | \(p\)-valores en línea para (B) son caros | \(z\)-score / FDA basal en línea; subrogados fuera de línea |
| **Signo de \(\Delta e_3\)** | G1 puede dar \(\Delta e_3<0\) bajo reorganización verdadera | Preferir delta-absoluto (8') para alerta temprana |
| **Inestabilidad de \(R_3\)** (P2) | Compresión exponencial demasiado agresiva | \(R_{\max}\) bajo (2–4); \(J=0\) al inicio |
| **Confusión de información parcial** | excess³ mal leído como átomo causal completo | Proxy híbrido preespecificado, no PID completa |
| **Dos formalismos** | Legado (1) frente a anidado (2) | Reportar ambos; P1 como puente mínimo |
| **Parámetros de salto** | \(J>0\) puede parecer *ad hoc* | Mantener \(J=0\) hasta cumplir S4 y criterios ampliados |

**Limitación conceptual.** excess³ no es una descomposición completa de información parcial. Su incorporación al reloj mejora la **dinámica del índice**; no convierte el proxy en una teoría axiomática de la información sinérgica. La interpretación causal del proceso generador de datos permanece deliberadamente cautelosa.

---

## 8. Prioridad operacional

### 8.1 Valor operacional por defecto (Propuesta 1)

**La Propuesta 1 (conservadora) se adopta como actualización por defecto del *pipeline* operacional**, con:

- la forma **delta-absoluta** (8') como ganancia por defecto;
- la compuerta suave (13) con condiciones (A)–(D);
- la extensión opcional (E) en conjuntos hiperpersistentes;
- \(\beta\) preespecificado (por ejemplo, \(0{,}5\)) y barrido de sensibilidad \(\beta\in\{0,0.25,0.5,1.0\}\).

El valor por defecto se motiva por cinco propiedades:

1. **Cierre dinámico con cambio estructural mínimo.** Φ₃ ya no queda confinado a un diagnóstico paralelo: modifica \(\Delta t_k\) de forma explícita y ablatable.
2. **Falseabilidad.** Fijar \(\beta=0\) recupera la construcción operacional estándar sin el canal Φ₃.
3. **Comportamiento controlado bajo hiperpersistencia.** Cuando \(A_3\) sigue el *cambio* del superávit y no la mera ocupación de la banda C, se limita la activación trivial.
4. **Factibilidad computacional.** La construcción es implementable sobre *pipelines* existentes de RECD anidado, dengue y cardiología a coste adicional \(O(1)\) una vez calculado excess³.
5. **Compatibilidad.** La propuesta es consistente con el RECD anidado (2) y con el RQA de seis modos (la ganancia Φ₃ puede entrar como modo adicional o peso del reloj, no como sustituto de LAM/TT).

Bajo banda C crónica, la compresión de Feigenbaum puede congelar \(\Delta t^{\mathrm{base}}\); \(\Gamma_3\) no puede entonces desplazar \(T\) hasta que la base se reabra. En ese régimen, \(A_3\) debe evaluarse como *alarma condicionada*, y puede considerarse un reloj de dominio sin profundidad (Sección 6.4, Sección 7). Los pesos 0,6/0,4 de excess³ permanecen fijos para no confundir efectos de reloj con el reajuste del proxy sobre los mismos eventos de evaluación.

### 8.2 Estatus de la Propuesta 2

La Propuesta 2 es una extensión de canal dual **experimental** y no es el valor operacional por defecto. La profundidad de canal dual y los saltos opcionales cambian la *forma* del tiempo discreto, no solo su escala. Esa construcción es útil para contrastar consistencia con \(f_3\) anidada, pero multiplica parámetros libres y dificulta localizar fallos en campo. La Propuesta 2 se considera, por tanto, solo después de que la Propuesta 1 muestre beneficio de dominio *y* la masa anidada \(f_3\) siga divergiendo de la geometría del reloj operacional (Sección 4; S2 sintético).

- **Estructura.** Canal dual \(C_{12}+C_3\), profundidad \(R_3\) y métrica \(\rho_3\) alineada con \(f_3\) anidada (evaluada en la suite sintética S2).
- **Alcance de la evaluación.** Solo sistemas sintéticos; \(J=0\) y \(R_{\max}=3\).
- **Condición para desarrollo ulterior.** Saltos y compresión más profunda se consideran solo después de que la Propuesta 1 demuestre beneficio de dominio bajo los criterios de la Sección 6.6.
- **Aplicaciones de vigilancia.** La Propuesta 2 no se aplica a despliegue epidemiológico o cardíaco hasta que se satisfagan esos criterios.

### 8.3 Prioridad relativa entre desarrollos afines

| Desarrollo | Prioridad relativa |
|-------------|-------------------|
| Integración de Φ₃ en la dinámica RECD (P1) | Prioridad operacional primaria |
| RQA adaptativo y comunidades de recurrencia cruzada | Paralela; se acopla vía condición (E) |
| Validación adicional fuera de muestra de excess³ | Informa umbrales de (B) |
| Descomposición ordinal completa de información parcial | Más largo plazo; independiente del despliegue de P1 |

### 8.4 Pasos empíricos abiertos

Las extensiones empíricas prioritarias incluyen: un análisis de cohorte SDDB con reloj específico de dominio; extensión DengAI con ensambles de subrogados [11]; SJU-3; y la condición RQA (E) [3, 13] una vez estabilizado el reloj de dominio en cardiología y dengue. Los valores numéricos por defecto compartidos figuran en el Apéndice A.

---

## 9. Conclusión

El trabajo previo sobre Tau Sistémico y Reloj Extramental Discreto ha establecido métricas relacionales ordinales y una construcción base de tiempo discreto [1, 5], excess³ como proxy continuo del Nivel 3 [2], evidencia Holter de reorganización ordinal pre-FV [4] y refinamiento basado en recurrencia bajo hiperpersistencia [3, 13]. La pregunta operacional no resuelta es cómo debe entrar Φ₃ en la construcción del índice \(t_k\) de la ecuación (1), permaneciendo a la vez consistente con la representación de masa anidada (2).

Desarrollamos dos respuestas complementarias porque la teoría no fuerza un único mapa. La **Propuesta 1** conserva el reloj legado y multiplica su incremento por una ganancia condicionada al superávit—el cambio más pequeño que hace a Φ₃ dinámico y ablatable. La **Propuesta 2** otorga a Φ₃ su propio canal y profundidad—la construcción necesaria para contrastar alineación estructural con la masa anidada, pero aún no justificada para uso de campo. Criterios de activación endurecidos compartidos impiden que la hiperpersistencia de la banda C convierta cualquiera de las dos construcciones en un reescalado permanente.

Los resultados principales son:

1. un diagnóstico estructural de la brecha entre el uso paralelo de Φ₃ y una contribución generativa al reloj operacional;
2. una **Propuesta 1** multiplicativa y ablatable adecuada a *pipelines* operacionales;
3. una **Propuesta 2** de canal dual con compresión dependiente de la profundidad (experimental; solo evaluación sintética);
4. **criterios de activación endurecidos** basados en cambio de superávit, sinergia residual, persistencia a dos escalas y \(\theta_e\) adaptativo;
5. **resultados sintéticos (S0–S2)** con \(A_3\) nula en S0, discriminación de caos frente a precaos y alto alineamiento \(\Gamma_3\leftrightarrow f_3\) en S1;
6. **análisis emparejados Holter y DengAI:** \(A_3\) limita la hiperpersistencia de alarmas; la compresión de Feigenbaum y la ocupación de la banda C restringen el \(\Delta T\) legado en ambos dominios salvo escape parcial (IQ-2004); la especificidad a nivel de evento y de brote bajo umbrales fijos queda por demostrar.

En síntesis, la Propuesta 1 es auditable e implementable entre dominios; la compuerta endurecida \(A_3\) controla con éxito la hiperpersistencia; el reloj legado avanza solo cuando hay escape parcial de la banda de caos; y la validación específica de dominio sigue siendo necesaria antes de cualquier afirmación operacional. El desplazamiento de \(T\) aún requiere escape de la banda C (o un reloj de dominio que no congele \(\Delta t^{\mathrm{base}}\)). La validación a escala de cohorte permanece como prerrequisito del despliegue.

excess³ se trata a lo largo del trabajo como proxy híbrido preespecificado y no como descomposición completa de información parcial. Φ₃ entra en el reloj únicamente a través de mapas \(F\) falseables y ablatables.

---

## Apéndice A — Parámetros por defecto

| Símbolo / campo | Por defecto | Notas |
|----------------|---------|-------|
| \(W\) sintético | 13 | Generadores S0–S2 |
| \(W\) DengAI | 13 | paso 1; \(\theta_3=0.10\) |
| \(W\) Holter (CCTP) | 101 | paso 5; \(\theta_3=0.08\) |
| \(m\) (Bandt–Pompe) | 3 | retardo 1 |
| \(\tau_{\mathrm{ch}}\) | 0.41 | umbral de caos |
| \(\tau_{\mathrm{st}}\) | 0.50 | umbral de coherencia fuerte |
| \(\delta\) | 4.6692016091 | constante de Feigenbaum |
| \(\beta\) (P1) | 0.5 | intensidad del canal |
| \(\psi\) | softplus | mapa monótono |
| modo \(\psi\) | `level` | o `change` / `both` |
| delta-absoluto | `True` | forma (8') |
| normalización | `zscore` | alternativa `rank` / `mad` |
| \(P_{\mathrm{arm}}\) | 3 | longitud del brazo de aproximación |
| \(\theta_e\) | 1.25 | umbral de nivel |
| \(\theta_{\Delta}\) | 0.40 | umbral de cambio |
| exigir cambio | `True` | (B′) |
| \(\theta_{\mathrm{res}}\) | 0.20 | sinergia residual; preespecificado vía S0 |
| \(L_s,L_{s,\min}\) | 3, 2 | escala corta |
| \(L_m,L_{m,\min}\) | 7, 4 | escala media |
| desplazamiento suave \(s_0\) | 3.25 | desplazamiento logístico |
| suelo suave | 0.25 | \(A_3^{\mathrm{soft}}<\mathrm{floor}\Rightarrow 0\) |
| \(\theta_e\) adaptativo | activo, \(\kappa=0.5\) | inflación por CV basal |
| \(d_{\min}\) | 3 (por defecto); **2 en Holter bivariado** | CCTP bivariado |
| \(R_{\max}\) (P2) | 3 | canal dual sintético |
| \(J\) (P2) | 0 | sin saltos |
| \(\eta\) (P2) | 0.35 | canal dual sintético |
| α_Syn, α_Surp | 0.6, 0.4 | fijos |

## Apéndice B — Relación con el formalismo anidado existente

La ecuación (2) del marco de 2026 [1] ya es una integración **linealmente ponderada** de Φ₃ en \(\Delta\mathrm{RECD}\). La presente construcción no redefine Φ₃; lo que hace es:

1. **acoplar** la estructura del Nivel 3 al incremento legado (1) usado en aplicaciones;
2. **condicionar** el peso a la evidencia de superávit (no solo a \(\lambda(\tau_s)\));
3. **especificar** activación, ablación y validación de modo que el canal sea científicamente auditable.

En notación unificada, la Propuesta 1 es el caso especial

\[
\Delta t_k
=
\Delta t_k^{\mathrm{base}}\,g\,\alpha\,
\bigl(1+\beta A_3\psi(\cdot)\bigr),
\]

mientras que la ecuación (2) es

\[
\Delta\mathrm{RECD}
=
\sum_\ell\alpha_\ell(\lambda)\Phi_\ell^\ast.
\]

Un *pipeline* completo puede reportar **ambos** índices: \(T^{\mathrm{legacy+P1}}\) para comparabilidad histórica y \(T^{\mathrm{nested}}\) para fracciones de masa \(f_\ell\).

## Apéndice C — Límites de alcance

Quedan fuera del presente análisis los temas siguientes:

- reformulación axiomática de información parcial de Syn/Surp;
- afirmaciones sobre la ontología del tiempo físico;
- optimización por búsqueda en rejilla de \(\beta\) sobre etiquetas de brote o de fibrilación ventricular;
- reemplazo del consenso RQA de seis modos (se complementa, no se elimina).

---

## Referencias

1. Padilla-Villanueva, J. (2026). *Systemic Tau and the RECD Framework: A Relational Theory of Hierarchical Ordinal Conjunctions and Critical Transitions in Complex Systems.* Zenodo. DOI: [10.5281/zenodo.21287252](https://doi.org/10.5281/zenodo.21287252).
2. Padilla-Villanueva, J. (2026). *excess³: a pre-specified continuous proxy for order-3 synergistic surplus — methods, Spanish introduction, and cross-domain notes.* Zenodo. DOI: [10.5281/zenodo.21385937](https://doi.org/10.5281/zenodo.21385937).
3. Padilla-Villanueva, J. (2026). *El Paradigma del Tau Sistémico y la Ley del Reloj Extramental Discreto en Sistemas Complejos (versión ilustrada).* Subtítulo: *Integración del Análisis de Recurrencia Cuantitativa (RQA) para la Caracterización de Hiperpersistencia.* Zenodo. DOI: [10.5281/zenodo.20576241](https://doi.org/10.5281/zenodo.20576241).
4. Padilla-Villanueva, J. (2026). *CCTP/SDDB: Systemic Tau and ordinal RECD before spontaneous ventricular fibrillation* (depósito compañero de código, series RR limpias, resultados y figuras del manuscrito *Context-Dependent Relational Reorganization of Heart Rate Dynamics Precedes Spontaneous Ventricular Fibrillation*). Zenodo. DOI: [10.5281/zenodo.21348295](https://doi.org/10.5281/zenodo.21348295).
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
15. DrivenData. (2017). *DengAI: Predicting disease spread* [conjunto de datos de competición; casos semanales de dengue y covariables climáticas de San Juan e Iquitos]. https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/
