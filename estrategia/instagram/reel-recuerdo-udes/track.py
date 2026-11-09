import subprocess, numpy as np, json, sys
SRC = sys.argv[1]; W, H = 270, 480
p = subprocess.run(["ffmpeg","-v","error","-i",SRC,"-vf",f"fps=10,scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
fr = np.frombuffer(p, np.uint8).reshape(-1, H, W, 3).astype(np.int16)
out = []
for f in fr:
    r, g, b = f[...,0], f[...,1], f[...,2]
    red = (r>120)&(r>g*1.8)&(r>b*1.8); white = (r>185)&(g>185)&(b>185)
    pts = [(x, y) for y in range(120, 330) for x in np.nonzero(white[y])[0]
           if red[y, max(0,x-35):x].any() and red[y, x+1:x+36].any()]
    if len(pts) < 10: out.append(None); continue
    pts = np.array(pts); sel = pts[pts[:,1] >= np.percentile(pts[:,1], 60)]
    out.append([float(np.median(sel[:,0])), float(np.median(sel[:,1])), float(pts[:,1].max())])
n = len(out); a = np.array([v if v else [np.nan]*3 for v in out])
for k in range(3):
    s = a[:,k]; idx = np.arange(n); m = ~np.isnan(s); s = np.interp(idx, idx[m], s[m])
    s = np.array([np.median(s[max(0,i-4):i+5]) for i in range(n)])
    a[:,k] = np.convolve(np.pad(s,7,mode='edge'), np.ones(15)/15, 'valid')
json.dump({"cx": (a[:,0]*4).tolist(), "cy": ((a[:,1]*0.5+a[:,2]*0.5)*4).tolist()}, open("track_s.json","w"))
print(n)
