import io,wave
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_startup_health_does_not_load_model():
 assert client.get('/health').json()['status']=='ok'
 assert client.get('/').status_code==200
 assert 'Content-Security-Policy' in client.get('/').headers
def test_voices_exact():
 data=client.get('/api/voices').json()['voices'];assert [v['id'] for v in data]==['af_heart','bf_isabella','am_puck','bm_fable']
def test_validation():
 assert client.post('/api/tts',json={'text':'   '}).status_code==422
 assert client.post('/api/tts',json={'text':'hello','voice':'not_real'}).status_code==422
 assert client.post('/api/tts',json={'text':'x'*1501}).status_code==422
 assert client.post('/api/tts',json={'text':'hello','speed':3}).status_code==422
def test_real_wav_generation_and_job():
 r=client.post('/api/tts',json={'text':'Small model, clear voice.','voice':'af_heart'});assert r.status_code==200,r.text;d=r.json();assert d['sample_rate']==24000 and d['duration_seconds']>0
 a=client.get(d['audio_url']);assert a.status_code==200 and a.headers['content-type']=='audio/wav'
 with wave.open(io.BytesIO(a.content)) as w:assert (w.getnchannels(),w.getframerate(),w.getsampwidth())==(1,24000,2)
 assert client.get('/api/tts/'+d['job_id']).json()['job_id']==d['job_id']
 assert 'attachment' in client.get(d['download_url']).headers.get('content-disposition','')
def test_remaining_real_voices():
 for voice in ['bf_isabella','am_puck','bm_fable']:
  r=client.post('/api/tts',json={'text':'This is a real voice test.', 'voice':voice});assert r.status_code==200,r.text;assert client.get(r.json()['audio_url']).status_code==200
def test_real_mp3_generation():
 r=client.post('/api/tts',json={'text':'MP3 output works.','voice':'am_puck','format':'mp3'});assert r.status_code==200,r.text;a=client.get(r.json()['audio_url']);assert a.content[:3]==b'ID3' or a.content[:2] in (b'\xff\xfb',b'\xff\xf3',b'\xff\xf2')
def test_traversal_and_unknown_job():
 assert client.get('/api/audio/..%2Fetc%2Fpasswd').status_code in (400,404)
 assert client.get('/api/audio/not-a-file.wav').status_code==400
 assert client.get('/api/tts/not-a-job').status_code==404
def test_concurrent_requests_both_succeed():
 def run(_):return client.post('/api/tts',json={'text':'Concurrent real inference test.'})
 with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,range(2)))
 assert all(r.status_code==200 for r in results)
def test_model_loading_failure_is_safe(monkeypatch):
 from app import model
 monkeypatch.setattr(model.engine,'loaded',False);monkeypatch.setattr(model.engine,'_load',lambda:(_ for _ in ()).throw(model.ModelLoadError('The speech model could not be loaded.')))
 r=client.post('/api/tts',json={'text':'Failure test'});assert r.status_code==503;assert 'Traceback' not in r.text
