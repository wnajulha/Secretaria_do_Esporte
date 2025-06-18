import pandas as pd
import matplotlib.pyplot as plt

# Lê o arquivo CSV
df = pd.read_csv("qtd_ginasios.csv")

# Conta quantas quadras por região
contagem_regioes = df['Regiao_Administrativa'].value_counts().sort_values()

# Cria o gráfico
plt.figure(figsize=(12, 10))
plt.barh(contagem_regioes.index, contagem_regioes.values, color="green")

plt.xlabel("Quantidade de ginasios")
plt.title("Quantidade de Ginasios por Região Administrativa - DF")
plt.grid(axis="x", linestyle="--", alpha=0.7)

# Define espaçamento de 10 em 10 no eixo X
max_val = contagem_regioes.max()
plt.xticks(range(0, max_val + 2, 1))  # se quiser mudar para de 10 em 10: range(0, max_val + 10, 10)

plt.tight_layout()
plt.show()
