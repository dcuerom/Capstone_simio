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

#### **Step 4 — Decide: ¿Alguna familia alcanzó la capacidad del horno (600 kg)?**

| Campo               | Valor                                               |
| ------------------- | --------------------------------------------------- |
| **Type**      | Decide                                              |
| **Condition** | `Model.MStaColaHorno[1] >= 600 OR Model.MStaColaHorno[2] >= 600 OR Model.MStaColaHorno[3] >= 600` |

> **Por qué evaluar las 3 familias y no solo `EntLote.EStaFamilia`**: El trigger se dispara por el lote que *acaba* de salir de fermentación, pero otras familias pueden haber acumulado 600 kg antes de que esa familia lo haga. Si solo se evalúa la familia disparadora, una familia con cola llena queda esperando indefinidamente hasta que un nuevo lote suyo vuelva a disparar el proceso.
>
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

#### **Step 5F — Decide: ¿Alguna familia lleva >= 15 minutos esperando?** *(rama de corrida anticipada)*

| Campo               | Valor                                                               |
| ------------------- | ------------------------------------------------------------------- |
| **Type**      | Decide                                                              |
| **Condition** | `(Model.MStaColaHorno[1] > 0 AND (Run.TimeNow - Model.MStaTimerHorno[1]) >= 15) OR (Model.MStaColaHorno[2] > 0 AND (Run.TimeNow - Model.MStaTimerHorno[2]) >= 15) OR (Model.MStaColaHorno[3] > 0 AND (Run.TimeNow - Model.MStaTimerHorno[3]) >= 15)` |

> **Por qué evaluar las 3 familias y no solo `EntLote.EStaFamilia`**: Igual que en Step 4, una familia puede haber agotado sus 15 minutos antes de que un nuevo lote suyo vuelva a disparar el proceso. La guarda `MStaColaHorno[f] > 0` es necesaria para que el timer residual de una cola vacía (valor anterior no reseteado) no active una corrida falsa.
>
> **¿Por qué 15 minutos?** Es el tiempo máximo que puede estar la masa en fermentación final esperando sin comprometer calidad (supuesto operacional del reporte §2.4). Si ninguna familia llenó el horno en 15 min → hacer corrida anticipada con lo que haya.

**Rama True → Step 5F bis (Decide horno libre para corrida anticipada)**
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

#### **Step 6 — Seleccionar familia y iniciar corrida** *(compartido por ambas rutas)*

Step 6 ya no ejecuta los resets directamente. En su lugar, delega la decisión a `ProcSeleccionarFamiliaHorno`, que elige la familia según `PropPoliticaSecuenciaHorno` y ejecuta los resets sobre la familia elegida (no sobre `EntLote.EStaFamilia`).

| Sub-step | Type        | Configuración |
| -------- | ----------- | ------------- |
| 6        | **Execute** | Process: `ProcSeleccionarFamiliaHorno` |

> **Por qué Execute y no los Assign directos**: Los resets anteriores (6a–6d) usaban `EntLote.EStaFamilia` — la familia del lote que *disparó* el umbral. Pero con las políticas de secuencia (Estrategia A–D), la familia elegida puede ser distinta. `ProcSeleccionarFamiliaHorno` decide cuál familia entra al horno y ejecuta en su Bloque 3:
> - `MStaColaHorno[Token.FamiliaElegida] = 0`
> - `MStaTimerHorno[Token.FamiliaElegida] = 0`
> - `MStaHornosEnUso = MStaHornosEnUso + 1`
> - `MStaUltimaFamiliaHorno = Token.FamiliaElegida`
> - Fire `EvtIniciarCorrida`
>
> La familia que disparó el umbral pero no fue elegida conserva su cola y timer: seguirá acumulando hasta que en la siguiente oportunidad sea la más prioritaria.

---

