"""Seam 2: arquivos → CLI → `.xlsx`, lido com openpyxl e conferido contra o gabarito."""

import stat
from datetime import date, datetime

import openpyxl
import pytest

from conciliacao_enxuta.cli import conciliar_batimentos, main
from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, conciliar
from conciliacao_enxuta.excel import gravar_excel, rotulo_da_faixa
from conciliacao_enxuta.exemplo import DIFERENCAS_SEM_CHAVE, gerar_bases_exemplo
from conciliacao_enxuta.gui_estado import conciliar_pela_janela
from conftest import ler_base

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
    # Com vários Batimentos a `_grafico` desce mais, com os blocos nas outras colunas
    linhas = [l for l in wb["_grafico"].iter_rows(max_col=2, values_only=True) if l != (None, None)]
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


def test_grafico_de_linha_com_uma_data_base_tem_um_ponto_so_no_excel(tmp_path, capsys):
    # Sem isto, o Excel completa o eixo com datas que não existem, até a altura do bloco da `_grafico`
    (tmp_path / "a.csv").write_text("Chave;Data;Valor\n1;30/09/2026;10,00\n", encoding="utf-8")
    (tmp_path / "b.csv").write_text("Chave;Data;Valor\n1;30/09/2026;12,00\n", encoding="utf-8")

    main(["conciliar", str(tmp_path / "a.csv"), str(tmp_path / "b.csv")])

    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])
    serie = wb["Resumo"]._charts[-1].series[0]
    assert serie.val.numRef.f == "'_grafico'!$B$2"
    assert serie.cat.numRef.f == "'_grafico'!$A$2"


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


DATA_BASE_SO_NA_B = ("Todos", "Base B", None, None, "01/10/2026", None, "Data-base só na Base B")


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
        ("Todos", "Base A", None, None, "28/09/2026", None, "Data-base só na Base A"),
        ("Todos", "Base A", None, None, "29/09/2026", None, "Data-base só na Base A"),
        DATA_BASE_SO_NA_B,
        ("Todos", "Base A", 5, "2", "ontem", "1,00", "Data ilegível"),
    ]
    assert avisos_de_data_bases_ignoradas(caminho) == []
    assert "Linhas rejeitadas: 1 (veja a aba Erros)" in avisos_do_resumo(caminho)

    main(["conciliar", str(base_b), str(base_b)])

    assert linhas_de_erros(capsys.readouterr().out.splitlines()[0]) == [tuple(CABECALHO_DE_ERROS)]


@pytest.mark.parametrize(
    ("texto", "centavos"),
    [
        ("0,50", 50),
        ("1,00", 100),
        ("2,5", 250),
        ("10", 1000),
        ("1.000", 100_000),
        ("1.000,50", 100_050),
        ("0.5", 50),
        # Arredonda como o Valor das bases: o meio para longe do zero
        ("0,015", 2),
        ("0,025", 3),
    ],
)
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


@pytest.mark.parametrize("texto", ["-1,00", "abc", "Infinity", "NaN", "1,234.56", "1.2,3", "1e3"])
def test_tolerancia_invalida_e_recusada_com_mensagem(tmp_path, capsys, texto):
    gabarito = gerar_bases_exemplo(tmp_path)

    with pytest.raises(SystemExit) as saida:
        main(["conciliar", str(gabarito.base_a), str(gabarito.base_b), f"--tolerancia={texto}"])

    assert saida.value.code == 2
    assert "Tolerância inválida" in capsys.readouterr().err
    assert not list(tmp_path.glob("*.xlsx"))


