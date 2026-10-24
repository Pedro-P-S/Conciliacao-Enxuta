"""Seam 2: arquivos → CLI → `.html` com o Resumo, lido com o `html.parser` da biblioteca padrão."""

from html.parser import HTMLParser
from pathlib import Path

import openpyxl

from conciliacao_enxuta.cli import main
from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, conciliar
from conciliacao_enxuta.exemplo import gerar_bases_exemplo
from conciliacao_enxuta.html import gravar_html
from conciliacao_enxuta.leitura import ler_base


class _Leitor(HTMLParser):
    """Junta os textos visíveis (sem os do `<style>`), as tags e os atributos de cada tag."""

    def __init__(self):
        super().__init__()
        self.textos: list[str] = []
        self.tags: list[tuple[str, dict]] = []
        self._no_style = False

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        self._no_style = tag == "style"

    def handle_endtag(self, tag):
        if tag == "style":
            self._no_style = False

    def handle_data(self, data):
        if data.strip() and not self._no_style:
            self.textos.append(data.strip())


def ler_html(caminho) -> _Leitor:
    leitor = _Leitor()
    leitor.feed(Path(caminho).read_text(encoding="utf-8"))
    return leitor


def reais(centavos: int) -> str:
    """Centavos → `1.234,56`, ou `-1.234,56`, como o Excel em português mostra `#.##0,00`."""
    texto = f"{abs(centavos) / 100:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"-{texto}" if centavos < 0 else texto


def conciliar_exemplo(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    assert main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)]) == 0
    return gabarito, capsys.readouterr().out.splitlines()


