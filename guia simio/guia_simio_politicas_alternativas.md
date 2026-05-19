# Guía de Implementación en SIMIO — Alternativas de Políticas de Producción y Secuencia de Horno

> **Referencia**: Basada en el Workbook SIMIO 6th Ed. y el análisis pre-modelación (§5.5.1–§5.5.3).
> **Objetivo**: Proveer el paso a paso para configurar y probar en SIMIO las alternativas de **políticas de producción** (qué y cuándo producir) y **políticas de secuencia de horno** (qué familia hornear primero cuando compiten por un horno libre).

---

## PARTE I: POLÍTICAS DE PRODUCCIÓN

Para facilitar la experimentación, sugerimos crear una propiedad en el modelo (`Model` → `Definitions` → `Properties` → `Add Integer Property`) llamada **`PropPoliticaProduccion`**, donde:
- **1** = Secuencial Predefinida (Actual Enfoque Híbrido)
- **2** = Política PULL (Puntos de Reorden / Kanban)
- **3** = Prioridad Dinámica (JIT / Criticidad)
- **4** = Bloques Horarios (Time-Bucketing)

Puedes usar esta propiedad en los `Decide` steps de tus procesos principales para enrutar la lógica según la política activa en el experimento.

### ALTERNATIVA 1: Política PULL Pura (Kanban / Min-Max)

Esta política reemplaza la tabla de secuencia estática. El sistema solo produce cuando el inventario (más lo que está en proceso) cae por debajo de un umbral crítico.

### Fase A: Parámetros del Sistema PULL

> **Separación de responsabilidades**: Los parámetros de política PULL **no** se agregan a `TableProceso` (que contiene tiempos de proceso por estación). Se requiere una tabla dedicada.

1. Ir a **Data** → **Tables** → **Add Data Table** → Nombrar `TablePoliticaPull`.
2. Agregar **3 columnas**:

| Columna | Tipo | Descripción | Fuente del valor |
|---|---|---|---|
| `TipoID` | Integer | Identificador del tipo de pan (1–10) | Manual (1 a 10, en orden) |
| `PuntoReorden_kg` | Real | Inventario posición mínimo $s$ (kg) que dispara producción | `data/analisis_eoq_rop.csv`, columna `ROP_kg` |
| `LotesAReponer` | Integer | Cantidad de batches a crear cuando se cruza el ROP | `Math.Ceiling(EOQ_kg / KgPorBatch)` por tipo |

3. Poblar las **10 filas** con los valores de `data/analisis_eoq_rop.csv` generado por `generar_eoq.py`. La fila con `TipoID = i` corresponde al tipo de pan `i`.

> **Importante**: En todas las expresiones de Fase C, usar `TablePoliticaPull[Token.TipoActual].PuntoReorden_kg` y `TablePoliticaPull[Token.TipoActual].LotesAReponer` (no columnas de `TableProceso`).

### Fase B: Proceso Monitor de Inventario

En lugar de generar lotes cada 4 minutos con un `Interarrival Time`, un Timer periódico revisa los 10 tipos de pan y crea lotes cuando el inventario posición baja del ROP.

#### B.1 — Timer
1. Ir a **Definitions** → **Elements** → **Timers** → Crear `TimerRevisionPull`.
   - **Time Interval**: `3` (minutos).

> **Por qué 3 min**: El pipeline completo dura ~80 min. Un intervalo de 5 min introduce latencia innecesaria durante el peak 18:00–20:00. Con 3 min el sistema detecta el déficit más rápido sin sobrecargar el motor de eventos.

#### B.2 — Variable de bloqueo anti-solapamiento

Si el proceso tarda más de 3 minutos en ejecutarse (muchos tipos bajo ROP), el Timer puede dispararlo de nuevo antes de que termine el anterior. Eso causaría **doble-conteo en `MStaEnProceso`** y creación duplicada de lotes. Se necesita un semáforo.

1. Ir a **Definitions** → **States** → **Add State** → Tipo **Discrete (Integer)**:
   - **Name**: `MStaBloqueoPull`
   - **Rows**: `1`
   - **Initial Value**: `0`
   - Semántica: `0` = proceso libre, `1` = proceso en ejecución. Si el Timer dispara y encuentra `1`, termina sin hacer nada.

#### B.3 — Proceso ProcControlPull
1. Ir a **Definitions** → **Processes** → Crear `ProcControlPull`.
   - **Triggering Event**: `TimerRevisionPull.Event`
2. En las propiedades del proceso, ir a **Token States** → **Add State** (dos entradas):

| Nombre | Tipo | Propósito |
|---|---|---|
| `TipoActual` | Integer | Índice del tipo de pan en la iteración actual (1–10) |
| `LotesCreados` | Integer | Contador del loop interno de creación de lotes |

### Fase C: Lógica del Proceso (`ProcControlPull`)

El proceso recorre los 10 tipos de pan en secuencia, evalúa el inventario posición de cada uno, y crea los lotes necesarios.

> **Arquitectura del Step Create en SIMIO**: El step `Create` tiene **dos salidas**:
> - **Salida principal (token)**: El token del proceso (el hilo de control) continúa por aquí. Se usa para incrementar `LotesCreados` y volver al loop.
> - **Puerto `Created` (entidad nueva)**: La entidad recién creada fluye por aquí. Se usa para asignar sus atributos. Una vez que los steps conectados al puerto `Created` terminan (EndProcess de esa rama), SIMIO libera la entidad al `Starting Node` en la Facility.
>
> Estas dos salidas corren en paralelo: el token del proceso sigue su camino mientras la entidad se inicializa por el puerto `Created`.

#### Steps del proceso

**Bloque 0 — Filtros de entrada**

