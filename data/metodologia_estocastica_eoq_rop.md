# Análisis Estocástico de Producción: EOQ y ROP Probabilístico

Este documento expande el análisis determinista anterior hacia un **Planteamiento Estocástico** de revisión continua $(Q, R)$, incorporando la variabilidad e incertidumbre inherente en la demanda de los clientes.

---

## 1. Fundamentos del Enfoque Estocástico $(Q, R)$

En el mundo real, la demanda de pan no es un flujo constante, sino un proceso estocástico (modelado en SIMIO como un proceso de Poisson no homogéneo, NHPP). El modelo de revisión continua $(Q, R)$ define dos decisiones clave:
- **$Q$**: Cuánto pedir (EOQ).
- **$R$**: Cuándo pedir (ROP probabilístico).

Bajo incertidumbre, el Punto de Reorden ($R$) no solo cubre la demanda esperada durante el Lead Time ($L$), sino que agrega un **Stock de Seguridad Estocástico ($SS$)** calculado para satisfacer un Nivel de Servicio ($CSL$ - *Cycle Service Level*) objetivo.

$$ R = \mu_L + SS $$

Donde:
- **$\mu_L$**: Demanda esperada durante el Lead Time.
- **$SS$**: Stock de seguridad que absorbe la varianza estocástica.

---

## 2. Modelamiento de la Incertidumbre (Varianza de la Demanda)

Si asumimos que el Lead Time productivo ($L$) es constante (determinado por las recetas del archivo `parametros_proceso_panaderia.csv`), la incertidumbre del sistema recae exclusivamente en la demanda.

Sea $D_t$ la demanda por hora, con media $\mu_D$ y desviación estándar $\sigma_D$.
La demanda acumulada durante el Lead Time ($D_L$) posee:
- **Media**: $\mu_L = \mu_D \cdot L$
- **Varianza**: $\sigma_L^2 = \sigma_D^2 \cdot L$
- **Desviación Estándar**: $\sigma_L = \sigma_D \cdot \sqrt{L}$

### 2.1 El Nivel de Servicio y el Factor Z
Para evitar quiebres de stock con una probabilidad $\alpha$ (ej. 95%), utilizamos la inversa de la función de distribución acumulada normal estándar, $Z_\alpha$:

$$ P(D_L \leq R) = \alpha \implies R = \mu_L + Z_\alpha \cdot \sigma_L $$

Por lo tanto, el Stock de Seguridad Estocástico es:

$$ SS = Z_\alpha \cdot \sigma_L = Z_\alpha \cdot \sigma_D \sqrt{L} $$

---

## 3. Adaptación al Régimen No Estacionario (Peak de Demanda)

Dado que la panadería exhibe regímenes marcados (Valle, Medio, Peak), aplicar una $\sigma_D$ global ponderada del día subestimaría severamente el riesgo de quiebre en la tarde. 

Para obtener un modelo robusto que garantice el Nivel de Servicio en la franja más crítica (18:00 - 20:00), condicionamos los parámetros a las estadísticas del peak:
- $\mu_{peak}$: Demanda promedio por hora durante el peak.
- $\sigma_{peak}$: Desviación estándar de la demanda por hora durante el peak.

El ROP robusto adaptado al peak queda definido como:

$$ ROP_{robusto} = (\mu_{peak} \cdot L) + \left( Z_\alpha \cdot \sigma_{peak} \sqrt{L} \right) $$

---

## 4. Estocasticidad en la Composición de la Demanda

A diferencia de un modelo clásico de inventarios, la varianza de la demanda horaria ($\sigma_D^2$) en nuestro sistema proviene de **dos fuentes probabilísticas independientes** que ocurren simultáneamente (generando una Suma Aleatoria Compuesta):
1. **Llegada de Clientes ($N_t$)**: Proceso de Poisson con tasa de arribo $\lambda_t$. Su varianza es igual a su media, $\text{Var}(N_t) = \lambda_t$.
2. **Tamaño del Pedido ($X_i$)**: Cantidad comprada por cliente, modelada por una distribución Triangular$(a, c, b)$. 

La varianza real de la demanda en peso por hora, $\text{Var}(D_t)$, se obtiene mediante la **Ley de la Varianza Total** (o varianza de una suma aleatoria):

$$ D_t = \sum_{i=1}^{N_t} X_i $$

$$ \text{Var}(D_t) = E[N_t] \cdot \text{Var}(X) + \text{Var}(N_t) \cdot (E[X])^2 $$