def test_cli_grava_o_html_ao_lado_do_xlsx_e_imprime_os_dois_caminhos(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    nome = f"conciliacao_{gabarito.data_base.isoformat()}"
    assert linhas == [str(tmp_path / f"{nome}.xlsx"), str(tmp_path / f"{nome}.html")]
    assert (tmp_path / f"{nome}.html").exists()


def test_html_traz_o_quadro_do_resumo_com_os_totais_do_gabarito_em_reais(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    textos = ler_html(linhas[1]).textos
    quadro = {
        "Data-base mais recente": f"{gabarito.data_base:%d/%m/%Y}",
        "Tolerância": "1,00",
        "Total A": reais(gabarito.total_a),
        "Total B": reais(gabarito.total_b),
        "Diferença total": reais(gabarito.diferenca_total),
        "Diferença absoluta": reais(gabarito.diferenca_absoluta),
        "Chaves com Diferença": f"{gabarito.chaves_com_diferenca:,}".replace(",", "."),
    }
    for rotulo, valor in quadro.items():
        assert textos[textos.index(rotulo) + 1] == valor


def depois(textos: list[str], rotulo: str, quantos: int) -> list[str]:
    """Os `quantos` textos que vêm logo depois de `rotulo`."""
    inicio = textos.index(rotulo) + 1
    return textos[inicio : inicio + quantos]


def test_html_traz_os_avisos_de_linhas_sem_chave_e_de_linhas_rejeitadas_depois_do_quadro(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    textos = ler_html(linhas[1]).textos
    titulo = "Linhas sem Chave, fora do cruzamento"
    assert depois(textos, titulo, 8) == [
        "Linhas", "Soma",
        "Base A", str(gabarito.sem_chave_a.linhas), reais(gabarito.sem_chave_a.soma),
        "Base B", str(gabarito.sem_chave_b.linhas), reais(gabarito.sem_chave_b.soma),
    ]
    rejeitadas = f"Linhas rejeitadas: {len(gabarito.rejeitadas)} (veja a aba Erros)"
    assert textos.index("Chaves com Diferença") < textos.index(titulo) < textos.index(rejeitadas)


def test_sem_avisos_o_html_nao_tem_aviso(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor\n1,2026-09-30,10.00\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor\n1,2026-09-30,15.00\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    textos = ler_html(capsys.readouterr().out.splitlines()[1]).textos
    assert "Linhas sem Chave, fora do cruzamento" not in textos
    assert not any(t.startswith("Linhas rejeitadas") for t in textos)


def test_acima_do_limite_o_html_traz_o_aviso_de_corte_das_operacoes(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave;Data;Valor\n1;30/09/2026;10,00\n2;30/09/2026;20,00\n3;30/09/2026;30,00\n", encoding="utf-8")
    base_b.write_text("Chave;Data;Valor\n1;30/09/2026;0\n", encoding="utf-8")
    (lida_a, rejeitadas_a), (lida_b, rejeitadas_b) = ler_base(base_a), ler_base(base_b)
    resultado = conciliar(lida_a, lida_b, TOLERANCIA_PADRAO, rejeitadas_a, rejeitadas_b)

    textos = ler_html(gravar_html(resultado, tmp_path, limite=2)).textos

    assert "Nem todas as operações com diferença couberam: mostrando 2 de 3, as maiores." in textos


def test_html_traz_os_atributos_problematicos_do_gabarito_depois_dos_avisos(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    textos = ler_html(linhas[1]).textos
    titulo = "Atributos Problemáticos"
    esperado = ["Atributo", "Valor", "Diferença absoluta", "Diferença acima do peso"]
    for atributo, valor, absoluta, acima in gabarito.por_atributo[:5]:
        esperado += [atributo, valor, reais(absoluta), f"{acima * 100:.2f}%".replace(".", ",")]
    assert depois(textos, titulo, len(esperado)) == esperado
    assert textos[textos.index(titulo) + 5 : textos.index(titulo) + 7] == ["Carteira", "Legado"]
    rejeitadas = next(t for t in textos if t.startswith("Linhas rejeitadas"))
    assert textos.index(titulo) > textos.index(rejeitadas)


def test_sem_atributo_acima_do_peso_o_html_nao_tem_atributos_problematicos(tmp_path, capsys):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave,Data,Valor,Moeda\n1,2026-09-30,10.00,BRL\n", encoding="utf-8")
    base_b.write_text("Chave,Data,Valor,Moeda\n1,2026-09-30,15.00,BRL\n", encoding="utf-8")

    main(["conciliar", str(base_a), str(base_b)])

    assert "Atributos Problemáticos" not in ler_html(capsys.readouterr().out.splitlines()[1]).textos


def test_html_traz_os_dois_graficos_em_svg_com_os_rotulos_da_idade_iguais_aos_do_excel(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)
    rotulos_do_excel = [
        linha[0] for linha in openpyxl.load_workbook(linhas[0])["_grafico"].iter_rows(min_col=4, max_col=4, min_row=2, values_only=True)
        if linha[0]
    ]
    assert len(rotulos_do_excel) == 5

    leitor = ler_html(linhas[1])
    textos = leitor.textos
    barras, no_tempo = "Diferença absoluta por Idade da Diferença", "Diferença absoluta por Data-base"
    assert textos.index("Atributos Problemáticos") < textos.index(barras) < textos.index(no_tempo)
    inicio = textos.index(barras)
    assert [t for t in textos[inicio : textos.index(no_tempo)] if t in rotulos_do_excel] == rotulos_do_excel
    assert [tag for tag, _ in leitor.tags].count("svg") == 2
    # A linha tem um ponto por Data-base comum
    pontos = next(attrs["points"] for tag, attrs in leitor.tags if tag == "polyline")
    assert len(pontos.split()) == len(gabarito.historico)


def test_html_nao_tem_script_nem_aponta_para_nada_fora_do_arquivo(tmp_path, capsys):
    _, linhas = conciliar_exemplo(tmp_path, capsys)

    leitor = ler_html(linhas[1])
    assert "script" not in [tag for tag, _ in leitor.tags]
    referencias = [v for _, attrs in leitor.tags for k, v in attrs.items() if k in ("src", "href", "xlink:href")]
    assert all(v.startswith("#") for v in referencias)
    assert "url(" not in Path(linhas[1]).read_text(encoding="utf-8")


def conciliar_csv(tmp_path, capsys, linhas_a: str, linhas_b: str):
    """Grava as duas bases em `.csv`, concilia pela CLI e devolve os caminhos do `.xlsx` e do `.html`."""
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text(linhas_a, encoding="utf-8")
    base_b.write_text(linhas_b, encoding="utf-8")
    assert main(["conciliar", str(base_a), str(base_b)]) == 0
    return capsys.readouterr().out.splitlines()


def test_o_percentual_do_html_arredonda_como_o_excel(tmp_path, capsys):
    # Moeda X: 100% da Diferença absoluta e 3/32 do peso, 90,625% acima do peso; o Excel mostra 90,63%
    xlsx, html = conciliar_csv(
        tmp_path, capsys,
        "Chave,Data,Valor,Moeda\n1,2026-09-30,0.03,X\n2,2026-09-30,0.29,Y\n",
        "Chave,Data,Valor,Moeda\n1,2026-09-30,10.03,X\n2,2026-09-30,0.29,Y\n",
    )

    celula = next(
        linha[3] for linha in openpyxl.load_workbook(xlsx)["Resumo"].iter_rows() if linha[1].value == "X"
    )
    assert (celula.value, celula.number_format) == (0.90625, "0.00%")
    assert depois(ler_html(html).textos, "X", 2) == ["10,00", "90,63%"]


def textos_do_grafico_de_linha(textos: list[str]) -> list[str]:
    """Os textos do gráfico da Diferença absoluta por Data-base, o último do `.html`, sem o título."""
    return textos[textos.index("Diferença absoluta por Data-base") + 1 :]


def test_sem_diferenca_o_eixo_do_grafico_mostra_0(tmp_path, capsys):
    linhas = "Chave,Data,Valor\n1,2026-09-29,10.00\n1,2026-09-30,10.00\n"
    _, html = conciliar_csv(tmp_path, capsys, linhas, linhas)

    assert textos_do_grafico_de_linha(ler_html(html).textos) == ["0,00", "29/09/2026", "30/09/2026"]


def test_com_uma_data_base_so_o_grafico_de_linha_traz_o_ponto_e_a_data_uma_vez(tmp_path, capsys):
    _, html = conciliar_csv(
        tmp_path, capsys, "Chave,Data,Valor\n1,2026-09-30,10.00\n", "Chave,Data,Valor\n1,2026-09-30,15.00\n"
    )

    leitor = ler_html(html)
    assert textos_do_grafico_de_linha(leitor.textos) == ["5,00", "0,00", "30/09/2026"]
    assert "circle" in [tag for tag, _ in leitor.tags]


def test_atributo_com_caractere_de_controle_sai_sem_ele_e_com_menor_e_comercial_e_aspas_sai_como_texto(
    tmp_path, capsys
):
    xlsx, html = conciliar_csv(
        tmp_path, capsys,
        'Chave,Data,Valor,Moeda\n1,2026-09-30,10.00,Le\x01gado\n2,2026-09-30,10.00,"<b> & ""x"""\n'
        "3,2026-09-30,100.00,BRL\n",
        "Chave,Data,Valor,Moeda\n1,2026-09-30,0,Z\n2,2026-09-30,0,Z\n3,2026-09-30,100.00,BRL\n",
    )

    no_excel = {linha[1].value for linha in openpyxl.load_workbook(xlsx)["Resumo"].iter_rows() if linha[0].value == "Moeda"}
    assert no_excel == {"Legado", '<b> & "x"'}
    textos = ler_html(html).textos
    assert {"Legado", '<b> & "x"'} <= set(textos)
    assert "b" not in [tag for tag, _ in ler_html(html).tags]
