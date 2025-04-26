import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

# Carregar os dados das receitas de um arquivo externo
df = pd.read_csv("dados.csv")

# Função para processar os dados e criar o dicionário de ingredientes
def processar_dados(df):
    ingredientes_dict = {}
    
    for _, row in df.iterrows():
        ingredientes = [ing.strip() for ing in row['ingredientes'].split(',')]
        tipos = [tipo.strip() for tipo in row['tipos_ingredientes'].split(',')]
        
        # Criar dicionário de ingredientes e seus tipos
        for i, ingrediente in enumerate(ingredientes):
            if ingrediente not in ingredientes_dict:
                ingredientes_dict[ingrediente] = tipos[i]
    
    return ingredientes_dict

# Construir o grafo de co-ocorrência
def construir_grafo(df, ingredientes_dict):
    G = nx.Graph()
    
    # Adicionar nós (ingredientes) com atributo tipo
    for ingrediente, tipo in ingredientes_dict.items():
        G.add_node(ingrediente, tipo=tipo)
    
    # Adicionar arestas (co-ocorrências)
    for _, row in df.iterrows():
        ingredientes = [ing.strip() for ing in row['ingredientes'].split(',')]
        
        # Criar arestas entre todos os pares de ingredientes na receita
        for i in range(len(ingredientes)):
            for j in range(i+1, len(ingredientes)):
                if G.has_edge(ingredientes[i], ingredientes[j]):
                    # Se a aresta já existe, incrementar o peso
                    G[ingredientes[i]][ingredientes[j]]['weight'] += 1
                else:
                    # Criar nova aresta com peso 1
                    G.add_edge(ingredientes[i], ingredientes[j], weight=1)
    
    return G

# Processar os dados
ingredientes_dict = processar_dados(df)

# Construir o grafo
G = construir_grafo(df, ingredientes_dict)

# Calcular coeficiente de assortatividade
assortativity = nx.attribute_assortativity_coefficient(G, "tipo")
print(f"Coeficiente de assortatividade por tipo: {assortativity:.4f}")

# Criar dicionário de cores para cada tipo
tipo_cores = {
    'Proteína': '#FF5733',    # Vermelho
    'Carboidrato': '#FFC300', # Amarelo
    'Vegetal': '#4CAF50',     # Verde
    'Fruta': '#9C27B0',       # Roxo
    'Laticínio': '#2196F3',   # Azul
    'Gordura': '#FF9800',     # Laranja
    'Condimento': '#795548',  # Marrom
    'Outro': '#607D8B'        # Cinza azulado
}

# Criar lista de cores para cada nó
node_colors = [tipo_cores[G.nodes[node]['tipo']] for node in G.nodes()]

# Calcular tamanho dos nós com base no grau
node_sizes = [100 + 20 * G.degree(node) for node in G.nodes()]

# Análise estatística da co-ocorrência
def analisar_coocorrencias(G):
    # Contar o número de co-ocorrências por tipo
    coocorrencias = {}
    total_coocorrencias = 0
    
    for u, v, data in G.edges(data=True):
        tipo_u = G.nodes[u]['tipo']
        tipo_v = G.nodes[v]['tipo']
        
        # Ordenar os tipos para evitar duplicações
        par_tipos = tuple(sorted([tipo_u, tipo_v]))
        
        peso = data.get('weight', 1)
        if par_tipos in coocorrencias:
            coocorrencias[par_tipos] += peso
        else:
            coocorrencias[par_tipos] = peso
            
        total_coocorrencias += peso
    
    # Calcular percentuais
    percentuais = {par: (valor / total_coocorrencias) * 100 for par, valor in coocorrencias.items()}
    
    # Ordenar por frequência
    percentuais_ordenados = dict(sorted(percentuais.items(), key=lambda item: item[1], reverse=True))
    
    return percentuais_ordenados, total_coocorrencias

