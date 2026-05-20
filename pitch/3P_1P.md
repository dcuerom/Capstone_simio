# Estructura del Pitch — Panadería Supermercado
## "Dos palancas, una configuración ganadora"

> **Documento de diseño del entregable Pitch** (10–12 min · 10 slides).
> Pensado para que cada slide tenga **placeholders explícitos** que se completarán al cierre de los experimentos en SIMIO.
> **Audiencia**: Gerencia ejecutiva del supermercado.
> **KPI principal**: % de demanda satisfecha (Fill Rate) global y por SKU — objetivo 90%.

---

## 1. Diseño Experimental

### 1.1 Las dos palancas de decisión

| Eje | Palanca | Naturaleza | Niveles evaluados |
|---|---|---|---|
| **A** | Política de Producción | "¿Qué y cuándo lanzar?" | (1) Plan puro · (2) Plan + Reactivo (Híbrida) · (3) PULL puro (Kanban/ROP) |
| **B** | Dimensionamiento de Recursos | "¿Cuánta capacidad instalada?" | Mezcladoras {4·5·6} · Panaderos {8·9·10} · Hornos {2·4·6} · Manipuladores horno {3·4·5} |

> **Parámetro operativo fijo (no se varía)** — Política de secuencia de horno: **Fija F1→F2→F3**.
> Se adopta por defecto por su **predictibilidad operativa** (0 overhead decisional para el panadero, setups planificables, secuencia compatible con turnos), y se mantiene constante en todos los escenarios para aislar el efecto real de las palancas de decisión gerencial.

### 1.2 Estrategia experimental — narrativa de "embudo"

En lugar de presentar la matriz completa (12+ combinaciones), se siguen **2 bloques secuenciales**, donde el primer bloque cierra la decisión de política y la fija para el dimensionamiento de recursos. Esto convierte un diseño factorial en una historia clara para gerencia.

| Bloque | Variable que se mueve | Variables fijas | Slide |
|---|---|---|---|
| **1** | Política Producción (3 niveles) | Recursos = base teórica · Horno = Fija F1→F2→F3 | 7 |
| **2** | Recursos (OFAT, 3 niveles cada uno) | Política Producción = ganadora B1 · Horno = Fija F1→F2→F3 | 8 |

### 1.3 Configuración base (configuración mínima viable)

> Punto de partida del Eje C, derivado de `reporte_pre_modelacion.md` §6.4.

| Recurso | Cantidad base | Justificación analítica |
|---|---|---|
| Mezcladoras | **5** | Cuello de botella crítico (2.442 min/día, ventana 555 min → 88% util.) |
| Amasadoras | 3 | Dependiente del tiempo de amasado manual (~50% mezclado) |
| Mesas de formado | 3 | Paralelo a mezcladoras |
| Hornos | **2** | 1 basta en volumen (49% util.) pero 2 dan flexibilidad temporal |
| Panaderos | **9** | Turno único 06:00–15:15 (incluye amasado manual) |
| Manipuladores de horno | **4** | 2 por turno × 2 turnos (A: 06–15:15 · B: 12–21:15) |
| Ayudantes | 2 | 1 por turno × 2 turnos |
| Carros / Bandejas | 20–30 / 400–500 | Para reportar; no se varían en experimentos |

### 1.4 Configuración de corridas

- **Réplicas por escenario**: 50
- **Horizonte de simulación**: 1 día operativo (06:00 inicio producción → 21:00 cierre tienda)
- **Warm-up**: 0 (la pre-apertura 06:00–09:00 actúa como warm-up natural del inventario)
- **Total ejecutado de corridas**:
  - Bloque 1 (3 políticas de producción): 3 × 50 = **150**
  - Bloque 2 OFAT mezcladoras {4, 6}: 2 × 50 = **100**
  - Bloque 2 OFAT panaderos {8, 10}: 2 × 50 = **100**
  - Bloque 2 OFAT hornos {3, 4, 5, 6}: 4 × 50 = **200** (se añadieron 3 y 5 hornos para caracterizar mejor el codo)
  - Bloque 2 manipuladores {3, 5} con 4 hornos (combinado): 2 × 50 = **100** (tested with 4 hornos porque con 2 hornos el sistema está saturado y enmascara el efecto)
  - Campeón consolidado: ya incluido en B2 (Hibrido + 5 hornos)
  - **TOTAL = 650 corridas (13 escenarios × 50 réplicas)**

