# Guía de Implementación en SIMIO — Parte 3: Processes, Experiments y Resultados

---

## FASE 7: Processes (Lógica Personalizada)

Los Processes en SIMIO permiten implementar lógica que va más allá de las propiedades estándar de Source/Server/Sink. Se acceden desde **Definitions → Processes** o desde **Add-On Process Triggers** de cada objeto.

### Paso 7.1 — Process: Asignación de tipo de pan al cliente

**Ubicación**: En `SrcClientes` → Properties → **Add-On Process Triggers** → **Before Exiting** → Crear nuevo proceso `ProcAsignarTiposCliente`

Este proceso calcula el índice de hora actual y asigna tipos de pan usando las probabilidades horarias.

#### Pasos del Process:

1. **Assign** — Calcular índice de hora: ✅

   - State Variable: `Model.MStaHoraIdx`
   - Value: `Math.Floor((Run.TimeNow - DateTime.FromString("09:00")) / DateTime.FromString("01:00")) + 1`
   - *(Alternativa simplificada)*: `Math.Floor(Run.TimeNow / 60) + 1` si la simulación empieza en t=0 correspondiente a 09:00
2. **Assign** — Nº de tipos a comprar:✅

   - State Variable: `EntCliente.EStaNTipos`
   - Value: `Random.Discrete(1, 0.50, 2, 0.85, 3, 1.00)`
3. **Assign** — Tipo 1 (primera selección): ❎

   - State Variable: `EntCliente.EStaTipo1`
   - Value: Usar distribución discreta acumulada basada en `TableProbEleccion[MStaHoraIdx]`:

   ```
   Random.Discrete(
     1, TableProbEleccion[MStaHoraIdx].PMarraqueta,
     2, TableProbEleccion[MStaHoraIdx].PMarraqueta + TableProbEleccion[MStaHoraIdx].PHallulla,
     3, ...(suma acumulada hasta PMarrInt)...,
     ...
     10, 1.0
   )
   ```

   > **Nota práctica**: SIMIO acepta `Random.Discrete` en forma acumulada. Se deben precalcular las probabilidades acumuladas en columnas adicionales de `TableProbEleccion` para simplificar la expresión.
   >
4. **Assign** — Cantidad tipo 1:

   - State Variable: `EntCliente.EStaKg1`
   - Value: `Random.Triangular(TableCompra[EntCliente.EStaTipo1].TriMin, TableCompra[EntCliente.EStaTipo1].TriModa, TableCompra[EntCliente.EStaTipo1].TriMax)`
5. **Decide** — ¿Compra 2º tipo?

   - Condition: `EntCliente.EStaNTipos >= 2`
   - **True branch**: Assign `EStaTipo2` y `EStaKg2` (con probabilidad condicional sin reemplazo)
   - **False branch**: Continuar
6. **Decide** — ¿Compra 3er tipo?

   - Condition: `EntCliente.EStaNTipos >= 3`
   - **True branch**: Assign `EStaTipo3` y `EStaKg3`
   - **False branch**: Continuar

> **Simplificación recomendada**: Para el 2º y 3er tipo, usar la misma distribución horaria (las probabilidades condicionales son muy similares a las marginales dado que hay 10 tipos). Si se requiere exactitud, precalcular las condicionales en tablas adicionales.

### Paso 7.2 — Process: Lógica de Venta (todo-o-nada) ❎

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

| Step       | Tipo                             | Configuración                                                                 |
| ---------- | -------------------------------- | ------------------------------------------------------------------------------ |
| 1          | **Decide**                 | Condition:`Model.MStaInventario[EntCliente.EStaTipo1] >= EntCliente.EStaKg1` |
| 2a (True)  | **Assign**                 | `Model.MStaInventario[EntCliente.EStaTipo1]` -= `EntCliente.EStaKg1`       |
| 2b (True)  | **Assign**                 | `Model.MStaVentas[EntCliente.EStaTipo1]` += `EntCliente.EStaKg1`           |
| 2c (False) | **Assign**                 | `Model.MStaQuiebres[EntCliente.EStaTipo1]` += `EntCliente.EStaKg1`         |
| 3 ❎       | **Decide**                 | Condition:`EntCliente.EStaNTipos >= 2`                                       |
| 4-6        | *(Repetir lógica para Tipo2)* |                                                                                |
| 7 ❎       | **Decide**                 | Condition:`EntCliente.EStaNTipos >= 3`                                       |
| 8-10       | *(Repetir lógica para Tipo3)* |                                                                                |

### Paso 7.3 — Process: Reposición de Inventario ✅

**Ubicación**: En `SnkLoteTerminado` → **Add-On Process Triggers** → **Entered** → Crear `ProcReponerInventario`

