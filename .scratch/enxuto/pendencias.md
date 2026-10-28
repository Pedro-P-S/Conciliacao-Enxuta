# Pendências dos reviews

Tudo o que os reviews antigos (`review.md`, `review-code-review.md`, `review-batimentos.md`) e o briefing da auditoria pediam e a spec responde foi feito. O que sobrou está aqui: o que não dá para conferir sem um humano e as sugestões que ficaram de fora, com o motivo.

## Conferir à mão

- **O `.xlsx` num Excel de verdade:** as fórmulas do Resumo com vários Batimentos (lista suspensa, `INDEX`/`MATCH` na `_grafico`) só foram conferidas pelo avaliador de `tests/conftest.py`; falta abrir no Excel e trocar o Batimento na lista.
- **O `.html` no navegador:** o rótulo do valor no fim da linha, a dica ao passar o mouse e a troca do Batimento na lista.

## Sugestões que ficaram de fora

- **A Tolerância com regras próprias de separador** (`cli.tolerancia_em_centavos`): reaproveitar o `_centavos` da leitura mudaria o arredondamento (hoje meio para o par, lá meio para longe do zero), e a spec manda deixá-lo como está.
- **Dois caminhos do Resumo do Excel** (`_resumo_de_um` e `_resumo_com_lista`): usar só o com lista mudaria o Resumo de um Batimento só (lista no topo e fórmulas no lugar de valores), que a spec quer sem lista.
- **`ler_batimentos` relê a Data, a Chave e os Atributos por Batimento:** o custo cresce com o número de colunas de valor, que costuma ser pequeno. Rever se alguém usar dezenas de Batimentos.
- **`.html` que falha depois do `.xlsx` gravado:** os dois ficariam de execuções diferentes. A spec só cobre a falha do `.xlsx`, e o `.html` aberto no navegador não fica travado no Windows.
- **Gosto, sem defeito nem divergência da spec:** `_do_arquivo` com o mesmo nome no `excel` e no `html`; a tupla de `quadro_do_resumo`; o `"more fields"` do texto do erro do polars (um teste pega se mudar); o ponto trocado por vírgula em dois lugares da leitura; o parâmetro `com_batimento` de `_tabela_por_atributo`; o `_juros` recalculado no `exemplo.py`; o teste que mede o relógio.
- **Fluxo:** o agente `implement-spec` não foi achado nas sessões dos tickets 38 a 43; o motivo segue desconhecido.
