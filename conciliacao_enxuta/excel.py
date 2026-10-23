"""Resultado → `.xlsx`. É aqui, e só aqui, que centavos viram reais."""

from __future__ import annotations

from pathlib import Path

import openpyxl
import polars as pl
from openpyxl.chart import LineChart, Reference
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
TITULO_PROBLEMATICOS = "Atributos Problemáticos"
NOTA_POR_TIPO = "Uma Chave pode contar em mais de um Tipo do Erro."
LIMITE_DE_LINHAS = 700_000


def _aviso_de_corte(limite: int, total: int) -> str:
    """O aviso de que a aba Operações com Diferença mostra só as `limite` maiores de `total`."""
    return (
        f"Nem todas as operações com diferença couberam: mostrando {_milhar(limite)} de {_milhar(total)}, "
        "as maiores."
    )


def _milhar(numero: int) -> str:
    """700000 → '700.000'."""
    return f"{numero:,}".replace(",", ".")


def _linha_sem_chave(casa: list[dict] | None) -> str | None:
    """As linhas sem Chave que casam com a Chave, como `−10.000,00 em 15/03/2026 na Base B`, separadas por `; `."""
    if not casa:
        return None
    textos = []
    for linha in casa:
        reais, centavos = divmod(abs(linha["Valor"]), 100)
        sinal = "−" if linha["Valor"] < 0 else ""
        textos.append(f"{sinal}{_milhar(reais)},{centavos:02d} em {linha['Data']:%d/%m/%Y} na Base {linha['Base']}")
    return "; ".join(textos)


def gravar_excel(resultado: Resultado, pasta: str | Path, limite: int = LIMITE_DE_LINHAS) -> Path:
    """Grava `conciliacao_AAAA-MM-DD.xlsx` em `pasta`, sobrescrevendo, e devolve o caminho.

    A aba Operações com Diferença mostra no máximo `limite` linhas, as maiores.
    """
    caminho = Path(pasta) / f"conciliacao_{resultado.data_base.isoformat()}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resumo"

    quadro = [
        ("Data-base mais recente", resultado.data_base, FORMATO_DATA),
        ("Tolerância", resultado.tolerancia / 100, FORMATO_REAIS),
        ("Total A", resultado.total_a / 100, FORMATO_REAIS),
        ("Total B", resultado.total_b / 100, FORMATO_REAIS),
        ("Diferença total", resultado.diferenca_total / 100, FORMATO_REAIS),
        ("Diferença absoluta", resultado.diferenca_absoluta / 100, FORMATO_REAIS),
        ("Chaves com Diferença", resultado.chaves_com_diferenca, FORMATO_INTEIRO),
    ]
    for linha, (rotulo, valor, formato) in enumerate(quadro, start=1):
        ws.cell(linha, 1, rotulo).font = Font(bold=True)
        ws.cell(linha, 2, valor).number_format = formato

    # A Idade da Diferença, uma linha abaixo do quadro: as 5 faixas sempre, mesmo vazias
    linha = len(quadro) + 2
    for coluna, titulo in enumerate(["Idade da Diferença", "Chaves", "Diferença absoluta"], start=1):
        ws.cell(linha, coluna, titulo).font = Font(bold=True)
    for faixa, chaves, absoluta in resultado.por_idade:
        linha += 1
        ws.cell(linha, 1, faixa)
        ws.cell(linha, 2, chaves).number_format = FORMATO_INTEIRO
        ws.cell(linha, 3, absoluta / 100).number_format = FORMATO_REAIS

    # Avisos, só quando acontecem, a partir de uma linha abaixo das faixas
    linha += 2
    if resultado.sem_chave_a.linhas or resultado.sem_chave_b.linhas:
        for coluna, titulo in enumerate(["Linhas sem Chave, fora do cruzamento", "Linhas", "Soma"], start=1):
            ws.cell(linha, coluna, titulo).font = Font(bold=True)
        for base, sem_chave in [("Base A", resultado.sem_chave_a), ("Base B", resultado.sem_chave_b)]:
            linha += 1
            ws.cell(linha, 1, base)
            ws.cell(linha, 2, sem_chave.linhas).number_format = FORMATO_INTEIRO
            ws.cell(linha, 3, sem_chave.soma / 100).number_format = FORMATO_REAIS
        linha += 2

    avisos = []
    if resultado.rejeitadas.height:
        avisos.append(f"Linhas rejeitadas: {_milhar(resultado.rejeitadas.height)} (veja a aba Erros)")
    aviso_de_corte = None
    if resultado.operacoes.height > limite:
        aviso_de_corte = _aviso_de_corte(limite, resultado.operacoes.height)
        avisos.append(aviso_de_corte)
    for linha, aviso in enumerate(avisos, start=linha):
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

    _aba_por_tipo(wb, resultado)
    _aba_por_atributo(wb, resultado)
    _aba_operacoes(wb, resultado, limite, aviso_de_corte)
    _aba_erros(wb, resultado, limite)
    _grafico_da_diferenca(wb, ws, resultado)

    wb.save(caminho)
    return caminho


