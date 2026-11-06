"""Lazy singleton, bounded CPU-only Paradee inference with low-memory lifecycle."""
import asyncio,gc,json,os,resource,subprocess,sys,threading,time
from dataclasses import dataclass
import numpy as np
from .config import get_settings
class ModelLoadError(RuntimeError): pass
class GenerationError(RuntimeError): pass
@dataclass
class Result: samples: object; sample_rate: int; elapsed: float
class ParadeeEngine:
    def __init__(self):
        self.settings=get_settings();self._model=None;self._lock=threading.Lock()
        self._slots=threading.BoundedSemaphore(self.settings.inference_slots)
        self.loaded=False;self.load_seconds=None;self.last_error=None;self.generation_count=0;self._accent=None
    @property
    def peak_rss_mb(self): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
    def _load(self):
        if self.loaded:return
        with self._lock:
            if self.loaded:return
            os.environ.setdefault('HF_HOME',str(self.settings.hf_home));start=time.perf_counter()
            try:
                from paradee import Paradee
                self._model=Paradee(version='1.2',quantized=True,threads=self.settings.onnx_threads)
                self.loaded=True;self.load_seconds=time.perf_counter()-start;self.last_error=None
            except Exception as exc:
                self.last_error=type(exc).__name__
                raise ModelLoadError('The speech model could not be loaded. Check download access and memory.') from exc
    def _phonemize(self,text,voice):
        p=subprocess.run([sys.executable,'-m','app.phonemizer'],input=json.dumps({'text':text,'voice':voice}),text=True,capture_output=True,timeout=90,cwd=os.getcwd())
        if p.returncode:raise RuntimeError('Phonemizer failed')
        return json.loads(p.stdout)
    def _sync(self,text,voice,speed):
        with self._slots:
            start=time.perf_counter()
            try:
                from paradee import SAMPLE_RATE
                if self.settings.isolate_phonemizer:
                    if self._model is not None:self._model=None;self.loaded=False;gc.collect()
                    chunks=self._phonemize(text,voice);self._load()
                    parts=[self._model.generate_from_phonemes(p,voice=voice,speed=speed) for p in chunks]
                    samples=np.concatenate(parts) if parts else np.array([],dtype=np.float32)
                else:
                    self._load();accent=voice.startswith('b')
                    if self._accent is not None and accent!=self._accent:self._model._g2p.clear();gc.collect()
                    self._accent=accent;samples=self._model(text,voice=voice,speed=speed)
                if samples is None or len(samples)==0:raise GenerationError('The model returned empty audio.')
                self.generation_count+=1;return Result(samples,SAMPLE_RATE,time.perf_counter()-start)
            except ModelLoadError:raise
            except MemoryError as exc:raise GenerationError('Not enough memory. Try shorter text.') from exc
            except GenerationError:raise
            except Exception as exc:raise GenerationError('Speech generation failed. Try shorter text or another voice.') from exc
    async def generate(self,text,voice,speed):return await asyncio.to_thread(self._sync,text,voice,speed)
    def status(self):
        return {'model':'Paradee-8M-v1.2','model_loaded':self.loaded,'model_load_seconds':self.load_seconds,'generation_count':self.generation_count,'peak_rss_mb':round(self.peak_rss_mb,2),'last_error':self.last_error,'inference_slots':self.settings.inference_slots,'onnx_threads':self.settings.onnx_threads,'isolate_phonemizer':self.settings.isolate_phonemizer}
engine=ParadeeEngine()
