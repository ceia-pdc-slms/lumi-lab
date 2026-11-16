# Entregas de novembro de 2026

O [planejamento completo](planejamento/entregas-novembro-2026.md) define os requisitos. Esta página conecta as entregas às tarefas do repositório. **A criação das tarefas não significa que a pesquisa foi executada ou concluída.**

## Até 19/11 — benchmark inicial e protótipos

[Marco no GitHub](https://github.com/ceia-pdc-slms/lumi-lab/milestone/1) · [Índice das oito tarefas](tarefas.md)

| Frente | Evidência de entrega |
|---|---|
| Integração | Materiais de 12/11 localizados e contrato revisado pelas duas frentes ([#1](https://github.com/ceia-pdc-slms/lumi-lab/issues/1)) |
| Dados | Catálogo de fontes e recorte versionado com splits e rastreabilidade ([#2](https://github.com/ceia-pdc-slms/lumi-lab/issues/2), [#3](https://github.com/ceia-pdc-slms/lumi-lab/issues/3)) |
| Benchmark | Código e notebook executado cobrindo as duas trilhas; predições e relatório do modelo pequeno e Lumi original ([#4](https://github.com/ceia-pdc-slms/lumi-lab/issues/4), [#6](https://github.com/ceia-pdc-slms/lumi-lab/issues/6)) |
| Adaptação | Notebook de inferência do Lumi, pelo menos dois mecanismos de decisão comparados em desenvolvimento e seleção fundamentada ([#5](https://github.com/ceia-pdc-slms/lumi-lab/issues/5), [#7](https://github.com/ceia-pdc-slms/lumi-lab/issues/7)) |
| Reasoning | Dados preparados, pipeline configurado e treino curto com carga/inferência de verificação ([#8](https://github.com/ceia-pdc-slms/lumi-lab/issues/8)) |

## Até 26/11 — variantes e comparação consolidada

[Marco no GitHub](https://github.com/ceia-pdc-slms/lumi-lab/milestone/2) · [Índice das oito tarefas](tarefas.md)

| Frente | Evidência de entrega |
|---|---|
| Adaptação | Decision consolidado e primeiro fine-tuning de Reasoning concluído, com tarefas suportadas e instruções ([#9](https://github.com/ceia-pdc-slms/lumi-lab/issues/9), [#10](https://github.com/ceia-pdc-slms/lumi-lab/issues/10)) |
| Integração | Adaptadores e versões candidatas funcionando com o avaliador ([#11](https://github.com/ceia-pdc-slms/lumi-lab/issues/11)) |
| Publicação | Pesos/artefatos e datasets públicos no Hugging Face com revisões e documentação ([#12](https://github.com/ceia-pdc-slms/lumi-lab/issues/12)) |
| Benchmark | Variantes no mesmo teste das referências, métricas separadas e relatório com análise de erros/recursos ([#13](https://github.com/ceia-pdc-slms/lumi-lab/issues/13), [#14](https://github.com/ceia-pdc-slms/lumi-lab/issues/14)) |
| Divulgação e pacote | Página Lumi no hub e release experimental reproduzível ([#15](https://github.com/ceia-pdc-slms/lumi-lab/issues/15), [#16](https://github.com/ceia-pdc-slms/lumi-lab/issues/16)) |

## Sequência operacional

Datas em **America/Sao_Paulo**; o horário das reuniões não foi definido nesta preparação.

| Data | Prioridade |
|---|---|
| 16–17/11 | Inventariar entregas de 12/11, assumir tarefas e fechar contrato/recorte |
| Até 18/11 | Fazer uma execução pequena de integração; identificar a versão do teste e as regras |
| 19/11 | Apresentar evidências do marco inicial e registrar pendências |
| Até 24/11 | Meta de disponibilização das variantes candidatas para integração e avaliação |
| 25/11 | Consolidar execuções, revisar falhas e conferir tabelas |
| 26/11 | Apresentar comparação, limitações e pacote experimental |

A composição do teste e a pontuação devem estar fixadas antes da comparação; correções posteriores são versionadas e aplicadas igualmente aos modelos afetados. O teste é público e não deve orientar o ajuste das variantes. Ausência de ganho sobre o Lumi original é resultado válido quando documentado.

## Aceite dos marcos

Fechar uma issue somente quando os critérios estiverem atendidos e a evidência estiver vinculada. No fechamento do marco, conferir código, notebooks executados, revisões dos artefatos, predições e relatórios; pendências permanecem explícitas. As issues são a fonte do estado atualizado.