| Step | Tipo             | Configuración                                                          |
| ---- | ---------------- | ----------------------------------------------------------------------- |
| 1    | **Assign** | `Model.MStaInventario[EntLote.EStaTipoPan]` += `EntLote.EStaKgLote` |
| 2    | **Assign** | `Model.MStaLotesProducidos[EntLote.EStaTipoPan]` += 1                 |

### Paso 7.4 — Process: Inicialización de Inventario ✅

**Ubicación**: En **Model** → **Definitions** → **Processes** → Crear `ProcInicializacion`
Trigger: **Add-On Process Triggers** del Model → **Initializing**

| Step | Asignación                                                 |
| ---- | ----------------------------------------------------------- |
| 1    | `MStaInventario[1]` = 240 (4 batches × 60 kg Marraqueta) |
| 2    | `MStaInventario[2]` = 165 (3 batches × 55 kg Hallulla)   |
| 3    | `MStaInventario[3]` = 120 (2 × 60 Marr.Int)              |
| 4    | `MStaInventario[4]` = 110 (2 × 55 Hall.Int)              |
| 5    | `MStaInventario[5]` = 55 (1 × 55 Hot Dog)                |
| 6    | `MStaInventario[6]` = 50 (1 × 50 Ciabatta)               |
| 7    | `MStaInventario[7]` = 45 (1 × 45 Baguette)               |
| 8    | `MStaInventario[8]` = 50 (1 × 50 Dobladita)              |
| 9    | `MStaInventario[9]` = 50 (2 × 25 Boc.Dama)               |
| 10   | `MStaInventario[10]` = 60 (1 × 60 Amasado)               |

### Paso 7.5 — Política de Carga del Horno (Simplificada)

Esta es la lógica más compleja. Se implementa en `SrvCargaHorno`:

**Opción A — Simplificada**: Modelar el horno como un Server con:

- **Batch Size**: Mínimo 1 lote (el batching se maneja por acumulación)
- Usar **Input Buffer** con regla de acumulación

**Opción B — Con Process**: En `SrvFermentacion` → **Exited** trigger:

| Step      | Tipo             | Configuración                                                     |
| --------- | ---------------- | ------------------------------------------------------------------ |
| 1         | **Assign** | `MStaColaHorno[EntLote.EStaFamilia]` += `EntLote.EStaKgLote`   |
| 2         | **Decide** | `MStaColaHorno[EntLote.EStaFamilia] >= 600`                      |
| 3 (True)  | **Assign** | Resetear cola, iniciar corrida ❎                                  |
| 3 (False) | **Delay**  | Timer de espera (máx 15 min), luego iniciar corrida anticipada ❎ |

---

## FASE 8: Configurar Input Parameters para Experimentación

### Paso 8.1 — Crear Referenced Properties

Para cada recurso cuya cantidad queremos variar en experimentos:

1. Clic en el objeto (ej. `SrvMezcladoAuto`) → Properties → **Initial Capacity**
2. Clic derecho en el campo → **Set Referenced Property** → **Create New Property**
3. Nombres:

| Property                 | Valor Default | Se usa en                                                          |
| ------------------------ | ------------- | ------------------------------------------------------------------ |
| `PropNumMezcladoras`   | 3             | `SrvMezcladoAuto` Initial Capacity                               |
| `PropNumHornos`        | 2             | `SrvHorneado` Initial Capacity                                   |
| `PropNumPanaderos`     | 9             | `ResPanadero` Initial Capacity (NO Figura initial capacity) ❎  |
| `PropNumManipuladores` | 2             | `ResManipulador` Initial Capacity ❎                             |
| `PropNumAmasadoras`    | 3             | `SrvAmasadoManual` Initial Capacity                              |
| `PropNumMesas`         | 3             | `SrvFormado` Initial Capacity                                    |

> **Ref. Workbook §3.5.1**: Las Referenced Properties aparecen automáticamente en la grilla de experimentos.

### Paso 8.2 — Crear Input Parameter Distributions

Ir a **Data** → **Input Parameters** → **Distribution**:

| Nombre                       | Distribución                  | Parámetros               | Random Stream | Uso                   |
| ---------------------------- | ------------------------------ | ------------------------- | ------------- | --------------------- |
| `InpDisInterarriboCliente` | (No aplica, usamos Rate Table) | —                        | —            | —                    |
| `InpDisNTipos`             | Discrete                       | (1, 0.5; 2, 0.85; 3, 1.0) | Stream 1      | Nº tipos por cliente |

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

