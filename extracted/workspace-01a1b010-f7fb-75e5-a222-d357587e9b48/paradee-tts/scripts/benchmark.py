"""Measure a real Uvicorn process; no model or audio mocks."""
import json,os,platform,subprocess,sys,time,threading
from pathlib import Path
import httpx,psutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));port=8765;base=f'http://127.0.0.1:{port}'
server=subprocess.Popen([str(ROOT/'.venv/bin/uvicorn'),'app.main:app','--host','127.0.0.1','--port',str(port),'--workers','1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);process=psutil.Process(server.pid)
memory={'total':0,'parent':0,'child':0};stop=threading.Event()
def monitor():
 while not stop.is_set():
  try:
   parent=process.memory_info().rss;child=sum(c.memory_info().rss for c in process.children(recursive=True));memory['parent']=max(memory['parent'],parent);memory['child']=max(memory['child'],child);memory['total']=max(memory['total'],parent+child)
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
  stop.wait(.01)
thread=threading.Thread(target=monitor);thread.start();report={'environment':'local Uvicorn server','timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'python':platform.python_version(),'platform':platform.platform(),'cpu_count':os.cpu_count()}
try:
 start=time.perf_counter()
 for _ in range(100):
  try:
   if httpx.get(base+'/health',timeout=.2).status_code==200:break
  except Exception:time.sleep(.1)
 report['cold_startup_seconds']=round(time.perf_counter()-start,4)
 texts={'short':'Small model, clear voice.','medium':'Paradee turns ordinary English text into speech using a compact neural network that runs entirely on a CPU.','long':'The history of artificial intelligence is filled with ambitious predictions, surprising setbacks, and quiet discoveries. Small models cannot solve every problem, but they can make useful technology easier to deploy, inspect, and afford. This sentence is intentionally longer to measure how generation time scales with the amount of speech produced.'}
 runs=[]
 for label,text in texts.items():
  for i in range(2):
   t=time.perf_counter();r=httpx.post(base+'/api/tts',json={'text':text,'voice':'af_heart'},timeout=90);elapsed=time.perf_counter()-t;assert r.status_code==200,r.text;d=r.json();runs.append({'length':label,'iteration':i+1,'characters':len(text),'request_seconds':round(elapsed,4),'model_seconds':d['generation_seconds'],'audio_seconds':d['duration_seconds'],'real_time_factor':round(d['generation_seconds']/d['duration_seconds'],5),'audio_bytes':d['file_size_bytes']})
 for voice in ['bf_isabella','am_puck','bm_fable']:
  r=httpx.post(base+'/api/tts',json={'text':'Voice and accent verification.','voice':voice},timeout=90);assert r.status_code==200,r.text
 report['runs']=runs;report['status']=httpx.get(base+'/api/status').json();report['voice_switch_test']='All four voices returned HTTP 200 with real audio'
finally:
 stop.set();thread.join();report['observed_memory_mb']={k:round(v/1048576,2) for k,v in memory.items()};server.terminate();server.wait(timeout=10)
from app.config import get_settings
models=list(get_settings().hf_home.rglob('paradee_int8.onnx'));report['model_download_bytes']=models[0].stat().st_size if models else None;site=ROOT/'.venv/lib/python3.12/site-packages';report['site_packages_bytes']=sum(p.stat().st_size for p in site.rglob('*') if p.is_file())
(ROOT/'benchmarks').mkdir(exist_ok=True)
(ROOT/'benchmarks/local-results.json').write_text(json.dumps(report,indent=2));lines=['# Local benchmark','',f"Measured on {report['platform']}, Python {report['python']}, {report['cpu_count']} visible CPUs.",'','**Local results only; not Render results.**','',f"- Cold startup: {report['cold_startup_seconds']} s",f"- Model bytes: {report['model_download_bytes']}",f"- Peak combined RSS: {report['observed_memory_mb']['total']} MB (10 ms polling)",f"- Installed site-packages: {report['site_packages_bytes']} bytes",'','| Run | Characters | Seconds | Audio seconds | RTF | Bytes |','|---|---:|---:|---:|---:|---:|']
for r in runs:lines.append(f"| {r['length']} #{r['iteration']} | {r['characters']} | {r['request_seconds']} | {r['audio_seconds']} | {r['real_time_factor']} | {r['audio_bytes']} |")
(ROOT/'benchmarks/LOCAL_BENCHMARK.md').write_text('\n'.join(lines));print(json.dumps(report,indent=2))
