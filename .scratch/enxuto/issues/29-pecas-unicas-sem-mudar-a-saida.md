# 29: Peças únicas, sem mudar a saída

**What to build:** prefatoração das correções da auditoria, sem mudar o que o usuário vê (a não ser o gerador de exemplo). O `excel` expõe `quadro_do_resumo(resultado)`, os rótulos e os valores do quadro do Resumo, e o Excel e o HTML passam a usá-lo no lugar de cada um juntar rótulos e valores. O corte por limite e o seu aviso ficam numa função só, usada pelas Operações e pelos Erros. Os reais formatados como texto (`1.234,56`) saem de uma função só, usada pela leitura, pelo Excel e pelo HTML. A regra de sinal da linha sem Chave (+Valor na Base A, −Valor na Base B) fica num lugar só no `cruzamento`. O comentário do `excel` e do `html` diz que são os únicos lugares onde os centavos viram reais. O gerador de bases de exemplo aceita o formato sem diferenciar maiúscula (`"CSV"` grava `.csv`). Ver spec: Decisões de implementação (Módulos: `cruzamento`, `excel`, gerador de exemplo), bloco "Decisões de 24/10/2026: correções da auditoria" (Implementação), Testes/Correções da auditoria (o gerador).

**Blocked by:** —

**Status:** ready-for-agent

- [ ] `quadro_do_resumo(resultado)` existe no `excel` e é a única fonte dos rótulos e valores do quadro, no Excel e no HTML.
- [ ] O corte por limite e o aviso de corte saem de uma função só, usada pelas abas Operações com Diferença e Erros.
- [ ] Os reais em texto saem de uma função só, usada pela leitura (Valor das Linhas rejeitadas), pelo Excel (Linha sem Chave) e pelo HTML.
- [ ] A regra de sinal da linha sem Chave está num lugar só no `cruzamento`, usada por todas as contas que a precisam.
- [ ] O comentário do `excel` e do `html` diz que são os únicos lugares onde os centavos viram reais.
- [ ] Teste: o gerador de exemplo com o formato `"CSV"` grava `.csv`.
- [ ] Os testes que já existem passam sem mudar o que conferem: `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q`.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` antes e depois da mudança e conferir que a aba Resumo, as abas Operações com Diferença e Erros e o `.html` mostram os mesmos números e textos.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
