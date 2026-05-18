# Paso 7.5 — Política de Carga del Horno: Opción B (Con Process)

### Implementación detallada en SIMIO

> **Ref. Workbook6 §7.2–7.3**: "The Add-On Process Trigger fires a process based on an event in the object's lifecycle. The pattern Assign → Decide → Assign is the standard for branching logic in Processes."
>
> **Ref. Workbook6 §3.5**: El patrón de estados globales del modelo (`Model.MStaXxx`) permite coordinar lógica entre objetos que de otro modo no se comunicarían.

---

## Contexto: ¿Qué modela esta política?

En la panadería real, un manipulador no mete al horno cada lote individualmente en cuanto llega. La práctica operativa es:

1. **Acumular** lotes de la misma familia hasta llenar la capacidad del horno (~600 kg de capacidad neta por corrida).
2. **Si el horno se llena** → meter inmediatamente (corrida de capacidad completa).
3. **Si el horno no se llena en 15 min** → meter lo que hay (corrida anticipada para no arruinar la masa fermentada).

La Opción B modela este comportamiento con un **Process** que se dispara cada vez que un lote sale de `SrvFermentacion`.

---

## PARTE 1: Preparación — Variables de Estado Necesarias

### 1.1 — Crear el State Array `MStaColaHorno ✅`

Antes de crear el Process, necesitas el estado que acumula los kg en cola, **separado por familia** (Familia 1, 2, 3).

1. Ir a **Definitions** → **States** → **Add State**
2. Configurar:

| Propiedad               | Valor                               |
| ----------------------- | ----------------------------------- |
| **Name**          | `MStaColaHorno`                   |
| **Type**          | `Real Array`                      |
| **Initial Value** | `0`                               |
| **Rows**          | `3` (una por familia de horneado) |

> **¿Por qué un array de 3?** Cada familia (masas blandas, masas duras, masas enriquecidas) tiene su propia corrida en el horno. No mezclas familias en la misma hornada. El índice 1 = Familia 1, índice 2 = Familia 2, índice 3 = Familia 3.

### 1.2 — Crear el State `MStaTimerHorno✅`

Necesitas saber **cuándo entró el primer lote de la cola actual** para calcular el tiempo de espera máximo.

1. Ir a **Definitions** → **States** → **Add State**
2. Configurar:

| Propiedad               | Valor              |
| ----------------------- | ------------------ |
| **Name**          | `MStaTimerHorno` |
| **Type**          | `Real Array`     |
| **Initial Value** | `0`              |
| **Rows**          | `3`              |

> Este array guardará el `Run.TimeNow` en el momento en que el primer lote de cada familia llegó a `SrvCargaHorno`. Permite calcular `Run.TimeNow - MStaTimerHorno[familia]` para saber cuánto llevan esperando.

### 1.3 — Crear el State `MStaHornosEnUso  ✅`

Para evitar disparar más corridas de las que la capacidad física permite (especialmente cuando hay múltiples hornos), se necesita un contador de hornos actualmente en ciclo.

1. Ir a **Definitions** → **States** → **Add State**

| Propiedad               | Valor                  |
| ----------------------- | ---------------------- |
| **Name**          | `MStaHornosEnUso`    |
| **Type**          | `Discrete (Integer)` |
| **Initial Value** | `0`                  |

> *Nota:* Al usar un Integer en lugar de un Boolean, la lógica escala automáticamente si experimentas con 1, 2 o más hornos (`PropNumHornos`).

---

## PARTE 2: Crear el Process `ProcPoliticaCargaHorno`

### 2.1 — Crear el Process ✅

1. Ir a **Definitions** → **Processes** → **Create Process**
2. Nombre: `ProcPoliticaCargaHorno`
3. **No** configurar un Triggering Event aún (se asociará como Add-On Trigger en el paso 2.5).

### 2.2 — Construir los Steps del Process

El diagrama lógico completo es:

