# Reporte Pre-Modelación: Panadería de Supermercado — Simulación DES

> **Proyecto Capstone — Simulación en SIMIO**
> Universidad del Desarrollo · Mayo 2026

---

## 1. Definición del Problema y Propósito del Estudio

### 1.1 Problema

Un supermercado opera una panadería propia que abastece una zona de autoservicio con 10 tipos de pan fresco. La jefatura ha detectado un **alto nivel de quiebre de stock** que genera quejas de clientes y pérdida de ventas (sin sustitución entre tipos).

### 1.2 Preguntas centrales

1. ¿Cuántos **panaderos** y **manipuladores/ayudantes** se requieren, y en qué turnos?
2. ¿Cuántos **hornos** son necesarios?
3. ¿Cuántas **mezcladoras** y **amasadoras** se requieren?
4. ¿En qué **horario** debe operar la panadería?
5. ¿Cuál es la **secuencia de producción** que minimiza quiebres de stock?
6. ¿Cuál es la **combinación de recursos** de menor costo que logre un nivel de servicio aceptable?

### 1.3 Criterio principal de evaluación

**Minimizar quiebres de stock** (kg de demanda insatisfecha) sujeto a un uso razonable de recursos. Métricas complementarias:

| Indicador                | Definición                                  |
| ------------------------ | -------------------------------------------- |
| Nivel de servicio (%)    | kg vendidos / kg demandados × 100, por tipo |
| Quiebres por tipo        | kg no vendidos por falta de stock            |
| Sobrantes al cierre      | kg producidos no vendidos al cierre (21:00)  |
| Utilización de recursos | % tiempo efectivo / tiempo disponible        |

---

## 2. Delimitación del Sistema

### 2.1 Dentro del modelo

| Subsistema                 | Elementos incluidos                                                                                                                            |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Producción**      | 10 tipos de pan, etapas secuenciales (pesado → mezclado → amasado → reposo → formado → fermentación → horneado → enfriado → traslado) |
| **Recursos humanos** | Panaderos y manipuladores/ayudantes con turnos de 8h, colación (45 min) y 2 descansos (15 min c/u) escalonados                                |
| **Maquinaria**       | Mezcladoras, amasadoras, mesas de formado, hornos industriales batch                                                                           |
| **Infraestructura**  | Cámaras de fermentación, zona de enfriamiento, carros y bandejas                                                                             |
| **Inventario sala**  | Stock por tipo de pan, reposición desde producción                                                                                           |
| **Demanda**          | Clientes con llegada no uniforme, compra de 1-3 tipos, cantidad triangular por tipo                                                            |
| **Hornos**           | Operación batch por familias de horneado (14/18/21 min), setup, carga/descarga                                                                |

### 2.2 Fuera del modelo

| Excluido | Justificación |
|---|---|
| Compra de materias primas | Se asume disponibilidad ilimitada de ingredientes |
| Transporte externo | No afecta operación interna |
| Fallas de equipo | Supuesto operacional del enunciado |
| Mantenimiento mayor | Fuera del horizonte diario |
| Ventas de otros productos | No interactúan con la panadería |
| Deterioro por sobreproducción | Supuesto: no hay deterioro dentro del día |

---

## 3. Levantamiento y Organización de la Información

### 3.1 Tipos de pan y familias de horneado

| #  | Tipo de Pan         | Familia   | Tiempo Horneado | Familia Proceso                    |
| -- | ------------------- | --------- | --------------- | ---------------------------------- |
| 1  | Marraqueta          | Familia 2 | 18 min          | Directo                            |
| 2  | Hallulla            | Familia 2 | 18 min          | Directo con materia grasa          |
| 3  | Marraqueta Integral | Familia 3 | 21 min          | Directo integral                   |
| 4  | Hallulla Integral   | Familia 2 | 18 min          | Directo integral con materia grasa |
| 5  | Pan Hot Dog         | Familia 1 | 14 min          | Enriquecido                        |
| 6  | Ciabatta            | Familia 3 | 21 min          | Alta hidratación                  |
| 7  | Baguette            | Familia 3 | 21 min          | Francés/artesanal                 |
| 8  | Dobladita           | Familia 1 | 14 min          | Masa grasa laminada simple         |
| 9  | Bocado de Dama      | Familia 1 | 14 min          | Pan pequeño enriquecido           |
| 10 | Amasado             | Familia 2 | 18 min          | Tradicional chileno                |

### 3.2 Tiempos de proceso por etapa (minutos)

> **Nota**: La Etapa 2 del CSV ("Amasado") corresponde al **ciclo automático de mezclado**. Adicionalmente, el panadero emplea 2 min para cargar la mezcladora y 1 min para retirar la masa (overhead).

| Tipo                | Pesado | Mezclado (auto) | Reposo | Formado | Ferm. Final | Horneado | Enfriado+Trasl. | **Ciclo total** | Kg/Batch |
| ------------------- | ------ | --------------- | ------ | ------- | ----------- | -------- | --------------- | --------------------- | -------- |
| Marraqueta          | 5      | 12              | 15     | 10      | 35          | 18       | 12              | 107                   | 60       |
| Hallulla            | 5      | 14              | 20     | 12      | 30          | 18       | 12              | 111                   | 55       |
| Marraqueta Integral | 5      | 13              | 18     | 10      | 40          | 21       | 12              | 119                   | 60       |
| Hallulla Integral   | 5      | 15              | 20     | 12      | 35          | 18       | 12              | 117                   | 55       |
| Pan Hot Dog         | 5      | 12              | 15     | 12      | 40          | 14       | 12              | 110                   | 55       |
| Ciabatta            | 5      | 10              | 30     | 8       | 45          | 21       | 15              | 134                   | 50       |
| Baguette            | 5      | 10              | 25     | 12      | 45          | 21       | 15              | 133                   | 45       |
| Dobladita           | 5      | 13              | 15     | 10      | 20          | 14       | 10              | 87                    | 50       |
| Bocado de Dama      | 5      | 12              | 15     | 10      | 30          | 14       | 10              | 96                    | 25       |
| Amasado             | 5      | 15              | 20     | 10      | 35          | 18       | 12              | 115                   | 60       |

#### Derivación de §3.2 — Ciclo total y Kg/Batch

> **Fuente**: `parametros_proceso_panaderia.csv`, columnas `Min1`…`Min7` y `KgPorBatchRef`.

**Kg/Batch**: Se toma directamente de la columna `KgPorBatchRef` del CSV. Ejemplo: Marraqueta → `KgPorBatchRef = 60`.

**Ciclo total**: Suma aritmética de los 7 tiempos de etapa del CSV. Ejemplo para Marraqueta:

$$
\text{Ciclo}_{\text{Marraqueta}} = \underbrace{5}_{\text{Pesado}} + \underbrace{12}_{\text{Mezclado}} + \underbrace{15}_{\text{Reposo}} + \underbrace{10}_{\text{Formado}} + \underbrace{35}_{\text{Ferm.}} + \underbrace{18}_{\text{Horneado}} + \underbrace{12}_{\text{Enfr.+Trasl.}} = 107 \text{ min}
$$

**Nota sobre la Etapa 2 ("Amasado" en el CSV)**: El enunciado (Sección II.A) especifica que "el panadero ingresa los ingredientes (2 min), luego la máquina opera en ciclo automático (que es el tiempo indicado [en el CSV]), luego el panadero retira la masa (1 min)". Por tanto, el valor `Min2` del CSV corresponde al **ciclo automático de mezclado** (🔶 S1). Los 2+1 = 3 min de overhead manual se modelan como etapas separadas (carga/retiro) que requieren al panadero.

**Kg/Bandeja**: Se calcula como `CapacidadKgPorCarroRef / 18` (18 bandejas por carro según el enunciado §III.D). Ejemplo: Marraqueta → `40 / 18 = 2,22 kg/bandeja`.

---

### 3.3 Demanda diaria por tipo

| Tipo                | Demanda (kg/día) | % del total    |
| ------------------- | ----------------- | -------------- |
| Marraqueta          | 2.000             | 24,4%          |
| Hallulla            | 1.700             | 20,7%          |
| Pan Hot Dog         | 1.200             | 14,6%          |
| Marraqueta Integral | 800               | 9,8%           |
| Hallulla Integral   | 800               | 9,8%           |
| Ciabatta            | 400               | 4,9%           |
| Amasado             | 380               | 4,6%           |
| Dobladita           | 350               | 4,3%           |
| Baguette            | 350               | 4,3%           |
| Bocado de Dama      | 220               | 2,7%           |
| **TOTAL**     | **8.200**   | **100%** |

#### Derivación de §3.3 — Demanda y porcentajes

> **Fuente**: Los valores de demanda diaria (kg/día) provienen directamente del enunciado del problema (Sección E.1 de `base_information.md`).

**Porcentaje del total**: Se calcula como `Demanda_tipo / 8.200 × 100`. Ejemplo:

$$
\%_{\text{Marraqueta}} = \frac{2.000}{8.200} \times 100 = 24{,}4\%
$$

