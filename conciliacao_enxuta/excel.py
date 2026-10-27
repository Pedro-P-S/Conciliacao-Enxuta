"""Resultado → `.xlsx`. Este módulo e o `html` são os únicos lugares onde os centavos viram reais."""

from __future__ import annotations

from pathlib import Path

import openpyxl
import polars as pl
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from conciliacao_enxuta.cruzamento import Resultado

# Código de formato do Excel; no Excel em português aparece como #.##0,00.
FORMATO_REAIS = "#,##0.00"
FORMATO_DATA = "DD/MM/YYYY"
# A célula continua data, para ordenar e filtrar; só o que o Excel mostra ganha o " ou antes".
FORMATO_DATA_OU_ANTES = 'DD/MM/YYYY" ou antes"'
FORMATO_INTEIRO = "#,##0"
FORMATO_PERCENTUAL = "0.00%"
TITULOS_SEM_CHAVE = ("Linhas sem Chave, fora do cruzamento", "Linhas", "Soma")
TITULO_PROBLEMATICOS = "Atributos Problemáticos"
TITULOS_POR_ATRIBUTO = ("Atributo", "Valor", "Diferença absoluta", "Diferença acima do peso")
TITULO_GRAFICO_DA_IDADE = "Diferença absoluta por Idade da Diferença"
TITULO_GRAFICO_DO_HISTORICO = "Diferença absoluta por Data-base"
NOTA_POR_TIPO = "Uma Chave pode contar em mais de um Tipo do Erro."
LIMITE_DE_LINHAS = 700_000
# Os avisos de corte, com o limite e o total já com separador de milhar
CORTE_DAS_OPERACOES = "Nem todas as operações com diferença couberam: mostrando {limite} de {total}, as maiores."
CORTE_DOS_ERROS = "Nem todos os erros couberam: mostrando {limite} de {total}."


def quadro_do_resumo(resultado: Resultado) -> list[tuple[str, object, str, str]]:
    """O quadro do Resumo, o mesmo no `.xlsx` e no `.html`: (rótulo, valor no Excel, formato no Excel, texto)."""
    em_reais = [
        ("Tolerância", resultado.tolerancia),
        ("Total A", resultado.total_a),
        ("Total B", resultado.total_b),
        ("Diferença total", resultado.diferenca_total),
        ("Diferença absoluta", resultado.diferenca_absoluta),
    ]
    return [
        ("Data-base mais recente", resultado.data_base, FORMATO_DATA, f"{resultado.data_base:%d/%m/%Y}"),
        *((rotulo, centavos / 100, FORMATO_REAIS, reais(centavos)) for rotulo, centavos in em_reais),
        (
            "Chaves com Diferença",
            resultado.chaves_com_diferenca,
            FORMATO_INTEIRO,
            milhar(resultado.chaves_com_diferenca),
        ),
    ]


def cortar(tabela: pl.DataFrame, limite: int, aviso: str) -> tuple[pl.DataFrame, str | None]:
    """As `limite` primeiras linhas de `tabela` e o `aviso` do corte (CORTE_DAS_OPERACOES ou CORTE_DOS_ERROS)
    preenchido; sem corte, a tabela inteira e None."""
    if tabela.height <= limite:
        return tabela, None
    return tabela.head(limite), aviso.format(limite=milhar(limite), total=milhar(tabela.height))


def avisos(resultado: Resultado, limite: int, operacoes: int | None = None) -> list[str]:
    """Os avisos do Resumo que acontecem: Linhas rejeitadas e corte das operações acima de `limite`.

    `operacoes` é o total de operações da aba inteira, quando a aba junta vários Batimentos."""
    lista = []
    if resultado.rejeitadas.height:
        lista.append(f"Linhas rejeitadas: {milhar(resultado.rejeitadas.height)} (veja a aba Erros)")
    total = resultado.operacoes.height if operacoes is None else operacoes
    if total > limite:
        lista.append(CORTE_DAS_OPERACOES.format(limite=milhar(limite), total=milhar(total)))
    return lista


def milhar(numero: int) -> str:
    """700000 → '700.000'."""
    return f"{numero:,}".replace(",", ".")