def test_tolerancia_grande_demais_e_recusada_com_mensagem_simples(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    with pytest.raises(SystemExit) as saida:
        main(["conciliar", str(gabarito.base_a), str(gabarito.base_b), "--tolerancia", "999999999999999999999"])

    assert saida.value.code == 2
    erro = capsys.readouterr().err
    assert "Tolerância inválida" in erro
    assert "Traceback" not in erro
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


CABECALHO_DE_ERROS = ["Batimento", "Base", "Linha", "Chave", "Data", "Valor", "Motivo"]


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
    batimento = "Todos" if motivo.startswith("Data") else "Valor"
    assert list(ws.iter_rows(values_only=True)) == [
        tuple(CABECALHO_DE_ERROS), (batimento, "Base A", 3, "2", data, valor, motivo)
    ]
    assert ws.freeze_panes == "A2"
    assert ws.auto_filter.ref == "A1:G2"
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
        "Batimento", "Chave", "Valor A", "Valor B", "Diferença absoluta", "Tipo do Erro", "Aberta desde",
        "Linha sem Chave", "Produto", "Carteira", "Moeda", "Filial",
    ]
    # Valor A e Valor B com o sinal; a Diferença absoluta sem sinal. O Batimento Valor vem primeiro, depois o Juros
    total = gabarito.chaves_com_diferenca
    assert [tuple(c.value for c in linha[:6]) for linha in linhas[1 : total + 1]] == [
        ("Valor", chave, a / 100, b / 100, abs(d) / 100, tipo) for chave, a, b, d, tipo in gabarito.operacoes
    ]
    assert [tuple(c.value for c in linha[:6]) for linha in linhas[total + 1 :]] == [
        ("Juros", chave, a / 100, b / 100, abs(d) / 100, tipo) for chave, a, b, d, tipo in gabarito.juros.operacoes
    ]
    assert any(d < 0 for _, _, _, d, _ in gabarito.operacoes)
    sinal_invertido = [linha for linha in linhas[1:total + 1] if linha[5].value == "Sinal invertido"]
    assert sinal_invertido and all(linha[2].value * linha[3].value < 0 for linha in sinal_invertido)
    assert all(c.number_format == FORMATO_REAIS for linha in linhas[1:] for c in linha[2:5])
    assert ws.freeze_panes == "A2"
    assert ws.auto_filter.ref == f"A1:L{len(linhas)}"


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
    assert [c.value for c in linhas[0]] == ["Batimento", "Tipo do Erro", "Chaves", "Diferença absoluta"]
    tabela = [linha for linha in linhas[1:-1] if linha[0].value == "Valor"]
    assert [(tipo.value, chaves.value, absoluta.value) for _, tipo, chaves, absoluta in tabela] == [
        (tipo, chaves, absoluta / 100) for tipo, chaves, absoluta in gabarito.por_tipo
    ]
    assert {linha[0].value for linha in linhas[1:-1]} == {"Valor", "Juros"}
    assert [absoluta for _, _, absoluta in gabarito.por_tipo] == sorted(
        (absoluta for _, _, absoluta in gabarito.por_tipo), reverse=True
    )
    assert all(absoluta.number_format == FORMATO_REAIS for *_, absoluta in tabela)
    assert linhas[-1][0].value == NOTA_POR_TIPO