### 1.5 Métricas reportadas (todos los experimentos)

Por cada escenario × réplica se registrarán los siguientes KPIs (media e intervalo de confianza 95% sobre las 50 réplicas):

| Familia | KPI | Granularidad |
|---|---|---|
| **Servicio** | Quiebres de stock | Por SKU |
| **Servicio** | Kg no vendidos por quiebre | Por SKU y total |
| **Servicio** | % demanda satisfecha (fill rate) | Por SKU y global |
| **Producción** | Sobrantes al cierre (21:00) | Por SKU y total |
| **Producción** | Producción total | Por SKU (kg y batches) |
| **Producción** | Número de lotes producidos | Por SKU |
| **Utilización** | % uso de hornos | Por horno |
| **Utilización** | % uso de mezcladoras | Por máquina |
| **Utilización** | % uso de amasadoras | Por máquina |
| **Utilización** | % uso de panaderos | Por trabajador y promedio |

---

## 2. Storyboard Slide a Slide

> **Convención**:
> - `[PH]` = placeholder de dato a completar tras correr los experimentos.
> - Las visualizaciones sugeridas se describen para que el diseñador/Gamma las prepare con los datos del CSV de outputs.

---

### SLIDE 1 — Portada

**Título**: Dónde invertir y dónde no: rediseñando la panadería con simulación
**Subtítulo**: Optimización de capacidad y reglas de operación · Panadería Supermercado
**Pie**: Equipo · Universidad del Desarrollo · Capstone Simulación · Mayo 2026

**Visual**: imagen de panadería de supermercado + 2 íconos (engranaje · horno) anticipando las 2 palancas evaluadas.

**Notas de presentación**: 15 seg. Presentar equipo y dejar enganche: *"Hoy mostraremos exactamente dónde invertir y dónde no para resolver los quiebres de stock — con evidencia simulada sobre 650 corridas."*

---

### SLIDE 2 — El problema de negocio

**Mensaje clave**: *"El sistema actual pierde ventas justo cuando el cliente más quiere pan"*.

**Bullets**:
- Alto nivel de quiebres de stock en la sección panadería
- 8.200 kg/día distribuidos en 10 tipos de pan, **sin sustitución entre productos**: cada quiebre es una venta perdida
- La demanda no es plana: **35% del día se concentra en 2 horas** (18:00–20:00)
- Impacto en experiencia del cliente y pérdida de tráfico al supermercado completo

**Visual principal**: gráfico de barras del perfil de demanda horaria (tabla §3.4 del reporte):
- Eje X: horas 09:00–21:00
- Eje Y: kg/hora
- Resaltar barras 18:00–20:00 en rojo (1.451 y 1.417 kg/hr)
- Líneas horizontales del régimen Bajo (~450), Medio (~657)

**Visual secundario** (KPI card): "35% demanda en 17% del tiempo de operación"

**Notas**: 1 min. *"La operación atiende 12 horas, pero un tercio de la venta ocurre en 2. Cualquier falla de stock en esa ventana es la más cara."*

---

### SLIDE 3 — Objetivo del estudio y KPI

**Mensaje clave**: *"Queremos garantizar 90% de servicio con el mínimo recurso, no a cualquier costo"*.

**Bullets**:
- **Objetivo principal**: maximizar el porcentaje de demanda satisfecha (meta operativa **90% global**)
- **Restricción**: usar el mínimo recurso posible (mezcladoras, hornos, personas)
- **Preguntas a responder**:
  1. ¿Qué política de producción liberar?
  2. ¿Cuántos recursos instalar?
- **Exploración futura** (fuera del alcance de este estudio): variar la política de secuencia de horno para cerrar la brecha hacia el 95%.

**Tabla — KPIs evaluados**:

| KPI | Objetivo |
|---|---|
| % Demanda satisfecha (global y por SKU) | ≥ 90% |
| Kg no vendidos por quiebre | Minimizar |
| Sobrantes al cierre | Minimizar (evitar sobreproducción) |
| Utilización de recursos | 70–85% (no saturar ni desperdiciar) |

