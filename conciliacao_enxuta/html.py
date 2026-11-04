"""Resultado → `.html` com o Resumo do Excel, num arquivo só e sem nada buscado na internet.

O único script desenha o gráfico da Diferença no tempo, com período e zoom, e, com mais de um Batimento, faz o
filtro. A Tolerância, as linhas sem Chave e as Linhas rejeitadas ficam só no Excel. Só o HTML tem a frase-resposta
no topo, o gráfico Por Tipo do Erro, os reais com `R$` abreviados e as partes da diferença e do valor nos Atributos
Problemáticos: é o Resumo para quem não é analista.

Este módulo e o `excel` são os únicos lugares onde os centavos viram reais.
"""

from __future__ import annotations

import json
from decimal import ROUND_HALF_UP, Decimal
from html import escape
from pathlib import Path

from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

from conciliacao_enxuta.cruzamento import Resultado
from conciliacao_enxuta.excel import (
    LIMITE_DE_LINHAS,
    NOTA_POR_TIPO,
    TITULO_GRAFICO_DA_IDADE,
    TITULO_GRAFICO_DO_HISTORICO,
    TITULO_PROBLEMATICOS,
    avisos,
    milhar,
    quadro_do_resumo,
    reais,
    rotulo_da_faixa,
)

# Um tema só, na identidade do Banrisul: o azul #0094FF domina, o azul escuro #000050 é texto e fundo, o turquesa e o
# roxo só apoiam. Os papéis de cor são tokens em `:root`. O escuro é escolhido, não inversão, e vale pela preferência
# do sistema ou por `data-theme="dark"`; `data-theme="light"` trava o claro. As fontes da marca (Exo 2 e Source Sans)
# são usadas se estiverem instaladas: o arquivo abre sem internet, então não as busca.
_ESCURO = (
    "--superficie:#000050;--cartao:#0c0c66;--texto:#ffffff;--texto-2:#c6cdf5;--texto-3:#a9b2ec;"
    "--grade:#2c2f86;--serie-1:#0094ff;--painel:#00003a;--painel-borda:#2c2f86;--roxo:#a68bff;"
)
ESTILO = (
    ":root{--superficie:#ffffff;--cartao:#eef6ff;--texto:#000050;--texto-2:#3b4174;--texto-3:#565c8a;"
    "--grade:#dbe1ef;--serie-1:#0094ff;--painel:#000050;--painel-borda:#000050;"
    "--painel-texto:#ffffff;--painel-rotulo:#b9c3f7;--painel-linha:#2a2f80;--foco:#1cd8ca;--roxo:#936ffa;"
    "--sobre-azul:#000050;}\n"
    '@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){' + _ESCURO + "}}\n"
    ':root[data-theme="dark"]{' + _ESCURO + """}
body { font-family: "Source Sans 3", "Source Sans Pro", "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif;
  font-size: 17px; line-height: 1.5; margin: 0 auto; padding: 32px 16px 56px; max-width: 760px;
  color: var(--texto); background: var(--superficie); -webkit-font-smoothing: antialiased; }
h1, h2, .valor, th { font-family: "Exo 2", "Segoe UI", system-ui, sans-serif; }
h1 { font-size: 34px; font-weight: 700; letter-spacing: -0.01em; line-height: 1.1; margin: 0; }
.frase { font-family: "Exo 2", "Segoe UI", system-ui, sans-serif; font-size: 22px; font-weight: 600; line-height: 1.3;
  margin: 0 0 20px; }
.nota { margin: 4px 0 0; font-size: 15px; color: var(--texto-2); }
h2 { font-size: 19px; font-weight: 600; margin: 40px 0 12px; }
.topo { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px 24px;
  margin-bottom: 24px; }
select { font: inherit; font-weight: 600; color: var(--texto); background: var(--superficie);
  border: 2px solid var(--serie-1); border-radius: 999px; padding: 6px 16px; max-width: 100%; cursor: pointer; }
select:focus-visible, summary:focus-visible { outline: 3px solid var(--foco); outline-offset: 2px; }

/* O quadro do Resumo: o painel azul-escuro, com um brilho azul no canto e o roxo e o turquesa de apoio */
.painel { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 24px 20px; padding: 28px;
  border-radius: 28px 28px 28px 8px; border: 1px solid var(--painel-borda); color: var(--painel-texto);
  background: radial-gradient(120% 90% at 100% 0%, rgba(0, 148, 255, 0.42), rgba(0, 148, 255, 0) 60%),
    radial-gradient(60% 70% at 92% 105%, rgba(28, 216, 202, 0.22), rgba(28, 216, 202, 0) 70%),
    radial-gradient(70% 80% at 0% 100%, rgba(147, 111, 250, 0.38), rgba(147, 111, 250, 0) 70%), var(--painel); }
.rotulo { display: block; font-size: 15px; color: var(--painel-rotulo); }
.valor { display: block; font-weight: 600; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; line-height: 1.15; }
.meta { grid-column: span 6; }
.meta .valor { font-size: 18px; font-weight: 500; }
.conta { grid-column: span 2; }
.conta .valor { font-size: 23px; }
.destaque, .chaves { border-top: 1px solid var(--painel-linha); padding-top: 22px; }
.destaque { grid-column: span 4; margin-right: -20px; padding-right: 20px; }  /* a linha de cima sem a falha do vão */
.destaque .valor { font-size: clamp(34px, 8vw, 46px); font-weight: 700; color: var(--serie-1); letter-spacing: -0.01em; }
.chaves { grid-column: span 2; }
.chaves .valor { font-size: clamp(28px, 6vw, 34px); }
.com-parte { display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 14px; }
.parte { display: flex; flex-direction: column; line-height: 1.2; }
.fracao { font-family: "Exo 2", "Segoe UI", system-ui, sans-serif; font-size: 20px; font-weight: 600;
  color: var(--foco); font-variant-numeric: tabular-nums; }
.de { font-size: 14px; color: var(--painel-rotulo); }
@media (max-width: 560px) {
  .painel { grid-template-columns: repeat(2, minmax(0, 1fr)); padding: 22px; gap: 20px 16px; }
  .meta, .conta, .destaque, .chaves { grid-column: span 2; }
  .destaque { margin-right: 0; padding-right: 0; }
  .chaves { border-top: 0; padding-top: 0; }
}

.aviso { margin: 16px 0 0; padding: 12px 18px; border-radius: 16px 16px 16px 4px; background: var(--cartao);
  color: var(--texto); font-size: 16px; }
table { border-collapse: collapse; width: 100%; margin: 16px 0 0; font-size: 16px; }
th, td { padding: 9px 10px; text-align: left; overflow-wrap: break-word; border-bottom: 1px solid var(--grade); }
th { font-size: 15px; font-weight: 600; color: var(--texto-2); border-bottom: 2px solid var(--serie-1); }
th:first-child, td:first-child { padding-left: 0; }
th:last-child, td:last-child { padding-right: 0; }
td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
@media (max-width: 560px) { table { font-size: 15px; } th, td { padding: 8px 6px; } }
details { margin-top: 8px; font-size: 15px; color: var(--texto-2); }
summary { cursor: pointer; color: var(--serie-1); font-weight: 600; width: fit-content; border-radius: 4px; }
svg { display: block; font-family: inherit; }
svg.idade { width: 100%; max-width: 600px; height: auto; font-size: 10.5px; }
svg text { fill: var(--texto-2); }
svg .v { fill: var(--texto); font-weight: 600; }
svg .v, svg .eixo { paint-order: stroke; stroke: var(--superficie); stroke-width: 4px; }  /* legível sobre a linha */
.grade { stroke: var(--grade); stroke-width: 1; }
.barra { fill: var(--serie-1); }
.alvo { fill: transparent; }
@media (max-width: 560px) { svg.idade { font-size: 13px; } }  /* no celular o SVG não amplia: a letra fica maior */

/* O gráfico no tempo, desenhado pelo script na largura da tela */
.cabeca { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px 16px;
  margin: 40px 0 6px; }
.cabeca h2 { margin: 0; }
.periodos { display: flex; flex-wrap: wrap; gap: 6px; }
.periodos button { font: inherit; font-size: 14px; font-weight: 600; color: var(--texto-2); background: transparent;
  border: 1.5px solid var(--grade); border-radius: 999px; padding: 3px 12px; cursor: pointer; }
.periodos button:hover { border-color: var(--serie-1); }
.periodos button[aria-pressed="true"] { background: var(--serie-1); border-color: var(--serie-1); color: var(--sobre-azul); }
.periodos button:focus-visible { outline: 3px solid var(--foco); outline-offset: 2px; }
.legenda { margin: 0 0 8px; font-size: 15px; color: var(--texto-2); }
.ajuda { color: var(--texto-3); }
.no-tempo { position: relative; }
.desenho { min-height: 230px; touch-action: pan-y; user-select: none; -webkit-user-select: none; cursor: crosshair; }
.desenho svg { font-size: 13px; overflow: visible; }
.tracejada { stroke-dasharray: 2 5; }
.area { fill: var(--serie-1); fill-opacity: 0.13; }
.linha { fill: none; stroke: var(--serie-1); stroke-width: 2.5; stroke-linejoin: round; stroke-linecap: round; }
.ponto { fill: var(--serie-1); stroke: var(--superficie); stroke-width: 2.5; }
.foco { fill: var(--roxo); }
.mira { stroke: var(--roxo); stroke-width: 1.5; stroke-dasharray: 4 4; }
.selecao { fill: var(--roxo); fill-opacity: 0.2; }
.dica { position: absolute; pointer-events: none; white-space: nowrap; padding: 6px 12px; font-size: 14px;
  color: var(--painel-texto); background: var(--painel); border: 1px solid var(--roxo); border-radius: 12px 12px 12px 4px; }
.dica span { display: block; font-size: 13px; color: var(--painel-rotulo); }
.dica strong { font-family: "Exo 2", "Segoe UI", system-ui, sans-serif; font-variant-numeric: tabular-nums; }
"""
)
# Mostra só o Resumo do Batimento escolhido. Roda também na abertura, para a lista e o Resumo
# não divergirem quando o navegador devolve a escolha anterior.
FILTRO = """
var lista = document.getElementById("batimento");
function mostrar() {
  document.querySelectorAll("section").forEach(function (s, i) { s.hidden = i !== lista.selectedIndex; });
}
lista.onchange = mostrar;
mostrar();
"""
# Desenha o gráfico da Diferença absoluta por Data-base na largura da tela, a partir de `data-pontos` (Data-base e
# centavos). Os botões escolhem o período até a Data-base mais recente; arrastar sobre o gráfico amplia um trecho.
GRAFICO = r"""
(function () {
  var MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
  function milhar(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, "."); }
  function reais(c) {
    var r = Math.abs(c) % 100;
    return (c < 0 ? "-" : "") + milhar(Math.floor(Math.abs(c) / 100)) + "," + (r < 10 ? "0" : "") + r;
  }
  function reaisCurtos(c) {  // como `reais_curtos` do Python: R$ 705,42, R$ 4,2 mil, R$ 688,3 mi, R$ 1,1 bi
    var a = Math.abs(c), sinal = c < 0 ? "-" : "", escalas = [[1e4, " mil"], [1e7, " mi"], [1e10, " bi"]], d, i;
    if (a < 100000) return sinal + "R$ " + reais(a);
    for (i = 0; i < escalas.length; i++) {  // décimos da unidade, com o meio para longe do zero
      d = Math.round(a / escalas[i][0]);
      if (d < 10000 || i === escalas.length - 1) break;
    }
    return sinal + "R$ " + milhar(Math.floor(d / 10)) + "," + (d % 10) + escalas[i][1];
  }
  function curto(c) {  // 1,25 bi, 350 mi, 12 mil: o eixo cabe sem perder a ordem de grandeza
    var v = c / 100, escalas = [[1e9, " bi"], [1e6, " mi"], [1e3, " mil"], [1, ""]];
    for (var i = 0; i < escalas.length - 1 && v < escalas[i][0]; i++);
    return (v / escalas[i][0]).toLocaleString("pt-BR", {maximumFractionDigits: 2}) + escalas[i][1];
  }
  function data(d) { return d.split("-").reverse().join("/"); }
  function dias(a, b) { return (Date.parse(b) - Date.parse(a)) / 864e5; }
  function passo(bruto) {
    var p = Math.pow(10, Math.floor(Math.log10(bruto))), f = bruto / p;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p;
  }

  document.querySelectorAll(".historico").forEach(function (caixa) {
    var pontos = JSON.parse(caixa.getAttribute("data-pontos"));
    var desenho = caixa.querySelector(".desenho"), dica = caixa.querySelector(".dica");
    var periodo = caixa.querySelector(".periodo"), botoes = caixa.querySelectorAll(".periodos button");
    var ini = 0, fim = pontos.length - 1, geo = null, arraste = null;

    function desenhar() {
      var largura = desenho.clientWidth;
      if (!largura || !pontos.length) return;
      var vis = pontos.slice(ini, fim + 1), n = vis.length;
      var altura = largura < 480 ? 230 : 290, dir = 12, topo = 28, base = altura - 30;
      var maior = Math.max.apply(null, vis.map(function (p) { return p[1]; }));
      var marcas = [0], teto = 1;
      if (maior > 0) {  // sem Diferença, o eixo só mostra o 0
        var s = Math.max(1, passo(maior / 5));
        teto = Math.ceil(maior / s) * s;
        for (var v = s; v <= teto + s / 2; v += s) marcas.push(v);
      }
      var rotulos = marcas.map(curto);
      var esq = 14 + 7.5 * Math.max.apply(null, rotulos.map(function (r) { return r.length; }));
      function x(i) { return n > 1 ? esq + i / (n - 1) * (largura - esq - dir) : (esq + largura - dir) / 2; }
      function y(v) { return base - v / teto * (base - topo); }
      geo = {esq: esq, dir: dir, largura: largura, n: n, x: x, y: y};

      var svg = ['<svg width="' + largura + '" height="' + altura + '" aria-hidden="true">'];
      marcas.forEach(function (v, k) {
        svg.push('<line class="grade' + (v ? " tracejada" : "") + '" x1="' + esq + '" x2="' + (largura - dir) +
          '" y1="' + y(v) + '" y2="' + y(v) + '"/>');
        svg.push('<text x="' + (esq - 10) + '" y="' + (y(v) + 4) + '" text-anchor="end">' + rotulos[k] + "</text>");
      });

      // As datas: por mês num período longo, por dia num curto, só as que cabem
      var cabem = Math.max(2, Math.floor((largura - esq - dir) / 80)), xs = [], rotulo;
      if (dias(vis[0][0], vis[n - 1][0]) > 62) {
        for (var i = 1; i < n; i++) if (vis[i][0].slice(0, 7) !== vis[i - 1][0].slice(0, 7)) xs.push(i);
        var pulo = Math.ceil(xs.length / cabem);
        xs = xs.filter(function (_, k) { return k % pulo === 0; });
        rotulo = function (d) { return MESES[+d.slice(5, 7) - 1] + "/" + d.slice(2, 4); };
      } else {
        var m = Math.min(n, cabem);
        for (var k = 0; k < m; k++) {
          var j = m > 1 ? Math.round(k * (n - 1) / (m - 1)) : 0;
          if (xs.indexOf(j) < 0) xs.push(j);
        }
        rotulo = function (d) { return d.slice(8, 10) + "/" + d.slice(5, 7); };
      }
      xs.forEach(function (i) {
        var ancora = x(i) > largura - dir - 24 ? "end" : x(i) < esq + 24 && n > 1 ? "start" : "middle";
        svg.push('<line class="grade" x1="' + x(i) + '" x2="' + x(i) + '" y1="' + base + '" y2="' + (base + 5) + '"/>');
        svg.push('<text x="' + x(i) + '" y="' + (base + 21) + '" text-anchor="' + ancora + '">' + rotulo(vis[i][0]) + "</text>");
      });

      var linha = vis.map(function (p, i) { return x(i).toFixed(1) + "," + y(p[1]).toFixed(1); }).join(" ");
      if (n > 1) {
        svg.push('<polygon class="area" points="' + x(0) + "," + base + " " + linha + " " + x(n - 1) + "," + base + '"/>');
        svg.push('<polyline class="linha" points="' + linha + '"/>');
      }
      var ultimo = vis[n - 1];  // o valor da última Data-base do período, acima do seu ponto
      svg.push('<circle class="ponto" cx="' + x(n - 1) + '" cy="' + y(ultimo[1]) + '" r="4.5"/>');
      svg.push('<text class="v" x="' + Math.min(x(n - 1), largura - dir) + '" y="' + (y(ultimo[1]) - 12) +
        '" text-anchor="' + (n > 1 ? "end" : "middle") + '">' + reaisCurtos(ultimo[1]) + "</text>");
      svg.push('<rect class="selecao" y="' + topo + '" height="' + (base - topo) + '" visibility="hidden"/>');
      svg.push('<line class="mira" y1="' + topo + '" y2="' + base + '" visibility="hidden"/>');
      svg.push('<circle class="ponto foco" r="5.5" visibility="hidden"/>');
      desenho.innerHTML = svg.join("") + "</svg>";
      dica.hidden = true;
      periodo.textContent = data(vis[0][0]) + (n > 1 ? " a " + data(vis[n - 1][0]) : "") + ", " + milhar(n) +
        (n === 1 ? " Data-base." : " Data-bases.");
    }

    function indice(ev) {
      if (geo.n < 2) return 0;
      var px = ev.clientX - desenho.getBoundingClientRect().left;
      var i = Math.round((px - geo.esq) / (geo.largura - geo.esq - geo.dir) * (geo.n - 1));
      return Math.max(0, Math.min(geo.n - 1, i));
    }
    function marca(classe, atributos) {
      var el = desenho.querySelector("." + classe);
      for (var a in atributos) el.setAttribute(a, atributos[a]);
    }
    function mostrarDica(i) {
      var p = pontos[ini + i], cx = geo.x(i), cy = geo.y(p[1]);
      marca("mira", {x1: cx, x2: cx, visibility: "visible"});
      marca("foco", {cx: cx, cy: cy, visibility: "visible"});
      dica.innerHTML = "<span>" + data(p[0]) + "</span><strong>" + reaisCurtos(p[1]) + "</strong>";
      dica.hidden = false;
      dica.style.left = Math.min(Math.max(cx - dica.offsetWidth / 2, 0), geo.largura - dica.offsetWidth) + "px";
      dica.style.top = Math.max(cy - dica.offsetHeight - 16, 0) + "px";
    }
    function esconder() {
      if (!geo || arraste !== null) return;
      marca("mira", {visibility: "hidden"});
      marca("foco", {visibility: "hidden"});
      dica.hidden = true;
    }
    function marcar(ativo) {
      botoes.forEach(function (b) { b.setAttribute("aria-pressed", String(b === ativo)); });
    }

    desenho.addEventListener("pointerdown", function (ev) {
      if (!geo || geo.n < 2) return;
      arraste = indice(ev);
      desenho.setPointerCapture(ev.pointerId);
    });
    desenho.addEventListener("pointermove", function (ev) {
      if (!geo) return;
      var i = indice(ev);
      mostrarDica(i);
      if (arraste !== null) {
        var a = Math.min(arraste, i), b = Math.max(arraste, i);
        marca("selecao", {x: geo.x(a), width: geo.x(b) - geo.x(a), visibility: "visible"});
      }
    });
    desenho.addEventListener("pointerup", function (ev) {
      if (arraste === null) return;
      var i = indice(ev), a = Math.min(arraste, i), b = Math.max(arraste, i), inicio = ini;
      arraste = null;
      marca("selecao", {visibility: "hidden"});
      if (b > a) {  // amplia o trecho arrastado
        ini = inicio + a;
        fim = inicio + b;
        marcar(null);
        desenhar();
      }
    });
    desenho.addEventListener("pointerleave", esconder);
    botoes.forEach(function (b) {
      b.onclick = function () {
        var limite = +b.getAttribute("data-dias");
        ini = 0;
        fim = pontos.length - 1;
        while (limite && dias(pontos[ini][0], pontos[fim][0]) > limite) ini++;
        marcar(b);
        desenhar();
      };
    });
    // Redesenha quando a largura muda, inclusive quando o Batimento escolhido aparece
    if (window.ResizeObserver) new ResizeObserver(desenhar).observe(desenho);
    else window.addEventListener("resize", desenhar);
    desenhar();
  });
})();
"""
# Os botões de período, até a Data-base mais recente; só aparecem os menores que o histórico
PERIODOS = ((30, "1 mês"), (90, "3 meses"), (180, "6 meses"), (365, "1 ano"))


