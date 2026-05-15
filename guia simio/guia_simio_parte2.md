# Guía de Implementación en SIMIO — Parte 2: Facility y Arribos

---

## FASE 4: Rate Table para Arribos de Clientes (NHPP)

### Paso 4.1 — Crear Rate Table ✅

Ir a **Data** → **Schedules** → **Create → Rate Table** → Nombre: `ClienteArrivalRate`

Configurar:

- **Interval Size**: 1 Hour
- **Number of Intervals**: 12 (corresponde a 09:00–21:00)

Ingresar los valores (clientes/hora, de la sección 3.11 del reporte):

| Intervalo | Hora real    | Rate (arrivals/hr) |
| --------- | ------------ | ------------------ |
| 1         | 09:00–10:00 | 275                |
| 2         | 10:00–11:00 | 275                |
| 3         | 11:00–12:00 | 275                |
| 4         | 12:00–13:00 | 439                |
| 5         | 13:00–14:00 | 417                |
| 6         | 14:00–15:00 | 417                |
| 7         | 15:00–16:00 | 275                |
| 8         | 16:00–17:00 | 275                |
| 9         | 17:00–18:00 | 299                |
| 10        | 18:00–19:00 | 819                |
| 11        | 19:00–20:00 | 806                |
| 12        | 20:00–21:00 | 279                |

### Paso 4.2 — Configurar Run Setup ✅

Ir a **Run Tab → Run Setup**:

- **Starting Time**: `9:00 AM` (la tienda abre a las 09:00)
- **Ending Type**: `Specific Ending Time`
- **Ending Time**: `9:00 PM` (21:00)

> **Ref. Workbook §4.2**: Esto evita que las estadísticas se diluyan con horas sin actividad.

---

## FASE 5: Objetos en el Facility (Línea de Producción)

### Paso 5.1 — Colocar objetos del Standard Library ❎

Ir a pestaña **Facility** y arrastrar desde el **[Standard Library]**:

#### Sources (generadores) ✅

| Objeto | Nombre          | Entity Type    | Arrival Mode                        | Configuración                             |
| ------ | --------------- | -------------- | ----------------------------------- | ------------------------------------------ |
| Source | `SrcLotes`    | `EntLote`    | Interarrival Time                   | Se controla por proceso/Timer (ver Fase 7) |
| Source | `SrcClientes` | `EntCliente` | **Time Varying Arrival Rate** | Rate Table =`ClienteArrivalRate`         |

**Configurar `SrcClientes`**:

1. Clic en `SrcClientes` → Properties
2. **Entity Type**: `EntCliente`
3. **Arrival Mode**: `Time Varying Arrival Rate`
4. **Arrival Rate Table**: `ClienteArrivalRate`

**State Assignments en `SrcClientes`** (Before Exiting):
Clic en **State Assignments** → expandir → **Before Exiting** → clic en `...` (Repeating Property Editor):

| # | State Variable Name       | New Value                                     |
| - | ------------------------- | --------------------------------------------- |
| 1 | `EntCliente.EStaNTipos` | `Random.Discrete(1, 0.50, 2, 0.85, 3, 1.0)` |
| 2 | `EntCliente.EStaTipo1`  | (ver nota abajo sobre proceso)                |

> **Nota**: La asignación de tipos de pan requiere lógica condicional basada en la hora → se implementa mejor con un **Process** (ver Fase 7).

#### Servers (estaciones de trabajo) ❎

Arrastrar desde [Standard Library] los siguientes **Server** objects:

| Nombre SIMIO         | Representa                   | Processing Time                                           | Initial Capacity                  |
| -------------------- | ---------------------------- | --------------------------------------------------------- | --------------------------------- |
| `SrvPesado`        | Pesado y dosificación       | `TableProceso[EntLote.EStaTipoPan].TiempoPesado`        | 3 (= nº panaderos en esta tarea) |
| `SrvCargaMezc`     | Carga de mezcladora          | `TableProceso[EntLote.EStaTipoPan].TiempoCargaMezc`     | 3                                 |
| `SrvMezcladoAuto`  | Ciclo automático mezcladora | `TableProceso[EntLote.EStaTipoPan].TiempoMezcladoAuto`  | **3** (nº mezcladoras)     |
| `SrvRetiroMasa`    | Retiro de masa               | `TableProceso[EntLote.EStaTipoPan].TiempoRetiroMasa`    | 3                                 |
| `SrvAmasadoManual` | Amasado manual               | `TableProceso[EntLote.EStaTipoPan].TiempoAmasadoManual` | 2-3 (nº amasadoras) ❓           |
| `SrvReposo`        | Reposo en masa               | `TableProceso[EntLote.EStaTipoPan].TiempoReposo`        | 999 (ilimitado)                   |
| `SrvFormado`       | Dividido y formado           | `TableProceso[EntLote.EStaTipoPan].TiempoFormado`       | 3 (mesas)                         |
| `SrvFermentacion`  | Fermentación final          | `TableProceso[EntLote.EStaTipoPan].TiempoFermentacion`  | 999 (ilimitado)                   |
| `SrvCargaHorno`    | Carga del horno              | 5 ❎                                                      | Depende de nº manipuladores      |
| `SrvHorneado`      | Horneado                     | `TableProceso[EntLote.EStaTipoPan].TiempoHorneado`      | 1-2 (nº hornos) ❓               |
| `SrvDescargaHorno` | Descarga del horno           | 5 ❎                                                      | Depende de nº manipuladores      |
| `SrvEnfriado`      | Enfriamiento                 | `TableProceso[EntLote.EStaTipoPan].TiempoEnfriado`      | 999 (ilimitado)                   |
| `SrvTraslado`      | Traslado a sala              | `TableProceso[EntLote.EStaTipoPan].TiempoTraslado`      | 2 (nº ayudantes)                 |

