# Guía de Implementación en SIMIO — Parte 2: Facility, Paths, Arribos y Turnos

> **Referencia**: SASMAA7 §7.2 (Schedules), §8.2 (Entity Movement — Paths), Workbook6 §3.1.5 (Drawn to Scale), §4.5 (Work Schedules)

---

## FASE 4: Rate Table para Arribos de Clientes (NHPP)

### Paso 4.1 — Crear Rate Table

Ir a **Data** → **Schedules** → **Create → Rate Table** → Nombre: `ClienteArrivalRate`

Configurar:
- **Interval Size**: 1 Hour
- **Number of Intervals**: 12 (corresponde a 09:00–21:00)

Ingresar los valores (clientes/hora, de la sección 3.11 del reporte):

| Intervalo | Hora real | Rate (arrivals/hr) |
|---|---|---|
| 1 | 09:00–10:00 | 275 |
| 2 | 10:00–11:00 | 275 |
| 3 | 11:00–12:00 | 275 |
| 4 | 12:00–13:00 | 439 |
| 5 | 13:00–14:00 | 417 |
| 6 | 14:00–15:00 | 417 |
| 7 | 15:00–16:00 | 275 |
| 8 | 16:00–17:00 | 275 |
| 9 | 17:00–18:00 | 299 |
| 10 | 18:00–19:00 | 819 |
| 11 | 19:00–20:00 | 806 |
| 12 | 20:00–21:00 | 279 |

### Paso 4.2 — Configurar Run Setup

Ir a **Run Tab → Run Setup**:
- **Starting Time**: `9:00 AM` (la tienda abre a las 09:00)
- **Ending Type**: `Specific Ending Time`
- **Ending Time**: `9:00 PM` (21:00)

> **Ref. Workbook §4.2**: Esto evita que las estadísticas se diluyan con horas sin actividad.

---

## FASE 5: Objetos en el Facility (Línea de Producción)

### Paso 5.1 — Colocar objetos del Standard Library

Ir a pestaña **Facility** y arrastrar desde el **[Standard Library]**:

#### Sources (generadores)

| Objeto | Nombre | Entity Type | Arrival Mode | Configuración |
|---|---|---|---|---|
| Source | `SrcLotes` | `EntLote` | Interarrival Time | Se controla por proceso/Timer (ver Fase 7) |
| Source | `SrcClientes` | `EntCliente` | **Time Varying Arrival Rate** | Rate Table = `ClienteArrivalRate` |

**Configurar `SrcClientes`**:
1. Clic en `SrcClientes` → Properties
2. **Entity Type**: `EntCliente`
3. **Arrival Mode**: `Time Varying Arrival Rate`
4. **Arrival Rate Table**: `ClienteArrivalRate`

**State Assignments en `SrcClientes`** (Before Exiting):
Clic en **State Assignments** → expandir → **Before Exiting** → clic en `...` (Repeating Property Editor):

| # | State Variable Name | New Value |
|---|---|---|
| 1 | `EntCliente.EStaNTipos` | `Random.Discrete(1, 0.50, 2, 0.85, 3, 1.0)` |
| 2 | `EntCliente.EStaTipo1` | (ver nota abajo sobre proceso) |

> **Nota**: La asignación de tipos de pan requiere lógica condicional basada en la hora → se implementa mejor con un **Process** (ver Fase 7).

#### Servers (estaciones de trabajo)

Arrastrar desde [Standard Library] los siguientes **Server** objects:

| Nombre SIMIO | Representa | Processing Time | Initial Capacity |
|---|---|---|---|
| `SrvPesado` | Pesado y dosificación | `TableProceso[EntLote.EStaTipoPan].TiempoPesado` | 3 (= nº panaderos en esta tarea) |
| `SrvCargaMezc` | Carga de mezcladora | `TableProceso[EntLote.EStaTipoPan].TiempoCargaMezc` | 3 |
| `SrvMezcladoAuto` | Ciclo automático mezcladora | `TableProceso[EntLote.EStaTipoPan].TiempoMezcladoAuto` | **3** (nº mezcladoras) |
| `SrvRetiroMasa` | Retiro de masa | `TableProceso[EntLote.EStaTipoPan].TiempoRetiroMasa` | 3 |
| `SrvAmasadoManual` | Amasado manual | `TableProceso[EntLote.EStaTipoPan].TiempoAmasadoManual` | 2-3 (nº amasadoras) |
| `SrvReposo` | Reposo en masa | `TableProceso[EntLote.EStaTipoPan].TiempoReposo` | 999 (ilimitado) |
| `SrvFormado` | Dividido y formado | `TableProceso[EntLote.EStaTipoPan].TiempoFormado` | 3 (mesas) |
| `SrvFermentacion` | Fermentación final | `TableProceso[EntLote.EStaTipoPan].TiempoFermentacion` | 999 (ilimitado) |
| `SrvCargaHorno` | Carga del horno | 5 | Depende de nº manipuladores |
| `SrvHorneado` | Horneado | `TableProceso[EntLote.EStaTipoPan].TiempoHorneado` | 1-2 (nº hornos) |
| `SrvDescargaHorno` | Descarga del horno | 5 | Depende de nº manipuladores |
| `SrvEnfriado` | Enfriamiento | `TableProceso[EntLote.EStaTipoPan].TiempoEnfriado` | 999 (ilimitado) |

> **Nota**: El antiguo `SrvTraslado` se elimina como Server y se reemplaza por un **Path** con distancia explícita (ver Paso 5.2).

#### Servidor especial: Venta al cliente

| Nombre SIMIO | Representa | Processing Time | Capacity |
|---|---|---|---|
| `SrvVenta` | Punto de venta/autoservicio | 0.5 (simbólico, la lógica real es un Process) | 999 |

#### Sinks

| Nombre SIMIO | Propósito |
|---|---|
| `SnkLoteTerminado` | Lote completado → incrementa inventario |
| `SnkClienteSale` | Cliente abandona la tienda |

### Paso 5.2 — Conectar objetos con Paths (con tiempos de traslado)

> **Cambio respecto a la versión anterior**: Se reemplazan los **Connectors** por **Paths** en los tramos donde existe desplazamiento físico dentro de la panadería. Esto captura el tiempo que los panaderos/manipuladores gastan trasladando producto entre estaciones, lo cual afecta la utilización real de los recursos.
>
> **Ref. SASMAA7 §8.2.2**: "The Path calculates the travel time based on each individual entity's DesiredSpeed and the length of the Path." Para nuestro caso usamos `Drawn to Scale = FALSE` con distancias lógicas explícitas.
>
> **Ref. Workbook §3.1.5**: "Change the Drawn to Scale property to FALSE and set the correct distances."

#### Configuración de entidad para velocidad de traslado

En `EntLote` → Properties → **Movement** → **Initial Desired Speed**:
- Valor: `1.0` (metros por segundo) — equivale a velocidad de caminata con carro

#### Tabla de tramos y distancias

| Tramo (Origen → Destino) | Tipo de Link | Distancia (m) | Tiempo aprox. | Justificación |
|---|---|---|---|---|
| `SrcLotes` → `SrvPesado` | **Connector** | 0 | 0 s | Generación lógica, sin movimiento |
| `SrvPesado` → `SrvCargaMezc` | **Path** | 3 m | ~3 s | Zona de pesado adyacente a mezcladoras |
| `SrvCargaMezc` → `SrvMezcladoAuto` | **Connector** | 0 | 0 s | Misma máquina (carga y ciclo) |
| `SrvMezcladoAuto` → `SrvRetiroMasa` | **Connector** | 0 | 0 s | Misma máquina (descarga) |
| `SrvRetiroMasa` → `SrvAmasadoManual` | **Path** | 4 m | ~4 s | Traslado a mesa de amasado |
| `SrvAmasadoManual` → `SrvReposo` | **Path** | 3 m | ~3 s | Traslado a zona de reposo |
| `SrvReposo` → `SrvFormado` | **Path** | 5 m | ~5 s | Zona de reposo a mesas de formado |
| `SrvFormado` → `SrvFermentacion` | **Path** | 6 m | ~6 s | Traslado de carros a cámara de fermentación |
| `SrvFermentacion` → `SrvCargaHorno` | **Path** | 8 m | ~8 s | Cámara de fermentación al horno (tramo largo) |
| `SrvCargaHorno` → `SrvHorneado` | **Connector** | 0 | 0 s | Misma estación (carga directa) |
| `SrvHorneado` → `SrvDescargaHorno` | **Connector** | 0 | 0 s | Misma estación (descarga directa) |
| `SrvDescargaHorno` → `SrvEnfriado` | **Path** | 5 m | ~5 s | Horno a zona de enfriamiento |
| `SrvEnfriado` → `SnkLoteTerminado` | **Path** | 15 m | ~15 s | **Traslado a sala de ventas** (tramo más largo) |

