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
FORMATO_INTEIRO = "#,##0"


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

    # Avisos, só quando acontecem, a partir de uma linha abaixo do quadro
    linha = len(quadro) + 2
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
