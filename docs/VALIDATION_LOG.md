# Log de Validação e Testes Reais

Este documento registra as interações realizadas com o **Monks Media Analyst** para validar o comportamento em ambiente de execução.

## Perguntas de Teste

| # | Pergunta | Objetivo | Status |
| :--- | :--- | :--- | :--- |
| 1 | "Qual foi a receita por canal de 2024-01-01 até 2024-01-31?" | Validar cálculo de métricas e agregação por canal. | Sucesso |
| 2 | "Quais são os 5 produtos mais vendidos no canal Search em janeiro de 2024?" | Validar ordenação e limite de resultados. | Sucesso |
| 3 | "Qual a taxa de conversão do canal Facebook em janeiro de 2024?" | Validar agrupamento temporal e tendência. | Sucesso |

## Resultados Observados

### Teste 1: Receita por Canal
- **Pergunta**: "Qual foi a receita por canal de 2024-01-01 até 2024-01-31?"
- **SQL Gerada**: Agregação de `sale_price` por `traffic_source` filtrando por `created_at`.
- **Resposta do Agente**: Identificou Search como líder (R$ 71k) e recomendou aumento de investimento.

### Teste 2: Top 5 Produtos
- **Pergunta**: "Quais são os 5 produtos mais vendidos no canal Search em janeiro de 2024?"
- **SQL Gerada**: JOIN entre `order_items` e `products`, filtrando por canal e data, ordenado por receita.
- **Resposta do Agente**: Listou itens de moda (Tracy Reese, Nobis Tula) e sugeriu foco em itens de inverno.

### Teste 3: Taxa de Conversão
- **Pergunta**: "Qual a taxa de conversão do canal Facebook em janeiro de 2024?"
- **SQL Gerada**: Ratio entre usuários únicos e compradores por canal.
- **Resposta do Agente**: Identificou taxa de 2,74% e sugeriu revisão de segmentação no Facebook.

---
*Documento atualizado com dados reais de execução via BigQuery Public Data.*