def reais(centavos: int, sinal: str = "-") -> str:
    """Centavos → `1.234,56`, ou `-1.234,56` (com `sinal` no negativo), como o Excel mostra `#.##0,00`."""
    inteiro, resto = divmod(abs(centavos), 100)
    return f"{sinal if centavos < 0 else ''}{milhar(inteiro)},{resto:02d}"


def _do_arquivo(ws, linha: int, coluna: int, valor):
    """Grava na célula um valor que veio do arquivo (Chave, Atributo, conteúdo de Linha rejeitada).

    O texto perde os caracteres de controle, que o Excel não aceita, e fica texto mesmo começando com `=`.
    """
    if not isinstance(valor, str):
        return ws.cell(linha, coluna, valor)
    celula = ws.cell(linha, coluna, ILLEGAL_CHARACTERS_RE.sub("", valor))
    celula.data_type = "s"  # sem isto o openpyxl grava como fórmula
    return celula


def _linha_sem_chave(casa: list[dict] | None) -> str | None:
    """As linhas sem Chave que casam com a Chave, como `−10.000,00 em 15/03/2026 na Base B`, separadas por `; `."""
    if not casa:
        return None
    textos = [
        f"{reais(linha['Valor'], sinal='−')} em {linha['Data']:%d/%m/%Y} na Base {linha['Base']}" for linha in casa
    ]
    return "; ".join(textos)


def gravar_excel(resultados: list[Resultado], pasta: str | Path, limite: int = LIMITE_DE_LINHAS) -> Path:
    """Grava `conciliacao_AAAA-MM-DD.xlsx` em `pasta`, sobrescrevendo, e devolve o caminho.

    `resultados` são os Batimentos, na ordem da Base A. As quatro abas de tabelas trazem a coluna Batimento na
    frente; cada uma mostra no máximo `limite` linhas.
    """
    # shortcut: o Resumo e os gráficos desenham só o primeiro Batimento, até o ticket 41
    resultado = resultados[0]
    caminho = Path(pasta) / f"conciliacao_{resultado.data_base.isoformat()}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resumo"

    quadro = quadro_do_resumo(resultado)
    for linha, (rotulo, valor, formato, _) in enumerate(quadro, start=1):
        ws.cell(linha, 1, rotulo).font = Font(bold=True)
        ws.cell(linha, 2, valor).number_format = formato

    # Avisos, só quando acontecem, a partir de uma linha abaixo do quadro
    linha = len(quadro) + 2
    if resultado.sem_chave_a.linhas or resultado.sem_chave_b.linhas:
        for coluna, titulo in enumerate(TITULOS_SEM_CHAVE, start=1):
            ws.cell(linha, coluna, titulo).font = Font(bold=True)
        for base, sem_chave in [("Base A", resultado.sem_chave_a), ("Base B", resultado.sem_chave_b)]:
            linha += 1
            ws.cell(linha, 1, base)
            ws.cell(linha, 2, sem_chave.linhas).number_format = FORMATO_INTEIRO
            ws.cell(linha, 3, sem_chave.soma / 100).number_format = FORMATO_REAIS
        linha += 2

    for linha, aviso in enumerate(
        avisos(resultado, limite, sum(r.operacoes.height for r in resultados)), start=linha
    ):
        ws.cell(linha, 1, aviso)

    # Os Atributos Problemáticos, uma linha abaixo dos avisos; sem Atributo acima do peso, a tabela não aparece
    if resultado.atributos_problematicos.height:
        linha = ws.max_row + 2
        ws.cell(linha, 1, TITULO_PROBLEMATICOS).font = Font(bold=True)
        _tabela_por_atributo(ws, linha + 1, resultado.atributos_problematicos)

    ws.column_dimensions["A"].width = 36
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 22

    _aba_por_tipo(wb, resultados)
    _aba_por_atributo(wb, resultados)
    _aba_operacoes(wb, resultados, limite)
    _aba_erros(wb, resultados, limite)
    _graficos(wb, ws, resultado)

    wb.save(caminho)
    return caminho


def rotulo_da_faixa(faixa: str, chaves: int, linhas: int) -> str:
    """`31 a 90 dias (12 Chaves)`, ou `91 a 365 dias (12 Chaves, 1 linha sem Chave)` quando há linhas sem Chave."""
    rotulo = f"{faixa} ({milhar(chaves)} {'Chave' if chaves == 1 else 'Chaves'}"
    if linhas:
        rotulo += f", {milhar(linhas)} {'linha' if linhas == 1 else 'linhas'} sem Chave"
    return rotulo + ")"


