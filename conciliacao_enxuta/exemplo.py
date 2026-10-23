"""Gerador de bases de exemplo com gabarito.

As Diferenças são plantadas e o gabarito é montado a partir delas, sem passar pelo cruzamento.
Cada base traz uma posição por dia útil de seis meses, e a Base B traz ainda uma Data-base que a Base A não tem.
A Base A traz o Atributo Produto, vazio em algumas Chaves; a Base B traz o Produto e a Filial. As duas trazem a
Carteira, em que Legado concentra a Diferença, e a Moeda, BRL em todas as Chaves.
No fim de cada base vêm Linhas rejeitadas, uma de cada motivo, que ficam fora de tudo.
No `.csv`, a Base A sai em UTF-8 com BOM e a Base B em cp1252, as duas formas do Excel em português.
Uso: `python -m conciliacao_enxuta.exemplo [PASTA] [csv|xlsx|parquet]` (padrão: `exemplo` e `csv`).
"""

from __future__ import annotations

import csv
import random
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import openpyxl
import polars as pl

from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO as TOLERANCIA
from conciliacao_enxuta.cruzamento import SEPARADOR_DE_TIPOS, SemChave

PRIMEIRA_DATA_BASE = date(2026, 4, 1)
DATA_BASE = date(2026, 9, 30)  # a mais recente comum às duas bases
SO_NA_BASE_B = date(2026, 10, 1)  # ignorada: a Base A não tem
N_CHAVES = 200

# Chaves gravadas em duas linhas, que o cruzamento tem de somar: uma sem Diferença e uma com
REPETIDAS_A = ["C00005", "C00011"]
REPETIDAS_B = ["C00006", "C00021"]
# Linhas sem Chave (vazia ou só espaço), que ficam fora do cruzamento; repetidas em toda Data-base.
# Todas passam da Tolerância: cada uma é Diferença do valor inteiro (+ em A, − em B) em toda Data-base comum.
SEM_CHAVE_A = [("", 12_345), ("   ", -2_000)]
SEM_CHAVE_B = [("", 77_700)]
DIFERENCAS_SEM_CHAVE = [v for _, v in SEM_CHAVE_A] + [-v for _, v in SEM_CHAVE_B]
# Linhas rejeitadas, no fim da base: (Chave, Data, Valor, Motivo), gravadas assim mesmo no arquivo, em texto, e no
# `.xlsx` também. O `.parquet` tem tipos nativos e não guarda Data nem Valor ilegível: lá, só a Base B as traz.
REJEITADAS_A = [
    ("C00002", None, "10,00", "Data vazia"),
    ("C00003", "31/02/2026", "10,00", "Data ilegível"),
    (None, "30/09/2026", "abc", "Valor ilegível"),  # sem Chave: rejeitada, e não vira linha sem Chave
]
REJEITADAS_B = [(" C00006 ", DATA_BASE, None, "Valor vazio")]  # a Data é data no `.xlsx` e no `.parquet`
# Chaves de Diferença plantada que ficam sem ela de uma Data-base a outra, inclusive, com esta Diferença.
# O Aberta desde delas é o dia útil seguinte; as outras têm Diferença desde a primeira Data-base ("ou antes"),
# com outro valor a cada dia.
PAUSAS = {
    "C00021": (date(2026, 6, 15), date(2026, 6, 15), 0),  # some e volta: Aberta desde 16/06/2026
    "C00031": (date(2026, 9, 29), date(2026, 9, 29), TOLERANCIA),  # cai para dentro da Tolerância: 30/09/2026
    "C00051": (PRIMEIRA_DATA_BASE, date(2026, 7, 31), 0),  # só abre depois: 03/08/2026
}

PRODUTOS = ("Crédito", "Débito", "Câmbio", "Seguro")
# Os nomes de coluna e os formatos variam de propósito, entre as bases e do nome exato
CABECALHO_A = ["CHAVE", "data", "Valor ", "Produto", "Carteira", "Moeda"]
CABECALHO_B = [" Chave", "DATA", "VALOR", "Produto", "Filial", "Carteira", "Moeda"]
ATRIBUTOS_A, ATRIBUTOS_B = CABECALHO_A[3:], CABECALHO_B[3:]


