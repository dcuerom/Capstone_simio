# Estructura del Pitch — Panadería Supermercado
## "Tres palancas, una configuración ganadora"

> **Documento de diseño del entregable Pitch** (10–12 min · 11 slides).
> Pensado para que cada slide tenga **placeholders explícitos** que se completarán al cierre de los experimentos en SIMIO.
> **Audiencia**: Gerencia ejecutiva del supermercado.
> **KPI principal**: % de demanda satisfecha (Fill Rate) global y por SKU.

---

## 1. Diseño Experimental

### 1.1 Las tres palancas de decisión

| Eje | Palanca | Naturaleza | Niveles evaluados |
|---|---|---|---|
| **A** | Política de Producción | "¿Qué y cuándo lanzar?" | (1) Plan puro · (2) Plan + Reactivo (Híbrida) · (3) PULL puro (Kanban/ROP) |
| **B** | Política de Secuencia de Horno | "¿Qué hornear primero?" | (1) Menor stock en sala · (2) Mayor demanda esperada · (3) Fija F1→F2→F3 · (4) Híbrida (stock bajo + demanda) |
| **C** | Dimensionamiento de Recursos | "¿Cuánta capacidad instalada?" | Mezcladoras {4·5·6} · Panaderos {8·9·10} · Hornos {1·2·3} · Manipuladores horno {3·4·5} |

### 1.2 Estrategia experimental — narrativa de "embudo"

En lugar de presentar la matriz completa (24+ combinaciones), se siguen **3 bloques secuenciales**, donde cada bloque cierra una decisión y fija esa variable para el siguiente. Esto convierte un diseño factorial en una historia clara para gerencia.

| Bloque | Variable que se mueve | Variables fijas | Slide |
|---|---|---|---|
| **1** | Política Producción (3 niveles) | Recursos = base teórica · Horno = Fija F1→F2→F3 | 7 |
| **2** | Política Horno (4 niveles) | Recursos = base teórica · Producción = ganadora B1 | 8 |
| **3** | Recursos (OFAT, 3 niveles cada uno) | Política Producción = ganadora B1 · Política Horno = ganadora B2 | 9 |

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

- **Réplicas por escenario**: 20
- **Horizonte de simulación**: 1 día operativo (06:00 inicio producción → 21:00 cierre tienda)
- **Warm-up**: 0 (la pre-apertura 06:00–09:00 actúa como warm-up natural del inventario)
- **Total estimado de corridas**:
  - Bloque 1: 3 × 20 = **60**
  - Bloque 2: 3 × 20 = **60** (la política Fija F1→F2→F3 ya fue corrida en B1, se reutiliza)
  - Bloque 3 (OFAT con 4 recursos × 3 niveles, excluyendo el base ya corrido): 8 × 20 = **160**
  - Escenario campeón consolidado: 1 × 20 = **20**
  - **TOTAL ≈ 300 corridas**

### 1.5 Métricas reportadas (todos los experimentos)

Por cada escenario × réplica se registrarán los siguientes KPIs (media e intervalo de confianza 95% sobre las 20 réplicas):

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

**Título**: Política antes que CAPEX: rediseñando la panadería con simulación
**Subtítulo**: Optimización de capacidad y reglas de operación · Panadería Supermercado
**Pie**: Equipo · Universidad del Desarrollo · Capstone Simulación · Mayo 2026

**Visual**: imagen de panadería de supermercado + 3 íconos (engranaje · horno · personas) anticipando las 3 palancas.

**Notas de presentación**: 15 seg. Presentar equipo y dejar enganche: *"Hoy mostraremos que la gerencia tiene tres palancas para resolver los quiebres de stock — y solo una requiere comprar equipos"*.

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

**Mensaje clave**: *"Queremos garantizar 95% de servicio con el mínimo recurso, no a cualquier costo"*.

**Bullets**:
- **Objetivo principal**: maximizar el porcentaje de demanda satisfecha (≥ 95% por SKU)
- **Restricción**: usar el mínimo recurso posible (mezcladoras, hornos, personas)
- **Preguntas a responder**:
  1. ¿Qué política de producción liberar?
  2. ¿En qué orden hornear cuando compiten lotes?
  3. ¿Cuántos recursos instalar?

