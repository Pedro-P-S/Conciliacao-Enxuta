"""Leitura de `.csv`, `.xlsx` e `.parquet`: nomes de coluna flexíveis, Valor e Data no formato brasileiro ou nativos."""

from datetime import date, time, timedelta
from decimal import Decimal

import openpyxl
import polars as pl
import pytest

from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, conciliar
from conciliacao_enxuta.leitura import ErroDeLeitura, ler_base


def test_valor_vira_centavos_exatos_mesmo_em_valores_grandes(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(
        "Chave,Data,Valor\n 1 ,2026-09-30,0.29\n2,2026-09-30,-1234.56\n3,2026-09-30,92233720368547.75\n",
        encoding="utf-8",
    )

    base, _ = ler_base(caminho)

    assert base["Chave"].to_list() == ["1", "2", "3"]
    assert base["Valor"].to_list() == [29, -123_456, 9_223_372_036_854_775]


def test_nomes_de_coluna_sem_diferenciar_maiuscula_acento_e_espaco_nas_pontas(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(" CHAVE ,Dáta,valor \n1,2026-09-30,10\n", encoding="utf-8-sig")  # com BOM, como o Excel salva

    base, _ = ler_base(caminho)

    assert base.columns == ["Chave", "Data", "Valor"]
    assert base["Valor"].to_list() == [1000]


def test_csv_em_cp1252_com_acento_e_lido(tmp_path):
    # Como o Excel em português salva o "CSV (separado por vírgulas)": cp1252, sem BOM
    caminho = tmp_path / "base.csv"
    caminho.write_text("Chave;Dáta;Valor;Descrição\n1;30/09/2026;10,00;Crédito à vista\n", encoding="cp1252")

    base, _ = ler_base(caminho)

    assert base.columns == ["Chave", "Data", "Valor", "Descrição"]
    assert base["Descrição"].to_list() == ["Crédito à vista"]
    assert base["Valor"].to_list() == [1000]


def test_csv_que_nao_e_utf8_nem_cp1252_da_mensagem_simples(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_bytes(b"Chave;Data;Valor\n\x81;30/09/2026;10,00\n")  # 0x81 nem existe em cp1252

    with pytest.raises(ErroDeLeitura, match=r"^base\.csv: não foi possível ler o texto do arquivo"):
        ler_base(caminho)


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

    assert ler_base(caminho)[0]["Valor"].to_list() == [centavos]


@pytest.mark.parametrize("texto", ["31/01/2026", "2026-01-31", "46053", " 31/01/2026 "])
def test_data_em_dd_mm_aaaa_aaaa_mm_dd_ou_data_do_excel(tmp_path, texto):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;{texto};10\n", encoding="utf-8")

    assert ler_base(caminho)[0]["Data"].to_list() == [date(2026, 1, 31)]


def test_a_ultima_data_do_excel_e_31_12_9999(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text("Chave;Data;Valor\n1;2958465;10\n", encoding="utf-8")

    assert ler_base(caminho)[0]["Data"].to_list() == [date(9999, 12, 31)]


def test_chave_com_espaco_nas_pontas_em_a_cruza_com_a_mesma_chave_em_b(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave;Data;Valor\n 0123 ;30/09/2026;10,00\n", encoding="utf-8")
    base_b.write_text("Chave;Data;Valor\n0123;30/09/2026;10,00\n", encoding="utf-8")

    resultado = conciliar(ler_base(base_a)[0], ler_base(base_b)[0], TOLERANCIA_PADRAO)

    assert resultado.chaves_com_diferenca == 0


@pytest.mark.parametrize("texto", ["31/02/2026", "ontem", "31/01/26", "26-01-31", "2958466"])
def test_data_ilegivel_nao_some_em_silencio(tmp_path, texto):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;{texto};10\n", encoding="utf-8")

    base, rejeitadas = ler_base(caminho)

    assert base.height == 0
    assert rejeitadas_em_tuplas(rejeitadas) == [(2, "1", texto, "10,00", "Data ilegível")]


@pytest.mark.parametrize(
    ("texto", "em_reais"),
    [("1234567,891", "1.234.567,89"), ("(1.234,56)", "-1.234,56"), ("-0,5", "-0,50"), ("123456", "123.456,00")],
)
def test_valor_lido_de_linha_rejeitada_pela_data_sai_em_reais(tmp_path, texto, em_reais):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;ontem;{texto}\n", encoding="utf-8")

    _, rejeitadas = ler_base(caminho)

    assert rejeitadas_em_tuplas(rejeitadas) == [(2, "1", "ontem", em_reais, "Data ilegível")]


def test_xlsx_com_valor_numerico_data_do_excel_e_chave_numerica(tmp_path):
    caminho = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Chave", "Data", "Valor"])
    ws.append([123, date(2026, 9, 30), 2.125])
    ws.append([" C1 ", date(2026, 9, 30), -1234.56])
    ws.append([456, date(2026, 9, 30), 10])
    wb.save(caminho)

    base, _ = ler_base(caminho)

    assert base["Chave"].to_list() == ["123", "C1", "456"]
    assert base["Data"].to_list() == [date(2026, 9, 30)] * 3
    assert base["Valor"].to_list() == [213, -123_456, 1000]


def test_parquet_com_tipos_nativos(tmp_path):
    caminho = tmp_path / "base.parquet"
    pl.DataFrame(
        {"CHAVE": [7, 8], "data": [date(2026, 9, 30), date(2026, 9, 30)], "Valor": [0.29, -1234.56]}
    ).write_parquet(caminho)

    base, _ = ler_base(caminho)

    assert base["Chave"].to_list() == ["7", "8"]
    assert base["Data"].to_list() == [date(2026, 9, 30)] * 2
    assert base["Valor"].to_list() == [29, -123_456]


def test_xlsx_com_tipos_misturados_na_coluna_nao_perde_linha_nem_valor(tmp_path):
    caminho = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Chave", "Data", "Valor"])
    for i in range(150):  # mais linhas do que a amostra que o leitor usa para adivinhar o tipo
        ws.append([i, date(2026, 9, 30), 1234.56])
    ws.append(["X1", "30/09/2026", "R$ 1.234,56"])
    wb.save(caminho)

    base, _ = ler_base(caminho)

    assert base.height == 151
    assert base["Chave"].to_list()[-2:] == ["149", "X1"]
    assert base["Data"].unique().to_list() == [date(2026, 9, 30)]
    assert base["Valor"].unique().to_list() == [123_456]


def test_erros_e_linhas_rejeitadas_valem_tambem_para_xlsx_e_parquet(tmp_path):
    xlsx = tmp_path / "base_a.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["Chave", "Data", "Vlr"])
    wb.active.append([1, date(2026, 9, 30), 10])
    wb.save(xlsx)
    with pytest.raises(ErroDeLeitura, match=r"^base_a\.xlsx: falta a coluna Valor\. Colunas encontradas: Chave, Data, Vlr\.$"):
        ler_base(xlsx)

    xlsx_ilegivel = tmp_path / "base_c.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["Chave", "Data", "Valor"])
    wb.active.append([1, "30/09/2026", 10])
    wb.active.append([2, "30/09/2026", "abc"])
    wb.save(xlsx_ilegivel)
    assert rejeitadas_em_tuplas(ler_base(xlsx_ilegivel)[1]) == [(3, "2", "30/09/2026", "abc", "Valor ilegível")]

    parquet = tmp_path / "base_b.parquet"
    pl.DataFrame({"Chave": ["1", "2"], "Data": [date(2026, 9, 30), None], "Valor": [1.0, 2.0]}).write_parquet(parquet)
    assert rejeitadas_em_tuplas(ler_base(parquet)[1]) == [(2, "2", None, "2,00", "Data vazia")]


def test_colunas_extras_viram_atributos_em_texto_com_o_nome_original(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(
        "Produto;CHAVE;Data;Valor;Região;filial\n"
        "Crédito; 1 ;30/09/2026;10,00;Sul;0101\n"
        ";2;30/09/2026;20,00;   ;0102\n",
        encoding="utf-8-sig",
    )

    base, _ = ler_base(caminho)

    assert base.columns == ["Chave", "Data", "Valor", "Produto", "Região", "filial"]
    assert base["Produto"].to_list() == ["Crédito", None]
    assert base["Região"].to_list() == ["Sul", None]  # só espaço é vazio
    assert base["filial"].to_list() == ["0101", "0102"]  # texto: o zero à esquerda fica


def test_atributo_numerico_ou_data_no_xlsx_vira_texto(tmp_path):
    caminho = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Chave", "Data", "Valor", "Filial", "Conta"])
    ws.append(["1", date(2026, 9, 30), 10, 101, None])
    ws.append(["2", date(2026, 9, 30), 20, 102, "1.1.01"])
    wb.save(caminho)

    base, _ = ler_base(caminho)

    assert base.schema["Filial"] == base.schema["Conta"] == pl.String
    assert base["Filial"].to_list() == ["101", "102"]
    assert base["Conta"].to_list() == [None, "1.1.01"]


def rejeitadas_em_tuplas(rejeitadas: pl.DataFrame) -> list[tuple]:
    return list(rejeitadas.select("Linha", "Chave", "Data", "Valor", "Motivo").iter_rows())


def test_data_ou_valor_vazio_ou_ilegivel_vira_linha_rejeitada_e_a_leitura_segue(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(
        "Chave;Data;Valor\n"
        "1;30/09/2026;10,00\n"
        "2;;20,00\n"
        "3;31/02/2026;30,00\n"
        "4;30/09/2026;\n"
        "5;30/09/2026;abc\n"
        "6;30/09/2026;60,00\n",
        encoding="utf-8",
    )

    base, rejeitadas = ler_base(caminho)

    assert base["Chave"].to_list() == ["1", "6"]
    assert rejeitadas_em_tuplas(rejeitadas) == [
        (3, "2", None, "20,00", "Data vazia"),
        (4, "3", "31/02/2026", "30,00", "Data ilegível"),
        (5, "4", "30/09/2026", None, "Valor vazio"),
        (6, "5", "30/09/2026", "abc", "Valor ilegível"),
    ]


def test_linha_sem_chave_com_data_ou_valor_ruim_e_rejeitada_e_nao_vira_linha_sem_chave(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(
        "Chave;Data;Valor\n1;30/09/2026;10,00\n;ontem;20,00\n  ;30/09/2026;\n;30/09/2026;40,00\n", encoding="utf-8"
    )

    base, rejeitadas = ler_base(caminho)

    assert base.select("Chave", "Valor").rows() == [("1", 1000), (None, 4000)]
    assert rejeitadas_em_tuplas(rejeitadas) == [
        (3, None, "ontem", "20,00", "Data ilegível"),
        (4, None, "30/09/2026", None, "Valor vazio"),
    ]


def test_linha_toda_vazia_e_ignorada_sem_virar_rejeitada(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text("Chave;Data;Valor;Produto\n1;30/09/2026;10,00;X\n;;;\n  ; ;;Y\n2;;20,00;Z\n", encoding="utf-8")

    base, rejeitadas = ler_base(caminho)

    assert base["Chave"].to_list() == ["1"]
    assert rejeitadas_em_tuplas(rejeitadas) == [(5, "2", None, "20,00", "Data vazia")]


def test_a_linha_rejeitada_e_a_que_o_usuario_ve_no_xlsx_e_no_parquet(tmp_path):
    xlsx = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Chave", "Data", "Valor"])  # linha 1
    ws.append([1, date(2026, 9, 30), 10])
    ws.append([None, None, None])  # linha toda vazia, ignorada, mas conta na numeração
    ws.append([3, "ontem", "abc"])  # linha 4
    wb.save(xlsx)
    _, rejeitadas = ler_base(xlsx)
    assert rejeitadas_em_tuplas(rejeitadas) == [(4, "3", "ontem", "abc", "Data ilegível")]

    parquet = tmp_path / "base.parquet"
    pl.DataFrame(
        {"Chave": ["1", "2"], "Data": [date(2026, 9, 30), date(2026, 9, 30)], "Valor": [1.0, None]}
    ).write_parquet(parquet)
    _, rejeitadas = ler_base(parquet)
    assert rejeitadas_em_tuplas(rejeitadas) == [(2, "2", "2026-09-30", None, "Valor vazio")]


@pytest.mark.parametrize(
    ("texto", "centavos"),
    [
        ("1.234,567", 123_457),
        ("1234.565", 123_457),
        ("-0,005", -1),
        ("0,004", 0),
        ("(1,2345)", -123),
    ],
)
def test_valor_em_texto_com_mais_de_2_casas_e_arredondado_com_o_meio_para_longe_do_zero(tmp_path, texto, centavos):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;2026-09-30;{texto}\n", encoding="utf-8")

    base, rejeitadas = ler_base(caminho)

    assert base["Valor"].to_list() == [centavos]
    assert rejeitadas.height == 0


def test_valor_numerico_com_mais_de_2_casas_no_xlsx_e_no_parquet_e_arredondado(tmp_path):
    valores = [1234.567, 1234.565, -0.005]
    xlsx = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["Chave", "Data", "Valor"])
    for i, valor in enumerate(valores):
        wb.active.append([i, date(2026, 9, 30), valor])
    wb.save(xlsx)
    parquet = tmp_path / "base.parquet"
    pl.DataFrame({"Chave": ["0", "1", "2"], "Data": [date(2026, 9, 30)] * 3, "Valor": valores}).write_parquet(parquet)

    for caminho in (xlsx, parquet):
        base, rejeitadas = ler_base(caminho)
        assert base["Valor"].to_list() == [123_457, 123_457, -1]
        assert rejeitadas.height == 0


@pytest.mark.parametrize("texto", ["abc", "#", "12a", "1,5#", "R$ 10,00 x", "--5", "(5", "5)", "-(5)", "1.2.3,45,6"])
def test_valor_com_caractere_estranho_vira_linha_rejeitada(tmp_path, texto):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;30/09/2026;{texto}\n", encoding="utf-8")

    base, rejeitadas = ler_base(caminho)

    assert base.height == 0
    assert rejeitadas_em_tuplas(rejeitadas) == [(2, "1", "30/09/2026", texto, "Valor ilegível")]


def test_atributo_com_numero_letra_simbolo_ou_vazio_vira_texto_ou_nulo_nos_tres_formatos(tmp_path):
    conteudos = [101, "Sul", "#@!%&*", None]
    esperado = ["101", "Sul", "#@!%&*", None]
    csv = tmp_path / "base.csv"
    csv.write_text(
        "Chave;Data;Valor;Extra\n" + "".join(f"{i};30/09/2026;10,00;{c if c is not None else ''}\n" for i, c in enumerate(conteudos)),
        encoding="utf-8",
    )
    xlsx = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["Chave", "Data", "Valor", "Extra"])
    for i, c in enumerate(conteudos):
        wb.active.append([i, date(2026, 9, 30), 10, c])
    wb.save(xlsx)
    parquet = tmp_path / "base.parquet"
    pl.DataFrame(
        {"Chave": ["0", "1", "2", "3"], "Data": [date(2026, 9, 30)] * 4, "Valor": [10.0] * 4,
         "Extra": esperado, "Numero": [1, 2, None, 4], "Sim": [True, False, None, True]}
    ).write_parquet(parquet)

    for caminho in (csv, xlsx, parquet):
        base, rejeitadas = ler_base(caminho)
        assert base["Extra"].to_list() == esperado
        assert rejeitadas.height == 0
    base, _ = ler_base(parquet)
    assert base["Numero"].to_list() == ["1", "2", None, "4"]
    assert base["Sim"].to_list() == ["true", "false", None, "true"]


def test_atributo_de_tipo_incomum_no_parquet_vira_texto_e_nao_para_a_leitura(tmp_path):
    caminho = tmp_path / "base.parquet"
    pl.DataFrame(
        {"Chave": ["1", "2"], "Data": [date(2026, 9, 30)] * 2, "Valor": [1.0, 2.0],
         "Lista": [[1, 2], None], "Prazo": [timedelta(days=3), None]}
    ).write_parquet(caminho)

    base, rejeitadas = ler_base(caminho)

    assert base.schema["Lista"] == base.schema["Prazo"] == pl.String
    assert base["Lista"].to_list() == ["[1, 2]", None]
    assert base["Prazo"].to_list()[1] is None
    assert "3" in base["Prazo"].to_list()[0]
    assert rejeitadas.height == 0


def test_valor_numerico_nan_infinito_ou_grande_demais_no_parquet_vira_linha_rejeitada(tmp_path):
    caminho = tmp_path / "base.parquet"
    pl.DataFrame(
        {"Chave": ["1", "2", "3", "4"], "Data": [date(2026, 9, 30)] * 4, "Valor": [1.5, float("nan"), float("inf"), 1e30]}
    ).write_parquet(caminho)

    base, rejeitadas = ler_base(caminho)

    assert base["Valor"].to_list() == [150]
    assert [(linha, chave, motivo) for linha, chave, _, _, motivo in rejeitadas_em_tuplas(rejeitadas)] == [
        (2, "2", "Valor ilegível"),
        (3, "3", "Valor ilegível"),
        (4, "4", "Valor ilegível"),
    ]


def test_valor_numerico_grande_demais_no_xlsx_vira_linha_rejeitada(tmp_path):
    caminho = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["Chave", "Data", "Valor"])
    wb.active.append([1, date(2026, 9, 30), 1.5])
    wb.active.append([2, date(2026, 9, 30), 1e30])
    wb.save(caminho)

    base, rejeitadas = ler_base(caminho)

    assert base["Valor"].to_list() == [150]
    assert [(linha, chave, motivo) for linha, chave, _, _, motivo in rejeitadas_em_tuplas(rejeitadas)] == [
        (3, "2", "Valor ilegível"),
    ]


def test_data_numerica_nan_infinita_ou_grande_demais_no_parquet_vira_linha_rejeitada(tmp_path):
    caminho = tmp_path / "base.parquet"
    pl.DataFrame(
        {"Chave": ["1", "2", "3", "4"], "Data": [46295.0, float("nan"), float("inf"), 1e30], "Valor": [1.5] * 4}
    ).write_parquet(caminho)

    base, rejeitadas = ler_base(caminho)

    assert base["Data"].to_list() == [date(2026, 9, 30)]
    assert [(linha, chave, motivo) for linha, chave, _, _, motivo in rejeitadas_em_tuplas(rejeitadas)] == [
        (2, "2", "Data ilegível"),
        (3, "3", "Data ilegível"),
        (4, "4", "Data ilegível"),
    ]


def test_data_numerica_grande_demais_no_xlsx_vira_linha_rejeitada(tmp_path):
    caminho = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["Chave", "Data", "Valor"])
    wb.active.append([1, 46295, 1.5])
    wb.active.append([2, 1e30, 1.5])
    wb.save(caminho)

    base, rejeitadas = ler_base(caminho)

    assert base["Data"].to_list() == [date(2026, 9, 30)]
    assert [(linha, chave, motivo) for linha, chave, _, _, motivo in rejeitadas_em_tuplas(rejeitadas)] == [
        (3, "2", "Data ilegível"),
    ]


def test_chave_numerica_longa_no_xlsx_sai_igual_mesmo_com_data_grande_demais_em_outra_linha(tmp_path):
    caminho = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["Chave", "Data", "Valor"])
    wb.active.append([12345678901234567, 46295, 10])
    wb.active.append([100000000000000000, 46295, 10])
    wb.active.append([999, 1e30, 5])
    wb.active.append([888, 46295, 1e30])
    wb.save(caminho)

    base, rejeitadas = ler_base(caminho)

    assert base["Chave"].to_list() == ["12345678901234570", "100000000000000000"]
    # O Valor lido sai em reais; o que não pôde ser lido e a Data saem como vieram, número redondo sem `.0`
    assert rejeitadas_em_tuplas(rejeitadas) == [
        (4, "999", "1e+30", "5,00", "Data ilegível"),
        (5, "888", "46295", "1e+30", "Valor ilegível"),
    ]


@pytest.mark.parametrize("texto", ["1,234.56", "1.2.3,4", "1.2,3", "0.500,00"])
def test_valor_com_separadores_ambiguos_vira_linha_rejeitada(tmp_path, texto):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;30/09/2026;{texto}\n", encoding="utf-8")

    base, rejeitadas = ler_base(caminho)

    assert base.height == 0
    assert rejeitadas_em_tuplas(rejeitadas) == [(2, "1", "30/09/2026", texto, "Valor ilegível")]


@pytest.mark.parametrize(("texto", "centavos"), [("1.234", 123_400), ("0.125", 13), ("00.500", 50)])
def test_ponto_sem_virgula_e_milhar_so_em_grupos_de_3_digitos_senao_decimal(tmp_path, texto, centavos):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;30/09/2026;{texto}\n", encoding="utf-8")

    assert ler_base(caminho)[0]["Valor"].to_list() == [centavos]


@pytest.mark.parametrize("texto", ["99999999999999999999", "92233720368547758,08", "-92233720368547758,09"])
def test_valor_em_texto_que_nao_cabe_em_centavos_int64_vira_linha_rejeitada(tmp_path, texto):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;30/09/2026;{texto}\n2;30/09/2026;10,00\n", encoding="utf-8")

    base, rejeitadas = ler_base(caminho)

    assert base["Valor"].to_list() == [1000]
    assert rejeitadas_em_tuplas(rejeitadas) == [(2, "1", "30/09/2026", texto, "Valor ilegível")]


def test_valor_inteiro_do_parquet_que_nao_cabe_em_centavos_int64_vira_linha_rejeitada(tmp_path):
    caminho = tmp_path / "base.parquet"
    pl.DataFrame(
        {"Chave": ["1", "2", "3"], "Data": [date(2026, 9, 30)] * 3, "Valor": [10**17, 10, -(10**17)]},
        schema_overrides={"Valor": pl.Int64},
    ).write_parquet(caminho)
    sem_sinal = tmp_path / "sem_sinal.parquet"
    pl.DataFrame(
        {"Chave": ["1", "2"], "Data": [date(2026, 9, 30)] * 2, "Valor": [2**64 - 1, 10]},
        schema_overrides={"Valor": pl.UInt64},
    ).write_parquet(sem_sinal)

    base, rejeitadas = ler_base(caminho)
    assert base["Valor"].to_list() == [1000]
    assert rejeitadas["Motivo"].to_list() == ["Valor ilegível"] * 2
    assert rejeitadas["Linha"].to_list() == [1, 3]

    base, rejeitadas = ler_base(sem_sinal)
    assert base["Valor"].to_list() == [1000]
    assert rejeitadas["Motivo"].to_list() == ["Valor ilegível"]


@pytest.mark.parametrize(
    ("texto", "centavos"), [("0,00499999999999", 0), ("-1,23499999999999", -123), ("0,0050000000001", 1)]
)
def test_valor_em_texto_e_arredondado_para_centavos_uma_vez_so(tmp_path, texto, centavos):
    caminho = tmp_path / "base.csv"
    caminho.write_text(f"Chave;Data;Valor\n1;30/09/2026;{texto}\n", encoding="utf-8")

    assert ler_base(caminho)[0]["Valor"].to_list() == [centavos]


def test_valor_numerico_do_xlsx_e_do_parquet_e_arredondado_para_centavos_uma_vez_so(tmp_path):
    floats = [2.1249999999, 0.00499999999, -1.23499999999]
    xlsx = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["Chave", "Data", "Valor"])
    for i, valor in enumerate(floats):
        wb.active.append([i, date(2026, 9, 30), valor])
    wb.save(xlsx)
    parquet = tmp_path / "float.parquet"
    pl.DataFrame({"Chave": ["0", "1", "2"], "Data": [date(2026, 9, 30)] * 3, "Valor": floats}).write_parquet(parquet)
    decimais = [Decimal("2.1249999999"), Decimal("0.0049999999"), Decimal("123456789012345.67")]
    decimal = tmp_path / "decimal.parquet"
    pl.DataFrame(
        {"Chave": ["0", "1", "2"], "Data": [date(2026, 9, 30)] * 3, "Valor": pl.Series(decimais, dtype=pl.Decimal(25, 10))}
    ).write_parquet(decimal)

    assert ler_base(xlsx)[0]["Valor"].to_list() == [212, 0, -123]
    assert ler_base(parquet)[0]["Valor"].to_list() == [212, 0, -123]
    assert ler_base(decimal)[0]["Valor"].to_list() == [212, 0, 12_345_678_901_234_567]


def test_valor_e_data_de_tipos_do_parquet_sao_lidos_ou_viram_linha_rejeitada(tmp_path):
    caminho = tmp_path / "base.parquet"
    datas = [date(2026, 9, 30)] * 2
    colunas = {
        "decimal": (pl.Series(datas), pl.Series([Decimal("10.505"), Decimal("-2")], dtype=pl.Decimal(10, 3))),
        "categorical": (pl.Series(["30/09/2026", "ontem"], dtype=pl.Categorical), pl.Series(["1,50", "2"], dtype=pl.Categorical)),
        "bool": (pl.Series(datas), pl.Series([True, False])),
        "time": (pl.Series([time(10), time(11)]), pl.Series([1.0, 2.0])),
        "nulos": (pl.Series([None, None]), pl.Series(["1", "2"])),
    }
    lidos = {}
    for nome, (data, valor) in colunas.items():
        pl.DataFrame({"Chave": ["1", "2"], "Data": data, "Valor": valor}).write_parquet(caminho)
        base, rejeitadas = ler_base(caminho)
        lidos[nome] = (base["Valor"].to_list(), rejeitadas["Motivo"].to_list())

    assert lidos == {
        "decimal": ([1051, -200], []),
        "categorical": ([150], ["Data ilegível"]),
        "bool": ([], ["Valor ilegível", "Valor ilegível"]),
        "time": ([], ["Data ilegível", "Data ilegível"]),
        "nulos": ([], ["Data vazia", "Data vazia"]),
    }


def test_a_linha_rejeitada_do_xlsx_conta_as_linhas_vazias_antes_do_cabecalho(tmp_path):
    caminho = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws["A3"], ws["B3"], ws["C3"] = "Chave", "Data", "Valor"  # linhas 1 e 2 vazias
    ws.append([1, date(2026, 9, 30), 10])
    ws.append([2, "31/01/26", 10])  # linha 5
    wb.save(caminho)

    _, rejeitadas = ler_base(caminho)

    assert rejeitadas_em_tuplas(rejeitadas) == [(5, "2", "31/01/26", "10,00", "Data ilegível")]