def _legado(i: int) -> bool:
    """As Chaves da Carteira Legado: pouco peso no total e muita Diferença.

    Caem todas no caso da Vírgula deslocada (i % 10 == 9), que nelas é sempre B = 1000 × A.
    """
    return i % 20 == 19


@dataclass(frozen=True)
class Gabarito:
    """O que o Resumo deve mostrar com a Tolerância padrão. Dinheiro em centavos."""

    base_a: Path
    base_b: Path
    data_base: date
    total_a: int
    total_b: int
    diferenca_total: int
    diferenca_absoluta: int
    chaves_com_diferenca: int
    sem_chave_a: SemChave
    sem_chave_b: SemChave
    # (Base, Linha, Chave, Data, Valor, Motivo) como a aba Erros mostra: a Base A e depois a B, na ordem do arquivo
    rejeitadas: tuple[tuple[str, int, str | None, str | None, str | None, str], ...]
    data_bases_so_em_b: tuple[date, ...]
    historico: tuple[tuple[date, int], ...]  # (Data-base comum, Diferença absoluta), em ordem de data
    # (Chave, A, B, Diferença, Tipo do Erro), por |Diferença| decrescente
    operacoes: tuple[tuple[str, int, int, int, str], ...]
    aberta_desde: dict[str, date]  # das Chaves das operações
    atributos: dict[str, dict[str, str | None]]  # das Chaves das operações: {Chave: {Atributo: valor}}
    # (Atributo, Valor, Diferença, Concentração), por Diferença absoluta decrescente
    por_atributo: tuple[tuple[str, str, int, float], ...]
    por_tipo: tuple[tuple[str, int, int], ...]  # (Tipo do Erro, Chaves, Diferença absoluta), da maior para a menor
    por_idade: tuple[tuple[str, int, int], ...]  # (Faixa de Idade, Chaves, Diferença absoluta), as 5 em ordem


def _reais_com_rs(centavos: int) -> str:
    """Centavos → `R$ 1.234,56`, ou `(1.234,56)` se negativo."""
    reais, resto = divmod(abs(centavos), 100)
    numero = f"{reais:,}".replace(",", ".") + f",{resto:02d}"
    return f"({numero})" if centavos < 0 else f"R$ {numero}"


def _reais_sem_milhar(centavos: int) -> str:
    """Centavos → `-1234,56`, sem separador de milhar."""
    sinal = "-" if centavos < 0 else ""
    reais, resto = divmod(abs(centavos), 100)
    return f"{sinal}{reais},{resto:02d}"


def _sem_chave(linhas: list[tuple[str, int]]) -> SemChave:
    return SemChave(linhas=len(linhas), soma=sum(valor for _, valor in linhas))


