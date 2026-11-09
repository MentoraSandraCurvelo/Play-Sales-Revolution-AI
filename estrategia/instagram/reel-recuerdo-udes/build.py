import json, subprocess
S = "/tmp/claude-0/-home-user-Play-Sales-Revolution-AI/56e793ef-bf15-5592-8182-e12bf01cfd05/scratchpad"
SRC = f"{S}/udes/edit/cut.mov"
W = json.load(open("words_all.json"))
FIX = {("Está", "la"): ("Están", "las")}
for i in range(len(W) - 1):
    k = (W[i]["text"], W[i + 1]["text"])
    if k in FIX: W[i]["text"], W[i + 1]["text"] = FIX[k]
BODY = 38.79; END = 2.6; TOTAL = round(BODY + END, 2)
t_int = next(w["start"] for w in W if w["text"].lower().startswith("luego"))
OV = [("o1.png", 0, 5.0), ("o2.png", 5.0, t_int), ("o3.png", t_int, BODY)]
RED = {"intención", "intención.", "propósito", "clientes.", "linkedin", "relaciones", "comerciales."}
AMB = {"conexiones", "estrategia,", "interrupción,", "interrupción", "entretenimiento.", "instagram,", "facebook,", "x"}
def wa(t):
    c = t.lower().strip("¿?,.:")
    if c in {x.strip(",.") for x in RED}: return r"{\c&H2D2DFF&}" + t + r"{\c&HFFFFFF&}"
    if c in {x.strip(",.") for x in AMB}: return r"{\c&H20B0FF&}" + t + r"{\c&HFFFFFF&}"
    return t
chunks, cur = [], []
for w in W:
    cur.append(w)
    if len(cur) == 3 or w["text"][-1] in ",.?:": chunks.append(cur); cur = []
if cur: chunks.append(cur)
fmt = lambda x: f"0:{int(x//60):02d}:{x-60*int(x//60):05.2f}"
TR = json.load(open("track_s.json")); CX, CY = TR["cx"], TR["cy"]
def pos(t):
    i = min(len(CX) - 1, max(0, int(round(t * 10))))
    return round(CX[i]), round(CY[i] + 90)
PW, PH, R = 680, 210, 48
panel = (f"m {R} 0 l {PW-R} 0 b {PW} 0 {PW} 0 {PW} {R} l {PW} {PH-R} b {PW} {PH} {PW} {PH} {PW-R} {PH} "
         f"l {R} {PH} b 0 {PH} 0 {PH} 0 {PH-R} l 0 {R} b 0 0 0 0 {R} 0")
ev = []
t = 0.0
while t < BODY - 1e-6:
    t2 = min(BODY, round(t + 0.2, 2)); (x1, y1), (x2, y2) = pos(t), pos(t2)
    fade = r"\fad(250,0)" if t == 0 else ""
    ev.append(f"Dialogue: 0,{fmt(t)},{fmt(t2)},Panel,,0,0,0,,{{\\an5\\move({x1},{y1},{x2},{y2})\\p1{fade}}}{panel}")
    t = t2
for i, ch in enumerate(chunks):
    st = ch[0]["start"]; en = ch[-1]["end"] + 0.15
    if i + 1 < len(chunks): en = min(en + 0.2, chunks[i + 1][0]["start"])
    en = min(en, BODY)
    # follow the panel in 0.2 s steps so text stays centered on it
    a = st
    while a < en - 1e-6:
        b = min(en, round(a + 0.2, 2)); (x1, y1), (x2, y2) = pos(a), pos(b)
        ev.append(f"Dialogue: 1,{fmt(a)},{fmt(b)},Sub,,0,0,0,,{{\\an5\\move({x1},{y1},{x2},{y2})}}{'  '.join(wa(w['text']) for w in ch)}")
        a = b
open("subs.ass", "w").write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Black,66,&H00FFFFFF,&H00FFFFFF,&H00141414,&H80000000,1,0,0,0,100,100,1,0,1,2,0,5,0,0,0,1
Style: Panel,Arial,20,&H200B0805,&H200B0805,&H802D2DFF,&H00000000,0,0,0,0,100,100,0,0,1,2,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n")
inp = ["-i", SRC]
for f, *_ in OV: inp += ["-loop", "1", "-t", str(TOTAL), "-i", f]
inp += ["-loop", "1", "-t", str(END), "-i", "o4.png", "-stream_loop", "-1", "-i", f"{S}/video1/musica.mp3"]
n = 1 + len(OV)
fc = f"[0:v]trim=0:{BODY},setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,fps=30,eq=contrast=1.04:saturation=1.06,unsharp=5:5:0.4,format=yuv420p,fade=t=in:d=0.35[s0];"
prev = "s0"
for k, (f, a, b) in enumerate(OV):
    fc += f"[{prev}][{1+k}:v]overlay=0:0:shortest=1:enable='between(t,{a},{b})'[s{k+1}];"; prev = f"s{k+1}"
fc += f"[{prev}]ass=subs.ass,setsar=1[body];[{n}:v]scale=1080:1920,fps=30,format=yuv420p,setsar=1[endv];"
fc += f"[0:a]atrim=0:{BODY},asetpts=PTS-STARTPTS,aresample=48000,highpass=f=90,afftdn=nf=-25,loudnorm=I=-15:TP=-1.5:LRA=11,aformat=channel_layouts=stereo[vz];anullsrc=r=48000:cl=stereo,atrim=0:{END}[sil];"
fc += "[body][vz][endv][sil]concat=n=2:v=1:a=1[vout][voz];"
fc += f"[{n+1}:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=0.07,afade=t=in:d=0.8,afade=t=out:st={TOTAL-2.2}:d=2.2[mu];"
fc += "[voz][mu]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
subprocess.run(["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
    "-t", str(TOTAL), "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
    "-c:a", "aac", "-b:a", "192k", "-threads", "2", "-movflags", "+faststart", "publicar/reel_recuerdo_udes.mp4"], check=True)
print("ok", TOTAL, len(ev), OV)