### 3.4 Perfil de demanda horaria (kg/hora)

| Franja       | Total kg | % diario | Régimen       |
| ------------ | -------- | -------- | -------------- |
| 09:00–10:00 | 448,8    | 5,5%     | Bajo           |
| 10:00–11:00 | 448,8    | 5,5%     | Bajo           |
| 11:00–12:00 | 448,8    | 5,5%     | Bajo           |
| 12:00–13:00 | 750,2    | 9,1%     | Medio          |
| 13:00–14:00 | 689,4    | 8,4%     | Medio          |
| 14:00–15:00 | 689,4    | 8,4%     | Medio          |
| 15:00–16:00 | 448,8    | 5,5%     | Bajo           |
| 16:00–17:00 | 448,8    | 5,5%     | Bajo           |
| 17:00–18:00 | 499,5    | 6,1%     | Medio          |
| 18:00–19:00 | 1.451,3  | 17,7%    | **Alto** |
| 19:00–20:00 | 1.416,6  | 17,3%    | **Alto** |
| 20:00–21:00 | 459,9    | 5,6%     | Bajo           |

**Observación**: La demanda presenta **tres regímenes claramente diferenciados**:

- **Bajo** (~450 kg/hr): mañana, tarde temprana y cierre → 6 horas
- **Medio** (~657 kg/hr): mediodía y pre-peak → 4 horas
- **Alto** (~1.434 kg/hr): peak vespertino 18:00–20:00 → 2 horas (**35% de la demanda diaria en 2 horas**)

#### Derivación de §3.4 — Perfil de demanda horaria

> **Fuente**: `perfil_demanda_por_hora_panaderia.csv` — cada fila tiene la demanda en kg por tipo para una franja horaria.

**Total kg por franja**: Suma de las 10 columnas de tipo de pan en cada fila del CSV. Ejemplo para 09:00–10:00:

$$
\text{Total}_{09\text{-}10} = 126{,}19 + 107{,}26 + 50{,}48 + 50{,}48 + 26{,}06 + 15{,}13 + 13{,}24 + 29{,}17 + 18{,}33 + 12{,}43 = 448{,}8 \text{ kg}
$$

**% diario**: Se calcula como `Total_franja / 8.200 × 100`. Ejemplo: `448,8 / 8.200 = 5,5%`.

**Clasificación de régimen**: Se agruparon las franjas por nivel de intensidad:
- **Bajo**: franjas con ~449 kg/hr (09–12, 15–17, 20–21)
- **Medio**: franjas con ~500–750 kg/hr (12–15, 17–18)
- **Alto**: franjas con >1.400 kg/hr (18–20)

> **Validación**: Σ de todas las franjas = 8.200 kg ✓ (coincide con la demanda diaria total del enunciado).

### 3.5 Lotes de producción requeridos por día

| Tipo                | Demanda kg      | Kg/Batch | Batches/día  |
| ------------------- | --------------- | -------- | ------------- |
| Marraqueta          | 2.000           | 60       | 34            |
| Hallulla            | 1.700           | 55       | 31            |
| Pan Hot Dog         | 1.200           | 55       | 22            |
| Hallulla Integral   | 800             | 55       | 15            |
| Marraqueta Integral | 800             | 60       | 14            |
| Bocado de Dama      | 220             | 25       | 9             |
| Ciabatta            | 400             | 50       | 8             |
| Baguette            | 350             | 45       | 8             |
| Dobladita           | 350             | 50       | 7             |
| Amasado             | 380             | 60       | 7             |
| **TOTAL**     | **8.200** | —       | **155** |

#### Derivación de §3.5 — Lotes de producción

> **Fuente**: `Demanda` del enunciado (§E.1) y `KgPorBatchRef` de `parametros_proceso_panaderia.csv`.

**Fórmula**: Cada tipo requiere `⌈Demanda / Kg_por_Batch⌉` batches (redondeo al entero superior).

$$
\text{Batches}_{\text{Marraqueta}} = \left\lceil \frac{2.000}{60} \right\rceil = \lceil 33{,}3 \rceil = 34
$$

$$
\text{Batches}_{\text{Hallulla}} = \left\lceil \frac{1.700}{55} \right\rceil = \lceil 30{,}9 \rceil = 31
$$

$$
\text{Batches}_{\text{Bocado de Dama}} = \left\lceil \frac{220}{25} \right\rceil = \lceil 8{,}8 \rceil = 9
$$

Se redondea al entero superior porque no se pueden producir fracciones de batch.

### 3.6 Corridas de horno por familia (capacidad 1.200 kg/corrida)

| Familia         | Tipos incluidos                              | Kg totales      | Corridas mín. | Tiempo hornear | Tiempo total/corrida* |
| --------------- | -------------------------------------------- | --------------- | -------------- | -------------- | --------------------- |
| Fam. 1 (corto)  | Hot Dog, Dobladita, Bocado de Dama           | 1.770           | 2              | 14 min         | 24 min                |
| Fam. 2 (medio)  | Marraqueta, Hallulla, Hallulla Int., Amasado | 4.880           | 5              | 18 min         | 28 min                |
| Fam. 3 (largo)  | Marraqueta Int., Ciabatta, Baguette          | 1.550           | 2              | 21 min         | 31 min                |
| **TOTAL** |                                              | **8.200** | **9**    |                |                       |

*Tiempo total/corrida = carga (5 min) + horneado + descarga (5 min), sin setup.

#### Derivación de §3.6 — Corridas de horno

> **Fuente**: Familias de horneado del enunciado (§III.B), demanda (§E.1) y capacidad del horno (§III.D: 1.200 kg/corrida).

**Paso 1 — Kg totales por familia**: Suma de la demanda diaria de todos los tipos de cada familia:

$$
\text{Fam 1} = \underbrace{1.200}_{\text{Hot Dog}} + \underbrace{350}_{\text{Dobladita}} + \underbrace{220}_{\text{Bocado}} = 1.770 \text{ kg}
$$

$$
\text{Fam 2} = \underbrace{2.000}_{\text{Marraq.}} + \underbrace{1.700}_{\text{Hallulla}} + \underbrace{800}_{\text{Hall. Int.}} + \underbrace{380}_{\text{Amasado}} = 4.880 \text{ kg}
$$

$$
\text{Fam 3} = \underbrace{800}_{\text{Marraq. Int.}} + \underbrace{400}_{\text{Ciabatta}} + \underbrace{350}_{\text{Baguette}} = 1.550 \text{ kg}
$$

**Paso 2 — Corridas mínimas**: `⌈Kg_familia / 1.200⌉`.

$$
\text{Corridas Fam 2} = \left\lceil \frac{4.880}{1.200} \right\rceil = \lceil 4{,}07 \rceil = 5
$$

**Paso 3 — Tiempo total/corrida**: `Carga (5 min) + Horneado (14/18/21 min) + Descarga (5 min)`. Tiempos de carga/descarga vienen del enunciado §III.E.

### 3.7 Carros y bandejas por batch de producción

| Tipo                | Kg/Batch | Kg/Carro | Kg/Bandeja | Bandejas/Batch | Carros/Batch |
| ------------------- | -------- | -------- | ---------- | -------------- | ------------ |
| Marraqueta          | 60       | 40       | 2,22       | 27             | 2            |
| Hallulla            | 55       | 45       | 2,50       | 22             | 2            |
| Marraqueta Integral | 60       | 38       | 2,11       | 29             | 2            |
| Hallulla Integral   | 55       | 42       | 2,33       | 24             | 2            |
| Pan Hot Dog         | 55       | 35       | 1,94       | 29             | 2            |
| Ciabatta            | 50       | 35       | 1,94       | 26             | 2            |
| Baguette            | 45       | 32       | 1,78       | 26             | 2            |
| Dobladita           | 50       | 45       | 2,50       | 20             | 2            |
| Bocado de Dama      | 25       | 28       | 1,56       | 17             | 1            |
| Amasado             | 60       | 40       | 2,22       | 27             | 2            |

#### Derivación de §3.7 — Carros y bandejas

> **Fuente**: `parametros_proceso_panaderia.csv`, columna `CapacidadKgPorCarroRef`, y enunciado §III.D (18 bandejas por carro).

**Kg/Carro**: Tomado directamente de `CapacidadKgPorCarroRef` en el CSV. Ejemplo: Marraqueta → 40 kg/carro.

**Kg/Bandeja**: Cada carro tiene 18 bandejas (enunciado §III.D), por tanto:

$$
\text{Kg/Bandeja}_{\text{Marraqueta}} = \frac{\text{CapacidadKgPorCarroRef}}{18} = \frac{40}{18} = 2{,}22 \text{ kg}
$$

**Bandejas/Batch**: `⌈Kg_Batch / Kg_Bandeja⌉`. Ejemplo:

$$
\text{Bandejas}_{\text{Marraqueta}} = \left\lceil \frac{60}{2{,}22} \right\rceil = \lceil 27{,}0 \rceil = 27
$$