**Tabla — KPIs evaluados**:

| KPI | Objetivo |
|---|---|
| % Demanda satisfecha (global y por SKU) | ≥ 95% |
| Kg no vendidos por quiebre | Minimizar |
| Sobrantes al cierre | Minimizar (evitar sobreproducción) |
| Utilización de recursos | 70–85% (no saturar ni desperdiciar) |

**Visual**: 4 cards con los KPIs principales.

**Notas**: 45 seg. Enfatizar el trade-off: *"Llegar al 100% es trivial si producimos sin límite — la gracia es llegar al 95% sin sobreproducir ni sobre-invertir."*

---

### SLIDE 4 — El sistema en una imagen

**Mensaje clave**: *"Producción multi-etapa → Horneado por familias → Inventario → Demanda estocástica. Tres puntos donde se decide."*

**Bullets**:
- 9 etapas productivas por lote (pesado → fermentación → horneado → enfriado → reposición)
- 3 familias de horneado **incompatibles** entre sí (14 / 18 / 21 min) + setup de 5 min al cambiar
- Demanda compuesta: llegada Poisson no homogénea × elección por hora × cantidad triangular

**Visual principal**: BPMN simplificado del flujo (versión reducida de `flujo/diagrama_bpmn_panaderia.md`) con 3 íconos destacados que marcan los puntos de decisión:
- 🎛️ **Decisión 1**: ¿Cuándo y qué lote liberar? (Política producción)
- 🔥 **Decisión 2**: ¿Qué familia hornear primero? (Política horno)
- 📦 **Decisión 3**: ¿Cuánta capacidad instalar? (Recursos)

**Notas**: 1 min. Recorrer brevemente el flujo y plantar los 3 íconos que aparecerán en los slides 7, 8 y 9.

---

### SLIDE 5 — Las 3 palancas y el diseño experimental

**Mensaje clave**: *"Probamos 3 × 4 × N combinaciones con 20 réplicas cada una"*.

**Visual principal**: matriz 3D / tabla resumen del diseño experimental:

| Eje | Niveles probados | Cantidad |
|---|---|---|
| 🎛️ Producción | Plan puro · Plan + Reactivo (Híbrida) · PULL puro | 3 |
| 🔥 Horno | Menor-stock · Mayor-demanda · Fija F1→F2→F3 · Híbrida | 4 |
| 📦 Recursos | Mezcladoras {4,5,6} · Panaderos {8,9,10} · Hornos {1,2,3} · Manipuladores {3,4,5} | OFAT |

**Bullets**:
- Estrategia tipo "embudo": cada bloque cierra una decisión y fija esa variable para el siguiente
- 20 réplicas por escenario → resultados con intervalo de confianza 95%
- Política horno por defecto en bloque 1: Fija F1→F2→F3 (la más conservadora, para aislar el efecto de producción)
- Las 3 políticas de producción cubren un **espectro de reactividad**: 0% (Plan puro) → reactividad moderada cada 30 min (Híbrida) → 100% reactiva por ROP (PULL)

**Notas**: 45 seg. *"La matriz completa sería 24 combinaciones; el pitch las recorre en 3 pasos."*

---

### SLIDE 6 — Punto de partida teórico (Configuración base)

**Mensaje clave**: *"El cálculo analítico dice: la mezcladora es la restricción, el horno tiene holgura"*.

**Bullets**:
- Configuración mínima viable derivada del análisis de carga de recursos (§6.2 reporte pre-modelación)
- La mezcladora exige 2.442 min/día y la ventana operativa es 555 min: **necesita 5 unidades** (88% utilización)
- El horno solo se ocupa 295 min de 600 disponibles → **49% utilización con 1 horno**, pero se proyectan **2 hornos** por flexibilidad temporal
- Esta es la "base" sobre la cual variaremos en el Eje C

**Tabla — Recursos base**:

