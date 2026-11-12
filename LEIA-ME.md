# Central Robótica — site de notícias de robótica

Reúne as principais notícias de robótica do mundo, todos os dias, em português.
Paleta vermelho e preto, fonte Orbitron.

## Guias do site

- **Destaques** — as notícias do dia: destaques grandes no topo e notícias menores abaixo.
  Lançamentos de robôs sempre têm prioridade.
- **Lançamentos** e categorias: Humanoides · Cães-robô e Quadrúpedes · Industriais · Drones ·
  Casa e Serviço · Medicina · Veículos Autônomos · Espaço e Oceano · IA e Pesquisa · Negócios.
- **Hoje / Dia / Semana / Mês / Ano** + **Arquivo** lateral — histórico completo, nada é apagado.
- **Catálogo de robôs** — todos os robôs separados por tipo, com status, ano e as notícias de cada um.
- **Fabricantes** — as principais fabricantes do mundo e seus robôs.
- **Sites especializados** — os principais sites de robótica do mundo e as últimas notícias de cada um.
- **Curiosidades** — curiosidade do dia, "Você sabia?", matérias e documentários.
- **História da robótica** — linha do tempo da Antiguidade até hoje.

## Atualização automática (gerenciador)

`coletor/gerenciador.py` roda a coleta completa: lê ~60 fontes do mundo todo (Brasil, EUA,
Europa, América Latina, China, Japão, Coreia), traduz para o português, classifica por tipo de
robô, prioriza lançamentos, busca a imagem de destaque e o link do site original de cada notícia,
marca curiosidades e documentários, atualiza os marcos da História e grava o status no site.

Tudo se atualiza sozinho:
- **Notícias, arquivo e lançamentos** — a cada coleta.
- **Curiosidades** — a "curiosidade do dia" muda todo dia; matérias e documentários chegam a cada coleta.
- **História** — os "marcos recentes" de cada mês são gerados a partir dos lançamentos mais citados.
- **Catálogo / Fabricantes / Sites** — contagem de notícias, última notícia e foto de cada robô.
- **A página aberta** avisa quando chegam notícias novas e vira o dia sozinha à meia-noite.

### No seu computador
Dê dois cliques em **`instalar_gerenciador.bat`**: cria a tarefa "Central Robotica - Atualizar
noticias" no Agendador de Tarefas do Windows, de hora em hora, sem abrir janela. Se o PC estiver
desligado no horário, roda assim que ligar. Para remover: `remover_gerenciador.ps1`.
Para atualizar na hora: `atualizar_noticias.bat`. Os registros ficam em `logs/`.

### Na internet (GitHub Pages) — funciona mesmo com o PC desligado
`.github/workflows/atualizar.yml` roda o gerenciador de hora em hora nos servidores do GitHub
e publica as notícias novas.

1. Crie um repositório no GitHub (ex.: `central-robotica`) e envie esta pasta.
2. *Settings → Pages*: *Deploy from a branch* → `main` / raiz.
3. *Settings → Actions → General*: marque *Read and write permissions*.
4. O site fica em `https://SEU-USUARIO.github.io/central-robotica/` e se atualiza sozinho.

## Editar conteúdo
- Fontes de notícias: lista `FONTES` em `coletor/atualizar.py`.
- Robôs, fabricantes e sites: `dados/catalogo.js`.
- Curiosidades, documentários e história: `dados/conteudo.js`.
