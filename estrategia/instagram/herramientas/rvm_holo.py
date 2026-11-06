"""Recorte RVM sobre escenario animado + entrada holográfica (Sandra se materializa).
uso: rvm_holo.py entrada.mp4 fondo_loop.mp4 salida.mp4 [y_crop] [intro_seg]"""
import sys, subprocess, numpy as np, cv2, onnxruntime as ort
src, bgv, out = sys.argv[1:4]
ycrop = int(sys.argv[4]) if len(sys.argv) > 4 else 40
INTRO = float(sys.argv[5]) if len(sys.argv) > 5 else 1.4
W, H, FPS = 1080, 1920, 30
MODEL = "/tmp/claude-0/-home-user-Play-Sales-Revolution-AI/56e793ef-bf15-5592-8182-e12bf01cfd05/scratchpad/modelos/rvm.onnx"
sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
dsr = np.array([0.4], np.float32)
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale=-2:2266,crop={W}:{H}:(iw-{W})/2:{ycrop}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
bgd = subprocess.Popen(["ffmpeg", "-v", "error", "-stream_loop", "-1", "-i", bgv, "-vf", f"scale={W}:{H}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)
yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
scan = (0.72 + 0.28 * (np.sin(np.arange(H, dtype=np.float32) * 0.9) > 0))[:, None, None]
cyan = np.array([0.35, 0.95, 1.0], np.float32)
rng = np.random.default_rng(7); n = 0
def sm(e0, e1, x): t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
while True:
    buf = dec.stdout.read(W * H * 3); bb = bgd.stdout.read(W * H * 3)
    if len(buf) < W * H * 3 or len(bb) < W * H * 3: break
    t = n / FPS
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    bg = np.frombuffer(bb, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    bg_soft = cv2.GaussianBlur(bg, (0, 0), 2.2); glow = cv2.GaussianBlur(bg, (0, 0), 40)
    fgr, pha, *rec = sess.run(None, {"src": fr.transpose(2, 0, 1)[None], "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": dsr})
    a = np.clip((pha[0, 0] - 0.04) / 0.92, 0, 1)[..., None]
    f = np.clip(fgr[0].transpose(1, 2, 0), 0, 1)
    # luz del escenario sobre ella: borde frío a un lado y rojo IAM al otro
    xs = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    rim = np.clip(cv2.GaussianBlur(a[..., 0], (0, 0), 3)[..., None] - cv2.GaussianBlur(a[..., 0], (0, 0), 14)[..., None], 0, 1)
    f = np.clip(f + rim * 0.9 * ((1 - xs) * np.array([0.1, 0.7, 0.9], np.float32) + xs * np.array([0.9, 0.12, 0.1], np.float32)), 0, 1)
    k = 0.0
    if t < INTRO:
        k = 1 - sm(INTRO * 0.55, INTRO, t)                 # cuánto holograma queda
        line = 1.05 - sm(0, INTRO * 0.7, t) * 1.15         # la línea de escaneo sube
        reveal = sm(line - 0.02, line + 0.02, yy)
        edge = np.exp(-((yy - line) / 0.012) ** 2) * a * 1.6
        holo = (0.25 + 0.75 * f.mean(2, keepdims=True)) * cyan * scan
        f = f * (1 - k) + holo * k + edge * cyan
        fl = 1 - k * 0.25 * rng.random()
        a = a * reveal * fl * (1 - 0.35 * k)
        if k > 0.05:
            sh = int(rng.integers(-6, 7) * k); a = np.roll(a, sh, 1); f = np.roll(f, sh, 1)
    edgeb = cv2.GaussianBlur(a[..., 0], (0, 0), 6)[..., None]
    wrap = np.clip((1 - edgeb) * a, 0, 1) * 0.16
    comp = f * a + bg_soft * (1 - a)
    comp = comp * (1 - wrap) + glow * wrap
    comp = np.clip((comp - 0.5) * 1.06 + 0.5, 0, 1)
    shp = cv2.GaussianBlur(comp, (0, 0), 1.2); comp = np.clip(comp + (comp - shp) * 0.35 * a, 0, 1)
    comp = np.clip(comp + np.random.normal(0, 0.008, comp.shape).astype(np.float32), 0, 1)
    enc.stdin.write((comp * 255).astype(np.uint8).tobytes()); n += 1
enc.stdin.close(); enc.wait(); dec.kill(); bgd.kill()
print("frames", n)