Para clientes:
```
SrcClientes → SrvVenta → SnkClienteSale    (todo con Connectors, flujo lógico)
```

#### Procedimiento para crear cada Path

1. En la **Standard Library**, seleccionar **Path** (no Connector ni TimePath)
2. Hacer clic en el **Output Node** del Server origen
3. Trazar la línea hasta el **Input Node** del Server destino → clic para terminar
4. En **Properties** del Path:
   - **Drawn to Scale**: `False`
   - **Logical Length**: ingresar la distancia de la tabla (ej. `15 meters`)
   - **Type**: `Unidirectional`
   - **Allow Passing**: `True` (múltiples lotes pueden transitar simultáneamente)

> **Impacto esperado**: Los ~47 metros totales de traslado por ciclo productivo consumen ~47 segundos por lote. Con 15-20 lotes/hora, esto son ~12-16 minutos-hombre/hora de tiempo productivo que antes no se contabilizaba, mejorando la precisión de las métricas de utilización de panaderos y manipuladores.

#### Paths vs. TimePaths vs. Connectors — Cuándo usar cada uno

| Tipo | Cuándo usarlo | Propiedad clave |
|---|---|---|
| **Connector** | Transferencia instantánea (misma máquina, flujo lógico) | Sin tiempo, sin distancia |
| **TimePath** | Tiempo fijo de traslado conocido (no depende de velocidad de entidad) | `Travel Time` |
| **Path** | Distancia conocida, tiempo depende de velocidad de la entidad | `Logical Length` + `DesiredSpeed` |

> **Ref. SASMAA7 §8.2.2**: "Connectors connect two objects directly with no internal time delay. TimePaths have a Travel Time property. Paths calculate travel time based on each entity's DesiredSpeed and the length of the Path."

### Paso 5.3 — Configurar Secondary Resources (Panaderos/Manipuladores)

Los recursos humanos se modelan como **Resources** (no como capacidad del Server):

1. Ir a **[Standard Library]** → arrastrar **Resource** al canvas
2. Crear:

| Resource | Nombre | Initial Capacity |
|---|---|---|
| Resource | `ResPanadero` | 9 (punto de partida) |
| Resource | `ResManipulador` | 2 |
| Resource | `ResAyudante` | 2 |

3. En cada Server que requiere recurso humano, configurar **Secondary Resources**:
   - Clic en el Server → Properties → **Secondary Resources** → **Seize**
   - Agregar el recurso requerido

| Server | Secondary Resource (Seize → Release) |
|---|---|
| `SrvPesado` | `ResPanadero` (1 unidad) |
| `SrvCargaMezc` | `ResPanadero` (1 unidad) |
| `SrvRetiroMasa` | `ResPanadero` (1 unidad) |
| `SrvAmasadoManual` | `ResPanadero` (1 unidad) |
| `SrvFormado` | `ResPanadero` (1 unidad) |
| `SrvCargaHorno` | `ResManipulador` (1 unidad) |
| `SrvDescargaHorno` | `ResManipulador` (1 unidad) |

> **Importante**: `SrvMezcladoAuto` NO requiere panadero (supuesto S1: panadero queda libre durante el ciclo automático).

---

## FASE 6: Estrategia Global de Turnos de Trabajo

> **Cambio respecto a la versión anterior**: Se implementa una estrategia completa de turnos que cubre los 3 roles (Panaderos, Manipuladores, Ayudantes), con descansos escalonados para garantizar cobertura continua y un turno vespertino de refuerzo para el peak de demanda (18:00–20:00).
>
> **Ref. SASMAA7 §7.2**: "A Day Pattern defines the working periods for a single day. A Work Schedule includes a combination of Day Patterns to make up a repeating work period."

### Paso 6.1 — Crear Day Patterns (Patrones de Día)

Ir a **Data** → **Schedules** → en la sección **Day Patterns**, crear los siguientes patrones:

#### Patrón A: `PatronPanaderoGrupoA` (Descanso temprano)