def test_sem_chaves_com_diferenca_a_aba_por_tipo_do_erro_so_tem_o_cabecalho_e_a_nota(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Por Tipo do Erro"]
    valores = [[c.value for c in linha if c.value is not None] for linha in ws.iter_rows()]
    assert [v for v in valores if v] == [["Batimento", "Tipo do Erro", "Chaves", "Diferença absoluta"], [NOTA_POR_TIPO]]


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
    mostrado = {
        linha[1].value: aberta_desde_mostrado(linha[6]) for linha in ws.iter_rows(min_row=2) if linha[0].value == "Valor"
    }
    assert mostrado == {
        chave: f"{desde:%d/%m/%Y}" + (" ou antes" if desde == primeira else "")
        for chave, desde in gabarito.aberta_desde.items()
    }
    # As Chaves plantadas: some e volta, cai para dentro da Tolerância na véspera, só abre depois e muda de valor
    assert mostrado["C00021"] == "16/06/2026"
    assert mostrado["C00031"] == "30/09/2026"
    assert mostrado["C00051"] == "03/08/2026"
    assert mostrado["C00001"] == "01/04/2026 ou antes"
    assert isinstance(ws["G2"].value, datetime)


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
    # O quadro termina em Chaves com Diferença, uma linha em branco e os avisos
    coluna_a = [c.value for c in ws["A"]]
    fim_do_quadro = coluna_a.index("Chaves com Diferença")
    assert coluna_a[fim_do_quadro + 1] is None
    assert coluna_a[fim_do_quadro + 2] == AVISO_SEM_CHAVE


@pytest.mark.parametrize("formato", ["csv", "xlsx", "parquet"])
def test_operacoes_mostram_os_atributos_com_o_nome_do_arquivo_e_o_valor_de_b_quando_a_esta_vazio(
    tmp_path, capsys, formato
):
    gabarito = gerar_bases_exemplo(tmp_path, formato)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Operações com Diferença"]
    cabecalho = [c.value for c in ws[1]]
    assert cabecalho[8:] == ["Produto", "Carteira", "Moeda", "Filial"]
    mostrado = {
        linha[1]: dict(zip(cabecalho[8:], linha[8:]))
        for linha in ws.iter_rows(min_row=2, values_only=True)
        if linha[0] == "Valor"
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
        "Batimento", "Chave", "Valor A", "Valor B", "Diferença absoluta", "Tipo do Erro", "Aberta desde",
        "Linha sem Chave",
    ]
    assert ws.auto_filter.ref == "A1:H2"


def test_por_atributo_mostra_a_diferenca_acima_do_peso_do_maior_para_o_menor(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Por Atributo"]
    linhas = list(ws.iter_rows())
    assert [c.value for c in linhas[0]] == ["Batimento", *CABECALHO_POR_ATRIBUTO]
    valor = [linha for linha in linhas[1:] if linha[0].value == "Valor"]
    assert {linha[0].value for linha in linhas[1:]} == {"Valor", "Juros"}
    mostrado = [tuple(c.value for c in linha[1:]) for linha in valor]
    assert [linha[:3] for linha in mostrado] == [
        (atributo, valor, absoluta / 100) for atributo, valor, absoluta, _ in gabarito.por_atributo
    ]
    assert [linha[3] for linha in mostrado] == pytest.approx([acima for _, _, _, acima in gabarito.por_atributo])
    assert all(linha[3].number_format == FORMATO_REAIS and linha[4].number_format == FORMATO_PERCENTUAL for linha in linhas[1:])
    assert ws.auto_filter.ref == f"A1:E{len(linhas)}"
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
    assert [[c.value for c in linha] for linha in wb["Por Atributo"].iter_rows()] == [["Batimento", *CABECALHO_POR_ATRIBUTO]]


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
    resultados, _ = conciliar_batimentos(base_a, base_b, TOLERANCIA_PADRAO)
    return gravar_excel(resultados, pasta, limite=limite)


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
        "Batimento", "Chave", "Valor A", "Valor B", "Diferença absoluta", "Tipo do Erro", "Aberta desde",
        "Linha sem Chave", "Produto",
    ]
    linhas = list(ws.iter_rows(min_row=3, values_only=True))
    assert [(chave, diferenca, produto) for _, chave, _, _, diferenca, _, _, _, produto in linhas] == [
        ("2", 50.0, "p2"), ("4", 40.0, "p4"), ("3", 30.0, "p3")
    ]
    assert ws.freeze_panes == "A3"
    assert ws.auto_filter.ref == "A2:I5"
    assert avisos_do_resumo(caminho)[-1] == aviso


def test_no_limite_nao_ha_corte_nem_aviso(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,110.00\n2,2026-09-30,150.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,100.00\n2,2026-09-30,100.00\n", encoding="utf-8")

    caminho = gravar_com_limite(base_a, base_b, tmp_path, limite=2)

    ws = openpyxl.load_workbook(caminho)["Operações com Diferença"]
    assert ws["B1"].value == "Chave"
    assert ws.freeze_panes == "A2"
    assert ws.auto_filter.ref == "A1:H3"
    assert not any(aviso.startswith("Nem todas") for aviso in avisos_do_resumo(caminho))


def test_o_corte_nas_bases_de_exemplo_mostra_as_maiores_do_gabarito_e_avisa_por_ultimo_no_resumo(tmp_path):
    gabarito = gerar_bases_exemplo(tmp_path)
    todas = [("Valor", op) for op in gabarito.operacoes] + [("Juros", op) for op in gabarito.juros.operacoes]
    total = len(todas)
    assert total > 4

    caminho = gravar_com_limite(gabarito.base_a, gabarito.base_b, tmp_path, limite=4)

    # O corte é da aba inteira: as 4 maiores Diferenças absolutas dos dois Batimentos, de volta à ordem por Batimento
    maiores = sorted(range(total), key=lambda i: -abs(todas[i][1][3]))[:4]
    esperadas = [(batimento, op[0]) for batimento, op in (todas[i] for i in sorted(maiores))]
    aviso = f"Nem todas as operações com diferença couberam: mostrando 4 de {total}, as maiores."
    ws = openpyxl.load_workbook(caminho)["Operações com Diferença"]
    assert ws["A1"].value == aviso
    assert ws["B2"].value == "Chave"
    assert [linha[:2] for linha in ws.iter_rows(min_row=3, values_only=True)] == esperadas
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
        ("Nem todos os erros couberam: mostrando 2 de 3.", None, None, None, None, None, None),
        tuple(CABECALHO_DE_ERROS),
        ("Todos", "Base A", 3, "2", None, "1,00", "Data vazia"),
        ("Todos", "Base A", 4, "3", "ontem", "1,00", "Data ilegível"),
    ]
    assert ws.freeze_panes == "A3"
    assert ws.auto_filter.ref == "A2:G4"
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
    # A Data-base plantada só na Base B vem antes das Linhas rejeitadas; as do Valor Juros vêm depois, com o Batimento
    valor = [("Todos" if r[-1].startswith("Data") else "Valor", *r) for r in gabarito.rejeitadas]
    juros = [("Juros", *r) for r in gabarito.juros.rejeitadas if r[-1].startswith("Valor")]
    assert juros or formato == "parquet"
    assert linhas == [tuple(CABECALHO_DE_ERROS), DATA_BASE_SO_NA_B, *valor, *juros]
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
    linhas = {linha[1]: linha for linha in ws.iter_rows(min_row=2, values_only=True)}
    assert linhas["1"][5] == "Casa com linha sem Chave"
    assert linhas["1"][7] == "−10.000,00 em 30/09/2026 na Base A; 10.000,00 em 30/09/2026 na Base B"
    assert linhas["2"][7] is None


def test_chave_plantada_casa_com_a_linha_sem_chave_de_uma_data_base_antiga(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)

    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    ws = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])["Operações com Diferença"]
    linhas = [linha for linha in ws.iter_rows(min_row=2, values_only=True) if linha[7]]
    assert {linha[1]: linha[7] for linha in linhas} == gabarito.linha_sem_chave
    assert len(linhas) == 1
    _, chave, _, _, diferenca, tipo, _, texto, *_ = linhas[0]
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
        ("Nem todos os erros couberam: mostrando 2 de 3.", None, None, None, None, None, None),
        tuple(CABECALHO_DE_ERROS),
        ("Todos", "Base A", None, None, "28/09/2026", None, "Data-base só na Base A"),
        ("Todos", "Base A", 4, "2", None, "1,00", "Data vazia"),
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
        ("Valor", "Base A", 4, "3", "30/09/2026", "100", "Valor ilegível")
    ]
    operacoes = {linha[1]: linha[8] for linha in wb["Operações com Diferença"].iter_rows(min_row=2, values_only=True)}
    assert operacoes == {"1": "SP", "K": "RJ"}


