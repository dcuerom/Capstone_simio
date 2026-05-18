# Guía de Implementación en SIMIO — Alternativas de Políticas de Producción

> **Referencia**: Basada en el Workbook SIMIO 6th Ed. y el análisis pre-modelación.
> **Objetivo**: Proveer el paso a paso para configurar y probar en SIMIO las 3 alternativas propuestas a la política secuencial de empuje (Push) actual.

Para facilitar la experimentación, sugerimos crear una propiedad en el modelo (`Model` → `Definitions` → `Properties` → `Add Integer Property`) llamada **`PropPoliticaProduccion`**, donde:
- **1** = Secuencial Predefinida (Actual Enfoque Híbrido)
- **2** = Política PULL (Puntos de Reorden / Kanban)
- **3** = Prioridad Dinámica (JIT / Criticidad)
- **4** = Bloques Horarios (Time-Bucketing)

Puedes usar esta propiedad en los `Decide` steps de tus procesos principales para enrutar la lógica según la política activa en el experimento.

---

## ALTERNATIVA 1: Política PULL Pura (Kanban / Min-Max)

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

## ALTERNATIVA 2: Política de Prioridad Dinámica (Índice de Criticidad)

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

## ALTERNATIVA 3: Producción por Bloques Horarios (Time-Bucketing Dinámico)

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

## CÓMO EVALUAR LAS ALTERNATIVAS (Experimentos)

1. En tu ventana de **Experiments**, añade una columna (Control) para la propiedad `PropPoliticaProduccion`.
2. Crea 4 escenarios base, manteniendo los recursos iguales (ej: 3 Mezcladoras, 2 Hornos, etc.) pero variando la Política del 1 al 4.
3. Observa las Responses que definiste en la Parte 3 de la guía:
   - ¿Qué política minimiza el `QuiebreTotalKg`?
   - ¿Qué política mantiene una `UtilMezcladora` más constante y reduce el agolpamiento?
   - ¿Aumentan los Setups de los Hornos en la política Dinámica (Alt 2) vs la de Bloques (Alt 3)?

> **Recomendación**: La Alternativa 3 (Bloques Horarios) suele ser la más equilibrada en entornos reales de supermercados, pero la Alternativa 2 (Dinámica) te mostrará la cota superior del nivel de servicio que tu configuración de máquinas puede lograr.