### 2.4 — Diagrama visual completo del Process✅

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ProcPoliticaCargaHorno                                                  │
│                                                                          │
│  ┌─────────┐   ┌──────────────────┐   ┌──────────────────────────────┐  │
│  │ Step 1  │──▶│ Step 2 (Decide)  │──▶│ Step 3 (Assign Timer)        │  │
│  │ Assign  │   │ ¿Primer lote de  │   │ MStaTimerHorno[f]=TimeNow    │  │
│  │ cola+=kg│   │  esta familia?   │   └──────────────┬───────────────┘  │
│  └─────────┘   └──────────────────┘         False ↑  │ True             │
│                       │ False                    └───┘                   │
│                       └──────────────────────────────┘                   │
│                                          ↓                               │
│                     ┌────────────────────────────────────┐               │
│                     │ Step 4 (Decide)                    │               │
│                     │ ¿ColaF1>=600 OR ColaF2>=600        │               │
│                     │       OR ColaF3>=600?              │               │
│                     └────────────────────────────────────┘               │
│                        True ↓                    ↓ False                 │
│            ┌───────────────────┐   ┌─────────────────────────────┐       │
│            │ Step 5T (Decide)  │   │ Step 5F (Decide)            │       │
│            │ Hornos libres?    │   │ ¿EsperaF1>=15 OR EsperaF2   │       │
│            └───────────────────┘   │   >=15 OR EsperaF3>=15?     │       │
│       True ↓       ↓ False         └─────────────────────────────┘       │
│    ┌────────────┐  FIN          True ↓                    ↓ False        │
│    │  Step 6    │          ┌──────────────────┐           FIN             │
│    │  Execute   │          │ Step 5Fbis       │                           │
│    │  ProcSelec │          │ Hornos libres?   │                           │
│    │  cionarFam │          └──────────────────┘                           │
│    │  iliaHorno │     True ↓           ↓ False                            │
│    └────────────┘  ┌────────────┐      FIN                                │
│          ↑         │  Step 6    │                                         │
│          └─────────│  Execute   │                                         │
│                    │  ProcSelec │                                         │
│                    │  cionarFam │                                         │
│                    │  iliaHorno │                                         │
│                    └────────────┘                                         │
└──────────────────────────────────────────────────────────────────────────┘
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

## PARTE 3: Elemento de Sincronización — `EvtIniciarCorrida` y control de compuerta

Cuando `ProcSeleccionarFamiliaHorno` (Bloque 3) dispara `EvtIniciarCorrida`, ese evento debe abrir la compuerta de carga solo para los lotes de la familia elegida. Sin este mecanismo, todos los lotes de todas las familias fluirían mezclados al horno, violando la restricción de que una corrida es de una sola familia.

La solución tiene tres piezas: (1) servidores de espera por familia controlados por estado, (2) un proceso que abre la compuerta al ocurrir el evento, y (3) un proceso que la cierra al terminar el horneado.

---

### 3.1 — Crear el Event

1. Ir a **Definitions** → **Elements** → **Events** → **Add Event**
2. Nombre: `EvtIniciarCorrida`

---

### 3.2 — Nuevas variables de estado necesarias

Ir a **Definitions → States** y crear:

| Nombre | Tipo | Rows | Valor Inicial | Propósito |
|---|---|---|---|---|
| `MStaCapEspera` | Discrete (Integer) Array | 3 | 0 | Capacidad activa de cada servidor de espera por familia. `0` = bloqueado, `999` = abierto. |
| `MStaLotesEnHorno` | Discrete (Integer) | 1 | 0 | Contador de lotes actualmente dentro de `SrvHorneado`. Detecta cuándo termina una corrida completa. |

---

### 3.3 — Reconfigurar el pipeline: añadir servidores de espera por familia

En lugar de que los lotes vayan directamente de `SrvFermentacion` a `SrvCargaHorno`, se insertan tres servidores de espera — uno por familia — que actúan como compuertas.

