# Guía de Implementación en SIMIO — Panadería de Supermercado (Parte 1)

> **Referencia**: Basada en el Workbook SIMIO 6th Ed. (Caps. 2–5) y el `reporte_pre_modelacion.md`

---

## FASE 1: Configuración Inicial del Proyecto

### Paso 1.1 — Crear proyecto nuevo✅

1. Abrir SIMIO → **File → New Project**
2. Nombre: `PanaderiaSupermercado`
3. En **Run Tab → Units**: configurar Time = **Minutes**, Length = **Meters**

### Paso 1.2 — Crear las Entidades ✅

En el **[Project Library]**, crear las siguientes entidades (clic derecho → Add → Entity):

| Entidad             | Nombre SIMIO   | Propósito                      |
| ------------------- | -------------- | ------------------------------- |
| Lote de producción | `EntLote`    | Fluye por el proceso productivo |
| Cliente             | `EntCliente` | Consume inventario en sala      |

#### Configurar `EntLote` — State Variables´ ✅

Ir a **Navigation Panel** → clic en `EntLote` → pestaña **Definitions** → **States**:

| State Variable            | Tipo             | Nombre          |
| ------------------------- | ---------------- | --------------- |
| Tipo de pan (1-10)        | Discrete Integer | `EStaTipoPan` |
| Familia de horneado (1-3) | Discrete Integer | `EStaFamilia` |
| Kg del lote               | Discrete Real    | `EStaKgLote`  |

#### Configurar `EntCliente` — State Variables ✅

Clic en `EntCliente` → **Definitions** → **States**:

| State Variable            | Tipo             | Nombre         |
| ------------------------- | ---------------- | -------------- |
| Nº tipos a comprar (1-3) | Discrete Integer | `EStaNTipos` |
| Tipo 1 seleccionado       | Discrete Integer | `EStaTipo1`  |
| Tipo 2 seleccionado       | Discrete Integer | `EStaTipo2`  |
| Tipo 3 seleccionado       | Discrete Integer | `EStaTipo3`  |
| Kg tipo 1                 | Discrete Real    | `EStaKg1`    |
| Kg tipo 2                 | Discrete Real    | `EStaKg2`    |
| Kg tipo 3                 | Discrete Real    | `EStaKg3`    |

---

## FASE 2: Tablas de Datos (Data Tab → Tables)

### Paso 2.1 — Tabla de Parámetros de Proceso ✅

Ir a pestaña **Data** → **Tables** → **Add Data Table** → Nombre: `TableProceso`

**Columnas** (Add Standard Property):

| Columna                 | Tipo       | Unit Type  | Descripción       |
| ----------------------- | ---------- | ---------- | ------------------ |
| `TipoPanID`           | Integer    | —         | ID 1-10            |
| `NombrePan`           | String     | —         | Nombre descriptivo |
| `FamiliaID`           | Integer    | —         | 1, 2 o 3           |
| `TiempoPesado`        | Expression | Time (Min) | 5 para todos       |
| `TiempoCargaMezc`     | Expression | Time (Min) | 2 para todos       |
| `TiempoMezcladoAuto`  | Expression | Time (Min) | 10-15 según tipo  |
| `TiempoRetiroMasa`    | Expression | Time (Min) | 1 para todos       |
| `TiempoAmasadoManual` | Expression | Time (Min) | ~50% del mezclado  |
| `TiempoReposo`        | Expression | Time (Min) | 15-30              |
| `TiempoFormado`       | Expression | Time (Min) | 8-12               |
| `TiempoFermentacion`  | Expression | Time (Min) | 20-45              |
| `TiempoHorneado`      | Expression | Time (Min) | 14/18/21           |
| `TiempoEnfriado`      | Expression | Time (Min) | 7-10               |
| `TiempoTraslado`      | Expression | Time (Min) | 3-5                |
| `KgPorBatch`          | Real       | —         | 25-60              |
| `CarrosPorBatch`      | Integer    | —         | 1-2                |

**Filas** (10 filas, una por tipo de pan):

