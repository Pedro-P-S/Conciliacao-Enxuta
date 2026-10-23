"""Seam 2: arquivos → CLI → `.xlsx`, lido com openpyxl e conferido contra o gabarito."""

from datetime import date, datetime

import openpyxl
import pytest

from conciliacao_enxuta.cli import main
from conciliacao_enxuta.exemplo import gerar_bases_exemplo

FORMATO_REAIS = "#,##0.00"


def ler_resumo(caminho) -> dict:
    """O quadro do Resumo como {rótulo: célula}."""
    ws = openpyxl.load_workbook(caminho)["Resumo"]
    return {linha[0].value: linha[1] for linha in ws.iter_rows(min_col=1, max_col=2) if linha[0].value}


def test_cli_gera_o_excel_com_o_resumo_do_gabarito_na_pasta_da_base_a(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    codigo = main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    esperado = tmp_path / f"conciliacao_{gabarito.data_base.isoformat()}.xlsx"
    assert codigo == 0
    assert capsys.readouterr().out.strip() == str(esperado)
    assert abas_visiveis(openpyxl.load_workbook(esperado)) == ["Resumo", "Operações com Diferença"]

    conferir_quadro_do_resumo(esperado, gabarito)


def conferir_quadro_do_resumo(caminho, gabarito) -> None:
    """O quadro do Resumo bate com o gabarito, com a Tolerância padrão e os formatos de data e reais."""
    resumo = ler_resumo(caminho)
    assert resumo["Data-base mais recente"].value == datetime.combine(gabarito.data_base, datetime.min.time())
    assert resumo["Data-base mais recente"].number_format == "DD/MM/YYYY"
    assert resumo["Tolerância"].value == 1.00
    assert resumo["Total A"].value == gabarito.total_a / 100
    assert resumo["Total B"].value == gabarito.total_b / 100
    assert resumo["Diferença total"].value == gabarito.diferenca_total / 100
    assert resumo["Diferença absoluta"].value == gabarito.diferenca_absoluta / 100
    assert resumo["Chaves com Diferença"].value == gabarito.chaves_com_diferenca
    for rotulo in ["Tolerância", "Total A", "Total B", "Diferença total", "Diferença absoluta"]:
        assert resumo[rotulo].number_format == FORMATO_REAIS


def abas_visiveis(wb) -> list[str]:
    return [ws.title for ws in wb.worksheets if ws.sheet_state == "visible"]


def test_resumo_tem_grafico_de_linha_da_diferenca_absoluta_com_os_dados_na_aba_oculta(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    wb = openpyxl.load_workbook(capsys.readouterr().out.strip())
    assert wb["_grafico"].sheet_state == "hidden"
    assert abas_visiveis(wb) == ["Resumo", "Operações com Diferença"]
    linhas = list(wb["_grafico"].iter_rows(values_only=True))
    assert linhas[0] == ("Data-base", "Diferença absoluta")
    assert linhas[1:] == [
        (datetime.combine(data, datetime.min.time()), absoluta / 100) for data, absoluta in gabarito.historico
    ]
    assert len(linhas) - 1 == 131  # uma por dia útil de abril a setembro de 2026

    resumo = wb["Resumo"]
    assert [type(g).__name__ for g in resumo._charts] == ["LineChart"]
    # Sem tabela de histórico: nenhuma data além da Data-base mais recente no Resumo
    datas = [c.value for linha in resumo.iter_rows() for c in linha if isinstance(c.value, datetime)]
    assert datas == [datetime.combine(gabarito.data_base, datetime.min.time())]
    # O gráfico fica abaixo de tudo o que está escrito no Resumo, com uma linha em branco (âncora começa em 0)
    assert resumo._charts[0].anchor._from.row > resumo.max_row


def avisos_de_data_bases_ignoradas(caminho) -> list[str]:
    ws = openpyxl.load_workbook(caminho)["Resumo"]
    return [c.value for c in ws["A"] if isinstance(c.value, str) and c.value.startswith("Data-bases ignoradas")]


def test_varias_data_bases_o_resumo_usa_a_maior_comum_e_avisa_a_que_esta_so_na_base_b(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    assert gabarito.data_base == date(2026, 9, 30)
    assert gabarito.data_bases_so_em_b == (date(2026, 10, 1),)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    caminho = capsys.readouterr().out.strip()
    assert caminho.endswith("conciliacao_2026-09-30.xlsx")
    assert ler_resumo(caminho)["Total B"].value == gabarito.total_b / 100
    assert avisos_de_data_bases_ignoradas(caminho) == [
        "Data-bases ignoradas por estarem só na Base B: 01/10/2026."
    ]


def test_aviso_lista_as_data_bases_de_cada_base_e_some_quando_nao_ha_nenhuma(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text(
        "Chave,Data,Valor\n1,2026-09-28,10.00\n1,2026-09-29,10.00\n1,2026-09-30,10.00\n", encoding="utf-8"
    )
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n1,2026-10-01,10.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    assert avisos_de_data_bases_ignoradas(capsys.readouterr().out.strip()) == [
        "Data-bases ignoradas por estarem só na Base A: 28/09/2026, 29/09/2026.",
        "Data-bases ignoradas por estarem só na Base B: 01/10/2026.",
    ]

    main(["conciliar", str(base_a), str(base_a)])

    assert avisos_de_data_bases_ignoradas(capsys.readouterr().out.strip()) == []


@pytest.mark.parametrize(("texto", "centavos"), [("0,50", 50), ("1,00", 100), ("2,5", 250), ("10", 1000)])
def test_tolerancia_no_formato_brasileiro(tmp_path, capsys, texto, centavos):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b), "--tolerancia", texto])

    caminho = capsys.readouterr().out.strip()
    assert ler_resumo(caminho)["Tolerância"].value == centavos / 100


def test_saida_em_outra_pasta_sobrescreve_o_arquivo_existente(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path / "bases")
    saida = tmp_path / "saida"
    saida.mkdir()
    esperado = saida / f"conciliacao_{gabarito.data_base.isoformat()}.xlsx"
    esperado.write_text("arquivo antigo")

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b), "--saida", str(saida)])

    assert capsys.readouterr().out.strip() == str(esperado)
    assert ler_resumo(esperado)["Chaves com Diferença"].value == gabarito.chaves_com_diferenca


