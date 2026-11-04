import subprocess, sys

# Duración de cada escena, sincronizada con la voz en off (unos 15 segundos) más el cierre.
D = [2.8, 2.6, 2.4, 2.8, 3.0, 3.0]
X = 0.5  # duración de cada transición
FPS = 30

subprocess.run(["node", "shot.js"], check=True)

args, filt = [], ""
for i, d in enumerate(D, 1):
    dur = d + X
    args += ["-i", f"f{i}.png"]
    frames = int(dur * FPS)
    filt += (f"[{i-1}:v]scale=1188:2112,zoompan=z='min(zoom+0.0009,1.1)':"
             f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={FPS},setsar=1[v{i}];")

chain, off, prev = "", 0.0, "[v1]"
for i in range(2, len(D) + 1):
    off = round(off + D[i - 2], 2)
    out = "[out]" if i == len(D) else f"[x{i}]"
    chain += f"{prev}[v{i}]xfade=transition=fade:duration={X}:offset={off}{out};"
    prev = out
filt += chain.rstrip(";")

audio = sys.argv[1:]  # opcional: voz.mp3 musica.mp3
cmd = ["ffmpeg", "-y", "-loglevel", "error"] + args
if len(audio) == 2:
    cmd += ["-i", audio[0], "-i", audio[1]]
    n = len(D)
    filt += (f";[{n}:a]adelay=300|300,volume=1.0[vo];[{n+1}:a]volume=0.22,afade=t=out:st=15.6:d=1.5[mu];"
             f"[vo][mu]amix=inputs=2:duration=longest:dropout_transition=0[aout]")
    cmd += ["-filter_complex", filt, "-map", "[out]", "-map", "[aout]", "-c:a", "aac", "-shortest"]
    name = "secuencia_con_audio.mp4"
else:
    cmd += ["-filter_complex", filt, "-map", "[out]"]
    name = "secuencia_sin_audio.mp4"
cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS), name]
subprocess.run(cmd, check=True)
print(name)