**Carros/Batch**: `⌈Kg_Batch / Kg_Carro⌉`. Ejemplo:

$$
\text{Carros}_{\text{Marraqueta}} = \left\lceil \frac{60}{40} \right\rceil = \lceil 1{,}5 \rceil = 2
$$

### 3.8 Distribuciones de compra por cliente

**Número de tipos por compra:**

| Tipos              | Probabilidad   |
| ------------------ | -------------- |
| 1 tipo             | 50%            |
| 2 tipos            | 35%            |
| 3 tipos            | 15%            |
| **E[tipos]** | **1,65** |

**Cantidad comprada por tipo — Distribución Triangular:**

| Tipo                | Mín (kg) | Moda (kg) | Máx (kg) | E[X] (kg) |
| ------------------- | --------- | --------- | --------- | --------- |
| Marraqueta          | 0,3       | 1,0       | 2,0       | 1,100     |
| Hallulla            | 0,3       | 1,0       | 2,0       | 1,100     |
| Marraqueta Integral | 0,3       | 0,5       | 2,0       | 0,933     |
| Hallulla Integral   | 0,3       | 0,7       | 1,5       | 0,833     |
| Pan Hot Dog         | 0,3       | 1,0       | 3,0       | 1,433     |
| Ciabatta            | 0,3       | 0,5       | 1,5       | 0,767     |
| Baguette            | 0,3       | 0,5       | 1,0       | 0,600     |
| Dobladita           | 0,3       | 0,5       | 1,5       | 0,767     |
| Bocado de Dama      | 0,3       | 0,5       | 1,0       | 0,600     |
| Amasado             | 0,3       | 0,8       | 2,0       | 1,033     |

#### Derivación de §3.8 — Distribuciones de compra

> **Fuente**: Enunciado §E.2 de `base_information.md`.

**Número de tipos**: Las probabilidades (50%, 35%, 15%) vienen directamente del enunciado. El valor esperado se calcula como:

$$
E[\text{tipos}] = 1 \times 0{,}50 + 2 \times 0{,}35 + 3 \times 0{,}15 = 0{,}50 + 0{,}70 + 0{,}45 = 1{,}65
$$

**Parámetros triangulares**: Mín, Moda y Máx se toman del enunciado §E.2. Por defecto `Mín = 0,3 kg` y `Máx = 2,0 kg`, salvo excepciones indicadas en el enunciado (Hot Dog máx 3 kg; Hallulla Integral, Ciabatta y Dobladita máx 1,5 kg; Baguette y Bocado de Dama máx 1 kg).

**E[X] — Media de la distribución triangular**: Se calcula con la fórmula estándar:

$$
E[X] = \frac{\text{mín} + \text{moda} + \text{máx}}{3}
$$

Ejemplo para Marraqueta:

$$
E[X]_{\text{Marraqueta}} = \frac{0{,}3 + 1{,}0 + 2{,}0}{3} = \frac{3{,}3}{3} = 1{,}100 \text{ kg}
$$

Ejemplo para Pan Hot Dog (con máx = 3,0 kg):

$$
E[X]_{\text{Hot Dog}} = \frac{0{,}3 + 1{,}0 + 3{,}0}{3} = \frac{4{,}3}{3} = 1{,}433 \text{ kg}
$$

### 3.9 Probabilidades de elección (primera selección) por hora

Extraídas de `probabilidades_eleccion_por_hora.csv`. Suman ~1,0 en cada franja. Ejemplo para horas representativas:

| Tipo            | 09–12 (Bajo) | 12–13 (Medio) | 18–19 (Alto) |
| --------------- | ------------- | -------------- | ------------- |
| Marraqueta      | 0,2645        | 0,2313         | 0,1854        |
| Hallulla        | 0,2248        | 0,1966         | 0,1576        |
| Marraqueta Int. | 0,1247        | 0,1090         | 0,0874        |
| Hallulla Int.   | 0,1164        | 0,1018         | 0,0816        |
| Pan Hot Dog     | 0,0546        | 0,1534         | 0,2501        |
| Ciabatta        | 0,0374        | 0,0525         | 0,0708        |
| Baguette        | 0,0327        | 0,0459         | 0,0619        |
| Dobladita       | 0,0720        | 0,0434         | 0,0225        |
| Bocado de Dama  | 0,0453        | 0,0273         | 0,0141        |
| Amasado         | 0,0277        | 0,0390         | 0,0687        |

**Observación clave**: El Pan Hot Dog pasa de 5,5% de probabilidad en horario bajo a **25%** en peak vespertino.

#### Derivación de §3.9 — Probabilidades de elección

> **Fuente**: `probabilidades_eleccion_por_hora.csv` — datos provistos directamente en el enunciado del problema.

Estas probabilidades fueron **proporcionadas como dato de entrada** (enunciado §E.2: *"El archivo probabilidades_eleccion_por_hora.xlsx indica por cada hora la probabilidad de elección del primer tipo de pan que el cliente escoge"*). No son calculadas por el modelador.

Se verificó que suman ~1,0 por franja (error < 0,00002 por redondeo).

### 3.10 Probabilidades condicionales (2ª y 3ª selección)

Cuando un cliente compra 2 o 3 tipos **diferentes**, la selección del 2º tipo (y 3º) se realiza sin reemplazo:

$$
P(\text{2º} = j \mid \text{1º} = i) = \frac{P_j}{1 - P_i}, \quad j \neq i
$$

$$
P(\text{3º} = k \mid \text{1º} = i, \text{2º} = j) = \frac{P_k}{1 - P_i - P_j}, \quad k \neq i,j
$$

**Ejemplo (09:00–10:00)** — P(2º tipo | 1º = Marraqueta):

| 2º tipo        | P condicional |
| --------------- | ------------- |
| Hallulla        | 0,3056        |
| Marraqueta Int. | 0,1695        |
| Hallulla Int.   | 0,1582        |
| Dobladita       | 0,0979        |
| Pan Hot Dog     | 0,0742        |
| Bocado de Dama  | 0,0616        |
| Ciabatta        | 0,0508        |
| Baguette        | 0,0445        |
| Amasado         | 0,0377        |

#### Derivación de §3.10 — Probabilidades condicionales

> **Fuente**: Derivación propia del modelador a partir de `probabilidades_eleccion_por_hora.csv` y el enunciado §E.2.

El enunciado indica que el cliente escoge un 2º o 3er tipo *"diferentes a los ya escogidos, siguiendo las mismas proporciones de probabilidad de decisión"*. Esto implica una **selección sin reemplazo**, donde se redistribuye la probabilidad del tipo ya elegido entre los restantes.

**Fórmula**: Si el 1er tipo elegido fue $i$ con probabilidad $P_i$, la probabilidad de elegir $j \neq i$ como 2º tipo es:

$$
P(\text{2º} = j \mid \text{1º} = i) = \frac{P_j}{1 - P_i}
$$

**Ejemplo numérico** (09:00, 1º = Marraqueta con $P_{\text{Marraq}} = 0{,}2645$):

$$
P(\text{2º} = \text{Hallulla}) = \frac{0{,}2248}{1 - 0{,}2645} = \frac{0{,}2248}{0{,}7355} = 0{,}3056 \checkmark
$$

$$
P(\text{2º} = \text{Marraq. Int.}) = \frac{0{,}1247}{0{,}7355} = 0{,}1695 \checkmark
$$

Para el 3er tipo, se excluyen los dos ya elegidos:

$$
P(\text{3º} = k \mid \text{1º}=i, \text{2º}=j) = \frac{P_k}{1 - P_i - P_j}, \quad k \neq i,j
$$

### 3.11 Distribución empírica de llegada de clientes

> **Enfoque metodológico**: La demanda de clientes se modela mediante una **distribución empírica** (tabla de frecuencias) construida directamente a partir de los datos observados del perfil de demanda horaria. A diferencia de un ajuste paramétrico (e.g., Poisson), la distribución empírica **no impone supuestos sobre la forma funcional** del proceso de llegada, preservando fielmente el patrón real observado.
>
> **Ref. Simio Workbook §23.4**: "Empirical distributions in SIMIO allow the modeler to directly use observed data when no theoretical distribution provides an adequate fit."

#### Tabla de frecuencias empíricas de llegada

La siguiente tabla constituye la **distribución empírica discreta** del número de clientes por franja horaria. Las frecuencias absolutas (`fᵢ`) se derivan de la demanda en kg y el consumo promedio por cliente. La frecuencia relativa (`fᵢ/N`) representa la probabilidad de que un cliente llegue en esa franja.

