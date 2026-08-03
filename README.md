# devops-api-starter

Repositório **template** da disciplina *Platform Engineering, DevSecOps & SRE
Practices*.

---

## 1. O que é este projeto

Uma API mínima em [FastAPI](https://fastapi.tiangolo.com/) que serve de base
para os laboratórios de **CI/CD** e de **observabilidade**.

A aplicação inteira cabe em um arquivo: [`app/main.py`](app/main.py). Isso é
intencional. O objetivo da disciplina não é discutir arquitetura de aplicação —
é discutir o **caminho que um código percorre até chegar em produção**: lint,
testes, análise de segurança, build da imagem, deploy e observabilidade.

Por isso não há banco de dados, autenticação, camada de serviço nem injeção de
dependência. Cada linha de código aqui existe para sustentar um momento
específico da aula.

Se você nunca viu FastAPI, o essencial é: cada função decorada com
`@app.get("/rota")` responde a uma requisição HTTP naquele endereço, e o
dicionário devolvido pela função vira o JSON da resposta. É só isso.

---

## 2. Endpoints

| Método | Rota | Retorno | Serve para |
|---|---|---|---|
| GET | `/` | `{"disciplina": "...", "versao": "1.0.0"}` | Prova de vida após o deploy |
| GET | `/health` | `{"status": "ok"}` | Healthcheck do Render; gancho para liveness/readiness |
| GET | `/version` | `{"versao": "1.0.0", "commit": ...}` | Rastreabilidade de artefato |
| GET | `/items/{item_id}` | 200 para 1, 2 e 3; **404** para o resto | Distinção 4xx x 5xx no método RED |
| GET | `/error` | **500** | Quebrar a pipeline; alimentar a métrica de erro |
| GET | `/slow` | 200 após espera; query `ms` (padrão 500, máx. 5000) | Variação de latência para o p95 |

Dois detalhes que voltam nas aulas seguintes:

- **`/version` lê a variável de ambiente `GIT_SHA`** e devolve `"local"` quando
  ela não existe. A pipeline injeta o SHA do commit no momento do build, então
  a resposta desse endpoint diz exatamente qual commit está no ar. Isso é
  rastreabilidade de artefato — sem ela, "está com bug em produção" vira
  adivinhação.
- **`/slow` usa `await asyncio.sleep(...)`**, e não `time.sleep(...)`. O
  primeiro devolve o controle para o event loop e deixa a aplicação atender
  outras requisições durante a espera; o segundo travaria o processo inteiro.
  A diferença fica visível no painel de latência do projeto 3.

Com a aplicação no ar, a documentação interativa gerada automaticamente pelo
FastAPI fica em `http://localhost:8000/docs`.

---

## 3. Como rodar local

### Sem Docker

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Testar:

```bash
curl localhost:8000/health
curl localhost:8000/items/1
curl "localhost:8000/slow?ms=800"
```

Rodar a verificação completa — os mesmos comandos que a pipeline vai executar:

```bash
pytest -v
ruff check .
ruff format --check .
bandit -r app/
```

### Com Docker

```bash
docker build -t starter .
docker run --rm -p 8000:8000 starter
```

Para simular o que a pipeline faz, passando o commit no build:

```bash
docker build --build-arg GIT_SHA=abc1234 -t starter .
docker run --rm -p 8000:8000 starter
curl localhost:8000/version
```

### Pelo Makefile

Se você tem `make` disponível, ele é o atalho para tudo acima:

```bash
make help
```

---

## 4. Anatomia do Dockerfile

O [`Dockerfile`](Dockerfile) é **multi-stage**: define dois estágios e entrega
só o segundo. A ideia é simples e vale para qualquer linguagem — *as
ferramentas necessárias para **construir** um software não são as mesmas
necessárias para **executá-lo***.

| Estágio | O que faz | Por que existe |
|---|---|---|
| `builder` | Cria um venv em `/opt/venv` e instala o `requirements.txt` | Concentra o pip, seu cache e qualquer compilador em uma imagem descartável |
| `final` | Copia o venv pronto e a pasta `app/`, cria um usuário sem privilégio e expõe a porta 8000 | É a imagem que vai para o registry e para produção |

O que se ganha com a separação:

- **Imagem menor.** Nada do estágio `builder` é copiado, exceto o venv já
  resolvido. Cache de pip e ferramentas de compilação ficam para trás.
- **Menos superfície de ataque.** Menos pacote instalado significa menos CVE
  para responder depois.
- **Build mais rápido.** O `COPY requirements.txt` acontece antes do `COPY app/`
  de propósito: enquanto as dependências não mudarem, o Docker reaproveita a
  camada de instalação e só refaz a cópia do código. Em uma aula de duas horas,
  isso é a diferença entre esperar 3 segundos e esperar 2 minutos.
- **Não roda como root.** O `USER appuser` no final garante que um eventual
  comprometimento da aplicação não venha com privilégio administrativo dentro
  do container.

O par `ARG GIT_SHA` + `ENV GIT_SHA=$GIT_SHA` é a ponte entre a pipeline e o
endpoint `/version`: o `ARG` recebe o valor no `docker build`, o `ENV` o
persiste dentro da imagem em execução.

---

## 5. Como usar este template

Este repositório está marcado como **template** no GitHub. Para criar os
projetos das aulas seguintes:

1. Clique em **Use this template** → **Create a new repository**
2. Dê o nome do projeto correspondente (`devops-api-pipeline` ou
   `devops-api-observability`)
3. ⚠️ **Marque o repositório como público**

> **Por que público?** O GitHub Code Scanning — a aba **Security**, onde os
> achados do SAST aparecem — só é gratuito em repositórios públicos. Em
> repositório privado a pipeline até roda, mas o relatório de segurança não
> aparece na interface, e a parte mais visual da aula se perde.

Use **Use this template** e não *fork*: o fork mantém o vínculo com o
repositório de origem e o histórico de commits; o template gera um repositório
novo e independente, que é o que queremos.

---

## 6. Próximos passos

| Projeto | O que acrescenta |
|---|---|
| `devops-api-pipeline` | A pipeline de CI/CD completa: os cinco estágios (Qualidade, Testes, Segurança, Build, Deploy), publicação da imagem no GHCR e deploy no Render |
| `devops-api-observability` | Instrumentação com Prometheus e painel RED no Grafana, rodando local |

A pasta [`.github/workflows/`](.github/workflows/) está aqui vazia de propósito:
é exatamente ali que o projeto 2 encaixa o arquivo da pipeline.

### Adiante-se: prepare o Render antes da aula (opcional)

O projeto 2 usa um serviço externo — o [Render](https://render.com) — para
hospedar a API, e essa parte não depende de nenhum código, só de cliques numa
interface. Se você fizer isso **antes** da aula, chega no laboratório de
pipeline com o ambiente pronto e sobra tempo para focar no que de fato é o
assunto daquele projeto: o YAML.

1. Crie uma conta gratuita em [render.com](https://render.com)
2. **New** → **Web Service** → conecte sua conta do GitHub
3. Ainda não escolha o repositório — ele só vai existir depois que você gerar o
   `devops-api-pipeline` a partir deste template (seção 5 acima)
4. Depois de criar o repositório e escolhê-lo aqui, configure:
   - **Language / Runtime**: `Docker`
   - **Branch**: `main`
   - **Instance Type**: `Free`
5. **Create Web Service** e aguarde o primeiro deploy — o próprio Render builda
   a imagem a partir do `Dockerfile` deste repositório
6. Com o serviço criado, vá em **Settings** → **Deploy Hook** e copie a URL
7. No repositório GitHub `devops-api-pipeline`: **Settings** → **Secrets and
   variables** → **Actions** → **New repository secret**
   - **Name**: `RENDER_DEPLOY_HOOK` — precisa ser exatamente esse nome, é o que
     a pipeline vai procurar
   - **Secret**: a URL copiada no passo 6

> Essa URL **é** a credencial: quem tem o link dispara deploy. Trate como
> senha — nunca em commit, nunca em print de tela, nunca no chat da turma.

O README do `devops-api-pipeline` repete este roteiro com mais contexto — volte
a ele se precisar durante a aula.