def _graficos(wb: openpyxl.Workbook, resumo, resultado: Resultado) -> None:
    """Abaixo de tudo no Resumo, o gráfico de barras da Idade e, abaixo dele, o de linha da Diferença absoluta por
    Data-base. Os dados vão na aba oculta `_grafico`: a linha nas colunas A e B, as barras nas colunas D e E."""
    dados = wb.create_sheet("_grafico")
    dados.sheet_state = "hidden"
    dados.append(["Data-base", "Diferença absoluta"])
    for data, absoluta in resultado.historico:
        dados.append([data, absoluta / 100])
        linha = dados.max_row
        dados.cell(linha, 1).number_format = FORMATO_DATA
        dados.cell(linha, 2).number_format = FORMATO_REAIS
    fim_da_linha = dados.max_row

    dados.cell(1, 4, "Idade da Diferença")
    dados.cell(1, 5, "Diferença absoluta")
    for linha, (faixa, chaves, linhas, absoluta) in enumerate(resultado.por_idade, start=2):
        dados.cell(linha, 4, rotulo_da_faixa(faixa, chaves, linhas))
        dados.cell(linha, 5, absoluta / 100).number_format = FORMATO_REAIS
    fim_das_barras = len(resultado.por_idade) + 1

    barras = BarChart()
    barras.title = TITULO_GRAFICO_DA_IDADE
    barras.add_data(Reference(dados, min_col=5, min_row=1, max_row=fim_das_barras), titles_from_data=True)
    barras.set_categories(Reference(dados, min_col=4, min_row=2, max_row=fim_das_barras))

    linha_no_tempo = LineChart()
    linha_no_tempo.title = TITULO_GRAFICO_DO_HISTORICO
    linha_no_tempo.add_data(Reference(dados, min_col=2, min_row=1, max_row=fim_da_linha), titles_from_data=True)
    linha_no_tempo.set_categories(Reference(dados, min_col=1, min_row=2, max_row=fim_da_linha))
    # Sem isto o Excel pinta cada trecho de uma cor e suaviza a linha
    linha_no_tempo.varyColors = False
    linha_no_tempo.series[0].smooth = False

    for grafico in (barras, linha_no_tempo):
        grafico.legend = None
        grafico.title.overlay = False  # sem isto o Excel desenha o título por cima da área do gráfico
        grafico.width, grafico.height = 24, 9
        grafico.y_axis.number_format = FORMATO_REAIS
        # No openpyxl 3.1 os eixos somem no Excel se não forem marcados como visíveis
        grafico.x_axis.delete = grafico.y_axis.delete = False

    inicio = resumo.max_row + 2
    resumo.add_chart(barras, f"A{inicio}")
    resumo.add_chart(linha_no_tempo, f"A{inicio + 20}")  # 9 cm de altura ocupam umas 17 linhas


def _com_batimento(resultados: list[Resultado], campo: str) -> pl.DataFrame:
    """A tabela `campo` de cada Resultado, uma depois da outra, com a coluna Batimento na frente."""
    return pl.concat([getattr(r, campo).select(pl.lit(r.batimento).alias("Batimento"), pl.all()) for r in resultados])


def _aba_por_tipo(wb: openpyxl.Workbook, resultados: list[Resultado]) -> None:
    """Quanto cada Tipo do Erro explica, por Batimento e na ordem do Resultado, e a nota abaixo da tabela."""
    ws = wb.create_sheet("Por Tipo do Erro")
    tabela = _com_batimento(resultados, "por_tipo")
    for coluna, titulo in enumerate(["Batimento", "Tipo do Erro", "Chaves", "Diferença absoluta"], start=1):
        ws.cell(1, coluna, titulo).font = Font(bold=True)
    for linha, (batimento, tipo, chaves, absoluta) in enumerate(tabela.iter_rows(), start=2):
        _do_arquivo(ws, linha, 1, batimento)
        ws.cell(linha, 2, tipo)
        ws.cell(linha, 3, chaves).number_format = FORMATO_INTEIRO
        ws.cell(linha, 4, absoluta / 100).number_format = FORMATO_REAIS
    ws.auto_filter.ref = f"A1:D{tabela.height + 1}"
    ws.cell(tabela.height + 3, 1, NOTA_POR_TIPO)  # uma linha em branco abaixo da tabela
    for letra, largura in zip("ABCD", (16, 24, 12, 20)):
        ws.column_dimensions[letra].width = largura


