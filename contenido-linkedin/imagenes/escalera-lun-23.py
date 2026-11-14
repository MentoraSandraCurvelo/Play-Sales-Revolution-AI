import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
D=sys.argv[1]; F="/mnt/skills/examples/canvas-design/canvas-fonts/"
B=lambda s: ImageFont.truetype(F+"Outfit-Bold.ttf",s); R=lambda s: ImageFont.truetype(F+"Outfit-Regular.ttf",s)
W,H=1080,1350
bg=Image.open(D+"/bg2.png").convert("RGB").resize((W,H),Image.LANCZOS).convert("RGBA")
cut=Image.open(D+"/cut.png").convert("RGBA")
s=1.1; cut=cut.resize((int(cut.width*s),int(cut.height*s)),Image.LANCZOS)
ox,oy=-300,-20
# grade subject to scene: slightly darker, warmer-red
rgb=cut.convert("RGB"); a=cut.split()[-1]
rgb=ImageEnhance.Brightness(rgb).enhance(0.84); rgb=ImageEnhance.Contrast(rgb).enhance(1.05)
tint=Image.new("RGB",rgb.size,(255,40,40)); rgb=Image.blend(rgb,tint,0.06)
dk=Image.new("L",rgb.size,0); dd=ImageDraw.Draw(dk)
for yy in range(rgb.height):
    fy=yy+oy
    v=0 if fy<980 else min(215,int(215*(fy-980)/170))
    dd.line([(0,yy),(rgb.width,yy)],fill=v)
rgb=Image.composite(Image.new("RGB",rgb.size,(10,6,8)),rgb,dk)
cut=rgb.convert("RGBA"); cut.putalpha(a)
# red rim glow behind subject
glow=Image.new("RGBA",(W,H),(0,0,0,0)); g=Image.new("RGBA",cut.size,(230,20,20,0)); g.putalpha(a.point(lambda v: int(v*0.85)))
glow.paste(g,(ox+14,oy),g); glow=glow.filter(ImageFilter.GaussianBlur(22))
bg=Image.alpha_composite(bg,glow)
# soft floor shadow
bg.alpha_composite(cut,(ox,oy))
c=bg
my=Image.new("L",(W,H),0); dy=ImageDraw.Draw(my)
for y in range(H):
    v=0
    if y<280: v=int(170*(1-y/280))
    if y>1100: v=min(250,int(250*(y-1100)/130))
    dy.line([(0,y),(W,y)],fill=v)
ov=Image.new("RGBA",(W,H),(6,6,8,255)); ov.putalpha(my); c=Image.alpha_composite(c,ov)
d=ImageDraw.Draw(c)
WH=(248,246,242); RED=(255,60,60)
d.text((W-60-d.textlength("IAM™ · INTELIGENCIA ARTIFICIAL EMPRESARIAL",font=B(20)),56),"IAM™ · INTELIGENCIA ARTIFICIAL EMPRESARIAL",font=B(20),fill=RED)
for i,t in enumerate(["Las 3 fases","de la IA empresarial"]):
    w=d.textlength(t,font=B(58)); d.text((W-60-w,88+i*64),t,font=B(58),fill=WH)
d.text((60,1236),"Medir antes. El criterio humano decide",font=B(30),fill=WH)
d.text((60,1274),"dónde entra la IA.",font=B(30),fill=RED)
t="Sandra Curvelo · IAM™"; d.text((W-60-d.textlength(t,font=R(20)),1286),t,font=R(20),fill=(200,196,190))
c.convert("RGB").save(D+"/lun-23-am-v5.jpg",quality=92)