def _linhas_da_base(
    valores: dict[str, int], repetidas: list[str], sem_chave: list[tuple[str, int]]
) -> list[tuple[str, int]]:
    """Uma linha por Chave; as `repetidas` saem em duas linhas que somam o Valor, e as sem Chave vão no fim."""
    linhas, segundas = [], []
    for chave, valor in valores.items():
        if chave in repetidas:
            linhas.append((chave, valor // 3))
            segundas.append((chave, valor - valor // 3))
        else:
            linhas.append((chave, valor))
    return linhas + segundas + sem_chave


def _atributos_plantados(chave: str) -> tuple[dict[str, str | None], dict[str, str | None]]:
    """Os Atributos da Chave em A e em B, como {Atributo: valor}.

    O Produto fica vazio em A nas Chaves múltiplas de 7.
    As órfãs dentro da Tolerância e as linhas sem Chave não têm Atributo.
    """
    if not re.fullmatch(r"C\d{5}", chave):
        return {}, {}
    i = int(chave[1:])
    produto = PRODUTOS[i % len(PRODUTOS)]
    nas_duas = {"Carteira": "Legado" if _legado(i) else "Atual", "Moeda": "BRL"}
    return (
        {"Produto": None if i % 7 == 0 else produto, **nas_duas},
        {"Produto": produto, "Filial": f"{i % 5 + 1:02d}", **nas_duas},
    )


def _escrever_csv(
    caminho: Path, cabecalho: list[str], linhas: list[list[str | None]], codificacao: str = "utf-8-sig"
) -> None:
    """`.csv` separado por `;`, como o Excel salva no Brasil; vazio é campo vazio.

    `utf-8-sig` (com BOM) é o "CSV UTF-8" do Excel; `cp1252` é o "CSV (separado por vírgulas)".
    """
    with caminho.open("w", newline="", encoding=codificacao) as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cabecalho)
        w.writerows([["" if campo is None else campo for campo in linha] for linha in linhas])


def _escrever_nativo(caminho: Path, cabecalho: list[str], linhas: list[tuple], rejeitadas: list[tuple]) -> None:
    """`.xlsx` ou `.parquet` como o sistema exporta: Data como data, Valor como número em reais e Atributos em texto.

    Cada linha é (Chave, Data, Valor em centavos, *Atributos); as `rejeitadas` vão no fim, como estão.
    """
    linhas = [(chave, data, valor / 100, *atributos) for chave, data, valor, *atributos in linhas] + rejeitadas
    if caminho.suffix == ".parquet":
        colunas = list(zip(*linhas))
        pl.DataFrame({nome: list(coluna) for nome, coluna in zip(cabecalho, colunas)}).write_parquet(caminho)
        return
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet()
    ws.append(cabecalho)
    for linha in linhas:
        ws.append(list(linha))
    wb.save(caminho)


def _dias_uteis(inicio: date, fim: date) -> list[date]:
    dias = (inicio + timedelta(n) for n in range((fim - inicio).days + 1))
    return [d for d in dias if d.weekday() < 5]


def _data_do_excel(data: date) -> str:
    """Data → número de série do Excel, como `46295`."""
    return str((data - date(1899, 12, 30)).days)


def _digitos_trocados(sorteio: random.Random) -> tuple[int, int]:
    """Um valor e o mesmo com o dígito do milhar e o da centena trocados: a Diferença passa da Tolerância."""
    while True:
        valor = sorteio.randint(10_000, 10_000_000)
        texto = str(valor)
        trocado = int(texto[:-4] + texto[-3] + texto[-4] + texto[-2:])
        if trocado != valor:
            sinal = sorteio.choice([-1, 1])
            return sinal * valor, sinal * trocado


def _posicao(
    sorteio: random.Random, data: date
) -> tuple[dict[str, int], dict[str, int], dict[str, int], dict[str, str]]:
    """Uma Data-base: os valores de A e de B e as Diferenças plantadas acima da Tolerância e seus Tipos, por Chave."""
    a: dict[str, int] = {}
    b: dict[str, int] = {}
    diferencas: dict[str, int] = {}
    tipos: dict[str, str] = {}

    for i in range(1, N_CHAVES + 1):
        chave = f"C{i:05d}"
        valor = sorteio.choice([-1, 1, 1, 1]) * sorteio.randint(1_000, 10_000_000)
        caso = i % 10
        if caso == 1:  # Diferença acima da Tolerância, positiva ou negativa
            delta = sorteio.choice([-1, 1]) * sorteio.randint(TOLERANCIA + 1, 500_000)
            inicio, fim, na_pausa = PAUSAS.get(chave, (None, None, None))
            if inicio and inicio <= data <= fim:
                a[chave], b[chave] = valor, valor - na_pausa
            else:
                a[chave], b[chave] = valor, valor - delta
                diferencas[chave], tipos[chave] = delta, "Sem padrão"
        elif caso == 2:  # Diferença dentro da Tolerância
            a[chave], b[chave] = valor, valor - sorteio.randint(-TOLERANCIA, TOLERANCIA)
        elif caso == 3:  # Só em A
            a[chave] = valor
            diferencas[chave], tipos[chave] = valor, "Só em A"
        elif caso == 4:  # Só em B
            b[chave] = valor
            diferencas[chave], tipos[chave] = -valor, "Só em B"
        elif caso == 7:  # Sinal invertido
            a[chave], b[chave] = valor, -valor
            diferencas[chave], tipos[chave] = 2 * valor, "Sinal invertido"
        elif caso == 8:  # Duplicado, num sentido ou no outro
            a[chave], b[chave] = sorteio.choice([(2 * valor, valor), (valor, 2 * valor)])
            diferencas[chave], tipos[chave] = a[chave] - b[chave], "Duplicado"
        elif caso == 9:  # Vírgula deslocada, para mais ou para menos
            fator = sorteio.choice([10, 100, 1000])
            a[chave], b[chave] = sorteio.choice([(valor * fator, valor), (valor, valor * fator)])
            if _legado(i):  # a Vírgula deslocada da Carteira Legado
                a[chave], b[chave] = valor, valor * 1000
            diferencas[chave], tipos[chave] = a[chave] - b[chave], "Vírgula deslocada"
        elif caso == 0 and i % 20 == 10:  # Dígitos trocados
            a[chave], b[chave] = _digitos_trocados(sorteio)
            diferencas[chave], tipos[chave] = a[chave] - b[chave], "Dígitos trocados"
        elif caso == 0:  # Duplicado e Dígitos trocados: o dobro destes números tem os mesmos dígitos
            a[chave], b[chave] = sorteio.choice([(251_748, 125_874), (125_874, 251_748), (285_714, 142_857)])
            diferencas[chave] = a[chave] - b[chave]
            tipos[chave] = SEPARADOR_DE_TIPOS.join(["Duplicado", "Dígitos trocados"])
        else:
            a[chave] = b[chave] = valor

    # Órfãs dentro da Tolerância também não contam
    a["SO_A_CENTAVOS"] = TOLERANCIA
    b["SO_B_CENTAVOS"] = TOLERANCIA
    return a, b, diferencas, tipos


def _por_tipo(diferencas: dict[str, int], tipos: dict[str, str]) -> tuple[tuple[str, int, int], ...]:
    """(Tipo, Chaves, Diferença absoluta) de cada Tipo plantado, da maior para a menor Diferença absoluta.

    Uma Chave com mais de um Tipo conta em cada um.
    """
    soma: dict[str, tuple[int, int]] = {}
    for chave, diferenca in diferencas.items():
        for tipo in tipos[chave].split(SEPARADOR_DE_TIPOS):
            chaves, absoluta = soma.get(tipo, (0, 0))
            soma[tipo] = (chaves + 1, absoluta + abs(diferenca))
    return tuple(
        sorted(((tipo, chaves, absoluta) for tipo, (chaves, absoluta) in soma.items()), key=lambda t: (-t[2], t[0]))
    )


def _por_idade(diferencas: dict[str, int], aberta_desde: dict[str, date]) -> tuple[tuple[str, int, int], ...]:
    """(Faixa, Chaves, Diferença absoluta) das 5 faixas de Idade, em ordem, mesmo vazias."""
    tetos = {"Até 30 dias": 30, "31 a 90 dias": 90, "91 a 365 dias": 365, "366 dias a 5 anos": 1826}  # 5 anos
    soma = {faixa: (0, 0) for faixa in [*tetos, "Mais de 5 anos"]}
    for chave, diferenca in diferencas.items():
        idade = (DATA_BASE - aberta_desde[chave]).days
        faixa = next((faixa for faixa, teto in tetos.items() if idade <= teto), "Mais de 5 anos")
        chaves, absoluta = soma[faixa]
        soma[faixa] = (chaves + 1, absoluta + abs(diferenca))
    return tuple((faixa, chaves, absoluta) for faixa, (chaves, absoluta) in soma.items())


def _aberta_desde(chave: str, plantadas: dict[date, dict[str, int]]) -> date:
    """A primeira Data-base da sequência de Data-bases seguidas, até a mais recente, em que a Chave tem Diferença."""
    desde = DATA_BASE
    for data in reversed(list(plantadas)):
        if chave not in plantadas[data]:
            break
        desde = data
    return desde


def gerar_bases_exemplo(pasta: str | Path, formato: str = "csv") -> Gabarito:
    """Escreve `base_a` e `base_b` em `pasta`, no `formato` (`csv`, `xlsx` ou `parquet`), e devolve o gabarito.

    As bases são as mesmas em qualquer formato; muda só como a Data e o Valor estão gravados.
    """
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    sorteio = random.Random(42)  # sempre as mesmas bases

    posicoes_a: dict[date, dict[str, int]] = {}
    posicoes_b: dict[date, dict[str, int]] = {}
    plantadas: dict[date, dict[str, int]] = {}
    tipos_plantados: dict[date, dict[str, str]] = {}
    for data in _dias_uteis(PRIMEIRA_DATA_BASE, DATA_BASE):
        posicoes_a[data], posicoes_b[data], plantadas[data], tipos_plantados[data] = _posicao(sorteio, data)
    a, b, diferencas = posicoes_a[DATA_BASE], posicoes_b[DATA_BASE], plantadas[DATA_BASE]
    tipos = tipos_plantados[DATA_BASE]  # o Tipo do Erro só vale na Data-base mais recente
    _, posicoes_b[SO_NA_BASE_B], _, _ = _posicao(sorteio, SO_NA_BASE_B)

    aberta_desde = {chave: _aberta_desde(chave, plantadas) for chave in diferencas}

    base_a, base_b = pasta / f"base_a.{formato}", pasta / f"base_b.{formato}"
    # As linhas sem Chave se repetem em toda Data-base, como numa posição diária: nos totais e no aviso, só contam
    # as da mais recente; no Histórico, entram em cada Data-base comum.
    linhas_a = [
        (chave, data, valor, *map(_atributos_plantados(chave)[0].get, ATRIBUTOS_A))
        for data, valores in posicoes_a.items()
        for chave, valor in _linhas_da_base(valores, REPETIDAS_A, SEM_CHAVE_A)
    ]
    linhas_b = [
        (f" {chave} ", data, valor, *map(_atributos_plantados(chave)[1].get, ATRIBUTOS_B))
        for data, valores in posicoes_b.items()
        for chave, valor in _linhas_da_base(valores, REPETIDAS_B, SEM_CHAVE_B)
    ]
    rejeitadas_a = [] if formato == "parquet" else REJEITADAS_A
    sem_atributos_a, sem_atributos_b = [None] * len(ATRIBUTOS_A), [None] * len(ATRIBUTOS_B)
    if formato == "csv":
        _escrever_csv(
            base_a,
            CABECALHO_A,
            [[c, d.strftime("%d/%m/%Y"), _reais_com_rs(v), *at] for c, d, v, *at in linhas_a]
            + [[c, d, v, *sem_atributos_a] for c, d, v, _ in rejeitadas_a],
        )
        _escrever_csv(
            base_b,
            CABECALHO_B,
            [[c, _data_do_excel(d), _reais_sem_milhar(v), *at] for c, d, v, *at in linhas_b]
            + [[c, d.isoformat(), v, *sem_atributos_b] for c, d, v, _ in REJEITADAS_B],
            codificacao="cp1252",  # com os acentos do Produto (Crédito, Débito, Câmbio)
        )
    else:
        _escrever_nativo(base_a, CABECALHO_A, linhas_a, [(c, d, v, *sem_atributos_a) for c, d, v, _ in rejeitadas_a])
        _escrever_nativo(base_b, CABECALHO_B, linhas_b, [(c, d, v, *sem_atributos_b) for c, d, v, _ in REJEITADAS_B])
    # A Linha é a que o usuário vê: o cabeçalho é a linha 1, menos no `.parquet`, que não tem cabeçalho
    primeira_a = len(linhas_a) + (1 if formato == "parquet" else 2)
    primeira_b = len(linhas_b) + (1 if formato == "parquet" else 2)
    rejeitadas = [
        (nome, primeira + i, chave and chave.strip(), data if data is None else str(data), valor, motivo)
        for nome, primeira, plantadas in (("Base A", primeira_a, rejeitadas_a), ("Base B", primeira_b, REJEITADAS_B))
        for i, (chave, data, valor, motivo) in enumerate(plantadas)
    ]
    return Gabarito(
        base_a=base_a,
        base_b=base_b,
        data_base=DATA_BASE,
        total_a=sum(a.values()) + _sem_chave(SEM_CHAVE_A).soma,
        total_b=sum(b.values()) + _sem_chave(SEM_CHAVE_B).soma,
        diferenca_total=sum(diferencas.values()) + sum(DIFERENCAS_SEM_CHAVE),
        diferenca_absoluta=sum(abs(d) for d in [*diferencas.values(), *DIFERENCAS_SEM_CHAVE]),
        chaves_com_diferenca=len(diferencas),
        sem_chave_a=_sem_chave(SEM_CHAVE_A),
        sem_chave_b=_sem_chave(SEM_CHAVE_B),
        rejeitadas=tuple(rejeitadas),
        data_bases_so_em_b=(SO_NA_BASE_B,),
        historico=tuple(
            (data, sum(abs(d) for d in [*ds.values(), *DIFERENCAS_SEM_CHAVE])) for data, ds in plantadas.items()
        ),
        operacoes=tuple(
            sorted(
                ((chave, a.get(chave, 0), b.get(chave, 0), d, tipos[chave]) for chave, d in diferencas.items()),
                key=lambda op: (-abs(op[3]), op[0]),
            )
        ),
        por_tipo=_por_tipo(diferencas, tipos),
        por_idade=_por_idade(diferencas, aberta_desde),
        aberta_desde=aberta_desde,
        atributos={chave: _atributos_da_chave(chave, chave in a, chave in b) for chave in diferencas},
        por_atributo=_por_atributo(a, b, diferencas),
    )


def _atributos_da_chave(chave: str, em_a: bool, em_b: bool) -> dict[str, str | None]:
    """Cada Atributo de A ou, se vazio ou ausente, de B: primeiro os de A, depois os só de B (a Filial)."""
    de_a, de_b = _atributos_plantados(chave)
    nomes = dict.fromkeys(ATRIBUTOS_A + ATRIBUTOS_B)
    return {nome: (de_a.get(nome) if em_a else None) or (de_b.get(nome) if em_b else None) for nome in nomes}


def _por_atributo(
    a: dict[str, int], b: dict[str, int], diferencas: dict[str, int]
) -> tuple[tuple[str, str, int, float], ...]:
    """(Atributo, Valor, Diferença, Concentração) dos valores com alguma Diferença plantada.

    O peso de cada Chave no total é |A|, ou |B| quando A é zero ou ausente; a Concentração é a % da Diferença
    absoluta − a % do peso no total. Ordem: Diferença absoluta decrescente, depois Atributo e Valor.
    """
    pesos = {chave: abs(a.get(chave, 0)) or abs(b.get(chave, 0)) for chave in a.keys() | b.keys()}
    peso_total, absoluta_total = sum(pesos.values()), sum(abs(d) for d in diferencas.values())
    soma: dict[tuple[str, str], tuple[int, int, int, bool]] = {}
    for chave, peso in pesos.items():
        diferenca = diferencas.get(chave)
        for atributo, valor in _atributos_da_chave(chave, chave in a, chave in b).items():
            if valor is None:
                continue
            p, d, absoluta, com_diferenca = soma.get((atributo, valor), (0, 0, 0, False))
            soma[(atributo, valor)] = (
                p + peso,
                d + (diferenca or 0),
                absoluta + abs(diferenca or 0),
                com_diferenca or diferenca is not None,
            )
    linhas = sorted(
        (-absoluta, atributo, valor, d, absoluta / absoluta_total - p / peso_total)
        for (atributo, valor), (p, d, absoluta, com_diferenca) in soma.items()
        if com_diferenca
    )
    return tuple((atributo, valor, d, concentracao) for _, atributo, valor, d, concentracao in linhas)


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else "exemplo"
    formato = sys.argv[2] if len(sys.argv) > 2 else "csv"
    print(gerar_bases_exemplo(pasta, formato))
