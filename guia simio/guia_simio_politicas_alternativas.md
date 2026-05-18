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
   - **Condition**: `PropPoliticaProduccion == 2` (Solo se ejecuta si la política PULL está activa).

### Fase C: Lógica del Proceso (`ProcControlPull`)
El proceso recorre los 10 tipos de pan, evalúa su nivel de stock, y si amerita, crea los lotes.

1. **Step Assign** (Inicializar): `Token.TipoActual = 1` (Necesitas crear un estado temporal Real `TipoActual` en el Token del proceso).
2. **Step Decide** (Evaluación de Reorden): 
   - Condition: `Model.MStaInventario[Token.TipoActual] + Model.MStaEnProceso[Token.TipoActual] <= TableProceso[Token.TipoActual].PuntoReorden`
3. **Rama True (Crear Lotes)**:
   - **Step Create**: 
     - Entity Type: `EntLote`
     - Number of Entities: `TableProceso[Token.TipoActual].LotesAReponer`
     - Create Location: `Node` (Seleccionar el Input Node de `SrvPesado`).
   - **Step Assign** (Asignar atributos al lote creado, conectando la salida "Created" del Create step):
     - `EntLote.EStaTipoPan = Token.TipoActual`
     - `EntLote.EStaFamilia = TableProceso[Token.TipoActual].FamiliaID`
     - `EntLote.EStaKgLote = TableProceso[Token.TipoActual].KgPorBatch`
     - `Model.MStaEnProceso[Token.TipoActual] = Model.MStaEnProceso[Token.TipoActual] + EntLote.EStaKgLote`
4. **Rama False & Convergencia**:
   - Ambas ramas (la salida de asignación y el False del Decide) van a un **Step Assign** para iterar: `Token.TipoActual = Token.TipoActual + 1`.
5. **Step Decide** (Loop):
   - Condition: `Token.TipoActual <= 10`
   - **True**: Vuelve al inicio del Step Decide de Evaluación.
   - **False**: FIN.

---

### ALTERNATIVA 2: Política de Prioridad Dinámica (Índice de Criticidad)

Esta política elimina el flujo periódico. Los lotes se generan bajo demanda "justo a tiempo" (JIT) en el momento en que los operarios / máquinas están libres para procesarlos, evaluando quién tiene la mayor urgencia.

### Fase A: Configuración del Disparador
La producción debe inyectarse cuando la línea lo permita. Puedes usar el evento de salida del operario o la mezcladora. 
Para simplificar: usaremos un **Timer** muy frecuente, pero que solo avanza si hay capacidad disponible.

1. Crear `TimerCriticidad` con Interval de `2` minutos.
2. Ir a **Definitions** → **Processes** → Crear `ProcGenerarLoteCritico`.
   - **Triggering Event**: `TimerCriticidad.Event`
   - **Condition**: `PropPoliticaProduccion == 3 AND (SrvPesado.InputBuffer.Contents < 2)` (Para no inundar el sistema, solo genera si hay espacio en la fila).

### Fase B: Lógica de Búsqueda del Más Crítico (`ProcGenerarLoteCritico`)
1. **Estados del Token**: Crear en las propiedades del proceso `Token.TipoCritico` (Integer) y `Token.MaxCriticidad` (Real).
2. **Step Assign** (Inicializar): 
   - `Token.MaxCriticidad = -9999`
   - `Token.TipoCritico = 0`
   - `Token.Indice = 1`
3. **Bloque de Loop (1 a 10)**:
   - **Assign** (Calcular Criticidad): 
     - Crear `Token.CritActual` (Real) = `(TableDemandaHora[Model.MStaHoraIdx].DemKg - Model.MStaInventario[Token.Indice] - Model.MStaEnProceso[Token.Indice]) / TableProceso[Token.Indice].KgPorBatch`
     > *Tip: Sumar extra puntos si `TableProceso[Token.Indice].FamiliaID` es igual a la última familia horneada, para minimizar Setups.*
   - **Decide**: `Token.CritActual > Token.MaxCriticidad`
   - **Rama True**: `Token.MaxCriticidad = Token.CritActual`, `Token.TipoCritico = Token.Indice`.
   - Iterar `Token.Indice = Token.Indice + 1` y regresar hasta 10.
4. **Step Decide (Post-Loop)**:
   - Condition: `Token.TipoCritico > 0`
5. **Rama True (Crear Lote)**:
   - **Step Create**: 1 entidad de `EntLote` en el Input Node de `SrvPesado`.
   - **Step Assign** (en nodo Created): Asignar Tipo, Familia, Kg, y sumar a `MStaEnProceso` (Igual que en Alternativa 1).

---

### ALTERNATIVA 3: Producción por Bloques Horarios (Time-Bucketing Dinámico)

Similar a la versión híbrida actual, pero recalcula el plan masivo en horas específicas del día en lugar de depender de una tabla estática para los 155 lotes completos.

### Fase A: Disparador por Bloques
1. Ir a **Definitions** → **Elements** → **Timers** → Crear `TimerBloqueHorario`.
   - En lugar de un intervalo fijo, puedes configurarlo con eventos o un intervalo de `240` minutos (4 horas). Ej: evalúa a las 06:00, 10:00, 14:00.

### Fase B: Lógica de Planificación en Bloque (`ProcGenerarBloque`)
- **Triggering Event**: `TimerBloqueHorario.Event`
- **Condition**: `PropPoliticaProduccion == 4`

1. Este proceso recorre los 10 tipos de pan.
2. Para cada tipo, calcula la demanda requerida para el **próximo bloque** (próximas 4 horas).
3. `DeficitBloque = DemandaProximas4Horas - Model.MStaInventario[Tipo] - Model.MStaEnProceso[Tipo]`.
4. Si `DeficitBloque > 0`, calcula cuántos lotes: `NumLotes = Math.Ceiling(DeficitBloque / TableProceso[Tipo].KgPorBatch)`.
5. **Step Create**: Crea `NumLotes` entidades del `EntLote`.
6. **Asignación Crucial (Prioridad de Familia)**:
   Para que los hornos no hagan setups innecesarios, los lotes de este bloque que se envíen a la fila deben estar ordenados por familia.
   - En el **Step Assign** de las entidades creadas, debes configurar la propiedad de entidad `Priority` basada en la Familia. Ej: `EntLote.Priority = TableProceso[Tipo].FamiliaID`.
   - En `SrvPesado` y las filas siguientes, asegúrate de que el **Ranking Rule** del Input Buffer esté en `Highest Priority First` o `Lowest Priority First` para que las familias se agrupen solas dentro de la cola.

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

1. En tu ventana de **Experiments**, añade una columna (Control) para la propiedad `PropPoliticaProduccion`.
2. Crea 4 escenarios base, manteniendo los recursos iguales (ej: 3 Mezcladoras, 2 Hornos, etc.) pero variando la Política del 1 al 4.
3. Observa las Responses que definiste en la Parte 3 de la guía:
   - ¿Qué política minimiza el `QuiebreTotalKg`?
   - ¿Qué política mantiene una `UtilMezcladora` más constante y reduce el agolpamiento?
   - ¿Aumentan los Setups de los Hornos en la política Dinámica (Alt 2) vs la de Bloques (Alt 3)?

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
