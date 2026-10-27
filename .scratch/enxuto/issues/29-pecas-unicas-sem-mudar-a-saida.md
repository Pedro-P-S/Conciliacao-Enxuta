# 29: Peças únicas, sem mudar a saída

**What to build:** prefatoração das correções da auditoria, sem mudar o que o usuário vê (a não ser o gerador de exemplo). O `excel` expõe `quadro_do_resumo(resultado)`, os rótulos e os valores do quadro do Resumo, e o Excel e o HTML passam a usá-lo no lugar de cada um juntar rótulos e valores. O corte por limite e o seu aviso ficam numa função só, usada pelas Operações e pelos Erros. Os reais formatados como texto (`1.234,56`) saem de uma função só, usada pela leitura, pelo Excel e pelo HTML. A regra de sinal da linha sem Chave (+Valor na Base A, −Valor na Base B) fica num lugar só no `cruzamento`. O comentário do `excel` e do `html` diz que são os únicos lugares onde os centavos viram reais. O gerador de bases de exemplo aceita o formato sem diferenciar maiúscula (`"CSV"` grava `.csv`). Ver spec: Decisões de implementação (Módulos: `cruzamento`, `excel`, gerador de exemplo), bloco "Decisões de 24/10/2026: correções da auditoria" (Implementação), Testes/Correções da auditoria (o gerador).

**Blocked by:** —

**Status:** done

- [x] `quadro_do_resumo(resultado)` existe no `excel` e é a única fonte dos rótulos e valores do quadro, no Excel e no HTML.
- [x] O corte por limite e o aviso de corte saem de uma função só, usada pelas abas Operações com Diferença e Erros.
- [x] Os reais em texto saem de uma função só, usada pela leitura (Valor das Linhas rejeitadas), pelo Excel (Linha sem Chave) e pelo HTML.
- [x] A regra de sinal da linha sem Chave está num lugar só no `cruzamento`, usada por todas as contas que a precisam.
- [x] O comentário do `excel` e do `html` diz que são os únicos lugares onde os centavos viram reais.
- [x] Teste: o gerador de exemplo com o formato `"CSV"` grava `.csv`.
- [x] Os testes que já existem passam sem mudar o que conferem: `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q`.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` antes e depois da mudança e conferir que a aba Resumo, as abas Operações com Diferença e Erros e o `.html` mostram os mesmos números e textos.

**Notas de entrega:**
- Seams (escolhidas pela spec, sem acesso ao usuário: "as que já existem, sem seam nova"): `gerar_bases_exemplo` para o teste novo do formato; a Seam 2 (CLI → `.xlsx` e `.html`) e a leitura guardam a prefatoração, sem mudar o que conferem.
- Teste novo (vermelho antes, verde depois): `test_gerador_de_exemplo_aceita_o_formato_em_maiuscula` em `tests/test_ponta_a_ponta.py`. O gerador passa o `formato` a minúscula.
- `conciliacao_enxuta/excel.py`: `quadro_do_resumo(resultado)` devolve (rótulo, valor no Excel, formato, texto) e substitui `ROTULOS_DO_QUADRO`; o Resumo do Excel usa valor e formato, o HTML usa o texto. `cortar(tabela, limite, aviso)` corta e preenche o aviso (`CORTE_DAS_OPERACOES` ou `CORTE_DOS_ERROS`), usada pelas abas Operações com Diferença e Erros e pelo aviso do Resumo; `_aviso_na_linha_1` escreve o aviso e devolve a linha do cabeçalho. Saiu `aviso_de_corte`. O comentário do módulo diz que ele e o `html` são os únicos lugares onde os centavos viram reais.
- `conciliacao_enxuta/html.py`: o quadro vem de `quadro_do_resumo`; o comentário do módulo diz o mesmo do `excel`.
- `conciliacao_enxuta/leitura.py`: saiu `_em_reais`; o Valor lido das Linhas rejeitadas sai de `excel.reais`, aplicado só às rejeitadas (depois do filtro), não à base toda.
- `conciliacao_enxuta/cruzamento.py`: `_soltas` é o único lugar da regra de sinal (+Valor em A, −Valor em B); a Diferença, o Histórico, a Idade e o `_casas` (que agora recebe as soltas e usa −Diferença como alvo) saem dela.
- Teste com olhos de usuário: um script fora do repositório rodou as bases de `exemplo\` (raiz, `caso_entrada_estranha`, `caso_sem_chave`, `revisao`), com o limite padrão e com limite 3 (para o corte das Operações e dos Erros), e despejou cada célula (valor, formato, negrito), o congelamento, o filtro e o `.html`. Antes e depois deram textos idênticos; a CLI sobre `exemplo\base_a.csv` e `base_b.csv` deu o mesmo `.html` byte a byte.
- pytest: 212 passed.

**Onde está agora (depois da entrega):**
Prefatoração entregue sem mudar a saída; os tickets 30 a 37 podem usar `quadro_do_resumo`, `cortar`, `excel.reais` e `_soltas`. Nada commitado.
