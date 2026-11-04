"""Seam 2: arquivos → CLI → `.html` com o Resumo, lido com o `html.parser` da biblioteca padrão."""

import json
from dataclasses import replace
from decimal import ROUND_HALF_UP, Decimal
from html.parser import HTMLParser
from pathlib import Path

import openpyxl
import pytest

from conciliacao_enxuta.cli import main
from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, conciliar
from conciliacao_enxuta.exemplo import gerar_bases_exemplo
from conciliacao_enxuta.html import gravar_html
from conftest import ler_base


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


def curto(centavos: int) -> str:
    """Centavos → `R$ 688,3 mi`, como o `.html` mostra: centavos abaixo de R$ 1.000, senão uma casa e mil, mi ou bi."""
    valor = Decimal(abs(centavos)) / 100
    if valor < 1000:
        texto = f"{valor:,.2f}"
    else:
        for expoente, nome in ((3, "mil"), (6, "mi"), (9, "bi")):
            arredondado = (valor / Decimal(10) ** expoente).quantize(Decimal("0.1"), ROUND_HALF_UP)
            if arredondado < 1000 or nome == "bi":
                texto = f"{arredondado:,.1f} {nome}"
                break
    texto = texto.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{'-' if centavos < 0 else ''}R$ {texto}"


def parte(numerador, denominador) -> str:
    """A fração em %, com 2 casas e o meio para cima, como o Excel mostra `0.00%`."""
    fracao = (Decimal(numerador) * 100 / Decimal(denominador)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return f"{fracao}%".replace(".", ",")


def conciliar_exemplo(tmp_path, capsys):
    gabarito = gerar_bases_exemplo(tmp_path)
    assert main(["conciliar", str(gabarito.base_a), str(gabarito.base_b)]) == 0
    return gabarito, capsys.readouterr().out.splitlines()


def test_cli_grava_o_html_ao_lado_do_xlsx_e_imprime_os_dois_caminhos(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    nome = f"conciliacao_{gabarito.data_base.isoformat()}"
    assert linhas == [str(tmp_path / f"{nome}.xlsx"), str(tmp_path / f"{nome}.html")]
    assert (tmp_path / f"{nome}.html").exists()


def test_html_traz_o_quadro_do_resumo_com_os_totais_do_gabarito_em_reais_abreviados(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    textos = ler_html(linhas[1]).textos
    quadro = {
        "Data-base mais recente": f"{gabarito.data_base:%d/%m/%Y}",
        "Total A": curto(gabarito.total_a),
        "Total B": curto(gabarito.total_b),
        "Diferença total": curto(gabarito.diferenca_total),
        "Diferença absoluta": curto(gabarito.diferenca_absoluta),
        "Chaves com Diferença": f"{gabarito.chaves_com_diferenca:,}".replace(",", "."),
    }
    for rotulo, valor in quadro.items():
        assert textos[textos.index(rotulo) + 1] == valor
    assert "Tolerância" not in textos  # fica só no Excel


def depois(textos: list[str], rotulo: str, quantos: int) -> list[str]:
    """Os `quantos` textos que vêm logo depois de `rotulo`."""
    inicio = textos.index(rotulo) + 1
    return textos[inicio : inicio + quantos]


def test_html_nao_traz_as_linhas_rejeitadas_nem_as_linhas_sem_chave(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    textos = ler_html(linhas[1]).textos
    assert gabarito.rejeitadas and not any(t.startswith("Linhas rejeitadas") for t in textos)  # só no Excel
    assert gabarito.sem_chave_a.linhas and "Linhas sem Chave, fora do cruzamento" not in textos


def test_ao_lado_das_chaves_com_diferenca_vem_a_porcentagem_das_chaves(tmp_path, capsys):
    # Chaves 1, 2 e 3; só a 1 tem Diferença: 1 de 3 é 33,33%
    _, html = conciliar_csv(
        tmp_path, capsys,
        "Chave,Data,Valor\n1,2026-09-30,10.00\n2,2026-09-30,10.00\n3,2026-09-30,10.00\n",
        "Chave,Data,Valor\n1,2026-09-30,15.00\n2,2026-09-30,10.00\n3,2026-09-30,10.00\n",
    )

    assert depois(ler_html(html).textos, "Chaves com Diferença", 3) == ["1", "33,33%", "das 3 Chaves"]


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


def test_com_varios_batimentos_o_aviso_de_corte_do_html_usa_o_total_de_todos_como_o_excel(tmp_path):
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text("Chave;Data;Valor|1;30/09/2026;10,00|2;30/09/2026;20,00|".replace("|", chr(10)), encoding="utf-8")
    base_b.write_text("Chave;Data;Valor|1;30/09/2026;0|2;30/09/2026;0|".replace("|", chr(10)), encoding="utf-8")
    (lida_a, rej_a), (lida_b, rej_b) = ler_base(base_a), ler_base(base_b)
    resultados = [replace(conciliar(lida_a, lida_b, TOLERANCIA_PADRAO, rej_a, rej_b), batimento=n) for n in ("X", "Y")]

    textos = ler_html(gravar_html(resultados, tmp_path, limite=3)).textos

    # Cada Batimento tem 2 operações (abaixo do limite 3), mas a aba do Excel junta as 4
    assert textos.count("Nem todas as operações com diferença couberam: mostrando 3 de 4, as maiores.") == 2


def test_html_traz_os_atributos_problematicos_do_gabarito_depois_dos_avisos(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    textos = ler_html(linhas[1]).textos
    titulo = "Atributos Problemáticos"
    esperado = ["Atributo", "Valor", "Diferença absoluta", "% da diferença", "% do valor"]
    das_chaves = sum(abs(operacao[3]) for operacao in gabarito.operacoes)
    for atributo, valor, absoluta, acima in gabarito.por_atributo[:5]:
        do_valor = Decimal(absoluta) / das_chaves - Decimal(f"{acima:.15g}")
        esperado += [atributo, valor, curto(absoluta), parte(absoluta, das_chaves), parte(do_valor, 1)]
    assert depois(textos, titulo, len(esperado)) == esperado
    assert textos[textos.index(titulo) + 6 : textos.index(titulo) + 8] == ["Carteira", "Legado"]
    assert textos.index(titulo) > textos.index("Chaves com Diferença")


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
    # As barras do Tipo do Erro e da Idade, de cada Batimento; a linha o script desenha
    assert [tag for tag, _ in leitor.tags].count("svg") == 4
    # O gráfico no tempo leva um ponto por Data-base comum
    pontos = next(attrs["data-pontos"] for tag, attrs in leitor.tags if attrs.get("class") == "historico")
    assert len(json.loads(pontos)) == len(gabarito.historico)


def conciliar_csv(tmp_path, capsys, linhas_a: str, linhas_b: str):
    """Grava as duas bases em `.csv`, concilia pela CLI e devolve os caminhos do `.xlsx` e do `.html`."""
    base_a, base_b = tmp_path / "a.csv", tmp_path / "b.csv"
    base_a.write_text(linhas_a, encoding="utf-8")
    base_b.write_text(linhas_b, encoding="utf-8")
    assert main(["conciliar", str(base_a), str(base_b)]) == 0
    return capsys.readouterr().out.splitlines()


def test_as_partes_da_diferenca_e_do_valor_arredondam_como_o_excel(tmp_path, capsys):
    # Moeda X: 100% da Diferença absoluta e 3/32 do peso (9,375%), 90,625% acima do peso; o Excel mostra 90,63%
    xlsx, html = conciliar_csv(
        tmp_path, capsys,
        "Chave,Data,Valor,Moeda\n1,2026-09-30,0.03,X\n2,2026-09-30,0.29,Y\n",
        "Chave,Data,Valor,Moeda\n1,2026-09-30,10.03,X\n2,2026-09-30,0.29,Y\n",
    )

    celula = next(
        linha[3] for linha in openpyxl.load_workbook(xlsx)["Resumo"].iter_rows() if linha[1].value == "X"
    )
    assert (celula.value, celula.number_format) == (0.90625, "0.00%")
    assert depois(ler_html(html).textos, "X", 3) == ["R$ 10,00", "100,00%", "9,38%"]


def grafico_no_tempo(html) -> tuple[list, list[tuple[str, str]], list[str]]:
    """Do primeiro gráfico no tempo: os pontos, os botões de período (texto e `aria-pressed`) e os textos dele."""
    leitor = ler_html(html)
    pontos = next(json.loads(a["data-pontos"]) for _, a in leitor.tags if a.get("class") == "historico")
    botoes = [a for t, a in leitor.tags if t == "button"]
    textos = leitor.textos[leitor.textos.index("Diferença absoluta por Data-base") + 1 :]
    return pontos, [(b["data-dias"], b["aria-pressed"]) for b in botoes], textos


def test_o_grafico_no_tempo_leva_a_diferenca_absoluta_de_cada_data_base_em_centavos(tmp_path, capsys):
    _, html = conciliar_csv(
        tmp_path, capsys,
        "Chave,Data,Valor\n1,2026-09-29,10.00\n1,2026-09-30,10.00\n",
        "Chave,Data,Valor\n1,2026-09-29,7.50\n1,2026-09-30,5.00\n",
    )

    pontos, botoes, textos = grafico_no_tempo(html)

    assert pontos == [["2026-09-29", 250], ["2026-09-30", 500]]
    assert botoes == []  # um dia de histórico: nenhum período menor que ele
    assert "Arraste sobre o gráfico para ampliar um período." in textos


def test_os_botoes_de_periodo_sao_os_menores_que_o_historico_e_comeca_em_tudo(tmp_path, capsys):
    _, linhas = conciliar_exemplo(tmp_path, capsys)  # 01/04 a 30/09: 182 dias

    _, botoes, textos = grafico_no_tempo(linhas[1])

    assert botoes == [("30", "false"), ("90", "false"), ("180", "false"), ("0", "true")] * 2  # 2 Batimentos
    assert textos[:4] == ["1 mês", "3 meses", "6 meses", "Tudo"]


def test_com_uma_data_base_so_o_grafico_no_tempo_nao_tem_periodo_nem_zoom(tmp_path, capsys):
    _, html = conciliar_csv(
        tmp_path, capsys, "Chave,Data,Valor\n1,2026-09-30,10.00\n", "Chave,Data,Valor\n1,2026-09-30,15.00\n"
    )

    pontos, botoes, textos = grafico_no_tempo(html)

    assert pontos == [["2026-09-30", 500]]
    assert botoes == [] and not any(t.startswith("Arraste") for t in textos)


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


def test_com_um_batimento_o_html_nao_tem_lista_e_o_unico_script_e_o_do_grafico(tmp_path, capsys):
    _, html = conciliar_csv(tmp_path, capsys, *UM_BATIMENTO)

    leitor = ler_html(html)
    assert not {"select", "section"} & {tag for tag, _ in leitor.tags}
    assert [tag for tag, _ in leitor.tags].count("script") == 1
    assert "batimento" not in Path(html).read_text(encoding="utf-8")  # sem o filtro
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
        assert leitor.textos[i + 1] == curto(total_a)
        assert leitor.textos[leitor.textos.index("Total B", i) + 1] == curto(total_b)
    assert [t for t in leitor.textos if t == "Atributos Problemáticos"] == ["Atributos Problemáticos"] * 2
    assert curto(gabarito.juros.diferenca_absoluta) in leitor.textos


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
    assert "--serie-1:#0094ff" in estilo.replace(" ", "")
    escuro = estilo[estilo.index("prefers-color-scheme: dark") :]
    assert ':root:not([data-theme="light"])' in escuro and ':root[data-theme="dark"]' in escuro
    assert escuro.replace(" ", "").count("--serie-1:#0094ff") == 2
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
    assert leitor.dados.count("Diferença absoluta (R$)") == 3  # um cabeçalho por tabela, com o valor exato
    assert depois(leitor.dados, "Data-base", 5)[1:] == ["29/09/2026", "2,50", "30/09/2026", "5,00"]
    # Um Tipo e as 5 faixas, com o valor abreviado; as dicas do gráfico no tempo o script mostra
    assert len(leitor.dicas) == 6 and "Sem padrão (1 Chave): R$ 5,00" in leitor.dicas


def test_a_barra_e_arredondada_so_na_ponta_e_sem_borda(
    tmp_path, capsys
):
    _, html = conciliar_csv(
        tmp_path, capsys,
        "Chave,Data,Valor\n1,2026-09-29,10.00\n1,2026-09-30,10.00\n",
        "Chave,Data,Valor\n1,2026-09-29,12.50\n1,2026-09-30,15.00\n",
    )

    leitor = ler_html(html)
    marcas = {classe: [a for t, a in leitor.tags if a.get("class") == classe] for classe in ("barra",)}
    assert len(marcas["barra"]) == 2  # o Tipo e a faixa com Diferença; as faixas vazias não têm barra
    # A barra é um caminho com 4px arredondados na ponta, e 24px de espessura no máximo
    assert " a4,4 " in marcas["barra"][0]["d"] and 0 < float(marcas["barra"][0]["data-h"]) <= 24
    assert all("stroke" not in a for a in marcas["barra"])


def test_o_svg_escala_com_a_largura_da_tela_e_cabe_em_375px(tmp_path, capsys):
    _, html = conciliar_csv(tmp_path, capsys, *UM_BATIMENTO)

    svgs = [a for tag, a in ler_html(html).tags if tag == "svg"]
    assert len(svgs) == 2  # os das barras; o gráfico no tempo é desenhado na largura da tela
    for a in svgs:
        largura = float(a["viewbox"].split()[2])
        assert a["width"] == "100%" and largura <= 375 - 2 * 16


def test_o_html_comeca_pela_frase_com_o_tipo_do_erro_que_mais_explica_a_diferenca(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    textos = ler_html(linhas[1]).textos
    tipo, chaves, absoluta = gabarito.por_tipo[0]
    frase = f"{tipo} explica {parte(absoluta, gabarito.diferenca_absoluta)} da Diferença absoluta, em {chaves} Chaves."
    assert textos.index(frase) < textos.index("Data-base mais recente")


def test_a_frase_diz_1_chave_no_singular_e_some_sem_chave_com_diferenca(tmp_path, capsys):
    _, html = conciliar_csv(tmp_path, capsys, *UM_BATIMENTO)
    assert "Sem padrão explica 100,00% da Diferença absoluta, em 1 Chave." in ler_html(html).textos

    _, html = conciliar_csv(
        tmp_path, capsys, "Chave,Data,Valor\n1,2026-09-30,10.00\n", "Chave,Data,Valor\n1,2026-09-30,10.00\n"
    )
    textos = ler_html(html).textos
    assert not any("explica" in t for t in textos)
    assert "Diferença absoluta por Tipo do Erro" not in textos


def test_o_grafico_por_tipo_do_erro_vem_depois_do_quadro_e_antes_dos_atributos_problematicos(tmp_path, capsys):
    gabarito, linhas = conciliar_exemplo(tmp_path, capsys)

    textos = ler_html(linhas[1]).textos
    inicio, fim = textos.index("Diferença absoluta por Tipo do Erro"), textos.index("Atributos Problemáticos")
    assert textos.index("Chaves com Diferença") < inicio < fim
    rotulos = [f"{tipo} ({chaves} {'Chave' if chaves == 1 else 'Chaves'})" for tipo, chaves, _ in gabarito.por_tipo]
    assert [t for t in textos[inicio:fim] if t in rotulos] == rotulos
    assert "Uma Chave pode contar em mais de um Tipo do Erro." in textos[inicio:fim]
    assert [t for t in textos[inicio:fim] if t.startswith("R$ ")][0] == curto(gabarito.por_tipo[0][2])


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("1.01", "R$ 1,01"),  # acima da Tolerância de R$ 1,00, para a Diferença absoluta não ser zero
        ("999.99", "R$ 999,99"),
        ("1000.00", "R$ 1,0 mil"),
        ("1049.99", "R$ 1,0 mil"),
        ("1050.00", "R$ 1,1 mil"),
        ("999949.99", "R$ 999,9 mil"),
        ("999950.00", "R$ 1,0 mi"),
        ("688281380.19", "R$ 688,3 mi"),
        ("1234500000000.00", "R$ 1.234,5 bi"),
    ],
)
def test_os_reais_do_quadro_vao_com_rs_e_abreviados(tmp_path, capsys, valor, esperado):
    _, html = conciliar_csv(
        tmp_path, capsys, f"Chave,Data,Valor\n1,2026-09-30,{valor}\n", "Chave,Data,Valor\n1,2026-09-30,0\n"
    )

    textos = ler_html(html).textos
    assert curto(int(Decimal(valor) * 100)) == esperado
    assert depois(textos, "Total A", 1) == [esperado] and depois(textos, "Total B", 1) == ["R$ 0,00"]
    assert depois(textos, "Diferença absoluta", 1) == [esperado]


def test_o_negativo_leva_o_sinal_antes_do_rs_e_os_dados_do_grafico_ficam_exatos(tmp_path, capsys):
    _, html = conciliar_csv(
        tmp_path, capsys, "Chave,Data,Valor\n1,2026-09-30,0\n", "Chave,Data,Valor\n1,2026-09-30,416385257.37\n"
    )

    leitor = ler_html(html)
    assert depois(leitor.textos, "Diferença total", 1) == ["-R$ 416,4 mi"]
    assert "416.385.257,37" in leitor.dados