| Nº | Step | Configuración | Salida |
|---|---|---|---|
| 0a | **Decide** | `Model.PropPoliticaProduccion == 2` | False → `EndProcess` \| True → paso 0b |
| 0b | **Decide** | `Model.MStaBloqueoPull == 1` | True → `EndProcess` (ya hay una ejecución activa) \| False → paso 0c |
| 0c | **Assign** | `Model.MStaBloqueoPull = 1` | → paso 1 |

**Bloque 1 — Inicialización del loop principal**

| Nº | Step | Configuración |
|---|---|---|
| 1 | **Assign** | `Token.TipoActual = 1` |

**Bloque 2 — Evaluación de inventario posición**

> La condición compara *inventario posición* = on-hand + on-order (lo que ya está en el pipeline) contra el ROP. Esto evita crear lotes duplicados para batches que ya están en proceso.

| Nº | Step | Configuración | Salida |
|---|---|---|---|
| 2 | **Decide** | `Model.MStaInventario[Token.TipoActual] + Model.MStaEnProceso[Token.TipoActual] <= TablePoliticaPull[Token.TipoActual].PuntoReorden_kg` | True → paso 3 \| False → paso 6 |

**Bloque 3 — Loop de creación de lotes**

| Nº | Step | Configuración | Salida |
|---|---|---|---|
| 3 | **Assign** | `Token.LotesCreados = 0` | → paso 4 |
| 4 | **Decide** | `Token.LotesCreados < TablePoliticaPull[Token.TipoActual].LotesAReponer` | True → paso 5 \| False → paso 6 |

**Bloque 4 — Creación de 1 lote (rama True del paso 4)**

| Nº | Step | Puerto | Configuración |
|---|---|---|---|
| 5 | **Create** | — | Entity Type: `EntLote`, Number of Entities: `1`, Starting Node: `Input@SrvPesado` ¹ |
| 5-C1 | **Assign** | `Created` ← *entidad* | `EntLote.EStaTipoPan = Token.TipoActual` |
| 5-C2 | **Assign** | `Created` (continúa) | `EntLote.EStaFamilia = TableProceso[Token.TipoActual].FamiliaID` |
| 5-C3 | **Assign** | `Created` (continúa) | `EntLote.EStaKgLote = TableProceso[Token.TipoActual].KgPorBatch` |
| 5-C4 | **Assign** | `Created` (continúa) | `Model.MStaEnProceso[Token.TipoActual] = Model.MStaEnProceso[Token.TipoActual] + EntLote.EStaKgLote` ² |
| 5-C5 | **EndProcess** | `Created` (cierra) | Libera la entidad al `Starting Node`. SIMIO la envía a `Input@SrvPesado`. |
| 5-T | **Assign** | Salida principal ← *token* | `Token.LotesCreados = Token.LotesCreados + 1` → vuelve al **paso 4** |

> ¹ `Input@SrvPesado` es el nombre interno del nodo de entrada del servidor `SrvPesado`. Si el servidor tiene otro nombre en el modelo, ajustar aquí.
>
> ² El incremento de `MStaEnProceso` ocurre en el puerto `Created` (en el contexto de la entidad) para garantizar que el contador se actualiza **antes** de que la entidad entre a la Facility y antes de que el timer pueda dispararse de nuevo.

**Bloque 5 — Avance al siguiente tipo (convergencia de falsas)**

Los pasos 6-8 son alcanzados tanto por la rama False del paso 2 (no hay déficit) como por la rama False del paso 4 (ya se crearon todos los lotes necesarios).

| Nº | Step | Configuración | Salida |
|---|---|---|---|
| 6 | **Assign** | `Token.TipoActual = Token.TipoActual + 1` | → paso 7 |
| 7 | **Decide** | `Token.TipoActual <= 10` | True → vuelve al **paso 2** \| False → paso 8 |
| 8 | **Assign** | `Model.MStaBloqueoPull = 0` | → paso 9 |
| 9 | **EndProcess** | — | Fin del proceso. El semáforo queda en 0 para el próximo disparo del Timer. |

---

### Fase D: Decremento de `MStaEnProceso` al completar el pipeline

> **Este paso es obligatorio.** Sin él, `MStaEnProceso[i]` crece sin límite y la condición del paso 2 nunca vuelve a ser verdadera: el sistema PULL queda paralizado después del primer ciclo.

El decremento debe ocurrir cuando el lote **termina el pipeline completo** y llega a la góndola (inventario). Ese momento es el evento de salida del paso de Reposición (último servidor antes del Sink, o el proceso `ProcActualizarInventario` que gestiona el inventario en sala).

#### D.1 — Dónde agregar el decremento

Localiza el proceso o el nodo donde actualmente se incrementa `MStaInventario` (registro de stock en sala). Puede ser:

- Un proceso `ProcActualizarInventario` disparado al terminar el enfriado, o
- El evento `Exited` del último servidor del pipeline (p.ej. `SrvEnfriado` o `SrvReposicion`).

#### D.2 — Assigns a agregar

En ese punto del proceso, **inmediatamente antes o después** del assign que suma al inventario, agregar:

```
// Decremento: el lote ya no está "en proceso", ahora está en sala
Model.MStaEnProceso[EntLote.EStaTipoPan] =
    Model.MStaEnProceso[EntLote.EStaTipoPan] - EntLote.EStaKgLote

// Incremento de inventario en sala (si no existe aún, agregar aquí)
Model.MStaInventario[EntLote.EStaTipoPan] =
    Model.MStaInventario[EntLote.EStaTipoPan] + EntLote.EStaKgLote
```

En SIMIO (tabla de Assign steps):

