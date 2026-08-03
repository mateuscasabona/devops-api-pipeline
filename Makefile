# Makefile como "porta de entrada" do projeto: os mesmos comandos que o
# desenvolvedor roda na máquina dele são os que a pipeline roda no runner.
# Se diverge, a pipeline vira surpresa.

.DEFAULT_GOAL := help
.PHONY: help install run test lint docker-build docker-run

help:
	@echo "Alvos disponiveis:"
	@echo "  make install       Instala as dependencias da aplicacao e de desenvolvimento"
	@echo "  make run           Sobe a API local em http://localhost:8000 com reload"
	@echo "  make test          Roda a suite de testes com pytest"
	@echo "  make lint          Verifica estilo e formatacao com ruff"
	@echo "  make docker-build  Constroi a imagem Docker com a tag 'starter'"
	@echo "  make docker-run    Sobe o container publicando a porta 8000"

install:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -v

lint:
	ruff check .
	ruff format --check .

docker-build:
	docker build -t starter .

docker-run:
	docker run --rm -p 8000:8000 starter