**Visual**: 4 cards con los KPIs principales.

**Notas**: 45 seg. Enfatizar el trade-off: *"Llegar al 100% es trivial si producimos sin límite — la gracia es llegar al 90% sin sobreproducir ni sobre-invertir."*

---

### SLIDE 4 — El sistema en una imagen

**Mensaje clave**: *"Producción multi-etapa → Horneado por familias → Inventario → Demanda estocástica. Dos puntos donde la gerencia decide."*

**Bullets**:
- 9 etapas productivas por lote (pesado → fermentación → horneado → enfriado → reposición)
- 3 familias de horneado **incompatibles** entre sí (14 / 18 / 21 min) + setup de 5 min al cambiar — secuencia operativa fija F1→F2→F3
- Demanda compuesta: llegada Poisson no homogénea × elección por hora × cantidad triangular

**Visual principal**: BPMN simplificado del flujo (versión reducida de `flujo/diagrama_bpmn_panaderia.md`) con 2 íconos destacados que marcan los puntos de decisión gerencial:
- 🎛️ **Decisión 1**: ¿Cuándo y qué lote liberar? (Política producción)
- 📦 **Decisión 2**: ¿Cuánta capacidad instalar? (Recursos)

> El **horneado** sigue una secuencia operativa fija (F1→F2→F3) que no es objeto de decisión gerencial en este estudio.

**Notas**: 1 min. Recorrer brevemente el flujo y plantar los 2 íconos que aparecerán en los slides 7 y 8.

---

### SLIDE 5 — Las 2 palancas y el diseño experimental

**Mensaje clave**: *"Probamos 3 políticas × N configuraciones de recursos, con 20 réplicas cada una y secuencia de horno fija"*.

**Visual principal**: matriz 2D / tabla resumen del diseño experimental:

| Eje | Niveles probados | Cantidad |
|---|---|---|
| 🎛️ Producción | Plan puro · Plan + Reactivo (Híbrida) · PULL puro | 3 |
| 📦 Recursos | Mezcladoras {4,5,6} · Panaderos {8,9,10} · Hornos {2,4,6} · Manipuladores {3,4,5} | OFAT |

> Parámetro fijo: secuencia de horno F1→F2→F3 (constante en todos los escenarios).

**Bullets**:
- Estrategia tipo "embudo": el Bloque 1 cierra la política de producción ganadora; el Bloque 2 dimensiona los recursos sobre esa política
- 20 réplicas por escenario → resultados con intervalo de confianza 95%
- Las 3 políticas de producción cubren un **espectro de reactividad**: 0% (Plan puro) → reactividad moderada cada 30 min (Híbrida) → 100% reactiva por ROP (PULL)
- Fijar la secuencia de horno en F1→F2→F3 elimina ruido experimental y refleja la práctica operativa real (predictibilidad y simplicidad para el panadero)

**Notas**: 45 seg. *"Concentramos el análisis en las dos decisiones de mayor impacto gerencial: qué política seguir y con qué capacidad."*

---

### SLIDE 6 — Punto de partida (Configuración base)

**Mensaje clave**: *"El cálculo analítico dice que la mezcladora sería la restricción; la simulación va a mostrar lo contrario."*

**Bullets**:
- Configuración mínima viable derivada del análisis de carga de recursos (§6.2 reporte pre-modelación)
- La mezcladora exige 2.442 min/día y la ventana operativa es 555 min: **necesita 5 unidades** (88 % de utilización teórica esperada)
- El horno se calculó con 295 min de 600 disponibles → **49 % utilización teórica con 1 horno**, pero se proyectan **2 hornos** por flexibilidad temporal
- Esta es la "base" sobre la cual variaremos en el Eje B (recursos)

**Tabla — Recursos base (teórico vs simulado con política Híbrida)**:

| Recurso | Cantidad base | % Util. teórica | % Util. simulada (50 réplicas) | Diagnóstico |
|---|---|---|---|---|
| Mezcladoras | 5 | 88 % | **31,6 %** | 🟢 Mucha holgura — sobredimensionada |
| Hornos | 2 | ~25 % | **87,0 %** | 🔴 **Saturado** — cuello de botella real |
| Panaderos | 9 | ~80 % | **54,6 %** | 🟢 Holgura — sobredimensionado |
| Manipuladores horno | 4 | ~25 % | **39,8 %** | 🟢 Holgura — bien dimensionado |