| Franja horaria | Clientes estimados (`fᵢ`) | Frecuencia relativa (`fᵢ/N`) | Frecuencia acumulada (`Fᵢ`) | Régimen   |
| -------------- | -------------------------- | ----------------------------- | ----------------------------- | --------- |
| 09:00–10:00   | 275                        | 0,0567                        | 0,0567                        | Bajo      |
| 10:00–11:00   | 275                        | 0,0567                        | 0,1134                        | Bajo      |
| 11:00–12:00   | 275                        | 0,0567                        | 0,1700                        | Bajo      |
| 12:00–13:00   | 439                        | 0,0905                        | 0,2605                        | Medio     |
| 13:00–14:00   | 417                        | 0,0859                        | 0,3464                        | Medio     |
| 14:00–15:00   | 417                        | 0,0859                        | 0,4324                        | Medio     |
| 15:00–16:00   | 275                        | 0,0567                        | 0,4890                        | Bajo      |
| 16:00–17:00   | 275                        | 0,0567                        | 0,5457                        | Bajo      |
| 17:00–18:00   | 299                        | 0,0616                        | 0,6073                        | Medio     |
| 18:00–19:00   | 819                        | 0,1688                        | 0,7761                        | **Alto** |
| 19:00–20:00   | 806                        | 0,1661                        | 0,9422                        | **Alto** |
| 20:00–21:00   | 279                        | 0,0575                        | 0,9997                        | Bajo      |
| **Total (N)** | **4.851**                  | **≈1,0000**                  |                               |           |

#### Implementación en SIMIO — Rate Table con tasas empíricas

La distribución empírica se implementa en SIMIO mediante un **Rate Table**, donde cada intervalo horario recibe directamente la tasa de llegada observada (clientes/hora). SIMIO internamente genera los tiempos entre llegadas como un proceso de Poisson no homogéneo (NHPP) cuya tasa λ(t) varía según la tabla:

| Intervalo | Rate (clientes/hr) | Interarribo medio (seg) |
| --------- | ------------------- | ----------------------- |
| 1         | 275                 | 13,1                    |
| 2         | 275                 | 13,1                    |
| 3         | 275                 | 13,1                    |
| 4         | 439                 | 8,2                     |
| 5         | 417                 | 8,6                     |
| 6         | 417                 | 8,6                     |
| 7         | 275                 | 13,1                    |
| 8         | 275                 | 13,1                    |
| 9         | 299                 | 12,0                    |
| 10        | 819                 | 4,4                     |
| 11        | 806                 | 4,5                     |
| 12        | 279                 | 12,9                    |

> **Justificación del enfoque empírico**: La demanda observada presenta un patrón **trimodal** (bajo-medio-alto) que no se ajusta adecuadamente a ninguna distribución paramétrica estándar. El uso de tasas empíricas directas evita errores de especificación y garantiza que la simulación reproduce fielmente el perfil de carga operativa real.

#### Derivación de §3.11 — Cálculo de clientes por hora (paso a paso)

> **Fuentes**: `perfil_demanda_por_hora_panaderia.csv` (kg/hora por tipo), `probabilidades_eleccion_por_hora.csv` (prob. de elección), parámetros triangulares del enunciado §E.2, y probabilidad de N tipos (§E.2).

El problema proporciona la demanda en **kg por hora**, pero la simulación necesita la llegada de **clientes por hora**. La conversión requiere estimar cuántos kg compra un cliente promedio, lo cual depende de la hora (porque las probabilidades de elección cambian por franja).

**Paso 1 — E[kg por evento de compra de un tipo] ponderado por hora**:

Para cada franja horaria $h$, se pondera la media triangular de cada tipo por su probabilidad de elección en esa hora:

$$
E[\text{kg/tipo}]_h = \sum_{i=1}^{10} P_i(h) \times E[X_i]
$$

donde $P_i(h)$ viene del CSV de probabilidades y $E[X_i] = (\text{mín}_i + \text{moda}_i + \text{máx}_i) / 3$.

**Ejemplo para 09:00–10:00**:

$$
E[\text{kg/tipo}]_{09} = (0{,}2645 \times 1{,}100) + (0{,}2248 \times 1{,}100) + (0{,}1247 \times 0{,}933) + \cdots = 0{,}9891 \text{ kg}
$$

**Paso 2 — E[kg por cliente]**:

Multiplicar por el número esperado de tipos que compra un cliente:

$$
E[\text{kg/cliente}]_h = E[\text{tipos}] \times E[\text{kg/tipo}]_h = 1{,}65 \times E[\text{kg/tipo}]_h
$$

Ejemplo 09:00: $E[\text{kg/cliente}]_{09} = 1{,}65 \times 0{,}9891 = 1{,}6320$ kg.

**Paso 3 — Clientes por hora**:

Dividir la demanda total de la franja (suma de las 10 columnas del CSV de demanda) entre el consumo esperado por cliente:

$$
\text{Clientes}_h = \left\lfloor \frac{\text{Demanda total}_h}{E[\text{kg/cliente}]_h} \right\rceil
$$

**Ejemplo completo para 09:00–10:00**:

$$
\text{Demanda}_{09} = 126{,}19 + 107{,}26 + 50{,}48 + \cdots + 12{,}43 = 448{,}8 \text{ kg}
$$

$$
\text{Clientes}_{09} = \frac{448{,}8}{1{,}6320} = 275 \text{ clientes}
$$

**Ejemplo para 18:00–19:00 (peak)**:

$$
E[\text{kg/tipo}]_{18} = (0{,}1854 \times 1{,}100) + (0{,}1576 \times 1{,}100) + \cdots + (0{,}0687 \times 1{,}033) = 1{,}0733
$$

$$
E[\text{kg/cliente}]_{18} = 1{,}65 \times 1{,}0733 = 1{,}7710 \text{ kg}
$$

$$
\text{Clientes}_{18} = \frac{1.451{,}3}{1{,}7710} = 819 \text{ clientes}
$$

**Paso 4 — Tabla resumen de la derivación por hora**:

| Franja | Demanda (kg) | E[kg/tipo] | E[kg/cliente] | Clientes |
|---|---|---|---|---|
| 09–10 | 448,8 | 0,9891 | 1,6320 | 275 |
| 10–11 | 448,8 | 0,9891 | 1,6320 | 275 |
| 11–12 | 448,8 | 0,9891 | 1,6320 | 275 |
| 12–13 | 750,1 | 1,0347 | 1,7072 | 439 |
| 13–14 | 689,4 | 1,0016 | 1,6526 | 417 |
| 14–15 | 689,4 | 1,0016 | 1,6526 | 417 |
| 15–16 | 448,8 | 0,9891 | 1,6320 | 275 |
| 16–17 | 448,8 | 0,9891 | 1,6320 | 275 |
| 17–18 | 499,5 | 1,0123 | 1,6702 | 299 |
| 18–19 | 1.451,3 | 1,0733 | 1,7710 | 819 |
| 19–20 | 1.416,5 | 1,0649 | 1,7571 | 806 |
| 20–21 | 459,9 | 0,9993 | 1,6488 | 279 |
| **Total** | **8.200** | | | **4.851** |

> **Nota**: El E[kg/cliente] varía por hora porque las probabilidades de elección cambian (p.ej., en el peak vespertino aumenta la probabilidad de Hot Dog, cuya media triangular es mayor: 1,433 kg vs. ~0,6–1,1 kg de otros tipos).

**Interarribo medio**: Se calcula como `3.600 / clientes_por_hora`. Ejemplo 09:00: `3.600/275 = 13,1 seg`.

### 3.12 Restricciones del horno

| Parámetro                    | Valor                              |
| ----------------------------- | ---------------------------------- |
| Capacidad máxima por corrida | 1.200 kg (6 carros × 18 bandejas) |
| Carga mínima recomendada     | 600 kg (50%)                       |
| No mezclar familias           | Obligatorio                        |
| Retiro parcial                | Prohibido                          |
| Espera máx. pre-corrida      | 15 min                             |
| Setup cambio familia          | 5 min                              |
| Carga/Descarga                | 5 min c/u (1 manipulador)          |

#### Derivación de §3.12 — Restricciones del horno

> **Fuente**: Enunciado §III.C–G de `base_information.md`.

Todos los valores se toman directamente del enunciado:
- **1.200 kg** = 6 carros × (18 bandejas × Kg/bandeja promedio), enunciado §III.D
- **600 kg (50%)** = carga mínima recomendada, enunciado §III.G
- **5 min setup** al cambiar familia, enunciado §III.F
- **5 min carga/descarga** c/u, enunciado §III.E
- **15 min espera máxima**, enunciado §III.G

### 3.13 Turnos de trabajo

| Parámetro                       | Valor                                      |
| -------------------------------- | ------------------------------------------ |
| Jornada efectiva                 | 8 horas                                    |
| Colación                        | 45 min                                     |
| Descansos                        | 2 × 15 min                                |
| **Tiempo productivo neto** | **6 hrs 45 min = 405 min**           |
| Escalonamiento                   | Obligatorio (≥1 persona/función siempre) |

#### Derivación de §3.13 — Tiempo productivo neto

> **Fuente**: Enunciado §II.D de `base_information.md`.

El enunciado establece: jornada de 8 horas, colación de 45 min, y 2 descansos de 15 min. El tiempo productivo neto se calcula como:

