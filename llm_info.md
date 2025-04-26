# Informações sobre o Uso de LLM no Projeto

## Modelo Utilizado
Para este projeto, utilizei o **Gemini** para auxiliar na análise e classificação dos ingredientes da culinária brasileira.

## Prompts Utilizados

### Prompt para Classificação de Ingredientes
```
Por favor, classifique os seguintes ingredientes das receitas brasileiras nas categorias:
- Proteína
- Carboidrato
- Vegetal
- Fruta
- Laticínio
- Gordura
- Condimento
- Outro

Lista de ingredientes:
[lista de ingredientes extraídos das receitas]
```

### Prompt para Detalhamento de Ingredientes
```
Para cada um dos seguintes ingredientes da culinária brasileira, forneça:
1. Classificação (proteína, carboidrato, vegetal, fruta, laticínio, gordura, condimento, outro)
2. Uma breve descrição
3. Valor nutricional principal

Ingredientes:
[lista de ingredientes]
```

## Processo de Extração
As receitas foram coletadas manualmente do site [nome do website], mas utilizei o Gemini para ajudar a classificar e padronizar os nomes dos ingredientes, garantindo consistência na análise de co-ocorrência.