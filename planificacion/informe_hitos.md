# Informe de Hitos — Capstone Simulación Panadería (SIMIO)

> **Proyecto:** Modelación y análisis mediante simulación de eventos discretos de una panadería de supermercado  
> **Horizonte:** Martes 21 de Abril — Miércoles 20 de Mayo de 2026 (~22 días hábiles)  
> **Metodología:** 14 pasos de desarrollo de simulación (referencia del curso)

---

## Resumen Ejecutivo

El proyecto se estructura en **6 hitos** que marcan puntos de control progresivos a lo largo de 5 semanas. Cada hito agrupa actividades de la metodología de simulación y establece un entregable verificable antes de avanzar a la siguiente fase. Este enfoque secuencial-iterativo asegura que no se invierta esfuerzo en implementación sin tener primero una base conceptual sólida, ni se documenten resultados sin haberlos validado.

---

## HITO 1 — Definición del Problema y Alcance Completados

| Atributo | Detalle |
|---|---|
| **Semana** | Semana 1 (21–25 Abril) |
| **Pasos metodológicos** | 1. Problema → 2. Sistema |
| **Entregable** | Documento de alcance con objetivos, criterios y límites del sistema |

### Propósito

Establecer con total claridad **qué se quiere responder** con el modelo de simulación y **qué parte de la realidad** quedará representada. Esto incluye:

- Definir las preguntas centrales: ¿cuántos panaderos, ayudantes, hornos y máquinas se requieren? ¿Qué política de producción conviene?
- Fijar el criterio de evaluación principal (minimizar quiebres de stock, maximizar nivel de servicio, etc.)
- Delimitar los subsistemas **dentro** del modelo (producción, hornos, RRHH, inventario, demanda) y los que quedan **fuera** (compras de MP, fallas eléctricas, mantenimiento mayor)

### Aporte al Proyecto

Sin esta definición, el modelo corre el riesgo de volverse **difuso** o innecesariamente complejo. Al cerrar este hito, el equipo tiene un marco de referencia compartido que guía todas las decisiones posteriores de modelamiento. La delimitación del sistema evita que se modelen elementos que no aportan a las preguntas de negocio.

### Actividades

| # | Actividad | Días |
|---|---|---|
| 1.1 | Definir elementos, objetivos y criterios de evaluación | Ma 21 – Mi 22 |
| 1.2 | Delimitar alcance: subsistemas dentro y fuera del modelo | Mi 22 – Ju 23 |

---

## HITO 2 — Base de Datos y Supuestos Formalizados

| Atributo | Detalle |
|---|---|
| **Semana** | Semana 1–2 (Ju 24 Abr – Mi 30 Abr) |
| **Pasos metodológicos** | 3. Datos → 4. Supuestos |
| **Entregable** | Tablas de parámetros validadas + documento de supuestos explícitos |

### Propósito

Reunir, organizar y verificar la **consistencia de toda la información** necesaria para construir el modelo, y documentar las **decisiones de simplificación**. Esto cubre:

- Parámetros de proceso por tipo de pan (tiempos de etapa, tamaños de lote, capacidades)
- Perfiles de demanda horaria y probabilidades de elección por tipo de pan
- Reglas de composición de compra por cliente (distribuciones triangulares)
- Supuestos explícitos: ¿demanda por cliente individual o agregada? ¿Tiempos determinísticos o estocásticos? ¿Enfriamiento con capacidad limitada?

### Aporte al Proyecto

Los datos son la **materia prima** del modelo. Si se trabaja con datos inconsistentes, los resultados carecerán de validez. Los supuestos explícitos permiten que cualquier revisor entienda las simplificaciones aplicadas. Este hito actúa como **punto de no retorno** antes de invertir tiempo en diseño e implementación.

### Actividades

| # | Actividad | Días |
|---|---|---|
| 2.1 | Recolectar y organizar parámetros de proceso (archivos xlsx) | Ju 24 – Lu 28 |
| 2.2 | Organizar perfiles de demanda y probabilidades de elección | Vi 25 – Ma 29 |
| 2.3 | Formular y documentar supuestos explícitos del modelo | Ma 29 – Mi 30 |

---

## HITO 3 — Modelo Conceptual Validado y Nivel de Detalle Definido

