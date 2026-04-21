## Modelación y análisis mediante simulación de eventos discretos de una panadería de supermercado con múltiples tipos de pan, recursos compartidos y riesgo de quiebre de stock

## I. Contexto

Un supermercado opera una panadería propia que abastece durante el día una zona de ventas de autoservicio. La panadería produce diariamente 10 tipos de pan frescos:

1. Marraqueta
2. Hallulla
3. Marraqueta Integral
4. Hallulla Integral
5. Pan Hot Dog
6. Ciabatta
7. Baguette
8. Dobladita
9. Bocado de Dama
10. Amasado

El supermercado atiende público entre 09:00 y 21:00 horas, pero la panadería debe comenzar antes de la apertura para que a las 09:00 exista disponibilidad inicial de todos los productos. Durante la operación, la panadería debe producir, hornear, enfriar y reponer pan hacia la sala de ventas con el fin de minimizar los quiebres de stock. Se supone que cuando un cliente no encuentra el tipo de pan que desea, la venta se pierde; no hay sustitución por otro tipo de pan.

La jefatura del supermercado ha observado que existe un alto nivel de quiebre de stock, que ha originado muchas quejas por parte de los clientes, y han decidido hacer un rediseño completo de la sección para lograr tener un buen nivel de servicio, ya que son conscientes que el pan fresco atrae clientes y de paso eleva las ventas de los restantes productos del supermercado. Así, necesitan definir:

* cuántos trabajadores se requieren, considerando turnos de trabajo (que pueden sobreponerse) dada la extensión de tiempo de operación de la panadería.
* qué combinación de trabajadores conviene usar, distinguiendo al menos entre panaderos y manipuladores de hornos / apoyo de despacho,
* cuántos hornos son necesarios,
* cuántas máquinas de proceso se requieren, considerando amasadoras y mezcladoras,
* En qué horario debería operar la panadería,
* y cuál debiera ser la secuencia de producción más conveniente para reducir pérdidas por quiebre de stock.

Lógicamente, interesa conocer el número mínimo necesario de todos estos recursos, que logre un buen nivel de servicio, porque todos ellos implican costos.

## II. Alcance del modelo

El archivo “parametros_proceso_panaderia.xlsx” contiene los tiempos de cada etapa del proceso de fabricación por tipo de pan, además de otra información útil para el modelamiento.

El modelo debe representar, como mínimo, los siguientes subsistemas:

## A. Producción

Cada tipo de pan debe recorrer etapas de producción que incluyan, según corresponda:

* pesado y dosificación de ingredientes. Esto se hace manualmente por el panadero. En el archivo “parametros_proceso_panaderia.xlsx” se indica el tamaño de lote que se procesa cada vez que se prepara un tipo de pan, que está limitado por las capacidades de la mezcladora.
* mezclado: El panadero ingresa los ingredientes ( 2 minutos), y luego la máquina opera en ciclo automático (que es el tiempo indicado). Luego el panadero retira la masa y la lleva a amasado (1 minuto).
* Amasado: Operación manual hecha por el panadero.
* reposo o fermentación en masa, sin intervención de personas.
* dividido y formado, realizada por el panadero.
* fermentación final, sin intervención de personas,
* horneado, automático,
* enfriado, sin intervención de personas,
* traslado o reposición a la zona de ventas, realizado por los ayudantes.

## B. Recursos

El sistema contará con recursos limitados:

* Panaderos, responsables de preparación, amasado, formado y apoyo general.
* Manipuladores de hornos / despacho, responsables de cargar y descargar hornos, mover carros/bandejas y reponer pan a sala.
* Mezcladoras
* Amasadoras
* Mesas o estaciones de formado
* Cámaras de fermentación o capacidad de espera controlada
* Hornos
* Carros, bandejas o racks.

Las cantidades de cada recurso las debe determinar el estudio, según los objetivos planteados.

## C. Inventario en sala de ventas

La zona de ventas debe modelarse como un inventario por tipo de pan. La demanda de clientes reduce ese stock. Si el inventario de un producto llega a cero, se registra un quiebre de stock y la demanda no satisfecha se pierde.

## D. Turnos de trabajo

Los trabajadores de todo tipo tienen jornadas de 8 horas diarias de trabajo efectivo. Los turnos pueden ser traslapados entre distintas personas, y no necesariamente comienzan a horas específicas, sino que en los momentos más convenientes para los objetivos operacionales planteados.

Además, cuentan con 45 minutos para una colación, y dos periodos extra de descanso de 15 minutos. Las salidas a colación y descanso no son simultáneas, sino que deben ser escalonadas, asegurando que al menos una persona de cada función está presente en todo momento.

## E. Demanda

Los clientes llegan al supermercado de manera no uniforme durante el día. Los clientes de panadería siguen el mismo patrón horario general del supermercado, pero cada tipo de pan presenta además un comportamiento particular de demanda.