TITULO_GRAFICO_POR_TIPO = "Diferença absoluta por Tipo do Erro"
TITULOS_PROBLEMATICOS = ("Atributo", "Valor", "Diferença absoluta", "% da diferença", "% do valor")
COLUNA_DOS_DADOS = "Diferença absoluta (R$)"  # nas tabelas dos dados dos gráficos, com o valor exato

# Onde cada linha do quadro fica no painel (a Tolerância fica só no Excel): a Data-base em cima, os totais no meio e, embaixo, em
# destaque, a Diferença absoluta e as Chaves com Diferença
_LUGAR_NO_PAINEL = {
    "Data-base mais recente": "meta",
    "Total A": "conta",
    "Total B": "conta",
    "Diferença total": "conta",
    "Diferença absoluta": "destaque",
    "Chaves com Diferença": "chaves",
}


def gravar_html(resultados: list[Resultado], pasta: str | Path, limite: int = LIMITE_DE_LINHAS) -> Path:
    """Grava `conciliacao_AAAA-MM-DD.html` em `pasta`, sobrescrevendo, e devolve o caminho.

    `resultados` são os Batimentos, na ordem da Base A. Com mais de um, o arquivo traz uma lista suspensa e o
    Resumo de cada um; só o primeiro aparece sem o script. `limite` é o mesmo do `.xlsx`: acima dele, o Resumo
    avisa do corte das operações.
    """
    caminho = Path(pasta) / f"conciliacao_{resultados[0].data_base.isoformat()}.html"
    total = sum(r.operacoes.height for r in resultados)  # o corte é da aba inteira, como no Excel
    lista, corpo, script = "", _resumo(resultados[0], limite, total), GRAFICO
    if len(resultados) > 1:
        opcoes = "".join(f"<option>{_do_arquivo(r.batimento)}</option>" for r in resultados)
        lista = f'<select id="batimento" aria-label="Batimento">{opcoes}</select>'
        secoes = "\n".join(
            f"<section{' hidden' if i else ''}>\n{_resumo(r, limite, total)}\n</section>" for i, r in enumerate(resultados)
        )
        corpo, script = secoes, FILTRO + GRAFICO
    titulo = f"Conciliação {resultados[0].data_base:%d/%m/%Y}"
    pagina = (
        '<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(titulo)}</title><style>{ESTILO}</style></head>\n<body>\n"
        f'<header class="topo"><h1>Resumo</h1>{lista}</header>\n'
        + corpo
        + f"\n<script>{script}</script>\n</body></html>\n"
    )
    caminho.write_text(pagina, encoding="utf-8")
    return caminho


