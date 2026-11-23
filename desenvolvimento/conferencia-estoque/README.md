# Desenvolvimento — Conferência de estoque em CSV

Automação independente em Python, com dados fictícios e apenas a biblioteca padrão. Compara o saldo registrado com a contagem física e grava as divergências sem sobrescrever arquivos existentes. Valida duplicatas, quantidades negativas e colunas obrigatórias.

Execute nesta pasta: `python conferir.py sistema.csv contagem.csv relatorio.csv`.

O exemplo gera três linhas: dois cabos a menos na contagem, uma fonte ausente no sistema e um teclado sem contagem. O mouse tem saldo igual e fica fora do relatório. Para repetir, escolha um nome novo para o relatório.

Na entrevista, explique por que “sem contagem” é diferente de “contagem igual a zero”. Mostre como a validação evita que um SKU duplicado substitua silenciosamente uma linha.

**Currículo:** automação de conciliação de estoque em Python, com validação de CSV e geração de relatório de divergências.