| Sub-step | State Variable | New Value |
|---|---|---|
| D-1 | `Model.MStaEnProceso[EntLote.EStaTipoPan]` | `Model.MStaEnProceso[EntLote.EStaTipoPan] - EntLote.EStaKgLote` |
| D-2 | `Model.MStaInventario[EntLote.EStaTipoPan]` | `Model.MStaInventario[EntLote.EStaTipoPan] + EntLote.EStaKgLote` |

#### D.3 — Decremento de inventario por despacho al cliente

El inventario también debe decrementarse cuando el cliente compra. Ese assign debe existir en el proceso de atención al cliente. Verificar que esté presente:

| Sub-step | State Variable | New Value |
|---|---|---|
| C-1 | `Model.MStaInventario[TipoPanComprado]` | `Model.MStaInventario[TipoPanComprado] - kg_comprados` |

Sin este assign, `MStaInventario` nunca baja y el ROP nunca se cruza.

---

### ALTERNATIVA 2: Política de Prioridad Dinámica (Índice de Criticidad)

Esta política elimina el flujo periódico. Los lotes se generan bajo demanda "justo a tiempo" (JIT) en el momento en que los operarios / máquinas están libres para procesarlos, evaluando quién tiene la mayor urgencia.

### Fase A: Configuración del Disparador
La producción debe inyectarse cuando la línea lo permita. Puedes usar el evento de salida del operario o la mezcladora. 
Para simplificar: usaremos un **Timer** muy frecuente, pero que solo avanza si hay capacidad disponible.

1. Crear `TimerCriticidad` con Interval de `2` minutos.
2. Ir a **Definitions** → **Processes** → Crear `ProcGenerarLoteCritico`.
   - **Triggering Event**: `TimerCriticidad.Event`
   - **Token States**: En las propiedades del proceso, agregar: `TipoCritico` (Integer), `Indice` (Integer), `MaxCriticidad` (Real), `CritActual` (Real), y `DemandaActual` (Real).

### Fase B: Lógica de Búsqueda del Más Crítico (`ProcGenerarLoteCritico`)
1. **Step Decide** (Filtro de Política y Capacidad):
   - Condition: `Model.PropPoliticaProduccion == 3 AND (SrvPesado.InputBuffer.Contents < 2)` (Para no inundar el sistema).
   - **False**: `EndProcess`.
   - **True**: Continúa.
2. **Step Assign** (Inicializar): 
   - `Token.MaxCriticidad = -9999`
   - `Token.TipoCritico = 0`
   - `Token.Indice = 1`
3. **Bloque de Loop (1 a 10)**:
   - **Assign** (Extraer demanda actual): 
     - *SIMIO no permite indexar columnas dinámicamente (`Dem1`, `Dem2`, etc.). Se usa una suma condicional:*
     - `Token.DemandaActual = (Token.Indice==1)*TableDemandaHora[Model.MStaHoraIdx].Dem1 + (Token.Indice==2)*TableDemandaHora[Model.MStaHoraIdx].Dem2 + ... + (Token.Indice==10)*TableDemandaHora[Model.MStaHoraIdx].Dem10`
   - **Assign** (Calcular Criticidad): 
     - `Token.CritActual = (Token.DemandaActual - Model.MStaInventario[Token.Indice] - Model.MStaEnProceso[Token.Indice]) / TableProceso[Token.Indice].KgPorBatch`
     > *Tip: Sumar extra puntos si `TableProceso[Token.Indice].FamiliaID` es igual a la última familia horneada, para minimizar Setups.*
   - **Decide**: `Token.CritActual > Token.MaxCriticidad`
   - **Rama True**: `Token.MaxCriticidad = Token.CritActual`, `Token.TipoCritico = Token.Indice`.
   - Ambas ramas van a: **Step Assign**: `Token.Indice = Token.Indice + 1`
   - **Step Decide** (Loop): `Token.Indice <= 10`
     - **True**: Vuelve al inicio del Step Assign para extraer demanda.
     - **False**: Continúa al siguiente paso.
4. **Step Decide (Post-Loop)**:
   - Condition: `Token.TipoCritico > 0`
5. **Rama True (Crear Lote)**:
   - **Step Create**: Entity Type: `EntLote`, Number of Entities: `1`, Starting Node: `Input@SrvPesado`.
   - **Step Assign** (en nodo `Created`): 
     - `EntLote.EStaTipoPan = Token.TipoCritico`
     - `EntLote.EStaFamilia = TableProceso[Token.TipoCritico].FamiliaID`
     - `EntLote.EStaKgLote = TableProceso[Token.TipoCritico].KgPorBatch`
     - `Model.MStaEnProceso[Token.TipoCritico] = Model.MStaEnProceso[Token.TipoCritico] + EntLote.EStaKgLote`

---

### ALTERNATIVA 3: Producción por Bloques Horarios (Time-Bucketing Dinámico)

Similar a la versión híbrida actual, pero recalcula el plan masivo en horas específicas del día en lugar de depender de una tabla estática para los 155 lotes completos.

### Fase A: Disparador por Bloques
1. Ir a **Definitions** → **Elements** → **Timers** → Crear `TimerBloqueHorario`.
   - En lugar de un intervalo fijo, puedes configurarlo con un intervalo de `240` minutos (4 horas). Ej: evalúa a las 06:00, 10:00, 14:00.

### Fase B: Lógica de Planificación en Bloque (`ProcGenerarBloque`)
1. Ir a **Definitions** → **Processes** → Crear `ProcGenerarBloque`.
   - **Triggering Event**: `TimerBloqueHorario.Event`
   - **Token States**: Añadir `Tipo` (Integer), `LotesCreados` (Integer), `DeficitBloque` (Real), `DemandaProximas4Horas` (Real), y `NumLotes` (Integer).
