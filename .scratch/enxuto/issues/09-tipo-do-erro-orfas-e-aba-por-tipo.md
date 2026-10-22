# 09: Tipo do Erro (Só em A, Só em B, Sem padrão) e aba Por Tipo do Erro

**What to build:** o analista vê o que explica cada Diferença e quanto cada Tipo pesa. Na Data-base mais recente, cada Chave com Diferença recebe o Tipo do Erro: Só em A, Só em B ou Sem padrão (os padrões de valor entram no ticket 10). A coluna Tipo do Erro entra nas Operações com Diferença, depois de Diferença. Nasce a aba **Por Tipo do Erro**, com as colunas Tipo do Erro, Chaves e Diferença absoluta, ordenada pela Diferença absoluta, e uma nota de que uma Chave pode contar em mais de um Tipo. Ver spec: Solução, Decisões de implementação (Regras/Tipo do Erro, Saída/Por Tipo do Erro); histórias 20, 21 e 27.

**Blocked by:** 08

**Status:** ready-for-agent

- [ ] Seam 1: Chave só em A (com |Valor| > Tolerância) é Só em A; só em B é Só em B; presente nas duas e sem outro Tipo é Sem padrão.
- [ ] Seam 1: o Tipo é calculado só na Data-base mais recente.
- [ ] O Tipo do Erro é texto com os tipos separados por `; ` na ordem da spec (Só em A; Só em B; Sinal invertido; Duplicado; Vírgula deslocada; Dígitos trocados; Sem padrão), pronto para receber vários.
- [ ] Aba `Por Tipo do Erro`: uma linha por Tipo presente, com Chaves e Diferença absoluta (reais), ordenada pela Diferença absoluta decrescente, com a nota de que uma Chave pode contar em mais de um Tipo.
- [ ] O gerador de exemplo planta Só em A, Só em B e Sem padrão no gabarito; o teste de ponta a ponta confere a coluna nas Operações e a aba contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que as Chaves plantadas como Só em A e Só em B aparecem com esse Tipo e que a aba Por Tipo do Erro soma as Chaves e a Diferença absoluta de cada Tipo, com a nota.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