| Recurso | Cantidad base | % Utilización teórica |
|---|---|---|
| Mezcladoras | 5 | 88% |
| Hornos | 2 | ~25% (con holgura) |
| Panaderos | 9 | ~80% |
| Manipuladores horno | 4 | ~25% |

**Visual**: barra horizontal de utilización teórica por recurso, mostrando dónde hay holgura y dónde hay tensión.

**Notas**: 45 seg. *"Acá ya tenemos una sorpresa: el horno no es el problema. La mezcladora sí."*

---

### SLIDE 7 — Eje A: ¿Cuál política de producción?

**Mensaje clave**: *"Plan puro pierde el peak; PULL reacciona tarde; el ajuste reactivo sobre un plan base anticipa y absorbe la varianza"*. **[VALIDAR CON DATOS]**

**Bloque experimental**:
- Variable: Política de Producción ∈ {Plan puro, Plan + Reactivo (Híbrida), PULL puro}
- Fijo: Recursos = base · Política horno = Fija F1→F2→F3
- 3 escenarios × 20 réplicas = 60 corridas

**Lógica de cada política a contar en el slide (1 línea cada una)**:
- **Plan puro**: secuencia fija de 155 lotes generada offline; sin reacción a inventario observado.
- **Plan + Reactivo (Híbrida)**: mismo plan base + revisor cada 30 min que inyecta lotes de emergencia si proyecta déficit a 2 hrs.
- **PULL puro**: sin plan a priori; cada SKU se reabastece cuando su inventario cae bajo su ROP (calculado en `analisis_eoq_rop.csv`).

**Visual principal**: gráfico de barras agrupadas
- Eje X: 10 SKUs (ordenados por demanda decreciente)
- Eje Y: % demanda satisfecha
- 3 series: Plan puro (gris) · Plan + Reactivo (azul) · PULL (naranja)
- Línea horizontal objetivo: 95%

```
% Servicio por SKU — Política Producción
100% ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ (objetivo 95%)
 90% ┤  █ █ █   █ █ █   █ █ █   ...   ← [PH] series
 80% ┤  █ █ ▓   █ █ ▓   █ █ ▓   ...
 70% ┤
     └─ Marraq Hallull HotDog MarraqInt ...
        ▒ Plan puro · █ Híbrida · ▓ PULL
```

**KPI cards laterales (5 filas × 3 columnas)**:

| KPI | Plan puro | Plan + Reactivo | PULL |
|---|---|---|---|
| Fill rate global | `[PH] %` | `[PH] %` | `[PH] %` |
| Fill rate mínimo (peor SKU) | `[PH] %` | `[PH] %` | `[PH] %` |
| Kg no vendidos | `[PH] kg` | `[PH] kg` | `[PH] kg` |
| Sobrantes 21:00 | `[PH] kg` | `[PH] kg` | `[PH] kg` |
| Lotes reactivos | N/A | `[PH]` | N/A |

**Tabla de respaldo** (slide oculto / anexo):

| SKU | % Servicio Plan | IC 95% | % Servicio Híbrida | IC 95% | % Servicio PULL | IC 95% | Mejor |
|---|---|---|---|---|---|---|---|
| Marraqueta | `[PH]` | `[PH]` | `[PH]` | `[PH]` | `[PH]` | `[PH]` | `[PH]` |
| ... (10 filas) | | | | | | | |

**Mensaje de cierre**: *"La política `[PH: ganadora]` se adopta para el siguiente bloque. Hipótesis a confirmar: la reactividad moderada sobre un plan base bate tanto al plan rígido como al PULL puro, porque combina anticipación con corrección."*

**Notas**: 1 min 15 seg. Marco narrativo: las 3 políticas representan un **espectro de reactividad** (0% → 100%). El plan puro falla porque no se adapta a la varianza del peak; el PULL falla porque reacciona después del quiebre (el lead time productivo de 90–120 min lo hace estructuralmente tarde); la híbrida anticipa con plan + corrige con revisor. **Si los datos contradicen esta hipótesis, ajustar el guion según la ganadora real.**

---

### SLIDE 8 — Eje B: ¿Cuál secuencia de horno?

