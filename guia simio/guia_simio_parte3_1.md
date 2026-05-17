# Guía de Implementación en SIMIO — Parte 3: Processes, Experiments y Resultados

---

## FASE 7: Processes (Lógica Personalizada)

Los Processes en SIMIO permiten implementar lógica que va más allá de las propiedades estándar de Source/Server/Sink. Se acceden desde **Definitions → Processes** o desde **Add-On Process Triggers** de cada objeto.

### Paso 7.1 — Process: Asignación de tipo de pan al cliente (con probabilidades condicionales)

**Ubicación**: En `SrcClientes` → Properties → **Add-On Process Triggers** → **Before Exiting** → Crear nuevo proceso `ProcAsignarTiposCliente`

> **Ref. Reporte §3.10**: La selección del 2º y 3er tipo de pan se realiza **sin reemplazo** usando probabilidades condicionales:
>
> P(2º = j | 1º = i) = Pⱼ / (1 − Pᵢ),  j ≠ i
>
> P(3º = k | 1º = i, 2º = j) = Pₖ / (1 − Pᵢ − Pⱼ),  k ≠ i,j
>
> **Ref. Workbook §7.2**: Se implementa mediante **Assign** y **Decide** steps dentro del Process, usando `Random.Uniform(0,1)` y un recorrido acumulativo que excluye los tipos ya seleccionados.

Este proceso calcula el índice de hora actual, asigna el primer tipo con probabilidades marginales y luego asigna el 2º/3er tipo con **probabilidades condicionales exactas** (sin reemplazo).

#### Diagrama conceptual del Process

```
[Assign HoraIdx] → [Assign NTipos] → [Assign Tipo1] → [Assign Kg1]
                                                           ↓
                                              [Decide: NTipos >= 2?]
                                                  ↓ True           ↓ False → FIN
                                [Assign ProbRest1]
                                [Assign Rand2 = U(0,1) * ProbRest1]
                                [Assign Tipo2 via scan condicional]
                                [Assign Kg2]
                                          ↓
                              [Decide: NTipos >= 3?]
                                  ↓ True           ↓ False → FIN
                    [Assign ProbRest2]
                    [Assign Rand3 = U(0,1) * ProbRest2]
                    [Assign Tipo3 via scan condicional]
                    [Assign Kg3]
                          ↓
                         FIN
```

#### Pasos del Process — Detalle completo

**Grupo A: Hora y número de tipos**

| Step | Tipo | State Variable | Value |
|------|------|---------------|-------|
| A1 | **Assign** | `Model.MStaHoraIdx` | `Math.Floor(Run.TimeNow / 60) + 1` |
| A2 | **Assign** | `EntCliente.EStaNTipos` | `Random.Discrete(1, 0.50, 2, 0.85, 3, 1.00)` |

> **Nota A1**: La simulación empieza en t=0 correspondiente a 09:00. `Run.TimeNow` está en minutos, por lo que `Math.Floor(Run.TimeNow / 60) + 1` da el índice 1-12 de la tabla `TableProbEleccion`. Se debe acotar con `Math.Min(12, Math.Max(1, ...))` para seguridad.

**Grupo B: Primera selección (probabilidades marginales)**

| Step | Tipo | State Variable | Value |
|------|------|---------------|-------|
| B1 | **Assign** | `EntCliente.EStaTipo1` | *(ver expresión completa abajo)* |
| B2 | **Assign** | `EntCliente.EStaKg1` | `Random.Triangular(TableCompra[EntCliente.EStaTipo1].TriMin, TableCompra[EntCliente.EStaTipo1].TriModa, TableCompra[EntCliente.EStaTipo1].TriMax)` |

**Expresión para B1** — `Random.Discrete` con probabilidades acumuladas:

