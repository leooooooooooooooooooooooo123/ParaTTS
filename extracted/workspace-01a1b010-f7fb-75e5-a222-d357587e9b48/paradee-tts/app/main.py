import time
from collections import defaultdict,deque
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI,Request
from fastapi.responses import FileResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from .audio import cleanup_audio
from .config import get_settings
from .routes import health,voices,tts
settings=get_settings();hits=defaultdict(deque)
@asynccontextmanager
async def lifespan(_):cleanup_audio();yield;cleanup_audio()
app=FastAPI(title='Paradee TTS API',version='1.0.0',lifespan=lifespan,description='English speech with real Paradee-8M-v1.2 ONNX inference.',docs_url='/docs',redoc_url=None)
@app.middleware('http')
async def controls(req:Request,call_next):
 length=req.headers.get('content-length')
 if length and int(length)>settings.max_request_bytes:return JSONResponse({'detail':'Request body too large.'},413)
 if req.url.path=='/api/tts' and req.method=='POST':
  now=time.monotonic();q=hits[req.client.host if req.client else 'unknown']
  while q and q[0]<now-settings.rate_limit_window_seconds:q.popleft()
  if len(q)>=settings.rate_limit_requests:return JSONResponse({'detail':'Rate limit exceeded. Try again shortly.'},429,headers={'Retry-After':str(settings.rate_limit_window_seconds)})
  q.append(now)
 response=await call_next(req)
 response.headers.update({'X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','Referrer-Policy':'no-referrer','Permissions-Policy':'camera=(), microphone=(), geolocation=()','Content-Security-Policy':"default-src 'self'; style-src 'self'; script-src 'self'; media-src 'self' blob:; connect-src 'self'"})
 return response
app.include_router(health.router);app.include_router(voices.router);app.include_router(tts.router)
static=Path(__file__).parent/'static';app.mount('/static',StaticFiles(directory=static),name='static')
@app.get('/',include_in_schema=False)
def index():return FileResponse(static/'index.html')
@app.get('/favicon.ico',include_in_schema=False)
def favicon():return JSONResponse({},204)