# Contar ingredientes por tipo
ingredientes_por_tipo = {}
for ingrediente, tipo in ingredientes_dict.items():
    if tipo in ingredientes_por_tipo:
        ingredientes_por_tipo[tipo].append(ingrediente)
    else:
        ingredientes_por_tipo[tipo] = [ingrediente]

# Contar quantidade de ingredientes por tipo
qtd_por_tipo = {tipo: len(ingredientes) for tipo, ingredientes in ingredientes_por_tipo.items()}

# Calcular estatísticas por tipo
estatisticas_tipo = {}
for tipo in qtd_por_tipo.keys():
    # Nós deste tipo
    nos_tipo = [node for node in G.nodes() if G.nodes[node]['tipo'] == tipo]
    
    # Grau médio dos nós deste tipo
    if nos_tipo:
        grau_medio = sum(G.degree(node) for node in nos_tipo) / len(nos_tipo)
    else:
        grau_medio = 0
    
    estatisticas_tipo[tipo] = {
        'quantidade': qtd_por_tipo[tipo],
        'grau_medio': grau_medio
    }

# Analisar co-ocorrências
percentuais_coocorrencia, total_edges = analisar_coocorrencias(G)

# Visualizar o grafo
plt.figure(figsize=(14, 10))

# Usar layout Kamada-Kawai para melhor visualização
pos = nx.kamada_kawai_layout(G)

# Desenhar nós
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)

# Desenhar arestas com espessura baseada no peso
edge_weights = [G[u][v]['weight'] * 0.5 for u, v in G.edges()]
nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.3)

# Desenhar labels apenas para os nós mais importantes (maior grau)
# Calcular grau para cada nó
degree_dict = dict(G.degree())
# Selecionar os top 30 nós com maior grau
top_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:30]
top_nodes_dict = {node: label for node, label in top_nodes}

# Desenhar apenas os labels dos nós mais importantes
labels = {node: node for node in G.nodes() if node in top_nodes_dict}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight="bold")

# Adicionar legenda
import matplotlib.patches as mpatches
legend_patches = [mpatches.Patch(color=color, label=tipo) for tipo, color in tipo_cores.items()]
plt.legend(handles=legend_patches, loc='upper right')

plt.title("Grafo de Co-ocorrência de Ingredientes na Culinária Brasileira", fontsize=16)
plt.axis('off')
plt.tight_layout()

# Exibir as estatísticas
print("\nEstatísticas por tipo de ingrediente:")
for tipo, stats in estatisticas_tipo.items():
    print(f"{tipo}: {stats['quantidade']} ingredientes, grau médio: {stats['grau_medio']:.2f}")

print("\nTop 10 co-ocorrências por tipo:")
for i, (par_tipos, percentual) in enumerate(list(percentuais_coocorrencia.items())[:10]):
    print(f"{i+1}. {par_tipos[0]} + {par_tipos[1]}: {percentual:.2f}%")

# Análise de homofilia (mesmo tipo) vs heterofilia (tipos diferentes)
homofilia = 0
heterofilia = 0

for par, valor in percentuais_coocorrencia.items():
    if par[0] == par[1]:  # Mesmo tipo
        homofilia += valor
    else:  # Tipos diferentes
        heterofilia += valor

print(f"\nCo-ocorrências entre mesmo tipo (homofilia): {homofilia:.2f}%")
print(f"Co-ocorrências entre tipos diferentes (heterofilia): {heterofilia:.2f}%")

# Criar uma interpretação textual da assortatividade
if assortativity > 0.1:
    interpretacao = "A culinária brasileira tende a valorizar combinações homogêneas (ingredientes do mesmo tipo aparecem juntos com frequência)."
elif assortativity < -0.1:
    interpretacao = "A culinária brasileira tende a valorizar combinações contrastantes (ingredientes de tipos diferentes aparecem juntos com frequência)."
else:
    interpretacao = "A culinária brasileira apresenta um equilíbrio entre combinações homogêneas e contrastantes."

print(f"\nInterpretação da assortatividade: {interpretacao}")

# Salvar o gráfico como imagem
plt.savefig("grafo_culinaria_brasileira.png", dpi=300, bbox_inches="tight")

