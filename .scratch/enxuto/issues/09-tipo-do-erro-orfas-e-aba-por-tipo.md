# 09: Tipo do Erro (Só em A, Só em B, Sem padrão) e aba Por Tipo do Erro

**What to build:** o analista vê o que explica cada Diferença e quanto cada Tipo pesa. Na Data-base mais recente, cada Chave com Diferença recebe o Tipo do Erro: Só em A, Só em B ou Sem padrão (os padrões de valor entram no ticket 10). A coluna Tipo do Erro entra nas Operações com Diferença, depois de Diferença. Nasce a aba **Por Tipo do Erro**, com as colunas Tipo do Erro, Chaves e Diferença absoluta, ordenada pela Diferença absoluta, e uma nota de que uma Chave pode contar em mais de um Tipo. Ver spec: Solução, Decisões de implementação (Regras/Tipo do Erro, Saída/Por Tipo do Erro); histórias 20, 21 e 27.

**Blocked by:** 08

**Status:** done

- [x] Seam 1: Chave só em A (com |Valor| > Tolerância) é Só em A; só em B é Só em B; presente nas duas e sem outro Tipo é Sem padrão.
- [x] Seam 1: o Tipo é calculado só na Data-base mais recente.
- [x] O Tipo do Erro é texto com os tipos separados por `; ` na ordem da spec (Só em A; Só em B; Sinal invertido; Duplicado; Vírgula deslocada; Dígitos trocados; Sem padrão), pronto para receber vários.
- [x] Aba `Por Tipo do Erro`: uma linha por Tipo presente, com Chaves e Diferença absoluta (reais), ordenada pela Diferença absoluta decrescente, com a nota de que uma Chave pode contar em mais de um Tipo.
- [x] O gerador de exemplo planta Só em A, Só em B e Sem padrão no gabarito; o teste de ponta a ponta confere a coluna nas Operações e a aba contra o gabarito.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que as Chaves plantadas como Só em A e Só em B aparecem com esse Tipo e que a aba Por Tipo do Erro soma as Chaves e a Diferença absoluta de cada Tipo, com a nota.

**Notas de entrega:**

- `conciliacao_enxuta/cruzamento.py`: `Resultado.operacoes` ganhou a coluna `Tipo`, calculada só nas Chaves com Diferença da Data-base mais recente por `_tipo_do_erro()`. É uma lista ordenada de (nome, condição) juntada com `SEPARADOR_DE_TIPOS` (`; `), e o ticket 10 só acrescenta itens nela. Vale Só em A quando B é nulo (a Chave não está na Base B), Só em B quando A é nulo e Sem padrão quando nenhum se aplica. Uma Chave presente nas duas com valor 0 num lado é Sem padrão, não órfã. O campo novo `Resultado.por_tipo` (Tipo, Chaves, Absoluta em centavos) separa os Tipos pelo `; `, de modo que a Chave conta em cada Tipo que tem. Ordena pela Absoluta decrescente e desempata pelo nome.
- `conciliacao_enxuta/excel.py`: a aba `Por Tipo do Erro`, entre o Resumo e as Operações, tem as colunas Tipo do Erro, Chaves e Diferença absoluta e, uma linha abaixo da tabela, a nota "Uma Chave pode contar em mais de um Tipo do Erro.". As Operações com Diferença ganharam a coluna Tipo do Erro depois de Diferença, e o filtro agora vai até a coluna E.
- `conciliacao_enxuta/exemplo.py`: `_posicao` devolve o Tipo plantado em cada Chave com Diferença. O `Gabarito` ganhou o Tipo em `operacoes` e o campo `por_tipo`.
- Testes: `tests/test_cruzamento.py` (Só em A, Só em B e Sem padrão; zero num lado não é órfã; Tipo só na Data-base mais recente; tabela por Tipo) e `tests/test_ponta_a_ponta.py` (abas; coluna Tipo do Erro; aba Por Tipo do Erro contra o gabarito; aba sem Chaves com Diferença, só com o cabeçalho e a nota).
- Olhos de usuário: no `exemplo\`, C00003 aparece como Só em A e C00004 como Só em B. A aba Por Tipo do Erro traz Só em B 20 / 1.156.604,30, Só em A 20 / 988.285,09 e Sem padrão 20 / 42.064,18, mais a nota, e bate com a soma feita sobre as Operações.

**Onde está agora (depois da entrega):** o Tipo do Erro mostra Só em A, Só em B e Sem padrão, e a aba Por Tipo do Erro já existe. O ticket 10 acrescenta os padrões de valor à lista de `_tipo_do_erro` em `cruzamento.py` e planta esses padrões no gerador de exemplo. Não há commit: quem commita é o orquestrador.
