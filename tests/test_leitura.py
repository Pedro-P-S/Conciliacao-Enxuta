"""Leitura de `.csv`, `.xlsx` e `.parquet`: nomes de coluna flexíveis, Valor e Data no formato brasileiro ou nativos."""

from datetime import date

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

    base = ler_base(caminho)

    assert base["Chave"].to_list() == ["1", "2", "3"]
    assert base["Valor"].to_list() == [29, -123_456, 9_223_372_036_854_775]


def test_nomes_de_coluna_sem_diferenciar_maiuscula_acento_e_espaco_nas_pontas(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(" CHAVE ,Dáta,valor \n1,2026-09-30,10\n", encoding="utf-8-sig")  # com BOM, como o Excel salva

    base = ler_base(caminho)

    assert base.columns == ["Chave", "Data", "Valor"]
    assert base["Valor"].to_list() == [1000]


def test_csv_em_cp1252_com_acento_e_lido(tmp_path):
    # Como o Excel em português salva o "CSV (separado por vírgulas)": cp1252, sem BOM
    caminho = tmp_path / "base.csv"
    caminho.write_text("Chave;Dáta;Valor;Descrição\n1;30/09/2026;10,00;Crédito à vista\n", encoding="cp1252")

    base = ler_base(caminho)

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


def test_xlsx_com_valor_numerico_data_do_excel_e_chave_numerica(tmp_path):
    caminho = tmp_path / "base.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Chave", "Data", "Valor"])
    ws.append([123, date(2026, 9, 30), 2.125])
    ws.append([" C1 ", date(2026, 9, 30), -1234.56])
    ws.append([456, date(2026, 9, 30), 10])
    wb.save(caminho)

    base = ler_base(caminho)

    assert base["Chave"].to_list() == ["123", "C1", "456"]
    assert base["Data"].to_list() == [date(2026, 9, 30)] * 3
    assert base["Valor"].to_list() == [213, -123_456, 1000]


def test_parquet_com_tipos_nativos(tmp_path):
    caminho = tmp_path / "base.parquet"
    pl.DataFrame(
        {"CHAVE": [7, 8], "data": [date(2026, 9, 30), date(2026, 9, 30)], "Valor": [0.29, -1234.56]}
    ).write_parquet(caminho)

    base = ler_base(caminho)

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

    base = ler_base(caminho)

    assert base.height == 151
    assert base["Chave"].to_list()[-2:] == ["149", "X1"]
    assert base["Data"].unique().to_list() == [date(2026, 9, 30)]
    assert base["Valor"].unique().to_list() == [123_456]


def test_erros_de_leitura_valem_tambem_para_xlsx_e_parquet(tmp_path):
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
    with pytest.raises(ErroDeLeitura, match=r"^base_c\.xlsx, linha 3: Valor ilegível: 'abc'\.$"):
        ler_base(xlsx_ilegivel)

    parquet = tmp_path / "base_b.parquet"
    pl.DataFrame({"Chave": ["1", "2"], "Data": [date(2026, 9, 30), None], "Valor": [1.0, 2.0]}).write_parquet(parquet)
    with pytest.raises(ErroDeLeitura, match=r"^base_b\.parquet, linha 2: Data vazia\.$"):
        ler_base(parquet)


def test_colunas_extras_viram_atributos_em_texto_com_o_nome_original(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(
        "Produto;CHAVE;Data;Valor;Região;filial\n"
        "Crédito; 1 ;30/09/2026;10,00;Sul;0101\n"
        ";2;30/09/2026;20,00;   ;0102\n",
        encoding="utf-8-sig",
    )

    base = ler_base(caminho)

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

    base = ler_base(caminho)

    assert base.schema["Filial"] == base.schema["Conta"] == pl.String
    assert base["Filial"].to_list() == ["101", "102"]
    assert base["Conta"].to_list() == [None, "1.1.01"]
