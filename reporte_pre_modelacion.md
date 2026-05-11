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

| Indicador | Definición |
|---|---|
| Nivel de servicio (%) | kg vendidos / kg demandados × 100, por tipo |
| Quiebres por tipo | kg no vendidos por falta de stock |
| Sobrantes al cierre | kg producidos no vendidos al cierre (21:00) |
| Utilización de recursos | % tiempo efectivo / tiempo disponible |

---

## 2. Delimitación del Sistema

### 2.1 Dentro del modelo

| Subsistema | Elementos incluidos |
|---|---|
| **Producción** | 10 tipos de pan, etapas secuenciales (pesado → mezclado → amasado → reposo → formado → fermentación → horneado → enfriado → traslado) |
| **Recursos humanos** | Panaderos y manipuladores/ayudantes con turnos de 8h, colación (45 min) y 2 descansos (15 min c/u) escalonados |
| **Maquinaria** | Mezcladoras, amasadoras, mesas de formado, hornos industriales batch |
| **Infraestructura** | Cámaras de fermentación, zona de enfriamiento, carros y bandejas |
| **Inventario sala** | Stock por tipo de pan, reposición desde producción |
| **Demanda** | Clientes con llegada no uniforme, compra de 1-3 tipos, cantidad triangular por tipo |
| **Hornos** | Operación batch por familias de horneado (14/18/21 min), setup, carga/descarga |

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

| # | Tipo de Pan | Familia | Tiempo Horneado | Familia Proceso |
|---|---|---|---|---|
| 1 | Marraqueta | Familia 2 | 18 min | Directo |
| 2 | Hallulla | Familia 2 | 18 min | Directo con materia grasa |
| 3 | Marraqueta Integral | Familia 3 | 21 min | Directo integral |
| 4 | Hallulla Integral | Familia 2 | 18 min | Directo integral con materia grasa |
| 5 | Pan Hot Dog | Familia 1 | 14 min | Enriquecido |
| 6 | Ciabatta | Familia 3 | 21 min | Alta hidratación |
| 7 | Baguette | Familia 3 | 21 min | Francés/artesanal |
| 8 | Dobladita | Familia 1 | 14 min | Masa grasa laminada simple |
| 9 | Bocado de Dama | Familia 1 | 14 min | Pan pequeño enriquecido |
| 10 | Amasado | Familia 2 | 18 min | Tradicional chileno |

### 3.2 Tiempos de proceso por etapa (minutos)

> **Nota**: La Etapa 2 del CSV ("Amasado") corresponde al **ciclo automático de mezclado**. Adicionalmente, el panadero emplea 2 min para cargar la mezcladora y 1 min para retirar la masa (overhead).

| Tipo | Pesado | Mezclado (auto) | Reposo | Formado | Ferm. Final | Horneado | Enfriado+Trasl. | **Ciclo total** | Kg/Batch |
|---|---|---|---|---|---|---|---|---|---|
| Marraqueta | 5 | 12 | 15 | 10 | 35 | 18 | 12 | 107 | 60 |
| Hallulla | 5 | 14 | 20 | 12 | 30 | 18 | 12 | 111 | 55 |
| Marraqueta Integral | 5 | 13 | 18 | 10 | 40 | 21 | 12 | 119 | 60 |
| Hallulla Integral | 5 | 15 | 20 | 12 | 35 | 18 | 12 | 117 | 55 |
| Pan Hot Dog | 5 | 12 | 15 | 12 | 40 | 14 | 12 | 110 | 55 |
| Ciabatta | 5 | 10 | 30 | 8 | 45 | 21 | 15 | 134 | 50 |
| Baguette | 5 | 10 | 25 | 12 | 45 | 21 | 15 | 133 | 45 |
| Dobladita | 5 | 13 | 15 | 10 | 20 | 14 | 10 | 87 | 50 |
| Bocado de Dama | 5 | 12 | 15 | 10 | 30 | 14 | 10 | 96 | 25 |
| Amasado | 5 | 15 | 20 | 10 | 35 | 18 | 12 | 115 | 60 |

### 3.3 Demanda diaria por tipo

| Tipo | Demanda (kg/día) | % del total |
|---|---|---|
| Marraqueta | 2.000 | 24,4% |
| Hallulla | 1.700 | 20,7% |
| Pan Hot Dog | 1.200 | 14,6% |
| Marraqueta Integral | 800 | 9,8% |
| Hallulla Integral | 800 | 9,8% |
| Ciabatta | 400 | 4,9% |
| Amasado | 380 | 4,6% |
| Dobladita | 350 | 4,3% |
| Baguette | 350 | 4,3% |
| Bocado de Dama | 220 | 2,7% |
| **TOTAL** | **8.200** | **100%** |