> **⚠️ Nota sobre Capacity Type**: SIMIO solo ofrece dos opciones en el dropdown Capacity Type: **Fixed** y **WorkSchedule**. No existe la opción "From State". El comportamiento equivalente se logra dejando Capacity Type = **Fixed** y escribiendo la expresión de estado directamente en el campo **Initial Capacity**, como se detalla a continuación.

#### Nuevos servidores a arrastrar al Facility

| Nombre | Processing Time | Capacity Type | Initial Capacity | Propósito |
|---|---|---|---|---|
| `SrvEsperaF1` | `0` | Fixed | `Model.MStaCapEspera[1]` | Retiene lotes de Familia 1 hasta que su corrida sea autorizada |
| `SrvEsperaF2` | `0` | Fixed | `Model.MStaCapEspera[2]` | Retiene lotes de Familia 2 |
| `SrvEsperaF3` | `0` | Fixed | `Model.MStaCapEspera[3]` | Retiene lotes de Familia 3 |

**Cómo configurar cada servidor:**
1. Arrastrar un **Server** al Facility y nombrarlo `SrvEsperaF1`
2. En el Property Inspector → **Processing Time** = `0`
3. **Capacity Type** = `Fixed` (dejarlo en Fixed — no cambiarlo)
4. En el campo **Initial Capacity**: borrar el `1` por defecto y escribir la expresión `Model.MStaCapEspera[1]`
5. Repetir para `SrvEsperaF2` (`Model.MStaCapEspera[2]`) y `SrvEsperaF3` (`Model.MStaCapEspera[3]`)

> **¿Cómo funciona?** Al escribir una expresión de estado en Initial Capacity, SIMIO evalúa esa expresión cada vez que la variable cambia. Como `MStaCapEspera` arranca en `0`, el servidor inicia bloqueado — ningún lote puede entrar ni ser procesado, y se acumulan en el Input Buffer. Cuando `ProcAbrirCargaHorno` asigna `MStaCapEspera[f] = 999`, SIMIO re-evalúa la capacidad del servidor correspondiente y libera todos los lotes retenidos.
>
> **Si SIMIO no re-evalúa dinámicamente la expresión** (puede ocurrir en versiones antiguas): el fallback es reemplazar `SrvEsperaFx` por **BasicNodes con Input Buffer ilimitado** y controlar el flujo mediante el peso de salida del conector hacia `SrvCargaHorno` — configurar el Selection Weight del link de salida como `Model.MStaCapEspera[f]`. Con valor `0` el link no se usa; con `999` los lotes fluyen. En este caso `MStaCapEspera` sigue siendo el mismo array, y `ProcAbrirCargaHorno` no cambia.
>
> **Processing Time = 0**: El servidor de espera no consume tiempo de simulación, solo actúa como compuerta.

#### Nueva secuencia de conexiones

Reemplazar la conexión directa `SrvFermentacion → SrvCargaHorno` por:

```
SrvFermentacion
    ↓
[TransferNode: NodoSalidaFermentacion]
    ├─ EntLote.EStaFamilia == 1  →  SrvEsperaF1  ─┐
    ├─ EntLote.EStaFamilia == 2  →  SrvEsperaF2  ──┼─→ SrvCargaHorno → SrvHorneado
    └─ EntLote.EStaFamilia == 3  →  SrvEsperaF3  ─┘
```

Para configurar el routing en `NodoSalidaFermentacion`:
1. Clic en el nodo → **Outbound Link Rule**: `By Expression`
2. En cada conector saliente, asignar **Selection Weight**:
   - Conector a `SrvEsperaF1`: `EntLote.EStaFamilia == 1`
   - Conector a `SrvEsperaF2`: `EntLote.EStaFamilia == 2`
   - Conector a `SrvEsperaF3`: `EntLote.EStaFamilia == 3`

---

### 3.4 — Proceso `ProcAbrirCargaHorno` (dispara la compuerta)

Este proceso escucha `EvtIniciarCorrida` y abre brevemente la compuerta de la familia elegida, dejando pasar todos los lotes que estaban esperando. Luego cierra la compuerta para que los lotes que lleguen después de esta corrida queden retenidos.

