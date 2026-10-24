# 35: Tolerância no formato brasileiro

**What to build:** a Tolerância, na GUI e na CLI, é lida no formato brasileiro, com as mesmas regras de separador do Valor (`1.000` é R$ 1.000,00, `0,50` é R$ 0,50). Uma Tolerância que não vira número, ou grande demais, dá uma mensagem simples. O arredondamento dela para centavos fica como está. Ver spec: Interface (Tolerância), bloco "Decisões de 24/10/2026" (Tolerância), Testes/Correções da auditoria (de ponta a ponta); história 56.

**Blocked by:** 30, 32

**Status:** ready-for-agent

- [ ] Teste de ponta a ponta, pela CLI e pelo `gui_estado`: `1.000` dá a Tolerância R$ 1.000,00 no Resumo; `0,50` dá R$ 0,50.
- [ ] Teste de ponta a ponta: uma Tolerância inválida (`abc`, `1,234.56`) e uma grande demais dão mensagem simples, sem traceback.
- [ ] O arredondamento da Tolerância para centavos não muda.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` com `--tolerancia 1.000` e conferir a Tolerância e as Chaves com Diferença na aba Resumo; rodar com `--tolerancia abc` e conferir a mensagem simples.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
