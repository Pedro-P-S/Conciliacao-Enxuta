"""Cruzamento da Base A com a Base B pela Chave: só funções puras sobre DataFrames."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import polars as pl

TOLERANCIA_PADRAO = 100  # centavos: R$ 1,00
SEM_PADRAO = "Sem padrão"
SEPARADOR_DE_TIPOS = "; "
# Faixas da Idade da Diferença, em ordem: (nome, maior Idade em dias da faixa; None = sem limite)
FAIXAS_DE_IDADE = (
    ("Até 30 dias", 30),
    ("31 a 90 dias", 90),
    ("91 a 365 dias", 365),
    ("366 dias a 5 anos", 1826),  # 5 anos = 5 × 365 + 1 dia de ano bissexto
    ("Mais de 5 anos", None),
)


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
    sem_chave_a: SemChave  # só na Data-base mais recente
    sem_chave_b: SemChave
    data_bases_so_em_a: tuple[date, ...]  # ignoradas por não estarem na Base B
    data_bases_so_em_b: tuple[date, ...]  # ignoradas por não estarem na Base A
    historico: tuple[tuple[date, int], ...]  # (Data-base comum, Diferença absoluta), em ordem de data
    # As Chaves com Diferença da Data-base mais recente: Chave, A, B, Diferenca, Tipo, Desde (o Aberta desde),
    # OuAntes (o Aberta desde é a primeira Data-base comum) e Casa (as linhas sem Chave que casam com a Chave:
    # lista de Valor, Data e Base "A" ou "B", em ordem de Data; nula quando nenhuma), por |Diferença| decrescente.
    # O lado ausente vale 0. É DataFrame porque a lista pode ter centenas de milhares de linhas.
    operacoes: pl.DataFrame
    # Os Atributos de cada linha de `operacoes`, na mesma ordem, com o nome original: primeiro os de A, depois
    # os só de B. Ficam fora de `operacoes` para um Atributo poder se chamar, por exemplo, Tipo.
    atributos: pl.DataFrame
    # Por Tipo do Erro: Tipo, Chaves e Absoluta (soma das |Diferença|), por Absoluta decrescente.
    # Uma Chave com mais de um Tipo conta em cada um.
    por_tipo: pl.DataFrame
    # Por faixa de Idade da Diferença: (Faixa, Chaves, Diferença absoluta), as 5 sempre, na ordem de FAIXAS_DE_IDADE
    por_idade: tuple[tuple[str, int, int], ...]
    # Por Atributo e valor, só os valores com alguma Chave com Diferença: Atributo, Valor, Diferenca (soma com sinal)
    # e Concentracao (fração da Diferença absoluta − fração do peso no total), por Diferença absoluta decrescente.
    # O peso é |A|, ou |B| quando A é zero ou ausente. Valor vazio não entra.
    por_atributo: pl.DataFrame


def _preparar(base: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Separa as linhas sem Chave (vazia ou só espaço) e soma numa só as de mesma Chave e Data-base.

    Os Atributos das linhas somadas vêm da primeira.
    """
    sem_chave = pl.col("Chave").str.strip_chars().fill_null("") == ""
    fora = base.filter(sem_chave)
    somadas = (
        base.filter(~sem_chave)
        .group_by("Chave", "Data", maintain_order=True)
        .agg(pl.col("Valor").sum(), pl.exclude("Chave", "Data", "Valor").first())
    )
    return somadas, fora


def _sem_chave(fora: pl.DataFrame, data_base: date) -> SemChave:
    """Conta e soma as linhas sem Chave da Data-base mais recente, a mesma dos totais do Resumo.

    Somar todas as Data-bases contaria várias vezes a mesma linha das posições diárias.
    """
    fora = fora.filter(pl.col("Data") == data_base)
    return SemChave(linhas=fora.height, soma=int(fora["Valor"].sum()))