2. **Step Decide** (Filtro de Política):
   - Condition: `Model.PropPoliticaProduccion == 4`
   - **False**: `EndProcess`.
   - **True**: Continúa.
3. **Step Assign** (Inicializar): `Token.Tipo = 1`
4. **Bloque de Loop (1 a 10)**:
   - **Assign**: Calcula `Token.DemandaProximas4Horas`. *(Pre-calcular esto en una columna de la tabla `TableDemandaHora` llamada `DemAcum4h`, o sumarlo condicionalmente).*
   - **Assign**: `Token.DeficitBloque = Token.DemandaProximas4Horas - Model.MStaInventario[Token.Tipo] - Model.MStaEnProceso[Token.Tipo]`
   - **Decide**: `Token.DeficitBloque > 0`
   - **Rama True**:
     - **Assign** (Fórmula de redondeo hacia arriba, SIMIO no tiene Math.Ceiling): `Token.NumLotes = Math.Floor((Token.DeficitBloque + TableProceso[Token.Tipo].KgPorBatch - 0.01) / TableProceso[Token.Tipo].KgPorBatch)`
     - **Assign** (Iniciar loop de creación): `Token.LotesCreados = 0`
     - **Decide** (Loop): `Token.LotesCreados < Token.NumLotes`
       - **True**: 
         - **Step Create**: 1 entidad en `Input@SrvPesado`.
         - **Step Assign** (En nodo `Created`): Asignar atributos (`EStaTipoPan = Token.Tipo`, `EStaFamilia`, `EStaKgLote`, sumar a `MStaEnProceso`) y prioridad: `EntLote.Priority = TableProceso[Token.Tipo].FamiliaID`.
         - **Step Assign** (Flujo principal de Create): `Token.LotesCreados = Token.LotesCreados + 1` y vuelve al Decide de creación.
   - **Convergencia**: **Step Assign**: `Token.Tipo = Token.Tipo + 1`
   - **Step Decide** (Fin loop tipos): `Token.Tipo <= 10`
     - **True**: Vuelve al inicio para el siguiente tipo.
     - **False**: FIN (`EndProcess`).

6. **Asignación Crucial (Prioridad de Familia)**:
   - En `SrvPesado` y las filas siguientes, asegúrate de que el **Ranking Rule** del Input Buffer esté en `Highest Priority First` o `Lowest Priority First` para que las familias se agrupen solas dentro de la cola basándose en la asignación hecha de `EntLote.Priority`.

---

## PARTE II: POLÍTICAS DE SECUENCIA DE HORNO

> **Ref. Reporte §5.5.3**: Estas políticas son **ortogonales** a las de producción. Las políticas de producción (Parte I) deciden **qué producir**. Las de secuencia de horno deciden **qué familia hornear primero** cuando hay múltiples familias compitiendo por un horno libre.

### Contexto: ¿Cuándo aplica la decisión?

La decisión se toma en `ProcPoliticaCargaHorno` (ver `guia_simio_paso7_5_opcionB.md`), en el momento en que hay un horno libre **y más de una familia tiene cola > 0**. Si solo una familia tiene cola, no hay decisión — se hornea esa.

### Preparación: Variables y propiedad de control

#### 1. Crear propiedad `PropPoliticaSecuenciaHorno`

`Model` → `Definitions` → `Properties` → `Add Integer Property`:

| Valor | Estrategia |
|---|---|
| **1** | A — Prioridad al menor stock en sala |
| **2** | B — Prioridad a la mayor demanda esperada |
| **3** | C — Secuencia fija F1→F2→F3 |
| **4** | D — Híbrida (stock + demanda + setup) |

#### 2. Crear variables de estado adicionales

Ir a **Definitions → States → Add State**:

| Nombre | Tipo | Rows | Valor Inicial | Propósito |
|---|---|---|---|---|
| `MStaUltimaFamiliaHorno` | Discrete (Integer) | — | `0` | Última familia horneada (para calcular setup) |
| `MStaSeqFamiliaActual` | Discrete (Integer) | — | `1` | Índice de la familia actual en la rotación fija (Estrategia C) |
| `MStaSetupsAcum` | Discrete (Integer) | — | `0` | Contador de setups realizados (métrica) |

#### 3. Crear tabla `TableStockFamilia` (vista agregada)

> Esta tabla **no es obligatoria** — puedes calcular los valores inline. Pero simplifica las expresiones.

Ir a **Data → Tables → Add Table**: `TableStockFamilia` con 3 filas (una por familia) y columnas:

| Columna | Tipo | Descripción |
|---|---|---|
| `FamiliaID` | Integer | 1, 2, 3 |
| `TiposIncluidos` | String | "5,8,9", "1,2,4,10", "3,6,7" (referencia) |

Los cálculos de stock y demanda se hacen inline en el Process (ver cada estrategia).

---

### Proceso central: `ProcSeleccionarFamiliaHorno`

Este proceso se invoca **dentro** de `ProcPoliticaCargaHorno` (Opción B), reemplazando la lógica directa del Step 6. En vez de hornear siempre la familia del lote que disparó el trigger, se evalúa cuál familia tiene prioridad.

**Ubicación**: Crear como process independiente en **Definitions → Processes**.

**Cuándo se invoca**: Cuando `ProcPoliticaCargaHorno` determina que hay que iniciar una corrida (Step 6), en lugar de hacer Fire directo, ejecuta `ProcSeleccionarFamiliaHorno` que decide **qué familia** entra al horno.

---

### ESTRATEGIA A: Prioridad al menor stock en sala

