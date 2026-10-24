# 35: Tolerância no formato brasileiro

**What to build:** a Tolerância, na GUI e na CLI, é lida no formato brasileiro, com as mesmas regras de separador do Valor (`1.000` é R$ 1.000,00, `0,50` é R$ 0,50). Uma Tolerância que não vira número, ou grande demais, dá uma mensagem simples. O arredondamento dela para centavos fica como está. Ver spec: Interface (Tolerância), bloco "Decisões de 24/10/2026" (Tolerância), Testes/Correções da auditoria (de ponta a ponta); história 56.

**Blocked by:** 30, 32

**Status:** done

- [x] Teste de ponta a ponta, pela CLI e pelo `gui_estado`: `1.000` dá a Tolerância R$ 1.000,00 no Resumo; `0,50` dá R$ 0,50.
- [x] Teste de ponta a ponta: uma Tolerância inválida (`abc`, `1,234.56`) e uma grande demais dão mensagem simples, sem traceback.
- [x] O arredondamento da Tolerância para centavos não muda.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` com `--tolerancia 1.000` e conferir a Tolerância e as Chaves com Diferença na aba Resumo; rodar com `--tolerancia abc` e conferir a mensagem simples.

**Notas de entrega:**
- Seams (pela spec, "Seams dos testes"): a seam 2 de ponta a ponta, `main` da CLI e `conciliar_pela_janela` do `gui_estado`. Sem seam nova.
- `tolerancia_em_centavos` (no `cli`, usada pela CLI e pelo `gui_estado`) segue as regras de separador do Valor: com vírgula, a vírgula é decimal e o ponto só vale como milhar em grupos de 3 (`1.000,50`; `1,234.56` e `1.2,3` são inválidos); sem vírgula, `1.000` é milhar e `0.5` é decimal. Só dígitos e separadores: `1e3`, `Infinity` e `NaN` são inválidos.
- Acima de Int64 em centavos dá "Tolerância grande demais: ...". Antes, passava e a conciliação rodava com ela.
- O arredondamento continua o do `Decimal` (o meio vai para o par: `0,015` e `0,025` dão 2 centavos); há um teste que trava isso.
- O regex do milhar virou a constante `MILHAR` no `leitura`, usada pelo Valor e pela Tolerância.
- Teste com olhos de usuário em `exemplo\`: com `--tolerancia 1.000`, o Resumo mostra Tolerância 1.000 e 125 Chaves com Diferença (140 com a padrão); `--tolerancia abc` e `999999999999999999999` dão a mensagem simples do argparse, código 2, sem traceback.
- Arquivos: `conciliacao_enxuta/cli.py`, `conciliacao_enxuta/leitura.py`, `tests/test_ponta_a_ponta.py`, `tests/test_gui.py`.

**Onde está agora (depois da entrega):**
A leitura da Tolerância está em `tolerancia_em_centavos`, em `conciliacao_enxuta/cli.py`; o separador de milhar é `MILHAR`, em `conciliacao_enxuta/leitura.py`.