| Row | TipoPanID      | Mezclado | Reposo | Formado | Ferm. | Horneado | Enfriado | Traslado | Kg/Batch |
| --- | -------------- | -------- | ------ | ------- | ----- | -------- | -------- | -------- | -------- |
| 1   | 1 (Marraqueta) | 12       | 15     | 10      | 35    | 18       | 8        | 4        | 60       |
| 2   | 2 (Hallulla)   | 14       | 20     | 12      | 30    | 18       | 8        | 4        | 55       |
| 3   | 3 (Marr.Int)   | 13       | 18     | 10      | 40    | 21       | 8        | 4        | 60       |
| 4   | 4 (Hall.Int)   | 15       | 20     | 12      | 35    | 18       | 8        | 4        | 55       |
| 5   | 5 (Hot Dog)    | 12       | 15     | 12      | 40    | 14       | 8        | 4        | 55       |
| 6   | 6 (Ciabatta)   | 10       | 30     | 8       | 45    | 21       | 10       | 5        | 50       |
| 7   | 7 (Baguette)   | 10       | 25     | 12      | 45    | 21       | 10       | 5        | 45       |
| 8   | 8 (Dobladita)  | 13       | 15     | 10      | 20    | 14       | 7        | 3        | 50       |
| 9   | 9 (Boc.Dama)   | 12       | 15     | 10      | 30    | 14       | 7        | 3        | 25       |
| 10  | 10 (Amasado)   | 15       | 20     | 10      | 35    | 18       | 8        | 4        | 60       |

> **Cómo referenciar**: En un Server, poner Processing Time = `TableProceso[EntLote.EStaTipoPan].TiempoMezcladoAuto`

### Paso 2.2 — Tabla de Probabilidades de Elección por Hora ✅

**Data** → **Add Data Table** → Nombre: `TableProbEleccion`

**Columnas**: `HoraID` (Integer), y para cada tipo de pan **dos columnas**:

- `PMarraqueta` (Real) — probabilidad marginal
- `PHallulla` (Real), `PMarrInt` (Real), `PHallInt` (Real), `PHotDog` (Real), `PCiabatta` (Real), `PBaguette` (Real), `PDobladita` (Real), `PBocDama` (Real), `PAmasado` (Real)

**12 filas** (una por hora, datos de la sección 3.9 del reporte):

| Row | HoraID | PMarraq | PHallulla | PMarrInt | PHallInt | PHotDog | PCiabatta | PBaguette | PDoblad | PBocDama | PAmasado |
| --- | ------ | ------- | --------- | -------- | -------- | ------- | --------- | --------- | ------- | -------- | -------- |
| 1   | 1      | 0.2645  | 0.2248    | 0.1247   | 0.1164   | 0.0546  | 0.0374    | 0.0327    | 0.0720  | 0.0453   | 0.0277   |
| 2   | 2      | 0.2645  | 0.2248    | 0.1247   | 0.1164   | 0.0546  | 0.0374    | 0.0327    | 0.0720  | 0.0453   | 0.0277   |
| 3   | 3      | 0.2645  | 0.2248    | 0.1247   | 0.1164   | 0.0546  | 0.0374    | 0.0327    | 0.0720  | 0.0453   | 0.0277   |
| 4   | 4      | 0.2313  | 0.1966    | 0.1090   | 0.1018   | 0.1534  | 0.0525    | 0.0459    | 0.0434  | 0.0273   | 0.0390   |
| 5   | 5      | 0.2505  | 0.2129    | 0.1181   | 0.1102   | 0.0831  | 0.0569    | 0.0498    | 0.0470  | 0.0295   | 0.0422   |
| 6   | 6      | 0.2505  | 0.2129    | 0.1181   | 0.1102   | 0.0831  | 0.0569    | 0.0498    | 0.0470  | 0.0295   | 0.0422   |
| 7   | 7      | 0.2645  | 0.2248    | 0.1247   | 0.1164   | 0.0546  | 0.0374    | 0.0327    | 0.0720  | 0.0453   | 0.0277   |
| 8   | 8      | 0.2645  | 0.2248    | 0.1247   | 0.1164   | 0.0546  | 0.0374    | 0.0327    | 0.0720  | 0.0453   | 0.0277   |
| 9   | 9      | 0.2381  | 0.2024    | 0.1123   | 0.1048   | 0.1124  | 0.0438    | 0.0383    | 0.0649  | 0.0408   | 0.0424   |
| 10  | 10     | 0.1854  | 0.1576    | 0.0874   | 0.0816   | 0.2501  | 0.0708    | 0.0619    | 0.0225  | 0.0141   | 0.0687   |
| 11  | 11     | 0.1897  | 0.1612    | 0.0894   | 0.0835   | 0.2326  | 0.0724    | 0.0634    | 0.0230  | 0.0145   | 0.0703   |
| 12  | 12     | 0.2584  | 0.2196    | 0.1218   | 0.1137   | 0.0762  | 0.0365    | 0.0320    | 0.0704  | 0.0442   | 0.0271   |

