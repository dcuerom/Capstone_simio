# Diagrama de Flujo BPMN 2.0 — Panadería de Supermercado

> [!NOTE]
> Diagrama construido bajo los principios **BPMN 2.0** para el proyecto de simulación de eventos discretos en SIMIO. Cubre los tres subsistemas principales: **Producción**, **Gestión de Hornos** y **Sala de Ventas / Demanda**.

---

## 1. Vista General de Pools e Interacciones

```mermaid
graph LR
    subgraph SISTEMA["Sistema Panadería Supermercado"]
        P["Pool 1: Producción"]
        H["Pool 2: Gestión de Hornos"]
        V["Pool 3: Sala de Ventas y Demanda"]
    end
    P -- "Lote listo para horneado" --> H
    H -- "Pan horneado y enfriado" --> V
    V -- "Señal de quiebre / stock bajo" --> P
```

---

## 2. Pool 1 — Proceso de Producción (por tipo de pan)

> **Lanes:** Panadero · Mezcladora · Amasadora · Mesa de Formado · Cámara de Fermentación

```mermaid
flowchart TD
    START(("⬤ Inicio de Jornada<br/>Pre-apertura"))

    subgraph LANE_PANADERO["🧑‍🍳 Lane: Panadero"]
        A["Pesado y Dosificación<br/>⏱ 5 min<br/>📦 Lote según tipo"]
        C["Carga ingredientes<br/>en mezcladora<br/>⏱ 2 min"]
        E["Retiro de masa<br/>de mezcladora<br/>⏱ 1 min"]
        F["Amasado manual<br/>⏱ 10-15 min<br/>según tipo"]
        H_FORM["Dividido y Formado<br/>⏱ 8-12 min<br/>según tipo"]
    end

    subgraph LANE_MEZCLADORA["⚙️ Lane: Mezcladora"]
        D["Mezclado automático<br/>⏱ según tipo<br/>ciclo sin operario"]
    end

    subgraph LANE_AMASADORA["⚙️ Lane: Amasadora"]
        F2["Uso de Amasadora<br/>recurso compartido"]
    end

    subgraph LANE_FERMENTACION["🧪 Lane: Cámara de Fermentación"]
        G["Reposo / Fermentación<br/>en masa<br/>⏱ 15-30 min"]
        I["Fermentación final<br/>⏱ 20-45 min<br/>sin intervención"]
    end

    START --> A
    A --> C
    C --> D
    D --> E
    E --> F
    F --> F2
    F2 --> G
    G --> H_FORM
    H_FORM --> I
    I --> LOTE_LISTO(("◯ Lote listo<br/>para horneado"))
```

### Detalle de tiempos por etapa y tipo de pan

| Tipo de Pan | Pesado | Amasado | Reposo | Formado | Ferm. Final | Horneado | Enfriado | Kg/Batch |
|---|---|---|---|---|---|---|---|---|
| Marraqueta | 5 | 12 | 15 | 10 | 35 | 18 | 12 | 60 |
| Hallulla | 5 | 14 | 20 | 12 | 30 | 18 | 12 | 55 |
| Marraqueta Integral | 5 | 13 | 18 | 10 | 40 | 21 | 12 | 60 |
| Hallulla Integral | 5 | 15 | 20 | 12 | 35 | 18 | 12 | 55 |
| Pan Hot Dog | 5 | 12 | 15 | 12 | 40 | 14 | 12 | 55 |
| Ciabatta | 5 | 10 | 30 | 8 | 45 | 21 | 15 | 50 |
| Baguette | 5 | 10 | 25 | 12 | 45 | 21 | 15 | 45 |
| Dobladita | 5 | 13 | 15 | 10 | 20 | 14 | 10 | 50 |
| Bocado de Dama | 5 | 12 | 15 | 10 | 30 | 14 | 10 | 25 |
| Amasado | 5 | 15 | 20 | 10 | 35 | 18 | 12 | 60 |

---

## 3. Pool 2 — Gestión de Hornos

> **Lanes:** Manipulador de Horno · Horno · Zona de Enfriamiento