**Mensaje clave**: *"La política de horno que mira el stock en sala lidera en peak; la fija es robusta pero rígida"*. **[VALIDAR CON DATOS]**

**Bloque experimental**:
- Variable: Política Horno ∈ {Menor-stock, Mayor-demanda, Fija F1→F2→F3, Híbrida}
- Fijo: Recursos = base · Producción = ganadora del Slide 7
- 4 escenarios × 20 réplicas = 80 corridas

**Visual principal**: gráfico de líneas
- Eje X: 10 SKUs
- Eje Y: % demanda satisfecha
- 4 series (una por política), con bandas de confianza 95%
- Línea horizontal objetivo: 95%

**Visual secundario**: heatmap "ganador por SKU × política":

| SKU | Menor-stock | Mayor-demanda | Fija | Híbrida |
|---|---|---|---|---|
| Marraqueta | `[PH]` 🟢/🟡/🔴 | `[PH]` | `[PH]` | `[PH]` |
| ... (10 filas) | | | | |

**KPI cards (4)**: fill rate global por política horno.

| Política Horno | Fill global | Kg perdidos | Sobrantes | Setups día |
|---|---|---|---|---|
| Menor-stock | `[PH]` | `[PH]` | `[PH]` | `[PH]` |
| Mayor-demanda | `[PH]` | `[PH]` | `[PH]` | `[PH]` |
| Fija F1→F2→F3 | `[PH]` | `[PH]` | `[PH]` | `[PH]` |
| Híbrida | `[PH]` | `[PH]` | `[PH]` | `[PH]` |

**Mensaje de cierre**: *"La política `[PH: ganadora]` será la base para evaluar el dimensionamiento de recursos."*

**Notas**: 1 min 15 seg. Discutir el trade-off: Fija tiene 0 setups extra pero no se adapta; Menor-stock se adapta pero puede generar más cambios de familia (más setups, menos throughput).

---

### SLIDE 9 — Eje C: ¿Cuántos recursos instalar?

**Mensaje clave**: *"Subir mezcladoras de 4 a 5 es crítico; pasar a 6 no mueve la aguja. La curva de retorno tiene un codo claro."* **[VALIDAR CON DATOS]**

**Bloque experimental** (OFAT — One Factor At a Time):
- Variables: 4 recursos × 3 niveles = 12 puntos (8 nuevos + 4 base ya corridos)
- Fijo: Política Producción + Política Horno = ganadoras de Slides 7 y 8
- 8 escenarios nuevos × 20 réplicas = 160 corridas

**Visual principal**: 4 mini-gráficos en grilla 2×2, uno por recurso:

```
Mezcladoras (4·5·6)        Panaderos (8·9·10)
   ↑ Fill                     ↑ Fill
100%┤    ●─●                100%┤      ●─●
 80%┤  ●                     90%┤    ●
 60%┤                        80%┤  ●
    └─ 4  5  6                  └─ 8  9 10

Hornos (1·2·3)             Manipuladores (3·4·5)
   ↑ Fill                     ↑ Fill
100%┤  ●─●─●               100%┤    ●─●
 80%┤                        90%┤  ●
    └─ 1  2  3                  └─ 3  4  5
```

Para cada curva marcar:
- El "codo" óptimo (punto de inflexión)
- La línea objetivo 95%
- Bandas de confianza 95%

**Tabla de respaldo — Utilización de cada recurso en su nivel óptimo**:

| Recurso | Nivel óptimo | % Utilización (real) | Holgura |
|---|---|---|---|
| Mezcladoras | `[PH]` | `[PH] %` | `[PH]` |
| Panaderos | `[PH]` | `[PH] %` | `[PH]` |
| Hornos | `[PH]` | `[PH] %` | `[PH]` |
| Manipuladores horno | `[PH]` | `[PH] %` | `[PH]` |

**Mensaje de cierre**: *"El dimensionamiento óptimo coincide en gran medida con la base teórica del §6.2. La excepción es `[PH]`."*

**Notas**: 1 min 30 seg. Este es el slide que muestra el rigor del análisis de sensibilidad — mostrar cómo el "codo" justifica la inversión.

---

