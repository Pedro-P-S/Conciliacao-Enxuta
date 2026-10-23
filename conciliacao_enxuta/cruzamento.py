"""Cruzamento da Base A com a Base B pela Chave: só funções puras sobre DataFrames."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import polars as pl

TOLERANCIA_PADRAO = 100  # centavos: R$ 1,00


@dataclass(frozen=True)
class SemChave:
    """As linhas de uma base sem Chave, que ficam fora do cruzamento. Soma em centavos."""

    linhas: int
    soma: int


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
    sem_chave_a: SemChave
    sem_chave_b: SemChave


def _preparar(base: pl.DataFrame) -> tuple[pl.DataFrame, SemChave]:
    """Separa as linhas sem Chave (vazia ou só espaço) e soma numa só as de mesma Chave e Data-base."""
    sem_chave = pl.col("Chave").str.strip_chars().fill_null("") == ""
    fora = base.filter(sem_chave)
    somadas = base.filter(~sem_chave).group_by("Chave", "Data", maintain_order=True).agg(pl.col("Valor").sum())
    return somadas, SemChave(linhas=fora.height, soma=int(fora["Valor"].sum()))


def conciliar(base_a: pl.DataFrame, base_b: pl.DataFrame, tolerancia: int) -> Resultado:
    """Cruza as bases na Data-base mais recente comum às duas.

    Antes, a Preparação tira as linhas sem Chave e soma as de mesma Chave e Data-base.
    Junção completa pela Chave; Diferença = A − B, com o lado que falta valendo 0.
    Uma Chave tem Diferença quando |Diferença| > Tolerância.
    """
    base_a, sem_chave_a = _preparar(base_a)
    base_b, sem_chave_b = _preparar(base_b)
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
        sem_chave_a=sem_chave_a,
        sem_chave_b=sem_chave_b,
    )
