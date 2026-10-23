"""Cruzamento da Base A com a Base B pela Chave: só funções puras sobre DataFrames."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import polars as pl

TOLERANCIA_PADRAO = 100  # centavos: R$ 1,00


class SemDataBaseComum(Exception):
    """As duas bases não têm nenhuma Data-base em comum: não há o que cruzar."""


@dataclass(frozen=True)
class Resultado:
    """Os totais da Data-base mais recente e o Histórico da Diferença. Dinheiro em centavos."""

    data_base: date
    tolerancia: int
    total_a: int
    total_b: int
    diferenca_total: int
    diferenca_absoluta: int
    chaves_com_diferenca: int
    data_bases_so_em_a: tuple[date, ...]  # ignoradas por não estarem na Base B
    data_bases_so_em_b: tuple[date, ...]  # ignoradas por não estarem na Base A
    historico: tuple[tuple[date, int], ...]  # (Data-base comum, Diferença absoluta), em ordem de data


def conciliar(base_a: pl.DataFrame, base_b: pl.DataFrame, tolerancia: int) -> Resultado:
    """Cruza as bases em cada Data-base comum às duas; os totais são os da mais recente.

    Junção completa pela Chave dentro de cada Data-base; Diferença = A − B, com o lado que falta valendo 0.
    Uma Chave tem Diferença quando |Diferença| > Tolerância.
    """
    datas_a, datas_b = set(base_a["Data"]), set(base_b["Data"])
    comuns = sorted(datas_a & datas_b)
    if not comuns:
        raise SemDataBaseComum("A Base A e a Base B não têm nenhuma Data-base em comum.")
    data_base = comuns[-1]

    a = base_a.filter(pl.col("Data").is_in(comuns)).select("Chave", "Data", pl.col("Valor").alias("A"))
    b = base_b.filter(pl.col("Data").is_in(comuns)).select("Chave", "Data", pl.col("Valor").alias("B"))
    cruzado = a.join(b, on=["Chave", "Data"], how="full", coalesce=True).with_columns(
        (pl.col("A").fill_null(0) - pl.col("B").fill_null(0)).alias("Diferenca")
    )
    com_diferenca = cruzado.filter(pl.col("Diferenca").abs() > tolerancia)

    absoluta_por_data = dict(
        com_diferenca.group_by("Data").agg(pl.col("Diferenca").abs().sum()).iter_rows()
    )
    na_mais_recente = com_diferenca.filter(pl.col("Data") == data_base)

    return Resultado(
        data_base=data_base,
        tolerancia=tolerancia,
        total_a=int(a.filter(pl.col("Data") == data_base)["A"].sum()),
        total_b=int(b.filter(pl.col("Data") == data_base)["B"].sum()),
        diferenca_total=int(na_mais_recente["Diferenca"].sum()),
        diferenca_absoluta=int(na_mais_recente["Diferenca"].abs().sum()),
        chaves_com_diferenca=na_mais_recente.height,
        data_bases_so_em_a=tuple(sorted(datas_a - datas_b)),
        data_bases_so_em_b=tuple(sorted(datas_b - datas_a)),
        historico=tuple((data, int(absoluta_por_data.get(data, 0))) for data in comuns),
    )
