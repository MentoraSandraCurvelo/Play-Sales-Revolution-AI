"""Quita la pared blanca de las tomas de ventas con un segmentador local y pone el fondo Wall Street."""
import subprocess, numpy as np, cv2, mediapipe as mp, urllib.request, os
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
W, H = 1080, 1920
MODEL = "selfie_multiclass.tflite"
if not os.path.exists(MODEL):
    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite", MODEL)
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=MODEL), running_mode=vision.RunningMode.VIDEO,
    output_confidence_masks=True, output_category_mask=False))
bg = cv2.cvtColor(cv2.imread("bg_ws.png"), cv2.COLOR_BGR2RGB)
bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_AREA)
bg = cv2.GaussianBlur(bg, (0, 0), 3).astype(np.float32)
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "ventas_src.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-i", "ventas_src.mp4", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "19", "-preset", "fast",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "ventas_comp.mp4"], stdin=subprocess.PIPE)
prev = None; i = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    small = cv2.resize(fr, (540, 960), interpolation=cv2.INTER_AREA)
    res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(small)), int(i * 1000 / 30))
    a = 1.0 - res.confidence_masks[0].numpy_view().astype(np.float32)   # 0 = fondo
    a = cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)
    if prev is not None: a = 0.65 * a + 0.35 * prev                       # menos parpadeo
    prev = a
    a = np.clip((a - 0.35) / 0.4, 0, 1)
    a = cv2.GaussianBlur(a, (0, 0), 2.0)[..., None]
    out = fr.astype(np.float32) * a + bg * (1 - a)
    enc.stdin.write(out.astype(np.uint8).tobytes()); i += 1
enc.stdin.close(); enc.wait(); dec.wait()
print("frames", i)
