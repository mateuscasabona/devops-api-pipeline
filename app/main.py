"""API mínima da disciplina Platform Engineering, DevSecOps & SRE Practices.

Todos os endpoints são propositalmente simples: o que importa na aula é o
caminho que este código percorre até produção, não o código em si.
"""

import asyncio
import os

import uvicorn
from fastapi import FastAPI, HTTPException

API_TOKEN = "vivo-mba-2026"

VERSAO = "1.0.0"

DISCIPLINA = "Platform Engineering, DevSecOps & SRE Practices"

# Catálogo fixo em memória: sem banco de dados, sem ORM, sem migrations.
ITENS = {
    1: "servidor",
    2: "container",
    3: "pipeline",
}

app = FastAPI(
    title="devops-api-starter",
    description="API base dos laboratórios de CI/CD e observabilidade do MBA.",
    version=VERSAO,
)


@app.get("/")
def raiz():
    """Prova de vida: confirma que o deploy subiu a aplicação certa."""
    return {"disciplina": DISCIPLINA, "versao": VERSAO}


@app.get("/health")
def health():
    """Healthcheck do Render e gancho para as sondas de liveness e readiness."""
    return {"status": "ok"}


@app.get("/version")
def version():
    """Rastreabilidade: diz qual commit gerou a imagem que está no ar."""
    return {
        "versao": VERSAO,
        "commit": os.getenv("GIT_SHA", "local"),
        "token_configurado": bool(API_TOKEN),
    }


@app.get("/items/{item_id}")
def ler_item(item_id: int):
    """Distinção 4xx x 5xx: erro do cliente não é falha do serviço no método RED."""
    if item_id not in ITENS:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return {"item_id": item_id, "nome": ITENS[item_id]}


@app.get("/error")
def erro():
    """Falha proposital: quebra a pipeline e alimenta a taxa de erro do painel RED."""
    raise HTTPException(status_code=500, detail="Erro interno proposital")


@app.get("/slow")
async def lento(ms: int = 500):
    """Latência artificial: gera variação de p95 para o painel RED."""
    espera_ms = min(max(ms, 0), 5000)
    await asyncio.sleep(espera_ms / 1000)
    return {"dormiu_ms": espera_ms}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