def _grafico_da_diferenca(wb: openpyxl.Workbook, resumo, resultado: Resultado) -> None:
    """Gráfico de linha da Diferença absoluta por Data-base, abaixo de tudo no Resumo; os dados vão na aba oculta `_grafico`."""
    dados = wb.create_sheet("_grafico")
    dados.sheet_state = "hidden"
    dados.append(["Data-base", "Diferença absoluta"])
    for data, absoluta in resultado.historico:
        dados.append([data, absoluta / 100])
        linha = dados.max_row
        dados.cell(linha, 1).number_format = FORMATO_DATA
        dados.cell(linha, 2).number_format = FORMATO_REAIS

    grafico = LineChart()
    grafico.title = "Diferença absoluta por Data-base"
    grafico.legend = None
    grafico.width, grafico.height = 24, 9
    grafico.y_axis.number_format = FORMATO_REAIS
    # No openpyxl 3.1 os eixos somem no Excel se não forem marcados como visíveis
    grafico.x_axis.delete = grafico.y_axis.delete = False
    fim = dados.max_row
    grafico.add_data(Reference(dados, min_col=2, min_row=1, max_row=fim), titles_from_data=True)
    grafico.set_categories(Reference(dados, min_col=1, min_row=2, max_row=fim))
    resumo.add_chart(grafico, f"A{resumo.max_row + 2}")


def _aba_por_tipo(wb: openpyxl.Workbook, resultado: Resultado) -> None:
    """Quanto cada Tipo do Erro explica, já na ordem do Resultado, e a nota abaixo da tabela."""
    ws = wb.create_sheet("Por Tipo do Erro")
    for coluna, titulo in enumerate(["Tipo do Erro", "Chaves", "Diferença absoluta"], start=1):
        ws.cell(1, coluna, titulo).font = Font(bold=True)
    for linha, (tipo, chaves, absoluta) in enumerate(resultado.por_tipo.iter_rows(), start=2):
        ws.cell(linha, 1, tipo)
        ws.cell(linha, 2, chaves).number_format = FORMATO_INTEIRO
        ws.cell(linha, 3, absoluta / 100).number_format = FORMATO_REAIS
    ws.cell(resultado.por_tipo.height + 3, 1, NOTA_POR_TIPO)  # uma linha em branco abaixo da tabela
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 20


def _aba_por_atributo(wb: openpyxl.Workbook, resultado: Resultado) -> None:
    """Os valores de Atributo com Diferença acima do peso, já na ordem do Resultado (do maior para o menor); sem filtro.

    Sem Atributo nas bases, fica só o cabeçalho.
    """
    ws = wb.create_sheet("Por Atributo")
    _tabela_por_atributo(ws, 1, resultado.por_atributo)
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 24
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 16


def _tabela_por_atributo(ws, linha_do_cabecalho: int, tabela) -> None:
    """Cabeçalho e linhas de uma tabela no formato de `Resultado.por_atributo`, a partir de `linha_do_cabecalho`."""
    for coluna, titulo in enumerate(["Atributo", "Valor", "Diferença absoluta", "Diferença acima do peso"], start=1):
        ws.cell(linha_do_cabecalho, coluna, titulo).font = Font(bold=True)
    for linha, (atributo, valor, absoluta, acima_do_peso) in enumerate(tabela.iter_rows(), start=linha_do_cabecalho + 1):
        ws.cell(linha, 1, atributo)
        ws.cell(linha, 2, valor)
        ws.cell(linha, 3, absoluta / 100).number_format = FORMATO_REAIS
        ws.cell(linha, 4, acima_do_peso).number_format = FORMATO_PERCENTUAL