def _tipo_do_erro(tolerancia: int) -> pl.Expr:
    """Todos os Tipos que se aplicam, separados por `; ` na ordem da spec; Sem padrão quando nenhum se aplica.

    Espera as colunas A e B antes de o lado ausente virar 0 (nulo = a Chave não está naquela base) e a Casa.
    A Tolerância é a folga nas comparações de Sinal invertido, Duplicado e Vírgula deslocada.
    """
    a, b = pl.col("A").fill_null(0), pl.col("B").fill_null(0)

    def um_e_vezes_o_outro(*fatores: int) -> pl.Expr:
        """A = fator × B ou B = fator × A, com a Tolerância de folga."""
        return pl.any_horizontal(
            [((x - fator * y).abs() <= tolerancia) for fator in fatores for x, y in ((a, b), (b, a))]
        )

    def digitos(valor: pl.Expr) -> pl.Expr:
        """Os dígitos de |valor| em ordem crescente: iguais quando são os mesmos dígitos em qualquer ordem."""
        return valor.abs().cast(pl.String).str.split("").list.sort().list.join("")

    tipos = [
        ("Só em A", pl.col("B").is_null()),
        ("Só em B", pl.col("A").is_null()),
        ("Sinal invertido", (a != 0) & ((a + b).abs() <= tolerancia)),
        ("Duplicado", um_e_vezes_o_outro(2)),
        ("Vírgula deslocada", um_e_vezes_o_outro(10, 100, 1000)),
        (
            "Dígitos trocados",
            (pl.col("Diferenca") % 9 == 0) & (a.abs() != b.abs()) & (digitos(a) == digitos(b)),
        ),
        ("Casa com linha sem Chave", pl.col("Casa").is_not_null()),
    ]
    juntos = pl.concat_str(
        [pl.when(condicao).then(pl.lit(nome)) for nome, condicao in tipos],
        separator=SEPARADOR_DE_TIPOS,
        ignore_nulls=True,
    )
    return pl.when(juntos == "").then(pl.lit(SEM_PADRAO)).otherwise(juntos).alias("Tipo")


def _casas(
    com_diferenca: pl.DataFrame,
    sem_chave_a: pl.DataFrame,
    sem_chave_b: pl.DataFrame,
    comuns: list[date],
    tolerancia: int,
) -> pl.DataFrame:
    """Chave e Casa: as linhas sem Chave que zeram, dentro da Tolerância, a Diferença que a Chave tinha.

    Cada valor de linha sem Chave de uma base é comparado uma vez só, na primeira Data-base comum em que aparece;
    nas seguintes, é o mesmo lançamento. Na Base A, casa quando Diferença ≈ −Valor; na Base B, Diferença ≈ Valor.
    """
    linhas = (
        pl.concat(
            [
                sem_chave_a.select("Data", "Valor", pl.lit("A").alias("Base"), (-pl.col("Valor")).alias("Alvo")),
                sem_chave_b.select("Data", "Valor", pl.lit("B").alias("Base"), pl.col("Valor").alias("Alvo")),
            ]
        )
        .filter(pl.col("Data").is_in(comuns))
        .group_by("Base", "Valor")
        .agg(pl.col("Data").min(), pl.col("Alvo").first())
    )
    return (
        com_diferenca.select("Chave", "Data", "Diferenca")
        .join(linhas, on="Data")
        .filter((pl.col("Diferenca") - pl.col("Alvo")).abs() <= tolerancia)
        .sort("Data", "Base", "Valor")
        .group_by("Chave", maintain_order=True)
        .agg(pl.struct("Valor", "Data", "Base").alias("Casa"))
    )


def _aberta_desde(com_diferenca: pl.DataFrame, comuns: list[date]) -> pl.DataFrame:
    """Chave, Desde e OuAntes das Chaves com Diferença na Data-base mais recente.

    Desde é a primeira Data-base da sequência contínua de Data-bases comuns com Diferença que chega até a mais
    recente. Numa Data-base em que a Chave está dentro da Tolerância ou fora das duas bases, a sequência se quebra.
    Na sequência, a Chave com Diferença na i-ésima Data-base (contando de 0) é a (n − i)-ésima mais recente das
    suas Data-bases com Diferença; antes de uma quebra, é menos que isso.
    """
    n = len(comuns)
    indices = pl.DataFrame({"Data": comuns, "i": range(n)}, schema={"Data": pl.Date, "i": pl.Int64})
    return (
        com_diferenca.select("Chave", "Data")
        .join(indices, on="Data")
        .filter(pl.col("i") + pl.col("i").rank("ordinal", descending=True).over("Chave").cast(pl.Int64) == n)
        .group_by("Chave")
        .agg(pl.col("Data").min().alias("Desde"))
        .with_columns((pl.col("Desde") == comuns[0]).alias("OuAntes"))
    )