def _resumo(resultado: Resultado, limite: int, total_de_operacoes: int) -> str:
    """O Resumo de um Batimento: a frase-resposta, o quadro, os avisos, o Tipo do Erro, os Atributos Problemáticos
    e os dois gráficos da Diferença."""
    partes = []
    if resultado.por_tipo.height:  # o Tipo do Erro que mais explica a Diferença absoluta, antes dos números
        tipo, chaves, absoluta = resultado.por_tipo.row(0)
        partes.append(
            f'<p class="frase">{escape(tipo)} explica {_porcento(absoluta / resultado.diferenca_absoluta)} da '
            f"Diferença absoluta, em {_chaves(chaves)}.</p>"
        )
    em_reais = {
        "Total A": resultado.total_a,
        "Total B": resultado.total_b,
        "Diferença total": resultado.diferenca_total,
        "Diferença absoluta": resultado.diferenca_absoluta,
    }
    partes.append('<div class="painel">')
    for rotulo, _, _, texto in quadro_do_resumo(resultado):
        if rotulo not in _LUGAR_NO_PAINEL:
            continue
        if rotulo in em_reais:
            texto = reais_curtos(em_reais[rotulo])
        valor = f'<span class="valor">{escape(texto)}</span>'
        if rotulo == "Chaves com Diferença" and resultado.chaves:  # e, ao lado, quanto são de todas as Chaves
            fracao = _porcento(resultado.chaves_com_diferenca / resultado.chaves)
            total = _chaves(resultado.chaves)
            valor = (
                f'<span class="com-parte">{valor}<span class="parte"><span class="fracao">{fracao}</span>'
                f'<span class="de">das {total}</span></span></span>'
            )
        partes.append(f'<div class="{_LUGAR_NO_PAINEL[rotulo]}"><span class="rotulo">{escape(rotulo)}</span>{valor}</div>')
    partes.append("</div>")

    # O aviso do corte, só quando acontece; as linhas sem Chave e as Linhas rejeitadas ficam só no Excel
    partes += [
        f'<p class="aviso">{escape(aviso)}</p>'
        for aviso in avisos(resultado, limite, total_de_operacoes, rejeitadas=False)
    ]

    # Quanto cada Tipo do Erro explica; sem Chave com Diferença, nada
    if resultado.por_tipo.height:
        tipos = [(f"{tipo} ({_chaves(chaves)})", absoluta) for tipo, chaves, absoluta in resultado.por_tipo.iter_rows()]
        partes.append(_grafico_de_barras(TITULO_GRAFICO_POR_TIPO, "Tipo do Erro", tipos, NOTA_POR_TIPO))

    # Os Atributos Problemáticos, com a parte da diferença e a parte do valor de cada um no lugar da Diferença acima
    # do peso, que é a primeira menos a segunda; sem Atributo acima do peso, a tabela não aparece
    if resultado.atributos_problematicos.height:
        das_chaves = resultado.operacoes["Diferenca"].abs().sum()  # a Diferença absoluta só das Chaves
        partes.append(f"<h2>{escape(TITULO_PROBLEMATICOS)}</h2>")
        partes.append(_cabecalho(TITULOS_PROBLEMATICOS))
        for atributo, valor, absoluta, acima_do_peso in resultado.atributos_problematicos.iter_rows():
            da_diferenca = absoluta / das_chaves
            partes.append(
                f"<tr><td>{_do_arquivo(atributo)}</td><td>{_do_arquivo(valor)}</td>"
                f'<td class="n">{reais_curtos(absoluta)}</td><td class="n">{_porcento(da_diferenca)}</td>'
                f'<td class="n">{_porcento(da_diferenca - acima_do_peso)}</td></tr>'
            )
        partes.append("</table>")

    idade = [(rotulo_da_faixa(faixa, chaves, linhas), absoluta) for faixa, chaves, linhas, absoluta in resultado.por_idade]
    partes.append(_grafico_de_barras(TITULO_GRAFICO_DA_IDADE, "Faixa", idade))
    partes.append(_grafico_de_linha(resultado))
    return "\n".join(partes)


