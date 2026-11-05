#!/usr/bin/env python3
"""Sube un mp4 a LinkedIn (API /rest/videos) y escribe el urn en el JSON de la cola.
Uso: python3 contenido-linkedin/subir_video.py <id-de-la-cola>"""
import json, subprocess, sys, os, tempfile
ID=sys.argv[1]; D=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.dirname(D)
P=f"{D}/cola/{ID}.json"; q=json.load(open(P,encoding='utf-8'))
f=os.path.join(REPO,q['archivo_video']); n=os.path.getsize(f)
H=['-H','Content-Type: application/json','-H','LinkedIn-Version: 202601','-H','X-Restli-Protocol-Version: 2.0.0']
def post(url,body):
    r=subprocess.run(['curl','-sS','-X','POST',url,*H,'--data',json.dumps(body)],capture_output=True,text=True); return r.stdout
init=json.loads(post('https://api.linkedin.com/rest/videos?action=initializeUpload',{"initializeUploadRequest":{"owner":"urn:li:person:tsJbwdb3B2","fileSizeBytes":n,"uploadCaptions":False,"uploadThumbnail":False}}))
v=init['value']; urn=v['video']; etags=[]
with open(f,'rb') as fh:
    data=fh.read()
for ins in v['uploadInstructions']:
    a,b=ins['firstByte'],ins['lastByte']
    tmp=tempfile.NamedTemporaryFile(delete=False); tmp.write(data[a:b+1]); tmp.close()
    r=subprocess.run(['curl','-sS','-D','-','-o','/dev/null','-X','PUT',ins['uploadUrl'],'-H','Content-Type: application/octet-stream','--data-binary','@'+tmp.name],capture_output=True,text=True)
    os.unlink(tmp.name)
    et=[l.split(':',1)[1].strip() for l in r.stdout.splitlines() if l.lower().startswith('etag:')]
    if not et: sys.exit('Falló la subida de una parte: '+r.stdout[:300])
    etags.append(et[0])
fin=post('https://api.linkedin.com/rest/videos?action=finalizeUpload',{"finalizeUploadRequest":{"video":urn,"uploadToken":v.get('uploadToken',''),"uploadedPartIds":etags}})
q['video']=urn; json.dump(q,open(P,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('Video subido:',urn,fin[:200])