def test_texto_que_comeca_com_igual_sai_no_excel_como_texto_e_nao_como_formula(tmp_path, capsys):
    base_a, base_b = tmp_path / "base_a.csv", tmp_path / "base_b.csv"
    base_a.write_text(
        "Chave;Data;Valor;Filial\n=K;30/09/2026;5,00;=A1+1\n3;30/09/2026;=SOMA(A1:A2);SP\n", encoding="utf-8"
    )
    base_b.write_text("Chave;Data;Valor;Filial\n1;30/09/2026;20,00;SP\n", encoding="utf-8")

    assert main(["conciliar", str(base_a), str(base_b)]) == 0

    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])
    valor_rejeitado = wb["Erros"]["F2"]
    assert (valor_rejeitado.value, valor_rejeitado.data_type) == ("=SOMA(A1:A2)", "s")
    chave, filial = next(
        (linha[1], linha[8]) for linha in wb["Operações com Diferença"].iter_rows(min_row=2) if linha[1].value == "=K"
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


def test_pasta_sem_permissao_nao_manda_fechar_o_excel(tmp_path, capsys, monkeypatch):
    gabarito = gerar_bases_exemplo(tmp_path)

    def sem_permissao(resultados, pasta):
        raise PermissionError(13, "Acesso negado", str(tmp_path / "conciliacao_novo.xlsx"))

    monkeypatch.setattr("conciliacao_enxuta.cli.gravar_excel", sem_permissao)
    codigo = main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    saida = capsys.readouterr()
    assert codigo == 1
    assert saida.err.strip() == f"{tmp_path}: não deu para gravar na pasta de saída; falta permissão."


BASE_B_BOA = "Chave;Data;Valor\n1;30/09/2026;10,00\n"
ERROS_DO_ARQUIVO_INTEIRO = {
    # nome da Base A, conteúdo (None: não existe; "pasta": uma pasta com esse nome; lista: as linhas de um `.xlsx`)
    # e a mensagem esperada
    "não existe": ("base_a.csv", None, "base_a.csv: o arquivo não existe."),
    "não abre": ("base_a.csv", "pasta", "base_a.csv: não deu para abrir o arquivo."),
    "vazio": ("base_a.csv", b"", "base_a.csv: o arquivo está vazio."),
    "xlsx corrompido": ("base_a.xlsx", b"lixo", "base_a.xlsx: o arquivo está corrompido."),
    "parquet corrompido": ("base_a.parquet", b"lixo", "base_a.parquet: o arquivo está corrompido."),
    "campo a mais": (
        "base_a.csv",
        b"Chave;Data;Valor\n1;30/09/2026;10,00;x\n",
        "base_a.csv: uma linha tem mais campos que o cabeçalho.",
    ),
    "UTF-16": (
        "base_a.csv",
        BASE_B_BOA.encode("utf-16"),
        "base_a.csv: não foi possível ler o texto do arquivo. Salve o .csv como UTF-8.",
    ),
    "formato não suportado": (
        "base_a.txt",
        BASE_B_BOA.encode(),
        "base_a.txt: formato não suportado. Use .csv, .xlsx ou .parquet.",
    ),
    "coluna fixa faltando": (
        "base_a.csv",
        b"Chave;Data\n1;30/09/2026\n",
        "base_a.csv: falta a coluna Valor. Colunas encontradas: Chave, Data.",
    ),
    "Data e DATA": (
        "base_a.csv",
        b"Chave;Data;DATA;Valor\n1;30/09/2026;30/09/2026;10,00\n",
        "base_a.csv: coluna repetida: Data.",
    ),
    "Valor;Valor": (
        "base_a.csv",
        b"Chave;Data;Valor;Valor\n1;30/09/2026;10,00;10,00\n",
        "base_a.csv: coluna repetida: Valor.",
    ),
    "Valor e Valor no xlsx": (
        "base_a.xlsx",
        [["Chave", "Data", "Valor", "Valor"], [1, "30/09/2026", 10, 10]],
        "base_a.xlsx: coluna repetida: Valor.",
    ),
}


@pytest.mark.parametrize("caso", ERROS_DO_ARQUIVO_INTEIRO)
def test_erro_do_arquivo_inteiro_da_mensagem_simples_com_o_arquivo_na_cli_e_na_janela(
    tmp_path, capsys, monkeypatch, caso
):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))
    nome, conteudo, esperada = ERROS_DO_ARQUIVO_INTEIRO[caso]
    base_a, base_b = tmp_path / nome, tmp_path / "base_b.csv"
    if conteudo == "pasta":
        base_a.mkdir()
    elif isinstance(conteudo, list):
        wb = openpyxl.Workbook()
        for linha in conteudo:
            wb.active.append(linha)
        wb.save(base_a)
    elif conteudo is not None:
        base_a.write_bytes(conteudo)
    base_b.write_text(BASE_B_BOA, encoding="utf-8")

    codigo = main(["conciliar", str(base_a), str(base_b)])
    saida = capsys.readouterr()
    resposta = conciliar_pela_janela(str(base_a), str(base_b), "1,00")

    assert codigo == 1
    assert saida.out == ""
    assert saida.err.strip() == esperada
    assert resposta.caminho is None
    assert resposta.mensagem == esperada
    assert not list(tmp_path.glob("conciliacao_*"))