### 3.4 Perfil de demanda horaria (kg/hora)

| Franja | Total kg | % diario | Régimen |
|---|---|---|---|
| 09:00–10:00 | 448,8 | 5,5% | Bajo |
| 10:00–11:00 | 448,8 | 5,5% | Bajo |
| 11:00–12:00 | 448,8 | 5,5% | Bajo |
| 12:00–13:00 | 750,2 | 9,1% | Medio |
| 13:00–14:00 | 689,4 | 8,4% | Medio |
| 14:00–15:00 | 689,4 | 8,4% | Medio |
| 15:00–16:00 | 448,8 | 5,5% | Bajo |
| 16:00–17:00 | 448,8 | 5,5% | Bajo |
| 17:00–18:00 | 499,5 | 6,1% | Medio |
| 18:00–19:00 | 1.451,3 | 17,7% | **Alto** |
| 19:00–20:00 | 1.416,6 | 17,3% | **Alto** |
| 20:00–21:00 | 459,9 | 5,6% | Bajo |

**Observación**: La demanda presenta **tres regímenes claramente diferenciados**:
- **Bajo** (~450 kg/hr): mañana, tarde temprana y cierre → 6 horas
- **Medio** (~657 kg/hr): mediodía y pre-peak → 4 horas
- **Alto** (~1.434 kg/hr): peak vespertino 18:00–20:00 → 2 horas (**35% de la demanda diaria en 2 horas**)

### 3.5 Lotes de producción requeridos por día

| Tipo | Demanda kg | Kg/Batch | Batches/día |
|---|---|---|---|
| Marraqueta | 2.000 | 60 | 34 |
| Hallulla | 1.700 | 55 | 31 |
| Pan Hot Dog | 1.200 | 55 | 22 |
| Hallulla Integral | 800 | 55 | 15 |
| Marraqueta Integral | 800 | 60 | 14 |
| Bocado de Dama | 220 | 25 | 9 |
| Ciabatta | 400 | 50 | 8 |
| Baguette | 350 | 45 | 8 |
| Dobladita | 350 | 50 | 7 |
| Amasado | 380 | 60 | 7 |
| **TOTAL** | **8.200** | — | **155** |

### 3.6 Corridas de horno por familia (capacidad 1.200 kg/corrida)

| Familia | Tipos incluidos | Kg totales | Corridas mín. | Tiempo hornear | Tiempo total/corrida* |
|---|---|---|---|---|---|
| Fam. 1 (corto) | Hot Dog, Dobladita, Bocado de Dama | 1.770 | 2 | 14 min | 24 min |
| Fam. 2 (medio) | Marraqueta, Hallulla, Hallulla Int., Amasado | 4.880 | 5 | 18 min | 28 min |
| Fam. 3 (largo) | Marraqueta Int., Ciabatta, Baguette | 1.550 | 2 | 21 min | 31 min |
| **TOTAL** | | **8.200** | **9** | | |

*Tiempo total/corrida = carga (5 min) + horneado + descarga (5 min), sin setup.

### 3.7 Carros y bandejas por batch de producción

| Tipo | Kg/Batch | Kg/Carro | Kg/Bandeja | Bandejas/Batch | Carros/Batch |
|---|---|---|---|---|---|
| Marraqueta | 60 | 40 | 2,22 | 27 | 2 |
| Hallulla | 55 | 45 | 2,50 | 22 | 2 |
| Marraqueta Integral | 60 | 38 | 2,11 | 29 | 2 |
| Hallulla Integral | 55 | 42 | 2,33 | 24 | 2 |
| Pan Hot Dog | 55 | 35 | 1,94 | 29 | 2 |
| Ciabatta | 50 | 35 | 1,94 | 26 | 2 |
| Baguette | 45 | 32 | 1,78 | 26 | 2 |
| Dobladita | 50 | 45 | 2,50 | 20 | 2 |
| Bocado de Dama | 25 | 28 | 1,56 | 17 | 1 |
| Amasado | 60 | 40 | 2,22 | 27 | 2 |

### 3.8 Distribuciones de compra por cliente

**Número de tipos por compra:**

| Tipos | Probabilidad |
|---|---|
| 1 tipo | 50% |
| 2 tipos | 35% |
| 3 tipos | 15% |
| **E[tipos]** | **1,65** |

**Cantidad comprada por tipo — Distribución Triangular:**

