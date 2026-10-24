"""Seam 2: arquivos → CLI → `.xlsx`, lido com openpyxl e conferido contra o gabarito."""

import stat
from datetime import date, datetime

import openpyxl
import pytest

from conciliacao_enxuta.cli import main
from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, conciliar
from conciliacao_enxuta.excel import gravar_excel
from conciliacao_enxuta.exemplo import DIFERENCAS_SEM_CHAVE, gerar_bases_exemplo
from conciliacao_enxuta.leitura import ler_base

FORMATO_REAIS = "#,##0.00"
FORMATO_PERCENTUAL = "0.00%"
CABECALHO_POR_ATRIBUTO = ["Atributo", "Valor", "Diferença absoluta", "Diferença acima do peso"]
TITULO_PROBLEMATICOS = "Atributos Problemáticos"
ABAS = ["Resumo", "Por Tipo do Erro", "Por Atributo", "Operações com Diferença", "Erros"]


def ler_resumo(caminho) -> dict:
    """O quadro do Resumo como {rótulo: célula}."""
    ws = openpyxl.load_workbook(caminho)["Resumo"]
    return {linha[0].value: linha[1] for linha in ws.iter_rows(min_col=1, max_col=2) if linha[0].value}


def test_cli_gera_o_excel_com_o_resumo_do_gabarito_na_pasta_da_base_a(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    codigo = main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    esperado = tmp_path / f"conciliacao_{gabarito.data_base.isoformat()}.xlsx"
    assert codigo == 0
    assert capsys.readouterr().out.splitlines()[0] == str(esperado)
    assert abas_visiveis(openpyxl.load_workbook(esperado)) == ABAS

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

    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])
    assert wb["_grafico"].sheet_state == "hidden"
    assert abas_visiveis(wb) == ABAS
    linhas = list(wb["_grafico"].iter_rows(max_col=2, values_only=True))
    assert linhas[0] == ("Data-base", "Diferença absoluta")
    assert linhas[1:] == [
        (datetime.combine(data, datetime.min.time()), absoluta / 100) for data, absoluta in gabarito.historico
    ]
    assert len(linhas) - 1 == 131  # uma por dia útil de abril a setembro de 2026

    resumo = wb["Resumo"]
    assert [type(g).__name__ for g in resumo._charts][-1] == "LineChart"
    # Sem tabela de histórico: nenhuma data além da Data-base mais recente no Resumo
    datas = [c.value for linha in resumo.iter_rows() for c in linha if isinstance(c.value, datetime)]
    assert datas == [datetime.combine(gabarito.data_base, datetime.min.time())]
    # O gráfico fica abaixo de tudo o que está escrito no Resumo, com uma linha em branco (âncora começa em 0)
    assert resumo._charts[-1].anchor._from.row > resumo.max_row


def test_resumo_tem_grafico_de_barras_da_idade_com_os_dados_ao_lado_dos_da_linha(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])
    # As 5 faixas sempre, mesmo vazias, com as Chaves no rótulo; "1 Chave" no singular. As 3 linhas sem Chave, que
    # se repetem desde a primeira Data-base, caem em 91 a 365 dias e entram no rótulo dela.
    barras = list(wb["_grafico"].iter_rows(min_col=4, max_col=5, max_row=6, values_only=True))
    assert barras == [
        ("Idade da Diferença", "Diferença absoluta"),
        ("Até 30 dias (1 Chave)", gabarito.por_idade[0][3] / 100),
        ("31 a 90 dias (1 Chave)", gabarito.por_idade[1][3] / 100),
        ("91 a 365 dias (138 Chaves, 3 linhas sem Chave)", gabarito.por_idade[2][3] / 100),
        ("366 dias a 5 anos (0 Chaves)", 0),
        ("Mais de 5 anos (0 Chaves)", 0),
    ]
    assert sum(absoluta for _, absoluta in barras[1:]) == pytest.approx(gabarito.diferenca_absoluta / 100)
    # Os dados da linha continuam nas colunas A e B
    assert wb["_grafico"]["A1"].value == "Data-base"

    resumo = wb["Resumo"]
    assert [type(g).__name__ for g in resumo._charts] == ["BarChart", "LineChart"]
    barras_no_resumo, linha_no_resumo = resumo._charts
    assert resumo.max_row < barras_no_resumo.anchor._from.row < linha_no_resumo.anchor._from.row


