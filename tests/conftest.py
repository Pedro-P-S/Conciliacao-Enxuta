"""O openpyxl não calcula fórmulas. Com vários Batimentos o Resumo e a `_grafico` (colunas A:E) são fórmulas que
buscam o Batimento escolhido; este módulo as resolve, só as do Resumo e da `_grafico`, para os testes lerem o Resumo
como o Excel o mostraria. Os testes que conferem as fórmulas carregam com `formulas=True`."""

import re

import openpyxl
import pytest

_INDEX = re.compile(r"INDEX\('_grafico'!\$([A-Z])\$2:\$[A-Z]\$\d+,\('_grafico'!\$G\$2-1\)\*(\d+)\+(\d+)\)")
_NA = object()


def resolver_formulas(wb, posicao: int = 1) -> None:
    """Troca, no Resumo e na `_grafico`, as fórmulas pelo valor que o Excel mostraria com o `posicao`-ésimo
    Batimento escolhido (as células em branco viram None)."""
    dados, resumo = wb["_grafico"], wb["Resumo"]
    nome = dados.cell(1 + posicao, 8).value

    def indice(coluna, altura, k):
        return dados[f"{coluna}{1 + (posicao - 1) * int(altura) + int(k)}"].value

    def ref(endereco):
        valor = resumo[endereco.replace("$", "")].value
        return None if valor == "" else valor

    def calcular(texto: str):
        texto = texto.removeprefix("=")
        com_texto = texto.endswith('&""')
        texto = texto.removesuffix('&""')
        texto = _INDEX.sub(lambda m: f"idx('{m[1]}',{m[2]},{m[3]})", texto)
        texto = re.sub(r'(idx\([^)]*\)|\$?[A-Z]+\$?\d+)=""', lambda m: f"vazio({m[1]})", texto)
        texto = re.sub(r"(?<![\w'])(\$?[A-Z]+\$?\d+)(?![\w(])", lambda m: f"ref('{m[1]}')", texto)
        contexto = {
            "idx": indice, "ref": ref, "NA": lambda: _NA, "vazio": lambda v: v in (None, ""),
            "IF": lambda c, a, b: a if c else b,
        }
        valor = eval(texto, {"__builtins__": {}}, contexto)  # noqa: S307 - só as fórmulas geradas por `excel`
        if com_texto and valor is None:
            valor = ""
        return None if valor == "" else valor

    # `ref` lê o Resumo já resolvido, então o Resumo vai de cima para baixo e a `_grafico` primeiro
    dados["G2"] = posicao
    resumo["B1"] = nome
    for ws, colunas in ((dados, range(1, 6)), (resumo, range(1, 5))):
        for linha in ws.iter_rows(min_row=2 if ws is dados else 3):
            for celula in linha:
                if celula.column in colunas and isinstance(celula.value, str) and celula.value.startswith("="):
                    valor = calcular(celula.value)
                    celula.value = "#N/A" if valor is _NA else valor


@pytest.fixture
def escolher():
    return resolver_formulas


@pytest.fixture(autouse=True)
def formulas_resolvidas(monkeypatch):
    original = openpyxl.load_workbook

    def carregar(*args, formulas: bool = False, **kwargs):
        wb = original(*args, **kwargs)
        if not formulas and "_grafico" in wb.sheetnames and wb["_grafico"]["G2"].value:
            resolver_formulas(wb)
        return wb

    monkeypatch.setattr(openpyxl, "load_workbook", carregar)