def _aba_por_atributo(wb: openpyxl.Workbook, resultados: list[Resultado]) -> None:
    """Os valores de Atributo com Diferença acima do peso, por Batimento e na ordem do Resultado (do maior para o
    menor); com filtro.

    Sem Atributo nas bases, fica só o cabeçalho.
    """
    ws = wb.create_sheet("Por Atributo")
    tabela = _com_batimento(resultados, "por_atributo")
    _tabela_por_atributo(ws, 1, tabela, com_batimento=True)
    ws.auto_filter.ref = f"A1:E{tabela.height + 1}"
    for letra, largura in zip("ABCDE", (16, 24, 24, 20, 16)):
        ws.column_dimensions[letra].width = largura


def _tabela_por_atributo(ws, linha_do_cabecalho: int, tabela, com_batimento: bool = False) -> None:
    """Cabeçalho e linhas de uma tabela no formato de `Resultado.por_atributo`, a partir de `linha_do_cabecalho`;
    com `com_batimento`, a tabela traz o Batimento como primeira coluna."""
    titulos = (("Batimento",) if com_batimento else ()) + TITULOS_POR_ATRIBUTO
    for coluna, titulo in enumerate(titulos, start=1):
        ws.cell(linha_do_cabecalho, coluna, titulo).font = Font(bold=True)
    for linha, valores in enumerate(tabela.iter_rows(), start=linha_do_cabecalho + 1):
        for coluna, valor in enumerate(valores[:-2], start=1):
            _do_arquivo(ws, linha, coluna, valor)
        ws.cell(linha, len(titulos) - 1, valores[-2] / 100).number_format = FORMATO_REAIS
        ws.cell(linha, len(titulos), valores[-1]).number_format = FORMATO_PERCENTUAL


def _aviso_na_linha_1(ws, aviso: str | None) -> int:
    """Escreve o aviso de corte, se houver, na linha 1; devolve a linha do cabeçalho (2 com aviso, 1 sem)."""
    if not aviso:
        return 1
    ws.cell(1, 1, aviso).font = Font(bold=True)
    return 2


def _aba_operacoes(wb: openpyxl.Workbook, resultados: list[Resultado], limite: int) -> None:
    """As Chaves com Diferença, uma por linha, por Batimento e na ordem do Resultado; cabeçalho congelado e com filtro.

    Depois do Aberta desde vêm a Linha sem Chave e os Atributos, com o nome original. O limite é da aba inteira:
    acima dele ficam as maiores Diferenças absolutas de todos os Batimentos; quando há corte, o aviso vai na linha 1
    e o cabeçalho passa para a linha 2.
    """
    ws = wb.create_sheet("Operações com Diferença")
    todas = _com_batimento(resultados, "operacoes").with_row_index("_i")
    atributos = pl.concat([r.atributos for r in resultados], how="diagonal")  # alinhados com `todas` pela ordem
    # Corta pelas maiores (o sort é estável) e volta à ordem por Batimento
    por_tamanho = todas.sort(pl.col("Diferenca").abs(), descending=True, maintain_order=True)
    operacoes, aviso = cortar(por_tamanho, limite, CORTE_DAS_OPERACOES)
    operacoes = operacoes.sort("_i")
    if atributos.width:  # sem Atributo, o DataFrame não tem linhas
        atributos = atributos[operacoes["_i"].to_list()]
    linha_do_cabecalho = _aviso_na_linha_1(ws, aviso)
    titulos = [
        "Batimento", "Chave", "Valor A", "Valor B", "Diferença absoluta", "Tipo do Erro", "Aberta desde",
        "Linha sem Chave",
    ]
    primeiro_atributo = len(titulos) + 1
    titulos += atributos.columns
    for coluna, titulo in enumerate(titulos, start=1):
        _do_arquivo(ws, linha_do_cabecalho, coluna, titulo).font = Font(bold=True)
    for linha, (_, batimento, chave, a, b, diferenca, tipo, desde, ou_antes, casa) in enumerate(
        operacoes.iter_rows(), start=linha_do_cabecalho + 1
    ):
        _do_arquivo(ws, linha, 1, batimento)
        _do_arquivo(ws, linha, 2, chave)
        # Valor A e Valor B com o sinal; a Diferença sem
        for coluna, centavos in enumerate((a, b, abs(diferenca)), start=3):
            ws.cell(linha, coluna, centavos / 100).number_format = FORMATO_REAIS
        ws.cell(linha, 6, tipo)
        ws.cell(linha, 7, desde).number_format = FORMATO_DATA_OU_ANTES if ou_antes else FORMATO_DATA
        ws.cell(linha, 8, _linha_sem_chave(casa))
    for coluna, atributo in enumerate(atributos.iter_columns(), start=primeiro_atributo):
        for linha, valor in enumerate(atributo, start=linha_do_cabecalho + 1):
            _do_arquivo(ws, linha, coluna, valor)
        ws.column_dimensions[get_column_letter(coluna)].width = 18
    ws.freeze_panes = f"A{linha_do_cabecalho + 1}"
    ws.auto_filter.ref = f"A{linha_do_cabecalho}:{get_column_letter(len(titulos))}{linha_do_cabecalho + operacoes.height}"
    for letra, largura in zip("ABCDEFGH", (16, 24, 18, 18, 18, 24, 22, 36)):
        ws.column_dimensions[letra].width = largura