| Scenario | Mezcladoras | Hornos | Panaderos | Manipuladores |
| -------- | ----------- | ------ | --------- | ------------- |
| Base     | 3           | 1      | 9         | 2             |
| Esc2     | 3           | 2      | 9         | 2             |
| Esc3     | 4           | 2      | 9         | 3             |
| Esc4     | 3           | 2      | 10        | 3             |
| Esc5     | 4           | 2      | 10        | 3             |

### Paso 9.4 — Definir Responses

En la pestaña **Design** → **Add Response**:

| Response Name        | Expression                                                                       | Units |
| -------------------- | -------------------------------------------------------------------------------- | ----- |
| `QuiebreTotalKg`   | `Model.MStaQuiebres[1] + Model.MStaQuiebres[2] + ... + Model.MStaQuiebres[10]` | Kg    |
| `NivelServicioPct` | `(Sum(MStaVentas) / (Sum(MStaVentas) + Sum(MStaQuiebres))) * 100`              | %     |
| `VentasTotalesKg`  | `Model.MStaVentas[1] + ... + Model.MStaVentas[10]`                             | Kg    |
| `UtilMezcladora`   | `SrvMezcladoAuto.ResourceState.ScheduledUtilization`                           | —    |
| `UtilHorno`        | `SrvHorneado.ResourceState.ScheduledUtilization`                               | —    |

### Paso 9.5 — Ejecutar y Analizar

1. Clic en **Run** en la sección Experiment del ribbon
2. Ir a **Response Results** → comparar escenarios gráficamente
3. Ir a **Pivot Grid** → ver Average, Half-Width, Min, Max
4. Ir a **Input Analysis** → **Response Sensitivity** para ver qué recurso impacta más

> **Ref. Workbook §3.5.7–3.5.11**: Los Response Results charts muestran intervalos de confianza. Si los intervalos de dos escenarios no se traslapan, la diferencia es estadísticamente significativa.

---

## FASE 10: Análisis de Resultados (Checklist)

### 10.1 — Métricas clave a verificar

| Métrica                    | Dónde encontrarla                                            | Valor esperado        |
| --------------------------- | ------------------------------------------------------------- | --------------------- |
| Quiebres totales (kg)       | Response `QuiebreTotalKg`                                   | Minimizar             |
| Nivel de servicio (%)       | Response `NivelServicioPct`                                 | > 95%                 |
| Utilización mezcladora     | Results → SrvMezcladoAuto → ScheduledUtilization            | < 90%                 |
| Utilización horno          | Results → SrvHorneado → ScheduledUtilization                | < 85%                 |
| Cola horno (promedio)       | Results → SrvCargaHorno → InputBuffer → Content → Average | < 3 lotes             |
| Tiempo en sistema (lote)    | Results → EntLote → FlowTime → Average                     | Razonable             |
| Inventario promedio en sala | Status Labels durante la corrida                              | Positivo durante peak |

### 10.2 — Reportar desde Pivot Grid

1. Ir a **Results** tab después de correr
2. Filtrar por **Category**: `Capacity` → ver `ScheduledUtilization` por servidor
3. Filtrar por **Category**: `Content` → ver promedio en cola por InputBuffer
4. Filtrar por **Category**: `FlowTime` → ver tiempos promedio
5. Cambiar unidades con **Unit Settings** → Time = Minutes

### 10.3 — Status Labels útiles (para debug visual)

En **Drawing** tab, agregar **Status Labels** al canvas:

| Label                   | Expression                           |
| ----------------------- | ------------------------------------ |
| "Inventario Marraqueta" | `Model.MStaInventario[1]`          |
| "Quiebres Totales"      | `Sum(Model.MStaQuiebres)`          |
| "Hora Simulada"         | `Run.TimeNow`                      |
| "Clientes Atendidos"    | `SrcClientes.TotalEntitiesCreated` |

---

## Resumen de Archivos de Referencia

| Archivo                                   | Contenido                                                      |
| ----------------------------------------- | -------------------------------------------------------------- |
| `reporte_pre_modelacion.md`             | Fuente de verdad: parámetros, supuestos, lógica de decisión |
| `parametros_proceso_panaderia.csv`      | Tiempos por etapa y tamaño de lote                            |
| `perfil_demanda_por_hora_panaderia.csv` | Demanda horaria por tipo                                       |
| `probabilidades_eleccion_por_hora.csv`  | Probabilidades de elección por hora                           |
| `guia_simio_parte1.md`                  | Setup del proyecto, entidades, tablas de datos                 |
| `guia_simio_parte2.md`                  | Facility, Rate Tables, Work Schedules                          |
| `guia_simio_parte3.md`                  | Processes, Experiments, Resultados (este archivo)              |