> **Lógica**: La familia con menos inventario en sala tiene prioridad. Ataca directamente los quiebres de stock.
>
> **Override de calidad**: Si una familia lleva ≥ 15 min esperando horno (su masa está al límite de fermentación), obtiene prioridad absoluta sobre el criterio de stock, independientemente de los niveles de inventario. Entre varias familias en emergencia, gana la que lleva más tiempo esperando. Solo si ninguna familia está en emergencia se aplica el criterio de menor stock.

#### Token States requeridos

Añadir en las propiedades del proceso **`ProcSeleccionarFamiliaHorno`** → **Token States**:

| Nombre | Tipo | Propósito |
|---|---|---|
| `EsperaF1` | Real | Minutos que lleva esperando la cola de Familia 1 |
| `EsperaF2` | Real | Minutos que lleva esperando la cola de Familia 2 |
| `EsperaF3` | Real | Minutos que lleva esperando la cola de Familia 3 |
| `FamiliaEmergencia` | Integer | Familia en situación de calidad crítica (0 = ninguna) |
| `MaxEspera` | Real | Mayor tiempo de espera entre familias en emergencia |
| `StockF1` | Real | Stock agregado en sala de Familia 1 |
| `StockF2` | Real | Stock agregado en sala de Familia 2 |
| `StockF3` | Real | Stock agregado en sala de Familia 3 |
| `MinStock` | Real | Mínimo stock encontrado hasta ahora (para comparación) |
| `FamiliaElegida` | Integer | Resultado final: familia que entra al horno |

---

#### Steps del proceso

**Bloque 0 — Calcular tiempo de espera por familia**

> El multiplicador `(MStaColaHorno[f] > 0)` garantiza que si la cola está vacía, la espera se trate como 0 y no como el valor residual del timer anterior.

| Step | Tipo | Configuración |
|---|---|---|
| 0a | **Assign** | `Token.EsperaF1 = (Model.MStaColaHorno[1] > 0) * (Run.TimeNow - Model.MStaTimerHorno[1])` |
| 0b | **Assign** | `Token.EsperaF2 = (Model.MStaColaHorno[2] > 0) * (Run.TimeNow - Model.MStaTimerHorno[2])` |
| 0c | **Assign** | `Token.EsperaF3 = (Model.MStaColaHorno[3] > 0) * (Run.TimeNow - Model.MStaTimerHorno[3])` |

**Bloque 1 — Override de calidad: buscar familia en emergencia**

> Se recorre cada familia en orden. Si su espera supera los 15 min, se registra como candidata de emergencia. Si varias familias están en emergencia, gana la que lleva más tiempo.

| Step | Tipo | Configuración | Salida |
|---|---|---|---|
| 1a | **Assign** | `Token.FamiliaEmergencia = 0` `Token.MaxEspera = 0` | → 1b |
| 1b | **Decide** | `Token.EsperaF1 >= 15` | True → 1b-T \| False → 1c |
| 1b-T | **Assign** | `Token.FamiliaEmergencia = 1` `Token.MaxEspera = Token.EsperaF1` | → 1c |
| 1c | **Decide** | `Token.EsperaF2 >= 15 AND Token.EsperaF2 > Token.MaxEspera` | True → 1c-T \| False → 1d |
| 1c-T | **Assign** | `Token.FamiliaEmergencia = 2` `Token.MaxEspera = Token.EsperaF2` | → 1d |
| 1d | **Decide** | `Token.EsperaF3 >= 15 AND Token.EsperaF3 > Token.MaxEspera` | True → 1d-T \| False → 1e |
| 1d-T | **Assign** | `Token.FamiliaEmergencia = 3` | → 1e |
| 1e | **Decide** | `Token.FamiliaEmergencia > 0` | True → 1e-T (override activo) \| False → Bloque 2 |
| 1e-T | **Assign** | `Token.FamiliaElegida = Token.FamiliaEmergencia` | → Bloque 3 (saltarse Bloque 2) |

**Bloque 2 — Selección por menor stock (caso normal)**

> Solo se ejecuta cuando ninguna familia está en emergencia de calidad. Se inicializa `MinStock` en un valor imposiblemente alto (`9999999`) para que cualquier stock real lo supere en la primera comparación. La condición `MStaColaHorno[f] > 0` evita elegir una familia sin masa lista.

| Step | Tipo | Configuración | Salida |
|---|---|---|---|
| 2a | **Assign** | `Token.StockF1 = Model.MStaInventario[5] + Model.MStaInventario[8] + Model.MStaInventario[9]` | → 2b |
| 2b | **Assign** | `Token.StockF2 = Model.MStaInventario[1] + Model.MStaInventario[2] + Model.MStaInventario[4] + Model.MStaInventario[10]` | → 2c |
| 2c | **Assign** | `Token.StockF3 = Model.MStaInventario[3] + Model.MStaInventario[6] + Model.MStaInventario[7]` | → 2d |
| 2d | **Assign** | `Token.FamiliaElegida = 0` `Token.MinStock = 9999999` | → 2e |
| 2e | **Decide** | `Model.MStaColaHorno[1] > 0 AND Token.StockF1 < Token.MinStock` | True → 2e-T \| False → 2f |
| 2e-T | **Assign** | `Token.FamiliaElegida = 1` `Token.MinStock = Token.StockF1` | → 2f |
| 2f | **Decide** | `Model.MStaColaHorno[2] > 0 AND Token.StockF2 < Token.MinStock` | True → 2f-T \| False → 2g |
| 2f-T | **Assign** | `Token.FamiliaElegida = 2` `Token.MinStock = Token.StockF2` | → 2g |
| 2g | **Decide** | `Model.MStaColaHorno[3] > 0 AND Token.StockF3 < Token.MinStock` | True → 2g-T \| False → 2h |
| 2g-T | **Assign** | `Token.FamiliaElegida = 3` | → 2h |
| 2h | **Decide** | `Token.FamiliaElegida > 0` | True → Bloque 3 \| False → **EndProcess** (ninguna familia tiene cola) |

