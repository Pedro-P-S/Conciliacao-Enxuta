"""Cruzamento da Base A com a Base B pela Chave: só funções puras sobre DataFrames."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import polars as pl

TOLERANCIA_PADRAO = 100  # centavos: R$ 1,00
SEM_PADRAO = "Sem padrão"
SEPARADOR_DE_TIPOS = "; "


class SemDataBaseComum(Exception):
    """As duas bases não têm nenhuma Data-base em comum: não há o que cruzar."""


@dataclass(frozen=True)
class SemChave:
    """As linhas de uma base sem Chave, que ficam fora do cruzamento. Soma em centavos."""

    linhas: int
    soma: int


@dataclass(frozen=True)
class Resultado:
    """Os totais e as Operações com Diferença da Data-base mais recente e o Histórico da Diferença.

    Dinheiro em centavos.
    """

    data_base: date
    tolerancia: int
    total_a: int
    total_b: int
    diferenca_total: int
    diferenca_absoluta: int
    chaves_com_diferenca: int
    sem_chave_a: SemChave  # só nas Data-bases comuns
    sem_chave_b: SemChave
    data_bases_so_em_a: tuple[date, ...]  # ignoradas por não estarem na Base B
    data_bases_so_em_b: tuple[date, ...]  # ignoradas por não estarem na Base A
    historico: tuple[tuple[date, int], ...]  # (Data-base comum, Diferença absoluta), em ordem de data
    # As Chaves com Diferença da Data-base mais recente: Chave, A, B, Diferenca e Tipo, por |Diferença| decrescente.
    # O lado ausente vale 0. É DataFrame porque a lista pode ter centenas de milhares de linhas.
    operacoes: pl.DataFrame
    # Por Tipo do Erro: Tipo, Chaves e Absoluta (soma das |Diferença|), por Absoluta decrescente.
    # Uma Chave com mais de um Tipo conta em cada um.
    por_tipo: pl.DataFrame


def _preparar(base: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Separa as linhas sem Chave (vazia ou só espaço) e soma numa só as de mesma Chave e Data-base."""
    sem_chave = pl.col("Chave").str.strip_chars().fill_null("") == ""
    fora = base.filter(sem_chave)
    somadas = base.filter(~sem_chave).group_by("Chave", "Data", maintain_order=True).agg(pl.col("Valor").sum())
    return somadas, fora


def _sem_chave(fora: pl.DataFrame, comuns: list[date]) -> SemChave:
    """Conta e soma as linhas sem Chave das Data-bases que entram no cruzamento."""
    fora = fora.filter(pl.col("Data").is_in(comuns))
    return SemChave(linhas=fora.height, soma=int(fora["Valor"].sum()))


def _tipo_do_erro() -> pl.Expr:
    """Todos os Tipos que se aplicam, separados por `; ` na ordem da spec; Sem padrão quando nenhum se aplica.

    Espera as colunas A e B antes de o lado ausente virar 0 (nulo = a Chave não está naquela base).
    """
    tipos = [
        ("Só em A", pl.col("B").is_null()),
        ("Só em B", pl.col("A").is_null()),
    ]
    juntos = pl.concat_str(
        [pl.when(condicao).then(pl.lit(nome)) for nome, condicao in tipos],
        separator=SEPARADOR_DE_TIPOS,
        ignore_nulls=True,
    )
    return pl.when(juntos == "").then(pl.lit(SEM_PADRAO)).otherwise(juntos).alias("Tipo")


def _por_tipo(operacoes: pl.DataFrame) -> pl.DataFrame:
    """Uma linha por Tipo presente, com as Chaves e a Diferença absoluta; a Chave conta em cada Tipo que tem."""
    return (
        operacoes.select(pl.col("Tipo").str.split(SEPARADOR_DE_TIPOS), pl.col("Diferenca").abs())
        .explode("Tipo")
        .group_by("Tipo")
        .agg(pl.len().cast(pl.Int64).alias("Chaves"), pl.col("Diferenca").sum().alias("Absoluta"))
        .sort("Absoluta", "Tipo", descending=[True, False])
    )


def conciliar(base_a: pl.DataFrame, base_b: pl.DataFrame, tolerancia: int) -> Resultado:
    """Cruza as bases em cada Data-base comum às duas; os totais são os da mais recente.

    Antes, a Preparação tira as linhas sem Chave e soma as de mesma Chave e Data-base.
    Junção completa pela Chave dentro de cada Data-base; Diferença = A − B, com o lado que falta valendo 0.
    Uma Chave tem Diferença quando |Diferença| > Tolerância.
    """
    base_a, sem_chave_a = _preparar(base_a)
    base_b, sem_chave_b = _preparar(base_b)
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
    operacoes = (
        na_mais_recente.select(
            "Chave", pl.col("A").fill_null(0), pl.col("B").fill_null(0), "Diferenca", _tipo_do_erro()
        )
        .sort(pl.col("Diferenca").abs(), "Chave", descending=[True, False])
    )

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
        sem_chave_a=_sem_chave(sem_chave_a, comuns),
        sem_chave_b=_sem_chave(sem_chave_b, comuns),
        operacoes=operacoes,
        por_tipo=_por_tipo(operacoes),
    )
