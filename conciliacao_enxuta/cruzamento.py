"""Cruzamento da Base A com a Base B pela Chave: só funções puras sobre DataFrames."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import polars as pl

TOLERANCIA_PADRAO = 100  # centavos: R$ 1,00


@dataclass(frozen=True)
class Resultado:
    """Os totais da Data-base mais recente. Dinheiro em centavos."""

    data_base: date
    tolerancia: int
    total_a: int
    total_b: int
    diferenca_total: int
    diferenca_absoluta: int
    chaves_com_diferenca: int


def conciliar(base_a: pl.DataFrame, base_b: pl.DataFrame, tolerancia: int) -> Resultado:
    """Cruza as bases na Data-base mais recente comum às duas.

    Junção completa pela Chave; Diferença = A − B, com o lado que falta valendo 0.
    Uma Chave tem Diferença quando |Diferença| > Tolerância.
    """
    data_base = max(set(base_a["Data"]) & set(base_b["Data"]))
    a = base_a.filter(pl.col("Data") == data_base).select("Chave", pl.col("Valor").alias("A"))
    b = base_b.filter(pl.col("Data") == data_base).select("Chave", pl.col("Valor").alias("B"))

    cruzado = a.join(b, on="Chave", how="full", coalesce=True).with_columns(
        (pl.col("A").fill_null(0) - pl.col("B").fill_null(0)).alias("Diferenca")
    )
    com_diferenca = cruzado.filter(pl.col("Diferenca").abs() > tolerancia)

    return Resultado(
        data_base=data_base,
        tolerancia=tolerancia,
        total_a=int(a["A"].sum()),
        total_b=int(b["B"].sum()),
        diferenca_total=int(com_diferenca["Diferenca"].sum()),
        diferenca_absoluta=int(com_diferenca["Diferenca"].abs().sum()),
        chaves_com_diferenca=com_diferenca.height,
    )
