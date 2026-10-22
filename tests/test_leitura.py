"""Leitura de `.csv` simples: o Valor vira centavos exatos."""

from conciliacao_enxuta.leitura import ler_base


def test_valor_vira_centavos_exatos_mesmo_em_valores_grandes(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(
        "Chave,Data,Valor\n 1 ,2026-09-30,0.29\n2,2026-09-30,-1234.56\n3,2026-09-30,92233720368547.75\n",
        encoding="utf-8",
    )

    base = ler_base(caminho)

    assert base["Chave"].to_list() == ["1", "2", "3"]
    assert base["Valor"].to_list() == [29, -123_456, 9_223_372_036_854_775]