| Tipo | Mín (kg) | Moda (kg) | Máx (kg) | E[X] (kg) |
|---|---|---|---|---|
| Marraqueta | 0,3 | 1,0 | 2,0 | 1,100 |
| Hallulla | 0,3 | 1,0 | 2,0 | 1,100 |
| Marraqueta Integral | 0,3 | 0,5 | 2,0 | 0,933 |
| Hallulla Integral | 0,3 | 0,7 | 1,5 | 0,833 |
| Pan Hot Dog | 0,3 | 1,0 | 3,0 | 1,433 |
| Ciabatta | 0,3 | 0,5 | 1,5 | 0,767 |
| Baguette | 0,3 | 0,5 | 1,0 | 0,600 |
| Dobladita | 0,3 | 0,5 | 1,5 | 0,767 |
| Bocado de Dama | 0,3 | 0,5 | 1,0 | 0,600 |
| Amasado | 0,3 | 0,8 | 2,0 | 1,033 |

### 3.9 Probabilidades de elección (primera selección) por hora — Tabla completa

Extraídas de `probabilidades_eleccion_por_hora.csv`. Suman ~1,0 en cada franja. **Cada hora tiene una distribución discreta propia** que debe alimentar al modelo SIMIO como tabla independiente.

| Franja | Marraq. | Hallulla | Marr.Int | Hall.Int | HotDog | Ciabatta | Baguette | Doblad. | Boc.Dama | Amasado |
|---|---|---|---|---|---|---|---|---|---|---|
| 09–10 | 0,2645 | 0,2248 | 0,1247 | 0,1164 | 0,0546 | 0,0374 | 0,0327 | 0,0720 | 0,0453 | 0,0277 |
| 10–11 | 0,2645 | 0,2248 | 0,1247 | 0,1164 | 0,0546 | 0,0374 | 0,0327 | 0,0720 | 0,0453 | 0,0277 |
| 11–12 | 0,2645 | 0,2248 | 0,1247 | 0,1164 | 0,0546 | 0,0374 | 0,0327 | 0,0720 | 0,0453 | 0,0277 |
| 12–13 | 0,2313 | 0,1966 | 0,1090 | 0,1018 | 0,1534 | 0,0525 | 0,0459 | 0,0434 | 0,0273 | 0,0390 |
| 13–14 | 0,2505 | 0,2129 | 0,1181 | 0,1102 | 0,0831 | 0,0569 | 0,0498 | 0,0470 | 0,0295 | 0,0422 |
| 14–15 | 0,2505 | 0,2129 | 0,1181 | 0,1102 | 0,0831 | 0,0569 | 0,0498 | 0,0470 | 0,0295 | 0,0422 |
| 15–16 | 0,2645 | 0,2248 | 0,1247 | 0,1164 | 0,0546 | 0,0374 | 0,0327 | 0,0720 | 0,0453 | 0,0277 |
| 16–17 | 0,2645 | 0,2248 | 0,1247 | 0,1164 | 0,0546 | 0,0374 | 0,0327 | 0,0720 | 0,0453 | 0,0277 |
| 17–18 | 0,2381 | 0,2024 | 0,1123 | 0,1048 | 0,1124 | 0,0438 | 0,0383 | 0,0649 | 0,0408 | 0,0424 |
| 18–19 | 0,1854 | 0,1576 | 0,0874 | 0,0816 | **0,2501** | 0,0708 | 0,0619 | 0,0225 | 0,0141 | 0,0687 |
| 19–20 | 0,1897 | 0,1612 | 0,0894 | 0,0835 | **0,2326** | 0,0724 | 0,0634 | 0,0230 | 0,0145 | 0,0703 |
| 20–21 | 0,2584 | 0,2196 | 0,1218 | 0,1137 | 0,0762 | 0,0365 | 0,0320 | 0,0704 | 0,0442 | 0,0271 |

**Observaciones clave**:
- Las franjas 09–12, 15–17 comparten la **misma distribución** (6 horas idénticas).
- El **Pan Hot Dog** pasa de 5,5% en horario bajo a **25,0%** en peak vespertino (18–19), un cambio de 4,6×.
- **Dobladita** y **Bocado de Dama** tienen demanda **uniforme** a lo largo del día (probabilidad casi constante).
- Cada hora debe configurarse como una **tabla de probabilidad discreta separada** en SIMIO.

### 3.10 Probabilidades condicionales (2ª y 3ª selección)

Cuando un cliente compra 2 o 3 tipos **diferentes**, la selección del 2º tipo (y 3º) se realiza sin reemplazo:

$$P(\text{2º} = j \mid \text{1º} = i) = \frac{P_j}{1 - P_i}, \quad j \neq i$$

$$P(\text{3º} = k \mid \text{1º} = i, \text{2º} = j) = \frac{P_k}{1 - P_i - P_j}, \quad k \neq i,j$$

**Ejemplo (09:00–10:00)** — P(2º tipo | 1º = Marraqueta):

