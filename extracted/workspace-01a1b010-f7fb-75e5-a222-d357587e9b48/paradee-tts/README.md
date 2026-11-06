# Paradee TTS Studio

A complete English text-to-speech website and API using the **real Paradee-8M-v1.2 int8 ONNX model**. No simulated speech, GPU, PyTorch, FFmpeg, database or frontend framework.

## Features

- Four official voices: `af_heart`, `bf_isabella`, `am_puck`, `bm_fable`
- Responsive accessible light/dark HTML/CSS/vanilla-JS studio
- Real voice previews, speed control, playback and WAV/MP3 downloads
- 24 kHz mono WAV; 128 kbps MP3 when `lameenc` is available
- FastAPI/OpenAPI, validation, request limits, per-client rate limiting and security headers
- Lazy model loading, one inference slot, one ONNX thread and temporary UUID audio
- Low-memory phonemizer isolation and automatic audio cleanup
- Real-model tests and measured local benchmark

## Setup

Use **Python 3.12**. Current Misaki releases do not support Python 3.13.

```bash
git clone <your-repository-url>
cd paradee-tts
python3.12 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env            # Windows: Copy-Item .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Open **http://localhost:8000** and **http://localhost:8000/docs**. The first generation needs internet access to download the 8,462,119-byte model into `HF_HOME`.

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness without model loading |
| GET | `/api/status` | Model/memory/concurrency/MP3 status |
| GET | `/api/voices` | Official voices and preview text |
| POST | `/api/tts` | Synchronous generation |
| GET | `/api/tts/{job_id}` | Current in-memory job metadata |
| GET | `/api/audio/{filename}` | Playback; `?download=true` downloads |
| GET | `/docs` | Interactive OpenAPI documentation |

```bash
curl -X POST http://localhost:8000/api/tts \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hello from Paradee.","voice":"af_heart","format":"wav","speed":1.0}'
```

The JSON response supplies `audio_url`, `download_url`, duration, sample rate and generation time. Speed accepts 0.75–1.5. Input is English only and limited to 1,500 characters.

## Configuration

See `.env.example`. Defaults prioritize small hosts:

| Setting | Default |
|---|---:|
| `INFERENCE_SLOTS` | 1 |
| `ONNX_THREADS` | 1 |
| `ISOLATE_PHONEMIZER` | true |
| `MAX_CHARACTERS` | 1500 |
| `MAX_REQUEST_BYTES` | 16384 |
| `RATE_LIMIT_REQUESTS` | 30 |
| `RATE_LIMIT_WINDOW_SECONDS` | 60 |
| `AUDIO_TTL_SECONDS` | 1800 |
| `MAX_AUDIO_FILES` | 25 |
| `AUDIO_DIR` | `/tmp/paradee-audio` |
| `HF_HOME` | `/tmp/paradee-hf` |

Low-memory mode runs Misaki/spaCy in a short-lived subprocess, releases it, then loads ONNX and synthesizes in 256-phoneme chunks. A warm ONNX session is released before subsequent phonemization, preventing both memory-heavy stages from coexisting. This adds latency but substantially reduces combined RSS. Disable isolation only when memory is less important than latency.

Input text is not persisted. Generated audio uses random UUID filenames in a private temporary directory and expires. Job metadata is in memory. The rate limiter is per-process and does not replace edge abuse protection.

## Tests and measured results

```bash
pip install -r requirements-dev.txt
pytest -q
python scripts/benchmark.py
```

Latest local verification: **9 tests passed**, all using real inference where generation is tested. Coverage includes startup, exact voices, validation, WAV structure, MP3 signatures, playback/download, job lookup, traversal rejection, two concurrent requests and model-load failure.

Measured on Linux x86_64, Python 3.12.16, two visible CPUs:

- Peak combined parent + child RSS: **412.71 MB** (10 ms polling)
- Cold startup: **0.4908 s**
- Short generation: **2.8396 / 2.8406 s**
- Medium generation: **2.9750 / 2.9394 s**
- Long generation, 22.8 s audio: **3.4801 / 3.4643 s**
- All four voices returned real audio successfully

Exact artifacts: `benchmarks/LOCAL_BENCHMARK.md` and `benchmarks/local-results.json`. These are **not Render measurements**.

## GitHub and Render

```bash
git init
git add .
git commit -m "Initial release: Paradee TTS Studio"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/paradee-tts.git
git push -u origin main
```

Then in Render choose **New → Blueprint**, connect the repository and deploy `render.yaml`. It configures Python 3.12, one worker and conservative memory settings. After deployment, test `/health`, `/api/status`, every voice, MP3/WAV playback and downloads.

**No public Render deployment has been performed.** No public URL or Render Free compatibility is claimed. Local RAM below 512 MB does not guarantee Render behavior.

## Troubleshooting

- **Python 3.13 install failure:** recreate the environment with Python 3.12.
- **First generation fails:** confirm outbound Hugging Face access and writable `HF_HOME`; retry after the model downloads.
- **Memory failure:** retain one worker/slot/thread and isolation; shorten text.
- **MP3 unavailable:** install a compatible `lameenc` wheel or select WAV.
- **404 audio:** files intentionally expire or disappear on restart; generate again.
- **429:** wait for the rate-limit window; add reverse-proxy limits for public production.
- **No browser sound:** press play after generation and check autoplay/device settings.

## Model attribution

Official model: <https://huggingface.co/sahilmahendrakar/Paradee-8M-v1.2>  
Official integration: <https://github.com/sahilmahendrakar/paradee>  
Pinned commit: `c2789ef9abf54a9384eef89cc7de3f1afe5ad01d`  
License: Apache-2.0.
