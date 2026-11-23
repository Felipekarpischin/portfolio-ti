# Suporte — Triagem de incidentes HTTP

Laboratório fictício. Em uma janela de atendimento, usuários relatam lentidão e falhas ao acessar um sistema web. Recebemos um CSV com status HTTP e latência. Código 0 representa timeout registrado pelo monitor.

Execute nesta pasta: `python triagem.py monitoramento.csv`.

Resultado esperado: seis medições, dois HTTP 5xx, um timeout, duas respostas com latência de pelo menos 800 ms e mediana geral de 605 ms. A mediana inclui o tempo de espera do timeout. O total de respostas lentas considera apenas requisições com resposta HTTP e inclui respostas com erro.

Na entrevista, explique como diferenciaria erro do servidor, timeout e lentidão. Os dados justificam escalar para investigação. Para localizar a causa, peça horário, rota, ID de requisição e logs do serviço, e compare o período com uma janela sem incidentes.

**Currículo:** laboratório de triagem de incidentes HTTP, com análise de latência, erros 5xx e timeouts, e roteiro de escalonamento.

