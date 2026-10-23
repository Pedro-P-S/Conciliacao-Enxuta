"""Seam 1: `conciliar` com DataFrames pequenos montados no teste."""

from datetime import date, timedelta

import polars as pl
import pytest

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


def test_linhas_sem_chave_contam_so_na_data_base_mais_recente_como_os_totais():
    # Em posições diárias, a mesma linha sem Chave se repete a cada Data-base: somar todas a contaria várias vezes.
    a = base_com_data_bases(
        {1: [("x", 100), ("", 500)], 2: [("x", 100), ("", 500)], 3: [("x", 100), ("", 500), ("", 7)]}
    )
    b = base_com_data_bases(
        {2: [("x", 100), ("", 2_000)], 3: [("x", 100), ("", 300)], 4: [("x", 100), ("", 9_000)]}
    )

    r = conciliar(a, b, tolerancia=100)

    assert r.data_base == dia(3)
    assert r.sem_chave_a == SemChave(linhas=2, soma=507)
    assert r.sem_chave_b == SemChave(linhas=1, soma=300)  # nem a Data-base 2, nem a 4, só em B


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
            2: [("pequena", 10_000), ("dentro", 10_000), ("so_b", 40_000), ("grande", 170_000), ("igual", 500)],
        }
    )

    r = conciliar(a, b, tolerancia=100)

    assert r.operacoes.columns == ["Chave", "A", "B", "Diferenca", "Tipo", "Desde", "OuAntes"]
    assert r.operacoes.select("Chave", "A", "B", "Diferenca", "Tipo").rows() == [
        ("grande", 100_000, 170_000, -70_000, "Sem padrão"),
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
    b = base([("b1", 30_000), ("p1", 9_000), ("p2", 50_000), ("p3", 2_300)])

    r = conciliar(a, b, tolerancia=100)

    assert r.por_tipo.columns == ["Tipo", "Chaves", "Absoluta"]
    assert r.por_tipo.rows() == [("Só em B", 1, 30_000), ("Só em A", 2, 3_000), ("Sem padrão", 2, 2_300)]


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


def test_diferenca_presente_desde_a_primeira_data_base_e_marcada_ou_antes():
    # A Data-base 1 está só em A: a primeira comum é a 2.
    a = base_com_data_bases(
        {1: [("z", 1)], 2: [("x", 5_000), ("y", 3_000)], 3: [("x", 6_000), ("y", 3_000), ("w", 4_000)]}
    )
    b = base_com_data_bases({2: [("x", 1_000), ("y", 3_000)], 3: [("x", 1_000), ("y", 1_000)]})

    r = conciliar(a, b, tolerancia=100)

    assert aberta_desde(r) == {"x": (dia(2), True), "y": (dia(3), False), "w": (dia(3), False)}


def test_com_uma_so_data_base_toda_diferenca_e_ou_antes():
    r = conciliar(base([("x", 5_000), ("y", 1)]), base([("x", 1_000), ("y", 1)]), tolerancia=100)

    assert aberta_desde(r) == {"x": (DIA, True)}


def tipos(a: pl.DataFrame, b: pl.DataFrame, tolerancia: int = 100) -> dict[str, str]:
    """{Chave: Tipo do Erro} das Operações com Diferença."""
    return dict(conciliar(a, b, tolerancia).operacoes.select("Chave", "Tipo").iter_rows())


def test_tipo_do_erro_sinal_invertido():
    a = base([("credito", 50_000), ("debito", -7_300)])
    b = base([("credito", -50_000), ("debito", 7_300)])

    assert tipos(a, b) == {"credito": "Sinal invertido", "debito": "Sinal invertido"}


def test_tipo_do_erro_duplicado_nos_dois_sentidos():
    a = base([("a_dobro", 20_000), ("b_dobro", -3_500)])
    b = base([("a_dobro", 10_000), ("b_dobro", -7_000)])

    assert tipos(a, b) == {"a_dobro": "Duplicado", "b_dobro": "Duplicado"}


def test_tipo_do_erro_virgula_deslocada_em_cada_fator():
    # A/B = 10, 100, 1000, 0,1, 0,01 e 0,001
    a = base(
        [("x10", 52_300), ("x100", 523_000), ("x1000", -5_230_000), ("d10", 5_230), ("d100", 5_230), ("d1000", 5_230)]
    )
    b = base(
        [("x10", 5_230), ("x100", 5_230), ("x1000", -5_230), ("d10", 52_300), ("d100", 523_000), ("d1000", 5_230_000)]
    )

    assert tipos(a, b) == dict.fromkeys(["x10", "x100", "x1000", "d10", "d100", "d1000"], "Vírgula deslocada")


def test_tipo_do_erro_digitos_trocados_exige_multiplo_de_9_e_os_mesmos_digitos():
    a = base([("trocados", 12_345), ("so_multiplo_de_9", 10_000), ("so_mesmos_digitos", 1_234)])
    b = base([("trocados", 13_245), ("so_multiplo_de_9", 10_900), ("so_mesmos_digitos", -4_321)])

    assert tipos(a, b) == {
        "trocados": "Dígitos trocados",  # Diferença de −900
        "so_multiplo_de_9": "Sem padrão",  # Diferença de −900, mas outros dígitos
        "so_mesmos_digitos": "Sem padrão",  # Diferença de 5.555, que não é múltiplo de 9
    }


def test_combinacao_lista_todos_os_tipos_na_ordem_da_spec_e_conta_a_chave_nos_dois():
    # 251.748 é o dobro de 125.874, com os mesmos dígitos, e a Diferença de 125.874 é múltiplo de 9
    a = base([("dobro_trocado", 251_748), ("so_a", 3_000)])
    b = base([("dobro_trocado", 125_874)])

    r = conciliar(a, b, tolerancia=100)

    assert dict(r.operacoes.select("Chave", "Tipo").iter_rows()) == {
        "dobro_trocado": "Duplicado; Dígitos trocados",
        "so_a": "Só em A",
    }
    assert r.por_tipo.rows() == [("Duplicado", 1, 125_874), ("Dígitos trocados", 1, 125_874), ("Só em A", 1, 3_000)]


def test_tolerancia_e_folga_no_sinal_invertido_no_duplicado_e_na_virgula_deslocada():
    # Tolerância de R$ 5,00: até 500 centavos de folga conta; 501 já não
    a = base(
        [
            ("quase_sinal", 50_000), ("sinal_fora", 50_000),
            ("quase_dobro", 20_500), ("dobro_fora", 20_501),
            ("quase_virgula", 100_500), ("virgula_fora", 100_501),
        ]
    )
    b = base(
        [
            ("quase_sinal", -49_500), ("sinal_fora", -49_499),
            ("quase_dobro", 10_000), ("dobro_fora", 10_000),
            ("quase_virgula", 1_000), ("virgula_fora", 1_000),
        ]
    )

    assert tipos(a, b, tolerancia=500) == {
        "quase_sinal": "Sinal invertido",
        "sinal_fora": "Sem padrão",
        "quase_dobro": "Duplicado",
        "dobro_fora": "Sem padrão",
        "quase_virgula": "Vírgula deslocada",
        "virgula_fora": "Sem padrão",
    }


def abertas_ha(dias_por_chave: dict[str, tuple[int, int]]) -> pl.DataFrame:
    """Base A em que cada Chave tem o Valor dado em toda Data-base desde `dias` antes de DIA até DIA.

    {Chave: (dias, Valor)}. Há ainda uma Data-base 3.000 dias antes, para nenhuma ser a primeira.
    """
    inicios = {DIA - timedelta(dias) for dias, _ in dias_por_chave.values()} | {DIA - timedelta(3_000)}
    return pl.concat(
        [
            base([(chave, valor) for chave, (dias, valor) in dias_por_chave.items() if data >= DIA - timedelta(dias)], data)
            for data in sorted(inicios | {DIA})
        ]
    )


def base_b_nas_mesmas_datas(a: pl.DataFrame) -> pl.DataFrame:
    """Base B com só uma Chave sem Diferença em cada Data-base de `a`."""
    datas = a["Data"].unique().sort()
    return pl.concat([base([("igual", 0)], data) for data in datas])


def test_bordas_das_faixas_de_idade():
    a = abertas_ha({f"d{n}": (n, n * 100) for n in [30, 31, 90, 91, 365, 366, 1826, 1827]})

    r = conciliar(a, base_b_nas_mesmas_datas(a), tolerancia=100)

    assert r.por_idade == (
        ("Até 30 dias", 1, 3_000),
        ("31 a 90 dias", 2, 3_100 + 9_000),
        ("91 a 365 dias", 2, 9_100 + 36_500),
        ("366 dias a 5 anos", 2, 36_600 + 182_600),
        ("Mais de 5 anos", 1, 182_700),
    )


def test_diferenca_aberta_na_propria_data_base_mais_recente_tem_idade_zero():
    a = abertas_ha({"hoje": (0, 5_000), "antiga": (100, 7_000)})

    r = conciliar(a, base_b_nas_mesmas_datas(a), tolerancia=100)

    assert r.por_idade[0] == ("Até 30 dias", 1, 5_000)


def test_faixas_de_idade_somam_as_chaves_com_diferenca_e_a_diferenca_absoluta():
    # Diferenças positivas e negativas, uma "ou antes" (desde a primeira Data-base) e faixas vazias
    a = abertas_ha({"x": (10, 5_000), "y": (10, -8_000), "z": (200, -3_000), "w": (3_000, 4_000)})

    r = conciliar(a, base_b_nas_mesmas_datas(a), tolerancia=100)

    assert [nome for nome, _, _ in r.por_idade] == [
        "Até 30 dias", "31 a 90 dias", "91 a 365 dias", "366 dias a 5 anos", "Mais de 5 anos"
    ]
    assert sum(chaves for _, chaves, _ in r.por_idade) == r.chaves_com_diferenca == 4
    assert sum(absoluta for _, _, absoluta in r.por_idade) == r.diferenca_absoluta == 20_000
    assert r.por_idade[1] == ("31 a 90 dias", 0, 0)
    assert r.por_idade[3] == ("366 dias a 5 anos", 0, 0)
    assert r.por_idade[4] == ("Mais de 5 anos", 1, 4_000)  # 3.000 dias: a faixa que a conta der, mesmo "ou antes"


def base_com_atributos(linhas: list[tuple[str, int, dict[str, str | None]]], data: date = DIA) -> pl.DataFrame:
    """Base lida com Atributos em texto: (Chave, Valor, {Atributo: valor})."""
    nomes = list(dict.fromkeys(nome for _, _, atributos in linhas for nome in atributos))
    return pl.DataFrame(
        {
            "Chave": [c for c, _, _ in linhas],
            "Data": [data] * len(linhas),
            "Valor": [v for _, v, _ in linhas],
            **{nome: [atributos.get(nome) for _, _, atributos in linhas] for nome in nomes},
        },
        schema={"Chave": pl.String, "Data": pl.Date, "Valor": pl.Int64, **{nome: pl.String for nome in nomes}},
    )


def test_atributo_vem_de_a_e_se_vazio_ou_ausente_vem_de_b():
    a = base_com_atributos(
        [
            ("cheio_em_a", 30_000, {"Produto": "Crédito", "Filial": "01"}),
            ("vazio_em_a", 20_000, {"Produto": None, "Filial": "02"}),
            ("so_em_a", 10_000, {"Produto": "Câmbio", "Filial": "03"}),
        ]
    )
    b = base_com_atributos(
        [
            ("cheio_em_a", 0, {"Produto": "Débito", "Canal": "Agência"}),
            ("vazio_em_a", 0, {"Produto": "Seguro", "Canal": None}),
            ("so_em_b", 40_000, {"Produto": "Consórcio", "Canal": "App"}),
        ]
    )

    r = conciliar(a, b, tolerancia=100)

    assert r.operacoes["Chave"].to_list() == ["so_em_b", "cheio_em_a", "vazio_em_a", "so_em_a"]
    # Todos os Atributos, primeiro os de A e depois os só de B, sem repetir nomes iguais
    assert r.atributos.columns == ["Produto", "Filial", "Canal"]
    assert r.atributos.rows() == [
        ("Consórcio", None, "App"),
        ("Crédito", "01", "Agência"),
        ("Seguro", "02", None),
        ("Câmbio", "03", None),
    ]


def test_chave_repetida_na_mesma_data_base_fica_com_os_atributos_da_primeira_linha():
    a = base_com_atributos(
        [("1", 10_000, {"Produto": "primeira"}), ("1", 5_000, {"Produto": "segunda"}), ("2", 700, {"Produto": "x"})]
    )
    b = base([("1", 0)])

    r = conciliar(a, b, tolerancia=100)

    assert r.operacoes.select("Chave", "A").rows() == [("1", 15_000), ("2", 700)]
    assert r.atributos["Produto"].to_list() == ["primeira", "x"]


def test_atributos_sao_os_da_data_base_mais_recente():
    a = pl.concat(
        [
            base_com_atributos([("1", 10_000, {"Produto": "antigo"})], date(2026, 9, 29)),
            base_com_atributos([("1", 10_000, {"Produto": "atual"})]),
        ]
    )
    b = pl.concat([base([("1", 0)], date(2026, 9, 29)), base([("1", 0)])])

    r = conciliar(a, b, tolerancia=100)

    assert r.atributos["Produto"].to_list() == ["atual"]


def test_bases_sem_atributos_nao_tem_atributos_nas_operacoes():
    r = conciliar(base([("1", 10_000)]), base([("1", 0)]), tolerancia=100)

    assert r.operacoes.height == 1
    assert r.atributos.columns == []


def test_valor_de_atributo_com_pouco_peso_e_muita_diferenca_fica_no_topo_por_atributo():
    # Legado pesa 1.000 de 301.000 no total e tem metade da Diferença absoluta; Atual pesa o resto e tem a outra metade
    a = base_com_atributos(
        [
            ("legado", 1_000, {"Carteira": "Legado"}),
            ("atual_1", 100_000, {"Carteira": "Atual"}),
            ("atual_2", 100_000, {"Carteira": "Atual"}),
            ("atual_3", 100_000, {"Carteira": "Atual"}),
        ]
    )
    b = base([("legado", 51_000), ("atual_1", 50_000), ("atual_2", 100_000), ("atual_3", 100_000)])

    r = conciliar(a, b, tolerancia=100)

    assert r.por_atributo.select("Atributo", "Valor", "Diferenca", "Parte").rows() == [
        ("Carteira", "Legado", -50_000, 0.5),
        ("Carteira", "Atual", 50_000, 0.5),
    ]


def test_valor_que_todas_as_chaves_tem_tem_concentracao_1_e_fica_abaixo_do_concentrado():
    a = base_com_atributos(
        [
            ("legado", 1_000, {"Carteira": "Legado", "Moeda": "BRL"}),
            ("atual_1", 100_000, {"Carteira": "Atual", "Moeda": "BRL"}),
            ("atual_2", 100_000, {"Carteira": "Atual", "Moeda": "BRL"}),
        ]
    )
    b = base([("legado", 51_000), ("atual_1", 50_000), ("atual_2", 100_000)])

    r = conciliar(a, b, tolerancia=100)

    assert r.por_atributo.select("Atributo", "Valor", "Diferenca", "Parte").rows() == [
        ("Carteira", "Legado", -50_000, 0.5),
        ("Moeda", "BRL", 0, 1.0),
        ("Carteira", "Atual", 50_000, 0.5),
    ]
    assert r.por_atributo["Concentracao"][1] == pytest.approx(1.0)


def test_peso_no_total_e_o_valor_a_absoluto_e_cai_para_o_valor_b_quando_a_e_zero():
    a = base_com_atributos(
        [
            ("a_zero", 0, {"Canal": "X"}),  # peso 10.000, de B
            ("a_vale", 10_000, {"Canal": "Z"}),  # peso 10.000, de A, e não os 60.000 de B
            ("negativo", -80_000, {"Canal": "Y"}),  # peso 80.000
        ]
    )
    b = base_com_atributos(
        [
            ("a_zero", 10_000, {"Canal": "X"}),
            ("a_vale", 60_000, {"Canal": "Z"}),
            ("negativo", -80_000, {"Canal": "Y"}),
            ("so_em_b", 10_000, {"Canal": "X"}),  # peso 10.000, de B
        ]
    )

    r = conciliar(a, b, tolerancia=100)

    # Peso total 110.000 e Diferença absoluta 70.000: Z = (50/70) ÷ (10/110) e X = (20/70) ÷ (20/110)
    assert r.por_atributo.select("Valor", "Diferenca").rows() == [("Z", -50_000), ("X", -20_000)]
    assert r.por_atributo["Concentracao"].to_list() == pytest.approx([55 / 7, 11 / 7])


def test_por_atributo_so_tem_os_valores_com_alguma_chave_com_diferenca():
    a = base_com_atributos(
        [
            ("com", 10_000, {"Produto": "Crédito"}),
            ("dentro", 10_050, {"Produto": "Débito"}),  # Diferença dentro da Tolerância
            ("igual", 10_000, {"Produto": "Câmbio"}),
            ("igual_credito", 10_000, {"Produto": "Crédito"}),
        ]
    )
    b = base([("com", 0), ("dentro", 10_000), ("igual", 10_000), ("igual_credito", 10_000)])

    r = conciliar(a, b, tolerancia=100)

    assert r.por_atributo.select("Valor", "Diferenca", "Parte").rows() == [("Crédito", 10_000, 1.0)]