| 2º tipo | P condicional |
|---|---|
| Hallulla | 0,3056 |
| Marraqueta Int. | 0,1695 |
| Hallulla Int. | 0,1582 |
| Dobladita | 0,0979 |
| Pan Hot Dog | 0,0742 |
| Bocado de Dama | 0,0616 |
| Ciabatta | 0,0508 |
| Baguette | 0,0445 |
| Amasado | 0,0377 |

### 3.11 Tasa de llegada de clientes estimada

**Metodología de estimación**: La tasa se calcula de forma inversa a partir de la demanda conocida en kg/hora. Para cada franja horaria:

$$N_{\text{clientes/hr}} = \frac{\text{Demanda total (kg/hr)}}{E[\text{tipos}] \times \sum_{i} P_i \times E[\text{Tri}_i]}$$

Donde:
- $E[\text{tipos}]$ = 1,65 (valor esperado de tipos por cliente)
- $P_i$ = probabilidad de elegir tipo $i$ en esa hora (tabla §3.9)
- $E[\text{Tri}_i]$ = $(\min + \text{moda} + \max)/3$ para la distribución triangular de cada tipo

Esta estimación asume que la selección "sin reemplazo" para 2º y 3º tipo no distorsiona significativamente el promedio (razonable con 10 tipos y probabilidades marginales pequeñas).

| Franja | Demanda (kg) | Clientes/hr | Inter-arribo (seg) | Inter-arribo (min) |
|---|---|---|---|---|
| 09:00–10:00 | 449 | ~275 | 13,1 | 0,22 |
| 10:00–11:00 | 449 | ~275 | 13,1 | 0,22 |
| 11:00–12:00 | 449 | ~275 | 13,1 | 0,22 |
| 12:00–13:00 | 750 | ~439 | 8,2 | 0,14 |
| 13:00–14:00 | 689 | ~417 | 8,6 | 0,14 |
| 14:00–15:00 | 689 | ~417 | 8,6 | 0,14 |
| 15:00–16:00 | 449 | ~275 | 13,1 | 0,22 |
| 16:00–17:00 | 449 | ~275 | 13,1 | 0,22 |
| 17:00–18:00 | 499 | ~299 | 12,0 | 0,20 |
| 18:00–19:00 | 1.451 | ~819 | 4,4 | 0,07 |
| 19:00–20:00 | 1.417 | ~806 | 4,5 | 0,07 |
| 20:00–21:00 | 460 | ~279 | 12,9 | 0,22 |
| **Total/día** | **8.200** | **~4.852** | | |

### 3.12 Restricciones del horno

| Parámetro | Valor |
|---|---|
| Capacidad máxima por corrida | 1.200 kg (6 carros × 18 bandejas) |
| Carga mínima recomendada | 600 kg (50%) |
| No mezclar familias | Obligatorio |
| Retiro parcial | Prohibido |
| Espera máx. pre-corrida | 15 min |
| Setup cambio familia | 5 min |
| Carga/Descarga | 5 min c/u (1 manipulador) |

### 3.13 Turnos de trabajo

| Parámetro | Valor |
|---|---|
| Jornada efectiva | 8 horas |
| Colación | 45 min |
| Descansos | 2 × 15 min |
| **Tiempo productivo neto** | **6 hrs 45 min = 405 min** |
| Escalonamiento | Obligatorio (≥1 persona/función siempre) |
## 4. Supuestos Explícitos

> [!IMPORTANT]
> Los supuestos marcados con 🔶 fueron consultados al equipo y confirmados. Los marcados con 🔷 son supuestos propios del modelador.

### 4.1 Supuestos confirmados

| # | Supuesto | Origen |
|---|---|---|
| 🔶 S1 | **Etapa 2 del CSV = ciclo automático de mezclado.** El tiempo indicado en la columna "Amasado" del archivo `parametros_proceso_panaderia.csv` corresponde al tiempo del ciclo automático de la mezcladora. El panadero queda libre durante este ciclo. | Consulta directa |
| 🔶 S2 | **Capacidad del horno = 1.200 kg/corrida.** Los valores de Kg/Carro del CSV son referenciales por tipo de pan individual. La restricción de 600 kg (50%) y 1.200 kg (100%) aplica a la corrida combinada de productos de una misma familia. | Consulta directa |
| 🔶 S3 | **Enfriado y traslado son un bloque combinado.** El tiempo del CSV incluye ambas actividades. La asignación interna se hace según contexto (ver S8). | Consulta directa |
| 🔶 S4 | **Inventario inicial (09:00) se calcula desde los perfiles de demanda**, evaluando si siguen alguna distribución de probabilidad. No hay un valor fijo predefinido. | Consulta directa |
| 🔶 S5 | **Compra todo-o-nada.** Si el stock de un tipo es menor a la cantidad que el cliente desea, la venta completa de ese tipo se pierde. No hay venta parcial. | Consulta directa |

