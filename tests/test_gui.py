"""GUI: `gui_estado` testado direto, sem Tkinter; a janela só pelo autoteste, em subprocesso."""

import os
import subprocess
import sys
from pathlib import Path

import openpyxl
import pytest

from conciliacao_enxuta.exemplo import gerar_bases_exemplo
from conciliacao_enxuta.gui_estado import TOLERANCIA_PADRAO_EM_TEXTO, conciliar_pela_janela

RAIZ = Path(__file__).resolve().parent.parent


def test_sem_base_a_da_mensagem_simples():
    resposta = conciliar_pela_janela("", "b.csv", "1,00")

    assert resposta.caminho is None
    assert resposta.mensagem == "Escolha o arquivo da Base A."


def test_sem_base_b_da_mensagem_simples():
    resposta = conciliar_pela_janela("a.csv", "  ", "1,00")

    assert resposta.caminho is None
    assert resposta.mensagem == "Escolha o arquivo da Base B."


@pytest.mark.parametrize("tolerancia", ["abc", "", "-1,00"])
def test_tolerancia_invalida_da_mensagem_simples(tolerancia):
    resposta = conciliar_pela_janela("a.csv", "b.csv", tolerancia)

    assert resposta.caminho is None
    assert resposta.mensagem.startswith("Tolerância inválida")
    assert "1,00" in resposta.mensagem


@pytest.mark.parametrize(("tolerancia", "em_reais"), [("1,00", 1.00), ("0,5", 0.50), ("2", 2.00)])
def test_com_tudo_certo_devolve_o_xlsx_na_pasta_da_base_a(tmp_path, tolerancia, em_reais):
    gabarito = gerar_bases_exemplo(tmp_path)

    resposta = conciliar_pela_janela(str(gabarito.base_a), str(gabarito.base_b), tolerancia)

    assert resposta.mensagem == ""
    assert resposta.caminho == tmp_path / f"conciliacao_{gabarito.data_base.isoformat()}.xlsx"
    assert resposta.caminho.exists()
    resumo = openpyxl.load_workbook(resposta.caminho)["Resumo"]
    quadro = {rotulo: valor for rotulo, valor in resumo.iter_rows(max_col=2, values_only=True) if rotulo}
    assert quadro["Tolerância"] == em_reais


def test_tolerancia_padrao_da_janela_e_1_00():
    assert TOLERANCIA_PADRAO_EM_TEXTO == "1,00"


def test_gui_estado_nao_importa_tkinter():
    codigo = "import sys, conciliacao_enxuta.gui_estado; print('tkinter' in sys.modules)"

    saida = subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, capture_output=True, text=True, check=True)

    assert saida.stdout.strip() == "False"


def test_autoteste_monta_a_janela_escondida_fecha_e_sai_com_0():
    ambiente = {**os.environ, "CONCILIACAO_AUTOTESTE": "1"}

    saida = subprocess.run(
        [sys.executable, "-m", "conciliacao_enxuta"], cwd=RAIZ, env=ambiente, capture_output=True, text=True, timeout=60
    )

    assert saida.returncode == 0, saida.stderr
