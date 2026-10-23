"""Gerador de bases de exemplo com gabarito.

As Diferenças são plantadas e o gabarito é montado a partir delas, sem passar pelo cruzamento.
Uso: `python -m conciliacao_enxuta.exemplo [PASTA]` (padrão: `exemplo`).
"""

from __future__ import annotations

import csv
import random
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO as TOLERANCIA

DATA_BASE = date(2026, 9, 30)
N_CHAVES = 200


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


def _escrever(caminho: Path, cabecalho: list[str], linhas: list[list[str]]) -> None:
    """`.csv` separado por `;` e com BOM, como o Excel salva no Brasil."""
    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cabecalho)
        w.writerows(linhas)


def gerar_bases_exemplo(pasta: str | Path) -> Gabarito:
    """Escreve `base_a.csv` e `base_b.csv` em `pasta` e devolve o gabarito."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    sorteio = random.Random(42)  # sempre as mesmas bases

    a: dict[str, int] = {}
    b: dict[str, int] = {}
    diferencas: list[int] = []  # as plantadas acima da Tolerância

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

    base_a, base_b = pasta / "base_a.csv", pasta / "base_b.csv"
    # Os nomes de coluna e os formatos variam de propósito, entre as bases e do nome exato
    _escrever(
        base_a,
        ["CHAVE", "data", "Valor "],
        [[chave, DATA_BASE.strftime("%d/%m/%Y"), _reais_com_rs(valor)] for chave, valor in a.items()],
    )
    data_do_excel = str((DATA_BASE - date(1899, 12, 30)).days)
    _escrever(
        base_b,
        [" Chave", "DATA", "VALOR"],
        [[f" {chave} ", data_do_excel, _reais_sem_milhar(valor)] for chave, valor in b.items()],
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
    )


if __name__ == "__main__":
    print(gerar_bases_exemplo(sys.argv[1] if len(sys.argv) > 1 else "exemplo"))
