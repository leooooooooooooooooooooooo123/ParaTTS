# Architecture

```text
Browser (accessible vanilla JS)
          │ HTTPS
          ▼
FastAPI ── validation, body limits, rate limits, security headers
          │
          ├─ health/voices/jobs/audio routes
          │
          └─ bounded generation semaphore
                    │
                    ▼
          Ephemeral Misaki subprocess
          American or British phonemes
                    │ exits, releasing spaCy RAM
                    ▼
          Paradee-8M-v1.2 int8 ONNX
          1 CPU thread · 256-phoneme chunks
                    │
                    ▼
          WAV (wave) or MP3 (lameenc)
                    │
                    ▼
          Private /tmp UUID file → playback/download → TTL cleanup
```

The application uses one Uvicorn worker and one inference slot. Health checks never load the model. In low-memory mode ONNX is unloaded before phonemization and reloaded afterward so the memory-heavy stages do not coexist. Text is never persisted.

## Repository

- `app/` — backend and browser studio
- `tests/` — real inference and security/API tests
- `scripts/` — measured server benchmark
- `benchmarks/` — exact local artifacts
- `render.yaml` — one-worker Render Blueprint
- `README.md` — setup, API and troubleshooting