def test_grafico_de_linha_do_resumo_e_uma_linha_so_de_uma_cor_sem_suavizacao(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    linha = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Resumo"]._charts[-1]
    # Sem varyColors explícito o Excel pinta cada trecho de uma cor
    assert linha.varyColors is False
    assert [serie.smooth for serie in linha.series] == [False]


def test_titulos_dos_graficos_do_resumo_ficam_acima_da_area_sem_cobri_la(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    graficos = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Resumo"]._charts
    # Sem overlay explícito o Excel desenha o título por cima das barras e da linha
    assert [grafico.title.overlay for grafico in graficos] == [False, False]


def test_rotulo_da_faixa_traz_1_linha_sem_chave_no_singular_e_nao_muda_sem_elas(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    # Chave 1 com Diferença de 10,00 e uma linha sem Chave de 5,00 em A, ambas abertas na própria Data-base
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,110.00\n,2026-09-30,5.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,100.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])
    barras = list(wb["_grafico"].iter_rows(min_row=2, min_col=4, max_col=5, max_row=3, values_only=True))
    assert barras == [("Até 30 dias (1 Chave, 1 linha sem Chave)", 15.00), ("31 a 90 dias (0 Chaves)", 0)]


def avisos_de_data_bases_ignoradas(caminho) -> list[str]:
    ws = openpyxl.load_workbook(caminho)["Resumo"]
    return [c.value for c in ws["A"] if isinstance(c.value, str) and "Data-base" in c.value and "ignorad" in c.value]


def linhas_de_erros(caminho) -> list[tuple]:
    return list(openpyxl.load_workbook(caminho)["Erros"].iter_rows(values_only=True))


DATA_BASE_SO_NA_B = ("Base B", None, None, "01/10/2026", None, "Data-base só na Base B")


def test_varias_data_bases_o_resumo_usa_a_maior_comum_e_a_que_esta_so_na_base_b_vai_para_a_aba_erros(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    assert gabarito.data_base == date(2026, 9, 30)
    assert gabarito.data_bases_so_em_b == (date(2026, 10, 1),)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    caminho = capsys.readouterr().out.splitlines()[0]
    assert caminho.endswith("conciliacao_2026-09-30.xlsx")
    assert ler_resumo(caminho)["Total B"].value == gabarito.total_b / 100
    assert linhas_de_erros(caminho)[1] == DATA_BASE_SO_NA_B
    assert avisos_de_data_bases_ignoradas(caminho) == []


def test_data_bases_ignoradas_vem_em_ordem_de_data_antes_das_linhas_rejeitadas(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text(
        "Chave,Data,Valor\n1,2026-09-29,10.00\n1,2026-09-28,10.00\n1,2026-09-30,10.00\n2,ontem,1.00\n",
        encoding="utf-8",
    )
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n1,2026-10-01,10.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    caminho = capsys.readouterr().out.splitlines()[0]
    assert linhas_de_erros(caminho) == [
        tuple(CABECALHO_DE_ERROS),
        ("Base A", None, None, "28/09/2026", None, "Data-base só na Base A"),
        ("Base A", None, None, "29/09/2026", None, "Data-base só na Base A"),
        DATA_BASE_SO_NA_B,
        ("Base A", 5, "2", "ontem", "1,00", "Data ilegível"),
    ]
    assert avisos_de_data_bases_ignoradas(caminho) == []
    assert "Linhas rejeitadas: 1 (veja a aba Erros)" in avisos_do_resumo(caminho)

    main(["conciliar", str(base_b), str(base_b)])

    assert linhas_de_erros(capsys.readouterr().out.splitlines()[0]) == [tuple(CABECALHO_DE_ERROS)]


@pytest.mark.parametrize(("texto", "centavos"), [("0,50", 50), ("1,00", 100), ("2,5", 250), ("10", 1000)])
def test_tolerancia_no_formato_brasileiro(tmp_path, capsys, texto, centavos):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b), "--tolerancia", texto])

    caminho = capsys.readouterr().out.splitlines()[0]
    assert ler_resumo(caminho)["Tolerância"].value == centavos / 100


def test_saida_em_outra_pasta_sobrescreve_o_arquivo_existente(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path / "bases")
    saida = tmp_path / "saida"
    saida.mkdir()
    esperado = saida / f"conciliacao_{gabarito.data_base.isoformat()}.xlsx"
    esperado.write_text("arquivo antigo")
    html = esperado.with_suffix(".html")
    html.write_text("arquivo antigo")

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b), "--saida", str(saida)])

    assert capsys.readouterr().out.splitlines() == [str(esperado), str(html)]
    assert "arquivo antigo" not in html.read_text(encoding="utf-8")
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

    caminho = capsys.readouterr().out.splitlines()[0]
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

    caminho = capsys.readouterr().out.splitlines()[0]
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

    caminho = capsys.readouterr().out.splitlines()[0]
    conferir_quadro_do_resumo(caminho, gabarito)
    assert ler_aviso_sem_chave(caminho) == {
        "Base A": (gabarito.sem_chave_a.linhas, gabarito.sem_chave_a.soma / 100, FORMATO_REAIS),
        "Base B": (gabarito.sem_chave_b.linhas, gabarito.sem_chave_b.soma / 100, FORMATO_REAIS),
    }
    assert avisos_de_data_bases_ignoradas(caminho) == []


def valores_do_resumo(caminho) -> list:
    return [[c.value for c in linha] for linha in openpyxl.load_workbook(caminho)["Resumo"].iter_rows()]


def test_gerador_de_exemplo_aceita_o_formato_em_maiuscula(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path, "CSV")
    assert gabarito.base_a.name == "base_a.csv"
    assert gabarito.base_b.name == "base_b.csv"

    assert main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)]) == 0
    conferir_quadro_do_resumo(tmp_path / f"conciliacao_{gabarito.data_base.isoformat()}.xlsx", gabarito)


