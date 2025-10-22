# Sistema de Telemedicina - Backend

Este é o backend da aplicação de telemedicina com FastAPI. Aqui você encontra tudo que precisa para rodar o projeto localmente.

## Como rodar o projeto

### 1. Primeiro, suba o banco de dados
O banco PostgreSQL roda no Docker. Você só precisa fazer isso uma vez:

```bash
docker-compose up -d
```

Isso vai criar um banco PostgreSQL na porta 5433. Pode fechar o Docker depois, o banco continua rodando.

### 2. Instale as dependências Python
```bash
pip install -r requirements.txt
```

### 3. Crie as tabelas do banco
Rode uma única vez para criar todas as tabelas:

```bash
python create_tables.py
```

### 4. Inicie o servidor
```bash
uvicorn main:app --reload
```

Pronto! O sistema estará rodando em: http://127.0.0.1:8000

## Testando a API

- **Swagger UI**: http://127.0.0.1:8000/docs
- **Redoc**: http://127.0.0.1:8000/redoc

Na interface do Swagger você pode testar todos os endpoints. Começe criando um usuário em `/auth/cadastro` e depois teste os outros endpoints.

## 🔧 Comandos úteis

**Ver se o banco está rodando:**
```bash
docker-compose ps
```

**Parar o banco (se precisar):**
```bash
docker-compose down
```

**Conectar no banco (DBeaver ou similar):**
- Host: localhost
- Porta: 5433
- Database: telemedicina_db
- Usuário: postgres
- Senha: postgres

## Estrutura do projeto

- `app/gestao_perfis/` - Cadastro de usuários, médicos, pacientes
- `app/gestao_consultas/` - Agendamento e prontuários
- `app/gestao_exames/` - Solicitações de exames e laudos
- `main.py` - API principal com todos os endpoints

