import pandas as pd
import folium
from folium.plugins import HeatMap

# Carregar CSV das quadras
quadras = pd.read_csv("qtd_quadras.csv")
quadras = quadras.dropna(subset=["Latitude", "Longitude"])
quadras["Tipo"] = "Quadra"
quadras["Descricao"] = quadras["Tipo_quadra"]

# Carregar CSV dos ginásios
ginasios = pd.read_csv("qtd_ginasios.csv")
ginasios = ginasios.dropna(subset=["Latitude", "Longitude"])
ginasios["Tipo"] = "Ginásio"
ginasios["Descricao"] = ginasios["Regiao_Administrativa"]

# Unir os dois DataFrames
locais = pd.concat([quadras, ginasios], ignore_index=True)

# ---------- MAPA SIMPLES ------------
mapa = folium.Map(location=[-15.7942, -47.8822], zoom_start=12)

for _, row in locais.iterrows():
    cor = "blue" if row["Tipo"] == "Quadra" else "green"
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=row["Descricao"],
        icon=folium.Icon(color=cor, icon="futbol", prefix="fa")
    ).add_to(mapa)

mapa.save("mapa_simples.html")
print("Mapa simples salvo como mapa_simples_sport.html")

# ---------- MAPA DE CALOR ------------
heat_data = locais[["Latitude", "Longitude"]].dropna().values.tolist()

mapa_calor = folium.Map(location=[-15.7942, -47.8822], zoom_start=11)
HeatMap(heat_data, min_opacity=0.4, radius=20, blur=15).add_to(mapa_calor)
mapa_calor.save("mapa_calor.html")
print("Mapa de calor salvo como mapa_calor_sport.html")


