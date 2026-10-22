# 11: Aberta desde

**What to build:** o analista vê há quanto tempo cada Diferença está aberta. Para cada Chave com Diferença na Data-base mais recente, o Aberta desde é a primeira Data-base da sequência contínua de Diferença (|Diferença| > Tolerância, nas Data-bases comuns) que chega até a mais recente: se a Diferença some e volta, vale a data da volta; se só muda de valor, a data não muda. Quando a sequência começa na primeira Data-base do arquivo, aparece "DD/MM/AAAA ou antes", e o Resumo avisa quantas Chaves estão assim. A coluna Aberta desde entra nas Operações com Diferença, depois de Tipo do Erro. Ver spec: Decisões de implementação (Regras/Aberta desde, Saída/Resumo — avisos, Saída/Operações com Diferença); histórias 18, 28, 29 e 30.

**Blocked by:** 09

**Status:** ready-for-agent

- [ ] Seam 1: Diferença que some numa Data-base e volta depois tem Aberta desde = data da volta.
- [ ] Seam 1: Diferença que só muda de valor entre Data-bases mantém o Aberta desde original.
- [ ] Seam 1: Diferença que cai para dentro da Tolerância numa Data-base conta como sumida.
- [ ] Seam 1: Diferença presente desde a primeira Data-base é marcada como "ou antes".
- [ ] Operações com Diferença: a coluna Aberta desde mostra `DD/MM/AAAA` ou `DD/MM/AAAA ou antes`.
- [ ] Resumo: o aviso de Chaves abertas desde a primeira Data-base aparece só quando há alguma, com a quantidade, e é o primeiro da lista de avisos (ordem da spec: Aberta desde a primeira Data-base, linhas sem Chave, Data-bases ignoradas, corte).
- [ ] O gerador de exemplo planta Chaves que somem e voltam, que mudam de valor e que já existem na primeira Data-base; o teste de ponta a ponta confere o Aberta desde e o aviso contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre o `exemplo\` de seis meses e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) o Aberta desde das Chaves plantadas (some e volta, muda de valor, "ou antes") e o aviso no Resumo.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
