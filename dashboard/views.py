from django.shortcuts import render
import pandas as pd
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
import io
import base64

def plot_to_base64(plt_fig):
    buf = io.BytesIO()
    plt_fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    plt.close(plt_fig)
    return string.decode('utf-8')

def dashboard_view(request):
    path_quadras = 'dashboard/qtd_quadras.csv'
    path_ginasios = 'dashboard/qtd_ginasios.csv' 

    quadras = pd.read_csv(path_quadras).dropna(subset=["Latitude", "Longitude"])
    quadras["Tipo"] = "Quadra"
    quadras["Descricao"] = quadras["Tipo_quadra"]

    ginasios = pd.read_csv(path_ginasios)
    ginasios_mapa = ginasios.dropna(subset=["Latitude", "Longitude"]).copy()
    ginasios_mapa["Tipo"] = "Ginásio"
    ginasios_mapa["Descricao"] = ginasios_mapa["Nome_do_ginasio"] 

    locais = pd.concat([quadras, ginasios_mapa], ignore_index=True)

    mapa_pontos = folium.Map(location=[-15.7942, -47.8822], zoom_start=11)
    for _, row in locais.iterrows():
        cor = "blue" if row["Tipo"] == "Quadra" else "green"
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"{row['Tipo']}: {row['Descricao']}",
            icon=folium.Icon(color=cor, icon="futbol", prefix="fa")
        ).add_to(mapa_pontos)
    mapa_pontos_html = mapa_pontos._repr_html_()
    
    heat_data = locais[["Latitude", "Longitude"]].dropna().values.tolist()
    mapa_calor = folium.Map(location=[-15.7942, -47.8822], zoom_start=11)
    HeatMap(heat_data, min_opacity=0.4, radius=20, blur=15).add_to(mapa_calor)
    mapa_calor_html = mapa_calor._repr_html_()

    contagem_ginasios = ginasios['Regiao_Administrativa'].value_counts().sort_values()
    fig_ginasios, ax_ginasios = plt.subplots(figsize=(10, 8))
    ax_ginasios.barh(contagem_ginasios.index, contagem_ginasios.values, color="green")
    ax_ginasios.set_xlabel("Quantidade de Ginásios")
    ax_ginasios.set_title("Quantidade de Ginásios por Região Administrativa - DF")
    ax_ginasios.grid(axis="x", linestyle="--", alpha=0.7)
    max_val_ginasios = contagem_ginasios.max()
    ax_ginasios.set_xticks(range(0, max_val_ginasios + 2, 1))
    grafico_ginasios_b64 = plot_to_base64(fig_ginasios)

    contagem_quadras = quadras['Regiao_Administrativa'].value_counts().sort_values()
    fig_quadras, ax_quadras = plt.subplots(figsize=(10, 8))
    ax_quadras.barh(contagem_quadras.index, contagem_quadras.values, color="blue")
    ax_quadras.set_xlabel("Quantidade de Quadras")
    ax_quadras.set_title("Quantidade de Quadras por Região Administrativa - DF")
    ax_quadras.grid(axis="x", linestyle="--", alpha=0.7)
    max_val_quadras = contagem_quadras.max()
    ax_quadras.set_xticks(range(0, max_val_quadras + 10, 10))
    grafico_quadras_b64 = plot_to_base64(fig_quadras)

    dados_ginasios_agrupados = {}
    
    ginasios_com_horario = ginasios.dropna(
        subset=['Regiao_Administrativa', 'Endereço', 'Nome_do_ginasio', 'Horario_de_funcionamento']
    ).sort_values('Regiao_Administrativa')

    for regiao, df_regiao in ginasios_com_horario.groupby('Regiao_Administrativa'):
        lista_de_ginasios = df_regiao[['Nome_do_ginasio', 'Endereço', 'Horario_de_funcionamento']].to_dict('records')
        dados_ginasios_agrupados[regiao] = lista_de_ginasios

    context = {
        'mapa_pontos_html': mapa_pontos_html,
        'mapa_calor_html': mapa_calor_html,
        'grafico_ginasios_b64': grafico_ginasios_b64,
        'grafico_quadras_b64': grafico_quadras_b64,
        'dados_ginasios_agrupados': dados_ginasios_agrupados,
    }

    return render(request, 'dashboard/index.html', context)