**Bloque 3 — Iniciar corrida de la familia elegida**

> Este bloque es el punto de convergencia de ambas rutas (override de calidad y selección por stock). Resetea la cola de la familia elegida, incrementa el contador de hornos en uso y dispara el evento de inicio de corrida. El reset del timer evita que el override de calidad se active de nuevo para lotes que aún no han llegado.

| Step | Tipo | Configuración |
|---|---|---|
| 3a | **Assign** | `Model.MStaColaHorno[Token.FamiliaElegida] = 0` |
| 3b | **Assign** | `Model.MStaTimerHorno[Token.FamiliaElegida] = 0` |
| 3c | **Assign** | `Model.MStaHornosEnUso = Model.MStaHornosEnUso + 1` |
| 3d | **Assign** | `Model.MStaUltimaFamiliaHorno = Token.FamiliaElegida` |
| 3e | **Fire** | Event: `EvtIniciarCorrida` |

> **Por qué resetear en Bloque 3 y no en Step 6 de `ProcPoliticaCargaHorno`**: El reset original (Step 6a del proceso de carga) usaba `EntLote.EStaFamilia`, que es la familia que *disparó* el umbral. Con Estrategia A, la familia elegida puede ser distinta. El reset debe hacerse sobre `Token.FamiliaElegida`, no sobre la familia disparadora. La familia que disparó el umbral pero no fue elegida conserva su cola y su timer: seguirá acumulando hasta que en la siguiente oportunidad de horno sea la de menor stock (o llegue a emergencia).

---

> **Índices de tipos por familia** (ref. reporte §3.1):
> - Familia 1 (14 min): tipos 5 (Hot Dog), 8 (Dobladita), 9 (Bocado de Dama)
> - Familia 2 (18 min): tipos 1 (Marraqueta), 2 (Hallulla), 4 (Hallulla Int.), 10 (Amasado)
> - Familia 3 (21 min): tipos 3 (Marraqueta Int.), 6 (Ciabatta), 7 (Baguette)

---

### ESTRATEGIA B: Prioridad a la mayor demanda esperada

> **Lógica**: La familia cuya demanda esperada en las próximas 2 horas es mayor tiene prioridad. Es proactiva — anticipa el peak.

#### Steps del Process

| Step | Tipo | Configuración |
|---|---|---|
| 1 | **Assign** | `Token.DemF1 = TableDemandaHora[Model.MStaHoraIdx].Dem5 + TableDemandaHora[Model.MStaHoraIdx].Dem8 + TableDemandaHora[Model.MStaHoraIdx].Dem9` |
| 2 | **Assign** | `Token.DemF2 = TableDemandaHora[Model.MStaHoraIdx].Dem1 + TableDemandaHora[Model.MStaHoraIdx].Dem2 + TableDemandaHora[Model.MStaHoraIdx].Dem4 + TableDemandaHora[Model.MStaHoraIdx].Dem10` |
| 3 | **Assign** | `Token.DemF3 = TableDemandaHora[Model.MStaHoraIdx].Dem3 + TableDemandaHora[Model.MStaHoraIdx].Dem6 + TableDemandaHora[Model.MStaHoraIdx].Dem7` |
| 4 | **Assign** | `Token.FamiliaElegida = 1`, `Token.MaxDem = Token.DemF1` |
| 5 | **Decide** | `Token.DemF2 > Token.MaxDem AND Model.MStaColaHorno[2] > 0` |
| 5T | **Assign** | `Token.FamiliaElegida = 2`, `Token.MaxDem = Token.DemF2` |
| 6 | **Decide** | `Token.DemF3 > Token.MaxDem AND Model.MStaColaHorno[3] > 0` |
| 6T | **Assign** | `Token.FamiliaElegida = 3` |
| 7 | **Decide** | `Model.MStaColaHorno[Token.FamiliaElegida] > 0` |
| 7T | **Assign** | Iniciar corrida de `Token.FamiliaElegida` |

> **Nota**: `TableDemandaHora` debe tener columnas `Dem1`…`Dem10` con la demanda en kg por tipo por franja (datos de `perfil_demanda_por_hora_panaderia.csv`). Si ya tienes la tabla con otro nombre, ajusta las referencias.

> **Ventaja sobre Estrategia A**: La Estrategia B anticipa demanda *futura*, mientras que A solo reacciona al stock *actual*. B es mejor para pre-cargar antes del peak 18:00–20:00.

---

### ESTRATEGIA C: Secuencia fija F1→F2→F3 (Round-Robin)

> **Lógica**: Las familias se hornean en orden cíclico fijo: 1 → 2 → 3 → 1 → 2 → 3 → ... Se salta la familia si su cola está vacía. Es la más simple y predecible.

#### Steps del Process

| Step | Tipo | Configuración |
|---|---|---|
| 1 | **Assign** | `Token.Intentos = 0` |
| 2 | **Decide** | `Model.MStaColaHorno[Model.MStaSeqFamiliaActual] > 0` |
| 2T | **Assign** | `Token.FamiliaElegida = Model.MStaSeqFamiliaActual` |
| 2T+ | **Assign** | Avanzar secuencia: `Model.MStaSeqFamiliaActual = (Model.MStaSeqFamiliaActual % 3) + 1` |
| 2T++ | **Assign** | Iniciar corrida de `Token.FamiliaElegida` |
| 2F | **Assign** | Saltar: `Model.MStaSeqFamiliaActual = (Model.MStaSeqFamiliaActual % 3) + 1` |
| 2F+ | **Assign** | `Token.Intentos = Token.Intentos + 1` |
| 3 | **Decide** | `Token.Intentos < 3` |
| 3T | → Volver a Step 2 | (probar la siguiente familia) |
| 3F | FIN | (las 3 familias tienen cola vacía — no hornear) |