# Análise detalhada da matriz de co-ocorrência entre tipos
def calcular_matriz_coocorrencia(G):
    # Todos os tipos possíveis
    tipos = list(set(nx.get_node_attributes(G, 'tipo').values()))
    tipos.sort()
    
    # Criar matriz de zeros
    matriz = np.zeros((len(tipos), len(tipos)))
    
    # Preencher matriz com contagens
    for u, v, data in G.edges(data=True):
        tipo_u = G.nodes[u]['tipo']
        tipo_v = G.nodes[v]['tipo']
        peso = data.get('weight', 1)
        
        i = tipos.index(tipo_u)
        j = tipos.index(tipo_v)
        
        matriz[i, j] += peso
        matriz[j, i] += peso  # Matriz simétrica
    
    return matriz, tipos

# Calcular e visualizar a matriz de co-ocorrência
matriz_coocorrencia, tipos = calcular_matriz_coocorrencia(G)

# Normalizar a matriz
totais_linha = matriz_coocorrencia.sum(axis=1)
matriz_normalizada = np.zeros_like(matriz_coocorrencia)
for i in range(len(tipos)):
    if totais_linha[i] > 0:
        matriz_normalizada[i, :] = matriz_coocorrencia[i, :] / totais_linha[i]

# Visualizar a matriz de co-ocorrência
plt.figure(figsize=(10, 8))
plt.imshow(matriz_normalizada, cmap='YlOrRd')
plt.colorbar(label='Frequência normalizada')
plt.title('Matriz de Co-ocorrência entre Tipos de Ingredientes', fontsize=14)
plt.xticks(range(len(tipos)), tipos, rotation=45, ha='right')
plt.yticks(range(len(tipos)), tipos)

# Adicionar valores à matriz
for i in range(len(tipos)):
    for j in range(len(tipos)):
        plt.text(j, i, f'{matriz_normalizada[i, j]:.2f}', 
                 ha='center', va='center', 
                 color='black' if matriz_normalizada[i, j] < 0.5 else 'white')

plt.tight_layout()
plt.savefig("matriz_coocorrencia.png", dpi=300, bbox_inches="tight")

# Análise final em um arquivo de texto
with open("analise_assortatividade.txt", "w", encoding="utf-8") as f:
    f.write("=== ANÁLISE DE ASSORTATIVIDADE NA CULINÁRIA BRASILEIRA ===\n\n")
    f.write(f"Coeficiente de assortatividade: {assortativity:.4f}\n")
    f.write(f"{interpretacao}\n\n")
    
    f.write("Co-ocorrências entre mesmo tipo (homofilia): {:.2f}%\n".format(homofilia))
    f.write("Co-ocorrências entre tipos diferentes (heterofilia): {:.2f}%\n\n".format(heterofilia))
    
    f.write("Combinações mais frequentes:\n")
    for i, (par_tipos, percentual) in enumerate(list(percentuais_coocorrencia.items())[:10]):
        f.write(f"{i+1}. {par_tipos[0]} + {par_tipos[1]}: {percentual:.2f}%\n")
    
    f.write("\nEstatísticas por tipo de ingrediente:\n")
    for tipo, stats in estatisticas_tipo.items():
        f.write(f"{tipo}: {stats['quantidade']} ingredientes, grau médio: {stats['grau_medio']:.2f}\n")
    
    f.write("\nIngredientes centrais na culinária brasileira:\n")
    for node, degree in list(sorted(G.degree(), key=lambda x: x[1], reverse=True))[:15]:
        tipo = G.nodes[node]['tipo']
        f.write(f"{node} ({tipo}): conectado a {degree} outros ingredientes\n")

print("\nAnálise completa! Arquivos gerados:")
print("1. grafo_culinaria_brasileira.png - Visualização do grafo")
print("2. matriz_coocorrencia.png - Matriz de co-ocorrência entre tipos")
print("3. analise_assortatividade.txt - Análise detalhada")