def _atributos(chaves: pl.DataFrame, base_a: pl.DataFrame, base_b: pl.DataFrame) -> pl.DataFrame:
    """Os Atributos de cada Chave, na ordem de `chaves`: o de A e, se vazio ou ausente, o de B.

    `base_a` e `base_b` são as bases preparadas (uma linha por Chave) na Data-base mais recente.
    """
    de_a, de_b = (
        chaves.join(base.drop("Data", "Valor"), on="Chave", how="left", maintain_order="left").drop("Chave")
        for base in (base_a, base_b)
    )
    colunas = []
    for nome in dict.fromkeys(de_a.columns + de_b.columns):
        if nome not in de_a.columns:
            colunas.append(de_b[nome])
        elif nome not in de_b.columns:
            colunas.append(de_a[nome])
        else:
            colunas.append(de_a[nome].fill_null(de_b[nome]))
    return pl.DataFrame(colunas)


def _por_tipo(operacoes: pl.DataFrame) -> pl.DataFrame:
    """Uma linha por Tipo presente, com as Chaves e a Diferença absoluta; a Chave conta em cada Tipo que tem."""
    return (
        operacoes.select(pl.col("Tipo").str.split(SEPARADOR_DE_TIPOS), pl.col("Diferenca").abs())
        .explode("Tipo")
        .group_by("Tipo")
        .agg(pl.len().cast(pl.Int64).alias("Chaves"), pl.col("Diferenca").sum().alias("Absoluta"))
        .sort("Absoluta", "Tipo", descending=[True, False])
    )


def _por_atributo(
    na_data_base: pl.DataFrame, base_a: pl.DataFrame, base_b: pl.DataFrame, tolerancia: int
) -> pl.DataFrame:
    """Onde a Diferença se concentra, descontado o peso que cada valor de Atributo já tem no total.

    `na_data_base` são todas as Chaves cruzadas na Data-base mais recente; `base_a` e `base_b`, as bases preparadas
    nela, de onde vêm os Atributos.
    """
    atributos = _atributos(na_data_base.select("Chave"), base_a, base_b)
    a, b = pl.col("A").fill_null(0), pl.col("B").fill_null(0)
    chaves = na_data_base.select(
        pl.when(a != 0).then(a).otherwise(b).abs().alias("Peso"),
        # Só a Diferença acima da Tolerância conta; dentro dela, fica nula
        pl.when(pl.col("Diferenca").abs() > tolerancia).then(pl.col("Diferenca")).alias("Diferenca"),
    )
    peso_total, absoluta_total = chaves["Peso"].sum(), chaves["Diferenca"].abs().sum()
    vazia = pl.DataFrame(
        schema={
            "Atributo": pl.String,
            "Valor": pl.String,
            "Diferenca": pl.Int64,
            "Concentracao": pl.Float64,
        }
    )
    if not atributos.columns:
        return vazia
    return (
        pl.concat([chaves, atributos], how="horizontal")
        .unpivot(index=["Peso", "Diferenca"], variable_name="Atributo", value_name="Valor")
        .drop_nulls("Valor")
        .group_by("Atributo", "Valor")
        .agg(
            pl.col("Peso").sum(),
            pl.col("Diferenca").sum(),
            pl.col("Diferenca").abs().sum().alias("Absoluta"),
            pl.col("Diferenca").is_not_null().any().alias("ComDiferenca"),
        )
        .filter("ComDiferenca")
        .with_columns((pl.col("Absoluta") / absoluta_total - pl.col("Peso") / peso_total).alias("Concentracao"))
        .sort(["Absoluta", "Atributo", "Valor"], descending=[True, False, False])
        .select(vazia.columns)
    )