**Visual**: barras horizontales comparando "% util teórica" vs "% util simulada" por recurso, con el horno destacado en rojo.

**Notas**: 1 min. *"Acá tenemos la primera gran sorpresa del estudio: el cálculo analítico subestimó el horno (predicción 25 %, real 87 %) y sobreestimó la mezcladora (predicción 88 %, real 32 %). La simulación es la única forma de capturar el efecto dinámico de los setups de cambio de familia, los lotes batch y la concurrencia de demanda en peak. Sin este resultado, la operación habría invertido en la palanca equivocada."*

---

### SLIDE 7 — Eje A: ¿Cuál política de producción?

**Mensaje clave**: *"Plan Puro e Híbrida quedan empatadas en ~54 % de servicio; PULL pierde 4 puntos por reaccionar tarde. La política sola no resuelve el problema: el horno ya está saturado al 87 %."*

**Bloque experimental**:
- Variable: Política de Producción ∈ {Plan puro, Plan + Reactivo (Híbrida), PULL puro}
- Fijo: Recursos = base teórica (5 mezcladoras · 2 hornos · 9 panaderos · 4 manipuladores) · Secuencia horno = F1→F2→F3
- 3 escenarios × 50 réplicas = 150 corridas

**Lógica de cada política**:
- **Plan puro**: secuencia fija de lotes generada offline; sin reacción a inventario observado.
- **Plan + Reactivo (Híbrida)**: mismo plan base + revisor periódico que inyecta lotes de emergencia si proyecta déficit.
- **PULL puro**: sin plan a priori; cada SKU se reabastece cuando su inventario cae bajo su ROP (calculado en `analisis_eoq_rop.csv`).

**Visual principal**: gráfico de barras agrupadas
- Eje X: 10 SKUs (ordenados por demanda decreciente)
- Eje Y: % demanda satisfecha
- 3 series: Plan puro (gris) · Plan + Reactivo (azul) · PULL (naranja)
- Línea horizontal objetivo: 90%

```
% Servicio por SKU — Política Producción (base 2 hornos)
100% ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ (objetivo 90%)
 70% ┤  █ █     █ █                       Marraq/Hallu/MarraqInt → Plan/Híbrida
 50% ┤  █ █ ▓   █ █ ▓   █   █ ▓ █         PULL recupera en SKUs de baja demanda
 30% ┤              █           ▓   ▓
 10% ┤              █                     Dobladita/Amasado: < 16 % con Plan/Híbrida
     └─ Marraq Hallu MarrIn HalIn HotDog Ciab Bague Dobl Boc Amas
        ▒ Plan puro · █ Híbrida · ▓ PULL
```

**KPI cards laterales (resultados reales — 50 réplicas)**:

| KPI | Plan puro | Plan + Reactivo (Híbrida) | PULL |
|---|---|---|---|
| **Fill rate global** | 53,73 % | **54,24 %** ← ganadora | 50,20 % |
| Fill rate mínimo (peor SKU) | 14,04 % (Dobladita) | 14,99 % (Amasado) | 29,50 % (Dobladita) |
| Kg no vendidos | 3.804,7 kg | **3.763,4 kg** | 4.095,3 kg |
| Personas no atendidas | 2.033 | **1.995** | 2.174 |
| Sobrantes 21:00 | 347,9 kg | 311,6 kg | 763,4 kg |
| Lotes producidos | 68 | 68 | 71 |
| Util. horno | 87,0 % | 87,0 % | 86,9 % |
| Util. mezcladora | 30,3 % | 31,6 % | 20,3 % |
| Util. panaderos | 52,7 % | 54,6 % | 39,0 % |

**Tabla de respaldo — % Servicio por SKU (10 productos)**:

| SKU | Plan puro | Plan + Reactivo | PULL | Mejor |
|---|---|---|---|---|
| Marraqueta | 70,8 % | 71,1 % | 52,0 % | Híbrida |
| Hallulla | 66,0 % | 63,1 % | 50,6 % | Plan puro |
| Marraqueta Integral | 68,5 % | 68,3 % | 51,9 % | Plan puro |
| Hallulla Integral | 14,7 % | 35,3 % | 38,6 % | PULL |
| Pan Hot Dog | 61,6 % | 55,5 % | 60,5 % | Plan puro |
| Ciabatta | 38,2 % | 36,1 % | 48,9 % | PULL |
| Baguette | 42,6 % | 34,1 % | 42,4 % | Plan puro |
| Dobladita | 14,0 % | 25,9 % | 29,5 % | PULL |
| Bocado de Dama | 31,9 % | 30,6 % | 36,7 % | PULL |
| Amasado | 15,0 % | 15,0 % | 58,3 % | PULL |

**Mensaje de cierre**: *"Híbrida gana el global por margen estrecho (54,24 % vs 53,73 % de Plan Puro y 50,20 % de PULL). Se adopta para el Bloque 2. **Observación crítica**: las 3 políticas tienen el horno saturado al 87 % — la política sola no permite superar el 55 % de servicio. La capacidad instalada es la palanca real."*

**Notas**: 1 min 15 seg. Marco narrativo: las 3 políticas representan un **espectro de reactividad** (0 % → 100 %). El resultado revela un cuello de botella estructural: con solo 2 hornos saturados al 87 %, ninguna política puede superar el ~54 % de servicio. PULL pierde 4 puntos porque acumula sobrantes (763 kg, 2,4× la base) al no anticipar el peak y queda corto en SKUs de alta rotación. La elección de Híbrida es marginal pero válida para sostener la comparación de recursos en B2.

---

### SLIDE 8 — Eje B: ¿Cuántos recursos instalar?

**Mensaje clave**: *"El horno es el único cuello de botella real. Mezcladoras, panaderos y manipuladores ya están sobredimensionados — la inversión debe focalizarse en hornos."*

**Bloque experimental** (OFAT — One Factor At a Time, sobre Híbrida):
- 4 recursos evaluados (mezcladoras, panaderos, hornos, manipuladores), con puntos extra en hornos {3, 5} para resolver el codo
- Fijo: Política Producción = Híbrida · Secuencia horno = F1→F2→F3
- 10 escenarios × 50 réplicas = 500 corridas (sumadas al base ya cubierto en B1)

**Visual principal**: 4 mini-gráficos en grilla 2×2 (datos reales del experimento):

```
Mezcladoras {4·5·6}              Panaderos {8·9·10}
   ↑ Fill (%)                       ↑ Fill (%)
 60% ┤  ●──●──●                   60% ┤  ●──●──●
 54% │  ··········                54% │  ··········    ← objetivo 90%
 50% ┤                            50% ┤
     └─  4   5   6                    └─  8   9  10
     [54,24] [54,24] [54,24]          [54,24] [54,24] [54,54]
     ⇒ Sin sensibilidad             ⇒ Sin sensibilidad

Hornos {2·4·6}                    Manipuladores {3·4·5}*
   ↑ Fill (%)                       ↑ Fill (%)
 90% ┤ ─ ─ ─ ─ ─ ─ ─ ─  ← 90%    90% ┤ ─ ─ ─ ─ ─ ─ ─ ─  ← 90%
 85% ┤                ●           80% ┤  ●──●──●
 80% ┤            ●                   │
 70% ┤                            54% ┤  ··········    (base 2 hornos)
 54% ┤  ●                             └─  3   4   5
     └─  2   4   6                    [79,5] [79,6] [79,6]
     [54,24] [79,60] [85,40]      *medidos con 4 hornos
     ⇒ Codo entre 4 y 5 hornos    ⇒ Sin sensibilidad
```

**Tabla — Sensibilidad por recurso (NvlServ global)**:

| Recurso (variando) | Nivel bajo | Nivel base | Nivel alto | Δ máximo | Diagnóstico |
|---|---|---|---|---|---|
| Mezcladoras | 4 → 54,24 % | **5 → 54,24 %** | 6 → 54,24 % | **0 pts** | 🟢 Sobredimensionada — no es restricción |
| Panaderos | 8 → 54,24 % | **9 → 54,24 %** | 10 → 54,54 % | **+0,3 pts** | 🟢 Sobredimensionado — no es restricción |
| Manipuladores (con 4 hornos) | 3 → 79,52 % | **4 → 79,60 %** | 5 → 79,60 % | **+0,08 pts** | 🟢 Sobredimensionado — no es restricción |
| **Hornos** | 2 → 54,24 % | 4 → 79,60 % | 6 → 85,40 % | **+31,2 pts** | 🔴 **Único cuello de botella** |

