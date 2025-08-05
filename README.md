# mc-nlp-api

This FastAPI microservice uses an LLM (via Ollama) to interpret natural language instructions (in Spanish) and convert them into structured JSON actions. It's designed to assist a Discord bot in understanding user inputs like adding an IP to a firewall or responding to general questions.

## 🔧 Features

- Receives Spanish natural language messages via HTTP POST
- Interprets messages using Ollama's local LLM (e.g., `llama3`)
- Responds with structured JSON containing `action` and `response`
- Includes logging and IP masking for privacy
- Designed to work as a backend for a Discord bot

## 📦 Requirements

- Python 3.10+
- Ollama installed and running (with your chosen model pulled)
- Docker (optional for containerized deployment)

## 🚀 Running Locally

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Run Ollama locally**

```bash
ollama run llama3
```

3. **Start the FastAPI app**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🐳 Docker Deployment

Use the following `docker-compose.yml` structure to run the app:

```yaml
services:
  mc-nlp-api:
    image: mc-nlp-api:latest
    build: .
    container_name: mc-nlp-api
    ports:
      - "8002:8000"
    environment:
      - OLLAMA_API_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 5s
```

> Make sure you also have the Ollama service running and accessible by the API.

## 🧪 Usage

Send a POST request to `/interpret`:

```json
POST /interpret
Content-Type: application/json

{
  "message": "Agrega mi IP 203.0.113.42"
}
```

Example response:

```json
{
  "action": "add_ip",
  "response": "203.0.113.42"
}
```

## ✅ Health Check

To confirm the API is running, call:

```
GET /health
```

Returns:

```json
{
  "status": "ok",
  "message": "API is running smoothly"
}
```

## 🧠 About

This service is part of a larger Discord bot project to automate server access management by interpreting user requests in natural language.

---

Built by Apollox 🚀