```
Random.Discrete(
  1, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta,
  2, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta + TableProbEleccion[Model.MStaHoraIdx].PHallulla,
  3, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta + TableProbEleccion[Model.MStaHoraIdx].PHallulla + TableProbEleccion[Model.MStaHoraIdx].PMarrInt,
  4, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta + TableProbEleccion[Model.MStaHoraIdx].PHallulla + TableProbEleccion[Model.MStaHoraIdx].PMarrInt + TableProbEleccion[Model.MStaHoraIdx].PHallInt,
  5, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta + TableProbEleccion[Model.MStaHoraIdx].PHallulla + TableProbEleccion[Model.MStaHoraIdx].PMarrInt + TableProbEleccion[Model.MStaHoraIdx].PHallInt + TableProbEleccion[Model.MStaHoraIdx].PHotDog,
  6, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta + TableProbEleccion[Model.MStaHoraIdx].PHallulla + TableProbEleccion[Model.MStaHoraIdx].PMarrInt + TableProbEleccion[Model.MStaHoraIdx].PHallInt + TableProbEleccion[Model.MStaHoraIdx].PHotDog + TableProbEleccion[Model.MStaHoraIdx].PCiabatta,
  7, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta + TableProbEleccion[Model.MStaHoraIdx].PHallulla + TableProbEleccion[Model.MStaHoraIdx].PMarrInt + TableProbEleccion[Model.MStaHoraIdx].PHallInt + TableProbEleccion[Model.MStaHoraIdx].PHotDog + TableProbEleccion[Model.MStaHoraIdx].PCiabatta + TableProbEleccion[Model.MStaHoraIdx].PBaguette,
  8, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta + TableProbEleccion[Model.MStaHoraIdx].PHallulla + TableProbEleccion[Model.MStaHoraIdx].PMarrInt + TableProbEleccion[Model.MStaHoraIdx].PHallInt + TableProbEleccion[Model.MStaHoraIdx].PHotDog + TableProbEleccion[Model.MStaHoraIdx].PCiabatta + TableProbEleccion[Model.MStaHoraIdx].PBaguette + TableProbEleccion[Model.MStaHoraIdx].PDobladita,
  9, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta + TableProbEleccion[Model.MStaHoraIdx].PHallulla + TableProbEleccion[Model.MStaHoraIdx].PMarrInt + TableProbEleccion[Model.MStaHoraIdx].PHallInt + TableProbEleccion[Model.MStaHoraIdx].PHotDog + TableProbEleccion[Model.MStaHoraIdx].PCiabatta + TableProbEleccion[Model.MStaHoraIdx].PBaguette + TableProbEleccion[Model.MStaHoraIdx].PDobladita + TableProbEleccion[Model.MStaHoraIdx].PBocDama,
  10, 1.0
)
```

> **Tip SIMIO**: Si la expresión es demasiado larga, agregar **columnas de probabilidades acumuladas** (`CumPMarraqueta`, `CumPHallulla`, ...) a `TableProbEleccion` y referenciar directamente: `Random.Discrete(1, TableProbEleccion[h].CumPMarraqueta, 2, TableProbEleccion[h].CumPHallulla, ..., 10, 1.0)`.

---

**Grupo C: Segunda selección — Probabilidad condicional sin reemplazo**

> **Lógica matemática**: Se genera un U(0,1), se escala por `(1 - P_tipo1)`, y se recorre acumulativamente las probabilidades de los tipos restantes (saltando el tipo1). Este "scan condicional" implementa exactamente P(2º = j | 1º = i) = Pⱼ / (1 − Pᵢ).

| Step | Tipo | Configuración |
|------|------|---------------|
| C0 | **Decide** | Condition: `EntCliente.EStaNTipos >= 2` — Si False, saltar al final |
| C1 | **Assign** | `EntCliente.EStaProbRest1` = `1.0 - TableProbEleccion[Model.MStaHoraIdx].P[EntCliente.EStaTipo1]` *(ver nota abajo)* |
| C2 | **Assign** | `EntCliente.EStaRand2` = `Random.Uniform(0, 1) * EntCliente.EStaProbRest1` |
| C3 | **Assign** | `EntCliente.EStaTipo2` = 0 *(inicializar)* |
| C4–C13 | **10× Decide+Assign** | Scan condicional (ver detalle abajo) |
| C14 | **Assign** | `EntCliente.EStaKg2` = `Random.Triangular(TableCompra[EntCliente.EStaTipo2].TriMin, TableCompra[EntCliente.EStaTipo2].TriModa, TableCompra[EntCliente.EStaTipo2].TriMax)` |

**Nota sobre C1**: En SIMIO no se puede indexar dinámicamente por nombre de columna. Se usa una **función auxiliar** con condicionales:

```
Expresión para EStaProbRest1:
1.0 - (
  Math.If(EntCliente.EStaTipo1 == 1, TableProbEleccion[Model.MStaHoraIdx].PMarraqueta,
  Math.If(EntCliente.EStaTipo1 == 2, TableProbEleccion[Model.MStaHoraIdx].PHallulla,
  Math.If(EntCliente.EStaTipo1 == 3, TableProbEleccion[Model.MStaHoraIdx].PMarrInt,
  Math.If(EntCliente.EStaTipo1 == 4, TableProbEleccion[Model.MStaHoraIdx].PHallInt,
  Math.If(EntCliente.EStaTipo1 == 5, TableProbEleccion[Model.MStaHoraIdx].PHotDog,
  Math.If(EntCliente.EStaTipo1 == 6, TableProbEleccion[Model.MStaHoraIdx].PCiabatta,
  Math.If(EntCliente.EStaTipo1 == 7, TableProbEleccion[Model.MStaHoraIdx].PBaguette,
  Math.If(EntCliente.EStaTipo1 == 8, TableProbEleccion[Model.MStaHoraIdx].PDobladita,
  Math.If(EntCliente.EStaTipo1 == 9, TableProbEleccion[Model.MStaHoraIdx].PBocDama,
  TableProbEleccion[Model.MStaHoraIdx].PAmasado)))))))))
)
```

**Detalle del scan condicional (C4–C13)** — Para cada tipo candidato j = 1,2,...,10:

```
Para j = 1 (Marraqueta):
  Decide: EntCliente.EStaTipo1 != 1 AND EntCliente.EStaTipo2 == 0
    True → Assign: acumulador temporal
      Decide: EStaRand2 <= TableProbEleccion[h].PMarraqueta
        True → Assign: EStaTipo2 = 1
        False → Assign: EStaRand2 = EStaRand2 - TableProbEleccion[h].PMarraqueta

Para j = 2 (Hallulla):
  Decide: EntCliente.EStaTipo1 != 2 AND EntCliente.EStaTipo2 == 0
    True →
      Decide: EStaRand2 <= TableProbEleccion[h].PHallulla
        True → Assign: EStaTipo2 = 2
        False → Assign: EStaRand2 = EStaRand2 - TableProbEleccion[h].PHallulla

  ... (repetir para j = 3 hasta 10)
```

> **Simplificación práctica en SIMIO**: En lugar de 10 bloques Decide anidados, se puede implementar con una **cadena de Decide lineales**. Cada Decide verifica:
> 1. ¿El tipo j ya fue seleccionado como tipo 1? → Si sí, saltar.
> 2. ¿El rand residual es ≤ P(j)? → Si sí, asignar EStaTipo2 = j.
> 3. Si no, restar P(j) del rand y continuar al siguiente tipo.
>
> El último tipo sin verificar recibe automáticamente la selección (caso "catch-all").

**Implementación compacta alternativa** (si SIMIO permite expresiones largas):

```
EStaTipo2 = expresión con Math.If anidados:

Math.If(EStaTipo1 != 1 AND EStaRand2 <= P1, 1,
Math.If(EStaTipo1 != 1 AND EStaTipo2 == 0, EStaRand2 - P1, ...))
```

> **Recomendación**: Usar la **cadena de Decide** (enfoque visual en el Process) ya que es más debuggeable y transparente. Cada Decide tiene dos ramas claras.

---

**Grupo D: Tercera selección — Probabilidad condicional doble**

| Step | Tipo | Configuración |
|------|------|---------------|
| D0 | **Decide** | Condition: `EntCliente.EStaNTipos >= 3` — Si False, saltar al final |
| D1 | **Assign** | `EntCliente.EStaProbRest2` = `EStaProbRest1 - P(tipo2)` *(misma lógica que C1 pero restando P del tipo2)* |
| D2 | **Assign** | `EntCliente.EStaRand3` = `Random.Uniform(0, 1) * EntCliente.EStaProbRest2` |
| D3 | **Assign** | `EntCliente.EStaTipo3` = 0 |
| D4–D13 | **10× Decide+Assign** | Scan condicional idéntico al Grupo C, pero ahora excluye **tanto tipo1 como tipo2** |
| D14 | **Assign** | `EntCliente.EStaKg3` = `Random.Triangular(...)` |

**Condición del Decide en D4–D13** (para tipo candidato j):
```
EntCliente.EStaTipo1 != j AND EntCliente.EStaTipo2 != j AND EntCliente.EStaTipo3 == 0
```

---

#### Resumen del algoritmo de selección condicional

