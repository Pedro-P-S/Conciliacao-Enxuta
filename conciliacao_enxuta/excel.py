"""Resultado → `.xlsx`. É aqui, e só aqui, que centavos viram reais."""

from __future__ import annotations

from pathlib import Path

import openpyxl
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font

from conciliacao_enxuta.cruzamento import Resultado

# Código de formato do Excel; no Excel em português aparece como #.##0,00.
FORMATO_REAIS = "#,##0.00"
FORMATO_DATA = "DD/MM/YYYY"
# A célula continua data, para ordenar e filtrar; só o que o Excel mostra ganha o " ou antes".
FORMATO_DATA_OU_ANTES = 'DD/MM/YYYY" ou antes"'
FORMATO_INTEIRO = "#,##0"
NOTA_POR_TIPO = "Uma Chave pode contar em mais de um Tipo do Erro."


def gravar_excel(resultado: Resultado, pasta: str | Path) -> Path:
    """Grava `conciliacao_AAAA-MM-DD.xlsx` em `pasta`, sobrescrevendo, e devolve o caminho."""
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
    if resultado.abertas_desde_a_primeira:
        primeira = resultado.historico[0][0]
        ws.cell(
            linha,
            1,
            f"Chaves com Diferença desde a primeira Data-base ({primeira:%d/%m/%Y}) ou antes: "
            f"{resultado.abertas_desde_a_primeira}. A Diferença delas pode ser ainda mais antiga.",
        )
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

    avisos = [
        f"Data-bases ignoradas por estarem só na {nome}: {', '.join(f'{d:%d/%m/%Y}' for d in datas)}."
        for nome, datas in (("Base A", resultado.data_bases_so_em_a), ("Base B", resultado.data_bases_so_em_b))
        if datas
    ]
    for linha, aviso in enumerate(avisos, start=linha):
        ws.cell(linha, 1, aviso)

    ws.column_dimensions["A"].width = 36
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20

    _aba_por_tipo(wb, resultado)
    _aba_operacoes(wb, resultado)
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


def _aba_operacoes(wb: openpyxl.Workbook, resultado: Resultado) -> None:
    """As Chaves com Diferença, uma por linha, já na ordem do Resultado; cabeçalho congelado e com filtro."""
    ws = wb.create_sheet("Operações com Diferença")
    titulos = ["Chave", "Valor A", "Valor B", "Diferença", "Tipo do Erro", "Aberta desde"]
    for coluna, titulo in enumerate(titulos, start=1):
        ws.cell(1, coluna, titulo).font = Font(bold=True)
    for linha, (chave, a, b, diferenca, tipo, desde, ou_antes) in enumerate(resultado.operacoes.iter_rows(), start=2):
        ws.cell(linha, 1, chave)
        for coluna, centavos in enumerate((a, b, diferenca), start=2):
            ws.cell(linha, coluna, centavos / 100).number_format = FORMATO_REAIS
        ws.cell(linha, 5, tipo)
        ws.cell(linha, 6, desde).number_format = FORMATO_DATA_OU_ANTES if ou_antes else FORMATO_DATA
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:F{resultado.operacoes.height + 1}"
    ws.column_dimensions["A"].width = 24
    for letra in "BCD":
        ws.column_dimensions[letra].width = 18
    ws.column_dimensions["E"].width = 24
    ws.column_dimensions["F"].width = 22