### 4.2 Supuestos del modelador

| # | Supuesto | Justificación |
|---|---|---|
| 🔷 S6 | **Amasado manual no tiene tiempo separado en el CSV.** Se interpreta que el proceso de amasado manual está implícito en el ciclo de producción. El panadero ocupa la amasadora durante un tiempo proporcional al ciclo de mezclado (se estima ≈ 50% del tiempo de mezclado auto). | El CSV no distingue un tiempo explícito para amasado manual separado del mezclado |
| 🔷 S7 | **Los tiempos de proceso son determinísticos.** Dado que el enunciado no especifica distribuciones para los tiempos de producción, se modelan como constantes según la tabla de parámetros. | El enunciado sugiere considerar tiempos determinísticos donde no se especifica distribución |
| 🔷 S8 | **Split enfriado/traslado:** Enfriado ≈ 67% del tiempo combinado, Traslado ≈ 33%. Ver tabla detallada abajo. | Proporción basada en que el enfriamiento es pasivo y más largo que el traslado activo |
| 🔷 S9 | **El enfriamiento tiene capacidad ilimitada** (espacio suficiente de racks/mesas para enfriar). | El enunciado no limita este recurso y sugiere evaluar esta decisión |
| 🔷 S10 | **Los panes no vendidos al final del día se descartan.** No hay stock que pase al día siguiente. | Coherente con la operación de pan fresco |
| 🔷 S11 | **La demanda se modela a nivel de cliente individual**, con llegadas según proceso de Poisson no homogéneo (tasa variable por hora). | Permite capturar variabilidad estocástica de la demanda |
| 🔷 S12 | **Materias primas disponibles sin restricción.** No hay quiebres de insumos. | Fuera del alcance del modelo |
| 🔷 S13 | **Todos los hornos son equivalentes e intercambiables.** | Supuesto operacional del enunciado |
| 🔷 S14 | **Carros y bandejas suficientes.** Se modelan explícitamente pero se asume disponibilidad inicial suficiente. El reporte final indica cuántos se necesitan. | Indicado en el enunciado |

### 4.3 Split enfriado/traslado (Supuesto S8)

| Tipo | Total (min) | Enfriado (min) | Traslado a sala (min) | Recurso traslado |
|---|---|---|---|---|
| Marraqueta | 12 | 8 | 4 | Ayudante |
| Hallulla | 12 | 8 | 4 | Ayudante |
| Marraqueta Integral | 12 | 8 | 4 | Ayudante |
| Hallulla Integral | 12 | 8 | 4 | Ayudante |
| Pan Hot Dog | 12 | 8 | 4 | Ayudante |
| Ciabatta | 15 | 10 | 5 | Ayudante |
| Baguette | 15 | 10 | 5 | Ayudante |
| Dobladita | 10 | 7 | 3 | Ayudante |
| Bocado de Dama | 10 | 7 | 3 | Ayudante |
| Amasado | 12 | 8 | 4 | Ayudante |

### 4.4 Inventario objetivo para las 09:00

El perfil de demanda muestra que las primeras 3 horas (09:00–12:00) tienen demanda idéntica (~449 kg/hr). Se propone como inventario inicial al menos **1,5× la demanda de la primera hora** por tipo, para absorber variabilidad:

| Tipo | Demanda 1ª hr (kg) | Inventario objetivo 09:00 (kg) | Batches necesarios pre-apertura |
|---|---|---|---|
| Marraqueta | 126,2 | 189,3 | 4 (240 kg) |
| Hallulla | 107,3 | 160,9 | 3 (165 kg) |
| Marraqueta Integral | 50,5 | 75,7 | 2 (120 kg) |
| Hallulla Integral | 50,5 | 75,7 | 2 (110 kg) |
| Pan Hot Dog | 26,1 | 39,1 | 1 (55 kg) |
| Ciabatta | 15,1 | 22,7 | 1 (50 kg) |
| Baguette | 13,2 | 19,9 | 1 (45 kg) |
| Dobladita | 29,2 | 43,8 | 1 (50 kg) |
| Bocado de Dama | 18,3 | 27,5 | 2 (50 kg) |
| Amasado | 12,4 | 18,6 | 1 (60 kg) |
| **TOTAL** | **448,8** | **673,2** | **18 batches** |

> El ciclo más largo pre-apertura es Ciabatta/Baguette (134/133 min). Para tener stock a las 09:00, la panadería debe iniciar operaciones **no más tarde de las 06:45** (considerando ~135 min de ciclo completo).

