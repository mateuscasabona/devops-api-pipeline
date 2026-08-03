"""Testes da API.

São a rede de segurança da pipeline: é este arquivo que o estágio "Testes"
executa antes de deixar qualquer build acontecer.
"""

from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_raiz_retorna_a_disciplina():
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert resposta.json()["disciplina"] == "Platform Engineering, DevSecOps & SRE Practices"


def test_health_retorna_ok():
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_item_conhecido_retorna_200():
    resposta = cliente.get("/items/1")
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "servidor"


def test_item_desconhecido_retorna_404():
    resposta = cliente.get("/items/99")
    assert resposta.status_code == 404


def test_error_retorna_500():
    resposta = cliente.get("/error")
    assert resposta.status_code == 500


def test_slow_retorna_200():
    resposta = cliente.get("/slow?ms=50")
    assert resposta.status_code == 200
    assert resposta.json() == {"dormiu_ms": 50}
