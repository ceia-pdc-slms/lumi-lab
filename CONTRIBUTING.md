# Como contribuir

## 1. Escolha e combine a tarefa

Comece pelo [índice de tarefas](docs/tarefas.md). Cada issue tem uma frente, marco, critérios de aceite e dependências. Registre na issue quem será o responsável individual e quem revisará. Se faltar uma entrega de 12/11, vincule o material existente ou explicite a pendência; não marque como concluída sem evidência.

Os dois trios compartilham o contrato de avaliação. Uma mudança em entradas, saídas, splits, métricas ou regras de correção exige revisão das duas frentes antes de integrar.

Os seis integrantes receberam convites de escrita no repositório. Aceite o convite no GitHub antes de enviar branches para este repo; se o acesso ainda não estiver ativo, avise Lucca na própria organização.

## 2. Trabalhe em uma branch por tarefa

```bash
git clone https://github.com/ceia-pdc-slms/lumi-lab.git
cd lumi-lab
git switch main
git pull --ff-only
git switch -c seu-nome/issue-N-assunto
```

Substitua `seu-nome`, `N` e `assunto`. Faça alterações na pasta do componente correspondente; não crie cópias completas do projeto por time.

```bash
git add caminho/dos/arquivos
git commit -m "docs: descreve a entrega da tarefa N"
git push -u origin HEAD
```

Abra um PR para `main`, com `Closes #N` quando ele cumprir toda a tarefa. Para entregas parciais, use `Refs #N`. Evite commits diretos na `main`.

## 3. Entregue evidência revisável

O PR deve explicar a mudança, como reproduzi-la, o que foi executado e as limitações. Inclua os comandos e resultados da verificação. Não declare inferência, treinamento ou comparação executados quando apenas preparou código/configuração.

- Mudanças de documentação: confira links, datas e comandos.
- Dados: registre fonte, versão, licença, idioma, transformações, deduplicação e split.
- Avaliador/adaptadores: cubra parsing, respostas inválidas, ferramenta errada, argumentos errados e falhas de execução com testes adequados.
- Treinamento/inferência: registre ambiente, configuração, modelo-base, revisões e artefatos.
- Resultados: mantenha predições e procedência suficientes para recalcular métricas.

Use notebooks como demonstrações do pipeline compartilhado, com saídas executadas e descrição de como reproduzir. Limpe tokens, credenciais, caminhos pessoais e saídas irrelevantes antes de enviar.

## 4. Revise e integre

Solicite revisão de pelo menos uma pessoa da frente correspondente. Mudanças no contrato e em critérios de avaliação também precisam de alguém da outra frente. Lucca coordena a integração e o fechamento dos marcos.

`CODEOWNERS` solicita revisão da coordenação. As sugestões por componente estão comentadas até os integrantes aceitarem seus convites e terem acesso de escrita confirmado. A existência do arquivo, sozinha, não substitui revisão nem garante proteção de branch. Se a implementação mudar após uma aprovação, peça nova revisão do trecho alterado.

## Regras de avaliação

- Use treino para ajustar pesos, desenvolvimento para escolher prompts/métodos e teste para avaliação.
- Os dados são públicos; essa separação é metodológica, não um controle de acesso.
- Fixe IDs, revisões e regras antes da comparação final. Uma correção do avaliador deve ser versionada e aplicada igualmente a todos os modelos afetados.
- Mantenha os resultados das duas trilhas separados. Não exclua respostas inválidas do denominador para melhorar a pontuação.
- Mostre tarefas não suportadas e cobertura. Não transforme ausência de suporte em resultado comparável sem uma regra explícita.
- Documente diferenças de hardware, runtime, quantização e orçamento de geração. Não apresente medições de velocidade em condições diferentes como equivalentes.

## Publicação

O trabalho é público. Pesos, adaptadores e datasets são publicados no Hugging Face com versões e documentação; registre os links no repo. O hub recebe resultados exportados pelo avaliador e revisados pelo time. Veja o [guia de publicação](docs/huggingface.md).

Não envie senhas, tokens, chaves, caches de modelos ou grandes binários para o Git. Modelos abertos não exigem armazenar os pesos dentro deste repositório.
