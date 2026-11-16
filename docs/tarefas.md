# Tarefas e dependências

**Organização inicial: 16/11/2026.** Todas as tarefas abaixo foram abertas. O estado atualizado e a atribuição individual são mantidos nas issues, não nesta tabela estática.

- [Marco de 19/11 — benchmark inicial e protótipos](https://github.com/ceia-pdc-slms/lumi-lab/milestone/1).
- [Marco de 26/11 — variantes e comparação consolidada](https://github.com/ceia-pdc-slms/lumi-lab/milestone/2).
- [Todas as issues](https://github.com/ceia-pdc-slms/lumi-lab/issues).

As etiquetas `frente:*` identificam o time; `prioridade:*` distingue bloqueios de integração e demais entregas. Combine um responsável individual e um revisor antes de iniciar. Uma dependência bloqueia a conclusão da tarefa, mas não impede preparar trabalho em paralelo quando houver dados ou interfaces suficientes.

## Entrega de 19/11/2026

| Tarefa | Frente | Depende de |
|---|---|---|
| [#1 — Registrar entregas de 12/11 e fechar o contrato comum](https://github.com/ceia-pdc-slms/lumi-lab/issues/1) | Integração | — |
| [#2 — Preencher catálogo verificável e selecionar fontes](https://github.com/ceia-pdc-slms/lumi-lab/issues/2) | Dados e benchmark | — |
| [#3 — Versionar o recorte e os splits das duas trilhas](https://github.com/ceia-pdc-slms/lumi-lab/issues/3) | Dados e benchmark | [#1](https://github.com/ceia-pdc-slms/lumi-lab/issues/1), [#2](https://github.com/ceia-pdc-slms/lumi-lab/issues/2) |
| [#4 — Implementar avaliador e notebook das duas trilhas](https://github.com/ceia-pdc-slms/lumi-lab/issues/4) | Dados e benchmark | [#1](https://github.com/ceia-pdc-slms/lumi-lab/issues/1) |
| [#5 — Executar inferência do Lumi original](https://github.com/ceia-pdc-slms/lumi-lab/issues/5) | Adaptação e fine-tuning | — |
| [#6 — Executar referências: modelo pequeno e Lumi original](https://github.com/ceia-pdc-slms/lumi-lab/issues/6) | Dados e benchmark | [#3](https://github.com/ceia-pdc-slms/lumi-lab/issues/3), [#4](https://github.com/ceia-pdc-slms/lumi-lab/issues/4), [#5](https://github.com/ceia-pdc-slms/lumi-lab/issues/5) |
| [#7 — Comparar dois mecanismos e selecionar a abordagem](https://github.com/ceia-pdc-slms/lumi-lab/issues/7) | Adaptação e fine-tuning | [#1](https://github.com/ceia-pdc-slms/lumi-lab/issues/1), [#5](https://github.com/ceia-pdc-slms/lumi-lab/issues/5) |
| [#8 — Preparar dados e executar treino curto do pipeline](https://github.com/ceia-pdc-slms/lumi-lab/issues/8) | Adaptação e fine-tuning | [#1](https://github.com/ceia-pdc-slms/lumi-lab/issues/1), [#5](https://github.com/ceia-pdc-slms/lumi-lab/issues/5) |

## Entrega de 26/11/2026

| Tarefa | Frente | Depende de |
|---|---|---|
| [#9 — Consolidar a variante selecionada](https://github.com/ceia-pdc-slms/lumi-lab/issues/9) | Adaptação e fine-tuning | [#7](https://github.com/ceia-pdc-slms/lumi-lab/issues/7) |
| [#10 — Concluir o primeiro fine-tuning e entregar a variante](https://github.com/ceia-pdc-slms/lumi-lab/issues/10) | Adaptação e fine-tuning | [#8](https://github.com/ceia-pdc-slms/lumi-lab/issues/8) |
| [#11 — Conectar Decision e Reasoning ao avaliador](https://github.com/ceia-pdc-slms/lumi-lab/issues/11) | Integração | [#4](https://github.com/ceia-pdc-slms/lumi-lab/issues/4), [#9](https://github.com/ceia-pdc-slms/lumi-lab/issues/9), [#10](https://github.com/ceia-pdc-slms/lumi-lab/issues/10) |
| [#12 — Disponibilizar modelos e datasets públicos no Hugging Face](https://github.com/ceia-pdc-slms/lumi-lab/issues/12) | Publicação | [#3](https://github.com/ceia-pdc-slms/lumi-lab/issues/3), [#9](https://github.com/ceia-pdc-slms/lumi-lab/issues/9), [#10](https://github.com/ceia-pdc-slms/lumi-lab/issues/10) |
| [#13 — Executar variantes no teste fixado e comparar as quatro referências](https://github.com/ceia-pdc-slms/lumi-lab/issues/13) | Dados e benchmark | [#6](https://github.com/ceia-pdc-slms/lumi-lab/issues/6), [#11](https://github.com/ceia-pdc-slms/lumi-lab/issues/11) |
| [#14 — Consolidar relatório comparativo e análise de erros](https://github.com/ceia-pdc-slms/lumi-lab/issues/14) | Dados e benchmark | [#13](https://github.com/ceia-pdc-slms/lumi-lab/issues/13) |
| [#15 — Publicar página Lumi com progresso e benchmark](https://github.com/ceia-pdc-slms/lumi-lab/issues/15) | Publicação | [#6](https://github.com/ceia-pdc-slms/lumi-lab/issues/6), [#14](https://github.com/ceia-pdc-slms/lumi-lab/issues/14), [#12](https://github.com/ceia-pdc-slms/lumi-lab/issues/12) |
| [#16 — Fechar pacote reproduzível e release experimental](https://github.com/ceia-pdc-slms/lumi-lab/issues/16) | Integração | [#12](https://github.com/ceia-pdc-slms/lumi-lab/issues/12), [#14](https://github.com/ceia-pdc-slms/lumi-lab/issues/14), [#15](https://github.com/ceia-pdc-slms/lumi-lab/issues/15) |

## Caminho principal de integração

Contrato e fontes → dados/avaliador → referências de 19/11. Em paralelo, inferência do Lumi → protótipos de decisão e treino curto → variantes candidatas → integração → comparação → relatório → página e pacote final.

A publicação dos artefatos no Hugging Face avança em paralelo à integração, usando as revisões candidatas. A página pode começar com as referências de 19/11, mas só é concluída com os resultados consolidados.

Critérios e evidências estão em cada issue. Use o [guia de contribuição](../CONTRIBUTING.md) e o [planejamento completo](planejamento/entregas-novembro-2026.md).
