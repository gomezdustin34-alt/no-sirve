import json, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k=Kokoro("models/kokoro-v1.0.onnx","models/voices-v1.0.bin")
L=json.load(open("lines.json")); out={}
for key,t in L.items():
    a,sr=k.create(t,voice="ef_dora",speed=1.12,lang="es")
    # trim silence
    idx=np.where(np.abs(a)>0.01)[0]; a=a[max(0,idx[0]-200):idx[-1]+2000]
    sf.write(f"vo/{key}.wav",a,sr); out[key]=round(len(a)/sr,3)
json.dump(out,open("vo/dur.json","w"),indent=1); print(out, sum(out.values()))