| Atributo | Detalle |
|---|---|
| **Semana** | Semana 2–3 (Mi 30 Abr – Ma 6 May) |
| **Pasos metodológicos** | 5. Modelo conceptual → 6. Nivel de detalle |
| **Entregable** | Diagramas BPMN/flujo + tablas de lógica + definición de granularidad |

### Propósito

Construir una **representación abstracta del sistema** antes de tocar el software:

- Definir las **entidades** (lotes de pan, clientes), **recursos** (panaderos, manipuladores, hornos, mezcladoras, amasadoras), **colas**, **variables de estado** (inventario por tipo) y **eventos** (llegada de cliente, inicio de horneado)
- Crear **diagramas de flujo y BPMN** que mapean el ciclo de vida completo: desde pesado de ingredientes hasta reposición en sala
- Definir la **granularidad**: demanda a nivel de cliente individual, producción por lote, inventario continuo en kg

### Aporte al Proyecto

El modelo conceptual es el **plano arquitectónico** de la simulación. Implementar sin un modelo conceptual claro lleva a errores de lógica difíciles de detectar y retrabajo costoso. Al definir el nivel de detalle adecuado, se asegura que el modelo sea suficientemente detallado para responder las preguntas, pero no tan complejo que se vuelva inmanejable.

### Actividades

| # | Actividad | Días |
|---|---|---|
| 3.1 | Definir entidades, recursos, colas, variables de estado y eventos | Mi 30 – Ju 1 |
| 3.2 | Crear diagramas de flujo / BPMN y tablas de lógica de decisión | Ju 1 – Lu 5 |
| 3.3 | Definir granularidad: cliente, lote, kg continuo | Vi 2 – Ma 6 |

---

## HITO 4 — Modelo SIMIO Implementado y Funcional

| Atributo | Detalle |
|---|---|
| **Semana** | Semana 3–4 (Ma 6 May – Mi 14 May) |
| **Pasos metodológicos** | 7. Implementación (construcción modular en SIMIO) |
| **Entregable** | Modelo SIMIO ejecutable con todos los módulos integrados |

### Propósito

Traducir el modelo conceptual al software SIMIO mediante una **construcción modular progresiva** de 5 módulos:

1. **Módulo Inventario + Demanda:** Sala de ventas con stock por tipo de pan y llegada de clientes con lógica de compra (1–3 tipos, distribución triangular)
2. **Módulo Producción:** Línea completa pesado → mezclado → amasado → fermentación → formado → fermentación final
3. **Módulo Horno:** Lógica batch con 3 familias (14/18/21 min), setup entre familias, carga mínima 50%, enfriamiento
4. **Módulo RRHH:** Panaderos y manipuladores con jornadas 8h, colaciones 45 min, descansos 15 min, escalonamiento
5. **Módulo Políticas:** Secuencia de producción y reposición a sala

### Aporte al Proyecto

La construcción modular permite detectar errores tempranamente en cada módulo antes de integrar, reduce bloqueos lógicos y facilita la distribución de trabajo. Este hito representa el **mayor esfuerzo** del proyecto (~8 días) y su completitud exitosa determina la factibilidad del resto.

### Actividades

| # | Actividad | Días |
|---|---|---|
| 4.1 | Módulo 1 — Inventario + demanda por cliente | Ma 6 – Ju 8 |
| 4.2 | Módulo 2 — Línea de producción | Mi 7 – Vi 9 |
| 4.3 | Módulo 3 — Horno batch | Ju 8 – Lu 12 |
| 4.4 | Módulo 4 — RRHH, turnos, descansos | Vi 9 – Ma 13 |
| 4.5 | Módulo 5 — Políticas de secuencia y reposición | Lu 12 – Mi 14 |

---

## HITO 5 — Modelo Verificado, Validado y Experimentación Completada

| Atributo | Detalle |
|---|---|
| **Semana** | Semana 4 (Ma 13 – Vi 16 May) |
| **Pasos metodológicos** | 8. Verificación → 9. Validación → 10. Experimentos → 11. Ejecución → 12. Sensibilidad |
| **Entregable** | Modelo V&V aprobado + resultados de todos los escenarios experimentales |

### Propósito

Asegurar que el modelo está **correctamente construido** y que **representa adecuadamente** el sistema, para luego ejecutar los experimentos:

- **Verificación:** Revisar lógica, flujos, asignación de recursos, animación, corridas de prueba
- **Validación:** Comparar resultados con magnitudes esperadas y coherencia de KPIs
- **Diseño experimental:** Definir escenarios, factores, réplicas, warm-up
- **Ejecución:** Correr escenarios y recopilar los 14+ indicadores de desempeño
- **Sensibilidad:** Probar variaciones de demanda, mix de productos, capacidad

### Aporte al Proyecto

Sin V&V, los resultados carecen de **credibilidad**. La experimentación estructurada permite comparar escenarios de forma rigurosa. El análisis de sensibilidad revela la **robustez** de las soluciones propuestas frente a variaciones en los parámetros de entrada.

### Actividades

| # | Actividad | Días |
|---|---|---|
| 5.1 | Revisar lógica, flujos, animación, corridas de prueba | Ma 13 – Mi 14 |
| 5.2 | Comparar magnitudes esperadas, coherencia KPIs | Mi 14 – Ju 15 |
| 5.3 | Definir escenarios, factores, réplicas, warm-up | Ju 15 – Vi 16 |
| 5.4 | Correr escenarios y recopilar resultados | Vi 16 – Lu 18 |
| 5.5 | Probar variaciones de demanda, capacidad, mix | Vi 16 – Lu 18 |

---

## HITO 6 — Entrega Final: Modelos SIMIO + Informes

| Atributo | Detalle |
|---|---|
| **Semana** | Semana 5 (Lu 18 – Mié 20 May) |
| **Pasos metodológicos** | 13. Decisiones → 14. Documentación |
| **Entregable** | Modelo SIMIO ejecutable + Informe Técnico + Informe Académico + Anexos |

### Propósito

Transformar los resultados en **decisiones accionables** para la gerencia y consolidar toda la documentación:

- **Decisiones:** ¿Conviene agregar un horno o un panadero? ¿La restricción principal está en fermentación o en hornos? ¿Qué política de secuenciamiento es óptima?
- **Informe Técnico (Gerencia):** Resultados, análisis, recomendación final de capacidad y política
- **Informe Académico:** Proceso de desarrollo, justificación de decisiones, dificultades, reflexiones, anexos
- **Documentación transversal:** Registro continuo del proceso (actividad 6.4, ejecutada cada viernes del proyecto)

### Aporte al Proyecto

La documentación da **trazabilidad** al estudio y permite que otros entiendan, repliquen y evalúen el trabajo. La actividad transversal asegura que no se acumule todo el esfuerzo de escritura al final.

### Actividades

| # | Actividad | Días |
|---|---|---|
| 6.1 | Interpretar resultados, cuellos de botella, recomendaciones | Lu 18 – Ma 19 |
| 6.2 | Informe técnico (gerencia) | Ma 19 – Mi 20 |
| 6.3 | Informe académico + anexos | Ma 19 – Mi 20 |
| 6.4 | Documentación transversal (cada viernes) | Transversal |

---

## Tabla de Correspondencia: Metodología ↔ Hitos

| Paso | Descripción | Hito |
|---|---|---|
| 1. Problema | Definir elementos y objetivos | H1 |
| 2. Sistema | Delimitar alcance | H1 |
| 3. Datos | Recolectar y organizar | H2 |
| 4. Supuestos | Simplificar realidad | H2 |
| 5. Modelo conceptual | Lógica del sistema | H3 |
| 6. Nivel de detalle | Unidad de modelación | H3 |
| 7. Implementación | Construir en SIMIO | H4 |
| 8. Verificación | ¿Funciona correctamente? | H5 |
| 9. Validación | ¿Representa la realidad? | H5 |
| 10. Experimentos | Definir escenarios | H5 |
| 11. Ejecución | Correr simulación | H5 |
| 12. Sensibilidad | Probar variaciones | H5 |
| 13. Decisiones | Conclusiones | H6 |
| 14. Documentación | Registrar proceso | H6 |

---

> [!TIP]
> La **Carta Gantt interactiva** está disponible en [gantt_chart.html](file:///home/dacmxo/Desktop/udd/Capstone_simio/gantt_chart.html). Ábrela en el navegador para ver la vista completa semana a semana con barras por actividad y diamantes por hito.