#### Paso 2.2b — Variables auxiliares para probabilidad condicional (2ª/3ª selección) ❓🛐

> **Ref. teórica (sección 3.10 del reporte)**: Cuando un cliente compra 2 o 3 tipos **diferentes**, la selección del 2º tipo se realiza **sin reemplazo**:
>
> P(2º = j | 1º = i) = Pⱼ / (1 − Pᵢ), para j ≠ i
>
> P(3º = k | 1º = i, 2º = j) = Pₖ / (1 − Pᵢ − Pⱼ), para k ≠ i,j
>
> Esto se implementa en SIMIO usando **variables de estado temporales** dentro de un Process (ver Paso 7.1), **no** con tablas precalculadas, ya que el cálculo depende de qué tipo se eligió previamente.

**Variables de estado adicionales en `EntCliente`** (agregar a las ya definidas en Paso 1.2):

Ir a **Navigation Panel** → clic en `EntCliente` → pestaña **Definitions** → **States**:

| State Variable                        | Tipo          | Nombre            | Uso                                                    |
| ------------------------------------- | ------------- | ----------------- | ------------------------------------------------------ |
| Prob. restante después del 1er tipo  | Discrete Real | `EStaProbRest1` | Almacena `1 − P(tipo1)` para normalizar             |
| Prob. restante después del 2do tipo  | Discrete Real | `EStaProbRest2` | Almacena `1 − P(tipo1) − P(tipo2)` para normalizar |
| Número aleatorio para 2ª selección | Discrete Real | `EStaRand2`     | U(0,1) escalado para selección condicional            |
| Número aleatorio para 3ª selección | Discrete Real | `EStaRand3`     | U(0,1) escalado para selección condicional            |

> **¿Por qué no precalcular las condicionales en tablas?** Con 10 tipos × 12 horas × 10 posibles primeras selecciones = 1.200 filas solo para el 2º tipo, más 10.800 para el 3º. El enfoque algorítmico (calcular en el Process) es mucho más manejable y flexible.
>
> **Ref. Workbook §7.2**: "Add-On Process Triggers" y "Assign Step" permiten realizar cálculos arbitrarios sobre state variables de la entidad antes de que esta salga del Source, exactamente lo que necesitamos para el muestreo condicional.

### Paso 2.3 — Tabla de Compra por Tipo (distribuciones triangulares) ✅

**Data** → **Add Data Table** → Nombre: `TableCompra`

| Row | TipoPanID | TriMin | TriModa | TriMax |
| --- | --------- | ------ | ------- | ------ |
| 1   | 1         | 0.3    | 1.0     | 2.0    |
| 2   | 2         | 0.3    | 1.0     | 2.0    |
| 3   | 3         | 0.3    | 0.5     | 2.0    |
| 4   | 4         | 0.3    | 0.7     | 1.5    |
| 5   | 5         | 0.3    | 1.0     | 3.0    |
| 6   | 6         | 0.3    | 0.5     | 1.5    |
| 7   | 7         | 0.3    | 0.5     | 1.0    |
| 8   | 8         | 0.3    | 0.5     | 1.5    |
| 9   | 9         | 0.3    | 0.5     | 1.0    |
| 10  | 10        | 0.3    | 0.8     | 2.0    |