def reais_curtos(centavos: int) -> str:
    """Centavos → reais com `R$`, abreviados para ler de longe: `R$ 705,42` abaixo de R$ 1.000, senão uma casa e
    `mil`, `mi` ou `bi` (`R$ 688,3 mi`), com o meio para longe do zero; `-R$ 416,4 mi` no negativo."""
    valor = Decimal(abs(centavos)) / 100
    if valor < 1000:
        texto = reais(abs(centavos))
    else:
        # A primeira unidade em que o arredondado fica abaixo de 1.000: R$ 999.950,00 é R$ 1,0 mi, não 1.000,0 mil
        for expoente, unidade in ((3, "mil"), (6, "mi"), (9, "bi")):
            decimos = int((valor / Decimal(10) ** expoente).quantize(Decimal("0.1"), ROUND_HALF_UP) * 10)
            if decimos < 10_000:
                break
        texto = f"{milhar(decimos // 10)},{decimos % 10} {unidade}"
    return f"{'-' if centavos < 0 else ''}R$ {texto}"


def _porcento(fracao: float) -> str:
    """A fração em texto, com 2 casas, como o Excel mostra `0.00%`: `90,63%`."""
    return f"{_percentual(fracao)}%".replace(".", ",")


def _chaves(quantas: int) -> str:
    """`1 Chave` ou `1.234 Chaves`."""
    return f"{milhar(quantas)} {'Chave' if quantas == 1 else 'Chaves'}"


