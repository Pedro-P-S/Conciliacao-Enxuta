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
    """Junta os textos visíveis (sem os do `<style>`), as tags e os atributos de cada tag.

    As dicas (`<title>` dentro do SVG) e a tabela dos dados dos gráficos (dentro de `<details>`) vão em listas
    à parte, para não misturar com os textos da página.
    """

    def __init__(self):
        super().__init__()
        self.textos: list[str] = []
        self.dicas: list[str] = []
        self.dados: list[str] = []
        self.tags: list[tuple[str, dict]] = []
        self._aberto: list[str] = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        self._aberto.append(tag)

    def handle_endtag(self, tag):
        while self._aberto and self._aberto.pop() != tag:
            pass

    def handle_data(self, data):
        if not data.strip() or "style" in self._aberto:
            return
        if "details" in self._aberto:
            self.dados.append(data.strip())
        elif "svg" in self._aberto and self._aberto[-1] == "title":
            self.dicas.append(data.strip())
        else:
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

    textos = ler_html(gravar_html([resultado], tmp_path, limite=2)).textos

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
    assert [tag for tag, _ in leitor.tags].count("svg") == 4  # 2 por Batimento
    # A linha tem um ponto por Data-base comum
    pontos = next(attrs["points"] for tag, attrs in leitor.tags if tag == "polyline")
    assert len(pontos.split()) == len(gabarito.historico)


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


UM_BATIMENTO = ("Chave,Data,Valor\n1,2026-09-30,10.00\n", "Chave,Data,Valor\n1,2026-09-30,15.00\n")


def test_com_um_batimento_o_html_nao_tem_lista_nem_script_nem_aponta_para_fora(tmp_path, capsys):
    _, html = conciliar_csv(tmp_path, capsys, *UM_BATIMENTO)

    leitor = ler_html(html)
    assert not {"script", "select", "section"} & {tag for tag, _ in leitor.tags}
    assert "url(" not in Path(html).read_text(encoding="utf-8")