$$
\text{Productivo} = 8 \text{ hrs} - 45 \text{ min} - 2 \times 15 \text{ min} = 480 - 45 - 30 = 405 \text{ min} = 6\text{h } 45\text{m}
$$

## 4. Supuestos Explícitos

> [!IMPORTANT]
> Los supuestos marcados con 🔶 fueron consultados al equipo y confirmados. Los marcados con 🔷 son supuestos propios del modelador.

### 4.1 Supuestos confirmados

| #     | Supuesto                                                                                                                                                                                                                                                         | Origen           |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| 🔶 S1 | **Etapa 2 del CSV = ciclo automático de mezclado.** El tiempo indicado en la columna "Amasado" del archivo `parametros_proceso_panaderia.csv` corresponde al tiempo del ciclo automático de la mezcladora. El panadero queda libre durante este ciclo. | Consulta directa |
| 🔶 S2 | **Capacidad del horno = 1.200 kg/corrida.** Los valores de Kg/Carro del CSV son referenciales por tipo de pan individual. La restricción de 600 kg (50%) y 1.200 kg (100%) aplica a la corrida combinada de productos de una misma familia.               | Consulta directa |
| 🔶 S3 | **Enfriado y traslado son un bloque combinado.** El tiempo del CSV incluye ambas actividades. La asignación interna se hace según contexto (ver S8).                                                                                                     | Consulta directa |
| 🔶 S4 | **Inventario inicial (09:00) se calcula desde los perfiles de demanda**, evaluando si siguen alguna distribución de probabilidad. No hay un valor fijo predefinido.                                                                                       | Consulta directa |
| 🔶 S5 | **Compra todo-o-nada.** Si el stock de un tipo es menor a la cantidad que el cliente desea, la venta completa de ese tipo se pierde. No hay venta parcial.                                                                                                 | Consulta directa |

### 4.2 Supuestos del modelador

| #      | Supuesto                                                                                                                                                                                                                                                                                    | Justificación                                                                                |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 🔷 S6  | **Amasado manual no tiene tiempo separado en el CSV.** Se interpreta que el proceso de amasado manual está implícito en el ciclo de producción. El panadero ocupa la amasadora durante un tiempo proporcional al ciclo de mezclado (se estima ≈ 50% del tiempo de mezclado auto). | El CSV no distingue un tiempo explícito para amasado manual separado del mezclado            |
| 🔷 S7  | **Los tiempos de proceso son determinísticos.** Dado que el enunciado no especifica distribuciones para los tiempos de producción, se modelan como constantes según la tabla de parámetros.                                                                                       | El enunciado sugiere considerar tiempos determinísticos donde no se especifica distribución |
| 🔷 S8  | **Split enfriado/traslado:** Enfriado ≈ 67% del tiempo combinado, Traslado ≈ 33%. Ver tabla detallada abajo.                                                                                                                                                                        | Proporción basada en que el enfriamiento es pasivo y más largo que el traslado activo       |
| 🔷 S9  | **El enfriamiento tiene capacidad ilimitada** (espacio suficiente de racks/mesas para enfriar).                                                                                                                                                                                       | El enunciado no limita este recurso y sugiere evaluar esta decisión                          |
| 🔷 S10 | **Los panes no vendidos al final del día se descartan.** No hay stock que pase al día siguiente.                                                                                                                                                                                    | Coherente con la operación de pan fresco                                                     |
| 🔷 S11 | **La demanda se modela a nivel de cliente individual**, con llegadas según una **distribución empírica** (tabla de frecuencias) implementada como Rate Table en SIMIO. Las tasas por hora son las observadas directamente, sin ajuste paramétrico.                                    | Preserva el patrón real sin imponer supuestos distribucionales. SIMIO genera interarribos Exponenciales dentro de cada intervalo, manteniendo la variabilidad estocástica |
| 🔷 S12 | **Materias primas disponibles sin restricción.** No hay quiebres de insumos.                                                                                                                                                                                                         | Fuera del alcance del modelo                                                                  |
| 🔷 S13 | **Todos los hornos son equivalentes e intercambiables.**                                                                                                                                                                                                                              | Supuesto operacional del enunciado                                                            |
| 🔷 S14 | **Carros y bandejas suficientes.** Se modelan explícitamente pero se asume disponibilidad inicial suficiente. El reporte final indica cuántos se necesitan.                                                                                                                         | Indicado en el enunciado                                                                      |

### 4.3 Split enfriado/traslado (Supuesto S8)

| Tipo                | Total (min) | Enfriado (min) | Traslado a sala (min) | Recurso traslado |
| ------------------- | ----------- | -------------- | --------------------- | ---------------- |
| Marraqueta          | 12          | 8              | 4                     | Ayudante         |
| Hallulla            | 12          | 8              | 4                     | Ayudante         |
| Marraqueta Integral | 12          | 8              | 4                     | Ayudante         |
| Hallulla Integral   | 12          | 8              | 4                     | Ayudante         |
| Pan Hot Dog         | 12          | 8              | 4                     | Ayudante         |
| Ciabatta            | 15          | 10             | 5                     | Ayudante         |
| Baguette            | 15          | 10             | 5                     | Ayudante         |
| Dobladita           | 10          | 7              | 3                     | Ayudante         |
| Bocado de Dama      | 10          | 7              | 3                     | Ayudante         |
| Amasado             | 12          | 8              | 4                     | Ayudante         |

#### Derivación de §4.3 — Split enfriado/traslado

> **Fuente**: El tiempo total "Enfriado y traslado" viene de `Min7` en `parametros_proceso_panaderia.csv`. La partición interna es supuesto del modelador (🔷 S8).

**Fórmula de split**: Enfriado ≈ 67% del total, Traslado ≈ 33% (redondeado a enteros). Ejemplo para Marraqueta (Total = 12 min):

$$
\text{Enfriado} = \lfloor 12 \times 0{,}67 \rfloor = 8 \text{ min}, \quad \text{Traslado} = 12 - 8 = 4 \text{ min}
$$

### 4.4 Inventario objetivo para las 09:00

El perfil de demanda muestra que las primeras 3 horas (09:00–12:00) tienen demanda idéntica (~449 kg/hr). Se propone como inventario inicial al menos **1,5× la demanda de la primera hora** por tipo, para absorber variabilidad:

| Tipo                | Demanda 1ª hr (kg) | Inventario objetivo 09:00 (kg) | Batches necesarios pre-apertura |
| ------------------- | ------------------- | ------------------------------ | ------------------------------- |
| Marraqueta          | 126,2               | 189,3                          | 4 (240 kg)                      |
| Hallulla            | 107,3               | 160,9                          | 3 (165 kg)                      |
| Marraqueta Integral | 50,5                | 75,7                           | 2 (120 kg)                      |
| Hallulla Integral   | 50,5                | 75,7                           | 2 (110 kg)                      |
| Pan Hot Dog         | 26,1                | 39,1                           | 1 (55 kg)                       |
| Ciabatta            | 15,1                | 22,7                           | 1 (50 kg)                       |
| Baguette            | 13,2                | 19,9                           | 1 (45 kg)                       |
| Dobladita           | 29,2                | 43,8                           | 1 (50 kg)                       |
| Bocado de Dama      | 18,3                | 27,5                           | 2 (50 kg)                       |
| Amasado             | 12,4                | 18,6                           | 1 (60 kg)                       |
| **TOTAL**     | **448,8**     | **673,2**                | **18 batches**            |

> El ciclo más largo pre-apertura es Ciabatta/Baguette (134/133 min). Para tener stock a las 09:00, la panadería debe iniciar operaciones **no más tarde de las 06:45** (considerando ~135 min de ciclo completo).

#### Derivación de §4.4 — Inventario objetivo

> **Fuentes**: `perfil_demanda_por_hora_panaderia.csv` (demanda 1ª hora por tipo) y `KgPorBatchRef` del CSV de parámetros.

**Paso 1 — Demanda de la 1ª hora por tipo**: Se toma la fila `09:00-10:00` del CSV de demanda. Ejemplo: Marraqueta = 126,19 kg.

**Paso 2 — Inventario objetivo**: Se aplica un factor de seguridad de 1,5×:

$$
\text{Inv. obj.}_{\text{Marraqueta}} = 126{,}19 \times 1{,}5 = 189{,}3 \text{ kg}
$$

> El factor 1,5× se justifica porque: (a) la demanda tiene variabilidad estocástica (distribución triangular por compra), y (b) se requiere margen para que la producción en curso reponga stock antes de agotar el inventario inicial.

**Paso 3 — Batches pre-apertura**: `⌈Inv_objetivo / Kg_Batch⌉`.

$$
\text{Batches}_{\text{Marraqueta}} = \left\lceil \frac{189{,}3}{60} \right\rceil = \lceil 3{,}16 \rceil = 4 \text{ batches} = 240 \text{ kg}
$$

**Paso 4 — Hora de inicio de operaciones**: El ciclo productivo más largo es Ciabatta (134 min). Para que este batch esté listo a las 09:00:

$$
\text{Inicio} = 09{:}00 - 134 \text{ min} \approx 06{:}46 \implies \text{inicio no más tarde de } 06{:}45
$$

---

## 5. Modelo Conceptual

### 5.1 Entidades del sistema

| Entidad                       | Descripción                                         | Atributos                                                      |
| ----------------------------- | ---------------------------------------------------- | -------------------------------------------------------------- |
| **Lote de producción** | Unidad que fluye por el proceso productivo           | TipoPan, FamiliaHorneado, KgLote, EtapaActual, HoraInicio      |
| **Corrida de horno**    | Agrupación de lotes de misma familia para una carga | Familia, ListaLotes, KgTotal, NCarros, TiempoCocción          |
| **Cliente**             | Entidad que consume inventario en sala               | NTiposAComprar, TiposSeleccionados[], KgPorTipo[], HoraLlegada |

### 5.2 Recursos

| Recurso               | Tipo              | Capacidad a determinar   | Usado en                                                 |
| --------------------- | ----------------- | ------------------------ | -------------------------------------------------------- |
| Panadero              | Humano (turno 8h) | Variable (estudio)       | Pesado, carga/retiro mezcladora, amasado manual, formado |
| Manipulador/Ayudante  | Humano (turno 8h) | Variable (estudio)       | Carga/descarga horno, traslado a sala                    |
| Mezcladora            | Máquina          | Variable (estudio)       | Ciclo automático de mezclado                            |
| Amasadora             | Máquina          | Variable (estudio)       | Amasado manual                                           |
| Mesa de Formado       | Estación         | Variable (estudio)       | Dividido y formado                                       |
| Cámara Fermentación | Espacio           | Capacidad ilimitada (S9) | Reposo, fermentación final                              |
| Horno                 | Máquina batch    | Variable (estudio)       | Horneado por familia                                     |
| Carros                | Transporte        | A reportar               | Transporte en horno y enfriamiento                       |
| Bandejas              | Transporte        | A reportar               | Dentro de carros                                         |

### 5.3 Variables de estado

#### Variables de inventario y estadísticas

| Variable | Tipo | Nombre SIMIO | Descripción |
|---|---|---|---|
| `Inventario[tipo]` | Continua (kg), Vector dim=10 | `MStaInventario` | Stock actual en sala por tipo de pan |
| `QuiebreAcum[tipo]` | Continua (kg), Vector dim=10 | `MStaQuiebres` | Demanda insatisfecha acumulada por tipo |
| `VentasAcum[tipo]` | Continua (kg), Vector dim=10 | `MStaVentas` | Kg vendidos acumulados por tipo |
| `LotesProducidos[tipo]` | Entera, Vector dim=10 | `MStaLotesProducidos` | Cantidad de batches completados por tipo |
| `ColaHorno[familia]` | Continua (kg), Vector dim=3 | `MStaColaHorno` | Kg acumulados esperando horno por familia |
| `HoraIdx` | Entera (1-12) | `MStaHoraIdx` | Índice de hora actual para tablas horarias |

#### Variables de control de producción (Enfoque Híbrido)

| Variable | Tipo | Nombre SIMIO | Descripción |
|---|---|---|---|
| `LotePlanActual` | Entera | `MStaLotePlanActual` | Índice de fila actual en `TablePlanProduccion` |
| `EnProceso[tipo]` | Continua (kg), Vector dim=10 | `MStaEnProceso` | Kg actualmente en el flujo productivo (aún no en sala) |
| `TipoReactivo` | Entera (1-10) | `MStaTipoReactivo` | Tipo de pan a producir como lote de emergencia |
| `LotesReactivos` | Entera | `MStaLotesReactivos` | Contador total de lotes de emergencia inyectados |

#### Variables de estado del horno

| Variable | Tipo | Descripción |
|---|---|---|
| `UltimaFamiliaHorno[horno]` | Categórica | Última familia horneada (para calcular setup) |
| `EstadoHorno[horno]` | Categórica | Libre / Cargando / Horneando / Descargando |
| `TiempoEsperaHorno[familia]` | Continua (min) | Tiempo que lleva esperando la carga |

> **Nota**: `EnProceso[tipo]` se incrementa cuando un lote entra a pesado y se decrementa cuando llega a sala de ventas. Permite al sistema reactivo calcular el déficit real sin duplicar producción.

### 5.4 Eventos principales

| Evento | Disparador | Acciones |
|---|---|---|
| Inicio de jornada | t=0 (06:00) | Inicia liberación de lotes según `TablePlanProduccion` |
| Liberación lote plan | `SrcLotes` cada ~4 min | Crea `EntLote` con tipo/familia/kg del plan secuencial |
| Revisión de déficit | `TimerRevisorDeficit` cada 30 min (desde 09:00) | Calcula déficit por tipo, puede inyectar lote reactivo |
| Lote reactivo | `EvtLoteReactivo` (Fire) | `SrcLotesReactivos` crea lote del tipo con mayor déficit |
| Llegada de cliente | Distribución empírica (Rate Table) | Selecciona tipos (condicional sin reemplazo), verifica stock |
| Fin de mezclado | Timer (auto cycle) | Libera mezcladora, panadero retira masa |
| Fin de fermentación | Timer | Lote disponible para horno, acumula en `ColaHorno[familia]` |
| Inicio de corrida | Política de carga/timeout | Carga horno, inicia cocción |
| Fin de horneado | Timer (14/18/21 min) | Descarga, envía a enfriamiento |
| Reposición a sala | Ayudante disponible | Incrementa `Inventario[tipo]`, decrementa `EnProceso[tipo]` |
| Colación/Descanso | Calendario turno (escalonado) | Retira recurso temporalmente (min. 3 panaderos activos) |
| Fin de jornada tienda | 21:00 | Cierre, calcula sobrantes |

### 5.5 Lógica de decisión

#### 5.5.1 Política de liberación de producción — Enfoque Híbrido

> **Decisión de diseño**: Se adoptó un enfoque **híbrido** que combina una secuencia de producción planificada con un mecanismo de ajuste reactivo por déficit. Esto balancea previsibilidad operativa con capacidad de respuesta a variaciones estocásticas.

**Componente 1 — Plan Base (fijo, `SrcLotes`)**:

```
SrcLotes genera EntLote cada ~4 min (155 lotes/día)
PARA cada lote i = 1..155:
  EStaTipoPan = TablePlanProduccion[i].PlanTipoPan
  EStaFamilia = TablePlanProduccion[i].PlanFamilia
  EStaKgLote  = TablePlanProduccion[i].PlanKgLote
  EnProceso[tipo] += KgLote
```

La secuencia en `TablePlanProduccion` se optimiza por:
1. Agrupación por familia (minimiza setups de horno)
2. Tipos de mayor demanda primero dentro de cada familia
3. Producción adelantada para el peak de 18:00-20:00

**Componente 2 — Ajuste Reactivo (dinámico, `ProcRevisorDeficit`)**:

```
CADA 30 minutos (desde 09:00, apertura de tienda):
  PARA cada tipo j = 1..10:
    deficit[j] = DemandaEsperada_2hrs[j] - Inventario[j] - EnProceso[j]
  j* = tipo con mayor déficit
  SI deficit[j*] > KgPorBatch[j*] / 2:
    MStaTipoReactivo = j*
    Fire EvtLoteReactivo → SrcLotesReactivos crea lote de emergencia
```

> **Horizonte de 2 horas**: Se anticipan 2 horas de demanda porque el ciclo productivo completo (pesado a sala) toma ~90-120 min.
>
> **Umbral de activación**: Solo se inyecta un lote reactivo si el déficit supera la mitad de un batch. Esto evita sobreproducción por déficits marginales.
>
> **Métrica de validación**: Si `LotesReactivos > 20` al final de la corrida, el plan base está mal dimensionado y requiere ajuste.

#### 5.5.2 Política de carga del horno

```
CUANDO lote termina fermentación final:
  Agregar kg a ColaHorno[familia]
  SI ColaHorno[familia] >= 600 kg (50% capacidad):
    Iniciar corrida (hasta 1200 kg)
  SINO:
    SI TiempoEsperaHorno[familia] >= 15 min:
      Iniciar corrida anticipada (con lo que haya)
    SINO:
      Esperar acumulación
```

#### 5.5.3 Política de secuencia de horno (a evaluar)

```
Estrategia A: Prioridad al producto con menor stock en sala
Estrategia B: Prioridad al producto con mayor demanda esperada
Estrategia C: Secuencia fija F1→F2→F3
Estrategia D: Híbrida (stock bajo + demanda esperada)
```

#### 5.5.4 Lógica de compra del cliente — Implementación con probabilidades condicionales