**Tabla — Curva fina de Hornos** (incluye puntos extra para identificar el codo):

| # Hornos | NvlServ | Δ vs anterior | Util. horno | Util. mezc. | Kg perdidos | Ventas (kg) | Lotes |
|---|---|---|---|---|---|---|---|
| 2 (base) | 54,24 % | — | 87,0 % | 31,6 % | 3.763 | 4.458 | 68 |
| 3 | 71,08 % | +16,84 pts | 86,8 % | 31,6 % | 2.379 | 5.843 | 102 |
| 4 | 79,60 % | +8,52 pts | 85,5 % | 31,6 % | 1.678 | 6.543 | 135 |
| **5 (codo)** | **85,24 %** | **+5,64 pts** | **78,1 %** | **31,7 %** | **1.214** | **7.007** | **158** |
| 6 | 85,40 % | +0,16 pts | 65,1 % | 31,7 % | 1.201 | 7.021 | 159 |

**Mensaje de cierre**: *"El codo de rendimiento está en **5 hornos** (85,24 % de servicio con 78 % de utilización). Pasar a 6 aporta solo 0,16 puntos y deja el horno al 65 %. La mezcladora, los panaderos y los manipuladores ya están en su nivel óptimo en la base teórica."*

**Notas**: 1 min 30 seg. Este slide aterriza la conclusión más importante del estudio: **el problema no es el plan ni el personal, es el horno**. Para llegar al 90 % desde el 85,24 % alcanzado con 5 hornos, la línea de exploración futura es ajustar la **política de secuencia de horno** (actualmente fija en F1→F2→F3) para reducir los setups de cambio de familia.

---

### SLIDE 9 — Configuración ganadora

**Mensaje clave**: *"La combinación Híbrida + 5 hornos eleva el servicio del 54 % al 85 % (+31 puntos) y reduce los quiebres en un 68 %, manteniendo la mezcladora y el personal en su nivel base."*

**Tabla resumen del escenario campeón**:

| Dimensión | Base mínima viable | **Campeón** |
|---|---|---|
| Política producción | Híbrida | **Híbrida** (sin cambios) |
| Secuencia horno (fija) | F1→F2→F3 | F1→F2→F3 |
| Mezcladoras | 5 | 5 (sin cambios) |
| Panaderos | 9 | 9 (sin cambios) |
| **Hornos** | **2** | **5 (+3 unidades)** |
| Manipuladores horno | 4 | 4 (sin cambios) |
| Hora inicio operación | 06:00 | 06:00 |

**KPIs del escenario campeón (50 réplicas)**:

| KPI | Base (2 hornos) | **Campeón (5 hornos)** | Δ absoluto | Δ relativo |
|---|---|---|---|---|
| Fill rate global | 54,24 % | **85,24 %** | +31,0 pts | +57 % |
| Fill rate mínimo (peor SKU) | 14,99 % (Amasado) | **64,55 %** (Dobladita) | +49,6 pts | +331 % |
| Kg no vendidos | 3.763 kg | **1.214 kg** | −2.549 kg | **−68 %** |
| Personas no atendidas | 1.995 | **634** | −1.361 | **−68 %** |
| Sobrantes 21:00 | 312 kg | 2.509 kg | +2.197 kg | — (atender peak requiere stock) |
| Ventas totales | 4.458 kg | **7.007 kg** | +2.549 kg | **+57 %** |
| Lotes producidos | 68 | 158 | +90 lotes | +132 % |
| Util. horno | 87 % | **78 %** | −9 pts | (deja margen para varianza) |
| Util. mezcladora | 32 % | 32 % | 0 pts | (sigue holgada) |
| Util. panaderos | 55 % | 56 % | +1 pt | (sigue holgado) |

