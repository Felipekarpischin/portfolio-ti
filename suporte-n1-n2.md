# Chamado fictício: estoque recusa a baixa

**Relato:** “Não consigo dar baixa de 12 cabos. O sistema está fora?”

## N1 — Coleta e triagem

Registre SKU, quantidade, horário, mensagem e impacto. Consulte o saldo e confira se o serviço responde. Neste caso, o produto CABO-01 começa com 10 unidades.

## N2 — Reprodução e confirmação

Na pasta do projeto, inicie a API com um arquivo de banco ainda inexistente:

```powershell
python estoque.py --db chamado-demo.db
```

Se já usou esse nome, escolha outro para começar com saldo 10 e histórico vazio. Em outro terminal, na mesma pasta, execute:

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/movimentos -H "Content-Type: application/json" --data-binary '@saida-invalida.json'
Invoke-RestMethod 'http://127.0.0.1:8000/produtos'
Invoke-RestMethod 'http://127.0.0.1:8000/movimentos'
```

Resultado esperado: HTTP 409, erro estoque_insuficiente, saldo 10 e histórico vazio. O terminal do servidor registra método, rota e status. Em seguida, faça a saída válida do README e confirme saldo 7 e uma movimentação no histórico.

Conferência opcional em um leitor SQLite:

```sql
SELECT sku, quantity FROM products WHERE sku = 'CABO-01';
SELECT id, delta, balance FROM movements WHERE sku = 'CABO-01' ORDER BY id;
```

## Resposta e escalonamento

> Conferi o item CABO-01. O sistema registra 10 unidades e a baixa solicitada era de 12. O saldo foi preservado. Confira a quantidade solicitada. Se o estoque físico estiver diferente, verifique com o responsável se há alguma entrada pendente de registro.

Se a rejeição persistir com saldo suficiente, encaminhe o caso ao time de produto com SKU, horário, quantidade, status e passos de reprodução. Inclua apenas registros pertinentes. Não altere o saldo diretamente.

