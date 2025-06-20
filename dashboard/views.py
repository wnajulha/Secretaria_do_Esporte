from django.shortcuts import render
import pandas as pd
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
import io
import base64

# --- Helper para converter gráfico Matplotlib para imagem Base64 ---
def plot_to_base64(plt_fig):
    """Converte uma figura Matplotlib em uma string base64 para embutir no HTML."""
    buf = io.BytesIO()
    plt_fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    plt.close(plt_fig) # Fecha a figura para liberar memória
    return string.decode('utf-8')

# --- Nossa View Principal ---
def dashboard_view(request):
    # Caminho para os arquivos CSV (agora dentro da pasta do app)
    path_quadras = 'dashboard/qtd_quadras.csv'
    path_ginasios = 'dashboard/qtd_ginasios.csv'

    # --- LÓGICA DE DADOS (Unida dos seus scripts) ---
    # Carregar e preparar os dados
    quadras = pd.read_csv(path_quadras).dropna(subset=["Latitude", "Longitude"])
    quadras["Tipo"] = "Quadra"
    quadras["Descricao"] = quadras["Tipo_quadra"]

    ginasios = pd.read_csv(path_ginasios).dropna(subset=["Latitude", "Longitude"])
    ginasios["Tipo"] = "Ginásio"
    ginasios["Descricao"] = ginasios["Regiao_Administrativa"]

    locais = pd.concat([quadras, ginasios], ignore_index=True)

    # --- 1. GERAÇÃO DO MAPA DE PONTOS ---
    mapa_pontos = folium.Map(location=[-15.7942, -47.8822], zoom_start=11)
    for _, row in locais.iterrows():
        cor = "blue" if row["Tipo"] == "Quadra" else "green"
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"{row['Tipo']}: {row['Descricao']}",
            icon=folium.Icon(color=cor, icon="futbol", prefix="fa")
        ).add_to(mapa_pontos)
    # Converte o mapa Folium para HTML
    mapa_pontos_html = mapa_pontos._repr_html_()

    # --- 2. GERAÇÃO DO MAPA DE CALOR ---
    heat_data = locais[["Latitude", "Longitude"]].values.tolist()
    mapa_calor = folium.Map(location=[-15.7942, -47.8822], zoom_start=11)
    HeatMap(heat_data, min_opacity=0.4, radius=20, blur=15).add_to(mapa_calor)
    # Converte o mapa Folium para HTML
    mapa_calor_html = mapa_calor._repr_html_()

    # --- 3. GERAÇÃO DO GRÁFICO DE GINÁSIOS (MATPLOTLIB) ---
    contagem_ginasios = ginasios['Regiao_Administrativa'].value_counts().sort_values()
    fig_ginasios, ax_ginasios = plt.subplots(figsize=(10, 8))
    ax_ginasios.barh(contagem_ginasios.index, contagem_ginasios.values, color="green")
    ax_ginasios.set_xlabel("Quantidade de Ginásios")
    ax_ginasios.set_title("Quantidade de Ginásios por Região Administrativa - DF")
    ax_ginasios.grid(axis="x", linestyle="--", alpha=0.7)
    max_val_ginasios = contagem_ginasios.max()
    ax_ginasios.set_xticks(range(0, max_val_ginasios + 2, 1))
    # Converte para Base64
    grafico_ginasios_b64 = plot_to_base64(fig_ginasios)

    # --- 4. GERAÇÃO DO GRÁFICO DE QUADRAS (MATPLOTLIB) ---
    contagem_quadras = quadras['Regiao_Administrativa'].value_counts().sort_values()
    fig_quadras, ax_quadras = plt.subplots(figsize=(10, 8))
    ax_quadras.barh(contagem_quadras.index, contagem_quadras.values, color="blue")
    ax_quadras.set_xlabel("Quantidade de Quadras")
    ax_quadras.set_title("Quantidade de Quadras por Região Administrativa - DF")
    ax_quadras.grid(axis="x", linestyle="--", alpha=0.7)
    max_val_quadras = contagem_quadras.max()
    ax_quadras.set_xticks(range(0, max_val_quadras + 10, 10)) # Mudei o passo para 10 para ficar melhor
    # Converte para Base64
    grafico_quadras_b64 = plot_to_base64(fig_quadras)

    # --- Monta o contexto para enviar ao template ---
    context = {
        'mapa_pontos_html': mapa_pontos_html,
        'mapa_calor_html': mapa_calor_html,
        'grafico_ginasios_b64': grafico_ginasios_b64,
        'grafico_quadras_b64': grafico_quadras_b64,
    }

    # Renderiza o template com os dados
    return render(request, 'dashboard/index.html', context)
