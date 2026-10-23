"""Resultado → `.xlsx`. É aqui, e só aqui, que centavos viram reais."""

from __future__ import annotations

from pathlib import Path

import openpyxl
from openpyxl.styles import Font

from conciliacao_enxuta.cruzamento import Resultado

# Código de formato do Excel; no Excel em português aparece como #.##0,00.
FORMATO_REAIS = "#,##0.00"
FORMATO_DATA = "DD/MM/YYYY"


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
        ("Chaves com Diferença", resultado.chaves_com_diferenca, "#,##0"),
    ]
    for linha, (rotulo, valor, formato) in enumerate(quadro, start=1):
        ws.cell(linha, 1, rotulo).font = Font(bold=True)
        ws.cell(linha, 2, valor).number_format = formato

    avisos = [
        f"Data-bases ignoradas por estarem só na {nome}: {', '.join(f'{d:%d/%m/%Y}' for d in datas)}."
        for nome, datas in (("Base A", resultado.data_bases_so_em_a), ("Base B", resultado.data_bases_so_em_b))
        if datas
    ]
    for linha, aviso in enumerate(avisos, start=len(quadro) + 2):
        ws.cell(linha, 1, aviso)

    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 20

    wb.save(caminho)
    return caminho
