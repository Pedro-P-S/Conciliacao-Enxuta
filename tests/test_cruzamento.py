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


def test_operacoes_com_diferenca_sao_so_da_data_base_mais_recente_acima_da_tolerancia_da_maior_para_a_menor():
    a = base_com_data_bases(
        {
            1: [("antiga", 900_000)],
            2: [("pequena", 10_200), ("dentro", 10_100), ("so_a", 30_000), ("grande", 100_000), ("igual", 500)],
        }
    )
    b = base_com_data_bases(
        {
            1: [("antiga", 0)],
            2: [("pequena", 10_000), ("dentro", 10_000), ("so_b", 40_000), ("grande", 200_000), ("igual", 500)],
        }
    )

    r = conciliar(a, b, tolerancia=100)

    assert r.operacoes.columns == ["Chave", "A", "B", "Diferenca", "Tipo", "Desde", "OuAntes"]
    assert r.operacoes.select("Chave", "A", "B", "Diferenca", "Tipo").rows() == [
        ("grande", 100_000, 200_000, -100_000, "Sem padrão"),
        ("so_b", 0, 40_000, -40_000, "Só em B"),
        ("so_a", 30_000, 0, 30_000, "Só em A"),
        ("pequena", 10_200, 10_000, 200, "Sem padrão"),
    ]
    assert r.operacoes.height == r.chaves_com_diferenca


def test_tipo_do_erro_so_em_a_so_em_b_e_sem_padrao():
    a = base([("so_a", 30_000), ("so_a_dentro", 100), ("as_duas", 10_500), ("igual", 7_000)])
    b = base([("so_b", 40_000), ("so_b_dentro", 50), ("as_duas", 10_000), ("igual", 7_000)])

    r = conciliar(a, b, tolerancia=100)

    assert dict(r.operacoes.select("Chave", "Tipo").iter_rows()) == {
        "so_b": "Só em B",
        "so_a": "Só em A",
        "as_duas": "Sem padrão",
    }


def test_chave_presente_nas_duas_com_valor_zero_num_lado_nao_e_orfa():
    a = base([("zero_em_a", 0), ("zero_em_b", 20_000)])
    b = base([("zero_em_a", 30_000), ("zero_em_b", 0)])

    r = conciliar(a, b, tolerancia=100)

    assert r.operacoes["Tipo"].to_list() == ["Sem padrão", "Sem padrão"]


def test_tipo_do_erro_e_calculado_so_na_data_base_mais_recente():
    # x é Só em A na Data-base 1 e está nas duas na 2; y é Só em B só na Data-base 1.
    a = base_com_data_bases({1: [("x", 50_000)], 2: [("x", 50_000), ("y", 9_000)]})
    b = base_com_data_bases({1: [("y", 9_000)], 2: [("x", 10_000)]})

    r = conciliar(a, b, tolerancia=100)

    assert r.operacoes.select("Chave", "Tipo").rows() == [("x", "Sem padrão"), ("y", "Só em A")]
    assert r.por_tipo.rows() == [("Sem padrão", 1, 40_000), ("Só em A", 1, 9_000)]


def test_por_tipo_do_erro_soma_chaves_e_diferenca_absoluta_da_maior_para_a_menor():
    a = base([("a1", 1_000), ("a2", -2_000), ("p1", 10_000), ("p2", 50_000), ("p3", 1_000)])
    b = base([("b1", 30_000), ("p1", 9_000), ("p2", 50_000), ("p3", 2_000)])

    r = conciliar(a, b, tolerancia=100)

    assert r.por_tipo.columns == ["Tipo", "Chaves", "Absoluta"]
    assert r.por_tipo.rows() == [("Só em B", 1, 30_000), ("Só em A", 2, 3_000), ("Sem padrão", 2, 2_000)]


def aberta_desde(r) -> dict:
    """{Chave: (Aberta desde, ou antes)} das Operações com Diferença."""
    return {chave: (desde, ou_antes) for chave, desde, ou_antes in r.operacoes.select("Chave", "Desde", "OuAntes").rows()}


def test_diferenca_que_some_e_volta_tem_aberta_desde_na_data_da_volta():
    # x tem Diferença em 1, some em 2 (A = B) e volta em 3; y some em 2 por estar ausente das duas bases.
    a = base_com_data_bases(
        {1: [("x", 5_000), ("y", 9_000)], 2: [("x", 1_000)], 3: [("x", 5_000), ("y", 9_000)], 4: [("x", 7_000), ("y", 9_000)]}
    )
    b = base_com_data_bases({1: [("x", 1_000)], 2: [("x", 1_000)], 3: [("x", 1_000)], 4: [("x", 1_000)]})

    r = conciliar(a, b, tolerancia=100)

    assert aberta_desde(r) == {"x": (dia(3), False), "y": (dia(3), False)}


def test_diferenca_que_so_muda_de_valor_mantem_o_aberta_desde_original():
    a = base_com_data_bases({1: [("x", 1_000)], 2: [("x", 5_000)], 3: [("x", -8_000)], 4: [("x", 2_000)]})
    b = base_com_data_bases({1: [("x", 1_000)], 2: [("x", 1_000)], 3: [("x", 1_000)], 4: [("x", 1_000)]})

    r = conciliar(a, b, tolerancia=100)

    assert aberta_desde(r) == {"x": (dia(2), False)}


def test_diferenca_que_cai_para_dentro_da_tolerancia_conta_como_sumida():
    a = base_com_data_bases({1: [("x", 5_000)], 2: [("x", 1_100)], 3: [("x", 5_000)]})
    b = base_com_data_bases({1: [("x", 1_000)], 2: [("x", 1_000)], 3: [("x", 1_000)]})

    r = conciliar(a, b, tolerancia=100)

    assert aberta_desde(r) == {"x": (dia(3), False)}


def test_diferenca_presente_desde_a_primeira_data_base_e_marcada_ou_antes_e_contada():
    # A Data-base 1 está só em A: a primeira comum é a 2.
    a = base_com_data_bases(
        {1: [("z", 1)], 2: [("x", 5_000), ("y", 3_000)], 3: [("x", 6_000), ("y", 3_000), ("w", 4_000)]}
    )
    b = base_com_data_bases({2: [("x", 1_000), ("y", 3_000)], 3: [("x", 1_000), ("y", 1_000)]})

    r = conciliar(a, b, tolerancia=100)

    assert aberta_desde(r) == {"x": (dia(2), True), "y": (dia(3), False), "w": (dia(3), False)}
    assert r.abertas_desde_a_primeira == 1


def test_com_uma_so_data_base_toda_diferenca_e_ou_antes():
    r = conciliar(base([("x", 5_000), ("y", 1)]), base([("x", 1_000), ("y", 1)]), tolerancia=100)

    assert aberta_desde(r) == {"x": (DIA, True)}
    assert r.abertas_desde_a_primeira == 1
