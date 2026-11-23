# Portfólio de TI · Suporte e Desenvolvimento

Quatro demonstrações com dados fictícios e exemplos que rodam localmente com Python 3.11 ou superior, sem dependências externas.

| Área | Projeto | O que demonstra |
|---|---|---|
| Suporte | [Diagnóstico de chamado ERP](suporte-n1-n2.md) | Reprodução via HTTP, conferência de saldo com SQL e orientação ao usuário |
| Suporte | [Triagem de incidentes HTTP](suporte/triagem-http/README.md) | Interpretação de erros 5xx, latência e timeouts |
| Desenvolvimento | [API de estoque](#api-de-estoque-para-erp) | JSON, SQLite, transações e tratamento de erros |
| Desenvolvimento | [Conferência de estoque em CSV](desenvolvimento/conferencia-estoque/README.md) | Validação de dados e geração de relatório de divergências |

## API de estoque para ERP

Projeto de estudo com dados fictícios. Usa Python 3 e SQLite, sem dependências externas. Registra entradas e saídas e guarda o histórico. A transação protege a atualização de saldo e histórico. A API roda localmente, sem autenticação.

No PowerShell, nesta pasta, rode:

```powershell
python estoque.py
```

Em outro terminal, na mesma pasta:

```powershell
$api = 'http://127.0.0.1:8000'
Invoke-RestMethod "$api/produtos"
Invoke-RestMethod "$api/movimentos" -Method Post -ContentType 'application/json' -Body '{"sku":"CABO-01","quantidade":-3}'
Invoke-RestMethod "$api/movimentos"
```

O banco começa com 10 cabos. Uma saída de 3 deixa saldo 7. Para começar outra demonstração, use um nome de arquivo ainda inexistente: `python estoque.py --db nova-demo.db`. Quantidade positiva registra entrada. A API retorna 400 para dados inválidos, 404 para produto desconhecido e 409 para saldo insuficiente.

**Em entrevista:** demonstre uma saída válida e explique como a transação impede que pedidos simultâneos gastem o mesmo saldo.

## Laboratório de suporte N1/N2

Abra o [roteiro do chamado](suporte-n1-n2.md). Ele usa a API acima para reproduzir uma falha reportada, interpretar HTTP 409, conferir o saldo e orientar o usuário.

## Texto para o currículo após praticar

- **Suporte de sistemas:** laboratório de suporte com reprodução de chamado via API REST, conferência de saldo em SQLite e documentação da solução.
- **Desenvolvimento júnior:** projeto de estudo de API de estoque em Python e SQLite, com movimentações transacionais, validação de saldo e histórico.

## Testes reproduzíveis

Na raiz do projeto, execute `python -m unittest -v`. Os testes usam um banco temporário e uma porta local livre para verificar as respostas da API e duas baixas concorrentes. Também exercitam entradas inválidas da triagem HTTP.