---

## 5. Modelo Conceptual

### 5.1 Entidades del sistema

| Entidad | Descripción | Atributos |
|---|---|---|
| **Lote de producción** | Unidad que fluye por el proceso productivo | TipoPan, FamiliaHorneado, KgLote, EtapaActual, HoraInicio |
| **Corrida de horno** | Agrupación de lotes de misma familia para una carga | Familia, ListaLotes, KgTotal, NCarros, TiempoCocción |
| **Cliente** | Entidad que consume inventario en sala | NTiposAComprar, TiposSeleccionados[], KgPorTipo[], HoraLlegada |

### 5.2 Recursos

| Recurso | Tipo | Capacidad a determinar | Usado en |
|---|---|---|---|
| Panadero | Humano (turno 8h) | Variable (estudio) | Pesado, carga/retiro mezcladora, amasado manual, formado |
| Manipulador/Ayudante | Humano (turno 8h) | Variable (estudio) | Carga/descarga horno, traslado a sala |
| Mezcladora | Máquina | Variable (estudio) | Ciclo automático de mezclado |
| Amasadora | Máquina | Variable (estudio) | Amasado manual |
| Mesa de Formado | Estación | Variable (estudio) | Dividido y formado |
| Cámara Fermentación | Espacio | Capacidad ilimitada (S9) | Reposo, fermentación final |
| Horno | Máquina batch | Variable (estudio) | Horneado por familia |
| Carros | Transporte | A reportar | Transporte en horno y enfriamiento |
| Bandejas | Transporte | A reportar | Dentro de carros |

### 5.3 Variables de estado

| Variable | Tipo | Descripción |
|---|---|---|
| `Inventario[tipo]` | Continua (kg) | Stock actual en sala por tipo de pan |
| `QuiebreAcum[tipo]` | Continua (kg) | Demanda insatisfecha acumulada por tipo |
| `VentasAcum[tipo]` | Continua (kg) | Kg vendidos acumulados por tipo |
| `LotesProducidos[tipo]` | Entera | Cantidad de batches completados por tipo |
| `UltimaFamiliaHorno[horno]` | Categórica | Última familia horneada (para calcular setup) |
| `EstadoHorno[horno]` | Categórica | Libre / Cargando / Horneando / Descargando |
| `ColaHorno[familia]` | Continua (kg) | Kg acumulados esperando horno por familia |
| `TiempoEsperaHorno[familia]` | Continua (min) | Tiempo que lleva esperando la carga |

### 5.4 Eventos principales

| Evento | Disparador | Acciones |
|---|---|---|
| Inicio de jornada | Hora de inicio panadería | Inicia producción de batches pre-apertura |
| Llegada de cliente | Proceso Poisson no homogéneo | Selecciona tipos, verifica stock, registra venta o quiebre |
| Fin de mezclado | Timer (auto cycle) | Libera mezcladora, panadero retira masa |
| Fin de fermentación | Timer | Lote disponible para horno |
| Lote listo para horno | Acumulación en cola | Evalúa política de carga |
| Inicio de corrida | Política de carga/timeout | Carga horno, inicia cocción |
| Fin de horneado | Timer (14/18/21 min) | Descarga, envía a enfriamiento |
| Fin de enfriamiento | Timer | Envía a traslado |
| Reposición a sala | Ayudante disponible | Incrementa inventario en sala |
| Colación/Descanso | Calendario turno | Retira recurso temporalmente (escalonado) |
| Fin de jornada tienda | 21:00 | Cierre, calcula sobrantes |

### 5.5 Lógica de decisión

#### 5.5.1 Política de liberación de producción

```
PARA cada franja horaria:
  Calcular demanda esperada por tipo para las próximas 2-3 horas
  Calcular déficit = demanda_esperada - inventario_actual - en_proceso
  SI déficit > 0:
    Ordenar tipos por déficit descendente
    Liberar batches de producción según prioridad
```

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

#### 5.5.4 Lógica de compra del cliente

```
LLEGADA de cliente a sala:
  Determinar N_tipos ~ Discrete(1:50%, 2:35%, 3:15%)
  PARA i = 1 hasta N_tipos:
    Seleccionar tipo según P(tipo|hora) condicional (sin reemplazo)
    Cantidad = Triangular(min, moda, max) según tipo
    SI Inventario[tipo] >= Cantidad:
      Inventario[tipo] -= Cantidad
      Registrar venta
    SINO:
      Registrar quiebre (toda la cantidad se pierde) ← 🔶 S5
```

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
LLEGADA CLIENTE (Poisson no homogéneo, tasa por hora)
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

