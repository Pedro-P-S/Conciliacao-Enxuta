# Conciliação Enxuta

Duas bases que deviam ter os mesmos valores: a ferramenta mostra onde não batem, por quê e desde quando. Sai um `.xlsx` com 5 abas e o Resumo em `.html`, na pasta da Base A. A spec está em [docs/spec.md](docs/spec.md).

## Gerar o executável no Windows

1. Instale o Python 3.11 ou mais novo, de [python.org](https://www.python.org/downloads/). Na instalação, marque **Add python.exe to PATH**.
2. Baixe o projeto: em [github.com/Pedro-P-S/Conciliacao-Enxuta](https://github.com/Pedro-P-S/Conciliacao-Enxuta), clique em **Code › Download ZIP** e extraia o ZIP. Quem tem Git pode usar `git clone https://github.com/Pedro-P-S/Conciliacao-Enxuta.git`.
3. Na pasta extraída, dê dois cliques em `gerar_exe.bat`. Ele instala os pacotes e gera o executável; precisa de internet e leva alguns minutos.
4. O executável fica em `dist\ConciliacaoEnxuta\ConciliacaoEnxuta.exe`. Leve a pasta `dist\ConciliacaoEnxuta` inteira: o `.exe` precisa da pasta `_internal` ao lado.

## Usar

Abra o `ConciliacaoEnxuta.exe`, clique em **Procurar** para escolher a Base A e a Base B (`.xlsx`, `.csv` ou `.parquet`), confira a Tolerância e clique em **Conciliar**. O resultado sai na pasta da Base A, e o botão **Abrir pasta** abre essa pasta.

As colunas `Chave`, `Data` e `Valor` são reconhecidas pelo nome; as outras viram Atributo.
