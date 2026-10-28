# Pendências dos reviews

Tudo o que os reviews antigos (`review.md`, `review-code-review.md`, `review-batimentos.md`) e o briefing da auditoria pediam e a spec responde foi feito, e o `.xlsx` e o `.html` foram conferidos no Excel 16 e no navegador em 28/10/2026. O que sobrou são as sugestões que ficaram de fora, com o motivo.

## Sugestões que ficaram de fora

- **`ler_batimentos` relê a Data, a Chave e os Atributos por Batimento:** o custo cresce com o número de colunas de valor, que costuma ser pequeno. Rever se alguém usar dezenas de Batimentos.
- **`.html` que falha depois do `.xlsx` gravado:** os dois ficariam de execuções diferentes. A spec só cobre a falha do `.xlsx`, e o `.html` aberto no navegador não fica travado no Windows.
- **Gosto, sem defeito nem divergência da spec:** `_do_arquivo` com o mesmo nome no `excel` e no `html`; a tupla de `quadro_do_resumo`; o `"more fields"` do texto do erro do polars (um teste pega se mudar); o ponto trocado por vírgula em dois lugares da leitura; o `_juros` recalculado no `exemplo.py`; o teste que mede o relógio.
- **Fluxo:** o agente `implement-spec` não foi achado nas sessões dos tickets 38 a 43; o motivo segue desconhecido.
