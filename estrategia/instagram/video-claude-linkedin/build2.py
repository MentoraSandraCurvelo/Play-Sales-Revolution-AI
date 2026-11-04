import subprocess, shutil
# Escenas alineadas con las pausas de la voz clonada de Sandra (toma 2, 13,3 s, entra a los 0,8 s).
D = [2.7, 3.0, 1.8, 1.9, 3.0, 3.6]
X, FPS, DELAY = 0.5, 30, 800
shutil.copy("dl/voz_sandra_2.mp3", "voz_sandra.mp3")
shutil.copy("dl/nave_clip.mp4", "nave_clip.mp4")
subprocess.run(["node", "shot.js"], check=True)
subprocess.run(["node", "shot_overlay.js"], check=True)
args = ["-i", "nave_clip.mp4", "-i", "o1.png"]
filt = (f"[0:v]trim=0:{D[0]+X},setpts=PTS-STARTPTS,fps={FPS},scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,setsar=1[c];[c][1:v]overlay=0:0,format=yuv420p[v1];")
for i in range(2, 7):
    dur = D[i-1] + X
    args += ["-i", f"f{i}.png"]
    filt += (f"[{i}:v]scale=1188:2112,zoompan=z='min(zoom+0.0009,1.1)':x='iw/2-(iw/zoom/2)':"
             f"y='ih/2-(ih/zoom/2)':d={int(dur*FPS)}:s=1080x1920:fps={FPS},setsar=1,format=yuv420p[v{i}];")
off, prev = 0.0, "[v1]"
for i in range(2, 7):
    off = round(off + D[i-2], 2)
    out = "[out]" if i == 6 else f"[x{i}]"
    filt += f"{prev}[v{i}]xfade=transition=fade:duration={X}:offset={off}{out};"
    prev = out
total = round(sum(D) + X, 2)
args += ["-i", "voz_sandra.mp3", "-i", "musica.mp3"]
filt += (f"[7:a]adelay={DELAY}|{DELAY},volume=1.0,apad[vo];[8:a]atrim=0:{total},volume=0.22,"
         f"afade=t=out:st={total-1.5}:d=1.5[mu];[mu][vo]amix=inputs=2:duration=first:dropout_transition=0[aout]")
cmd = ["ffmpeg", "-y", "-loglevel", "error"] + args + ["-filter_complex", filt, "-map", "[out]", "-map", "[aout]",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
       "-t", str(total), "-movflags", "+faststart", "reel_voz_sandra.mp4"]
subprocess.run(cmd, check=True)
print("ok", total)