**Crear el proceso**:
1. Ir a **Definitions** → **Processes** → **Create Process**
2. Nombre: `ProcAbrirCargaHorno`
3. **Triggering Event**: `EvtIniciarCorrida.Occurred`

**Steps**:

| Step | Tipo | Configuración | Nota |
|---|---|---|---|
| 1 | **Assign** | `Model.MStaCapEspera[Model.MStaUltimaFamiliaHorno] = 999` | Abre la compuerta: todos los lotes en espera de la familia elegida fluyen instantáneamente hacia `SrvCargaHorno` |
| 2 | **Delay** | `0.01` minutos | Pausa mínima para que SIMIO procese el vaciado del buffer antes de cerrar |
| 3 | **Assign** | `Model.MStaCapEspera[Model.MStaUltimaFamiliaHorno] = 0` | Cierra la compuerta: los lotes que lleguen después de esta corrida quedarán retenidos en `SrvEsperaFx` |

> El delay de `0.01` min no es tiempo real de producción — es la pausa mínima necesaria para que el motor de SIMIO libere todas las entidades acumuladas en el buffer antes de que se ejecute el Assign de cierre. Sin este delay, el Assign de apertura y cierre ocurrirían en el mismo instante de simulación y ningún lote pasaría.

---

### 3.5 — Proceso `ProcHornoCompleto` (libera el cupo al terminar la corrida)

Este proceso se dispara cuando cada lote sale de `SrvHorneado`. Usa `MStaLotesEnHorno` para detectar cuándo fue el ÚLTIMO lote de la corrida, y solo entonces decrementa `MStaHornosEnUso` — evitando que el contador baje varias veces por corrida.

#### Trigger: `SrvHorneado.Entered` (para el contador de subida)

En `SrvHorneado` → **Add-On Process Triggers** → **Entered** → crear proceso inline o `ProcContarEntradaHorno`:

| Step | Tipo | Configuración |
|---|---|---|
| 1 | **Assign** | `Model.MStaLotesEnHorno = Model.MStaLotesEnHorno + 1` |

#### Trigger: `SrvHorneado.Exited` (para el contador de bajada y liberación)

En `SrvHorneado` → **Add-On Process Triggers** → **Exited** → crear `ProcHornoCompleto`:

| Step | Tipo | Configuración | Salida |
|---|---|---|---|
| 1 | **Assign** | `Model.MStaLotesEnHorno = Model.MStaLotesEnHorno - 1` | → paso 2 |
| 2 | **Decide** | `Model.MStaLotesEnHorno == 0` | True → paso 3 \| False → EndProcess |
| 3 | **Assign** | `Model.MStaHornosEnUso = Math.Max(0, Model.MStaHornosEnUso - 1)` | → EndProcess |

> **Por qué no decrementar en cada Exited directamente**: Si hay 8 lotes en la corrida, `SrvHorneado.Exited` se dispara 8 veces. Decrementar `MStaHornosEnUso` en cada disparo lo llevaría a valores negativos y habilitaría nuevas corridas antes de que el horno esté realmente libre. El check `MStaLotesEnHorno == 0` garantiza que el decremento ocurre solo cuando el último lote sale.
>
> **`Math.Max(0, ...)`**: Guarda de seguridad por si el contador llegase a 0 inesperadamente antes de que todos los lotes salgan (por ejemplo, por condiciones de carrera entre réplicas).

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

Ir a **Definitions → States** y crear **todos** los siguientes antes de construir los processes. El orden importa: los processes referencian estas variables y SIMIO no compilará si no existen.