```
1. Generar NTipos ∈ {1, 2, 3} con P(1)=0.50, P(2)=0.35, P(3)=0.15

2. TIPO 1 — Selección marginal:
   Usar Random.Discrete con probabilidades acumuladas de la hora actual

3. TIPO 2 (si NTipos ≥ 2) — Selección condicional:
   a. ProbRest1 = 1 - P(Tipo1)
   b. Rand2 = U(0,1) × ProbRest1
   c. Para cada tipo j ≠ Tipo1:
      Si Rand2 ≤ P(j): Tipo2 = j → SALIR
      Sino: Rand2 = Rand2 - P(j) → siguiente j

4. TIPO 3 (si NTipos ≥ 3) — Selección condicional doble:
   a. ProbRest2 = ProbRest1 - P(Tipo2)
   b. Rand3 = U(0,1) × ProbRest2
   c. Para cada tipo k ≠ Tipo1, k ≠ Tipo2:
      Si Rand3 ≤ P(k): Tipo3 = k → SALIR
      Sino: Rand3 = Rand3 - P(k) → siguiente k
```

> **Validación**: Para la hora 09:00, si Tipo1 = Marraqueta (P=0.2645), las probabilidades condicionales del Tipo2 deben ser:
> - Hallulla: 0.2248 / (1-0.2645) = **0.3056** ✓
> - Marraqueta Int.: 0.1247 / 0.7355 = **0.1695** ✓
> - Hallulla Int.: 0.1164 / 0.7355 = **0.1582** ✓
>
> Esto coincide con la tabla del reporte §3.10.

> **Ref. Workbook §7.2–7.3**: El patrón Assign → Decide → Assign es el estándar de SIMIO para lógica ramificada en Processes. Los Add-On Process Triggers de tipo "Before Exiting" en el Source garantizan que la entidad ya tiene todos sus atributos asignados antes de entrar al flujo del modelo.

### Paso 7.2 — Process: Lógica de Venta (todo-o-nada)

**Ubicación**: En `SrvVenta` → **Add-On Process Triggers** → **Entered** → Crear `ProcVentaCliente`

Para cada tipo que el cliente quiere comprar:

```
PARA tipo 1:
  Decide: MStaInventario[EStaTipo1] >= EStaKg1?
    SÍ → Assign: MStaInventario[EStaTipo1] = MStaInventario[EStaTipo1] - EStaKg1
          Assign: MStaVentas[EStaTipo1] = MStaVentas[EStaTipo1] + EStaKg1
    NO → Assign: MStaQuiebres[EStaTipo1] = MStaQuiebres[EStaTipo1] + EStaKg1

SI EStaNTipos >= 2:
  (repetir para tipo 2)
SI EStaNTipos >= 3:
  (repetir para tipo 3)
```

#### Implementación paso a paso:

| Step | Tipo | Configuración |
|---|---|---|
| 1 | **Decide** | Condition: `Model.MStaInventario[EntCliente.EStaTipo1] >= EntCliente.EStaKg1` |
| 2a (True) | **Assign** | `Model.MStaInventario[EntCliente.EStaTipo1]` -= `EntCliente.EStaKg1` |
| 2b (True) | **Assign** | `Model.MStaVentas[EntCliente.EStaTipo1]` += `EntCliente.EStaKg1` |
| 2c (False) | **Assign** | `Model.MStaQuiebres[EntCliente.EStaTipo1]` += `EntCliente.EStaKg1` |
| 3 | **Decide** | Condition: `EntCliente.EStaNTipos >= 2` |
| 4-6 | *(Repetir lógica para Tipo2)* | |
| 7 | **Decide** | Condition: `EntCliente.EStaNTipos >= 3` |
| 8-10 | *(Repetir lógica para Tipo3)* | |

### Paso 7.3 — Process: Reposición de Inventario

**Ubicación**: En `SnkLoteTerminado` → **Add-On Process Triggers** → **Entered** → Crear `ProcReponerInventario`

| Step | Tipo | Configuración |
|---|---|---|
| 1 | **Assign** | `Model.MStaInventario[EntLote.EStaTipoPan]` += `EntLote.EStaKgLote` |
| 2 | **Assign** | `Model.MStaLotesProducidos[EntLote.EStaTipoPan]` += 1 |

### Paso 7.4 — Process: Inicialización de Inventario

**Ubicación**: En **Model** → **Definitions** → **Processes** → Crear `ProcInicializacion`
Trigger: **Add-On Process Triggers** del Model → **Initializing**

