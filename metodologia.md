## METODOLOGÍA PARA DESARROLLAR UNA SOLUCIÓN MEDIANTE SIMULACIÓN

Esta es una referencia de los pasos que normalmente habría que realizar para lograr el desarrollo de un modelo de simulación y el correspondiente análisis, contextualizado al caso visto en el curso. Debe transformarse en un plan específico de desarrollo, con pasos, responsables y recursos.

## 1. Definir el problema y el propósito del estudio

Lo primero es dejar completamente claro qué se quiere responder con el modelo.
En un caso como éste, las preguntas centrales son del tipo:

* cuántos panaderos, ayudantes, hornos y máquinas se requieren,
* en qué horario debe operar la panadería,
* qué política de producción conviene usar,
* y qué combinación permite minimizar quiebres de stock con un uso razonable de recursos.

En esta etapa también debe definirse el criterio principal de evaluación. Por ejemplo:

* minimizar quiebres de stock,
* maximizar nivel de servicio,
* minimizar costo,
* o buscar el menor costo que cumpla cierto nivel de servicio.

Si esta etapa queda mal definida, todo el estudio se vuelve difuso.

## 2. Delimitar el sistema

Luego se debe fijar qué parte de la realidad quedará dentro del modelo y qué quedará fuera.

En este caso, dentro del sistema deberían quedar al menos:

* la producción de pan,
* la operación de hornos,
* los recursos humanos,
* la reposición a sala,
* el inventario disponible para venta,
* y la demanda de clientes.

Y fuera del sistema podrían quedar, por ejemplo:

* compras de materias primas,
* transporte externo,
* fallas eléctricas,
* mantenimiento mayor,
* ventas de otros productos del supermercado.

Esta delimitación evita que el modelo se vuelva innecesariamente grande.

## 3. Levantar y organizar la información

Aquí se reúne toda la información necesaria para modelar.
Esto incluye:

* tipos de pan,
* tiempos de proceso por etapa,
* tamaños de lote,
* capacidades por carro, bandeja y horno,
* horario de operación,
* demanda diaria y perfil horario,
* reglas de compra de clientes,
* turnos del personal,
* tiempos de carga y descarga,
* tiempos de setup,
* reglas de compatibilidad de horno.

En esta etapa no basta con recopilar datos: hay que ordenarlos y revisar su consistencia.

## 4. Formular supuestos explícitos

Siempre habrá información faltante o decisiones de simplificación. Esas decisiones deben hacerse explícitas.

Ejemplos típicos en este caso:

* si la demanda se modelará por clientes individuales o agregada por intervalo,
* si se consideran tiempos determinísticos o distribuciones donde no se especifíca,
* si el enfriamiento tiene capacidad limitada,
* si los panes no vendidos al final del día se pierden o se descartan.

## 5. Construir el modelo conceptual

Antes del software, debe hacerse un modelo conceptual del sistema.
Aquí se define:

* entidades,
* recursos,
* colas,
* variables de estado,
* eventos,
* lógica de decisión,
* entradas y salidas del sistema.

Este modelo conceptual normalmente se representa con:

* diagramas de flujo,
* tablas de lógica,
* y descripción narrativa del sistema.

## 6. Definir el nivel de detalle adecuado

No todo debe modelarse con el mismo detalle, es decir, se debe elegir la unidad de modelación.

Por ejemplo:

* demanda a nivel cliente,
* producción por lote,
* inventario continuo en kg .

La idea es usar el nivel de detalle suficiente para responder la pregunta, sin sobrecargar el modelo.

## 7. Traducir el modelo conceptual al software

Recién aquí se comienza la implementación en SIMIO. La construcción debe hacerse por módulos, no todo de una vez.

Ejemplo:

1. modelar inventarios y demanda,
2. modelar una línea simple de producción,
3. incorporar recursos humanos,
4. agregar el horno y su lógica batch,
5. agregar políticas de control,
6. incorporar turnos y descansos,
7. activar indicadores y reportes.

Esto permite detectar errores antes de que el modelo sea demasiado complejo.

## 8. Verificar el modelo

La verificación responde a la pregunta: ¿el modelo fue construido correctamente?
Aquí se revisa:

* que la lógica implementada coincida con la lógica diseñada,
* que los flujos sigan el orden correcto,
* que los recursos se asignen como corresponde,
* que los tiempos y colas sean razonables,
* que no existan entidades “perdidas” ni bloqueos inesperados.

Herramientas típicas:

* animación,
* rastreo de entidades,
* revisión de colas,
* chequeo de eventos,
* corridas de prueba con casos muy pequeños.

Verificar no significa validar contra la realidad; significa revisar que el modelo esté bien programado.

## 9. Validar el modelo

La validación responde a otra pregunta: ¿el modelo representa de manera aceptable el sistema real o el sistema propuesto?

En un caso académico, la validación puede apoyarse en:

* coherencia lógica de resultados,
* comparación con órdenes de magnitud esperadas,
* contrastes con datos históricos si existen,
* análisis de sensibilidad.

Por ejemplo:

* si el horno aparece siempre $5 \%$ utilizado y hay quiebres masivos, probablemente algo está mal;
* si con mayor capacidad empeora todo, hay que revisar la lógica.

## 10. Diseñar los experimentos

Una vez que el modelo funciona, se define cómo se lo usará para experimentar.
Esto implica decidir:

* escenarios a comparar,
* factores de decisión,
* niveles de cada factor,
* horizonte de simulación,
* número de replicaciones,
* periodo de warm-up, si aplica,
* medidas de desempeño.

En este problema, factores típicos son:

* número de panaderos,
* número de ayudantes,
* número de hornos,
* número de máquinas,
* política de liberación de producción,
* política de secuenciamiento del horno,
* hora de inicio de operación.

## 11. Ejecutar el análisis experimental

Aquí se corren los escenarios definidos y se recopilan resultados.
Los indicadores deberían incluir, además de los indicados en el enunciado, otros tales como:

* quiebres de stock por tipo,
* kg no vendidos,
* porcentaje de demanda satisfecha,
* sobrantes al final del día,
* utilización de recursos,
* número de lotes,
* tiempo promedio de ciclo,
* tiempo en cola,
* ocupación del horno,
* frecuencia de setups.

En esta etapa no basta con mirar un valor aislado. Hay que comparar escenarios y entender relaciones causa-efecto.

## 12. Analizar sensibilidad y robustez

Una solución no debería evaluarse sólo en el escenario “promedio”.
Es importante analizar qué pasa si cambian:

* la demanda,
* el mix de productos,
* los tiempos de proceso,
* los descansos,
* los puntos de reposición,
* o la capacidad de horno.

Esto permite saber si una política sigue siendo buena bajo distintas condiciones.

## 13. Interpretar resultados y formular recomendaciones

La simulación no termina al obtener números; termina cuando esos números se traducen en decisiones.

Por ejemplo:

* si conviene agregar un horno o un panadero,
* si la restricción principal está en fermentación o en hornos,
* si el problema se resuelve mejor con capacidad o con mejor secuenciamiento,
* si la panadería debe comenzar a operar más temprano,
* o si ciertos tipos de pan deberían producirse en lotes distintos.

Aquí es donde la simulación se convierte en apoyo real a la toma de decisiones.

## 14. Documentar el estudio

Un estudio bien hecho debe dejar trazabilidad completa.
La documentación debería incluir:

* problema y objetivos,
* alcance,
* datos utilizados,
* supuestos,
* modelo conceptual,
* lógica implementada,
* verificación y validación,
* experimentos,
* resultados,
* conclusiones,
* limitaciones,
* y recomendaciones.
