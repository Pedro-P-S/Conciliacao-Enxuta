"""Gerador de bases de exemplo com gabarito.

As Diferenças são plantadas e o gabarito é montado a partir delas, sem passar pelo cruzamento.
Cada base traz uma posição por dia útil de seis meses, e a Base B traz ainda uma Data-base que a Base A não tem.
Uso: `python -m conciliacao_enxuta.exemplo [PASTA] [csv|xlsx|parquet]` (padrão: `exemplo` e `csv`).
"""

from __future__ import annotations

import csv
import random
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import openpyxl
import polars as pl

from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO as TOLERANCIA
from conciliacao_enxuta.cruzamento import SemChave

PRIMEIRA_DATA_BASE = date(2026, 4, 1)
DATA_BASE = date(2026, 9, 30)  # a mais recente comum às duas bases
SO_NA_BASE_B = date(2026, 10, 1)  # ignorada: a Base A não tem
N_CHAVES = 200

# Chaves gravadas em duas linhas, que o cruzamento tem de somar: uma sem Diferença e uma com
REPETIDAS_A = ["C00005", "C00011"]
REPETIDAS_B = ["C00006", "C00021"]
# Linhas sem Chave (vazia ou só espaço), que ficam fora do cruzamento
SEM_CHAVE_A = [("", 12_345), ("   ", -2_000)]
SEM_CHAVE_B = [("", 77_700)]


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
    data_bases_so_em_b: tuple[date, ...]
    historico: tuple[tuple[date, int], ...]  # (Data-base comum, Diferença absoluta), em ordem de data
    # (Chave, A, B, Diferença, Tipo do Erro), por |Diferença| decrescente
    operacoes: tuple[tuple[str, int, int, int, str], ...]
    por_tipo: tuple[tuple[str, int, int], ...]  # (Tipo do Erro, Chaves, Diferença absoluta), da maior para a menor


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


def _escrever_csv(caminho: Path, cabecalho: list[str], linhas: list[list[str]]) -> None:
    """`.csv` separado por `;` e com BOM, como o Excel salva no Brasil."""
    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cabecalho)
        w.writerows(linhas)


def _escrever_nativo(caminho: Path, cabecalho: list[str], linhas: list[tuple[str, date, int]]) -> None:
    """`.xlsx` ou `.parquet` como o sistema exporta: Data como data e Valor como número em reais."""
    if caminho.suffix == ".parquet":
        chaves, datas, valores = zip(*linhas)
        pl.DataFrame(
            {cabecalho[0]: chaves, cabecalho[1]: datas, cabecalho[2]: [v / 100 for v in valores]}
        ).write_parquet(caminho)
        return
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet()
    ws.append(cabecalho)
    for chave, data, valor in linhas:
        ws.append([chave, data, valor / 100])
    wb.save(caminho)


def _dias_uteis(inicio: date, fim: date) -> list[date]:
    dias = (inicio + timedelta(n) for n in range((fim - inicio).days + 1))
    return [d for d in dias if d.weekday() < 5]


def _data_do_excel(data: date) -> str:
    """Data → número de série do Excel, como `46295`."""
    return str((data - date(1899, 12, 30)).days)


def _posicao(
    sorteio: random.Random,
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
        else:
            a[chave] = b[chave] = valor

    # Órfãs dentro da Tolerância também não contam
    a["SO_A_CENTAVOS"] = TOLERANCIA
    b["SO_B_CENTAVOS"] = TOLERANCIA
    return a, b, diferencas, tipos


def _por_tipo(diferencas: dict[str, int], tipos: dict[str, str]) -> tuple[tuple[str, int, int], ...]:
    """(Tipo, Chaves, Diferença absoluta) de cada Tipo plantado, da maior para a menor Diferença absoluta."""
    soma: dict[str, tuple[int, int]] = {}
    for chave, diferenca in diferencas.items():
        chaves, absoluta = soma.get(tipos[chave], (0, 0))
        soma[tipos[chave]] = (chaves + 1, absoluta + abs(diferenca))
    return tuple(
        sorted(((tipo, chaves, absoluta) for tipo, (chaves, absoluta) in soma.items()), key=lambda t: (-t[2], t[0]))
    )


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
        posicoes_a[data], posicoes_b[data], plantadas[data], tipos_plantados[data] = _posicao(sorteio)
    a, b, diferencas = posicoes_a[DATA_BASE], posicoes_b[DATA_BASE], plantadas[DATA_BASE]
    tipos = tipos_plantados[DATA_BASE]  # o Tipo do Erro só vale na Data-base mais recente
    _, posicoes_b[SO_NA_BASE_B], _, _ = _posicao(sorteio)

    base_a, base_b = pasta / f"base_a.{formato}", pasta / f"base_b.{formato}"
    # Os nomes de coluna e os formatos variam de propósito, entre as bases e do nome exato.
    # As linhas sem Chave vão na Data-base mais recente; a Base B as repete na Data-base ignorada, onde não contam.
    cabecalho_a, cabecalho_b = ["CHAVE", "data", "Valor "], [" Chave", "DATA", "VALOR"]
    linhas_a = [
        (chave, data, valor)
        for data, valores in posicoes_a.items()
        for chave, valor in _linhas_da_base(valores, REPETIDAS_A, SEM_CHAVE_A if data == DATA_BASE else [])
    ]
    linhas_b = [
        (f" {chave} ", data, valor)
        for data, valores in posicoes_b.items()
        for chave, valor in _linhas_da_base(
            valores, REPETIDAS_B, SEM_CHAVE_B if data in (DATA_BASE, SO_NA_BASE_B) else []
        )
    ]
    if formato == "csv":
        _escrever_csv(base_a, cabecalho_a, [[c, d.strftime("%d/%m/%Y"), _reais_com_rs(v)] for c, d, v in linhas_a])
        _escrever_csv(base_b, cabecalho_b, [[c, _data_do_excel(d), _reais_sem_milhar(v)] for c, d, v in linhas_b])
    else:
        _escrever_nativo(base_a, cabecalho_a, linhas_a)
        _escrever_nativo(base_b, cabecalho_b, linhas_b)
    return Gabarito(
        base_a=base_a,
        base_b=base_b,
        data_base=DATA_BASE,
        total_a=sum(a.values()),
        total_b=sum(b.values()),
        diferenca_total=sum(diferencas.values()),
        diferenca_absoluta=sum(abs(d) for d in diferencas.values()),
        chaves_com_diferenca=len(diferencas),
        sem_chave_a=_sem_chave(SEM_CHAVE_A),
        sem_chave_b=_sem_chave(SEM_CHAVE_B),
        data_bases_so_em_b=(SO_NA_BASE_B,),
        historico=tuple((data, sum(abs(d) for d in ds.values())) for data, ds in plantadas.items()),
        operacoes=tuple(
            sorted(
                ((chave, a.get(chave, 0), b.get(chave, 0), d, tipos[chave]) for chave, d in diferencas.items()),
                key=lambda op: (-abs(op[3]), op[0]),
            )
        ),
        por_tipo=_por_tipo(diferencas, tipos),
    )


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else "exemplo"
    formato = sys.argv[2] if len(sys.argv) > 2 else "csv"
    print(gerar_bases_exemplo(pasta, formato))
