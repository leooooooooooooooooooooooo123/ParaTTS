"""Ephemeral Misaki worker; chunking follows official Apache-2.0 Paradee."""
import json,re,sys

def phonemize(text,voice):
    from misaki import en,espeak
    british=voice.startswith('b')
    g2p=en.G2P(trf=False,british=british,fallback=espeak.EspeakFallback(british=british),unk='')
    for sentence in (s for s in re.split(r'(?<=[.!?…])\s+|\n+',text.strip()) if s.strip()):
        ps,_=g2p(sentence)
        while len(ps)>256:
            cut=ps.rfind(' ',0,256);cut=cut if cut>0 else 256
            yield ps[:cut];ps=ps[cut:].lstrip()
        if ps: yield ps

def main():
    req=json.load(sys.stdin)
    json.dump(list(phonemize(req['text'],req['voice'])),sys.stdout,ensure_ascii=False)
if __name__=='__main__': main()
