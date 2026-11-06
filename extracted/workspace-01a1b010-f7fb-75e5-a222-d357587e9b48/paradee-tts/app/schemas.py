from typing import Literal
from pydantic import BaseModel, Field, field_validator
VoiceID = Literal['af_heart','bf_isabella','am_puck','bm_fable']
class TTSRequest(BaseModel):
    text: str = Field(min_length=1,max_length=1500)
    voice: VoiceID = 'af_heart'
    format: Literal['wav','mp3'] = 'wav'
    speed: float = Field(default=1.0,ge=.75,le=1.5)
    @field_validator('text')
    @classmethod
    def clean(cls,v):
        v=v.strip()
        if not v: raise ValueError('Text cannot be blank.')
        if '\x00' in v: raise ValueError('Null characters are not supported.')
        return v
class Voice(BaseModel):
    id: VoiceID; name: str; accent: str; gender: str; sample_text: str
class TTSMetadata(BaseModel):
    job_id: str; status: str; voice: VoiceID; format: Literal['wav','mp3']
    duration_seconds: float; sample_rate: int; file_size_bytes: int
    generation_seconds: float; audio_url: str; download_url: str