def _aba_operacoes(wb: openpyxl.Workbook, resultado: Resultado, limite: int, aviso_de_corte: str | None) -> None:
    """As Chaves com Diferença, uma por linha, já na ordem do Resultado; cabeçalho congelado e com filtro.

    Depois do Aberta desde vêm a Linha sem Chave e os Atributos, com o nome original. Mostra só as `limite`
    primeiras (as maiores); quando há corte, o aviso vai na linha 1 e o cabeçalho passa para a linha 2.
    """
    ws = wb.create_sheet("Operações com Diferença")
    linha_do_cabecalho = 1
    if aviso_de_corte:
        ws.cell(1, 1, aviso_de_corte).font = Font(bold=True)
        linha_do_cabecalho = 2
    # Operações e Atributos se alinham pela ordem das linhas: cortam juntos
    operacoes, atributos = resultado.operacoes.head(limite), resultado.atributos.head(limite)
    titulos = [
        "Chave", "Valor A", "Valor B", "Diferença absoluta", "Tipo do Erro", "Aberta desde", "Linha sem Chave"
    ]
    primeiro_atributo = len(titulos) + 1
    titulos += atributos.columns
    for coluna, titulo in enumerate(titulos, start=1):
        ws.cell(linha_do_cabecalho, coluna, titulo).font = Font(bold=True)
    for linha, (chave, a, b, diferenca, tipo, desde, ou_antes, casa) in enumerate(operacoes.iter_rows(), start=linha_do_cabecalho + 1):
        ws.cell(linha, 1, chave)
        # Valor A e Valor B com o sinal; a Diferença sem
        for coluna, centavos in enumerate((a, b, abs(diferenca)), start=2):
            ws.cell(linha, coluna, centavos / 100).number_format = FORMATO_REAIS
        ws.cell(linha, 5, tipo)
        ws.cell(linha, 6, desde).number_format = FORMATO_DATA_OU_ANTES if ou_antes else FORMATO_DATA
        ws.cell(linha, 7, _linha_sem_chave(casa))
    for coluna, atributo in enumerate(atributos.iter_columns(), start=primeiro_atributo):
        for linha, valor in enumerate(atributo, start=linha_do_cabecalho + 1):
            ws.cell(linha, coluna, valor)
        ws.column_dimensions[get_column_letter(coluna)].width = 18
    ws.freeze_panes = f"A{linha_do_cabecalho + 1}"
    ws.auto_filter.ref = f"A{linha_do_cabecalho}:{get_column_letter(len(titulos))}{linha_do_cabecalho + operacoes.height}"
    ws.column_dimensions["A"].width = 24
    for letra in "BCD":
        ws.column_dimensions[letra].width = 18
    ws.column_dimensions["E"].width = 24
    ws.column_dimensions["F"].width = 22
    ws.column_dimensions["G"].width = 36


def _aba_erros(wb: openpyxl.Workbook, resultado: Resultado, limite: int) -> None:
    """As Data-bases ignoradas, em ordem de data, e depois as Linhas rejeitadas da Base A e da Base B, na ordem do
    arquivo; cabeçalho congelado e com filtro.

    Existe sempre: sem erros, fica só o cabeçalho. Mostra só os `limite` primeiros; quando há corte, o aviso vai
    na linha 1 e o cabeçalho passa para a linha 2.
    """
    ws = wb.create_sheet("Erros")
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
    linha_do_cabecalho = 1
    if erros.height > limite:
        aviso = f"Nem todos os erros couberam: mostrando {_milhar(limite)} de {_milhar(erros.height)}."
        ws.cell(1, 1, aviso).font = Font(bold=True)
        linha_do_cabecalho = 2
        erros = erros.head(limite)
    for coluna, titulo in enumerate(erros.columns, start=1):
        ws.cell(linha_do_cabecalho, coluna, titulo).font = Font(bold=True)
    for linha, valores in enumerate(erros.iter_rows(), start=linha_do_cabecalho + 1):
        for coluna, valor in enumerate(valores, start=1):
            ws.cell(linha, coluna, valor)
    ws.freeze_panes = f"A{linha_do_cabecalho + 1}"
    ws.auto_filter.ref = f"A{linha_do_cabecalho}:F{linha_do_cabecalho + erros.height}"
    for letra, largura in zip("ABCDEF", (10, 10, 24, 14, 18, 18)):
        ws.column_dimensions[letra].width = largura