> Para generar cantidad: `Random.Triangular(TableCompra[tipo].TriMin, TableCompra[tipo].TriModa, TableCompra[tipo].TriMax)`

### Paso 2.4 — Tabla de Plan de Producción (secuencia base fija) ✅

> **Ref. Reporte §3.5**: Se requieren ~155 lotes/día. Esta tabla define la **secuencia base** de producción, agrupada por familia para minimizar setups de horno. Es la componente "fija" del enfoque híbrido.

**Data** → **Add Data Table** → Nombre: `TablePlanProduccion`

**Columnas**:

| Columna            | Tipo    | Descripción                                                          |
| ------------------ | ------- | --------------------------------------------------------------------- |
| `PlanRow`        | Integer | Número secuencial 1–155                                             |
| `PlanTipoPan`    | Integer | ID del tipo (1–10)                                                   |
| `PlanFamilia`    | Integer | Familia de horneado (1–3), redundante pero útil para filtrar        |
| `PlanKgLote`     | Real    | Kg del batch (de `TableProceso`)                                    |
| `PlanHoraLib`    | Real    | Hora de liberación en minutos desde inicio simulación (t=0 = 06:00) |
| `PlanEsReactivo` | Integer | 0 = lote planificado, 1 = lote inyectado reactivamente                |

**Criterio de secuenciamiento**: Los lotes se ordenan por:

1. **Hora de liberación** (ascendente) — para que la producción sea continua
2. **Familia** (agrupados) — para minimizar setups del horno
3. **Demanda descendente** dentro de familia — los tipos de mayor demanda primero

**Primeras filas de ejemplo** (total: 155 filas):

| Row | PlanTipoPan    | PlanFamilia | PlanKgLote | PlanHoraLib | Nota                     |
| --- | -------------- | ----------- | ---------- | ----------- | ------------------------ |
| 1   | 1 (Marraqueta) | 2           | 60         | 0           | Pre-apertura bloque Fam2 |
| 2   | 1 (Marraqueta) | 2           | 60         | 5           |                          |
| 3   | 2 (Hallulla)   | 2           | 55         | 10          |                          |
| 4   | 2 (Hallulla)   | 2           | 55         | 15          |                          |
| 5   | 10 (Amasado)   | 2           | 60         | 20          |                          |
| 6   | 4 (Hall.Int)   | 2           | 55         | 25          |                          |
| 7   | 5 (Hot Dog)    | 1           | 55         | 30          | Cambio a Fam1            |
| 8   | 8 (Dobladita)  | 1           | 50         | 35          |                          |
| 9   | 9 (Boc.Dama)   | 1           | 25         | 40          |                          |
| 10  | 3 (Marr.Int)   | 3           | 60         | 45          | Cambio a Fam3            |
| 11  | 6 (Ciabatta)   | 3           | 50         | 50          |                          |
| 12  | 7 (Baguette)   | 3           | 45         | 55          |                          |
| 13  | 1 (Marraqueta) | 2           | 60         | 60          | Ciclo 2, vuelta a Fam2   |
| ... | ...            | ...         | ...        | ...         |                          |

> **Cómo completar las 155 filas**: Distribuir los batches de cada tipo (§3.5 del reporte: 34 Marraqueta, 31 Hallulla, 22 Hot Dog, etc.) a lo largo de las 10 horas de producción (06:00–16:00), agrupando por familia en bloques de 5–8 lotes para llenar corridas de horno.

> **Interarrival base**: Con 155 lotes en ~600 min productivos → 1 lote cada ~3.9 min. Se puede usar `PlanHoraLib` directamente o un interarrival fijo de ~4 min.

### Paso 2.5 — Tabla de Demanda Esperada por Hora y Tipo ✅

> Esta tabla es la componente **reactiva** del enfoque híbrido. Permite calcular el déficit por tipo para decidir si inyectar lotes de emergencia.