def test_pasta_de_saida_que_nao_existe_da_mensagem_simples(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    pasta = tmp_path / "nao_existe"

    codigo = main(["conciliar", str(gabarito.base_a), str(gabarito.base_b), "--saida", str(pasta)])

    saida = capsys.readouterr()
    assert codigo == 1
    assert saida.out == ""
    assert saida.err.strip() == f"{pasta}: a pasta de saída não existe."
    assert not pasta.exists()


def test_erro_inesperado_na_cli_sai_com_mensagem_simples_sem_traceback(tmp_path, capsys, monkeypatch):
    gabarito = gerar_bases_exemplo(tmp_path)

    def falhar(*_):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr("conciliacao_enxuta.cli.conciliar", falhar)

    codigo = main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])

    saida = capsys.readouterr()
    assert codigo == 1
    assert saida.out == ""
    assert saida.err.strip() == "Algo deu errado e a conciliação não foi feita: falha simulada"


BASE_A_COM_DOIS = "Chave,Data,Valor Juros,Valor Receita\n1,2026-09-30,10.00,100.00\n2,2026-09-30,5.00,50.00\n"
BASE_B_COM_DOIS = "Chave,Data,Valor_Receita,valor juros\n1,2026-09-30,200.00,12.00\n2,2026-09-30,50.00,5.00\n"


