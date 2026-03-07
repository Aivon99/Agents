# LLM Gateway v1

A container-ready HTTP gateway that routes chat/text requests across multiple providers with a shared Postgres-backed reservation state.

## Current providers
- OpenRouter
- Gemini
- Cohere
- Hugging Face Inference Providers

## Behavior
- `ALLOW_PAID_FALLBACK=false`: free routes only
- `ALLOW_PAID_FALLBACK=true`: free routes first, then paid routes

## Start
```bash
cp .env.example .env
docker compose up --build
```

## Example request
```bash
curl -X POST http://localhost:8000/v1/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "chat",
    "messages": [
      {"role": "user", "content": "Give me 3 bullet points on convexity."}
    ],
    "max_output_tokens": 200,
    "require_json": false,
    "save_payloads": true
  }'
```

## Notes
- OpenRouter quota refresh is wired to the documented `/key` endpoint shape at adapter level.
- Gemini uses `count_tokens` and `generate_content` via the Google GenAI SDK.
- Cohere and Hugging Face use internal budget estimation in this v1.
- Prompt/response payload dumps are optional and are stored under `/app/data/request_payloads` instead of being mixed into the main DB rows.