> **Expresión `(X % 3) + 1`**: Implementa la rotación cíclica. Si `MStaSeqFamiliaActual = 1` → siguiente = `(1 % 3) + 1 = 2`. Si es 3 → `(3 % 3) + 1 = 1`. En SIMIO: `Math.Remainder(Model.MStaSeqFamiliaActual, 3) + 1`.

> **Esta es la estrategia que está implementada de facto** en el modelo actual (la secuencia del `TablePlanProduccion` agrupa por familia y el horno procesa en FIFO).

---

### ESTRATEGIA D: Híbrida (Stock + Demanda + Penalización de Setup)

> **Lógica**: Combina las tres dimensiones en un **índice de prioridad ponderado** por familia. Es la más sofisticada y la recomendada para la optimización final.

#### Fórmula del índice de prioridad

Para cada familia $f \in \{1, 2, 3\}$ con cola > 0:

$$
\text{Prioridad}_f = \underbrace{w_1 \times \frac{\text{DemandaEsperada}_f}{\text{Stock}_f + 1}}_{\text{urgencia}} - \underbrace{w_2 \times \text{Setup}_f}_{\text{penalización cambio}}
$$

donde:
- $w_1 = 1{,}0$ (peso de urgencia)
- $w_2 = 0{,}3$ (peso de penalización de setup)
- $\text{Setup}_f = 0$ si `MStaUltimaFamiliaHorno == f`, sino $\text{Setup}_f = 1$

Se hornea la familia con **mayor** `Prioridad_f`.

#### Steps del Process

| Step | Tipo | Configuración |
|---|---|---|
| 1–3 | **Assign** ×3 | Calcular `Token.StockF1`, `Token.StockF2`, `Token.StockF3` (igual que Estrategia A) |
| 4–6 | **Assign** ×3 | Calcular `Token.DemF1`, `Token.DemF2`, `Token.DemF3` (igual que Estrategia B) |
| 7 | **Assign** | `Token.PrioF1 = (Model.MStaColaHorno[1] > 0) * (Token.DemF1 / (Token.StockF1 + 1) - 0.3 * (Model.MStaUltimaFamiliaHorno != 1))` |
| 8 | **Assign** | `Token.PrioF2 = (Model.MStaColaHorno[2] > 0) * (Token.DemF2 / (Token.StockF2 + 1) - 0.3 * (Model.MStaUltimaFamiliaHorno != 2))` |
| 9 | **Assign** | `Token.PrioF3 = (Model.MStaColaHorno[3] > 0) * (Token.DemF3 / (Token.StockF3 + 1) - 0.3 * (Model.MStaUltimaFamiliaHorno != 3))` |
| 10 | **Assign** | `Token.FamiliaElegida = 1`, `Token.MaxPrio = Token.PrioF1` |
| 11 | **Decide** | `Token.PrioF2 > Token.MaxPrio` |
| 11T | **Assign** | `Token.FamiliaElegida = 2`, `Token.MaxPrio = Token.PrioF2` |
| 12 | **Decide** | `Token.PrioF3 > Token.MaxPrio` |
| 12T | **Assign** | `Token.FamiliaElegida = 3` |
| 13 | **Decide** | `Token.MaxPrio > 0` |
| 13T | **Assign** | Iniciar corrida + `Model.MStaUltimaFamiliaHorno = Token.FamiliaElegida` |
| 13F | FIN | (ninguna familia elegible) |

> **Nota SIMIO**: La expresión `(Model.MStaUltimaFamiliaHorno != 1)` devuelve 1 (true) o 0 (false) en SIMIO, lo que actúa como penalización binaria de setup. El `(Model.MStaColaHorno[f] > 0)` al inicio pone la prioridad a 0 si la familia no tiene cola.

#### Actualizar `MStaUltimaFamiliaHorno`

En **todos** los Steps de "Iniciar corrida" (Step 6 de `ProcPoliticaCargaHorno`), agregar un Assign adicional:

| Sub-step | State Variable | New Value |
|---|---|---|
| 6e | `Model.MStaUltimaFamiliaHorno` | `Token.FamiliaElegida` |
| 6f | `Model.MStaSetupsAcum` | `Model.MStaSetupsAcum + (Model.MStaUltimaFamiliaHorno != Token.FamiliaElegida)` |

---

### Integración con `ProcPoliticaCargaHorno`

El punto de integración es el **Step 6** del `ProcPoliticaCargaHorno` (ver `guia_simio_paso7_5_opcionB.md`). Actualmente, Step 6 inicia la corrida directamente con la familia del lote que disparó el trigger. Con las políticas de secuencia, se reemplaza por:

```
Step 6 original:
  Assign: MStaColaHorno[EntLote.EStaFamilia] = 0  ← REEMPLAZAR

Step 6 nuevo:
  Decide: PropPoliticaSecuenciaHorno == 1?
    → Ejecutar lógica Estrategia A (menor stock)
  Decide: PropPoliticaSecuenciaHorno == 2?
    → Ejecutar lógica Estrategia B (mayor demanda)
  Decide: PropPoliticaSecuenciaHorno == 3?
    → Ejecutar lógica Estrategia C (round-robin)
  Decide: PropPoliticaSecuenciaHorno == 4?
    → Ejecutar lógica Estrategia D (híbrida)
```