**Visual de utilización del campeón** (barras horizontales):
```
Util. recursos — Hibrido + 5 hornos
Horno       │██████████████░░░░░░│ 78 %  ← saturación útil
Panaderos   │██████████░░░░░░░░░░│ 56 %
Manipulad.  │█████████░░░░░░░░░░░│ 56 %
Mezcladora  │██████░░░░░░░░░░░░░░│ 32 %  ← amplia holgura
```

**Mensaje de cierre**: *"El cuello de botella se desplaza del horno (87 % → 78 %) hacia ninguno: el sistema queda con margen en todos los recursos, listo para absorber crecimiento de demanda."*

**Notas**: 1 min. El cambio CAPEX es focalizado (+3 hornos), no transversal: no se necesitan más mezcladoras, panaderos ni manipuladores. *"El diagnóstico identifica exactamente dónde invertir y dónde no — el resto del personal y maquinaria ya está bien dimensionado."*

---

### SLIDE 10 — Impacto esperado y recomendación

**Mensaje clave**: *"+3 hornos llevan el servicio del 54 % al 85 % y recuperan 2.549 kg/día de venta. La política sola no basta; el diagnóstico identifica con precisión dónde invertir y dónde no."*

**Bullets — Impacto cuantificado**:
- ↑ **Nivel de servicio** de **54,24 %** a **85,24 %** global (+31 puntos)
- ↓ **Kg perdidos** de **3.763 kg** a **1.214 kg** (**−68 %** reducción)
- ↓ **Personas no atendidas** de **1.995** a **634** (**−68 %** reducción)
- ↑ **Ventas recuperadas** de **4.458 kg** a **7.007 kg** (+2.549 kg/día, **+57 %**)
- ↑ **Uso eficiente de recursos**: horno pasa de **saturado (87 %)** a **útil (78 %)**, dejando margen para varianza
- ✅ **CAPEX focalizado**: solo +3 hornos. Mezcladoras, panaderos y manipuladores quedan en su nivel base (sin inversión adicional)

**Recomendación operativa (3 acciones)**:
1. **Mantener política Híbrida** (Plan + Reactivo) para liberación de lotes — gana el global por margen estrecho y opera bien con cualquier dimensionamiento
2. **Escalar a 5 hornos** (incremento de +3 sobre la base de 2): es el punto óptimo del codo de retorno; pasar a 6 aporta solo 0,16 pts adicionales
3. **No invertir** en mezcladoras, panaderos ni manipuladores adicionales — el OFAT muestra que ya están sobredimensionados

**Próximos pasos sugeridos**:
- **Cerrar la brecha 85 % → 90 %**: explorar políticas alternativas de **secuencia de horno** (priorizar familia con menor stock, agrupar lotes para reducir setups) — línea de trabajo del próximo ciclo
- Piloto controlado de 2 semanas con la configuración recomendada
- Re-evaluación si la demanda crece >10 % o cambia el mix de productos
- Extensión del modelo a otros locales con perfil de demanda similar

**Visual**: barra de "antes vs después" con los 3 KPIs principales (servicio, kg perdidos, ventas) + ícono de horno con badge "+3".

**Notas**: 1 min 30 seg. Cerrar con: *"El estudio entrega dos certezas: la política existente es razonable, y la inversión correcta es focalizada en hornos — todo lo demás ya está bien. Cerrar al 90 % es la siguiente conversación, y ya sabemos por dónde."*

---

## 3. Anexo A — Matriz Maestra de Escenarios

Total: 13 escenarios distintos × 50 réplicas = **650 corridas**.

> Secuencia de horno fija en todos los escenarios: **F1→F2→F3**. Ganadora B1 = **Híbrida** (54,24 %). Campeón = **E10 (Hibrido + 5 hornos)** = 85,24 %.

