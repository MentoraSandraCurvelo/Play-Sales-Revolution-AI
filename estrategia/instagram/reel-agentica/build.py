import json, subprocess
S = "/tmp/claude-0/-home-user-Play-Sales-Revolution-AI/56e793ef-bf15-5592-8182-e12bf01cfd05/scratchpad"
SEG = json.load(open("seg.json"))
W = [w for w in json.load(open("words.json")) if w.get("type") == "word"]
OFF = []; t = 0.0
for a, b in SEG: OFF.append(t); t += b - a
BODY = round(t, 2); END = 2.5; TOTAL = round(BODY + END, 2)
def final(g):
    for (a, b), o in zip(SEG, OFF):
        if a <= g < b: return o + g - a
    return None
def span(i, j=None):
    j = i if j is None else j
    return (round(OFF[i], 2), round(OFF[j] + SEG[j][1] - SEG[j][0], 2))
cta = next(final(w["start"]) for w in W if w["text"].lower().startswith("comenta") and final(w["start"]) is not None)
OV = [("o1.png", *span(0)), ("o2.png", *span(2)), ("o3.png", *span(4)), ("o4.png", *span(7)),
      ("o5.png", *span(8, 9)), ("o6.png", *span(10, 11)), ("o7.png", *span(12)), ("o8.png", round(cta, 2), BODY)]

KEY_RED = {"agéntica", "agente", "agentes", "apruebas", "aprobarlo", "solo", "crea"}
KEY_AMB = {"generativa", "herramientas", "sistema", "trabaja", "tablero", "pdf", "método", "uno", "dos", "tres"}
def word_ass(w):
    clean = w.strip("¿?,.:").lower()
    txt = w
    if clean == "agente" and "comenta" in cur_ctx: txt = txt.upper()
    if clean in KEY_RED: return r"{\c&H2D2DFF&}" + txt + r"{\c&HFFFFFF&}"
    if clean in KEY_AMB: return r"{\c&H20B0FF&}" + txt + r"{\c&HFFFFFF&}"
    return txt
ws = [w for w in W if final(w["start"]) is not None]
chunks, cur = [], []
for w in ws:
    cur.append(w)
    if len(cur) == 3 or w["text"][-1] in ",.?:":
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
def fmt(x):
    m = int(x // 60); s = x - 60 * m
    return f"0:{m:02d}:{s:05.2f}"
ev = []
for i, ch in enumerate(chunks):
    st = final(ch[0]["start"]); en = (final(ch[-1]["end"] - 0.001) or st + 0.4) + 0.15
    if i + 1 < len(chunks): en = min(en + 0.2, final(chunks[i + 1][0]["start"]))
    cur_ctx = " ".join(w["text"].lower() for w in ch) + (" comenta" if st >= cta - 0.5 else "")
    ev.append(f"Dialogue: 0,{fmt(st)},{fmt(en)},Sub,,0,0,0,,{'  '.join(word_ass(w['text']) for w in ch)}")
open("subs.ass", "w").write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Black,88,&H00FFFFFF,&H00FFFFFF,&H00141414,&H80000000,1,0,0,0,100,100,2,0,1,7,3,2,70,70,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n")

inp = ["-c:v", "libvpx-vp9", "-i", "fg.webm", "-i", "cut.mp4", "-loop", "1", "-t", str(TOTAL), "-i", "bg1.png"]
for f, *_ in OV: inp += ["-loop", "1", "-t", str(TOTAL), "-i", f]
inp += ["-loop", "1", "-t", str(END), "-i", "o9.png", "-stream_loop", "-1", "-i", f"{S}/video1/musica.mp3"]
n = 3 + len(OV)
fc = f"[2:v]scale=1080:1920,boxblur=3:1,eq=brightness=-0.04,fps=30,format=yuv420p,trim=0:{BODY}[bg];"
fc += f"[0:v]scale=1080:1920,fps=30,format=yuva420p,trim=0:{BODY},setpts=PTS-STARTPTS[fg];"
fc += "[bg][fg]overlay=0:0:shortest=1,format=yuv420p[s0];"
prev = "s0"
for k, (f, a, b) in enumerate(OV):
    fc += f"[{prev}][{3+k}:v]overlay=0:0:enable='between(t,{a},{b})'[s{k+1}];"; prev = f"s{k+1}"
fc += f"[{prev}]ass=subs.ass,setsar=1[body];[{n}:v]scale=1080:1920,fps=30,format=yuv420p,setsar=1[endv];"
fc += f"[1:a]atrim=0:{BODY},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-15:TP=-1.5:LRA=11[vz];anullsrc=r=48000:cl=stereo,atrim=0:{END}[sil];"
fc += "[vz]aformat=channel_layouts=stereo[vz2];[body][vz2][endv][sil]concat=n=2:v=1:a=1[vout][voz];"
fc += f"[{n+1}:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=0.09,afade=t=in:d=0.8,afade=t=out:st={TOTAL-2.2}:d=2.2[mu];"
fc += "[voz][mu]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
subprocess.run(["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
                "-t", str(TOTAL), "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-b:a", "192k", "-threads", "2", "-movflags", "+faststart", "reel_agentica.mp4"], check=True)
print("ok", TOTAL, len(ev), OV)