@pytest.mark.parametrize("texto", ["-1,00", "abc", "Infinity", "NaN"])
def test_tolerancia_invalida_e_recusada_com_mensagem(tmp_path, capsys, texto):
    gabarito = gerar_bases_exemplo(tmp_path)

    with pytest.raises(SystemExit) as saida:
        main(["conciliar", str(gabarito.base_a), str(gabarito.base_b), f"--tolerancia={texto}"])

    assert saida.value.code == 2
    assert "Tolerância inválida" in capsys.readouterr().err
    assert not list(tmp_path.glob("*.xlsx"))


AVISO_SEM_CHAVE = "Linhas sem Chave, fora do cruzamento"


def ler_aviso_sem_chave(caminho) -> dict | None:
    """O aviso de linhas sem Chave como {base: (linhas, soma em reais, formato da soma)}, ou None se não há."""
    linhas = list(openpyxl.load_workbook(caminho)["Resumo"].iter_rows(min_col=1, max_col=3))
    inicio = next((i for i, linha in enumerate(linhas) if linha[0].value == AVISO_SEM_CHAVE), None)
    if inicio is None:
        return None
    assert [c.value for c in linhas[inicio][1:]] == ["Linhas", "Soma"]
    return {
        linha[0].value: (linha[1].value, linha[2].value, linha[2].number_format)
        for linha in linhas[inicio + 1 : inicio + 3]
    }