> **Alternativa más limpia**: Crear `ProcSeleccionarFamiliaHorno` como Process separado y usar un **Execute** step en Step 6 para invocarlo. Dentro del process, usar los Decide sobre `PropPoliticaSecuenciaHorno` para ramificar.

---

### Responses adicionales para evaluar secuencia de horno

Agregar en **Experiments → Responses**:

| Response | Expresión | Propósito |
|---|---|---|
| `SetupsHorno` | `Model.MStaSetupsAcum` | Nº de cambios de familia (cada uno = 5 min perdidos) |
| `TiempoPerdidoSetup` | `Model.MStaSetupsAcum * 5` | Minutos totales perdidos en setup |

---

## CÓMO EVALUAR LAS ALTERNATIVAS (Experimentos)

### Políticas de producción (Parte I)

Para configurar las políticas de producción en los Experimentos de SIMIO, necesitas usar un concepto llamado **Controls** (Controles). Los controles te permiten cambiar variables o propiedades del modelo para cada escenario sin tener que modificar la lógica base.

#### Paso 1: Crear las propiedades de control en el Modelo Base
1. Ve a la pestaña **Facility** o **Definitions**.
2. En el panel izquierdo, selecciona **Properties**.
3. Haz clic en **Add Integer Property**.
4. Nombra esta propiedad `PropPoliticaProduccion` (asegúrate de que el Default Value sea `1`).
5. (*Opcional pero recomendado*) En la ventana de Properties a la derecha, usa la propiedad `Description` para anotar qué significa cada número:
   * `1 = Híbrida/Secuencial`
   * `2 = PULL (Kanban)`
   * `3 = Dinámica (Criticidad)`
   * `4 = Bloques Horarios`

*(Debes hacer lo mismo creando `PropPoliticaSecuenciaHorno` para la Parte II).*

#### Paso 2: Vincular la Propiedad a los Procesos
Esto ya quedó implementado si seguiste las Fases C/B de las alternativas. Cada proceso (`ProcControlPull`, `ProcGenerarLoteCritico`, etc.) empieza con un **Step Decide** que evalúa si `Model.PropPoliticaProduccion` coincide con el número de su política correspondiente. Si no, termina (`EndProcess`).

#### Paso 3: Agregar el Control a la ventana de Experimentos
1. Ve a la pestaña **Project Home** y haz clic en **New Experiment** (o abre tu experimento existente).
2. Arriba en el menú (Ribbon), busca el botón **Add Control** (generalmente agrupado con las Responses).
3. Aparecerá un menú desplegable con todas las propiedades de tu modelo. Selecciona `PropPoliticaProduccion`.
4. Verás que aparece una nueva columna en la grilla (tabla) de tus escenarios.

#### Paso 4: Crear los Escenarios (Filas)
Ahora puedes configurar cada fila para que simule una política distinta bajo las **mismas condiciones de recursos**.

1. Haz clic derecho en la grilla y selecciona **Add Scenario** para crear 4 filas.
2. Nómbralas para que sean fáciles de identificar.
3. En la columna `PropPoliticaProduccion`, asigna el número correspondiente a cada política:

| Name | Replications | PropPoliticaProduccion | (Otros recursos: Mezcladoras, Panaderos...) |
| :--- | :--- | :--- | :--- |
| **Esc 1: Híbrido (Base)** | 10 | **1** | 5 Mezcladoras, 9 Panaderos... |
| **Esc 2: PULL Pura** | 10 | **2** | 5 Mezcladoras, 9 Panaderos... |
| **Esc 3: Dinámica (JIT)** | 10 | **3** | 5 Mezcladoras, 9 Panaderos... |
| **Esc 4: Bloques** | 10 | **4** | 5 Mezcladoras, 9 Panaderos... |

#### Paso 5: Correr y Comparar
1. Haz clic en el botón **Run** del experimento.
2. Observa tus columnas de **Responses** (`QuiebreTotalKg`, `UtilMezcladora`).
3. *Tip:* Haz clic en la pestaña **Measure Risk** o **Response Results** dentro del experimento para ver gráficos de caja (Box Plots). Esto te permitirá ver no solo qué política es mejor en promedio, sino cuál es menos variable o arriesgada.

> **Recomendación**: La Alternativa 3 (Bloques Horarios) suele ser la más equilibrada en entornos reales de supermercados, pero la Alternativa 2 (Dinámica) te mostrará la cota superior del nivel de servicio que tu configuración de máquinas puede lograr.

### Políticas de secuencia de horno (Parte II)

1. Añadir columna de control para `PropPoliticaSecuenciaHorno` en la grilla de Experiments.
2. Crear escenarios combinados (producción × secuencia):

| Escenario | Producción | Secuencia Horno | Descripción |
|---|---|---|---|
| Base | 1 (Híbrida) | 3 (Fija F1→F2→F3) | Configuración actual de facto |
| Sec-A | 1 (Híbrida) | 1 (Menor stock) | Reactiva a quiebres |
| Sec-B | 1 (Híbrida) | 2 (Mayor demanda) | Proactiva al peak |
| Sec-D | 1 (Híbrida) | 4 (Híbrida) | Equilibrio stock+demanda+setup |
| Full-Opt | 3 (Dinámica) | 4 (Híbrida) | Máxima optimización |

3. Comparar `QuiebreTotalKg`, `SetupsHorno` y `NivelServicioPct` entre escenarios.

> **Recomendación**: La Estrategia D (Híbrida) tiende a dar el mejor equilibrio. La Estrategia C minimiza setups pero puede generar quiebres al ignorar urgencia. La Estrategia A es la más reactiva pero puede causar muchos setups.
