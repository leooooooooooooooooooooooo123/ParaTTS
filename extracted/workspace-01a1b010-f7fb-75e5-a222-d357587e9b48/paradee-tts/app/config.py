from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    max_characters: int = 1500
    max_request_bytes: int = 16384
    audio_ttl_seconds: int = 1800
    max_audio_files: int = 25
    inference_slots: int = 1
    onnx_threads: int = 1
    isolate_phonemizer: bool = True
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60
    audio_dir: Path = Path('/tmp/paradee-audio')
    hf_home: Path = Path('/tmp/paradee-hf')

@lru_cache
def get_settings(): return Settings()
