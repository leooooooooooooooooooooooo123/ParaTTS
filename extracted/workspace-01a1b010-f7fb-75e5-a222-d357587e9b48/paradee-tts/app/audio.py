import io,re,time,uuid,wave
from pathlib import Path
from threading import Lock
import numpy as np
from fastapi import HTTPException
from .config import get_settings
lock=Lock();jobs={}
try:
 import lameenc
 mp3_available=True
except ImportError:lameenc=None;mp3_available=False

def cleanup_audio():
 s=get_settings();s.audio_dir.mkdir(parents=True,exist_ok=True);s.audio_dir.chmod(0o700);now=time.time()
 with lock:
  files=sorted((p for p in s.audio_dir.iterdir() if p.is_file()),key=lambda p:p.stat().st_mtime)
  for p in files:
   if now-p.stat().st_mtime>s.audio_ttl_seconds:p.unlink(missing_ok=True);jobs.pop(p.stem,None)
  files=sorted((p for p in s.audio_dir.iterdir() if p.is_file()),key=lambda p:p.stat().st_mtime)
  while len(files)>s.max_audio_files:p=files.pop(0);p.unlink(missing_ok=True);jobs.pop(p.stem,None)
def pcm(samples):return (np.clip(np.asarray(samples).reshape(-1),-1,1)*32767).astype('<i2').tobytes()
def create_audio(samples,rate,fmt,voice,elapsed):
 cleanup_audio();raw=pcm(samples)
 if fmt=='wav':
  buf=io.BytesIO()
  with wave.open(buf,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(raw)
  data=buf.getvalue()
 else:
  if not mp3_available:raise HTTPException(503,'MP3 encoding is unavailable. Choose WAV.')
  enc=lameenc.Encoder();enc.set_bit_rate(128);enc.set_in_sample_rate(rate);enc.set_channels(1);enc.set_quality(2)
  data=enc.encode(raw)+enc.flush()
 job=uuid.uuid4().hex;path=get_settings().audio_dir/f'{job}.{fmt}';path.write_bytes(data)
 meta={'job_id':job,'status':'complete','voice':voice,'format':fmt,'duration_seconds':round(len(samples)/rate,3),'sample_rate':rate,'file_size_bytes':len(data),'generation_seconds':round(elapsed,4),'audio_url':f'/api/audio/{job}.{fmt}','download_url':f'/api/audio/{job}.{fmt}?download=true'}
 with lock:jobs[job]=meta
 return meta
def get_job(job):
 if not re.fullmatch(r'[a-f0-9]{32}',job):raise HTTPException(404,'Job not found.')
 with lock:meta=jobs.get(job)
 if not meta or not Path(get_settings().audio_dir/f"{job}.{meta['format']}").is_file():raise HTTPException(404,'Job not found or expired.')
 return meta
def audio_path(name):
 if not re.fullmatch(r'[a-f0-9]{32}\.(wav|mp3)',name):raise HTTPException(400,'Invalid audio filename.')
 return get_settings().audio_dir/name
