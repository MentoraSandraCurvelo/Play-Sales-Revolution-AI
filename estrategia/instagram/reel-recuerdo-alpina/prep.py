import json, subprocess
E = "/tmp/claude-0/-home-user-Play-Sales-Revolution-AI/56e793ef-bf15-5592-8182-e12bf01cfd05/scratchpad/udes/edit"
SEG = [("IMG_4147.mov", f"{E}/words2.json", 37.10, 39.95),   # En esta red hay que empezar por buscarlos,
       ("IMG_4147.mov", f"{E}/words2.json", 45.05, 46.34),   # Entonces, buscamos negocios.
       ("IMG_4147.mov", f"{E}/words2.json", 46.36, 47.90),   # Por ejemplo, quiero hacer un negocio
       ("IMG_4147.mov", f"{E}/words2.json", 48.60, 50.50),   # con el presidente de Alpina.
       ("IMG_4147.mov", f"{E}/words2.json", 51.45, 57.00),   # en vez de hacerle una llamada en frío ... qué han hecho.
       ("IMG_4147.mov", f"{E}/words2.json", 57.76, 60.05)]   # ahí estamos hablando de autoridad.
inp, fc, cat, W, off = [], "", "", [], 0.0
for k, (src, wf, a, b) in enumerate(SEG):
    inp += ["-ss", str(a), "-t", str(b - a), "-i", f"{E}/{src}"]
    d = b - a
    fc += f"[{k}:v]scale=1080:1920:flags=lanczos,fps=30,setsar=1,trim=0:{d},setpts=PTS-STARTPTS[v{k}];"
    fc += f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{d},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={d-0.04}:d=0.04[a{k}];"
    cat += f"[v{k}][a{k}]"
    for w in json.load(open(wf)):
        if w["start"] >= a - 0.05 and w["end"] <= b + 0.03:
            W.append({"text": w["text"], "start": round(w["start"] - a + off, 2), "end": round(min(w["end"], b) - a + off, 2)})
    off += d
fc += f"{cat}concat=n={len(SEG)}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", f"{E}/cut_alpina.mov"], check=True)
for w in W:
    if w["text"] == "hacerlo": w["text"] = "hacerle"
    if w["text"] == "ahí": w["text"] = "Ahí"
json.dump(W, open("words_all.json", "w"), ensure_ascii=False)
print(round(off, 2), " ".join(w["text"] for w in W[-14:]))
