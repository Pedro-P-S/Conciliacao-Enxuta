"""Gerador de bases de exemplo com gabarito.

As Diferenças são plantadas e o gabarito é montado a partir delas, sem passar pelo cruzamento.
Cada base traz uma posição por dia útil de seis meses, e a Base B traz ainda uma Data-base que a Base A não tem.
Uso: `python -m conciliacao_enxuta.exemplo [PASTA]` (padrão: `exemplo`).
"""

from __future__ import annotations

import csv
import random
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

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


def _linhas_do_csv(
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


def _escrever(caminho: Path, cabecalho: list[str], linhas: list[list[str]]) -> None:
    """`.csv` separado por `;` e com BOM, como o Excel salva no Brasil."""
    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cabecalho)
        w.writerows(linhas)


def _dias_uteis(inicio: date, fim: date) -> list[date]:
    dias = (inicio + timedelta(n) for n in range((fim - inicio).days + 1))
    return [d for d in dias if d.weekday() < 5]


def _data_do_excel(data: date) -> str:
    """Data → número de série do Excel, como `46295`."""
    return str((data - date(1899, 12, 30)).days)


def _posicao(sorteio: random.Random) -> tuple[dict[str, int], dict[str, int], list[int]]:
    """Uma Data-base: os valores de A e de B e as Diferenças plantadas acima da Tolerância."""
    a: dict[str, int] = {}
    b: dict[str, int] = {}
    diferencas: list[int] = []

    for i in range(1, N_CHAVES + 1):
        chave = f"C{i:05d}"
        valor = sorteio.choice([-1, 1, 1, 1]) * sorteio.randint(1_000, 10_000_000)
        caso = i % 10
        if caso == 1:  # Diferença acima da Tolerância, positiva ou negativa
            delta = sorteio.choice([-1, 1]) * sorteio.randint(TOLERANCIA + 1, 500_000)
            a[chave], b[chave] = valor, valor - delta
            diferencas.append(delta)
        elif caso == 2:  # Diferença dentro da Tolerância
            a[chave], b[chave] = valor, valor - sorteio.randint(-TOLERANCIA, TOLERANCIA)
        elif caso == 3:  # Só em A
            a[chave] = valor
            diferencas.append(valor)
        elif caso == 4:  # Só em B
            b[chave] = valor
            diferencas.append(-valor)
        else:
            a[chave] = b[chave] = valor

    # Órfãs dentro da Tolerância também não contam
    a["SO_A_CENTAVOS"] = TOLERANCIA
    b["SO_B_CENTAVOS"] = TOLERANCIA
    return a, b, diferencas


def gerar_bases_exemplo(pasta: str | Path) -> Gabarito:
    """Escreve `base_a.csv` e `base_b.csv` em `pasta` e devolve o gabarito."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    sorteio = random.Random(42)  # sempre as mesmas bases

    posicoes_a: dict[date, dict[str, int]] = {}
    posicoes_b: dict[date, dict[str, int]] = {}
    plantadas: dict[date, list[int]] = {}
    for data in _dias_uteis(PRIMEIRA_DATA_BASE, DATA_BASE):
        posicoes_a[data], posicoes_b[data], plantadas[data] = _posicao(sorteio)
    a, b, diferencas = posicoes_a[DATA_BASE], posicoes_b[DATA_BASE], plantadas[DATA_BASE]
    _, posicoes_b[SO_NA_BASE_B], _ = _posicao(sorteio)

    base_a, base_b = pasta / "base_a.csv", pasta / "base_b.csv"
    # Os nomes de coluna e os formatos variam de propósito, entre as bases e do nome exato.
    # As linhas sem Chave vão na Data-base mais recente; a Base B as repete na Data-base ignorada, onde não contam.
    _escrever(
        base_a,
        ["CHAVE", "data", "Valor "],
        [
            [chave, data.strftime("%d/%m/%Y"), _reais_com_rs(valor)]
            for data, valores in posicoes_a.items()
            for chave, valor in _linhas_do_csv(valores, REPETIDAS_A, SEM_CHAVE_A if data == DATA_BASE else [])
        ],
    )
    _escrever(
        base_b,
        [" Chave", "DATA", "VALOR"],
        [
            [f" {chave} ", _data_do_excel(data), _reais_sem_milhar(valor)]
            for data, valores in posicoes_b.items()
            for chave, valor in _linhas_do_csv(
                valores, REPETIDAS_B, SEM_CHAVE_B if data in (DATA_BASE, SO_NA_BASE_B) else []
            )
        ],
    )
    return Gabarito(
        base_a=base_a,
        base_b=base_b,
        data_base=DATA_BASE,
        total_a=sum(a.values()),
        total_b=sum(b.values()),
        diferenca_total=sum(diferencas),
        diferenca_absoluta=sum(abs(d) for d in diferencas),
        chaves_com_diferenca=len(diferencas),
        sem_chave_a=_sem_chave(SEM_CHAVE_A),
        sem_chave_b=_sem_chave(SEM_CHAVE_B),
        data_bases_so_em_b=(SO_NA_BASE_B,),
        historico=tuple((data, sum(abs(d) for d in ds)) for data, ds in plantadas.items()),
    )


if __name__ == "__main__":
    print(gerar_bases_exemplo(sys.argv[1] if len(sys.argv) > 1 else "exemplo"))
