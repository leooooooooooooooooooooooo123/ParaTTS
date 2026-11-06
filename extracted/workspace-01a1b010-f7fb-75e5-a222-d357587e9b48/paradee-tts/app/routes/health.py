from fastapi import APIRouter
from ..model import engine
from ..audio import mp3_available
router=APIRouter(tags=['Service'])
@router.get('/health')
def health():return {'status':'ok','service':'paradee-tts'}
@router.get('/api/status')
def status():return {**engine.status(),'mp3_available':mp3_available}