#### Servidor especial: Venta al cliente ✅

| Nombre SIMIO | Representa                  | Processing Time                                 | Capacity |
| ------------ | --------------------------- | ----------------------------------------------- | -------- |
| `SrvVenta` | Punto de venta/autoservicio | 0.5 (simbólico, la lógica real es un Process) | 999      |

#### Sinks ✅

| Nombre SIMIO         | Propósito                               |
| -------------------- | ---------------------------------------- |
| `SnkLoteTerminado` | Lote completado → incrementa inventario |
| `SnkClienteSale`   | Cliente abandona la tienda               |

### Paso 5.2 — Conectar objetos con Paths/Connectors✅

Conectar en secuencia lineal usando **Connectors** (sin distancia):

```
SrcLotes → SrvPesado → SrvCargaMezc → SrvMezcladoAuto → SrvRetiroMasa 
→ SrvAmasadoManual → SrvReposo → SrvFormado → SrvFermentacion 
→ SrvCargaHorno → SrvHorneado → SrvDescargaHorno → SrvEnfriado 
→ SrvTraslado → SnkLoteTerminado
```

Para clientes:

```
SrcClientes → SrvVenta → SnkClienteSale
```

> **Ref. Workbook §3.1.2**: Usar Connectors cuando no hay distancia física relevante. Usar Paths (con Drawn to Scale = FALSE) solo si se desea modelar distancia.

### Paso 5.3 — Configurar Secondary Resources (Panaderos/Manipuladores) ❎

Los recursos humanos se modelan como **Resources** (no como capacidad del Server):

1. Ir a **[Standard Library]** → arrastrar **Resource** al canvas
2. Crear: ✅

| Resource | Nombre             | Initial Capacity     |
| -------- | ------------------ | -------------------- |
| Resource | `ResPanadero`    | 9 (punto de partida) |
| Resource | `ResManipulador` | 2                    |

3. En cada Server que requiere recurso humano, configurar **Secondary Resources**: ❎
   - Clic en el Server → Properties → **Secondary Resources** → **Seize**
   - Agregar el recurso requerido

| Server               | Secondary Resource (Seize → Release) |
| -------------------- | ------------------------------------- |
| `SrvPesado`        | `ResPanadero` (1 unidad)            |
| `SrvCargaMezc`     | `ResPanadero` (1 unidad)            |
| `SrvRetiroMasa`    | `ResPanadero` (1 unidad)            |
| `SrvAmasadoManual` | `ResPanadero` (1 unidad)            |
| `SrvFormado`       | `ResPanadero` (1 unidad)            |
| `SrvCargaHorno`    | `ResManipulador` (1 unidad)         |
| `SrvDescargaHorno` | `ResManipulador` (1 unidad)         |
| `SrvTraslado`      | `ResManipulador` (1 unidad)         |

> **Importante**: `SrvMezcladoAuto` NO requiere panadero (supuesto S1: panadero queda libre durante el ciclo automático).

---

## FASE 6: Work Schedules (Turnos de Trabajo)

### Paso 6.1 — Crear horario de panadería ✅

Ir a **Data** → **Schedules** → **Work Schedule** → Nombre: `TurnoPanadero`

- **Days**: 1 (repite diariamente)
- **Day Pattern**: Crear nuevo → `PatronPanadero`

Configurar `PatronPanadero`:

| Work Period            | Start Time | Duration | End Time | Value |
| ---------------------- | ---------- | -------- | -------- | ----- |
| Periodo 1              | 6:00 AM    | 3h 45m   | 9:45 AM  | 1     |
| *(Descanso 15 min)*  |            |          |          |       |
| Periodo 2              | 10:00 AM   | 2h 30m   | 12:30 PM | 1     |
| *(Colación 45 min)* |            |          |          |       |
| Periodo 3              | 1:15 PM    | 2h 15m   | 3:30 PM  | 1     |
| *(Descanso 15 min)*  |            |          |          |       |
| Periodo 4              | 3:45 PM    | 2h 15m   | 6:00 PM  | 1     |

> Total productivo = 405 min (6h 45m) como indica el reporte.

### Paso 6.2 — Crear segundo turno ❎

Crear `TurnoPanadero2` con patrón similar pero desfasado:

- **Start**: 2:00 PM → **End**: 10:00 PM (cubre el peak de 18:00–20:00)

### Paso 6.3 — Asignar Work Schedule a Resources ✅

Clic en `ResPanadero` → Properties:

- **Capacity Type**: `Work Schedule`
- **Work Schedule**: `TurnoPanadero`

> **Ref. Workbook §4.5**: Para escalonar descansos, crear múltiples Work Schedules con patrones ligeramente desfasados y asignar subconjuntos de la capacidad a cada uno.

---

> **Continúa en Parte 3**: Processes (lógica de compra del cliente, asignación de tipo de pan, política de horno), Experiments y análisis de resultados.