def test_dois_batimentos_conciliam_cada_um_com_os_seus_totais_na_ordem_da_base_a(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text(BASE_A_COM_DOIS, encoding="utf-8")
    base_b.write_text(BASE_B_COM_DOIS, encoding="utf-8")

    resultados, avisos = conciliar_batimentos(base_a, base_b, TOLERANCIA_PADRAO)

    assert avisos == []
    # Totais conferidos à mão, em centavos: Juros 15,00 × 17,00 e Receita 150,00 × 250,00
    assert [(r.total_a, r.total_b, r.diferenca_total, r.chaves_com_diferenca) for r in resultados] == [
        (1500, 1700, -200, 1),
        (15000, 25000, -10000, 1),
    ]


def conciliar_dois(tmp_path, capsys, conteudo_a: str, conteudo_b: str) -> tuple[int, str, str]:
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text(conteudo_a, encoding="utf-8")
    base_b.write_text(conteudo_b, encoding="utf-8")
    codigo = main(["conciliar", str(base_a), str(base_b)])
    saida = capsys.readouterr()
    return codigo, saida.out, saida.err


def test_coluna_de_valor_so_numa_base_avisa_e_as_outras_sao_conciliadas(tmp_path, capsys):
    codigo, saida, erro = conciliar_dois(
        tmp_path, capsys, BASE_A_COM_DOIS, "Chave,Data,Valor Juros,Valor Taxa\n1,2026-09-30,12.00,1.00\n"
    )

    assert codigo == 0
    assert erro.splitlines() == [
        "Valor Receita só na Base A: não conciliado",
        "Valor Taxa só na Base B: não conciliado",
    ]
    assert ler_resumo(saida.splitlines()[0])["Total A"].value == 15.00  # o Batimento Juros


def test_sem_batimento_nas_duas_bases_a_mensagem_e_simples_e_nada_e_gerado(tmp_path, capsys):
    codigo, saida, erro = conciliar_dois(
        tmp_path, capsys, "Chave,Data,Valor Juros\n1,2026-09-30,1.00\n", "Chave,Data,Valor Receita\n1,2026-09-30,1.00\n"
    )

    assert (codigo, saida) == (1, "")
    assert erro.strip() == "A Base A e a Base B não têm nenhuma coluna de valor em comum."
    assert not list(tmp_path.glob("*.xlsx"))


def test_coluna_de_valor_repetida_continua_dando_coluna_repetida(tmp_path, capsys):
    mensagem = conciliar_com_erro(tmp_path, capsys, "Chave;Data;Valor Juros;valor_juros\n1;30/09/2026;1;2\n")

    assert mensagem == "base_a.csv: coluna repetida: Valor Juros."


def test_janela_mostra_o_aviso_da_coluna_de_valor_so_numa_base_e_concilia(tmp_path):
    (tmp_path / "a.csv").write_text(BASE_A_COM_DOIS, encoding="utf-8")
    (tmp_path / "b.csv").write_text("Chave,Data,Valor Juros\n1,2026-09-30,12.00\n", encoding="utf-8")

    resposta = conciliar_pela_janela(str(tmp_path / "a.csv"), str(tmp_path / "b.csv"), "1,00")

    assert resposta.mensagem == ""
    assert resposta.caminho.exists()
    assert resposta.avisos == ("Valor Receita só na Base A: não conciliado",)


def test_janela_sem_batimento_nas_duas_bases_da_mensagem_simples(tmp_path):
    (tmp_path / "a.csv").write_text("Chave,Data,Valor Juros\n1,2026-09-30,1.00\n", encoding="utf-8")
    (tmp_path / "b.csv").write_text("Chave,Data,Valor Receita\n1,2026-09-30,1.00\n", encoding="utf-8")

    resposta = conciliar_pela_janela(str(tmp_path / "a.csv"), str(tmp_path / "b.csv"), "1,00")

    assert resposta.caminho is None
    assert resposta.mensagem == "A Base A e a Base B não têm nenhuma coluna de valor em comum."


@pytest.mark.parametrize("formato", ["csv", "xlsx", "parquet"])
def test_exemplo_traz_um_segundo_batimento_que_bate_com_o_gabarito_e_difere_do_valor(tmp_path, formato):
    gabarito = gerar_bases_exemplo(tmp_path, formato)

    valor, juros = conciliar_batimentos(gabarito.base_a, gabarito.base_b, TOLERANCIA_PADRAO)[0]
    esperado = gabarito.juros

    assert (juros.total_a, juros.total_b) == (esperado.total_a, esperado.total_b)
    assert (juros.diferenca_total, juros.diferenca_absoluta) == (esperado.diferenca_total, esperado.diferenca_absoluta)
    assert juros.chaves_com_diferenca == len(esperado.operacoes)
    assert [tuple(op) for op in juros.operacoes.select("Chave", "A", "B", "Diferenca", "Tipo").rows()] == list(
        esperado.operacoes
    )
    assert [tuple(r) for r in juros.rejeitadas.rows()] == list(esperado.rejeitadas)
    # O primeiro Batimento segue o do gabarito de sempre, e as Diferenças dos dois não coincidem
    assert valor.total_a == gabarito.total_a
    assert valor.chaves_com_diferenca == gabarito.chaves_com_diferenca
    chaves_de_juros = {chave for chave, *_ in esperado.operacoes}
    assert chaves_de_juros.isdisjoint(chave for chave, *_ in gabarito.operacoes)
    assert {t for *_, t in esperado.operacoes} == {"Sem padrão", "Duplicado", "Sinal invertido"}  # outros Tipos por Chave
    assert esperado.rejeitadas != gabarito.rejeitadas


# Dois Batimentos, Juros e Receita, com as colunas da Base B em outra ordem. Diferenças conferidas à mão, em reais:
# Juros: Chave 1 (110 × 100); Receita: Chave 2 (150 × 100). A Chave 3 cai pela Data e a 4 pelo Valor de Juros.
LAYOUT_A = (
    "Chave,Data,Valor Juros,Valor Receita,Produto\n"
    "1,2026-09-30,110.00,100.00,p1\n2,2026-09-30,5.00,150.00,p2\n3,ontem,1.00,1.00,p3\n4,2026-09-30,abc,7.00,p4\n"
)
LAYOUT_B = (
    "Chave,Data,Valor Receita,Valor Juros\n"
    "1,2026-09-30,100.00,100.00\n2,2026-09-30,100.00,5.00\n1,2026-10-01,100.00,100.00\n4,2026-09-30,7.00,xyz\n"
)
QUATRO_ABAS = ["Por Tipo do Erro", "Por Atributo", "Operações com Diferença", "Erros"]


def gravar_dois(tmp_path, capsys):
    codigo, saida, _ = conciliar_dois(tmp_path, capsys, LAYOUT_A, LAYOUT_B)
    assert codigo == 0
    return openpyxl.load_workbook(saida.splitlines()[0], formulas=True)


def test_um_xlsx_so_com_a_coluna_batimento_com_filtro_nas_quatro_abas_e_as_linhas_por_batimento(tmp_path, capsys):
    wb = gravar_dois(tmp_path, capsys)

    assert len(list(tmp_path.glob("*.xlsx"))) == 1
    for aba in QUATRO_ABAS:
        ws = wb[aba]
        assert ws["A1"].value == "Batimento"
        assert ws.auto_filter.ref is not None
        assert ws.auto_filter.ref.startswith("A1:")
    por_tipo = [linha[:4] for linha in wb["Por Tipo do Erro"].iter_rows(min_row=2, max_row=3, values_only=True)]
    assert por_tipo == [("Juros", "Sem padrão", 1, 10.0), ("Receita", "Sem padrão", 1, 50.0)]
    por_atributo = [linha[:3] for linha in wb["Por Atributo"].iter_rows(min_row=2, values_only=True)]
    assert por_atributo == [("Juros", "Produto", "p1"), ("Receita", "Produto", "p2")]
    operacoes = [linha[:5] for linha in wb["Operações com Diferença"].iter_rows(min_row=2, values_only=True)]
    assert operacoes == [("Juros", "1", 110.0, 100.0, 10.0), ("Receita", "2", 150.0, 100.0, 50.0)]


def test_o_limite_vale_para_a_aba_inteira_e_deixa_as_maiores_diferencas_de_todos_os_batimentos(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    # Diferenças em reais: Juros 10, 20, 30 nas Chaves 1 a 3; Receita 25, 5, 40 nas mesmas Chaves
    base_a.write_text(
        "Chave,Data,Valor Juros,Valor Receita\n1,2026-09-30,110.00,125.00\n2,2026-09-30,120.00,105.00\n"
        "3,2026-09-30,130.00,140.00\n",
        encoding="utf-8",
    )
    base_b.write_text(
        "Chave,Data,Valor Juros,Valor Receita\n1,2026-09-30,100.00,100.00\n2,2026-09-30,100.00,100.00\n"
        "3,2026-09-30,100.00,100.00\n",
        encoding="utf-8",
    )

    caminho = gravar_com_limite(base_a, base_b, tmp_path, limite=3)

    ws = openpyxl.load_workbook(caminho)["Operações com Diferença"]
    assert ws["A1"].value == "Nem todas as operações com diferença couberam: mostrando 3 de 6, as maiores."
    linhas = [(b, chave, diferenca) for b, chave, _, _, diferenca, *_ in ws.iter_rows(min_row=3, values_only=True)]
    assert linhas == [("Juros", "3", 30.0), ("Receita", "3", 40.0), ("Receita", "1", 25.0)]
    assert ws.auto_filter.ref.startswith("A2:")


def test_aba_erros_com_varios_batimentos_tem_todos_para_a_data_e_a_data_base_e_o_batimento_para_o_valor(
    tmp_path, capsys
):
    wb = gravar_dois(tmp_path, capsys)

    erros = list(wb["Erros"].iter_rows(min_row=2, values_only=True))
    assert erros == [
        ("Todos", "Base B", None, None, "01/10/2026", None, "Data-base só na Base B"),
        ("Todos", "Base A", 4, "3", "ontem", "1,00", "Data ilegível"),
        ("Juros", "Base A", 5, "4", "2026-09-30", "abc", "Valor ilegível"),
        ("Juros", "Base B", 5, "4", "2026-09-30", "xyz", "Valor ilegível"),
    ]


def test_com_um_batimento_so_as_abas_trazem_o_nome_dele_na_coluna_batimento(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n2,ontem,1.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,90.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0])
    assert [c.value for c in wb["Operações com Diferença"][2]][:2] == ["Valor", "1"]
    assert [c.value for c in wb["Por Tipo do Erro"][2]][:2] == ["Valor", "Sem padrão"]
    assert [c.value for c in wb["Erros"][2]][:2] == ["Todos", "Base A"]


def bloco_do_grafico(wb, batimento: str) -> dict[str, list]:
    """As linhas da `_grafico` do Batimento, por título de coluna, achadas pelo cabeçalho da linha 1."""
    ws = wb["_grafico"]
    colunas = {c.value: c.column for c in ws[1] if c.value}
    linhas = [r for r in ws.iter_rows(min_row=2) if r[colunas["Batimento"] - 1].value == batimento]
    return {titulo: [linha[coluna - 1].value for linha in linhas] for titulo, coluna in colunas.items()}


def test_resumo_com_varios_batimentos_tem_no_topo_a_lista_suspensa_na_ordem_da_base_a_abrindo_no_primeiro(
    tmp_path, capsys
):
    wb = gravar_dois(tmp_path, capsys)

    resumo = wb["Resumo"]
    assert resumo["A1"].value == "Batimento"
    assert resumo["B1"].value == "Juros"
    [validacao] = resumo.data_validations.dataValidation
    assert validacao.type == "list" and str(validacao.sqref) == "B1"
    intervalo = validacao.formula1.removeprefix("'_grafico'!").replace("$", "")
    assert [c[0].value for c in wb["_grafico"][intervalo]] == ["Juros", "Receita"]


def test_resumo_com_varios_batimentos_busca_tudo_na_grafico_por_formula_e_os_graficos_leem_o_trecho_escolhido(
    tmp_path, capsys
):
    wb = gravar_dois(tmp_path, capsys)

    resumo, dados = wb["Resumo"], wb["_grafico"]
    quadro = [resumo.cell(linha, 2).value for linha in range(3, 10)]
    assert all(isinstance(v, str) and v.startswith("=") and "_grafico" in v for v in quadro)
    # Os dois gráficos seguem lendo A:B e D:E da `_grafico`, que agora são fórmulas
    assert len(resumo._charts) == 2
    assert dados["B2"].value.startswith("=") and dados["E2"].value.startswith("=")
    assert dados["D2"].value.startswith("=") and dados["A2"].value.startswith("=")
    # Os números de cada Batimento ficam em blocos fixos, um depois do outro
    assert bloco_do_grafico(wb, "Juros")["Quadro"][:7] != bloco_do_grafico(wb, "Receita")["Quadro"][:7]


def test_grafico_traz_o_quadro_a_idade_e_o_historico_de_cada_batimento_como_o_resultado_dele(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path, "csv")
    main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)])
    wb = openpyxl.load_workbook(capsys.readouterr().out.splitlines()[0], formulas=True)

    resultados, _ = conciliar_batimentos(gabarito.base_a, gabarito.base_b, TOLERANCIA_PADRAO)
    assert [r.batimento for r in resultados] == ["Valor", "Juros"]
    for r in resultados:
        bloco = bloco_do_grafico(wb, r.batimento)
        assert bloco["Quadro"][0].date() == r.data_base
        assert bloco["Quadro"][1:7] == [
            r.tolerancia / 100, r.total_a / 100, r.total_b / 100, r.diferenca_total / 100,
            r.diferenca_absoluta / 100, r.chaves_com_diferenca,
        ]
        assert list(zip(bloco["Idade: faixa"], bloco["Idade: Diferença absoluta"]))[:5] == [
            (rotulo_da_faixa(faixa, chaves, linhas), absoluta / 100) for faixa, chaves, linhas, absoluta in r.por_idade
        ]
        historico = list(zip(bloco["Histórico: Data-base"], bloco["Histórico: Diferença absoluta"]))
        assert [(d.date(), v) for d, v in historico[: len(r.historico)]] == [(d, v / 100) for d, v in r.historico]
        problematicos = bloco["Atributo: Atributo"][: r.atributos_problematicos.height]
        assert problematicos == r.atributos_problematicos["Atributo"].to_list()
    # Os Diferença do exemplo mudam de um Batimento para outro
    assert resultados[0].diferenca_absoluta != resultados[1].diferenca_absoluta