| Nombre | Tipo | Rows | Valor Inicial | Propósito |
|---|---|---|---|---|
| `MStaColaHorno` | Real Array | 3 | 0 | Kg lógicos acumulados por familia esperando horno (contador para política de carga) |
| `MStaTimerHorno` | Real Array | 3 | 0 | `Run.TimeNow` en que llegó el primer lote de cada familia (para la regla de 15 min) |
| `MStaHornosEnUso` | Discrete (Integer) | 1 | 0 | Corridas de horno activas. Incrementa al disparar `EvtIniciarCorrida`, decrementa al terminar la corrida |
| `MStaCapEspera` | Discrete (Integer) Array | 3 | 0 | Capacidad de `SrvEsperaF1/F2/F3`. `0` = bloqueado, `999` = abierto para paso de lotes |
| `MStaLotesEnHorno` | Discrete (Integer) | 1 | 0 | Lotes actualmente dentro de `SrvHorneado`. Detecta fin de corrida cuando llega a 0 |

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
| Corridas totales horno | Tally Statistic en `ProcAbrirCargaHorno` Step 1 | ~25–35 corridas/día |

> **Ref. Workbook6 §2.4.7–2.4.9**: "The InputBuffer Content shows the average number waiting. ScheduledUtilization = tiempo utilizado / tiempo disponible."

---

## Resumen del Flujo Completo

```
SrvFermentacion (Exited trigger)   ← Fermentación Final, justo antes de SrvCargaHorno
    ↓
ProcPoliticaCargaHorno
    ├─ Step 1:  Acumula kg en MStaColaHorno[EntLote.EStaFamilia]
    ├─ Step 2:  ¿Primer lote de esta familia? → Step 3: registrar MStaTimerHorno[familia]
    ├─ Step 4:  ¿ColaF1>=600 OR ColaF2>=600 OR ColaF3>=600?
    │    SÍ  → Step 5T:  ¿Hay hornos libres?
    │               SÍ  → Step 6: Execute ProcSeleccionarFamiliaHorno
    │               NO  → FIN
    │    NO  → Step 5F:  ¿EsperaF1>=15 OR EsperaF2>=15 OR EsperaF3>=15?
    │               SÍ  → Step 5Fbis: ¿Hay hornos libres?
    │                          SÍ  → Step 6: Execute ProcSeleccionarFamiliaHorno
    │                          NO  → FIN
    │               NO  → FIN (esperar más lotes)
    └─ (resets y Fire se ejecutan dentro de ProcSeleccionarFamiliaHorno, Bloque 3)

ProcSeleccionarFamiliaHorno  (invocado vía Execute desde Step 6)
    ├─ Bloque 0: Calcular tiempos de espera por familia
    ├─ Bloque 1: Override de calidad (familia con espera >=15 min tiene prioridad)
    ├─ Bloque 2: Si no hay emergencia → selección por menor stock / mayor demanda / round-robin / híbrida
    └─ Bloque 3: Reset MStaColaHorno[FamiliaElegida] + MStaTimerHorno[FamiliaElegida]
                 + MStaHornosEnUso++ + MStaUltimaFamiliaHorno = FamiliaElegida
                 + Fire EvtIniciarCorrida

EvtIniciarCorrida.Occurred
    ↓
ProcAbrirCargaHorno
    ├─ Assign: MStaCapEspera[MStaUltimaFamiliaHorno] = 999   ← abre compuerta
    ├─ Delay: 0.01 min                                        ← lotes fluyen a SrvCargaHorno
    └─ Assign: MStaCapEspera[MStaUltimaFamiliaHorno] = 0     ← cierra compuerta

SrvEsperaFx → SrvCargaHorno (5 min carga) → SrvHorneado

SrvHorneado (Entered trigger)
    ↓
    Assign: MStaLotesEnHorno = MStaLotesEnHorno + 1

SrvHorneado (Exited trigger)
    ↓
ProcHornoCompleto
    ├─ Assign: MStaLotesEnHorno = MStaLotesEnHorno - 1
    └─ Decide: MStaLotesEnHorno == 0?
         SÍ → Assign: MStaHornosEnUso = Math.Max(0, MStaHornosEnUso - 1)
         NO → EndProcess  (aún hay lotes horneando, no liberar)
```