| Step | Asignación |
|---|---|
| 1 | `MStaInventario[1]` = 240 (4 batches × 60 kg Marraqueta) |
| 2 | `MStaInventario[2]` = 165 (3 batches × 55 kg Hallulla) |
| 3 | `MStaInventario[3]` = 120 (2 × 60 Marr.Int) |
| 4 | `MStaInventario[4]` = 110 (2 × 55 Hall.Int) |
| 5 | `MStaInventario[5]` = 55 (1 × 55 Hot Dog) |
| 6 | `MStaInventario[6]` = 50 (1 × 50 Ciabatta) |
| 7 | `MStaInventario[7]` = 45 (1 × 45 Baguette) |
| 8 | `MStaInventario[8]` = 50 (1 × 50 Dobladita) |
| 9 | `MStaInventario[9]` = 50 (2 × 25 Boc.Dama) |
| 10 | `MStaInventario[10]` = 60 (1 × 60 Amasado) |

### Paso 7.5 — Política de Carga del Horno (Simplificada)

Esta es la lógica más compleja. Se implementa en `SrvCargaHorno`:

**Opción A — Simplificada**: Modelar el horno como un Server con:
- **Batch Size**: Mínimo 1 lote (el batching se maneja por acumulación)
- Usar **Input Buffer** con regla de acumulación

**Opción B — Con Process**: En `SrvFermentacion` → **Exited** trigger:

| Step | Tipo | Configuración |
|---|---|---|
| 1 | **Assign** | `MStaColaHorno[EntLote.EStaFamilia]` += `EntLote.EStaKgLote` |
| 2 | **Decide** | `MStaColaHorno[EntLote.EStaFamilia] >= 600` |
| 3 (True) | **Assign** | Resetear cola, iniciar corrida |
| 3 (False) | **Delay** | Timer de espera (máx 15 min), luego iniciar corrida anticipada |

---

## FASE 8: Configurar Input Parameters para Experimentación

### Paso 8.1 — Crear Referenced Properties

Para cada recurso cuya cantidad queremos variar en experimentos:

1. Clic en el objeto (ej. `SrvMezcladoAuto`) → Properties → **Initial Capacity**
2. Clic derecho en el campo → **Set Referenced Property** → **Create New Property**
3. Nombres:

| Property | Valor Default | Se usa en |
|---|---|---|
| `PropNumMezcladoras` | 3 | `SrvMezcladoAuto` Initial Capacity |
| `PropNumHornos` | 2 | `SrvHorneado` Initial Capacity |
| `PropNumPanaderosA` | 3 | `ResPanaderoA` Initial Capacity |
| `PropNumPanaderosB` | 3 | `ResPanaderoB` Initial Capacity |
| `PropNumPanaderosC` | 3 | `ResPanaderoC` Initial Capacity |
| `PropNumPanaderoRefuerzo` | 2 | `ResPanaderoRefuerzo` Initial Capacity |
| `PropNumManipuladores` | 2 | `ResManipulador` Initial Capacity |
| `PropNumAmasadoras` | 3 | `SrvAmasadoManual` Initial Capacity |
| `PropNumMesas` | 3 | `SrvFormado` Initial Capacity |

> **Ref. Workbook §3.5.1**: Las Referenced Properties aparecen automáticamente en la grilla de experimentos.
> **Nota**: Los 3 grupos de panaderos (A, B, C) permiten experimentar con diferentes distribuciones de personal entre turnos escalonados.

### Paso 8.2 — Crear Input Parameter Distributions

Ir a **Data** → **Input Parameters** → **Distribution**:

| Nombre | Distribución | Parámetros | Random Stream | Uso |
|---|---|---|---|---|
| `InpDisInterarriboCliente` | (No aplica, usamos Rate Table) | — | — | — |
| `InpDisNTipos` | Discrete | (1, 0.5; 2, 0.85; 3, 1.0) | Stream 1 | Nº tipos por cliente |

---

## FASE 9: Crear Experimento

### Paso 9.1 — Nuevo Experiment

**Project Home** → **New Experiment** → Nombre: `ExpRecursosOptimos`

### Paso 9.2 — Configurar Design Tab

En la pestaña **Design**:
- **Replications**: 20 (para obtener intervalos de confianza estrechos)
- **Confidence Level**: 95%

### Paso 9.3 — Crear Escenarios

Agregar filas (clic en `*`) variando los recursos:

| Scenario | Mezcl. | Hornos | PanadA | PanadB | PanadC | Refuerzo | Manip. |
|---|---|---|---|---|---|---|---|
| Base | 3 | 1 | 3 | 3 | 3 | 0 | 2 |
| Esc2_2Hornos | 3 | 2 | 3 | 3 | 3 | 0 | 2 |
| Esc3_Refuerzo | 3 | 2 | 3 | 3 | 3 | 2 | 3 |
| Esc4_MasPanad | 3 | 2 | 4 | 3 | 3 | 2 | 3 |
| Esc5_Full | 4 | 2 | 4 | 3 | 4 | 3 | 3 |

### Paso 9.4 — Definir Responses

En la pestaña **Design** → **Add Response**:

| Response Name | Expression | Units |
|---|---|---|
| `QuiebreTotalKg` | `Model.MStaQuiebres[1] + Model.MStaQuiebres[2] + ... + Model.MStaQuiebres[10]` | Kg |
| `NivelServicioPct` | `(Sum(MStaVentas) / (Sum(MStaVentas) + Sum(MStaQuiebres))) * 100` | % |
| `VentasTotalesKg` | `Model.MStaVentas[1] + ... + Model.MStaVentas[10]` | Kg |
| `UtilMezcladora` | `SrvMezcladoAuto.ResourceState.ScheduledUtilization` | — |
| `UtilHorno` | `SrvHorneado.ResourceState.ScheduledUtilization` | — |

### Paso 9.5 — Ejecutar y Analizar

1. Clic en **Run** en la sección Experiment del ribbon
2. Ir a **Response Results** → comparar escenarios gráficamente
3. Ir a **Pivot Grid** → ver Average, Half-Width, Min, Max
4. Ir a **Input Analysis** → **Response Sensitivity** para ver qué recurso impacta más

> **Ref. Workbook §3.5.7–3.5.11**: Los Response Results charts muestran intervalos de confianza. Si los intervalos de dos escenarios no se traslapan, la diferencia es estadísticamente significativa.

---

## FASE 10: Análisis de Resultados (Checklist)

### 10.1 — Métricas clave a verificar

| Métrica | Dónde encontrarla | Valor esperado |
|---|---|---|
| Quiebres totales (kg) | Response `QuiebreTotalKg` | Minimizar |
| Nivel de servicio (%) | Response `NivelServicioPct` | > 95% |
| Utilización mezcladora | Results → SrvMezcladoAuto → ScheduledUtilization | < 90% |
| Utilización horno | Results → SrvHorneado → ScheduledUtilization | < 85% |
| Cola horno (promedio) | Results → SrvCargaHorno → InputBuffer → Content → Average | < 3 lotes |
| Tiempo en sistema (lote) | Results → EntLote → FlowTime → Average | Razonable |
| Inventario promedio en sala | Status Labels durante la corrida | Positivo durante peak |

### 10.2 — Reportar desde Pivot Grid

1. Ir a **Results** tab después de correr
2. Filtrar por **Category**: `Capacity` → ver `ScheduledUtilization` por servidor
3. Filtrar por **Category**: `Content` → ver promedio en cola por InputBuffer
4. Filtrar por **Category**: `FlowTime` → ver tiempos promedio
5. Cambiar unidades con **Unit Settings** → Time = Minutes

### 10.3 — Status Labels útiles (para debug visual)

En **Drawing** tab, agregar **Status Labels** al canvas:

| Label | Expression |
|---|---|
| "Inventario Marraqueta" | `Model.MStaInventario[1]` |
| "Quiebres Totales" | `Sum(Model.MStaQuiebres)` |
| "Hora Simulada" | `Run.TimeNow` |
| "Clientes Atendidos" | `SrcClientes.TotalEntitiesCreated` |

---

## Resumen de Archivos de Referencia

| Archivo | Contenido |
|---|---|
| `reporte_pre_modelacion.md` | Fuente de verdad: parámetros, supuestos, lógica de decisión |
| `parametros_proceso_panaderia.csv` | Tiempos por etapa y tamaño de lote |
| `perfil_demanda_por_hora_panaderia.csv` | Demanda horaria por tipo |
| `probabilidades_eleccion_por_hora.csv` | Probabilidades de elección por hora |
| `guia_simio_parte1.md` | Setup del proyecto, entidades, tablas de datos |
| `guia_simio_parte2.md` | Facility, Rate Tables, Work Schedules |
| `guia_simio_parte3.md` | Processes, Experiments, Resultados (este archivo) |