## 1. Información de demanda diaria

Se espera la siguiente demanda total por día:

* Marraqueta: $\mathbf{2.000 ~ kg} \boldsymbol{/} \mathbf{d i a}$
* Hallulla: $\mathbf{1 . 7 0 0 ~ k g / d i  a}$
* Marraqueta Integral: $\mathbf{8 0 0 ~ k g} \boldsymbol{/} \mathbf{d i a}$
* Hallulla Integral: $\mathbf{8 0 0 ~ k g} \boldsymbol{/} \mathbf{d i a}$
* Pan Hot Dog: $\mathbf{1 . 2 0 0 ~ k g / d i a}$
* Ciabatta: $\mathbf{4 0 0 ~ k g} /$ día
* Baguette: $\mathbf{3 5 0 ~ k g} \boldsymbol{/} \mathbf{d i a}$
* Dobladita: $\mathbf{3 5 0 ~ k g} \boldsymbol{/} \mathbf{d i a}$
* Bocado de Dama: 220 kg/día
* Amasado: $\mathbf{3 8 0 ~ k g} \boldsymbol{/} \mathbf{d i a}$

Demanda total de la sección: $\mathbf{8 . 2 0 0}$ kg/día.

Los kilos esperados de demanda por hora durante el día y por tipo de pan están en el archivo “perfil_demanda_por_hora_panaderia.xlsx”. Esto fue determinado considerando la moda de demanda de cada compra por cada tipo de pan y la cantidad de clientes que lo compraba de manera histórica.

## 2. Composición de compra por cliente

Un cliente que compra pan:

* en $50 \%$ de los casos compra 1 tipo de pan
* en $35 \%$ de los casos compra 2 tipos diferentes de pan
* en $15 \%$ de los casos compra 3 tipos diferentes de pan.

La cantidad comprada por tipo de pan se modelará con una distribución triangular entre $\mathbf{0 , 3 ~ k g}$ y $\mathbf{2 , 0 ~ k g}$, salvo las excepciones que se indican, y con moda distinta según producto:

* Marraqueta: moda $1,0 \mathrm{~kg}$
* Hallulla: moda $1,0 \mathrm{~kg}$
* Marraqueta Integral: moda $0,5 \mathrm{~kg}$
* Hallulla Integral: moda $0,7 \mathrm{~kg}$, con máximo 1.5 Kg .
* Pan Hot Dog: moda $1,0 \mathrm{~kg}$, con máximo 3 Kg .
* Ciabatta: moda $0,5 \mathrm{~kg}$, con máximo 1.5 Kg .
* Baguette: moda $0,5 \mathrm{~kg}$, con máximo 1 Kg
* Dobladita: moda $0,5 \mathrm{~kg}$, con máximo $1,5 \mathrm{Kg}$
* Bocado de Dama: moda $0,5 \mathrm{~kg}$, con máximo 1 Kg
* Amasado: moda 0,8 kg

El archivo “probabilidades_eleccion_por_hora.xlsx” le facilita la vida, ya que indica por cada hora la probabilidad de elección del primer tipo de pan que el cliente escoge. Debe considerar sobre esta elección las probabilidades de que escoja un segundo o hasta tercer tipo de pan, diferentes a los ya escogidos, siguiendo las misas proporciones de probabilidad de decisión.

## III. Operación de Hornos y Proceso de Horneado

Cada producto debe tener tiempos distintos de preparación y cocción. Para ello, se entrega el archivo “parametros_proceso_panaderia.xlsx”, donde se indica por tipo de pan:

* familia de proceso,
* etapas secuenciales,
* tiempos de cada etapa,
* tamaño de lote de referencia,
* temperatura de horneado de referencia,
* y capacidad referencial por carro o carga.

## A. Descripción general del Proceso Productivo

La panadería cuenta con hornos industriales tipo piso o rotativos utilizados para la cocción de todos los tipos de pan. Estos hornos operan en modo batch (por corridas), es decir, cada ciclo de operación consiste en cargar el horno, ejecutar el proceso de cocción y luego descargar completamente su contenido antes de iniciar una nueva corrida.

## B. Familias de horneado

Los 10 tipos de pan se agrupan en tres familias de horneado, según su tiempo de cocción:

## Familia 1: Horneado corto (14 minutos)

* Pan Hot Dog
* Dobladita
* Bocado de Dama

## Familia 2: Horneado medio (18 minutos)

* Marraqueta
* Hallulla
* Hallulla Integral
* Amasado

## Familia 3: Horneado largo (21 minutos)

* Marraqueta Integral
* Ciabatta
* Baguette

## C. Restricción de compatibilidad

Durante una corrida de horno: Sólo pueden hornearse simultáneamente productos pertenecientes a la misma familia de horneado.

Esto implica que:

* No se permite mezclar productos de distintas familias en una misma carga.
* Cada corrida del horno está asociada a un único tiempo de cocción (14, 18 o 21 minutos).