| Etapa | Panadero | Manipulador | Mezcladora | Amasadora | Mesa | Horno |
|---|---|---|---|---|---|---|
| Pesado y dosificación | ✅ | | | | | |
| Carga mezcladora | ✅ | | ✅ | | | |
| Mezclado automático | | | ✅ | | | |
| Retiro de masa | ✅ | | ✅ | | | |
| Amasado manual | ✅ | | | ✅ | | |
| Reposo en masa | | | | | | |
| Dividido y formado | ✅ | | | | ✅ | |
| Fermentación final | | | | | | |
| Carga horno | | ✅ | | | | ✅ |
| Horneado | | | | | | ✅ |
| Descarga horno | | ✅ | | | | ✅ |
| Enfriado | | | | | | |
| Traslado a sala | | ✅ | | | | |

#### Tabla L2: Compatibilidad de familias en horno

| Corrida \ Familia | Fam 1 (14m) | Fam 2 (18m) | Fam 3 (21m) |
|---|---|---|---|
| Fam 1 (14m) | ✅ Sin setup | ❌ + 5 min setup | ❌ + 5 min setup |
| Fam 2 (18m) | ❌ + 5 min setup | ✅ Sin setup | ❌ + 5 min setup |
| Fam 3 (21m) | ❌ + 5 min setup | ❌ + 5 min setup | ✅ Sin setup |

#### Tabla L3: Política de carga del horno

| Condición | Acción |
|---|---|
| Cola familia ≥ 600 kg | Cargar horno (hasta 1200 kg), iniciar corrida |
| Cola familia < 600 kg Y espera < 15 min | Seguir esperando acumulación |
| Cola familia < 600 kg Y espera ≥ 15 min | Iniciar corrida anticipada con carga disponible |
| Horno ocupado | Lote espera en cola |
| Manipulador no disponible | Horno no puede iniciar carga/descarga (tiempo ocioso) |

---

## 6. Nivel de Detalle Adecuado

### 6.1 Unidades de modelación

| Aspecto | Nivel de detalle | Justificación |
|---|---|---|
| **Demanda** | Cliente individual | Permite modelar comportamiento estocástico (N tipos, cantidad triangular, selección condicional, todo-o-nada) |
| **Producción** | Lote (batch) | Unidad natural del proceso; tamaño fijo por tipo (25-60 kg) |
| **Inventario** | Continuo en kg por tipo | 10 SKUs independientes, descontados por cada compra |
| **Horno** | Corrida (batch de familia) | Agrupa múltiples lotes de producción de misma familia (hasta 1200 kg) |
| **Tiempo** | Minutos | Resolución suficiente para todas las operaciones (mín. 1 min) |
| **Recursos humanos** | Individual con calendario | Cada trabajador tiene turno, colación y descansos escalonados |
| **Carros/bandejas** | Conteo explícito | Necesario para reportar cantidad requerida |

### 6.2 Análisis de carga de recursos (justificación del nivel de detalle)

#### Mezcladora — CUELLO DE BOTELLA IDENTIFICADO

| Métrica | Valor |
|---|---|
| Tiempo ocupado por batch | 13-18 min (carga 2 + auto 10-15 + retiro 1) |
| Total batches/día | 155 |
| Total mezcladora-min/día | **2.442 min (40,7 hrs)** |
| Con 1 mezcladora (16 hrs) | **254% utilización → INSUFICIENTE** |
| Con 2 mezcladoras | 127% → INSUFICIENTE |
| Con 3 mezcladoras | 85% → VIABLE |

> **Hallazgo crítico**: La mezcladora es el recurso más restrictivo del sistema. Se requieren **mínimo 3 mezcladoras** para la producción diaria.

#### Panadero

| Métrica | Valor |
|---|---|
| Tiempo hands-on por batch | 16-20 min (pesado + carga + retiro + formado) |
| Total panadero-min/día (sin amasado manual) | 2.926 min (48,8 hrs) |
| Tiempo productivo neto por turno | 405 min (6h 45m) |
| Mínimo panaderos (turno único) | ⌈48,8 / 6,75⌉ = **8 panaderos** |
| Con amasado manual (+50% mezclado) | ~3.600 min → **9 panaderos** |

#### Horno

| Métrica | Valor |
|---|---|
| Corridas totales/día | 9 (mínimo teórico) |
| Tiempo total horno (sin setup) | 250 min (4,2 hrs) |
| Tiempo total horno (con setup) | 295 min (4,9 hrs) |
| Con 1 horno (16 hrs disponibles) | **31% utilización → 1 horno suficiente en teoría** |