def test_com_varios_batimentos_o_html_traz_a_lista_e_o_resumo_de_cada_um_com_so_o_primeiro_visivel(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    leitor = ler_html(linhas[1])
    assert leitor.textos[1:4] == ["Resumo", "Valor", "Juros"]  # a lista, na ordem da Base A, antes dos Resumos
    secoes = [attrs for tag, attrs in leitor.tags if tag == "section"]
    assert ["hidden" in attrs for attrs in secoes] == [False, True]
    # O Resumo de cada Batimento, na ordem das seções: totais e Atributos Problemáticos do gabarito
    totais = [t for t in leitor.textos if t in ("Total A", "Total B")]
    assert totais == ["Total A", "Total B"] * 2
    indices = [i for i, t in enumerate(leitor.textos) if t == "Total A"]
    esperado = [(gabarito.total_a, gabarito.total_b), (gabarito.juros.total_a, gabarito.juros.total_b)]
    for i, (total_a, total_b) in zip(indices, esperado):
        assert leitor.textos[i + 1] == reais(total_a)
        assert leitor.textos[leitor.textos.index("Total B", i) + 1] == reais(total_b)
    assert [t for t in leitor.textos if t == "Atributos Problemáticos"] == ["Atributos Problemáticos"] * 2
    assert reais(gabarito.juros.diferenca_absoluta) in leitor.textos


def test_com_varios_batimentos_o_unico_script_e_o_filtro_e_nada_aponta_para_fora(tmp_path, capsys):
    _, linhas = conciliar_exemplo(tmp_path, capsys)

    leitor = ler_html(linhas[1])
    assert [tag for tag, _ in leitor.tags].count("script") == 1
    referencias = [v for _, attrs in leitor.tags for k, v in attrs.items() if k in ("src", "href", "xlink:href")]
    assert all(v.startswith("#") for v in referencias)
    texto = Path(linhas[1]).read_text(encoding="utf-8")
    assert "url(" not in texto and "http" not in texto


def test_nome_de_batimento_com_menor_comercial_e_aspas_sai_como_texto(tmp_path, capsys):
    _, html = conciliar_csv(
        tmp_path, capsys,
        'Chave,Data,Valor,"Valor <b> & ""x"""\n1,2026-09-30,10.00,1.00\n',
        'Chave,Data,Valor,"Valor <b> & ""x"""\n1,2026-09-30,15.00,2.00\n',
    )

    leitor = ler_html(html)
    assert any(t.startswith("<b> & ") for t in leitor.textos)
    assert "b" not in [tag for tag, _ in leitor.tags]
    assert "&lt;b&gt; &amp; &quot;" in Path(html).read_text(encoding="utf-8")


def test_html_tem_um_tema_so_com_as_cores_em_tokens_e_os_temas_claro_e_escuro_declarados(tmp_path, capsys):
    _, html = conciliar_csv(tmp_path, capsys, *UM_BATIMENTO)

    texto = Path(html).read_text(encoding="utf-8")
    estilo = texto[texto.index("<style>") : texto.index("</style>")]
    assert texto.count("<style>") == 1
    assert "--serie-1:#2a78d6" in estilo.replace(" ", "")
    escuro = estilo[estilo.index("prefers-color-scheme: dark") :]
    assert ':root:not([data-theme="light"])' in escuro and ':root[data-theme="dark"]' in escuro
    assert escuro.replace(" ", "").count("--serie-1:#3987e5") == 2
    assert "background:var(--superficie)" in estilo.replace(" ", "")
    # Fora do `<style>` nenhuma cor escrita: tudo vem dos tokens
    assert "#" not in texto[texto.index("</style>") :].replace('href="#', "").replace('"#', "").replace("&#", "")


def test_html_traz_a_tabela_dos_dados_dos_graficos_e_a_dica_de_cada_barra_e_de_cada_ponto(tmp_path, capsys):
    _, html = conciliar_csv(
        tmp_path, capsys,
        "Chave,Data,Valor\n1,2026-09-29,10.00\n1,2026-09-30,10.00\n",
        "Chave,Data,Valor\n1,2026-09-29,12.50\n1,2026-09-30,15.00\n",
    )

    leitor = ler_html(html)
    assert leitor.dados.count("Diferença absoluta") == 2  # um cabeçalho por tabela
    assert depois(leitor.dados, "Data-base", 5)[1:] == ["29/09/2026", "2,50", "30/09/2026", "5,00"]
    assert ["29/09/2026: 2,50", "30/09/2026: 5,00"] == [d for d in leitor.dicas if d[:2] in ("29", "30")]
    assert len(leitor.dicas) == 5 + 2  # 5 faixas e 2 Data-bases


def test_as_marcas_seguem_as_regras_barra_arredondada_so_na_ponta_linha_de_2px_ponto_com_anel_e_sem_borda(
    tmp_path, capsys
):
    _, html = conciliar_csv(
        tmp_path, capsys,
        "Chave,Data,Valor\n1,2026-09-29,10.00\n1,2026-09-30,10.00\n",
        "Chave,Data,Valor\n1,2026-09-29,12.50\n1,2026-09-30,15.00\n",
    )

    leitor = ler_html(html)
    marcas = {classe: [a for t, a in leitor.tags if a.get("class") == classe] for classe in ("barra", "linha", "ponto")}
    assert len(marcas["barra"]) == 1  # só a faixa com Diferença tem barra visível
    assert marcas["linha"][0]["stroke-width"] == "2" and marcas["linha"][0]["stroke-linejoin"] == "round"
    assert len(marcas["ponto"]) == 2 and all(float(a["r"]) >= 4 for a in marcas["ponto"])
    # A barra é um caminho com 4px arredondados na ponta, e 24px de espessura no máximo
    assert " a4,4 " in marcas["barra"][0]["d"] and 0 < float(marcas["barra"][0]["data-h"]) <= 24
    assert all("stroke" not in a for a in marcas["barra"])


def test_o_svg_escala_com_a_largura_da_tela_e_cabe_em_375px(tmp_path, capsys):
    _, html = conciliar_csv(tmp_path, capsys, *UM_BATIMENTO)

    svgs = [a for tag, a in ler_html(html).tags if tag == "svg"]
    assert len(svgs) == 2
    for a in svgs:
        largura = float(a["viewbox"].split()[2])
        assert a["width"] == "100%" and largura <= 375 - 2 * 16