def _por_idade(operacoes: pl.DataFrame, data_base: date) -> tuple[tuple[str, int, int], ...]:
    """Chaves e Diferença absoluta de cada faixa de Idade: dias corridos do Aberta desde até a Data-base mais recente."""
    idade = (pl.lit(data_base) - pl.col("Desde")).dt.total_days()
    faixas, piso = [], 0
    for nome, teto in FAIXAS_DE_IDADE:
        na_faixa = operacoes.filter(idade >= piso)
        if teto is not None:
            na_faixa = na_faixa.filter(idade <= teto)
            piso = teto + 1
        faixas.append((nome, na_faixa.height, int(na_faixa["Diferenca"].abs().sum())))
    return tuple(faixas)


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
    # Cada linha sem Chave é uma Diferença do valor inteiro: +Valor em A, −Valor em B, uma linha por vez
    soltas = pl.concat(
        [
            sem_chave_a.select("Data", pl.col("Valor").alias("Diferenca")),
            sem_chave_b.select("Data", (-pl.col("Valor")).alias("Diferenca")),
        ]
    ).filter(pl.col("Diferenca").abs() > tolerancia)
    soltas_na_mais_recente = soltas.filter(pl.col("Data") == data_base)["Diferenca"]

    absoluta_por_data = dict(
        pl.concat([com_diferenca.select("Data", "Diferenca"), soltas])
        .group_by("Data")
        .agg(pl.col("Diferenca").abs().sum())
        .iter_rows()
    )
    na_mais_recente = com_diferenca.filter(pl.col("Data") == data_base)
    a_na_mais_recente = base_a.filter(pl.col("Data") == data_base)
    b_na_mais_recente = base_b.filter(pl.col("Data") == data_base)
    operacoes = (
        na_mais_recente.join(
            _casas(com_diferenca, sem_chave_a, sem_chave_b, comuns, tolerancia), on="Chave", how="left"
        )
        .select(
            "Chave", pl.col("A").fill_null(0), pl.col("B").fill_null(0), "Diferenca", _tipo_do_erro(tolerancia), "Casa"
        )
        .join(_aberta_desde(com_diferenca, comuns), on="Chave", how="left")
        .select("Chave", "A", "B", "Diferenca", "Tipo", "Desde", "OuAntes", "Casa")
        .sort(pl.col("Diferenca").abs(), "Chave", descending=[True, False])
    )

    return Resultado(
        data_base=data_base,
        tolerancia=tolerancia,
        total_a=int(a.filter(pl.col("Data") == data_base)["A"].sum()) + _sem_chave(sem_chave_a, data_base).soma,
        total_b=int(b.filter(pl.col("Data") == data_base)["B"].sum()) + _sem_chave(sem_chave_b, data_base).soma,
        diferenca_total=int(na_mais_recente["Diferenca"].sum() + soltas_na_mais_recente.sum()),
        diferenca_absoluta=int(na_mais_recente["Diferenca"].abs().sum() + soltas_na_mais_recente.abs().sum()),
        chaves_com_diferenca=na_mais_recente.height,
        data_bases_so_em_a=tuple(sorted(datas_a - datas_b)),
        data_bases_so_em_b=tuple(sorted(datas_b - datas_a)),
        historico=tuple((data, int(absoluta_por_data.get(data, 0))) for data in comuns),
        sem_chave_a=_sem_chave(sem_chave_a, data_base),
        sem_chave_b=_sem_chave(sem_chave_b, data_base),
        operacoes=operacoes,
        atributos=_atributos(operacoes.select("Chave"), a_na_mais_recente, b_na_mais_recente),
        por_tipo=_por_tipo(operacoes),
        por_idade=_por_idade(operacoes, data_base),
        por_atributo=_por_atributo(
            cruzado.filter(pl.col("Data") == data_base), a_na_mais_recente, b_na_mais_recente, tolerancia
        ),
    )
