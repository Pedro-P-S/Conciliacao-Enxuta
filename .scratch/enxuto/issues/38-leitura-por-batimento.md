# 38: Leitura por Batimento e conciliação de cada um

**What to build:** as colunas `Valor` e `Valor <nome>` (`Valor Juros`, `Valor_Juros`, `valor juros`) são colunas de valor; cada uma presente nas duas bases é um Batimento, na ordem das colunas da Base A, e o `Valor` puro sozinho continua funcionando. A `leitura` devolve, por Batimento, a base (com o Valor daquele Batimento em centavos) e as Linhas rejeitadas; o Valor vazio ou ilegível rejeita a linha só no seu Batimento, a Data vazia ou ilegível em todos, e nenhuma outra coluna de valor vira Atributo. O `conciliar_arquivos` roda o `conciliar` (inalterado) uma vez por Batimento, com a mesma Tolerância, e entrega os Resultados na ordem. Coluna de valor só numa base dá o aviso "Valor Juros só na Base A: não conciliado" na CLI e na GUI e a execução segue; sem nenhum Batimento nas duas bases, para com mensagem simples; sem nenhuma coluna de valor numa base, a mensagem diz que falta a coluna `Valor`. Ver spec: Decisões de implementação (Batimentos), Regras (Colunas de valor e Batimentos; Erros do arquivo inteiro), bloco "Decisões de 27/10/2026", Testes/Vários Batimentos (leitura); histórias 59, 60, 61 e 62.

Atalho provisório, a declarar nas Notas de entrega e a remover nos tickets 40, 41 e 42: enquanto o `excel` e o `html` não mostram vários Batimentos, eles desenham só o primeiro; com um Batimento só, a saída é idêntica à de hoje.

**Blocked by:** —

**Status:** ready-for-agent

- [ ] Teste de leitura: `Valor Juros`, `Valor_Juros` e `valor juros` são o mesmo Batimento (`Juros`); o `Valor` puro sozinho dá o Batimento `Valor`; a ordem é a da Base A.
- [ ] Teste de leitura: o Valor ilegível rejeita a linha só no seu Batimento; a Data ilegível, em todos; uma coluna de valor não vira Atributo em outro Batimento.
- [ ] Teste de ponta a ponta (CLI e `gui_estado`): coluna de valor só numa base dá o aviso e as outras são conciliadas; sem Batimento nas duas bases, mensagem simples sem traceback; sem coluna de valor, a mensagem diz que falta `Valor`; uma coluna de valor repetida continua dando "coluna repetida".
- [ ] Teste de ponta a ponta: duas bases com dois Batimentos conciliam cada um com os seus totais (conferidos pelo `conciliar` de cada Batimento).
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: copiar `exemplo\` para uma pasta com uma coluna `Valor Juros` nas duas bases (mais uma só na Base A), rodar a CLI e conferir o aviso, que o `.xlsx` e o `.html` saem como hoje para o primeiro Batimento e que um arquivo só com `Valor` dá o mesmo resultado de antes.

**Notas de entrega:**
(preencher na entrega)

**Onde está agora (depois da entrega):**
(preencher na entrega)
