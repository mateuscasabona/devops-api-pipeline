# ---------------------------------------------------------------------------
# Estágio 1 — builder: monta as dependências em um venv isolado.
# Tudo que é lixo de compilação (cache do pip, ferramentas de build) morre aqui
# e nunca chega à imagem que vai para produção.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# requirements.txt é copiado sozinho e antes do código: enquanto ele não mudar,
# o Docker reaproveita a camada de instalação em vez de baixar tudo de novo.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Estágio 2 — final: só o que é necessário para EXECUTAR.
# Imagem menor, menos pacotes instalados, menos superfície de ataque.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS final

# A pipeline injeta o SHA do commit no build; o endpoint /version devolve ele.
ARG GIT_SHA=local
ENV GIT_SHA=$GIT_SHA

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Rodar como root dentro do container é privilégio desnecessário.
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app/ ./app/

USER appuser
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