## D. Capacidad del horno

Cada horno tiene las siguientes características:

* Capacidad máxima: 6 carros (racks) por corrida
* Cada carro puede contener: 18 bandejas. En una bandeja específica no se combinan distintos tipos de pan.

El archivo “parametros_proceso_panaderia.xlsx” tiene los datos necesarios para estimar cuántas bandejas (y en consecuencia carros) se necesitan por cada tipo de pan y batch de producción de pan.

## E. Carga y Descarga del Horno

* Carga del horno: requiere 1 manipulador de horno y le toma 5 minutos
* Descarga del horno: requiere: 1 manipulador de horno, y le toma 5 minutos

## F. Tiempo de preparación (setup)

Cuando el horno cambia de una familia de horneado a otra, se requiere un tiempo adicional de preparación. Se considera 0 minutos si la nueva corrida es de la misma familia y 5 minutos si cambia a una familia distinta.

## G. Política de carga del horno

El horno no necesariamente opera siempre a capacidad completa. Para cada corrida se debe definir una política de carga.

Se establecen las siguientes condiciones:

* Carga mínima recomendada: 50% de la capacidad (600 kg)
* Si no se alcanza la carga mínima:
* se puede esperar acumulación de producto, o
* iniciar la corrida anticipadamente para evitar quiebres de stock
* Tiempo máximo de espera antes de iniciar una corrida: $\mathbf{1 5}$ minutos
* Se supone que existen suficientes carros y bandejas para toda la producción. Sin embargo, los debe modelar de manera explícita y limitada e indicar en su reporte final cuántos elementos necesita de cada tipo.

## H. Secuencia de producción

La selección de la familia de horneado a procesar en cada corrida no es fija, y debe ser determinada por una política de decisión.

El modelo debe permitir evaluar distintas estrategias, tales como:

* Prioridad al producto con menor stock en sala
* Prioridad al producto con mayor demanda esperada
* Secuencia fija de familias (por ejemplo: $14 \rightarrow 18 \rightarrow 21$ )
* Estrategias híbridas

## I. Restricción de retiro de carga

No se permite el retiro parcial de la carga del horno durante una corrida. Esto implica que todos los productos cargados en el horno permanecen hasta completar el tiempo de cocción y la descarga se realiza de forma completa al final de la corrida.

## J. Enfriamiento posterior

Una vez descargado el horno el producto debe pasar por una etapa de enfriamiento antes de ser enviado a la zona de ventas. El tiempo de enfriamiento está en la tabla de parámetros operacionales. Durante este tiempo, el producto no está disponible para la venta.

## K. Uso de recursos humanos

Cada operación del horno requiere un manipulador para la carga y un manipulador para la descarga. Si no hay manipulador disponible el horno no puede iniciar carga o descarga, generando posibles tiempos ociosos.

## L. Supuestos operacionales

Se consideran los siguientes supuestos:

* Todos los hornos son equivalentes
* No existen fallas de equipo
* No hay deterioro del producto por sobreproducción dentro del horizonte del día
* La capacidad del horno es homogénea para todos los tipos de pan

1. Indicadores de desempeño requeridos

El modelo debe reportar, al menos:

* quiebres de stock por tipo de pan,
* kilogramos no vendidos por quiebre,
* porcentaje de demanda satisfecha por tipo,
* Sobrantes de pan al final del día,
* producción total por tipo,
* inventario promedio y mínimo en sala,
* utilización de hornos,
* utilización de mezcladoras y amasadoras,
* utilización de panaderos,
* utilización de manipuladores de horno / despacho,
* número de lotes producidos por tipo,
* tiempo promedio de ciclo por lote,
* tiempo de espera promedio por recurso,

Se recomienda que cualquier supuesto adicional quede documentado y sea consistente con la lógica operacional del sistema. Consulte al profesor para estar seguro.

## V. Entregables

El trabajo debe incluir:

1. Modelo(s) en SIMIO: completamente ejecutable.
2. Informe técnico

Orientado como informe para la gerencia del supermercado, entregando la información sobre lo realizado, sus conclusiones y las sugerencias operativas, con:

* descripción del sistema,
* supuestos,
* estructura del modelo,
* definición de variables y recursos,
* escenarios evaluados,
* resultados,
* análisis de sensibilidad,
* y recomendación final de capacidad y política de producción.

1. Informe Académico

Relatando el proceso de desarrollo del modelo, planificación, organización de grupo, justificación de las decisiones de modelamiento y diseño, dificultades encontradas, aciertos, análisis realizados incluidos y descartados, análisis y reflexiones del proceso de desarrollo y sus resultados. Incluye, además:

* Anexos: con tablas de parámetros, distribuciones y lógica de demanda.
* Discusión: donde se explique qué recurso actúa como cuello de botella y por qué.

Se entregarán guías específicas sobre cada informe.
