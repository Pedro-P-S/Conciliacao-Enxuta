"""Seam 2: arquivos → CLI → `.xlsx`, lido com openpyxl e conferido contra o gabarito."""

from datetime import datetime

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
    assert openpyxl.load_workbook(esperado).sheetnames == ["Resumo"]

    resumo = ler_resumo(esperado)
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