### SLIDE 10 — Cuello de botella y configuración ganadora

**Mensaje clave**: *"La combinación Producción `[PH]` + Horno `[PH]` + recursos `[PH]` alcanza ≥95% en todos los SKUs sin sobrecapacidad"*.

**Tabla resumen del escenario campeón**:

| Dimensión | Configuración ganadora |
|---|---|
| Política producción | `[PH: Híbrida / PULL]` |
| Política horno | `[PH: Menor-stock / Mayor-demanda / Fija / Híbrida]` |
| Mezcladoras | `[PH]` |
| Panaderos | `[PH]` |
| Hornos | `[PH]` |
| Manipuladores horno | `[PH]` |
| Hora de inicio operación | `[PH: 06:00]` |

**KPIs del escenario campeón (vs base teórica sin optimización)**:

| KPI | Base mín. viable | Campeón | Δ |
|---|---|---|---|
| Fill rate global | `[PH] %` | `[PH] %` | `[PH]` |
| Fill rate mínimo (peor SKU) | `[PH] %` | `[PH] %` | `[PH]` |
| Kg no vendidos | `[PH] kg` | `[PH] kg` | `[PH]` |
| Sobrantes 21:00 | `[PH] kg` | `[PH] kg` | `[PH]` |
| # Lotes producidos | `[PH]` | `[PH]` | `[PH]` |

**Visual de utilización del campeón**: barras horizontales con %util por recurso, indicando dónde está el cuello de botella residual.

**Notas**: 1 min. *"La gracia es que el campeón usa la misma capacidad instalada que la base teórica — la mejora viene de las dos políticas, no del CAPEX."* (si esto resulta ser cierto con los datos).

---

### SLIDE 11 — Impacto esperado y recomendación

**Mensaje clave**: *"Antes de invertir en un 3er horno o 6ª mezcladora, la operación gana más cambiando la política de horno. La inversión en `[PH]` solo se justifica si la demanda crece `[PH]`%."*

**Bullets — Impacto**:
- ↑ **Nivel de servicio** de `[PH base]%` a `[PH campeón]%` global
- ↓ **Kg perdidos** de `[PH]` a `[PH]` (`[PH]%` reducción)
- ↓ **Sobrantes** de `[PH]` a `[PH]` (`[PH]%` reducción)
- ↑ **Uso eficiente de recursos**: mezcladora en `[PH]%`, horno en `[PH]%`
- 🚫 **CAPEX evitado**: no se requiere `[PH: 3er horno / 6ª mezcladora / etc.]`

**Recomendación operativa (3 acciones inmediatas)**:
1. **Adoptar política `[PH]`** para liberación de lotes (configuración del controlador de producción)
2. **Adoptar política `[PH]`** para secuencia de horno (lógica de despacho del operador)
3. **Mantener / Ajustar a** `[PH]` mezcladoras y `[PH]` hornos en la base instalada

**Próximos pasos sugeridos**:
- Piloto controlado de 2 semanas con la política recomendada
- Re-evaluación si la demanda crece >`[PH]%` o cambia el mix de productos
- Extensión del modelo a otros locales con perfil de demanda similar

**Visual**: barra de "antes vs después" con los 3 KPIs principales + ícono de CAPEX tachado.

**Notas**: 1 min 30 seg. Cerrar con la frase: *"La inteligencia operativa supera al CAPEX cuando se sabe dónde mirar."*

---

## 3. Anexo A — Matriz Maestra de Escenarios

Total: 15 escenarios distintos × 20 réplicas = **300 corridas**.

