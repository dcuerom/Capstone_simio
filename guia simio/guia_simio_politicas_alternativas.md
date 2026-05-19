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
1. Ir a **Data** → **Tables** → Seleccionar `TableProceso` (o crear una nueva tabla `TablePoliticaPull`).
2. Agregar dos columnas tipo **Real** o **Integer**:
   - `PuntoReorden`: El nivel de stock crítico ($s$) en kg que dispara la producción.
   - `LotesAReponer`: La cantidad de batches a producir ($Q$) cuando se alcanza el punto de reorden.

### Fase B: Proceso Monitor de Inventario
En lugar de generar lotes cada 4 minutos con un `Interarrival Time`, usaremos un proceso periódico (Timer) que revisa los 10 tipos de pan constantemente.

1. Ir a **Definitions** → **Elements** → **Timers** → Crear `TimerRevisionPull`.
   - **Time Interval**: `5` (minutos).
2. Ir a **Definitions** → **Processes** → Crear `ProcControlPull`.
   - **Triggering Event**: `TimerRevisionPull.Event`
   - Configurar **Token States**: En las propiedades del proceso, ir a **Token States** → **Add State** de tipo `Integer` llamado `TipoActual`. Añadir otro `Integer` llamado `LotesCreados`.

### Fase C: Lógica del Proceso (`ProcControlPull`)
El proceso recorre los 10 tipos de pan, evalúa su nivel de stock, y si amerita, crea los lotes.

1. **Step Decide** (Filtro de Política):
   - Condition: `Model.PropPoliticaProduccion == 2`
   - **False**: `EndProcess` (termina sin hacer nada).
   - **True**: Continúa al siguiente step.
2. **Step Assign** (Inicializar): `Token.TipoActual = 1`
3. **Step Decide** (Evaluación de Reorden): 
   - Condition (ejemplo asumiendo tabla consolidada): `Model.MStaInventario[Token.TipoActual] + Model.MStaEnProceso[Token.TipoActual] <= TableProceso[Token.TipoActual].PuntoReorden`
4. **Rama True (Crear Lotes)**:
   - **Step Assign** (Iniciar contador): `Token.LotesCreados = 0`
   - **Step Decide** (Loop de lotes): `Token.LotesCreados < TableProceso[Token.TipoActual].LotesAReponer`
   - **Rama True (Crear 1 lote)**:
     - **Step Create**: 
       - Entity Type: `EntLote`
       - Number of Entities: `1`
       - Starting Node: `Input@SrvPesado` (o el nodo Input respectivo).
     - **Step Assign** (En el nodo `Created` del step Create):
       - `EntLote.EStaTipoPan = Token.TipoActual`
       - `EntLote.EStaFamilia = TableProceso[Token.TipoActual].FamiliaID`
       - `EntLote.EStaKgLote = TableProceso[Token.TipoActual].KgPorBatch`
       - `Model.MStaEnProceso[Token.TipoActual] = Model.MStaEnProceso[Token.TipoActual] + EntLote.EStaKgLote`
     - **Step Assign** (En la salida principal del step Create): `Token.LotesCreados = Token.LotesCreados + 1`
     - Ligar esta salida de vuelta al **Step Decide** del loop de lotes.
   - **Rama False (Fin lotes)**: Confluye con la rama False del Step Decide de Evaluación de Reorden.
5. **Convergencia y Loop Principal**:
   - **Step Assign**: `Token.TipoActual = Token.TipoActual + 1`
6. **Step Decide** (Fin de iteración tipos):
   - Condition: `Token.TipoActual <= 10`
   - **True**: Vuelve al inicio del Step Decide de Evaluación (Paso 3).
   - **False**: FIN (`EndProcess`).

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

> **Lógica**: La familia cuyo inventario agregado en sala es más bajo tiene prioridad. Ataca directamente los quiebres de stock.

#### Steps del Process

| Step | Tipo | Configuración |
|---|---|---|
| 1 | **Assign** | `Token.StockF1 = Model.MStaInventario[5] + Model.MStaInventario[8] + Model.MStaInventario[9]` |
| 2 | **Assign** | `Token.StockF2 = Model.MStaInventario[1] + Model.MStaInventario[2] + Model.MStaInventario[4] + Model.MStaInventario[10]` |
| 3 | **Assign** | `Token.StockF3 = Model.MStaInventario[3] + Model.MStaInventario[6] + Model.MStaInventario[7]` |
| 4 | **Assign** | `Token.FamiliaElegida = 1` |
| 5 | **Assign** | `Token.MinStock = Token.StockF1` |
| 6 | **Decide** | `Token.StockF2 < Token.MinStock AND Model.MStaColaHorno[2] > 0` |
| 6T | **Assign** | `Token.FamiliaElegida = 2`, `Token.MinStock = Token.StockF2` |
| 7 | **Decide** | `Token.StockF3 < Token.MinStock AND Model.MStaColaHorno[3] > 0` |
| 7T | **Assign** | `Token.FamiliaElegida = 3` |
| 8 | **Decide** | `Model.MStaColaHorno[Token.FamiliaElegida] > 0` |
| 8T | **Assign** | Iniciar corrida de `Token.FamiliaElegida` (resetear cola, Fire, etc.) |
| 8F | FIN | (ninguna familia tiene cola — no hornear) |

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
