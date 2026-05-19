# Análisis Analítico de Producción: EOQ y ROP en Operaciones de Panadería

Este documento formaliza el marco teórico y matemático utilizado para el cálculo de la Cantidad Económica de Pedido (EOQ - *Economic Order Quantity*) y el Punto de Reorden (ROP - *Reorder Point*) aplicados a la producción interna de la panadería del supermercado.

---

## 1. Fundamentos del Modelo EOQ (Cantidad Económica de Pedido)

El modelo EOQ busca minimizar el costo total anual (o periódico) de la gestión de inventarios, balanceando el costo de preparación de los equipos (setup) y el costo de mantener inventario. 

La función de Costo Total ($TC$) se define como:

$$ TC(Q) = \left( \frac{D}{Q} \right) S + \left( \frac{Q}{2} \right) H $$

Donde:
- **$D$**: Demanda acumulada en el período (Ej: kg diarios).
- **$Q$**: Tamaño del lote a producir (Cantidad Económica de Pedido, en kg).
- **$S$**: Costo de Setup o Preparación por cada lote de producción.
- **$H$**: Costo de Mantención por unidad (kg) por período.

Para encontrar el óptimo, derivamos la función de Costo Total respecto a $Q$ e igualamos a cero:

$$ \frac{dTC}{dQ} = - \frac{D \cdot S}{Q^2} + \frac{H}{2} = 0 $$

Despejando $Q$, obtenemos la fórmula clásica del EOQ:

$$ EOQ = Q^* = \sqrt{\frac{2 \cdot D \cdot S}{H}} $$

### Adaptación al Entorno de Panadería (Batches)
Dado que la panadería no puede producir fracciones de un batch, el tamaño del lote óptimo en unidades físicas (Batches) se calcula como la función techo del cociente entre el $EOQ$ y el tamaño estándar del batch de ese producto ($B_i$):

$$ EOQ_{batches} = \left\lceil \frac{EOQ}{B_i} \right\rceil $$

---

## 2. Análisis del Punto de Reorden (ROP) y Stock de Seguridad (SS)

El Punto de Reorden ($ROP$) determina el nivel exacto de inventario (en sala y en proceso) que debe disparar una nueva orden de producción para evitar el quiebre de stock durante el Lead Time ($L$).

En un escenario determinista estático, el ROP clásico es:

$$ ROP = d_{promedio} \times L $$

Donde:
- **$d_{promedio}$**: Tasa de demanda promedio (kg / hora).
- **$L$**: Lead Time o tiempo de ciclo de producción (horas).

### Ajuste por Variabilidad Intra-Día (Régimen Trimodal)
El análisis empírico demostró que la demanda de pan presenta un régimen altamente no estacionario, con peaks severos (ej. 18:00 - 20:00 hrs para el Pan Hot Dog y la Marraqueta). Utilizar el $d_{promedio}$ resultaría inevitablemente en quiebres de stock durante el peak vespertino.

Por lo tanto, se define el **ROP Peak** para garantizar el Nivel de Servicio en el escenario más estresante:

$$ ROP_{peak} = d_{peak} \times L $$

Donde:
- **$d_{peak}$**: Tasa de demanda máxima observada en la franja horaria más alta (kg / hora).

### 2.1 Cálculo del Stock de Seguridad (SS)
El Stock de Seguridad es el colchón de inventario diseñado para absorber las fluctuaciones de la demanda por sobre la media durante el Lead Time. En este modelo adaptativo, el SS sugerido es la diferencia analítica entre el ROP de estrés y el ROP promedio:

$$ SS = ROP_{peak} - ROP_{promedio} $$

$$ SS = (d_{peak} \times L) - (d_{promedio} \times L) = L \cdot (d_{peak} - d_{promedio}) $$

### 2.2 Política PULL en Simio
Bajo la Política PULL (Alternativa 1), el sistema evalúa la inecuación de inventario. Si el Nivel de Inventario Disponible ($I_{disponible}$) más el Inventario en Tránsito ($I_{en\_proceso}$) es menor o igual al ROP, se dispara la producción de un lote $Q^*$:

$$ I_{disponible} + I_{en\_proceso} \leq ROP_{peak} \implies \text{Trigger } Q^* $$

---

## 3. Ejemplo Numérico: Pan Hot Dog

Utilizando los datos del archivo `analisis_eoq_rop.csv` y `TableDemandaHora.csv` para el Pan Hot Dog:

- **$D$ (Demanda Diaria)**: $1200 \text{ kg}$
- **$d_{promedio}$ (Demanda Promedio)**: $100.0 \text{ kg/hr}$
- **$d_{peak}$ (Demanda Peak 18:00)**: $382.21 \text{ kg/hr}$
- **$L$ (Lead Time)**: $110 \text{ min} = 1.833 \text{ horas}$
- **$B_i$ (Tamaño Batch)**: $55 \text{ kg}$
- **$S$ (Costo Setup asumido)**: $1000$
- **$H$ (Costo Mantención asumido)**: $10$

**1. Cálculo del EOQ:**

$$ EOQ = \sqrt{\frac{2 \cdot 1200 \cdot 1000}{10}} = \sqrt{240000} \approx 489.9 \text{ kg} $$

$$ EOQ_{batches} = \left\lceil \frac{489.9}{55} \right\rceil = \lceil 8.9 \rceil = 9 \text{ batches} $$

**2. Cálculo del ROP Promedio:**

$$ ROP_{promedio} = 100.0 \times 1.833 = 183.33 \text{ kg} $$

**3. Cálculo del ROP Peak (Sugerido para Simio):**

$$ ROP_{peak} = 382.21 \times 1.833 = 700.72 \text{ kg} $$

$$ ROP_{batches} = \left\lceil \frac{700.72}{55} \right\rceil = \lceil 12.74 \rceil = 13 \text{ batches} $$

**4. Stock de Seguridad:**

$$ SS = 700.72 - 183.33 = 517.39 \text{ kg} $$

### Conclusión Analítica
Para el Pan Hot Dog, debido a su extrema variabilidad horaria (saltando de 26 kg/hr en la mañana a 382 kg/hr en la tarde), un modelo de reposición estándar fallaría. El sistema PULL requiere un punto de reorden alto (13 batches) para anticipar la onda de demanda vespertina, requiriendo un stock de seguridad severo de ~517 kg.
