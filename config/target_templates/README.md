# Target templates

These example configs keep the harness usable for common real-world stacks without making the repo depend on a specific vendor or app.

## Included templates

- `openai_compatible_chat.yaml` — standard OpenAI-compatible `/v1/chat/completions` endpoint
- `fastapi_chat.yaml` — JSON chat endpoint on a local FastAPI app
- `fastapi_sse_chat.yaml` — streaming SSE endpoint on a FastAPI app

## Example usage

```bash
breaklab verify --config config/target_templates/openai_compatible_chat.yaml
breaklab verify --config config/target_templates/fastapi_chat.yaml
breaklab verify --config config/target_templates/fastapi_sse_chat.yaml --report
```

## Notes

- Replace the example `base_url`, credentials, and routes with your real service.
- Keep the attestation string truthful and explicit before running the battery.
- Keep the target on a controlled, permissioned environment for red-team work.