def test_resumo_avisa_as_linhas_sem_chave_de_cada_base_e_os_totais_somam_as_chaves_repetidas(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    assert gabarito.sem_chave_a.linhas > 0 and gabarito.sem_chave_b.linhas > 0

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    caminho = capsys.readouterr().out.strip()
    assert ler_aviso_sem_chave(caminho) == {
        "Base A": (gabarito.sem_chave_a.linhas, gabarito.sem_chave_a.soma / 100, FORMATO_REAIS),
        "Base B": (gabarito.sem_chave_b.linhas, gabarito.sem_chave_b.soma / 100, FORMATO_REAIS),
    }
    resumo = ler_resumo(caminho)
    assert resumo["Total A"].value == gabarito.total_a / 100
    assert resumo["Total B"].value == gabarito.total_b / 100
    assert resumo["Diferença total"].value == gabarito.diferenca_total / 100
    assert resumo["Diferença absoluta"].value == gabarito.diferenca_absoluta / 100
    assert resumo["Chaves com Diferença"].value == gabarito.chaves_com_diferenca


def test_sem_linhas_sem_chave_o_resumo_nao_tem_aviso(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n1,2026-09-30,5.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,15.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    caminho = capsys.readouterr().out.strip()
    assert ler_aviso_sem_chave(caminho) is None
    assert ler_resumo(caminho)["Chaves com Diferença"].value == 0


def test_sem_data_base_comum_a_mensagem_e_simples_e_nenhum_excel_e_gerado(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-29,10.00\n1,2026-09-30,10.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-10-01,10.00\n", encoding="utf-8")

    codigo = main(["conciliar", str(base_a), str(base_b)])

    saida = capsys.readouterr()
    assert codigo == 1
    assert saida.out == ""
    assert saida.err.strip() == "A Base A e a Base B não têm nenhuma Data-base em comum."
    assert not list(tmp_path.glob("*.xlsx"))


def test_base_vazia_tambem_da_a_mensagem_simples(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n", encoding="utf-8")

    assert main(["conciliar", str(base_a), str(base_b)]) == 1
    assert capsys.readouterr().err.strip() == "A Base A e a Base B não têm nenhuma Data-base em comum."
    assert not list(tmp_path.glob("*.xlsx"))


@pytest.mark.parametrize("formato", ["csv", "xlsx", "parquet"])
def test_bases_em_csv_xlsx_ou_parquet_dao_o_resumo_do_gabarito(tmp_path, capsys, formato):
    gabarito = gerar_bases_exemplo(tmp_path, formato)
    assert gabarito.base_a.suffix == gabarito.base_b.suffix == f".{formato}"

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    caminho = capsys.readouterr().out.strip()
    conferir_quadro_do_resumo(caminho, gabarito)
    assert ler_aviso_sem_chave(caminho) == {
        "Base A": (gabarito.sem_chave_a.linhas, gabarito.sem_chave_a.soma / 100, FORMATO_REAIS),
        "Base B": (gabarito.sem_chave_b.linhas, gabarito.sem_chave_b.soma / 100, FORMATO_REAIS),
    }
    assert avisos_de_data_bases_ignoradas(caminho) == [
        "Data-bases ignoradas por estarem só na Base B: 01/10/2026."
    ]


def valores_do_resumo(caminho) -> list:
    return [[c.value for c in linha] for linha in openpyxl.load_workbook(caminho)["Resumo"].iter_rows()]


def test_base_a_em_xlsx_e_base_b_em_parquet_dao_o_mesmo_resumo_que_em_csv(tmp_path, capsys):
    em_csv = gerar_bases_exemplo(tmp_path / "csv")
    em_xlsx = gerar_bases_exemplo(tmp_path / "misturado", "xlsx")
    em_parquet = gerar_bases_exemplo(tmp_path / "misturado", "parquet")

    main(["conciliar", str(em_csv.base_a), str(em_csv.base_b)])
    main(["conciliar", str(em_xlsx.base_a), str(em_parquet.base_b)])

    caminho_csv, caminho_misturado = capsys.readouterr().out.split()
    assert valores_do_resumo(caminho_misturado) == valores_do_resumo(caminho_csv)


def test_extensao_nao_suportada_da_mensagem_simples_com_o_nome_do_arquivo(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    estranho = tmp_path / "base_b.txt"
    estranho.write_text("Chave;Data;Valor\n", encoding="utf-8")

    codigo = main(["conciliar", str(gabarito.base_a), str(estranho)])

    saida = capsys.readouterr()
    assert codigo == 1
    assert saida.out == ""
    assert saida.err.strip() == "base_b.txt: formato não suportado. Use .csv, .xlsx ou .parquet."
    assert "Traceback" not in saida.err
    assert not list(tmp_path.glob("*.xlsx"))


def conciliar_com_erro(tmp_path, capsys, conteudo_a: str) -> str:
    """Roda a CLI com a Base A dada e uma Base B boa; confere o código e que nada foi gerado; devolve a mensagem."""
    base_a, base_b = tmp_path / "base_a.csv", tmp_path / "base_b.csv"
    base_a.write_text(conteudo_a, encoding="utf-8")
    base_b.write_text("Chave;Data;Valor\n1;30/09/2026;10,00\n", encoding="utf-8")

    codigo = main(["conciliar", str(base_a), str(base_b)])

    saida = capsys.readouterr()
    assert codigo != 0
    assert saida.out == ""
    assert "Traceback" not in saida.err
    assert not list(tmp_path.glob("*.xlsx"))
    return saida.err.strip()


def test_falta_de_coluna_diz_qual_falta_em_qual_arquivo_e_as_colunas_encontradas(tmp_path, capsys):
    mensagem = conciliar_com_erro(tmp_path, capsys, "\ufeff CHAVE ;data;Vlr\n1;30/09/2026;10,00\n")

    assert mensagem == "base_a.csv: falta a coluna Valor. Colunas encontradas: CHAVE, data, Vlr."


def test_varias_colunas_faltando_sao_todas_nomeadas(tmp_path, capsys):
    mensagem = conciliar_com_erro(tmp_path, capsys, "Chave;Conta\n1;X\n")

    assert mensagem == "base_a.csv: faltam as colunas Data, Valor. Colunas encontradas: Chave, Conta."


@pytest.mark.parametrize("texto", ["12,3,4", "abc", "99.999.999.999.999.999.999,00"])
def test_valor_ilegivel_diz_o_arquivo_a_linha_e_o_conteudo(tmp_path, capsys, texto):
    mensagem = conciliar_com_erro(tmp_path, capsys, f"Chave;Data;Valor\n1;30/09/2026;10,00\n2;30/09/2026;{texto}\n")

    assert mensagem == f"base_a.csv, linha 3: Valor ilegível: {texto!r}."


@pytest.mark.parametrize("texto", ["31/02/2026", "ontem"])
def test_data_ilegivel_diz_o_arquivo_a_linha_e_o_conteudo(tmp_path, capsys, texto):
    mensagem = conciliar_com_erro(tmp_path, capsys, f"Chave;Data;Valor\n1;{texto};10,00\n")

    assert mensagem == f"base_a.csv, linha 2: Data ilegível: {texto!r}."


@pytest.mark.parametrize(
    ("linha", "mensagem"),
    [("2;30/09/2026;", "base_a.csv, linha 3: Valor vazio."), ("2;;10,00", "base_a.csv, linha 3: Data vazia.")],
)
def test_valor_ou_data_vazio_numa_linha_com_chave_diz_o_arquivo_e_a_linha(tmp_path, capsys, linha, mensagem):
    assert conciliar_com_erro(tmp_path, capsys, f"Chave;Data;Valor\n1;30/09/2026;10,00\n{linha}\n") == mensagem


def test_aba_operacoes_com_diferenca_lista_as_chaves_da_data_base_mais_recente_da_maior_para_a_menor(
    tmp_path, capsys
):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.strip())["Operações com Diferença"]
    linhas = list(ws.iter_rows())
    assert [c.value for c in linhas[0]] == ["Chave", "Valor A", "Valor B", "Diferença"]
    assert [tuple(c.value for c in linha) for linha in linhas[1:]] == [
        (chave, a / 100, b / 100, d / 100) for chave, a, b, d in gabarito.operacoes
    ]
    assert len(linhas) - 1 == gabarito.chaves_com_diferenca
    assert all(c.number_format == FORMATO_REAIS for linha in linhas[1:] for c in linha[1:])
    assert ws.freeze_panes == "A2"
    assert ws.auto_filter.ref == f"A1:D{gabarito.chaves_com_diferenca + 1}"