def _erros_do_batimento(resultado: Resultado, primeiro: bool) -> pl.DataFrame:
    """As Data-bases ignoradas, em ordem de data, e depois as Linhas rejeitadas da Base A e da Base B, com a coluna
    Batimento na frente: `Todos` para o que vale para todos (a Data-base ignorada e a Linha rejeitada pela Data) e o
    nome do Batimento para a rejeitada pelo Valor. Só o `primeiro` Batimento traz o que vale para todos."""
    ignoradas = sorted(
        [(d, "Base A") for d in resultado.data_bases_so_em_a] + [(d, "Base B") for d in resultado.data_bases_so_em_b]
    )
    # A Data vai como texto, como a das Linhas rejeitadas, para a coluna ter um tipo só
    data_bases = pl.DataFrame(
        {
            "Base": [base for _, base in ignoradas],
            "Data": [f"{d:%d/%m/%Y}" for d, _ in ignoradas],
            "Motivo": [f"Data-base só na {base}" for _, base in ignoradas],
        },
        schema={"Base": pl.String, "Data": pl.String, "Motivo": pl.String},
    )
    erros = pl.concat([data_bases, resultado.rejeitadas], how="diagonal").select(resultado.rejeitadas.columns)
    pelo_valor = pl.col("Motivo").str.starts_with("Valor")
    if not primeiro:
        erros = erros.filter(pelo_valor)
    return erros.select(
        pl.when(pelo_valor).then(pl.lit(resultado.batimento)).otherwise(pl.lit("Todos")).alias("Batimento"), pl.all()
    )


def _aba_erros(wb: openpyxl.Workbook, resultados: list[Resultado], limite: int) -> None:
    """Por Batimento, as Data-bases ignoradas e as Linhas rejeitadas (ver `_erros_do_batimento`); cabeçalho
    congelado e com filtro.

    Existe sempre: sem erros, fica só o cabeçalho. Mostra só os `limite` primeiros da aba inteira; quando há corte,
    o aviso vai na linha 1 e o cabeçalho passa para a linha 2.
    """
    ws = wb.create_sheet("Erros")
    erros = pl.concat([_erros_do_batimento(r, i == 0) for i, r in enumerate(resultados)])
    erros, aviso = cortar(erros, limite, CORTE_DOS_ERROS)
    linha_do_cabecalho = _aviso_na_linha_1(ws, aviso)
    for coluna, titulo in enumerate(erros.columns, start=1):
        ws.cell(linha_do_cabecalho, coluna, titulo).font = Font(bold=True)
    for linha, valores in enumerate(erros.iter_rows(), start=linha_do_cabecalho + 1):
        for coluna, valor in enumerate(valores, start=1):
            _do_arquivo(ws, linha, coluna, valor)
    ws.freeze_panes = f"A{linha_do_cabecalho + 1}"
    ws.auto_filter.ref = f"A{linha_do_cabecalho}:G{linha_do_cabecalho + erros.height}"
    for letra, largura in zip("ABCDEFG", (16, 10, 10, 24, 14, 18, 18)):
        ws.column_dimensions[letra].width = largura
