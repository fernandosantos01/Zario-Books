# Tradutor de Metadados — Plugin para Calibre

Plugin para o [Calibre](https://calibre-ebook.com/) que traduz automaticamente os metadados de livros e HQs do inglês para português (PT-BR), usando a API pública de tradução do Google.

Nasceu de um problema bem específico: ao baixar metadados de HQs via Calibre (Google Books, Amazon, etc.), sinopse, título e idioma costumam vir em inglês — mesmo quando a obra em si está em português. Esse plugin resolve isso com um clique.

## Funcionalidades

- **Sinopse**: traduzida automaticamente e aplicada direto, sem necessidade de confirmação.
- **Idioma**: alterado automaticamente para `por` (português) sempre que a sinopse é traduzida com sucesso.
- **Título**: traduzido, mas só aplicado após confirmação manual — um diálogo mostra o título original e a sugestão de tradução, permitindo aceitar, editar ou manter o original. Isso evita substituir nomes oficiais de obras por traduções literais incorretas.
- **Suporte a múltiplos livros**: selecione vários livros/HQs de uma vez; o plugin processa todos e mostra um resumo no final.
- **Não bloqueia a interface**: as traduções rodam em threads separadas (`QThread`), então o Calibre continua responsivo durante o processo.

## Instalação

### Opção 1 — Baixar o `.zip` já empacotado

1. Baixe o arquivo `TradutorMetadados.zip` da [última release](../../releases) (ou da raiz deste repositório).
2. No Calibre, vá em **Preferências → Plugins → Carregar plugin de arquivo** e selecione o `.zip`.
3. Reinicie o Calibre.
4. Vá em **Preferências → Toolbars & menus**, selecione a barra de ferramentas principal, encontre **"Traduzir Metadados"** na lista de ações disponíveis e arraste para a barra.

### Opção 2 — Build manual a partir do código fonte

```bash
git clone https://github.com/fernandosantos01/Zario-Books.git
cd tradutor-metadados-calibre/tradutor_metadados

# empacota em zip
zip -r ../TradutorMetadados.zip __init__.py main.py icon.png plugin-import-name-tradutor_metadados.txt

# instala no Calibre
calibre-customize -a ../TradutorMetadados.zip
```

## Como usar

1. Selecione um ou mais livros/HQs na biblioteca do Calibre (eles precisam ter uma sinopse preenchida).
2. Clique no botão **"Traduzir Metadados"** na barra de ferramentas, ou use o atalho `Ctrl+T`.
3. A sinopse e o idioma são traduzidos e aplicados automaticamente.
4. Para cada livro com título traduzível, um diálogo aparece perguntando se você quer usar a tradução sugerida (editável), ou manter o título original.
5. Ao final, um resumo mostra quantas traduções tiveram sucesso e se houve algum erro.

## Estrutura do projeto

```
tradutor_metadados/
├── __init__.py                                  # Metadados do plugin (nome, versão, autor)
├── main.py                                      # Lógica principal: tradução, threading, UI
├── icon.png                                     # Ícone do botão na toolbar
└── plugin-import-name-tradutor_metadados.txt    # Nome do pacote interno exigido pelo Calibre
```

### Detalhes técnicos relevantes

- A tradução usa o endpoint não-oficial `translate.googleapis.com/translate_a/single` (parâmetro `client=gtx`). É gratuito, mas não tem SLA — pode mudar de comportamento sem aviso.
- O ícone do botão **não** é resolvido automaticamente a partir de `action_spec`; ele é carregado manualmente em `genesis()` via `get_icons()`, conforme a API atual do Calibre exige.
- HTML da sinopse é simplificado (tags removidas) antes da tradução e reconstituído como um único parágrafo `<p>` depois — parágrafos múltiplos no original são colapsados em um só.

## Limitações conhecidas

- Depende de um endpoint não-oficial do Google, sem garantia de disponibilidade contínua.
- Sinopses com múltiplos parágrafos HTML perdem a formatação original (ver "Detalhes técnicos" acima).
- Sem cache: se você traduzir o mesmo livro duas vezes, duas requisições são feitas.
- O título traduzido é sugestão automática (tradução literal) — pode não corresponder ao título oficial de mercado da obra em português. Por isso a confirmação manual é obrigatória para esse campo.

## Compatibilidade

- Testado em Calibre 9.9, Linux.
- Requer Calibre 2.0.0 ou superior (`minimum_calibre_version`).

## Contribuindo

Sugestões e PRs são bem-vindos. Algumas ideias de melhorias futuras:
- Preservar parágrafos múltiplos da sinopse original.
- Cache de traduções já feitas.
- Suporte a outros pares de idioma além de inglês → português.
- Fallback para a API oficial do Google Cloud Translation.

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

## Autor

Criado por [José Fernando] ([@fernandosantos01]((https://github.com/fernandosantos01))).