```mermaid
flowchart TD
    LOTE_IN(("◯ Lote listo<br/>para horneado"))

    subgraph DECISION_FAMILIA["📋 Política de Secuencia de Producción"]
        GW_SEQ{{"✦ Gateway Exclusivo<br/>Selección de Familia"}}
        OPT1["Prioridad: menor<br/>stock en sala"]
        OPT2["Prioridad: mayor<br/>demanda esperada"]
        OPT3["Secuencia fija<br/>F1→F2→F3"]
        OPT4["Estrategia<br/>híbrida"]
    end

    subgraph CLASIFICACION["📦 Clasificación por Familia de Horneado"]
        GW_FAM{{"✦ Gateway Exclusivo<br/>¿Familia del lote?"}}
        FAM1["Familia 1: Horneado corto<br/>⏱ 14 min<br/>Hot Dog · Dobladita · Bocado de Dama"]
        FAM2["Familia 2: Horneado medio<br/>⏱ 18 min<br/>Marraqueta · Hallulla · Hallulla Int. · Amasado"]
        FAM3["Familia 3: Horneado largo<br/>⏱ 21 min<br/>Marraqueta Int. · Ciabatta · Baguette"]
    end

    subgraph CARGA_POLICY["⚖️ Política de Carga"]
        GW_CARGA{{"✦ Gateway Exclusivo<br/>¿Carga ≥ 50%<br/>capacidad?"}}
        ESPERAR["Esperar acumulación<br/>⏱ máx 15 min"]
        GW_TIMEOUT{{"✦ Gateway Exclusivo<br/>¿Tiempo espera<br/>> 15 min?"}}
        CARGAR_PARCIAL["Iniciar corrida<br/>anticipada<br/>evitar quiebre"]
        CARGAR_COMPLETO["Proceder<br/>con carga completa"]
    end

    subgraph SETUP["🔧 Setup de Horno"]
        GW_SETUP{{"✦ Gateway Exclusivo<br/>¿Misma familia<br/>que corrida anterior?"}}
        NO_SETUP["Sin setup<br/>⏱ 0 min"]
        SI_SETUP["Setup cambio familia<br/>⏱ 5 min"]
    end

    subgraph LANE_MANIPULADOR["👷 Lane: Manipulador de Horno"]
        CARGA_HORNO["Carga del horno<br/>⏱ 5 min<br/>👤 1 manipulador"]
        DESCARGA_HORNO["Descarga del horno<br/>⏱ 5 min<br/>👤 1 manipulador"]
    end

    subgraph LANE_HORNO["🔥 Lane: Horno"]
        HORNEADO["Horneado batch<br/>⏱ 14/18/21 min<br/>🚫 Sin retiro parcial<br/>📦 Máx 6 carros × 18 bandejas"]
    end

    subgraph LANE_ENFRIAMIENTO["❄️ Lane: Zona de Enfriamiento"]
        ENFRIADO["Enfriamiento<br/>⏱ 10-15 min<br/>sin intervención"]
    end

    LOTE_IN --> GW_SEQ
    GW_SEQ --> OPT1 & OPT2 & OPT3 & OPT4
    OPT1 & OPT2 & OPT3 & OPT4 --> GW_FAM

    GW_FAM -->|"Corto"| FAM1
    GW_FAM -->|"Medio"| FAM2
    GW_FAM -->|"Largo"| FAM3

    FAM1 & FAM2 & FAM3 --> GW_CARGA

    GW_CARGA -->|"Sí ≥50%"| CARGAR_COMPLETO
    GW_CARGA -->|"No <50%"| ESPERAR
    ESPERAR --> GW_TIMEOUT
    GW_TIMEOUT -->|"Sí > 15 min"| CARGAR_PARCIAL
    GW_TIMEOUT -->|"No"| ESPERAR

    CARGAR_COMPLETO & CARGAR_PARCIAL --> GW_SETUP

    GW_SETUP -->|"Sí, misma"| NO_SETUP
    GW_SETUP -->|"No, diferente"| SI_SETUP
    NO_SETUP & SI_SETUP --> CARGA_HORNO

    CARGA_HORNO --> HORNEADO
    HORNEADO --> DESCARGA_HORNO
    DESCARGA_HORNO --> ENFRIADO
    ENFRIADO --> PAN_LISTO(("◯ Pan listo<br/>para sala"))
```

### Restricciones clave del horno

| Parámetro | Valor |
|---|---|
| Capacidad máxima por corrida | 6 carros (racks) |
| Bandejas por carro | 18 |
| No mezclar familias | ✅ Obligatorio |
| Retiro parcial | 🚫 Prohibido |
| Carga mínima recomendada | 50% (600 kg) |
| Espera máxima pre-corrida | 15 min |
| Setup cambio de familia | 5 min |
| Carga/Descarga | 5 min c/u (1 manipulador) |

---

## 4. Pool 3 — Sala de Ventas y Demanda de Clientes

> **Lanes:** Manipulador/Ayudante de Despacho · Inventario Sala · Cliente