def _do_arquivo(texto: str) -> str:
    """Um texto que veio do arquivo (Atributo e o seu valor) sem os caracteres de controle, como no Excel, e escapado."""
    return escape(ILLEGAL_CHARACTERS_RE.sub("", texto))


def _percentual(fracao: float) -> Decimal:
    """A fração em %, com 2 casas, como o Excel mostra `0.00%`: com 15 dígitos e o meio arredondado para cima."""
    return (Decimal(f"{fracao:.15g}") * 100).quantize(Decimal("0.01"), ROUND_HALF_UP)


def _cabecalho(titulos: tuple[str, ...]) -> str:
    """O começo de uma tabela, com a linha de títulos."""
    return "<table><tr>" + "".join(f"<th>{escape(t)}</th>" for t in titulos) + "</tr>"


def _dados_do_grafico(titulos: tuple[str, str], linhas: list[tuple[str, str]]) -> str:
    """Os dados do gráfico em tabela, recolhida, para quem não enxerga as marcas."""
    corpo = "".join(f'<tr><td>{escape(r)}</td><td class="n">{v}</td></tr>' for r, v in linhas)
    return f"<details><summary>Dados do gráfico</summary>{_cabecalho(titulos)}{corpo}</table></details>"


def _grafico_de_barras(titulo: str, coluna: str, barras: list[tuple[str, int]], nota: str | None = None) -> str:
    """A Diferença absoluta de cada linha de `barras` (rótulo, centavos), em barras deitadas, com o `titulo`, a
    `nota` embaixo, se houver, e os dados numa tabela cuja primeira coluna se chama `coluna`."""
    largura, linha, espessura, maxima = 340, 44, 16, 230  # a barra sai de x = 1, na linha de base
    maior = max((absoluta for _, absoluta in barras), default=0) or 1
    altura = len(barras) * linha
    titulo = escape(titulo)
    svg = [f'<svg class="idade" viewBox="0 0 {largura} {altura}" width="100%" role="img" aria-label="{titulo}">']
    for i, (rotulo, absoluta) in enumerate(barras):
        y, w = i * linha, round(absoluta / maior * maxima)
        dica = escape(f"{rotulo}: {reais_curtos(absoluta)}")
        svg.append(f'<g><title>{dica}</title><rect class="alvo" x="0" y="{y}" width="{largura}" height="{linha}"/>')
        svg.append(f'<text x="0" y="{y + 14}">{escape(rotulo)}</text>')
        if w:
            r = min(4, w)  # 4px arredondados só na ponta do dado; a base é reta
            svg.append(
                f'<path class="barra" data-h="{espessura}" d="M1,{y + 22} H{1 + w - r} a{r},{r} 0 0 1 {r},{r} '
                f'V{y + 22 + espessura - r} a{r},{r} 0 0 1 -{r},{r} H1 Z"/>'
            )
        svg.append(f'<text class="v" x="{w + 7}" y="{y + 35}">{reais_curtos(absoluta)}</text></g>')
    svg.append(f'<line class="grade" x1="0.5" y1="0" x2="0.5" y2="{altura}"/></svg>')
    if nota:
        svg.append(f'<p class="nota">{escape(nota)}</p>')
    dados = _dados_do_grafico((coluna, COLUNA_DOS_DADOS), [(r, reais(a)) for r, a in barras])
    return f"<h2>{titulo}</h2>\n" + "\n".join(svg) + "\n" + dados