**Data** → **Add Data Table** → Nombre: `TableDemandaHora`

**Columnas**: `HoraID` (Integer), más una columna `DemKg_T1`...`DemKg_T10` (Real) para cada tipo.

**Cálculo**: Demanda esperada (kg/hora) = Clientes/hora × P(tipo, hora) × E[kg/compra] × NTiposPromedio

Donde: NTiposPromedio = 1×0.50 + 2×0.35 + 3×0.15 = **1.65**

| HoraID   | DemKg_T1 | DemKg_T2 | DemKg_T3 | DemKg_T4 | DemKg_T5 | DemKg_T6 | DemKg_T7 | DemKg_T8 | DemKg_T9 | DemKg_T10 |
| -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- | --------- |
| 1 (09h)  | 120      | 102      | 57       | 53       | 25       | 17       | 15       | 33       | 21       | 13        |
| 4 (12h)  | 168      | 143      | 79       | 74       | 111      | 38       | 33       | 31       | 20       | 28        |
| 10 (18h) | 251      | 213      | 118      | 110      | 338      | 96       | 84       | 30       | 19       | 93        |
| 11 (19h) | 252      | 215      | 119      | 111      | 310      | 96       | 84       | 31       | 19       | 94        |

> **Nota**: Completar las 12 filas usando la fórmula. Las filas 10–11 (18:00–20:00) son las de mayor demanda; el plan base debe tener producción adelantada para cubrirlas.

---

## FASE 3: Variables de Estado del Modelo (Globales) ✅

Ir a **Navigation Panel** → clic en **Model** → **Definitions** → **States**:

#### Variables de inventario y estadísticas

| Variable                   | Tipo                     | Nombre                  | Descripción                    |
| -------------------------- | ------------------------ | ----------------------- | ------------------------------- |
| Inventario actual          | Real (Vector, dim=10)    | `MStaInventario`      | Kg disponibles en sala por tipo |
| Quiebres acumulados        | Real (Vector, dim=10)    | `MStaQuiebres`        | Kg perdidos por tipo            |
| Ventas acumuladas          | Real (Vector, dim=10)    | `MStaVentas`          | Kg vendidos por tipo            |
| Lotes producidos           | Integer (Vector, dim=10) | `MStaLotesProducidos` | Batches completados             |
| Cola horno familia         | Real (Vector, dim=3)     | `MStaColaHorno`       | Kg esperando horno              |
| Hora actual (índice 1-12) | Integer                  | `MStaHoraIdx`         | Índice para tablas horarias    |

#### Variables de control de producción (Enfoque Híbrido)

| Variable                   | Tipo                  | Nombre                 | Descripción                                                |
| -------------------------- | --------------------- | ---------------------- | ----------------------------------------------------------- |
| Lote actual del plan       | Integer               | `MStaLotePlanActual` | Índice de la fila actual en `TablePlanProduccion`        |
| Kg en proceso por tipo     | Real (Vector, dim=10) | `MStaEnProceso`      | Kg actualmente en el flujo productivo (aún no en sala)     |
| Flag de lote reactivo      | Integer               | `MStaEsReactivo`     | 1 si el próximo lote a crear es reactivo, 0 si es del plan |
| Tipo reactivo pendiente    | Integer               | `MStaTipoReactivo`   | Tipo de pan a producir cuando `MStaEsReactivo=1`          |
| Lotes reactivos inyectados | Integer               | `MStaLotesReactivos` | Contador total de lotes extra inyectados                    |

> **Nota sobre vectores**: En SIMIO, los vectores se definen con dimensión en la propiedad "Rows" del State Variable.

> **`MStaEnProceso`**: Se incrementa cuando un lote entra a `SrvPesado` y se decrementa cuando llega a `SnkLoteTerminado`. Esto permite al sistema reactivo saber cuánto pan está "en camino" y no duplicar producción innecesariamente.

---

> **Continúa en Parte 2**: Objetos del Facility (Sources, Servers, Sinks), Rate Tables para arribos NHPP, y Work Schedules.