Dado que en una distribución de Poisson $E[N_t] = \text{Var}(N_t) = \lambda_t$, factorizamos:

$$ \sigma_D^2 = \lambda_t \cdot \left( \text{Var}(X) + E[X]^2 \right) $$

Donde para la distribución Triangular$(a, c, b)$:
- **Media**: $E[X] = \frac{a+b+c}{3}$
- **Varianza**: $\text{Var}(X) = \frac{a^2+b^2+c^2 - ab - ac - bc}{18}$

### Factor de Probabilidad de Elección ($P_k$)
Para un tipo de pan específico $k$, la tasa de llegada efectiva que impacta su inventario es el proceso de Poisson filtrado $\lambda_{t,k} = \lambda_t \cdot P_k$, donde $P_k$ es la probabilidad de que un cliente elija ese pan (proveniente del archivo `probabilidades_eleccion_por_hora.csv`).

---

## 5. Ejemplo Analítico y Despliegue (Pan Hot Dog en Peak)

Demostración del cálculo para el **Pan Hot Dog** en la hora peak (18:00 - 19:00):
- Tasa total de arribo: $\lambda_{peak} = 819 \text{ clientes/hr}$
- Probabilidad de elección Hot Dog: $P_{hotdog} = 0.2501$
- Tasa de arribo filtrada: $\lambda_{hotdog} = 819 \times 0.2501 \approx 204.8 \text{ clientes/hr}$
- Distribución de Pedido: Triangular(0.3, 1.0, 3.0) kg
  - Esperanza: $E[X] = \frac{0.3 + 1.0 + 3.0}{3} \approx 1.433 \text{ kg}$
  - Varianza: $\text{Var}(X) = \frac{0.3^2 + 3.0^2 + 1.0^2 - 0.9 - 0.3 - 3.0}{18} \approx 0.355 \text{ kg}^2$

**Paso 1: Cálculo de la Varianza Horaria ($\sigma_D^2$)**

Sustituyendo en la fórmula de la varianza total:
$$ \sigma_D^2 = 204.8 \cdot (0.355 + 1.433^2) = 204.8 \cdot (0.355 + 2.053) = 204.8 \cdot 2.408 \approx 493.2 $$

La desviación estándar horaria es:
$$ \sigma_D = \sqrt{493.2} \approx 22.21 \text{ kg/hr} $$

**Paso 2: Conversión al Lead Time**

Sabiendo que el Lead Time del Hot Dog es $L = 110 \text{ min} = 1.833 \text{ hr}$ y la demanda media en peak es $\mu_{peak} = \lambda_{hotdog} \cdot E[X] \approx 293.5 \text{ kg/hr}$:

$$ \mu_L = 293.5 \cdot 1.833 = 538 \text{ kg} $$
$$ \sigma_L = \sigma_D \sqrt{L} = 22.21 \cdot \sqrt{1.833} \approx 22.21 \cdot 1.354 \approx 30.07 \text{ kg} $$

**Paso 3: Cálculo del Stock de Seguridad y ROP (Nivel de Servicio 95%)**

Para un $CSL$ del 95%, el factor normal $Z_{0.95} = 1.645$:

$$ SS = Z_{0.95} \cdot \sigma_L = 1.645 \cdot 30.07 \approx 49.46 \text{ kg} $$

El **Punto de Reorden Estocástico Definitivo** es:
$$ ROP_{95\%} = \mu_L + SS = 538 + 49.46 = 587.46 \text{ kg} $$

Llevado a Batches (Lotes de 55 kg):
$$ ROP_{batches} = \left\lceil \frac{587.46}{55} \right\rceil = 11 \text{ batches} $$

### Conclusión Analítica y Comparativa
En el modelo determinista ajustado empíricamente al límite absoluto del peak (sin considerar la varianza estadística), calculamos un ROP ultra-conservador de **13 batches** para el Pan Hot Dog para asegurar 0 quiebres.

El **Planteamiento Estocástico**, al modelar matemáticamente la varianza real de la suma compuesta (Poisson + Triangular) y apuntar a un **95% de Nivel de Servicio óptimo**, demuestra analíticamente que un ROP de **11 batches** ($\approx 605$ kg) es estadísticamente suficiente para absorber la incertidumbre sin sobreproducir innecesariamente en la hora pico, logrando un balance mucho más eficiente en la utilización de los hornos y amasadoras.