```mermaid
flowchart TD
    PAN_IN(("◯ Pan listo<br/>para sala"))

    subgraph LANE_AYUDANTE["👷 Lane: Ayudante de Despacho"]
        REPOSICION["Reposición a sala<br/>traslado por ayudante"]
    end

    subgraph LANE_INVENTARIO["📊 Lane: Inventario por Tipo de Pan"]
        INV_UPDATE["Actualizar inventario<br/>+Kg por tipo de pan"]
        INV_STATE["Estado del inventario<br/>10 SKUs independientes"]
    end

    subgraph LANE_CLIENTE["🛒 Lane: Cliente"]
        LLEGADA(("⬤ Llegada<br/>de cliente"))
        GW_TIPOS{{"✦ Gateway Exclusivo<br/>¿Cuántos tipos compra?"}}
        T1["1 tipo de pan<br/>P = 50%"]
        T2["2 tipos de pan<br/>P = 35%"]
        T3["3 tipos de pan<br/>P = 15%"]

        GW_MERGE(("○"))

        SELECCION["Selección de tipo de pan<br/>según probabilidad horaria"]

        CANTIDAD["Determinar cantidad<br/>Triangular: 0.3 - moda - máx kg<br/>según tipo"]

        GW_STOCK{{"✦ Gateway Exclusivo<br/>¿Hay stock del<br/>tipo seleccionado?"}}

        VENTA["Venta realizada<br/>Descontar Kg del inventario"]
        QUIEBRE["🚨 Quiebre de Stock<br/>Venta perdida<br/>Registrar demanda insatisfecha"]

        GW_MAS{{"✦ Gateway Exclusivo<br/>¿Compra más<br/>tipos de pan?"}}
        FIN_CLIENTE(("⬤ Fin<br/>cliente"))
    end

    PAN_IN --> REPOSICION
    REPOSICION --> INV_UPDATE
    INV_UPDATE --> INV_STATE

    LLEGADA --> GW_TIPOS
    GW_TIPOS -->|"50%"| T1
    GW_TIPOS -->|"35%"| T2
    GW_TIPOS -->|"15%"| T3
    T1 & T2 & T3 --> GW_MERGE
    GW_MERGE --> SELECCION
    SELECCION --> CANTIDAD
    CANTIDAD --> GW_STOCK

    GW_STOCK -->|"Sí"| VENTA
    GW_STOCK -->|"No, stock = 0"| QUIEBRE

    VENTA --> GW_MAS
    QUIEBRE --> GW_MAS

    GW_MAS -->|"Sí"| SELECCION
    GW_MAS -->|"No"| FIN_CLIENTE
```

---

## 5. Proceso Transversal — Gestión de Turnos de Trabajo

```mermaid
flowchart LR
    subgraph TURNOS["⏰ Gestión de Turnos (aplica a todos los recursos humanos)"]
        INICIO_TURNO(("⬤ Inicio<br/>turno"))
        TRABAJO["Trabajo efectivo<br/>⏱ 8 hrs"]
        
        GW_COLACION{{"✦ ¿Hora de<br/>colación?"}}
        COLACION["Colación<br/>⏱ 45 min"]
        
        GW_DESCANSO{{"✦ ¿Hora de<br/>descanso?"}}
        DESCANSO["Descanso<br/>⏱ 15 min × 2"]
        
        GW_COBERTURA{{"✦ Gateway Paralelo<br/>¿Al menos 1 persona<br/>por función presente?"}}
        ESCALONAR["Escalonar salidas<br/>para mantener cobertura"]
        
        FIN_TURNO(("⬤ Fin<br/>turno"))
    end

    INICIO_TURNO --> TRABAJO
    TRABAJO --> GW_COLACION
    GW_COLACION -->|"Sí"| COLACION
    GW_COLACION -->|"No"| GW_DESCANSO
    COLACION --> GW_COBERTURA
    GW_DESCANSO -->|"Sí"| DESCANSO
    GW_DESCANSO -->|"No"| TRABAJO
    DESCANSO --> GW_COBERTURA
    GW_COBERTURA -->|"Cumple"| TRABAJO
    GW_COBERTURA -->|"No cumple"| ESCALONAR
    ESCALONAR --> TRABAJO
    TRABAJO -->|"8 hrs cumplidas"| FIN_TURNO
```

---

## 6. Diagrama Integrado End-to-End (Flujo Principal)