```
[ENTRADA: lote sale de SrvFermentacion]
        ↓
[Step 1 — Assign: sumar kg a la cola de su familia]
        ↓
[Step 2 — Decide: ¿es el primer lote de esta familia en cola?]
     Sí ↓                         No ↓ (saltar a Step 4)
[Step 3 — Assign: registrar tiempo de entrada (timer)]
        ↓
[Step 4 — Decide: ¿Cola >= 600 kg?]
     Sí ↓                         No ↓
[Step 5T — Decide: ¿Hay hornos libres?]  [Step 5F — Decide: ¿Tiempo espera >= 15 min?]
     Sí ↓    No ↓ (FIN)               Sí ↓                 No ↓ (FIN)
[Step 6 — Iniciar corrida]         [Step 6 — Decide: ¿Hay hornos libres?]
                                       Sí ↓    No ↓ (FIN)
                                  [Step 7 — Iniciar corrida anticipada]
                                
[Iniciar corrida = Assign: resetear cola + MStaHornosEnUso++ + Fire evento]
```

### 2.3 — Detalle paso a paso de cada Step

#### **Step 1 — Assign: Acumular kg ✅**

| Campo                    | Valor                                                             |
| ------------------------ | ----------------------------------------------------------------- |
| **Type**           | Assign                                                            |
| **State Variable** | `Model.MStaColaHorno[EntLote.EStaFamilia]`                      |
| **New Value**      | `Model.MStaColaHorno[EntLote.EStaFamilia] + EntLote.EStaKgLote` |

> Cada vez que un lote termina fermentación, sus kg se suman al acumulador de su familia.

---

#### **Step 2 — Decide: ¿Es el primer lote de esta familia? ✅**

| Campo               | Valor                                                              |
| ------------------- | ------------------------------------------------------------------ |
| **Type**      | Decide                                                             |
| **Condition** | `Model.MStaColaHorno[EntLote.EStaFamilia] == EntLote.EStaKgLote` |

> **¿Por qué esta condición?** Si la cola ahora es igual al tamaño de *este* lote, significa que antes estaba en 0 → este lote es el primero. Solo entonces registramos el timer.
>
> **Ref. Workbook6 §7.3**: "Use a Decide step with a condition to branch the token flow. True and False branches exit from the right and bottom of the Decide step respectively."

**Rama True → Step 3:**

#### **Step 3 — Assign: Registrar timer de inicio ✅**

| Campo                    | Valor                                         |
| ------------------------ | --------------------------------------------- |
| **Type**           | Assign                                        |
| **State Variable** | `Model.MStaTimerHorno[EntLote.EStaFamilia]` |
| **New Value**      | `Run.TimeNow`                               |

> `Run.TimeNow` es la expresión estándar de SIMIO para el tiempo de simulación actual (en minutos si los units están en minutos).

**Ambas ramas convergen en → Step 4:**

---

#### **Step 4 — Decide: ¿Se alcanzó la capacidad del horno (600 kg)? ✅**

| Campo               | Valor                                               |
| ------------------- | --------------------------------------------------- |
| **Type**      | Decide                                              |
| **Condition** | `Model.MStaColaHorno[EntLote.EStaFamilia] >= 600` |

> **El valor 600** representa la capacidad máxima de una corrida del horno. Ajustar según el reporte §4.3 si la capacidad física es diferente.
>
> **Ref. Workbook6 §7.2**: El Decide step en un Process ejecuta *ambas* ramas como flujos independientes de tokens. El token toma solo una rama según la condición.

**Rama True → Step 5T:**

---

#### **Step 5T — Decide: ¿Hay hornos libres?** *(rama de capacidad completa) ✅*

| Campo               | Valor                                     |
| ------------------- | ----------------------------------------- |
| **Type**      | Decide                                    |
| **Condition** | `Model.MStaHornosEnUso < PropNumHornos` |

> *Nota:* `PropNumHornos` es la Referenced Property creada para controlar la cantidad de hornos en tus experimentos (típicamente 1 o 2). También puedes usar directamente `SrvHorneado.Capacity.Average` si no usas la propiedad referenciada.

