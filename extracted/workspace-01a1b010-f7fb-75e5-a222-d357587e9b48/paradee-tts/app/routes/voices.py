from fastapi import APIRouter
router=APIRouter(tags=['Voices'])
VOICES=[{'id':'af_heart','name':'Heart','accent':'American','gender':'Female','sample_text':'Hello! I am Heart, an American English voice.'},{'id':'bf_isabella','name':'Isabella','accent':'British','gender':'Female','sample_text':'Hello! I am Isabella, a British English voice.'},{'id':'am_puck','name':'Puck','accent':'American','gender':'Male','sample_text':'Hello! I am Puck, an American English voice.'},{'id':'bm_fable','name':'Fable','accent':'British','gender':'Male','sample_text':'Hello! I am Fable, a British English voice.'}]
@router.get('/api/voices')
def voices():return {'voices':VOICES}
