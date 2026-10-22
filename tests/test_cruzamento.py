"""Seam 1: `conciliar` com DataFrames pequenos montados no teste."""

from datetime import date

import polars as pl

from conciliacao_enxuta.cruzamento import conciliar

DIA = date(2026, 9, 30)


def base(linhas: list[tuple[str, int]], data: date = DIA) -> pl.DataFrame:
    """Base lida: Chave, Data e Valor em centavos."""
    return pl.DataFrame(
        {
            "Chave": [c for c, _ in linhas],
            "Data": [data] * len(linhas),
            "Valor": [v for _, v in linhas],
        },
        schema={"Chave": pl.String, "Data": pl.Date, "Valor": pl.Int64},
    )


def test_juncao_completa_com_lado_ausente_valendo_zero():
    a = base([("1", 10_000), ("2", 5_000)])
    b = base([("1", 10_000), ("3", 2_000)])

    r = conciliar(a, b, tolerancia=100)

    assert r.data_base == DIA
    assert r.total_a == 15_000
    assert r.total_b == 12_000
    # Chave 2 só em A (+5.000) e Chave 3 só em B (−2.000)
    assert r.chaves_com_diferenca == 2
    assert r.diferenca_total == 3_000
    assert r.diferenca_absoluta == 7_000


def test_diferenca_igual_a_tolerancia_nao_conta_e_um_centavo_acima_conta():
    a = base([("igual", 10_100), ("acima", 10_101)])
    b = base([("igual", 10_000), ("acima", 10_000)])

    r = conciliar(a, b, tolerancia=100)

    assert r.chaves_com_diferenca == 1
    assert r.diferenca_total == 101


def test_tolerancia_vale_tambem_para_chaves_so_em_a_e_so_em_b():
    a = base([("so_a_dentro", 100), ("so_a_fora", 101)])
    b = base([("so_b_dentro", 50), ("so_b_fora", 250)])

    r = conciliar(a, b, tolerancia=100)

    assert r.chaves_com_diferenca == 2
    assert r.diferenca_total == 101 - 250
    assert r.diferenca_absoluta == 101 + 250


def test_invariante_total_a_menos_total_b_e_diferenca_total_mais_o_que_ficou_na_tolerancia():
    a = base([("1", 100_000), ("2", 50_000), ("3", 7_000), ("4", 30_000)])
    b = base([("1", 99_950), ("2", 60_000), ("5", 80), ("4", 29_901)])

    r = conciliar(a, b, tolerancia=100)

    dentro_da_tolerancia = 50 + (-80) + 99  # Chaves 1, 5 (só em B) e 4
    assert r.chaves_com_diferenca == 2  # Chaves 2 e 3
    assert r.diferenca_total == -10_000 + 7_000
    assert r.total_a - r.total_b == r.diferenca_total + dentro_da_tolerancia


def test_positivas_e_negativas_se_anulam_na_total_e_nao_na_absoluta():
    a = base([("1", 50_000), ("2", 10_000)])
    b = base([("1", 10_000), ("2", 50_000)])

    r = conciliar(a, b, tolerancia=100)

    assert r.diferenca_total == 0
    assert r.diferenca_absoluta == 80_000
    assert r.total_a == r.total_b == 60_000