| ID | Bloque | Política Producción | Mezcl. | Panad. | Hornos | Manip. | NvlServ | Quiebre kg |
|---|---|---|---|---|---|---|---|---|
| E01 | B1 | Plan puro | 5 | 9 | 2 | 4 | 53,73 % | 3.805 |
| E02 | B1 | **Híbrida** ← ganadora | 5 | 9 | 2 | 4 | **54,24 %** | **3.763** |
| E03 | B1 | PULL puro | 5 | 9 | 2 | 4 | 50,20 % | 4.095 |
| E04 | B2 | Híbrida | **4** | 9 | 2 | 4 | 54,24 % | 3.763 |
| E05 | B2 | Híbrida | **6** | 9 | 2 | 4 | 54,24 % | 3.763 |
| E06 | B2 | Híbrida | 5 | **8** | 2 | 4 | 54,24 % | 3.763 |
| E07 | B2 | Híbrida | 5 | **10** | 2 | 4 | 54,54 % | 3.738 |
| E08 | B2 | Híbrida | 5 | 9 | **3** | 4 | 71,08 % | 2.379 |
| E09 | B2 | Híbrida | 5 | 9 | **4** | 4 | 79,60 % | 1.678 |
| **E10** | B2 | Híbrida | 5 | 9 | **5** | 4 | **85,24 %** | **1.214** ← **Campeón** |
| E11 | B2 | Híbrida | 5 | 9 | **6** | 4 | 85,40 % | 1.201 |
| E12 | B2 | Híbrida | 5 | 9 | 4 | **3** | 79,52 % | 1.685 |
| E13 | B2 | Híbrida | 5 | 9 | 4 | **5** | 79,60 % | 1.678 |

> **Notas sobre el diseño**:
> - La base de recursos {Mezcl.=5, Panad.=9, Hornos=2, Manip.=4} se cubre con cada política en B1 (E01–E03).
> - Se añadieron escenarios extra con **3 y 5 hornos** (E08, E10) para caracterizar con mayor resolución el codo de retorno (queda entre 4 y 5 hornos).
> - Las variaciones de **manipuladores se midieron con 4 hornos** (E12, E13) — con 2 hornos el sistema está saturado y enmascararía el efecto del recurso.
> - El campeón consolidado (E10) ya está incluido como uno de los escenarios B2 — no requiere corrida adicional.

---

## 4. Anexo B — Plantilla CSV de resultados

Los resultados ya están consolidados en `pitch/ResultsExport.csv` (export directo de SIMIO, 50 réplicas por escenario). Notas de interpretación:

**Mapeo de columnas (validado contra sumatorias y NvlServ)**:
- `NivelServicioPct_ExperimentResponse` → % servicio global del escenario
- `QuiebreTotalKg_ExperimentResponse` → kg perdidos por quiebre (total escenario)
- `InventarioFinal_ExperimentResponse` → kg sobrantes al cierre
- `QuiebresPorPersona_ExperimentResponse` → # personas no atendidas (total escenario)
- `NvlServ{1..10}` → % servicio por SKU (1=Marraqueta, 2=Hallulla, 3=Marraqueta Integral, 4=Hallulla Integral, 5=Pan Hot Dog, 6=Ciabatta, 7=Baguette, 8=Dobladita, 9=Bocado de Dama, 10=Amasado)
- `Inv{1..10}` → **kg perdidos por SKU** (las etiquetas `Inv` y `QuiebreKg` están invertidas en el export: la suma de `Inv{N}` coincide con `QuiebreTotalKg`)
- `QuiebreKg{1..10}` → **inventario final por SKU** (suma coincide con `InventarioFinal`)
- `QuiebrePer{1..10}` → # personas no atendidas por SKU
- `Lotes{1..10}` → # lotes producidos por SKU

**Mapeo de `PropPoliticaProduccion_ExperimentControl`**:
- 0 = Híbrida (Plan + Reactivo)
- 1 = Plan puro
- 2 = PULL puro

> Secuencia de horno: F1→F2→F3 (fija — `PropPoliticaSecuenciaHorno_ExperimentControl=1` en todos los escenarios).

---

## 5. Notas finales para producción del pitch

- **Tono**: ejecutivo, no académico. Cada slide debe poder leerse en 30 segundos sin explicación.
- **Datos visibles**: priorizar gráficos sobre tablas; los datos finos van en anexo/respaldo.
- **Color**: usar paleta consistente entre slides (1 color por política de producción, 1 paleta secuencial para los niveles de recursos, 1 color "alerta" para quiebres).
- **Tiempo objetivo**: 10–12 min con margen de Q&A. Distribución sugerida:
  - Slides 1–6 (contexto y diseño): 4 min
  - Slides 7–8 (resultados de las 2 palancas): 3–4 min
  - Slides 9–10 (campeón e impacto): 2–3 min
