"""Leitura de `.csv`: nomes de coluna flexíveis, Valor e Data no formato brasileiro."""

from datetime import date

import pytest

from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, conciliar
from conciliacao_enxuta.leitura import ler_base


def test_valor_vira_centavos_exatos_mesmo_em_valores_grandes(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(
        "Chave,Data,Valor\n 1 ,2026-09-30,0.29\n2,2026-09-30,-1234.56\n3,2026-09-30,92233720368547.75\n",
        encoding="utf-8",
    )

    base = ler_base(caminho)

    assert base["Chave"].to_list() == ["1", "2", "3"]
    assert base["Valor"].to_list() == [29, -123_456, 9_223_372_036_854_775]


def test_nomes_de_coluna_sem_diferenciar_maiuscula_acento_e_espaco_nas_pontas(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(" CHAVE ,Dáta,valor \n1,2026-09-30,10\n", encoding="utf-8-sig")  # com BOM, como o Excel salva

    base = ler_base(caminho)

    assert base.columns == ["Chave", "Data", "Valor"]
    assert base["Valor"].to_list() == [1000]


@pytest.mark.parametrize(
    ("texto", "centavos"),
    [
        ("1.234,56", 123_456),
        ("(1.234,56)", -123_456),
        ("-1.234,56", -123_456),
        ("R$ 1.234,56", 123_456),
        ("-R$ 1.234,56", -123_456),
        ("R$ (500,00)", -50_000),
        ("1234,5", 123_450),
        ("0,29", 29),
        ("1.234.567,89", 123_456_789),
        ("92.233.720.368.547,75", 9_223_372_036_854_775),
        ("1.234", 123_400),
        ("R$ 1.234.567", 123_456_700),
        ("1234.5", 123_450),
    ],
)
def test_valor_no_formato_brasileiro_vira_centavos_exatos(tmp_path, texto, centavos):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;2026-09-30;{texto}\n", encoding="utf-8")

    assert ler_base(caminho)["Valor"].to_list() == [centavos]


@pytest.mark.parametrize("texto", ["31/01/2026", "2026-01-31", "46053", " 31/01/2026 "])
def test_data_em_dd_mm_aaaa_aaaa_mm_dd_ou_data_do_excel(tmp_path, texto):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;{texto};10\n", encoding="utf-8")

    assert ler_base(caminho)["Data"].to_list() == [date(2026, 1, 31)]


def test_chave_com_espaco_nas_pontas_em_a_cruza_com_a_mesma_chave_em_b(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave;Data;Valor\n 0123 ;30/09/2026;10,00\n", encoding="utf-8")
    base_b.write_text("Chave;Data;Valor\n0123;30/09/2026;10,00\n", encoding="utf-8")

    resultado = conciliar(ler_base(base_a), ler_base(base_b), TOLERANCIA_PADRAO)

    assert resultado.chaves_com_diferenca == 0


@pytest.mark.parametrize("texto", ["31/02/2026", "ontem"])
def test_data_ilegivel_nao_some_em_silencio(tmp_path, texto):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;{texto};10\n", encoding="utf-8")

    with pytest.raises(ValueError, match=texto):
        ler_base(caminho)