def test_base_a_em_xlsx_e_base_b_em_parquet_dao_o_mesmo_resumo_que_em_csv(tmp_path, capsys):
    em_csv = gerar_bases_exemplo(tmp_path / "csv")
    em_xlsx = gerar_bases_exemplo(tmp_path / "misturado", "xlsx")
    em_parquet = gerar_bases_exemplo(tmp_path / "misturado", "parquet")

    main(["conciliar", str(em_csv.base_a), str(em_csv.base_b)])
    main(["conciliar", str(em_xlsx.base_a), str(em_parquet.base_b)])

    caminho_csv, _, caminho_misturado, _ = capsys.readouterr().out.splitlines()
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


CABECALHO_DE_ERROS = ["Base", "Linha", "Chave", "Data", "Valor", "Motivo"]


def conciliar_com_linhas_rejeitadas(tmp_path, capsys, conteudo_a: str) -> str:
    """Roda a CLI com a Base A dada e uma Base B boa; confere que deu certo e devolve o caminho do `.xlsx`."""
    base_a, base_b = tmp_path / "base_a.csv", tmp_path / "base_b.csv"
    base_a.write_text(conteudo_a, encoding="utf-8")
    base_b.write_text("Chave;Data;Valor\n1;30/09/2026;10,00\n", encoding="utf-8")

    assert main(["conciliar", str(base_a), str(base_b)]) == 0
    return capsys.readouterr().out.splitlines()[0]


@pytest.mark.parametrize(
    ("linha", "data", "valor", "motivo"),
    [
        ("2;30/09/2026;12,3,4", "30/09/2026", "12,3,4", "Valor ilegível"),
        ("2;30/09/2026;abc", "30/09/2026", "abc", "Valor ilegível"),
        ("2;30/09/2026;99.999.999.999.999.999.999,00", "30/09/2026", "99.999.999.999.999.999.999,00", "Valor ilegível"),
        ("2;31/02/2026;10,00", "31/02/2026", "10,00", "Data ilegível"),
        ("2;ontem;10,00", "ontem", "10,00", "Data ilegível"),
        ("2;30/09/2026;", "30/09/2026", None, "Valor vazio"),
        ("2;;10,00", None, "10,00", "Data vazia"),
    ],
)
def test_linha_com_data_ou_valor_ruim_vai_para_a_aba_erros_e_a_conciliacao_segue(
    tmp_path, capsys, linha, data, valor, motivo
):
    caminho = conciliar_com_linhas_rejeitadas(tmp_path, capsys, f"Chave;Data;Valor\n1;30/09/2026;10,00\n{linha}\n")

    wb = openpyxl.load_workbook(caminho)
    assert abas_visiveis(wb) == ABAS
    ws = wb["Erros"]
    assert list(ws.iter_rows(values_only=True)) == [tuple(CABECALHO_DE_ERROS), ("Base A", 3, "2", data, valor, motivo)]
    assert ws.freeze_panes == "A2"
    assert ws.auto_filter.ref == "A1:F2"
    assert ler_resumo(caminho)["Total A"].value == 10.00
    assert "Linhas rejeitadas: 1 (veja a aba Erros)" in avisos_do_resumo(caminho)


def test_aba_operacoes_com_diferenca_lista_as_chaves_da_data_base_mais_recente_da_maior_para_a_menor(
    tmp_path, capsys
):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Operações com Diferença"]
    linhas = list(ws.iter_rows())
    assert [c.value for c in linhas[0]] == [
        "Chave", "Valor A", "Valor B", "Diferença absoluta", "Tipo do Erro", "Aberta desde", "Linha sem Chave",
        "Produto", "Carteira", "Moeda", "Filial",
    ]
    # Valor A e Valor B com o sinal; a Diferença absoluta sem sinal
    assert [tuple(c.value for c in linha[:5]) for linha in linhas[1:]] == [
        (chave, a / 100, b / 100, abs(d) / 100, tipo) for chave, a, b, d, tipo in gabarito.operacoes
    ]
    assert any(d < 0 for _, _, _, d, _ in gabarito.operacoes)
    sinal_invertido = [linha for linha in linhas[1:] if linha[4].value == "Sinal invertido"]
    assert sinal_invertido and all(linha[1].value * linha[2].value < 0 for linha in sinal_invertido)
    assert len(linhas) - 1 == gabarito.chaves_com_diferenca
    assert all(c.number_format == FORMATO_REAIS for linha in linhas[1:] for c in linha[1:4])
    assert ws.freeze_panes == "A2"
    assert ws.auto_filter.ref == f"A1:K{gabarito.chaves_com_diferenca + 1}"


NOTA_POR_TIPO = "Uma Chave pode contar em mais de um Tipo do Erro."