```
LLEGADA de cliente (ProcAsignarTiposCliente, Before Exiting de SrcClientes):
  HoraIdx = Math.Floor(Run.TimeNow / 60) + 1
  N_tipos ~ Discrete(1:50%, 2:35%, 3:15%)

  TIPO 1 — Selección marginal:
    Tipo1 = Random.Discrete con prob. acumuladas de TableProbEleccion[HoraIdx]
    Kg1 = Triangular(min, moda, max) de TableCompra[Tipo1]

  TIPO 2 (si N_tipos >= 2) — Selección condicional sin reemplazo:
    ProbRest1 = 1 - P(Tipo1)
    Rand2 = U(0,1) * ProbRest1
    PARA cada tipo j != Tipo1 (scan condicional):
      SI Rand2 <= P(j): Tipo2 = j -> SALIR
      SINO: Rand2 -= P(j) -> siguiente j
    Kg2 = Triangular de TableCompra[Tipo2]

  TIPO 3 (si N_tipos >= 3) — Selección condicional doble:
    ProbRest2 = ProbRest1 - P(Tipo2)
    Rand3 = U(0,1) * ProbRest2
    PARA cada tipo k != Tipo1, k != Tipo2:
      SI Rand3 <= P(k): Tipo3 = k -> SALIR
      SINO: Rand3 -= P(k) -> siguiente k
    Kg3 = Triangular de TableCompra[Tipo3]
```

```
VENTA (ProcVentaCliente, Entered de SrvVenta):
  PARA cada tipo seleccionado (1, 2, 3 si aplica):
    SI Inventario[tipo] >= Cantidad:
      Inventario[tipo] -= Cantidad
      VentasAcum[tipo] += Cantidad
    SINO:
      QuiebreAcum[tipo] += Cantidad  <-- S5 (todo-o-nada)
```

> **Validación §3.10**: Para hora 09:00 con Tipo1=Marraqueta (P=0.2645), P(Tipo2=Hallulla) = 0.2248/(1-0.2645) = 0.3056 ✓

### 5.6 Diagrama de flujo del proceso productivo (narrativo)

```
INICIO JORNADA (pre-apertura)
│
├─→ [1. PESADO Y DOSIFICACIÓN] ──→ 5 min, requiere: PANADERO
│
├─→ [2a. CARGA MEZCLADORA] ──→ 2 min, requiere: PANADERO + MEZCLADORA
│
├─→ [2b. MEZCLADO AUTOMÁTICO] ──→ 10-15 min (CSV), requiere: MEZCLADORA (panadero LIBRE) ← 🔶 S1
│
├─→ [2c. RETIRO DE MASA] ──→ 1 min, requiere: PANADERO
│
├─→ [3. AMASADO MANUAL] ──→ ~50% del tiempo mezclado (🔷 S6), requiere: PANADERO + AMASADORA
│
├─→ [4. REPOSO EN MASA] ──→ 15-30 min, sin recurso humano
│
├─→ [5. DIVIDIDO Y FORMADO] ──→ 8-12 min, requiere: PANADERO + MESA
│
├─→ [6. FERMENTACIÓN FINAL] ──→ 20-45 min, sin recurso humano
│
├─→ [COLA HORNO] ──→ Espera por familia, política de carga (min 600 kg, máx 1200 kg, timeout 15 min)
│
├─→ [SETUP HORNO] ──→ 0 o 5 min según cambio de familia
│
├─→ [7a. CARGA HORNO] ──→ 5 min, requiere: MANIPULADOR
│
├─→ [7b. HORNEADO] ──→ 14/18/21 min según familia, automático
│
├─→ [7c. DESCARGA HORNO] ──→ 5 min, requiere: MANIPULADOR
│
├─→ [8. ENFRIADO] ──→ 7-10 min (🔷 S8), sin recurso humano
│
├─→ [9. TRASLADO A SALA] ──→ 3-5 min (🔷 S8), requiere: AYUDANTE
│
└─→ [INVENTARIO SALA] ──→ Disponible para venta
```

### 5.7 Flujo del cliente

```
LLEGADA CLIENTE (Distribución empírica — Rate Table con tasas observadas por hora)
│
├─→ Determinar N_tipos (1/2/3)
│
├─→ PARA cada tipo a comprar:
│     ├─→ Seleccionar tipo (probabilidad horaria, sin reemplazo)
│     ├─→ Determinar cantidad (Triangular)
│     ├─→ ¿Stock >= cantidad?
│     │     ├─ SÍ → Venta (descontar inventario)
│     │     └─ NO → Quiebre (venta perdida, todo-o-nada) ← 🔶 S5
│     └─→ ¿Más tipos?
│
└─→ FIN CLIENTE
```

### 5.8 Diagrama de flujo XML (BPMN 2.0)

Los diagramas BPMN 2.0 detallados se encuentran en:

- **Archivo Draw.io**: `flujo/bpmn_panaderia.drawio`
- **Documentación Mermaid**: `flujo/diagrama_bpmn_panaderia.md`

Estos cubren los tres pools (Producción, Gestión de Hornos, Sala de Ventas) con lanes por recurso.

### 5.9 Tablas de lógica

#### Tabla L1: Asignación de recursos por etapa

| Etapa                  | Panadero | Manipulador | Mezcladora | Amasadora | Mesa | Horno |
| ---------------------- | -------- | ----------- | ---------- | --------- | ---- | ----- |
| Pesado y dosificación | ✅       |             |            |           |      |       |
| Carga mezcladora       | ✅       |             | ✅         |           |      |       |
| Mezclado automático   |          |             | ✅         |           |      |       |
| Retiro de masa         | ✅       |             | ✅         |           |      |       |
| Amasado manual         | ✅       |             |            | ✅        |      |       |
| Reposo en masa         |          |             |            |           |      |       |
| Dividido y formado     | ✅       |             |            |           | ✅   |       |
| Fermentación final    |          |             |            |           |      |       |
| Carga horno            |          | ✅          |            |           |      | ✅    |
| Horneado               |          |             |            |           |      | ✅    |
| Descarga horno         |          | ✅          |            |           |      | ✅    |
| Enfriado               |          |             |            |           |      |       |
| Traslado a sala        |          | ✅          |            |           |      |       |

#### Tabla L2: Compatibilidad de familias en horno

| Corrida \ Familia | Fam 1 (14m)      | Fam 2 (18m)      | Fam 3 (21m)      |
| ----------------- | ---------------- | ---------------- | ---------------- |
| Fam 1 (14m)       | ✅ Sin setup     | ❌ + 5 min setup | ❌ + 5 min setup |
| Fam 2 (18m)       | ❌ + 5 min setup | ✅ Sin setup     | ❌ + 5 min setup |
| Fam 3 (21m)       | ❌ + 5 min setup | ❌ + 5 min setup | ✅ Sin setup     |

#### Tabla L3: Política de carga del horno

| Condición                               | Acción                                               |
| ---------------------------------------- | ----------------------------------------------------- |
| Cola familia ≥ 600 kg                   | Cargar horno (hasta 1200 kg), iniciar corrida         |
| Cola familia < 600 kg Y espera < 15 min  | Seguir esperando acumulación                         |
| Cola familia < 600 kg Y espera ≥ 15 min | Iniciar corrida anticipada con carga disponible       |
| Horno ocupado                            | Lote espera en cola                                   |
| Manipulador no disponible                | Horno no puede iniciar carga/descarga (tiempo ocioso) |

---

## 6. Nivel de Detalle Adecuado

### 6.1 Unidades de modelación

| Aspecto                    | Nivel de detalle           | Justificación                                                                                                  |
| -------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Demanda**          | Cliente individual         | Permite modelar comportamiento estocástico (N tipos, cantidad triangular, selección condicional, todo-o-nada) |
| **Producción**      | Lote (batch)               | Unidad natural del proceso; tamaño fijo por tipo (25-60 kg)                                                    |
| **Inventario**       | Continuo en kg por tipo    | 10 SKUs independientes, descontados por cada compra                                                             |
| **Horno**            | Corrida (batch de familia) | Agrupa múltiples lotes de producción de misma familia (hasta 1200 kg)                                         |
| **Tiempo**           | Minutos                    | Resolución suficiente para todas las operaciones (mín. 1 min)                                                 |
| **Recursos humanos** | Individual con calendario  | Cada trabajador tiene turno, colación y descansos escalonados                                                  |
| **Carros/bandejas**  | Conteo explícito          | Necesario para reportar cantidad requerida                                                                      |

### 6.2 Análisis de carga de recursos (justificación del nivel de detalle)

#### Mezcladora — CUELLO DE BOTELLA IDENTIFICADO

| Métrica                  | Valor                                       |
| ------------------------- | ------------------------------------------- |
| Tiempo ocupado por batch  | 13-18 min (carga 2 + auto 10-15 + retiro 1) |
| Total batches/día        | 155                                         |
| Total mezcladora-min/día | **2.442 min (40,7 hrs)**              |
| Con 1 mezcladora (16 hrs) | **254% utilización → INSUFICIENTE** |
| Con 2 mezcladoras         | 127% → INSUFICIENTE                        |
| Con 3 mezcladoras         | 85% → VIABLE                               |

> **Hallazgo crítico**: La mezcladora es el recurso más restrictivo del sistema. Se requieren **mínimo 3 mezcladoras** para la producción diaria.

