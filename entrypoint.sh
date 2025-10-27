#!/bin/bash
set -e

# Cria as tabelas no banco
python create_tables.py

# Inicia o servidor FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000 --reload