**Rama True → Step 6 (Iniciar corrida completa)**
**Rama False → FIN** *(el lote queda en cola; cuando un horno se libere, el próximo lote en salir de SrvFermentacion disparará el proceso nuevamente)*

---

**Rama False del Step 4 → Step 5F:**

#### **Step 5F — Decide: ¿Tiempo de espera >= 15 minutos?** *(rama de corrida anticipada) ✅*

| Campo               | Valor                                                               |
| ------------------- | ------------------------------------------------------------------- |
| **Type**      | Decide                                                              |
| **Condition** | `(Run.TimeNow - Model.MStaTimerHorno[EntLote.EStaFamilia]) >= 15` |

> **¿Por qué 15 minutos?** Es el tiempo máximo que puede estar la masa fermentada esperando sin comprometer calidad (supuesto operacional del reporte §2.4). Si la cola no llenó el horno en 15 min → hacer corrida anticipada.

**Rama True → Step 6F (Decide horno libre para corrida anticipada)**
**Rama False → FIN** *(aún hay tiempo; esperar más lotes)*

---

#### **Step 5F bis — Decide: ¿Hay hornos libres?** *(para corrida anticipada) ✅*

| Campo               | Valor                                     |
| ------------------- | ----------------------------------------- |
| **Type**      | Decide                                    |
| **Condition** | `Model.MStaHornosEnUso < PropNumHornos` |

**Rama True → Step 6 (Iniciar corrida anticipada)**
**Rama False → FIN**

---

#### **Step 6 — Iniciar corrida del horno** *(compartido por ambas rutas) ✅*

Este bloque se compone de 3 Assign consecutivos + 1 Fire:

| Sub-step | Type             | State Variable                                | New Value                     |
| -------- | ---------------- | --------------------------------------------- | ----------------------------- |
| 6a       | **Assign** | `Model.MStaColaHorno[EntLote.EStaFamilia]`  | `0`                         |
| 6b       | **Assign** | `Model.MStaTimerHorno[EntLote.EStaFamilia]` | `0`                         |
| 6c       | **Assign** | `Model.MStaHornosEnUso`                     | `Model.MStaHornosEnUso + 1` |
| 6d       | **Fire**   | Event:`EvtIniciarCorrida`                   | *(ver Parte 3) ❎*          |

> **¿Por qué resetear la cola a 0 antes de Fire?** Evita doble conteo. El evento `EvtIniciarCorrida` será el disparador que mueve al lote a través de `SrvCargaHorno → SrvHorneado`. Los nuevos lotes que lleguen mientras el horno procesa empezarán a acumular desde 0 en `MStaColaHorno`.

---

### 2.4 — Diagrama visual completo del Process✅