#### Panadero

| Métrica                                     | Valor                                         |
| -------------------------------------------- | --------------------------------------------- |
| Tiempo hands-on por batch                    | 16-20 min (pesado + carga + retiro + formado) |
| Total panadero-min/día (sin amasado manual) | 2.926 min (48,8 hrs)                          |
| Tiempo productivo neto por turno             | 405 min (6h 45m)                              |
| Mínimo panaderos (turno único)             | ⌈48,8 / 6,75⌉ =**8 panaderos**        |
| Con amasado manual (+50% mezclado)           | ~3.600 min →**9 panaderos**            |

#### Horno

| Métrica                         | Valor                                                       |
| -------------------------------- | ----------------------------------------------------------- |
| Corridas totales/día            | 9 (mínimo teórico)                                        |
| Tiempo total horno (sin setup)   | 250 min (4,2 hrs)                                           |
| Tiempo total horno (con setup)   | 295 min (4,9 hrs)                                           |
| Con 1 horno (16 hrs disponibles) | **31% utilización → 1 horno suficiente en teoría** |

> **Nota**: Aunque 1 horno basta en volumen agregado, la restricción operativa es el **timing**: la producción debe distribuirse durante el día para evitar quiebres, especialmente antes del peak de 18:00–20:00. Probablemente se necesiten **2 hornos** para flexibilidad de secuenciamiento.

#### Manipulador/Ayudante

| Métrica                             | Valor                                      |
| ------------------------------------ | ------------------------------------------ |
| Carga/descarga horno                 | 9 corridas × 10 min = 90 min              |
| Traslado a sala                      | 155 batches × ~4 min = 620 min            |
| Total manipulador-min/día           | **710 min (11,8 hrs)**               |
| Mínimo manipuladores (turno único) | ⌈11,8 / 6,75⌉ =**2 manipuladores** |

#### Derivación de §6.2 — Cálculos de carga de recursos

> **Fuentes**: Tiempos de `parametros_proceso_panaderia.csv`, batches de §3.5, tiempos del enunciado (§II.A, §III.E), y tiempo productivo neto de §3.13.

**Mezcladora**: Cada batch ocupa la mezcladora durante `carga (2 min) + ciclo_auto (Min2 del CSV) + retiro (1 min)`:

$$
\text{Ciclo mezcladora}_{\text{Marraqueta}} = 2 + 12 + 1 = 15 \text{ min}
$$

Total = Σ (ciclo × batches). Ejemplo parcial: Marraqueta: 15 × 34 = 510 min, Hallulla: 17 × 31 = 527 min, ..., Amasado: 18 × 7 = 126 min. **Total = 2.442 min**.

Utilización con N mezcladoras (jornada ~16 hrs = 960 min): `2.442 / (N × 960)`. Con 3: 85%.

**Panadero**: Tiempo "hands-on" por batch = `pesado (5) + carga_mezcladora (2) + retiro (1) + formado (Min4 del CSV)`:

$$
\text{Hands-on}_{\text{Marraqueta}} = 5 + 2 + 1 + 10 = 18 \text{ min} \times 34 = 612 \text{ min}
$$

Total sin amasado manual = 2.926 min. Mínimo panaderos = `⌈2.926 / 405⌉` = `⌈7,2⌉` = 8 (donde 405 min = tiempo productivo neto por turno).

Con amasado manual (🔷 S6: ~50% del tiempo de mezclado auto): +988 min → 3.914 min → `⌈3.914/405⌉` = 10 panaderos.

**Horno**: 9 corridas × (carga 5 + horneado + descarga 5). Sin setup: Fam1: 2×24 = 48, Fam2: 5×28 = 140, Fam3: 2×31 = 62 → **250 min**. Con setup peor caso (+5 min por cambio de familia, máx 8 cambios): 250 + 45 = **295 min**. Utilización: 295/960 = 31%.

**Manipulador**: Horno: 9 × (5+5) = 90 min. Traslado: Σ(traslado × batches) usando tiempos del split S8 → **620 min**. Total: 710 min = 11,8 hrs → `⌈11,8/6,75⌉` = 2.

### 6.3 Elementos que NO requieren modelado detallado

| Elemento                        | Nivel de abstracción              | Razón                                                |
| ------------------------------- | ---------------------------------- | ----------------------------------------------------- |
| Cámaras de fermentación       | Capacidad ilimitada (delay simple) | No se espera que sean cuello de botella (supuesto S9) |
| Composición de ingredientes    | No modelado                        | No afecta tiempos ni capacidad                        |
| Calidad del producto            | No modelado                        | Fuera de alcance                                      |
| Layout físico de la panadería | No modelado                        | Tiempos de transporte incluidos en etapas             |
| Fallas de equipo                | No modelado                        | Supuesto del enunciado                                |

### 6.4 Resumen de recursos mínimos estimados (punto de partida para experimentación)

| Recurso          | Mínimo estimado       | Notas                                               |
| ---------------- | ---------------------- | --------------------------------------------------- |
| Mezcladoras      | 3                      | Cuello de botella principal                         |
| Amasadoras       | 2-3                    | Depende del tiempo de amasado manual (S6)           |
| Mesas de formado | 2-3                    | Paralelo con mezcladoras                            |
| Hornos           | 1-2                    | 1 basta en volumen; 2 para flexibilidad temporal    |
| Panaderos        | 8-9 por turno          | Requiere 2+ turnos traslapados                      |
| Manipuladores    | 2 por turno            | Con turnos traslapados                              |
| Carros           | ~20-30 en circulación | 2 carros/batch × batches simultáneos              |
| Bandejas         | ~400-500               | ~27 bandejas/batch promedio × batches simultáneos |

---

## Anexo A: Validación de datos de entrada

### A.1 Perfil de demanda horaria

Se verificó que la suma de la demanda horaria por tipo coincide con la demanda diaria declarada:

| Tipo                | Suma perfil (kg) | Esperado (kg) | Δ     |
| ------------------- | ---------------- | ------------- | ------ |
| Marraqueta          | 2.000,0          | 2.000         | −0,02 |
| Hallulla            | 1.700,0          | 1.700         | −0,03 |
| Marraqueta Integral | 800,0            | 800           | +0,01  |
| Hallulla Integral   | 800,0            | 800           | +0,01  |
| Pan Hot Dog         | 1.200,0          | 1.200         | +0,01  |
| Ciabatta            | 400,0            | 400           | −0,02 |
| Baguette            | 350,0            | 350           | +0,01  |
| Dobladita           | 350,0            | 350           | +0,04  |
| Bocado de Dama      | 220,0            | 220           | −0,04 |
| Amasado             | 380,0            | 380           | +0,00  |

**Resultado**: ✅ Datos consistentes (diferencias < 0,05 kg por redondeo).

### A.2 Probabilidades de elección

Se verificó que las probabilidades suman 1,0 en cada franja:

| Franja            | Suma P             |
| ----------------- | ------------------ |
| Todas las franjas | 0,99998 – 1,00001 |

**Resultado**: ✅ Consistentes (error < 0,00002 por redondeo).

### A.3 Regímenes de demanda identificados y justificación del enfoque empírico

La demanda NO sigue una distribución uniforme ni normal a lo largo del día. Se identifican **3 regímenes discretos**:

| Régimen        | Horas               | Kg/hr promedio | % del día    |
| --------------- | ------------------- | -------------- | ------------- |
| **Bajo**  | 09-12, 15-17, 20-21 | ~451           | 33%           |
| **Medio** | 12-15, 17-18        | ~657           | 32%           |
| **Alto**  | 18-20               | ~1.434         | **35%** |

> **Justificación de la distribución empírica**: La demanda horaria presenta un patrón **trimodal** con saltos abruptos (especialmente la transición de 500→1.451 kg/hr entre 17:00–18:00). Este comportamiento no se ajusta a distribuciones paramétricas estándar (Normal, Poisson homogéneo, etc.). Por tanto, se utiliza una **distribución empírica** (tabla de frecuencias observadas) como entrada directa al Rate Table de SIMIO, lo que garantiza que la simulación reproduce fielmente la carga operativa real sin sesgo de especificación.

---

## Anexo B: Referencias a archivos fuente

| Archivo                                   | Contenido                                                        | Validado |
| ----------------------------------------- | ---------------------------------------------------------------- | -------- |
| `parametros_proceso_panaderia.csv`      | Tiempos por etapa, tamaño de lote, temperatura, capacidad carro | ✅       |
| `perfil_demanda_por_hora_panaderia.csv` | Kg demandados por hora por tipo de pan                           | ✅       |
| `probabilidades_eleccion_por_hora.csv`  | P(elegir tipo i) por franja horaria                              | ✅       |
| `flujo/bpmn_panaderia.drawio`           | Diagrama BPMN 2.0 completo (Draw.io)                             | ✅       |
| `flujo/diagrama_bpmn_panaderia.md`      | Documentación Mermaid del BPMN                                  | ✅       |