| Work Period | Start Time | Duration | End Time | Value |
|---|---|---|---|---|
| Periodo 1 | 6:00 AM | 2h 00m | 8:00 AM | 1 |
| *(Descanso 15 min)* | | | | |
| Periodo 2 | 8:15 AM | 2h 45m | 11:00 AM | 1 |
| *(Colación 45 min)* | | | | |
| Periodo 3 | 11:45 AM | 3h 00m | 2:45 PM | 1 |
| *(Descanso 15 min)* | | | | |
| Periodo 4 | 3:00 PM | 1h 00m | 4:00 PM | 1 |

> Total neto = 8h 45min turno – (2×15 min + 45 min) = **405 min productivos** ✓

#### Patrón B: `PatronPanaderoGrupoB` (Descanso tardío, desfasado 30 min)

| Work Period | Start Time | Duration | End Time | Value |
|---|---|---|---|---|
| Periodo 1 | 6:00 AM | 2h 30m | 8:30 AM | 1 |
| *(Descanso 15 min)* | | | | |
| Periodo 2 | 8:45 AM | 2h 45m | 11:30 AM | 1 |
| *(Colación 45 min)* | | | | |
| Periodo 3 | 12:15 PM | 2h 30m | 2:45 PM | 1 |
| *(Descanso 15 min)* | | | | |
| Periodo 4 | 3:00 PM | 1h 00m | 4:00 PM | 1 |

> Total neto = **405 min** ✓. Los descansos están desfasados 30 min respecto al Grupo A.

#### Patrón C: `PatronPanaderoGrupoC` (Descanso intermedio)

| Work Period | Start Time | Duration | End Time | Value |
|---|---|---|---|---|
| Periodo 1 | 6:00 AM | 2h 15m | 8:15 AM | 1 |
| *(Descanso 15 min)* | | | | |
| Periodo 2 | 8:30 AM | 2h 30m | 11:00 AM | 1 |
| *(Colación 45 min)* | | | | |
| Periodo 3 | 11:45 AM | 3h 00m | 2:45 PM | 1 |
| *(Descanso 15 min)* | | | | |
| Periodo 4 | 3:00 PM | 1h 00m | 4:00 PM | 1 |

> Total neto = **405 min** ✓

#### Patrón D: `PatronManipulador` (Turno completo)

| Work Period | Start Time | Duration | End Time | Value |
|---|---|---|---|---|
| Periodo 1 | 6:00 AM | 3h 45m | 9:45 AM | 1 |
| *(Descanso 15 min)* | | | | |
| Periodo 2 | 10:00 AM | 2h 30m | 12:30 PM | 1 |
| *(Colación 45 min)* | | | | |
| Periodo 3 | 1:15 PM | 2h 15m | 3:30 PM | 1 |
| *(Descanso 15 min)* | | | | |
| Periodo 4 | 3:45 PM | 2h 15m | 6:00 PM | 1 |

#### Patrón E: `PatronRefuerzoVespertino` (Turno parcial para peak)

| Work Period | Start Time | Duration | End Time | Value |
|---|---|---|---|---|
| Periodo 1 | 2:00 PM | 3h 45m | 5:45 PM | 1 |
| *(Descanso 15 min)* | | | | |
| Periodo 2 | 6:00 PM | 4h 00m | 10:00 PM | 1 |

> Total neto = **465 min** (7h 45m). Cubre producción para el peak de 18:00–20:00.

### Paso 6.2 — Crear Work Schedules

En **Data** → **Schedules** → sección **Work Schedules**:

| Work Schedule | Day Pattern | Days | Start Date |
|---|---|---|---|
| `TurnoPanaderoA` | `PatronPanaderoGrupoA` | 1 (diario) | Lunes |
| `TurnoPanaderoB` | `PatronPanaderoGrupoB` | 1 (diario) | Lunes |
| `TurnoPanaderoC` | `PatronPanaderoGrupoC` | 1 (diario) | Lunes |
| `TurnoManipulador` | `PatronManipulador` | 1 (diario) | Lunes |
| `TurnoRefuerzo` | `PatronRefuerzoVespertino` | 1 (diario) | Lunes |

> **Ref. SASMAA7 §7.2.1**: "A Work Schedule includes a combination of Day Patterns to make up a repeating work period. The repeating period can be between 1 and 28 days."

### Paso 6.3 — Implementar escalonamiento con múltiples Resources

> **Problema**: SIMIO asigna un único Work Schedule a todo el recurso. Para escalonar descansos entre grupos de panaderos, se necesitan **múltiples Resources** (uno por grupo de turno).
>
> **Ref. Workbook §4.5**: "Para escalonar descansos, crear múltiples Work Schedules con patrones ligeramente desfasados y asignar subconjuntos de la capacidad a cada uno."