> **Nota**: Aunque 1 horno basta en volumen agregado, la restricción operativa es el **timing**: la producción debe distribuirse durante el día para evitar quiebres, especialmente antes del peak de 18:00–20:00. Probablemente se necesiten **2 hornos** para flexibilidad de secuenciamiento.

#### Manipulador/Ayudante

| Métrica | Valor |
|---|---|
| Carga/descarga horno | 9 corridas × 10 min = 90 min |
| Traslado a sala | 155 batches × ~4 min = 620 min |
| Total manipulador-min/día | **710 min (11,8 hrs)** |
| Mínimo manipuladores (turno único) | ⌈11,8 / 6,75⌉ = **2 manipuladores** |

### 6.3 Elementos que NO requieren modelado detallado

| Elemento | Nivel de abstracción | Razón |
|---|---|---|
| Cámaras de fermentación | Capacidad ilimitada (delay simple) | No se espera que sean cuello de botella (supuesto S9) |
| Composición de ingredientes | No modelado | No afecta tiempos ni capacidad |
| Calidad del producto | No modelado | Fuera de alcance |
| Layout físico de la panadería | No modelado | Tiempos de transporte incluidos en etapas |
| Fallas de equipo | No modelado | Supuesto del enunciado |

### 6.4 Resumen de recursos mínimos estimados (punto de partida para experimentación)

| Recurso | Mínimo estimado | Notas |
|---|---|---|
| Mezcladoras | 3 | Cuello de botella principal |
| Amasadoras | 2-3 | Depende del tiempo de amasado manual (S6) |
| Mesas de formado | 2-3 | Paralelo con mezcladoras |
| Hornos | 1-2 | 1 basta en volumen; 2 para flexibilidad temporal |
| Panaderos | 8-9 por turno | Requiere 2+ turnos traslapados |
| Manipuladores | 2 por turno | Con turnos traslapados |
| Carros | ~20-30 en circulación | 2 carros/batch × batches simultáneos |
| Bandejas | ~400-500 | ~27 bandejas/batch promedio × batches simultáneos |

---

## Anexo A: Validación de datos de entrada

### A.1 Perfil de demanda horaria

Se verificó que la suma de la demanda horaria por tipo coincide con la demanda diaria declarada:

| Tipo | Suma perfil (kg) | Esperado (kg) | Δ |
|---|---|---|---|
| Marraqueta | 2.000,0 | 2.000 | −0,02 |
| Hallulla | 1.700,0 | 1.700 | −0,03 |
| Marraqueta Integral | 800,0 | 800 | +0,01 |
| Hallulla Integral | 800,0 | 800 | +0,01 |
| Pan Hot Dog | 1.200,0 | 1.200 | +0,01 |
| Ciabatta | 400,0 | 400 | −0,02 |
| Baguette | 350,0 | 350 | +0,01 |
| Dobladita | 350,0 | 350 | +0,04 |
| Bocado de Dama | 220,0 | 220 | −0,04 |
| Amasado | 380,0 | 380 | +0,00 |

**Resultado**: ✅ Datos consistentes (diferencias < 0,05 kg por redondeo).

### A.2 Probabilidades de elección

Se verificó que las probabilidades suman 1,0 en cada franja:

| Franja | Suma P |
|---|---|
| Todas las franjas | 0,99998 – 1,00001 |

**Resultado**: ✅ Consistentes (error < 0,00002 por redondeo).

### A.3 Regímenes de demanda identificados

La demanda NO sigue una distribución uniforme ni normal a lo largo del día. Se identifican **3 regímenes discretos**:

| Régimen | Horas | Kg/hr promedio | % del día |
|---|---|---|---|
| **Bajo** | 09-12, 15-17, 20-21 | ~451 | 33% |
| **Medio** | 12-15, 17-18 | ~657 | 32% |
| **Alto** | 18-20 | ~1.434 | **35%** |

> La demanda horaria se modela mejor como un **perfil escalonado no homogéneo** (step function) que como una distribución continua. Cada producto tiene entre 1 y 7 tasas horarias distintas.

---

## Anexo B: Referencias a archivos fuente

| Archivo | Contenido | Validado |
|---|---|---|
| `parametros_proceso_panaderia.csv` | Tiempos por etapa, tamaño de lote, temperatura, capacidad carro | ✅ |
| `perfil_demanda_por_hora_panaderia.csv` | Kg demandados por hora por tipo de pan | ✅ |
| `probabilidades_eleccion_por_hora.csv` | P(elegir tipo i) por franja horaria | ✅ |
| `flujo/bpmn_panaderia.drawio` | Diagrama BPMN 2.0 completo (Draw.io) | ✅ |
| `flujo/diagrama_bpmn_panaderia.md` | Documentación Mermaid del BPMN | ✅ |
