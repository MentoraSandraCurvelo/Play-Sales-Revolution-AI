"""Recorte de alta calidad con RobustVideoMatting + composición cinematográfica.
uso: rvm_comp.py entrada.mov fondo.png salida.mp4 [y_crop] [t_ini] [t_fin]"""
import sys, subprocess, numpy as np, cv2, onnxruntime as ort
src, bgp, out = sys.argv[1:4]
ycrop = int(sys.argv[4]) if len(sys.argv) > 4 else 40
ss = sys.argv[5] if len(sys.argv) > 5 else "0"; to = sys.argv[6] if len(sys.argv) > 6 else None
W, H = 1080, 1920
MODEL = "/tmp/claude-0/-home-user-Play-Sales-Revolution-AI/56e793ef-bf15-5592-8182-e12bf01cfd05/scratchpad/modelos/rvm.onnx"
sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
dsr = np.array([0.4], np.float32)
bg = cv2.cvtColor(cv2.imread(bgp), cv2.COLOR_BGR2RGB)
bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
bg_soft = cv2.GaussianBlur(bg, (0, 0), 4)                      # profundidad de campo
# luz ambiente del fondo para el "light wrap"
glow = cv2.GaussianBlur(bg, (0, 0), 40)
mean_bg = bg.reshape(-1, 3).mean(0)
dec_cmd = ["ffmpeg", "-v", "error", "-ss", ss] + (["-to", to] if to else []) + ["-i", src,
           "-vf", f"scale=-2:2266,crop={W}:{H}:(iw-{W})/2:{ycrop}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
dec = subprocess.Popen(dec_cmd, stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-ss", ss] + (["-to", to] if to else []) + ["-i", src, "-map", "0:v", "-map", "1:a?",
                        "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", out], stdin=subprocess.PIPE)
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    x = fr.transpose(2, 0, 1)[None]
    fgr, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": dsr})
    a = pha[0, 0]
    a = np.clip((a - 0.04) / 0.92, 0, 1)[..., None]
    f = np.clip(fgr[0].transpose(1, 2, 0), 0, 1)                # color de primer plano sin el reflejo de la pared
    # igualar un poco el tono de la persona a la escena (suave, 12%)
    f = f * (1 - 0.05) + f * (mean_bg / max(mean_bg.mean(), 1e-3)) * 0.05
    # light wrap: el fondo "envuelve" los bordes
    edge = np.clip(cv2.GaussianBlur(a, (0, 0), 6)[..., None] if a.ndim == 2 else cv2.GaussianBlur(a[..., 0], (0, 0), 6)[..., None], 0, 1)
    wrap = np.clip((1 - edge) * a, 0, 1) * 0.18
    comp = f * a + bg_soft * (1 - a)
    comp = comp * (1 - wrap) + glow * wrap
    # contraste y nitidez de la persona (unsharp suave)
    comp = np.clip((comp - 0.5) * 1.06 + 0.5, 0, 1)
    sh = cv2.GaussianBlur(comp, (0, 0), 1.2); comp = np.clip(comp + (comp - sh) * 0.35 * a, 0, 1)
    # grano fino para que todo parezca grabado junto
    comp = np.clip(comp + np.random.normal(0, 0.008, comp.shape).astype(np.float32), 0, 1)
    enc.stdin.write((comp * 255).astype(np.uint8).tobytes()); n += 1
enc.stdin.close(); enc.wait(); dec.wait()
print("frames", n)