```
┌─────────────────────────────────────────────────────────────────────┐
│  ProcPoliticaCargaHorno                                             │
│                                                                     │
│  ┌─────────┐   ┌──────────────────┐   ┌─────────────────────────┐  │
│  │ Step 1  │──▶│ Step 2 (Decide)  │──▶│ Step 3 (Assign Timer)   │  │
│  │ Assign  │   │ ¿Primer lote?    │   │ Timer=Run.TimeNow       │  │
│  │ cola+=kg│   └──────────────────┘   └────────────┬────────────┘  │
│  └─────────┘          │ False                       │ True          │
│                       └─────────────────────────────┘              │
│                                          ↓                          │
│                               ┌──────────────────┐                 │
│                               │ Step 4 (Decide)  │                 │
│                               │ Cola >= 600?     │                 │
│                               └──────────────────┘                 │
│                        True ↓              ↓ False                  │
│                  ┌───────────────┐  ┌──────────────────┐           │
│                  │ Step 5T       │  │ Step 5F (Decide) │           │
│                  │ Hornos libres?│  │ Espera >= 15min? │           │
│                  └───────────────┘  └──────────────────┘           │
│           True ↓       ↓ False  True ↓           ↓ False           │
│        ┌────────┐     FIN   ┌─────────┐          FIN               │
│        │Step 6  │           │Step 5Fbis│                            │
│        │Corrida │           │Hornos   │                            │
│        │completa│           │libres?  │                            │
│        └────────┘           └─────────┘                            │
│        └────────┘    True ↓       ↓ False                          │
│             ↑      ┌────────┐    FIN                                │
│             └──────│Step 6  │                                       │
│                    │Corrida │                                       │
│                    │anticipad│                                      │
│                    └────────┘                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 2.5 — Asociar el Process como Add-On Trigger en `SrvFermentacion ✅`

1. En el **Facility**, hacer clic en `SrvFermentacion`
2. En el **Property Inspector** → buscar sección **Add-On Process Triggers**
3. Expandir → **Exited** → clic en `...`
4. Seleccionar **`ProcPoliticaCargaHorno`**

> **¿Por qué Exited y no Entered?** El trigger **Exited** se dispara cuando la entidad (el lote) *termina* el servicio de fermentación y está lista para moverse. En este momento, tiene sus atributos completos (`EStaFamilia`, `EStaKgLote`) y puede ser evaluada.
>
> **Ref. Workbook6 §7.2**: "Add-On Process Triggers include: Before Entering, Entered, Processing, Exited, Failed. The 'Exited' trigger fires after the entity completes service and is about to move to the next object."

---

## PARTE 3: Elemento de Sincronización — Event `EvtIniciarCorrida`

El **Fire** del Step 6d necesita un Event que sincronice la apertura del horno. Sin este evento, Simio no tiene cómo notificar a `SrvCargaHorno` que puede procesar.

### 3.1 — Crear el Event ✅

1. Ir a **Definitions** → **Elements** → **Events** → **Add Event**
2. Nombre: `EvtIniciarCorrida`

### 3.2 — Configurar `SrvCargaHorno` para escuchar el evento

En lugar de un Processing Time estático, `SrvCargaHorno` actuará como punto de control:

1. Clic en `SrvCargaHorno` → Properties
2. **Processing Time**: `5` (minutos — tiempo de carga física de lotes al horno)
3. En **Add-On Process Triggers** → **Entered** → crear nuevo process `ProcHornoCompleto`:

#### Process `ProcHornoCompleto` (en `SnkLoteTerminado` o al final de `SrvHorneado`)

Este process libera un cupo de horno cuando el ciclo de horneado termina:

| Step | Type             | Configuración                                                         |
| ---- | ---------------- | ---------------------------------------------------------------------- |
| 1    | **Assign** | `Model.MStaHornosEnUso` = `Math.Max(0, Model.MStaHornosEnUso - 1)` |

> **Ubicación correcta del trigger**: Asociar este Process al **Exited** de `SrvHorneado` (o al **Entered** de `SrvDescargaHorno`). Así, se resta 1 a los hornos en uso, permitiendo que el siguiente lote en cola dispare una nueva corrida.

---

## PARTE 4: Alternativa Simplificada con Delay (sin Event)

Si la implementación con Fire/Event resulta compleja, el Workbook6 §7.3 sugiere usar un **Delay** step dentro del Process para simular la "espera" hasta que se cumple el tiempo máximo:

### Process alternativo `ProcEsperaHorno`

Trigger: **Exited** de `SrvFermentacion`

| Step           | Type             | Configuración                                                               |
| -------------- | ---------------- | ---------------------------------------------------------------------------- |
| 1              | **Assign** | `MStaColaHorno[EStaFamilia]` += `EStaKgLote`                             |
| 2              | **Decide** | `MStaColaHorno[EStaFamilia] >= 600`                                        |
| 3T (True)      | **Assign** | Resetear cola + flag                                                         |
| 3F (False)     | **Delay**  | `15 - (Run.TimeNow - MStaTimerHorno[EStaFamilia])` minutos                 |
| 4 (post-Delay) | **Decide** | `Model.MStaHornosEnUso < PropNumHornos AND MStaColaHorno[EStaFamilia] > 0` |
| 5 (True)       | **Assign** | Iniciar corrida anticipada                                                   |

> **⚠️ Limitación del Delay en Process**: El token que ejecuta el Delay bloquea ese "hilo" del proceso durante 15 min. Si llegan más lotes mientras tanto, crearán tokens adicionales que también ejecutarán el Delay. Esto puede generar corridas duplicadas. Por eso **se recomienda la Opción con Event** para mayor precisión.
>
> **Ref. Workbook6 §7.3**: "A Delay step holds the process token for the specified duration. Multiple tokens can coexist in a Process simultaneously."

---

## PARTE 5: Variables de Estado a Declarar (Resumen Final)

Ir a **Definitions → States** y crear todos los siguientes antes de construir los processes:

| Nombre              | Tipo               | Rows | Valor Inicial | Propósito                                                |
| ------------------- | ------------------ | ---- | ------------- | --------------------------------------------------------- |
| `MStaColaHorno`   | Real Array         | 3    | 0             | Kg acumulados por familia en cola del horno               |
| `MStaTimerHorno`  | Real Array         | 3    | 0             | Tiempo (min) en que llegó el primer lote de cada familia |
| `MStaHornosEnUso` | Discrete (Integer) | —   | 0             | Contador de hornos en ciclo activo                        |

---

## PARTE 6: Verificación y Debugging

### 6.1 — Status Labels recomendados

Agregar en **Drawing Tab → Status Label**:

| Label               | Expresión                                |
| ------------------- | ----------------------------------------- |
| `Cola Horno F1`   | `Model.MStaColaHorno[1]`                |
| `Cola Horno F2`   | `Model.MStaColaHorno[2]`                |
| `Cola Horno F3`   | `Model.MStaColaHorno[3]`                |
| `Hornos Ocupados` | `Model.MStaHornosEnUso`                 |
| `Timer F1`        | `Run.TimeNow - Model.MStaTimerHorno[1]` |

Durante la animación, deberías observar:

- `ColaHorno[f]` sube con cada lote que sale de `SrvFermentacion`
- Cuando llega a 600 (o a 15 min de espera) y hay capacidad, `MStaHornosEnUso` se incrementa en 1.
- `ColaHorno[f]` se resetea a 0
- Al terminar `SrvHorneado`, `MStaHornosEnUso` se reduce en 1.

### 6.2 — Qué verificar en Results

Tras ejecutar el modelo:

| Métrica               | Dónde encontrarla                                               | Valor esperado        |
| ---------------------- | ---------------------------------------------------------------- | --------------------- |
| Cola promedio en horno | Results →`SrvCargaHorno` → InputBuffer → Content → Average | < 3 lotes             |
| Utilización horno     | Results →`SrvHorneado` → ScheduledUtilization                | 70–90%               |
| Corridas totales horno | Tally Statistic en Step 6c                                       | ~25–35 corridas/día |

> **Ref. Workbook6 §2.4.7–2.4.9**: "The InputBuffer Content shows the average number waiting. ScheduledUtilization = tiempo utilizado / tiempo disponible."

---

## Resumen del Flujo Completo

```
SrvFermentacion (Exited trigger)
    ↓
ProcPoliticaCargaHorno
    ├─ Acumula kg en MStaColaHorno[familia]
    ├─ Decide: ¿Primera vez? → registrar MStaTimerHorno
    ├─ Decide: ¿Cola >= 600?
    │    SÍ → Decide ¿Hay hornos libres? → Fire EvtIniciarCorrida
    │    NO → Decide ¿15 min esperados?
    │              SÍ → Decide ¿Hay hornos libres? → Fire EvtIniciarCorrida
    │              NO → FIN (esperar más lotes)
    └─ Fire resetea cola + Incrementa MStaHornosEnUso (+1)

SrvHorneado (Exited trigger)
    ↓
ProcHornoCompleto
    └─ Decrementa MStaHornosEnUso (-1)
```
