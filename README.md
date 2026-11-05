# Portfólio One Piece — Jônatas José

Portfólio pessoal responsivo com identidade visual inspirada em One Piece. O conteúdo preserva os links profissionais já usados no portfólio e destaca projetos públicos do GitHub.

## Tecnologias

- HTML, CSS e JavaScript para o site estático.
- Python e SQLite para a API opcional de métricas agregadas.
- Java e C# como clientes de exemplo para a API.

## Executar localmente

Requer Python 3.10 ou superior. Na raiz do projeto:

```sh
python analytics/server.py
```

A página fica em `http://127.0.0.1:8765/`. Para experimentar o aviso de consentimento e registrar uma visualização local, ajuste temporariamente `analyticsEndpoint` em `src/js/config.js` para `http://127.0.0.1:8765/api/visit`. Em seguida, aceite as métricas na própria página.

Consulte os totais salvos localmente:

```sh
python -c "import sqlite3; c=sqlite3.connect('analytics/data/visitors.sqlite3'); print(*c.execute('SELECT view_date, total_views FROM daily_views ORDER BY view_date DESC'), sep='\\n')"
```

Os exemplos Java e C# são clientes manuais para desenvolvimento:

```sh
javac analytics/examples/java/PortfolioAnalyticsClient.java
java -cp analytics/examples/java PortfolioAnalyticsClient
```

```sh
dotnet run --project analytics/examples/csharp/AnalyticsClient.csproj
```

## Métricas e privacidade

A API aceita apenas o evento `page_view`. O SQLite guarda uma linha por dia com o total de visualizações; não guarda nome, e-mail, IP, localização, endereço de página, agente de navegador ou identificador individual. A página só envia a contagem depois de a pessoa aceitar. A recusa fica registrada apenas no armazenamento local do navegador.

O servidor desliga os logs de requisição da aplicação e bloqueia o acesso HTTP ao diretório local do banco. Um proxy ou provedor de hospedagem ainda pode manter logs próprios; revise as configurações do serviço que hospedar a API.

## Publicação

O GitHub Pages publica apenas os arquivos estáticos. Ele não executa o servidor Python e, por isso, as métricas permanecem desligadas por padrão no site publicado. Para ativá-las online, hospede `analytics/server.py` em um serviço Python com armazenamento persistente e HTTPS, configure `ALLOWED_ORIGINS` com a origem do GitHub Pages e então defina a URL HTTPS de `/api/visit` em `src/js/config.js`.

A URL e o QR code do portfólio apontam para:

`https://kalebreus.github.io/portfolio-one-piece/`

As imagens de personagens são recursos visuais temáticos. Este é um projeto de fã sem vínculo oficial com One Piece.