def _grafico_de_linha(resultado: Resultado) -> str:
    """A Diferença absoluta por Data-base: os pontos vão em `data-pontos` e o script desenha o gráfico."""
    historico = resultado.historico
    titulo = escape(TITULO_GRAFICO_DO_HISTORICO)
    pontos = escape(json.dumps([[data.isoformat(), absoluta] for data, absoluta in historico]))
    extensao = (historico[-1][0] - historico[0][0]).days if historico else 0
    botoes = "".join(
        f'<button type="button" data-dias="{dias}" aria-pressed="false">{rotulo}</button>'
        for dias, rotulo in PERIODOS
        if dias < extensao
    )
    if botoes:
        botoes = (
            f'<div class="periodos" role="group" aria-label="Período">{botoes}'
            '<button type="button" data-dias="0" aria-pressed="true">Tudo</button></div>'
        )
    ajuda = ' <span class="ajuda">Arraste sobre o gráfico para ampliar um período.</span>' if len(historico) > 1 else ""
    dados = _dados_do_grafico(("Data-base", COLUNA_DOS_DADOS), [(f"{d:%d/%m/%Y}", reais(a)) for d, a in historico])
    return (
        f'<div class="historico" data-pontos="{pontos}">\n'
        f'<div class="cabeca"><h2>{titulo}</h2>{botoes}</div>\n'
        f'<p class="legenda"><span class="periodo"></span>{ajuda}</p>\n'
        f'<div class="no-tempo"><div class="desenho" role="img" aria-label="{titulo}"></div>'
        '<div class="dica" hidden></div></div>\n'
        f"</div>\n{dados}"
    )
