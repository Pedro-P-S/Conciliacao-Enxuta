"""Seam 1: `conciliar` com DataFrames pequenos montados no teste."""

from datetime import date

import polars as pl

from conciliacao_enxuta.cruzamento import SemChave, conciliar

DIA = date(2026, 9, 30)


def base(linhas: list[tuple[str | None, int]], data: date = DIA) -> pl.DataFrame:
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


def test_linhas_da_mesma_chave_na_mesma_data_base_sao_somadas_antes_de_comparar():
    a = base([("1", 3_000), ("1", 7_000), ("2", 500)])
    b = base([("1", 10_000), ("2", 200), ("2", 300)])

    r = conciliar(a, b, tolerancia=100)

    assert r.total_a == r.total_b == 10_500
    assert r.chaves_com_diferenca == 0
    assert r.diferenca_absoluta == 0


def test_linhas_sem_chave_ficam_fora_e_sao_contadas_e_somadas_por_base():
    a = base([("1", 10_000), (None, 500), ("", 250), ("   ", -50)])
    b = base([("1", 10_000), ("", 40_000)])

    r = conciliar(a, b, tolerancia=100)

    assert r.total_a == r.total_b == 10_000
    assert r.chaves_com_diferenca == 0
    assert r.diferenca_absoluta == 0
    assert r.sem_chave_a == SemChave(linhas=3, soma=700)
    assert r.sem_chave_b == SemChave(linhas=1, soma=40_000)


def test_sem_linhas_sem_chave_a_contagem_e_zero():
    r = conciliar(base([("1", 10_000)]), base([("1", 10_000)]), tolerancia=100)

    assert r.sem_chave_a == r.sem_chave_b == SemChave(linhas=0, soma=0)


def test_invariante_vale_com_chaves_repetidas():
    a = base([("1", 60_000), ("1", 40_000), ("2", 50_000), ("3", 30_000)])
    b = base([("1", 99_950), ("2", 20_000), ("2", 40_000), ("3", 10_000), ("3", 19_901)])

    r = conciliar(a, b, tolerancia=100)

    dentro_da_tolerancia = 50 + 99  # Chaves 1 e 3, já somadas
    assert r.chaves_com_diferenca == 1  # Chave 2: 50.000 − 60.000
    assert r.diferenca_total == -10_000
    assert r.total_a - r.total_b == r.diferenca_total + dentro_da_tolerancia


def dia(n: int) -> date:
    return date(2026, 9, n)


def base_com_data_bases(posicoes: dict[int, list[tuple[str, int]]]) -> pl.DataFrame:
    """Base com várias Data-bases: {dia de setembro: linhas}."""
    return pl.concat([base(linhas, dia(n)) for n, linhas in posicoes.items()])


def test_entram_so_as_data_bases_comuns_e_as_outras_vem_como_ignoradas_com_a_base():
    a = base_com_data_bases({1: [("x", 100_000)], 2: [("x", 200_000)], 3: [("x", 300_000)]})
    b = base_com_data_bases({2: [("x", 200_000)], 3: [("x", 290_000)], 4: [("x", 999_000)]})

    r = conciliar(a, b, tolerancia=100)

    assert r.data_base == dia(3)
    assert r.total_a == 300_000
    assert r.total_b == 290_000
    assert r.data_bases_so_em_a == (dia(1),)
    assert r.data_bases_so_em_b == (dia(4),)


def test_cruza_por_chave_dentro_de_cada_data_base_e_guarda_a_diferenca_absoluta_de_cada_uma_em_ordem():
    # A Chave x está em A na Data-base 2 e em B na Data-base 3: não cruzam entre si.
    a = base_com_data_bases({3: [("z", 7_000)], 1: [("x", 100_000)], 2: [("x", 50_000), ("y", 1_000)]})
    b = base_com_data_bases({2: [("y", 1_000)], 1: [("x", 100_000)], 3: [("x", 50_000)]})

    r = conciliar(a, b, tolerancia=100)

    assert r.historico == ((dia(1), 0), (dia(2), 50_000), (dia(3), 57_000))
    assert r.diferenca_absoluta == 57_000
    assert r.chaves_com_diferenca == 2


def test_linhas_sem_chave_contam_so_nas_data_bases_que_entram_no_cruzamento():
    a = base_com_data_bases({1: [("x", 100), ("", 500)], 2: [("x", 100), ("", 30)], 3: [("x", 100), ("", 7)]})
    b = base_com_data_bases({2: [("x", 100), ("", 2_000)], 3: [("x", 100)], 4: [("x", 100), ("", 9_000)]})

    r = conciliar(a, b, tolerancia=100)

    assert r.sem_chave_a == SemChave(linhas=2, soma=37)  # sem a Data-base 1, só em A
    assert r.sem_chave_b == SemChave(linhas=1, soma=2_000)  # sem a Data-base 4, só em B