#### Paso 6.3.1 — Separar `ResPanadero` en 3 sub-recursos

Eliminar el Resource genérico `ResPanadero` y crear:

| Resource | Nombre | Initial Capacity | Work Schedule |
|---|---|---|---|
| Resource | `ResPanaderoA` | 3 | `TurnoPanaderoA` |
| Resource | `ResPanaderoB` | 3 | `TurnoPanaderoB` |
| Resource | `ResPanaderoC` | 3 | `TurnoPanaderoC` |

**Capacity Type** de cada uno: `Work Schedule`

#### Paso 6.3.2 — Crear una List para agruparlos

Ir a **Data** → **Lists** → **Create List** → Nombre: `ListaPanaderos`
- Tipo: **Resource List**
- Agregar: `ResPanaderoA`, `ResPanaderoB`, `ResPanaderoC`

#### Paso 6.3.3 — Usar la List en Secondary Resources

En cada Server que requiere un panadero:
1. Clic en Server → **Secondary Resources** → **Seize**
2. **Object Type**: `Specific` → seleccionar `ListaPanaderos`
3. **Selection Rule**: `Preferred Order` (intenta tomar del primero disponible)
4. **Number of Units**: `1`

> Esto permite que cuando el Grupo A está en descanso, los Servers automáticamente toman panaderos de los Grupos B o C que siguen activos.

#### Paso 6.3.4 — Configurar Manipuladores

| Resource | Nombre | Initial Capacity | Capacity Type | Work Schedule |
|---|---|---|---|---|
| Resource | `ResManipulador` | 2 | Work Schedule | `TurnoManipulador` |
| Resource | `ResAyudante` | 2 | Work Schedule | `TurnoManipulador` |

#### Paso 6.3.5 — Configurar Refuerzo Vespertino (opcional, para experimentar)

| Resource | Nombre | Initial Capacity | Capacity Type | Work Schedule |
|---|---|---|---|---|
| Resource | `ResPanaderoRefuerzo` | 2 | Work Schedule | `TurnoRefuerzo` |

Agregar `ResPanaderoRefuerzo` a `ListaPanaderos` para que esté disponible automáticamente durante el turno vespertino.

### Paso 6.4 — Cobertura resultante (verificación)

La siguiente tabla muestra la cobertura mínima garantizada por hora:

| Hora | Grupo A | Grupo B | Grupo C | Refuerzo | **Mínimo disponible** |
|---|---|---|---|---|---|
| 06:00–08:00 | ✓ (3) | ✓ (3) | ✓ (3) | — | **9** |
| 08:00–08:15 | ✗ | ✓ (3) | ✓ (3) | — | **6** |
| 08:15–08:30 | ✓ (3) | ✓ (3) | ✗ | — | **6** |
| 08:30–08:45 | ✓ (3) | ✓ (3) | ✓ (3) | — | **9** |
| 11:00–11:45 | ✗ (col.) | ✓ (3) | ✗ (col.) | — | **3** |
| 11:45–12:15 | ✓ (3) | ✗ (col.) | ✓ (3) | — | **6** |
| 14:00–16:00 | ✓ (3) | ✓ (3) | ✓ (3) | ✓ (2) | **11** |
| 18:00–20:00 | — | — | — | ✓ (2) | **2** |

> **Resultado**: Durante la colación, siempre hay al menos 3 panaderos activos. Nunca se detiene la producción completamente.

### Paso 6.5 — Off-Shift Behavior

Para cada Resource, configurar en Properties:
- **Off Shift Rule**: `Finish Work Already Started`

> **Ref. SASMAA7 §7.2.2**: "You might implement logic so that 30 minutes before the end of the shift, he'd stop accepting new work, but if work was still in progress at the end of the shift he'd continue working until it was complete." La opción `Finish Work Already Started` logra esto automáticamente.

Opciones disponibles:
| Opción | Comportamiento |
|---|---|
| `Finish Work Already Started` | Termina el lote en proceso antes de ir a descanso **(recomendado)** |
| `Suspend Processing` | Pausa el trabajo y lo retoma después del descanso |
| `Force Off Shift` | Abandona inmediatamente (no recomendado para producción) |

---

> **Continúa en Parte 3**: Processes (lógica de compra del cliente, asignación de tipo de pan, política de horno), Experiments y análisis de resultados.