```mermaid
flowchart TD
    START(("⬤ INICIO<br/>Pre-apertura<br/>antes 09:00"))

    %% Producción
    PLAN["Planificación de<br/>secuencia de producción<br/>según política"]
    PESADO["1. Pesado y<br/>dosificación<br/>👤 Panadero · ⏱ 5 min"]
    MEZCLA_CARGA["2a. Carga ingredientes<br/>👤 Panadero · ⏱ 2 min"]
    MEZCLA_AUTO["2b. Mezclado automático<br/>⚙️ Mezcladora"]
    MEZCLA_RETIRO["2c. Retiro de masa<br/>👤 Panadero · ⏱ 1 min"]
    AMASADO["3. Amasado<br/>👤 Panadero · ⚙️ Amasadora<br/>⏱ 10-15 min"]
    REPOSO["4. Reposo / Fermentación<br/>🧪 Cámara · ⏱ 15-30 min"]
    FORMADO["5. Dividido y Formado<br/>👤 Panadero · ⏱ 8-12 min"]
    FERM_FINAL["6. Fermentación final<br/>🧪 Cámara · ⏱ 20-45 min"]

    %% Decisión Familia
    GW_F{{"✦ Clasificar<br/>familia de horneado"}}
    F1["Familia 1<br/>⏱ 14 min"]
    F2["Familia 2<br/>⏱ 18 min"]
    F3["Familia 3<br/>⏱ 21 min"]
    MERGE_F(("○"))

    %% Carga
    GW_C{{"✦ ¿Carga ≥ 50%?"}}
    WAIT["Esperar<br/>máx 15 min"]
    GW_T{{"✦ ¿Timeout?"}}

    %% Setup
    GW_S{{"✦ ¿Cambio<br/>de familia?"}}
    SETUP["Setup ⏱ 5 min"]

    %% Horno
    CARGA["Carga horno<br/>👷 Manipulador · ⏱ 5 min"]
    HORN["Horneado batch<br/>🔥 ⏱ 14/18/21 min"]
    DESC["Descarga horno<br/>👷 Manipulador · ⏱ 5 min"]
    ENFR["Enfriamiento<br/>❄️ ⏱ 10-15 min"]

    %% Sala
    REPO["Reposición a sala<br/>👷 Ayudante"]
    INV["Inventario sala<br/>+Kg por tipo"]

    %% Cliente
    CLI(("⬤ Llegada<br/>cliente"))
    SEL["Selección tipo pan<br/>según prob. horaria"]
    GW_STK{{"✦ ¿Stock > 0?"}}
    VENTA["✅ Venta"]
    QUIEBRE["🚨 Quiebre"]
    FIN(("⬤ FIN"))

    %% Conexiones principales
    START --> PLAN --> PESADO --> MEZCLA_CARGA --> MEZCLA_AUTO --> MEZCLA_RETIRO --> AMASADO --> REPOSO --> FORMADO --> FERM_FINAL

    FERM_FINAL --> GW_F
    GW_F -->|"Corto"| F1
    GW_F -->|"Medio"| F2
    GW_F -->|"Largo"| F3
    F1 & F2 & F3 --> MERGE_F

    MERGE_F --> GW_C
    GW_C -->|"Sí"| GW_S
    GW_C -->|"No"| WAIT --> GW_T
    GW_T -->|"Sí"| GW_S
    GW_T -->|"No"| WAIT

    GW_S -->|"Sí"| SETUP --> CARGA
    GW_S -->|"No"| CARGA

    CARGA --> HORN --> DESC --> ENFR --> REPO --> INV

    CLI --> SEL --> GW_STK
    GW_STK -->|"Sí"| VENTA --> FIN
    GW_STK -->|"No"| QUIEBRE --> FIN

    %% Retroalimentación
    INV -.->|"Señal stock bajo"| PLAN
```

---

## 7. Leyenda BPMN 2.0

| Símbolo | Significado BPMN |
|---|---|
| `(("⬤"))` | **Evento de inicio / fin** (Start / End Event) |
| `["..."]` | **Tarea** (Task / Activity) |
| `{{"✦ ..."}}` | **Gateway Exclusivo** (Exclusive Gateway — XOR) |
| `(("○"))` | **Gateway Paralelo / Merge** |
| `-->` | **Flujo de secuencia** (Sequence Flow) |
| `-.->` | **Flujo de mensaje** (Message Flow entre pools) |
| 👤 / 👷 | Recurso humano requerido (Panadero / Manipulador) |
| ⚙️ | Recurso de máquina requerido |
| 🧪 | Recurso de fermentación / cámara |
| ⏱ | Tiempo de la actividad |

---

## 8. Entidades del Modelo de Simulación

| Entidad | Descripción | Atributos clave |
|---|---|---|
| **Lote de Pan** | Entidad principal que fluye por producción | Tipo, familia, kg, etapa actual |
| **Cliente** | Entidad que consume inventario | Nº tipos a comprar, tipos seleccionados, kg por tipo |
| **Corrida de Horno** | Agrupación de lotes de misma familia | Familia, nº carros, kg total, tiempo cocción |

## 9. Recursos del Modelo

| Recurso | Tipo | Usado en etapas |
|---|---|---|
| Panadero | Humano (turno 8h) | Pesado, carga/retiro mezcladora, amasado, formado |
| Manipulador/Ayudante | Humano (turno 8h) | Carga/descarga horno, reposición a sala |
| Mezcladora | Máquina | Mezclado |
| Amasadora | Máquina | Amasado |
| Mesa de Formado | Estación | Dividido y formado |
| Cámara Fermentación | Espacio | Reposo, fermentación final |
| Horno | Máquina (batch) | Horneado |
| Carros/Bandejas | Transporte | Horneado, enfriamiento, traslado |