def test_aba_por_tipo_do_erro_soma_as_chaves_e_a_diferenca_absoluta_de_cada_tipo_com_a_nota(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    assert {tipo for tipo, _, _ in gabarito.por_tipo} == {
        "Só em A", "Só em B", "Sinal invertido", "Duplicado", "Vírgula deslocada", "Dígitos trocados",
        "Casa com linha sem Chave", "Sem padrão",
    }
    # Uma Chave com dois Tipos conta nos dois
    assert "Duplicado; Dígitos trocados" in {tipo for *_, tipo in gabarito.operacoes}

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Por Tipo do Erro"]
    linhas = [linha for linha in ws.iter_rows() if any(c.value is not None for c in linha)]
    assert [c.value for c in linhas[0]] == ["Tipo do Erro", "Chaves", "Diferença absoluta"]
    tabela = linhas[1:-1]
    assert [(tipo.value, chaves.value, absoluta.value) for tipo, chaves, absoluta in tabela] == [
        (tipo, chaves, absoluta / 100) for tipo, chaves, absoluta in gabarito.por_tipo
    ]
    assert [absoluta for _, _, absoluta in gabarito.por_tipo] == sorted(
        (absoluta for _, _, absoluta in gabarito.por_tipo), reverse=True
    )
    assert all(absoluta.number_format == FORMATO_REAIS for _, _, absoluta in tabela)
    assert linhas[-1][0].value == NOTA_POR_TIPO


def test_sem_chaves_com_diferenca_a_aba_por_tipo_do_erro_so_tem_o_cabecalho_e_a_nota(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Por Tipo do Erro"]
    valores = [[c.value for c in linha if c.value is not None] for linha in ws.iter_rows()]
    assert [v for v in valores if v] == [["Tipo do Erro", "Chaves", "Diferença absoluta"], [NOTA_POR_TIPO]]


def aberta_desde_mostrado(celula) -> str:
    """O texto que o Excel mostra na célula de Aberta desde: a data, com " ou antes" quando o formato o acrescenta."""
    texto = f"{celula.value:%d/%m/%Y}"
    assert celula.number_format in ("DD/MM/YYYY", 'DD/MM/YYYY" ou antes"')
    return texto + (" ou antes" if celula.number_format.endswith('" ou antes"') else "")


def test_aberta_desde_mostra_a_ultima_abertura_e_ou_antes_quando_vem_da_primeira_data_base(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    primeira = gabarito.historico[0][0]

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Operações com Diferença"]
    mostrado = {linha[0].value: aberta_desde_mostrado(linha[5]) for linha in ws.iter_rows(min_row=2)}
    assert mostrado == {
        chave: f"{desde:%d/%m/%Y}" + (" ou antes" if desde == primeira else "")
        for chave, desde in gabarito.aberta_desde.items()
    }
    # As Chaves plantadas: some e volta, cai para dentro da Tolerância na véspera, só abre depois e muda de valor
    assert mostrado["C00021"] == "16/06/2026"
    assert mostrado["C00031"] == "30/09/2026"
    assert mostrado["C00051"] == "03/08/2026"
    assert mostrado["C00001"] == "01/04/2026 ou antes"
    assert isinstance(ws["F2"].value, datetime)


def avisos_do_resumo(caminho) -> list[str]:
    """Os textos da coluna A do Resumo abaixo do quadro (o último é Chaves com Diferença) e acima dos Atributos
    Problemáticos, na ordem."""
    textos = [c.value for c in openpyxl.load_workbook(caminho)["Resumo"]["A"] if isinstance(c.value, str)]
    fim = textos.index(TITULO_PROBLEMATICOS) if TITULO_PROBLEMATICOS in textos else len(textos)
    return textos[textos.index("Chaves com Diferença") + 1 : fim]


def test_resumo_nao_avisa_das_chaves_abertas_desde_a_primeira_data_base(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    assert any(desde == date(2026, 4, 1) for desde in gabarito.aberta_desde.values())

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    avisos = avisos_do_resumo(capsys.readouterr().out.splitlines()[0])
    assert not any("ou antes" in aviso for aviso in avisos)
    assert avisos[0] == AVISO_SEM_CHAVE


FAIXAS = ["Até 30 dias", "31 a 90 dias", "91 a 365 dias", "366 dias a 5 anos", "Mais de 5 anos"]


def test_resumo_nao_tem_tabela_de_idade_e_os_avisos_vem_logo_abaixo_do_quadro(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    # As plantadas caem em até 30, 31 a 90 e 91 a 365 dias; as duas últimas faixas ficam vazias
    assert [nome for nome, *_ in gabarito.por_idade] == FAIXAS
    assert sum(chaves for _, chaves, _, _ in gabarito.por_idade) == gabarito.chaves_com_diferenca
    assert sum(linhas for _, _, linhas, _ in gabarito.por_idade) == len(DIFERENCAS_SEM_CHAVE)
    assert sum(absoluta for *_, absoluta in gabarito.por_idade) == gabarito.diferenca_absoluta

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Resumo"]
    textos = [c.value for linha in ws.iter_rows() for c in linha if isinstance(c.value, str)]
    assert "Idade da Diferença" not in textos
    assert not any(texto.startswith(faixa) for texto in textos for faixa in FAIXAS)
    # Quadro nas linhas 1 a 7, uma em branco, e os avisos
    assert ws["A7"].value == "Chaves com Diferença"
    assert ws["A8"].value is None
    assert ws["A9"].value == AVISO_SEM_CHAVE


@pytest.mark.parametrize("formato", ["csv", "xlsx", "parquet"])
def test_operacoes_mostram_os_atributos_com_o_nome_do_arquivo_e_o_valor_de_b_quando_a_esta_vazio(
    tmp_path, capsys, formato
):
    gabarito = gerar_bases_exemplo(tmp_path, formato)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Operações com Diferença"]
    cabecalho = [c.value for c in ws[1]]
    assert cabecalho[7:] == ["Produto", "Carteira", "Moeda", "Filial"]
    mostrado = {
        linha[0]: dict(zip(cabecalho[7:], linha[7:])) for linha in ws.iter_rows(min_row=2, values_only=True)
    }
    assert mostrado == gabarito.atributos
    # Produto vazio em A vem de B; a Filial só existe em B; a Chave só em A com Produto vazio fica sem ele
    produto_e_filial = {chave: (at["Produto"], at["Filial"]) for chave, at in mostrado.items()}
    assert produto_e_filial["C00021"] == ("Débito", "02")
    assert produto_e_filial["C00004"] == ("Crédito", "05")  # Só em B
    assert produto_e_filial["C00063"] == (None, None)  # Só em A
    assert produto_e_filial["C00013"] == ("Débito", None)  # Só em A


def test_bases_sem_atributos_as_operacoes_terminam_em_linha_sem_chave(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,90.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Operações com Diferença"]
    assert [c.value for c in ws[1]] == [
        "Chave", "Valor A", "Valor B", "Diferença absoluta", "Tipo do Erro", "Aberta desde", "Linha sem Chave"
    ]
    assert ws.auto_filter.ref == "A1:G2"


def test_por_atributo_mostra_a_diferenca_acima_do_peso_do_maior_para_o_menor(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Por Atributo"]
    linhas = list(ws.iter_rows())
    assert [c.value for c in linhas[0]] == CABECALHO_POR_ATRIBUTO
    mostrado = [tuple(c.value for c in linha) for linha in linhas[1:]]
    assert [linha[:3] for linha in mostrado] == [
        (atributo, valor, absoluta / 100) for atributo, valor, absoluta, _ in gabarito.por_atributo
    ]
    assert [linha[3] for linha in mostrado] == pytest.approx([acima for _, _, _, acima in gabarito.por_atributo])
    assert all(linha[2].number_format == FORMATO_REAIS and linha[3].number_format == FORMATO_PERCENTUAL for linha in linhas[1:])
    assert ws.auto_filter.ref is None
    # A Carteira Legado tem pouco peso no total e muita Diferença; a Moeda BRL, que todas as Chaves têm, não aparece
    assert mostrado[0][:2] == ("Carteira", "Legado")
    assert ("Moeda", "BRL") not in [linha[:2] for linha in mostrado]
    assert all(linha[3] > 0 for linha in mostrado)
    acima = [linha[3] for linha in mostrado]
    assert acima == sorted(acima, reverse=True)


def test_bases_sem_atributos_tem_a_aba_por_atributo_so_com_o_cabecalho(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,90.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])
    assert abas_visiveis(wb) == ABAS
    assert [[c.value for c in linha] for linha in wb["Por Atributo"].iter_rows()] == [CABECALHO_POR_ATRIBUTO]


def ler_problematicos(caminho) -> list | None:
    """As linhas da tabela de Atributos Problemáticos do Resumo (sem o cabeçalho), ou None se ela não aparece."""
    linhas = list(openpyxl.load_workbook(caminho)["Resumo"].iter_rows(min_col=1, max_col=4))
    inicio = next((i for i, linha in enumerate(linhas) if linha[0].value == TITULO_PROBLEMATICOS), None)
    if inicio is None:
        return None
    assert [c.value for c in linhas[inicio + 1]] == CABECALHO_POR_ATRIBUTO
    corpo = []
    for linha in linhas[inicio + 2 :]:
        if linha[0].value is None:
            break
        corpo.append(linha)
    return corpo


def test_resumo_mostra_os_atributos_problematicos_do_gabarito_depois_dos_avisos(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    caminho = capsys.readouterr().out.splitlines()[0]
    linhas = ler_problematicos(caminho)
    mostrado = [tuple(c.value for c in linha) for linha in linhas]
    esperado = gabarito.por_atributo[:5]
    assert [linha[:3] for linha in mostrado] == [(atributo, valor, absoluta / 100) for atributo, valor, absoluta, _ in esperado]
    assert [linha[3] for linha in mostrado] == pytest.approx([acima for _, _, _, acima in esperado])
    assert mostrado[0][:2] == ("Carteira", "Legado")
    assert all(linha[2].number_format == FORMATO_REAIS and linha[3].number_format == FORMATO_PERCENTUAL for linha in linhas)
    # Depois dos avisos
    coluna_a = [c.value for c in openpyxl.load_workbook(caminho)["Resumo"]["A"]]
    assert coluna_a.index(TITULO_PROBLEMATICOS) > coluna_a.index(AVISO_SEM_CHAVE)
    ultimo_aviso = max(i for i, v in enumerate(coluna_a) if isinstance(v, str) and v.startswith("Linhas rejeitadas"))
    assert coluna_a.index(TITULO_PROBLEMATICOS) > ultimo_aviso


def test_sem_atributo_acima_do_peso_o_resumo_nao_tem_atributos_problematicos(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    # A única Chave tem toda a Diferença e todo o peso: BRL fica com Diferença acima do peso 0
    base_a.write_text("Chave,Data,Valor,Moeda\n1,2026-09-30,10.00,BRL\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,90.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    assert ler_problematicos(capsys.readouterr().out.splitlines()[0]) is None


def gravar_com_limite(base_a, base_b, pasta, limite):
    """Arquivos → Resultado → `.xlsx` com o limite de linhas reduzido, que a CLI não expõe."""
    (lida_a, rejeitadas_a), (lida_b, rejeitadas_b) = ler_base(base_a), ler_base(base_b)
    resultado = conciliar(lida_a, lida_b, TOLERANCIA_PADRAO, rejeitadas_a, rejeitadas_b)
    return gravar_excel(resultado, pasta, limite=limite)


def test_acima_do_limite_a_aba_mostra_as_maiores_com_o_aviso_na_linha_1(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    # 5 Chaves com Diferença: 10, 50, 30, 40 e 20 reais; o Produto anda junto com a Chave
    base_a.write_text(
        "Chave,Data,Valor,Produto\n"
        "1,2026-09-30,110.00,p1\n2,2026-09-30,150.00,p2\n3,2026-09-30,130.00,p3\n"
        "4,2026-09-30,140.00,p4\n5,2026-09-30,120.00,p5\n",
        encoding="utf-8",
    )
    base_b.write_text(
        "Chave,Data,Valor\n1,2026-09-30,100.00\n2,2026-09-30,100.00\n3,2026-09-30,100.00\n"
        "4,2026-09-30,100.00\n5,2026-09-30,100.00\n",
        encoding="utf-8",
    )

    caminho = gravar_com_limite(base_a, base_b, tmp_path, limite=3)

    aviso = "Nem todas as operações com diferença couberam: mostrando 3 de 5, as maiores."
    ws = openpyxl.load_workbook(caminho)["Operações com Diferença"]
    assert ws["A1"].value == aviso
    assert [c.value for c in ws[2]] == [
        "Chave", "Valor A", "Valor B", "Diferença absoluta", "Tipo do Erro", "Aberta desde", "Linha sem Chave",
        "Produto",
    ]
    linhas = list(ws.iter_rows(min_row=3, values_only=True))
    assert [(chave, diferenca, produto) for chave, _, _, diferenca, _, _, _, produto in linhas] == [
        ("2", 50.0, "p2"), ("4", 40.0, "p4"), ("3", 30.0, "p3")
    ]
    assert ws.freeze_panes == "A3"
    assert ws.auto_filter.ref == "A2:H5"
    assert avisos_do_resumo(caminho)[-1] == aviso


def test_no_limite_nao_ha_corte_nem_aviso(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,110.00\n2,2026-09-30,150.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,100.00\n2,2026-09-30,100.00\n", encoding="utf-8")

    caminho = gravar_com_limite(base_a, base_b, tmp_path, limite=2)

    ws = openpyxl.load_workbook(caminho)["Operações com Diferença"]
    assert ws["A1"].value == "Chave"
    assert ws.freeze_panes == "A2"
    assert ws.auto_filter.ref == "A1:G3"
    assert not any(aviso.startswith("Nem todas") for aviso in avisos_do_resumo(caminho))


def test_o_corte_nas_bases_de_exemplo_mostra_as_maiores_do_gabarito_e_avisa_por_ultimo_no_resumo(tmp_path):
    gabarito = gerar_bases_exemplo(tmp_path)
    total = gabarito.chaves_com_diferenca
    assert total > 4

    caminho = gravar_com_limite(gabarito.base_a, gabarito.base_b, tmp_path, limite=4)

    aviso = f"Nem todas as operações com diferença couberam: mostrando 4 de {total}, as maiores."
    ws = openpyxl.load_workbook(caminho)["Operações com Diferença"]
    assert ws["A1"].value == aviso
    assert ws["A2"].value == "Chave"
    assert [linha[0] for linha in ws.iter_rows(min_row=3, values_only=True)] == [
        chave for chave, *_ in gabarito.operacoes[:4]
    ]
    avisos = avisos_do_resumo(caminho)
    assert avisos[-1] == aviso


def test_o_limite_e_o_total_saem_com_separador_de_milhar_brasileiro(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    chaves = range(1, 1235)
    base_a.write_text("Chave,Data,Valor\n" + "".join(f"{c},2026-09-30,{c}.50\n" for c in chaves), encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n" + "".join(f"{c},2026-09-30,0.00\n" for c in chaves), encoding="utf-8")

    caminho = gravar_com_limite(base_a, base_b, tmp_path, limite=1000)

    aviso = "Nem todas as operações com diferença couberam: mostrando 1.000 de 1.234, as maiores."
    ws = openpyxl.load_workbook(caminho)["Operações com Diferença"]
    assert ws["A1"].value == aviso
    assert ws.max_row == 1002
    assert avisos_do_resumo(caminho)[-1] == aviso


def test_sem_linhas_rejeitadas_a_aba_erros_so_tem_o_cabecalho_e_o_resumo_nao_avisa(tmp_path, capsys):
    caminho = conciliar_com_linhas_rejeitadas(tmp_path, capsys, "Chave;Data;Valor\n1;30/09/2026;10,00\n;;\n")

    ws = openpyxl.load_workbook(caminho)["Erros"]
    assert list(ws.iter_rows(values_only=True)) == [tuple(CABECALHO_DE_ERROS)]
    assert ws.freeze_panes == "A2"
    assert not any(aviso.startswith("Linhas rejeitadas") for aviso in avisos_do_resumo(caminho))


def test_acima_do_limite_a_aba_erros_mostra_os_primeiros_com_o_aviso_na_linha_1(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave;Data;Valor\n1;30/09/2026;10,00\n2;;1\n3;ontem;1\n", encoding="utf-8")
    base_b.write_text("Chave;Data;Valor\n1;30/09/2026;10,00\n4;30/09/2026;\n", encoding="utf-8")

    caminho = gravar_com_limite(base_a, base_b, tmp_path, limite=2)

    ws = openpyxl.load_workbook(caminho)["Erros"]
    assert list(ws.iter_rows(values_only=True)) == [
        ("Nem todos os erros couberam: mostrando 2 de 3.", None, None, None, None, None),
        tuple(CABECALHO_DE_ERROS),
        ("Base A", 3, "2", None, "1,00", "Data vazia"),
        ("Base A", 4, "3", "ontem", "1,00", "Data ilegível"),
    ]
    assert ws.freeze_panes == "A3"
    assert ws.auto_filter.ref == "A2:F4"
    # O aviso do Resumo conta as rejeitadas das duas bases, mesmo as que não couberam na aba
    assert "Linhas rejeitadas: 3 (veja a aba Erros)" in avisos_do_resumo(caminho)


@pytest.mark.parametrize("formato", ["csv", "xlsx", "parquet"])
def test_a_aba_erros_lista_as_linhas_rejeitadas_plantadas_e_o_resumo_avisa_quantas_sao(tmp_path, capsys, formato):
    gabarito = gerar_bases_exemplo(tmp_path, formato)
    motivos = {motivo for *_, motivo in gabarito.rejeitadas}
    if formato != "parquet":  # o .parquet tem tipos nativos: não guarda Data nem Valor ilegível
        assert motivos == {"Data vazia", "Data ilegível", "Valor vazio", "Valor ilegível"}
    assert {base for base, *_ in gabarito.rejeitadas} == ({"Base B"} if formato == "parquet" else {"Base A", "Base B"})

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    caminho = capsys.readouterr().out.splitlines()[0]
    linhas = list(openpyxl.load_workbook(caminho)["Erros"].iter_rows(values_only=True))
    # A Data-base plantada só na Base B vem antes das Linhas rejeitadas
    assert linhas == [tuple(CABECALHO_DE_ERROS), DATA_BASE_SO_NA_B, *gabarito.rejeitadas]
    assert f"Linhas rejeitadas: {len(gabarito.rejeitadas)} (veja a aba Erros)" in avisos_do_resumo(caminho)
    conferir_quadro_do_resumo(caminho, gabarito)


def test_coluna_linha_sem_chave_mostra_valor_data_base_e_base_de_cada_linha_que_casa(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    # Chave 1: Diferença +10.000,00, que a linha de 10.000,00 na Base B e a de −10.000,00 na Base A zeram;
    # Chave 2: −50,00, sem linha que case
    base_a.write_text(
        "Chave,Data,Valor\n1,2026-09-30,10000.00\n2,2026-09-30,50.00\n,2026-09-30,-10000.00\n", encoding="utf-8"
    )
    base_b.write_text(
        "Chave,Data,Valor\n1,2026-09-30,0.00\n2,2026-09-30,100.00\n,2026-09-30,10000.00\n", encoding="utf-8"
    )

    main(["conciliar", str(base_a), str(base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Operações com Diferença"]
    linhas = {linha[0]: linha for linha in ws.iter_rows(min_row=2, values_only=True)}
    assert linhas["1"][4] == "Casa com linha sem Chave"
    assert linhas["1"][6] == "−10.000,00 em 30/09/2026 na Base A; 10.000,00 em 30/09/2026 na Base B"
    assert linhas["2"][6] is None


def test_chave_plantada_casa_com_a_linha_sem_chave_de_uma_data_base_antiga(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Operações com Diferença"]
    linhas = [linha for linha in ws.iter_rows(min_row=2, values_only=True) if linha[6]]
    assert {linha[0]: linha[6] for linha in linhas} == gabarito.linha_sem_chave
    assert len(linhas) == 1
    chave, _, _, diferenca, tipo, _, texto, *_ = linhas[0]
    assert tipo == "Casa com linha sem Chave"
    assert texto.endswith("em 04/05/2026 na Base B")
    # A Diferença mudou depois da Data-base da linha: a de hoje não é o valor da linha
    valor_da_linha = abs(float(texto.split(" ")[0].lstrip("−").replace(".", "").replace(",", ".")))
    assert abs(diferenca - valor_da_linha) > TOLERANCIA_PADRAO / 100


def test_o_corte_da_aba_erros_conta_as_data_bases_ignoradas_junto_com_as_linhas_rejeitadas(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave;Data;Valor\n1;28/09/2026;10,00\n1;30/09/2026;10,00\n2;;1\n3;ontem;1\n", encoding="utf-8")
    base_b.write_text("Chave;Data;Valor\n1;30/09/2026;10,00\n", encoding="utf-8")

    caminho = gravar_com_limite(base_a, base_b, tmp_path, limite=2)

    assert linhas_de_erros(caminho) == [
        ("Nem todos os erros couberam: mostrando 2 de 3.", None, None, None, None, None),
        tuple(CABECALHO_DE_ERROS),
        ("Base A", None, None, "28/09/2026", None, "Data-base só na Base A"),
        ("Base A", 4, "2", None, "1,00", "Data vazia"),
    ]


def test_caractere_de_controle_no_valor_na_chave_ou_no_atributo_sai_no_excel_sem_ele_e_a_conciliacao_segue(
    tmp_path, capsys
):
    base_a, base_b = tmp_path / "base_a.csv", tmp_path / "base_b.csv"
    base_a.write_text(
        "Chave;Data;Valor;Filial\n1;30/09/2026;10,00;S\x02P\nK\x01;30/09/2026;5,00;RJ\n3;30/09/2026;1\x0200;SP\n",
        encoding="utf-8",
    )
    base_b.write_text("Chave;Data;Valor;Filial\n1;30/09/2026;20,00;SP\n", encoding="utf-8")

    assert main(["conciliar", str(base_a), str(base_b)]) == 0

    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])
    assert list(wb["Erros"].iter_rows(min_row=2, values_only=True)) == [
        ("Base A", 4, "3", "30/09/2026", "100", "Valor ilegível")
    ]
    operacoes = {linha[0]: linha[7] for linha in wb["Operações com Diferença"].iter_rows(min_row=2, values_only=True)}
    assert operacoes == {"1": "SP", "K": "RJ"}


def test_texto_que_comeca_com_igual_sai_no_excel_como_texto_e_nao_como_formula(tmp_path, capsys):
    base_a, base_b = tmp_path / "base_a.csv", tmp_path / "base_b.csv"
    base_a.write_text(
        "Chave;Data;Valor;Filial\n=K;30/09/2026;5,00;=A1+1\n3;30/09/2026;=SOMA(A1:A2);SP\n", encoding="utf-8"
    )
    base_b.write_text("Chave;Data;Valor;Filial\n1;30/09/2026;20,00;SP\n", encoding="utf-8")

    assert main(["conciliar", str(base_a), str(base_b)]) == 0

    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])
    valor_rejeitado = wb["Erros"]["E2"]
    assert (valor_rejeitado.value, valor_rejeitado.data_type) == ("=SOMA(A1:A2)", "s")
    chave, filial = next(
        (linha[0], linha[7]) for linha in wb["Operações com Diferença"].iter_rows(min_row=2) if linha[0].value == "=K"
    )
    assert (chave.data_type, filial.value, filial.data_type) == ("s", "=A1+1", "s")


def travar_o_xlsx_depois_de_uma_execucao(tmp_path, gabarito):
    """Gera os dois arquivos e deixa o `.xlsx` só de leitura, como o Excel faz ao abri-lo. Devolve {caminho: (bytes, mtime)}."""
    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])
    xlsx = tmp_path / f"conciliacao_{gabarito.data_base.isoformat()}.xlsx"
    html = xlsx.with_suffix(".html")
    xlsx.chmod(stat.S_IREAD)
    return {caminho: (caminho.read_bytes(), caminho.stat().st_mtime_ns) for caminho in (xlsx, html)}


def test_xlsx_que_nao_grava_nao_muda_nenhum_dos_dois_e_da_mensagem_simples_na_cli(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    antes = travar_o_xlsx_depois_de_uma_execucao(tmp_path, gabarito)
    capsys.readouterr()
    try:
        codigo = main(["conciliar", str(gabarito.base_a), str(gabarito.base_b), "--tolerancia", "5,00"])
    finally:
        next(iter(antes)).chmod(stat.S_IWRITE | stat.S_IREAD)

    saida = capsys.readouterr()
    assert codigo == 1
    assert saida.out == ""
    assert f"conciliacao_{gabarito.data_base.isoformat()}.xlsx" in saida.err
    assert "Traceback" not in saida.err and "Errno" not in saida.err
    assert {caminho: (caminho.read_bytes(), caminho.stat().st_mtime_ns) for caminho in antes} == antes
