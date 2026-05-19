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
    "Kg_Batch": [60, 55, 60, 55, 55, 50, 45, 50, 25, 60]
}

# 2. Cargar Perfil de Demanda Horaria
df_demanda = pd.read_csv('/home/dacmxo/Desktop/udd/Capstone_simio/simiona/TableDemandaHora.csv')
bread_cols = data["Tipo_de_Pan"]

# Extraer promedios y peaks
data["Demanda_Promedio_Hora_kg"] = [df_demanda[b].mean() for b in bread_cols]
data["Demanda_Peak_Hora_kg"] = [df_demanda[b].max() for b in bread_cols]

df = pd.DataFrame(data)

# Convertir Lead Time a Horas
df["Lead_Time_Horas"] = df["Lead_Time_Min"] / 60.0

# 3. Supuestos de Costos para Análisis EOQ
# S = Costo de Preparación (Setup). Representa el esfuerzo, tiempo de operario y máquina. (Valor supuesto: 1000)
# H = Costo de Mantención (Holding). Representa costo de vitrina y riesgo de merma al final del día. (Valor supuesto: 10/kg/día)
S_asumido = 1000
H_asumido = 10

df["Costo_Setup_S"] = S_asumido
df["Costo_Mantencion_H"] = H_asumido

# 4. Cálculos EOQ
# Fórmula EOQ: sqrt((2 * D * S) / H)
df["EOQ_Optimo_kg"] = np.sqrt((2 * df["Demanda_Diaria_kg"] * S_asumido) / H_asumido)
# Conversión a número de lotes (Batches redondos)
df["EOQ_Batches"] = np.ceil(df["EOQ_Optimo_kg"] / df["Kg_Batch"])

# 5. Cálculos ROP (Punto de Reorden) y Stock de Seguridad
# ROP Promedio = Demanda Promedio * Lead Time
df["ROP_Promedio_kg"] = df["Demanda_Promedio_Hora_kg"] * df["Lead_Time_Horas"]
# ROP Peak = Demanda Peak * Lead Time (Garantiza cubrir la franja de mayor estrés)
df["ROP_Peak_kg"] = df["Demanda_Peak_Hora_kg"] * df["Lead_Time_Horas"]

# Stock de Seguridad = Diferencia entre ROP para Peak y ROP Promedio
df["Stock_Seguridad_Sugerido_kg"] = df["ROP_Peak_kg"] - df["ROP_Promedio_kg"]

# El Punto de Reorden final sugerido es el ROP Peak para evitar los quiebres de stock críticos (objetivo principal del proyecto)
df["Punto_Reorden_Sugerido_kg"] = df["ROP_Peak_kg"]
df["Punto_Reorden_Batches"] = np.ceil(df["Punto_Reorden_Sugerido_kg"] / df["Kg_Batch"])

# 6. Formateo y Exportación
df_final = df[[
    "Tipo_de_Pan", 
    "Demanda_Diaria_kg", 
    "Demanda_Promedio_Hora_kg", 
    "Demanda_Peak_Hora_kg", 
    "Lead_Time_Min", 
    "Lead_Time_Horas", 
    "Costo_Setup_S", 
    "Costo_Mantencion_H", 
    "EOQ_Optimo_kg", 
    "EOQ_Batches", 
    "ROP_Promedio_kg", 
    "Stock_Seguridad_Sugerido_kg", 
    "Punto_Reorden_Sugerido_kg",
    "Punto_Reorden_Batches"
]]

output_path = '/home/dacmxo/Desktop/udd/Capstone_simio/data/analisis_eoq_rop.csv'
df_final.round(2).to_csv(output_path, index=False)
print(f"Análisis guardado exitosamente en: {output_path}")
