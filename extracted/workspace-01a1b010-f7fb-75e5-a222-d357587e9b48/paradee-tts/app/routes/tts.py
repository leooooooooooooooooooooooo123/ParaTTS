from fastapi import APIRouter,HTTPException,Query
from fastapi.responses import FileResponse
from ..audio import create_audio,get_job,audio_path
from ..model import engine,ModelLoadError,GenerationError
from ..schemas import TTSRequest,TTSMetadata
from ..config import get_settings
router=APIRouter(prefix='/api',tags=['Text to Speech'])
@router.post('/tts',response_model=TTSMetadata)
async def tts(req:TTSRequest):
 if len(req.text)>get_settings().max_characters:raise HTTPException(413,'Text exceeds the configured character limit.')
 try:
  r=await engine.generate(req.text,req.voice,req.speed);return create_audio(r.samples,r.sample_rate,req.format,req.voice,r.elapsed)
 except ModelLoadError as e:raise HTTPException(503,str(e))
 except GenerationError as e:raise HTTPException(500,str(e))
 except MemoryError:raise HTTPException(507,'Insufficient memory. Try shorter text.')
 except HTTPException:raise
 except Exception:raise HTTPException(500,'Audio could not be created. Please try again.')
@router.get('/tts/{job_id}',response_model=TTSMetadata)
def job(job_id:str):return get_job(job_id)
@router.get('/audio/{filename}')
def audio(filename:str,download:bool=Query(False)):
 p=audio_path(filename)
 if not p.is_file():raise HTTPException(404,'Audio not found or expired.')
 return FileResponse(p,media_type='audio/wav' if p.suffix=='.wav' else 'audio/mpeg',filename=p.name if download else None,headers={'Cache-Control':'private, max-age=300','X-Content-Type-Options':'nosniff'})
