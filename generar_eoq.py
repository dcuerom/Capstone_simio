import pandas as pd
import numpy as np

# 1. Definición de Parámetros Base
data = {
    "Tipo_de_Pan": [
        "Marraqueta", "Hallulla", "Marraqueta Integral", "Hallulla Integral", 
        "Pan Hot Dog", "Ciabatta", "Baguette", "Dobladita", "Bocado de Dama", "Amasado"
    ],
    "Demanda_Diaria_kg": [2000, 1700, 800, 800, 1200, 400, 350, 350, 220, 380],
    "Lead_Time_Min": [107, 111, 119, 117, 110, 134, 133, 87, 96, 115],
    "Kg_Batch": [60, 55, 60, 55, 55, 50, 45, 50, 25, 60],
    # Tri Min, Moda, Max
    "Tri_Min": [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
    "Tri_Moda": [1.0, 1.0, 0.5, 0.7, 1.0, 0.5, 0.5, 0.5, 0.5, 0.8],
    "Tri_Max": [2.0, 2.0, 2.0, 1.5, 3.0, 1.5, 1.0, 1.5, 1.0, 2.0]
}

# 2. Esperanza y Varianza de la Distribución Triangular
df = pd.DataFrame(data)
df['E_X'] = (df['Tri_Min'] + df['Tri_Moda'] + df['Tri_Max']) / 3.0
df['Var_X'] = (df['Tri_Min']**2 + df['Tri_Moda']**2 + df['Tri_Max']**2 - df['Tri_Min']*df['Tri_Moda'] - df['Tri_Min']*df['Tri_Max'] - df['Tri_Moda']*df['Tri_Max']) / 18.0

# 3. Cargar Probabilidades y determinar la franja Peak (18:00 - 19:00)
lambda_peak = 819.0

df_prob = pd.read_csv('/home/dacmxo/Desktop/udd/Capstone_simio/data/probabilidades_eleccion_por_hora.csv')
prob_peak = df_prob.iloc[9].to_dict()

P_k = []
for pan in df['Tipo_de_Pan']:
    if pan == "Marraqueta Integral":
        P_k.append(prob_peak['Marraqueta Integral'])
    elif pan == "Hallulla Integral":
        P_k.append(prob_peak['Hallulla Integral'])
    elif pan == "Pan Hot Dog":
        P_k.append(prob_peak['Pan Hot Dog'])
    elif pan == "Bocado de Dama":
        P_k.append(prob_peak['Bocado de Dama'])
    else:
        P_k.append(prob_peak[pan])
        
df['P_k_Peak'] = P_k
df['Lambda_k'] = lambda_peak * df['P_k_Peak']

# 4. Cálculo de Varianza Total (Ley de Varianza Total para Suma Compuesta)
df['Var_D_Horaria'] = df['Lambda_k'] * (df['Var_X'] + df['E_X']**2)
df['Sigma_D_Horaria'] = np.sqrt(df['Var_D_Horaria'])

# 5. Cálculo Estocástico para Lead Time
df['Lead_Time_Horas'] = df['Lead_Time_Min'] / 60.0
df['Mu_L'] = df['Lambda_k'] * df['E_X'] * df['Lead_Time_Horas']
df['Sigma_L'] = df['Sigma_D_Horaria'] * np.sqrt(df['Lead_Time_Horas'])

# 6. Cálculo EOQ
S_asumido = 1000
H_asumido = 10
df["Costo_Setup_S"] = S_asumido
df["Costo_Mantencion_H"] = H_asumido
df["EOQ_Optimo_kg"] = np.sqrt((2 * df["Demanda_Diaria_kg"] * S_asumido) / H_asumido)
df["EOQ_Batches"] = np.ceil(df["EOQ_Optimo_kg"] / df["Kg_Batch"])

# 7. Punto de Reorden Estocástico (Nivel de Servicio 95%)
Z_alpha = 1.645
df['Stock_Seguridad_kg'] = Z_alpha * df['Sigma_L']
df['ROP_Estocastico_kg'] = df['Mu_L'] + df['Stock_Seguridad_kg']
df['ROP_Estocastico_Batches'] = np.ceil(df['ROP_Estocastico_kg'] / df['Kg_Batch'])

# 8. Renombrar columnas para un reporte más detallado y profesional
df_final = df[[
    "Tipo_de_Pan", 
    "Demanda_Diaria_kg",
    "Lead_Time_Horas", 
    "E_X",
    "Var_X",
    "P_k_Peak",
    "Lambda_k",
    "Var_D_Horaria",
    "Sigma_D_Horaria",
    "Mu_L",
    "Sigma_L",
    "EOQ_Batches", 
    "Stock_Seguridad_kg", 
    "ROP_Estocastico_kg",
    "ROP_Estocastico_Batches"
]].copy()

df_final.columns = [
    "Tipo de Pan", 
    "Demanda Diaria (kg)",
    "Lead Time (Horas)", 
    "E[X] (Media de Compra kg)",
    "Var[X] (Varianza de Compra)",
    "P_k (Prob. Elección Peak)",
    "Lambda_k (Tasa Llegada Filtrada)",
    "Var(D) (Varianza Demanda Horaria)",
    "Sigma(D) (Desv. Est. Demanda Horaria)",
    "Mu_L (Demanda Esperada en Lead Time)",
    "Sigma_L (Desv. Est. en Lead Time)",
    "EOQ (Cantidad Óptima en Batches)", 
    "SS (Stock de Seguridad al 95% kg)", 
    "ROP Estocástico (Punto Reorden kg)",
    "ROP Estocástico (Batches)"
]

# 9. Construcción del Reporte Completo en formato de texto plano tipo CSV extendido
report_header = """REPORTE COMPLETO: ANÁLISIS ESTOCÁSTICO DE PRODUCCIÓN (EOQ Y ROP PROBABILÍSTICO)
==================================================================================================
DOCUMENTO DE REFERENCIA: metodologia_estocastica_eoq_rop.md
MODELO DE INVENTARIO: Revisión Continua (Q, R) con Demanda Compuesta (Poisson + Triangular)

PARÁMETROS GLOBALES DEL SISTEMA:
--------------------------------
- Nivel de Servicio Objetivo (CSL): 95%
- Factor Normal (Z_alpha): 1.645
- Tasa de Arribo Peak Global (Lambda_peak): 819.0 clientes/hora (18:00 - 19:00)
- Costo de Setup Asumido (S): 1000
- Costo de Mantención Asumido (H): 10 / kg

FUNDAMENTOS MATEMÁTICOS UTILIZADOS:
-----------------------------------
1. Varianza Total de Demanda Horaria: Var(D_t) = Lambda_k * (Var(X) + E[X]^2)
2. Demanda Esperada en Lead Time: Mu_L = Lambda_k * E[X] * L
3. Desviación Estándar en Lead Time: Sigma_L = Sigma_D_Horaria * sqrt(L)
4. Stock de Seguridad: SS = Z_alpha * Sigma_L
5. Punto de Reorden: ROP = Mu_L + SS
6. Lote Económico de Compra: EOQ = sqrt((2 * Demanda_Diaria * S) / H)

TABLA DE RESULTADOS DETALLADOS:
==================================================================================================
"""

# Generar la cadena del dataframe en formato CSV
csv_data = df_final.round(3).to_csv(index=False)

# Unir cabecera y datos
full_report = report_header + csv_data

output_path = '/home/dacmxo/Desktop/udd/Capstone_simio/data/analisis_eoq_rop.csv'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(full_report)

print(f"Reporte completo y estocástico guardado exitosamente en: {output_path}")