| ID | Bloque | Política Producción | Política Horno | Mezcl. | Panad. | Hornos | Manip. | Réplicas |
|---|---|---|---|---|---|---|---|---|
| E01 | B1 | Plan puro | Fija F1→F2→F3 | 5 | 9 | 2 | 4 | 20 |
| E02 | B1 | Plan + Reactivo (Híbrida) | Fija F1→F2→F3 | 5 | 9 | 2 | 4 | 20 |
| E03 | B1 | PULL puro | Fija F1→F2→F3 | 5 | 9 | 2 | 4 | 20 |
| E04 | B2 | `[ganadora B1]` | Menor-stock | 5 | 9 | 2 | 4 | 20 |
| E05 | B2 | `[ganadora B1]` | Mayor-demanda | 5 | 9 | 2 | 4 | 20 |
| E06 | B2 | `[ganadora B1]` | Híbrida (stock + demanda) | 5 | 9 | 2 | 4 | 20 |
| E07 | B3 | `[ganadora B1]` | `[ganadora B2]` | **4** | 9 | 2 | 4 | 20 |
| E08 | B3 | `[ganadora B1]` | `[ganadora B2]` | **6** | 9 | 2 | 4 | 20 |
| E09 | B3 | `[ganadora B1]` | `[ganadora B2]` | 5 | **8** | 2 | 4 | 20 |
| E10 | B3 | `[ganadora B1]` | `[ganadora B2]` | 5 | **10** | 2 | 4 | 20 |
| E11 | B3 | `[ganadora B1]` | `[ganadora B2]` | 5 | 9 | **1** | 4 | 20 |
| E12 | B3 | `[ganadora B1]` | `[ganadora B2]` | 5 | 9 | **3** | 4 | 20 |
| E13 | B3 | `[ganadora B1]` | `[ganadora B2]` | 5 | 9 | 2 | **3** | 20 |
| E14 | B3 | `[ganadora B1]` | `[ganadora B2]` | 5 | 9 | 2 | **5** | 20 |
| E15 | Campeón | `[ganadora B1]` | `[ganadora B2]` | `[opt]` | `[opt]` | `[opt]` | `[opt]` | 20 |

> **Reutilización entre bloques**:
> - El escenario con política horno "Fija F1→F2→F3" del bloque B2 ya fue corrido en B1 (escenarios E01–E03 para sus respectivas políticas de producción). Tras elegir la política ganadora de B1, el resultado correspondiente sirve como cuarto punto de comparación de B2 — no se vuelve a correr.
> - Si en B3 la combinación ganadora coincide con uno de los escenarios E04–E10, el "Campeón" (E15) puede omitirse usando ese resultado directamente.

---

## 4. Anexo B — Plantilla CSV de resultados

Para facilitar el llenado de placeholders, sugiero exportar los resultados de SIMIO en este formato (`pitch/resultados_experimentos.csv`):

```csv
escenario_id,replica,politica_prod,politica_horno,mezcl,panad,hornos,manip,sku,fill_rate,kg_no_vendidos,sobrantes,produccion_kg,n_lotes,n_lotes_reactivos,util_mezcl,util_amas,util_horno,util_panad,util_manip,setups_horno
E01,1,PlanPuro,Fija,5,9,2,4,Marraqueta,0.945,110,12,1890,32,0,...
E02,1,PlanReactivo,Fija,5,9,2,4,Marraqueta,0.962,76,32,1980,34,2,...
E03,1,PULL,Fija,5,9,2,4,Marraqueta,0.928,144,8,1856,31,N/A,...
...
```

> **Convención de nombres recomendada para `politica_prod`**: `PlanPuro`, `PlanReactivo`, `PULL`.
> **Convención para `politica_horno`**: `MenorStock`, `MayorDemanda`, `Fija`, `Hibrida`.

Con ese CSV se generan automáticamente los gráficos de los slides 7, 8, 9, 10 vía pivot/agregación por escenario.

---

## 5. Notas finales para producción del pitch

- **Tono**: ejecutivo, no académico. Cada slide debe poder leerse en 30 segundos sin explicación.
- **Datos visibles**: priorizar gráficos sobre tablas; los datos finos van en anexo/respaldo.
- **Color**: usar paleta consistente entre slides (1 color por política de producción, 1 paleta secuencial para política de horno, 1 color "alerta" para quiebres).
- **Tiempo objetivo**: 10–12 min con margen de Q&A. Distribución sugerida:
  - Slides 1–6 (contexto y diseño): 4 min
  - Slides 7–9 (resultados de los 3 ejes): 4 min
  - Slides 10–11 (campeón e impacto): 2–3 min
