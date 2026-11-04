import json, subprocess, sys
S = "/tmp/claude-0/-home-user-Play-Sales-Revolution-AI/56e793ef-bf15-5592-8182-e12bf01cfd05/scratchpad"
T = S + "/tomas_ventas"
# Palabras con tiempos globales del audio unido (transcripción ElevenLabs Scribe)
W = json.load(open("words.json"))
# Tramos de cada toma (segundos locales) y desplazamiento al tiempo final
A = (0.7, 7.6); B = (0.35, 16.4); C = (0.85, 12.35); END = 2.5
dA = A[1] - A[0]; dB = B[1] - B[0]; dC = C[1] - C[0]
oB, oC = dA, dA + dB
TOTAL = round(dA + dB + dC + END, 2)
def final(g):
    if g < 8.6: return g - A[0]
    if g < 26.5: return (g - 9.13) - B[0] + oB
    return (g - 27.03) - C[0] + oC
MOCK = (12.4, 17.0)       # pantallas del plugin (sin subtítulos encima)
DM = (30.0, oC + dC)       # notificación de mensaje directo
ROBOT = 1.6                # escena del robot al inicio

KEY_RED = {"claude", "vendedor", "nadie", "riesgo", "caos", "amplificar", "venta", "ventas"}
KEY_AMB = {"método", "herramienta", "proceso", "comercial", "siete", "países", "guía", "equipo", "contando"}
def fmt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
def word_ass(w):
    clean = w.strip("¿?,.").lower()
    txt = w.replace("Klaude", "Claude")
    if clean in ("venta",): txt = txt.upper()
    if clean in KEY_RED: return r"{\c&H2D2DFF&}" + txt + r"{\c&HFFFFFF&}"
    if clean in KEY_AMB: return r"{\c&H20B0FF&}" + txt + r"{\c&HFFFFFF&}"
    return txt
# trozos de máximo 3 palabras, cortando en puntuación
chunks, cur = [], []
for w in W:
    if w["type"] != "word": continue
    cur.append(w)
    if len(cur) == 3 or w["text"][-1] in ",.?":
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
ev = []
for i, ch in enumerate(chunks):
    st = final(ch[0]["start"]); en = final(ch[-1]["end"]) + 0.12
    if i + 1 < len(chunks): en = min(en + 0.25, final(chunks[i + 1][0]["start"]))
    if st < ROBOT - 0.05 and en <= ROBOT: pass
    if not (en <= MOCK[0] or st >= MOCK[1]): continue
    ev.append(f"Dialogue: 0,{fmt(max(st,0))},{fmt(en)},Sub,,0,0,0,,{'  '.join(word_ass(w['text']) for w in ch)}")
ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Black,92,&H00FFFFFF,&H00FFFFFF,&H00141414,&H80000000,1,0,0,0,100,100,2,0,1,7,3,2,70,70,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open("subs.ass", "w").write(ass)

inp = ["-i", f"{T}/IMG_9883.mov", "-i", f"{T}/IMG_9884.mov", "-i", f"{T}/IMG_9886.mov",
       "-loop", "1", "-t", str(TOTAL), "-i", f"{S}/portadas/r3.png",
       "-loop", "1", "-t", str(TOTAL), "-i", "o1.png", "-loop", "1", "-t", str(TOTAL), "-i", "o2.png",
       "-loop", "1", "-t", str(TOTAL), "-i", "o3.png", "-loop", "1", "-t", str(TOTAL), "-i", "o4.png",
       "-loop", "1", "-t", str(END), "-i", "o5.png",
       "-stream_loop", "-1", "-i", f"{S}/video1/musica.mp3"]
V = lambda i, a, b, crop="": (f"[{i}:v]trim={a}:{b},setpts=PTS-STARTPTS,scale=-2:2266,crop=1080:1920:(iw-1080)/2:60,fps=30,setsar=1,format=yuv420p[v{i}];"
                              f"[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];")
fc = V(0, *A) + V(1, *B) + V(2, *C)
fc += f"[8:v]scale=1080:1920,fps=30,setsar=1,format=yuv420p[v8];anullsrc=r=48000:cl=mono,atrim=0:{END}[a8];"
fc += "[a0]aresample=48000,aformat=channel_layouts=mono[b0];[a1]aresample=48000,aformat=channel_layouts=mono[b1];[a2]aresample=48000,aformat=channel_layouts=mono[b2];"
fc += "[v0][b0][v1][b1][v2][b2][v8][a8]concat=n=4:v=1:a=1[base][voz];"
fc += "[3:v]split[r1][r2];[r1]scale=-2:1920,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18[rbg];[r2]scale=1080:-2[rfg];[rbg][rfg]overlay=0:(H-h)/2-120,fps=30,format=yuva420p[rob];"
fc += f"[base][rob]overlay=0:0:enable='between(t,0,{ROBOT})'[x1];"
fc += f"[x1][4:v]overlay=0:0:enable='between(t,{MOCK[0]},13.85)'[x2];"
fc += f"[x2][5:v]overlay=0:0:enable='between(t,13.85,15.05)'[x3];"
fc += f"[x3][6:v]overlay=0:0:enable='between(t,15.05,{MOCK[1]})'[x4];"
fc += f"[x4][7:v]overlay=0:0:enable='between(t,{DM[0]},{DM[1]})'[x5];"
fc += "[x5]ass=subs.ass[vout];"
fc += "[voz]loudnorm=I=-15:TP=-1.5:LRA=11[vz];"
fc += f"[9:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,aresample=48000,volume=0.10,afade=t=in:d=0.8,afade=t=out:st={TOTAL-2.2}:d=2.2[mu];"
fc += "[vz][mu]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
cmd = ["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
       "-t", str(TOTAL), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
       "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart", "reel_ventas.mp4"]
subprocess.run(cmd, check=True)
print("ok", TOTAL, len(ev), "subtitulos")