def test_escolhendo_cada_batimento_o_resumo_mostra_o_quadro_e_os_graficos_dele(tmp_path, capsys, escolher):
    # Juros: Diferença absoluta 10,00 na Chave 1; Receita: 50,00 na Chave 2 (ver LAYOUT_A e LAYOUT_B)
    for posicao, nome, absoluta, chave in ((1, "Juros", 10.0, "1"), (2, "Receita", 50.0, "2")):
        wb = gravar_dois(tmp_path, capsys)
        escolher(wb, posicao)
        resumo, dados = wb["Resumo"], wb["_grafico"]
        assert resumo["B1"].value == nome
        quadro = {linha[0].value: linha[1].value for linha in resumo.iter_rows(min_row=3, max_row=9, max_col=2)}
        assert quadro["Diferença absoluta"] == absoluta and quadro["Chaves com Diferença"] == 1
        assert dados["B2"].value == absoluta  # a série da linha: a Data-base única
        assert sum(v for v in (c[0].value for c in dados["E2:E6"])) == absoluta  # as barras somam a Diferença absoluta


def test_data_base_e_a_mesma_para_todos_os_batimentos_mesmo_se_as_linhas_da_data_caem_pelo_valor(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    # Em 30/09 todas as linhas do Juros caem pelo Valor vazio; 01/10 só está na Base A e 02/10 só na B
    base_a.write_text(
        "Chave,Data,Valor Juros,Valor Receita\n1,2026-09-29,10.00,100.00\n1,2026-09-30,,100.00\n1,2026-10-01,1.00,1.00\n",
        encoding="utf-8",
    )
    base_b.write_text(
        "Chave,Data,Valor Juros,Valor Receita\n1,2026-09-29,10.00,100.00\n1,2026-09-30,,100.00\n1,2026-10-02,1.00,1.00\n",
        encoding="utf-8",
    )

    juros, receita = conciliar_batimentos(base_a, base_b, TOLERANCIA_PADRAO)[0]

    assert juros.data_base == receita.data_base == date(2026, 9, 30)
    assert juros.historico == ((date(2026, 9, 29), 0), (date(2026, 9, 30), 0))
    assert (juros.data_bases_so_em_a, juros.data_bases_so_em_b) == (
        (date(2026, 10, 1),),
        (date(2026, 10, 2),),
    )
    assert juros.data_bases_so_em_a == receita.data_bases_so_em_a
    assert (juros.total_a, juros.total_b, juros.chaves_com_diferenca) == (0, 0, 0)
