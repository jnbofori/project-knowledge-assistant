# Project Knowledge Assistant API

RAG-powered FastAPI backend for project document Q&A. Users authenticate with JWT, belong to projects, upload documents, and ask questions grounded in project-specific context.

## Stack

- **API:** FastAPI
- **Auth:** JWT (email/password)
- **Database:** PostgreSQL
- **Chunking:** LlamaIndex `SentenceSplitter`
- **Embeddings:** OpenAI
- **Vector store:** Qdrant
- **LLM:** OpenAI GPT

## Quick start

1. Copy environment file and set your OpenAI key:

```bash
cp .env.example .env
```

2. Start infrastructure:

```bash
docker compose up -d
```

3. Install dependencies and run migrations:

```bash
pip install -r requirements.txt
alembic upgrade head
```

4. Start the API:

```bash
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Typical flow

1. `POST /auth/register` — create account
2. `POST /auth/login` — get JWT (form: username=email, password=...)
3. `POST /projects` — create a project (Bearer token)
4. `POST /projects/{id}/documents` — upload `.txt`, `.md`, `.pdf`, or `.docx`
5. Poll `GET /projects/{id}/documents` until status is `ready`
6. `POST /projects/{id}/queries` — ask a question

## Project roles

| Role   | Upload | Query | Manage members |
|--------|--------|-------|----------------|
| owner  | yes    | yes   | yes            |
| admin  | yes    | yes   | yes            |
| member | yes    | yes   | no             |
| viewer | no     | yes   | no             |
