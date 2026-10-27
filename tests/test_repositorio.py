"""Checagens do repositório que o pre-commit roda: o que o reviewer pegaria tarde, pego cedo."""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def test_tickets_sem_caractere_de_controle():
    # Um `\b` ou `\v` de caminho do Windows escrito por script vira caractere de controle e quebra o caminho
    controle = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
    quebrados = [p.name for p in (RAIZ / ".scratch" / "enxuto" / "issues").glob("*.md")
                 if controle.search(p.read_text(encoding="utf-8"))]
    assert quebrados == []


def test_python_linha_a_linha_na_leitura_tem_shortcut():
    # map_batches/map_elements dentro de uma expressão que o polars repete já deixou a leitura 100 vezes mais lenta
    linhas = (RAIZ / "conciliacao_enxuta" / "leitura.py").read_text(encoding="utf-8").splitlines()
    sem_aviso = [n + 1 for n, linha in enumerate(linhas)
                 if re.search(r"\.map_(batches|elements)\(", linha) and "shortcut:" not in linhas[n - 1]]
    assert sem_aviso == []
