import subprocess, json, os
# Tramos elegidos de la toma (segundos del archivo original)
SEG = [
    (4.00, 8.55), (16.00, 24.35), (69.10, 73.60), (83.30, 86.90), (91.35, 104.80),
    (129.80, 131.75), (146.85, 148.25), (148.60, 154.55), (185.35, 188.00), (192.70, 197.75),
    (202.00, 210.35), (210.45, 212.60), (220.45, 222.45), (227.90, 235.60),
]
json.dump(SEG, open("seg.json", "w"))
os.makedirs("parts", exist_ok=True)
lst = []
for i, (a, b) in enumerate(SEG):
    out = f"parts/p{i:02d}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a}", "-to", f"{b}", "-i", "IMG_9913.mov",
                    "-vf", "scale=-2:2266,crop=1080:1920:(iw-1080)/2:40,fps=30,setsar=1",
                    "-af", f"afade=t=in:d=0.04,afade=t=out:st={b-a-0.05:.2f}:d=0.05",
                    "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-threads", "2", out], check=True)
    lst.append(f"file '{out}'")
open("parts.txt", "w").write("\n".join(lst) + "\n")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "parts.txt", "-c", "copy",
                "-movflags", "+faststart", "cut.mp4"], check=True)
print("ok", round(sum(b - a for a, b in SEG), 2))
