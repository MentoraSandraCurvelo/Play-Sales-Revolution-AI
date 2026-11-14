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
    if y<300: v=int(200*(1-y/300))
    if y>1060: v=min(250,int(250*(y-1060)/120))
    dy.line([(0,y),(W,y)],fill=v)
ov=Image.new("RGBA",(W,H),(6,6,8,255)); ov.putalpha(my); c=Image.alpha_composite(c,ov)

def holo(cx,cy,t,size,n=''):
    global c
    f=B(size); pre=n+'  ' if n else ''; pw=ImageDraw.Draw(c).textlength(pre,font=f); tw=ImageDraw.Draw(c).textlength(pre+t,font=f)
    x0,y0,x1,y1=int(cx-tw/2-22),int(cy-size*0.7),int(cx+tw/2+22),int(cy+size*0.75)
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    ld.rectangle((x0,y0,x1,y1),fill=(40,4,8,170))
    ld.line([(x0,y0),(x1,y0)],fill=(255,70,70,255),width=2); ld.line([(x0,y1),(x1,y1)],fill=(255,70,70,255),width=2)
    gl=lay.filter(ImageFilter.GaussianBlur(10)); c=Image.alpha_composite(c,gl); c=Image.alpha_composite(c,lay)
    tl=Image.new("RGBA",(W,H),(0,0,0,0)); td=ImageDraw.Draw(tl)
    td.text((cx-tw/2,cy-size*0.62),pre+t,font=f,fill=(255,90,90,255))
    c=Image.alpha_composite(c,tl.filter(ImageFilter.GaussianBlur(6)))
    td2=ImageDraw.Draw(c)
    if n: td2.text((cx-tw/2,cy-size*0.62),n,font=f,fill=(255,60,60))
    td2.text((cx-tw/2+pw,cy-size*0.62),t,font=f,fill=(255,236,236))
holo(655,833,"ADOPCIÓN",44,"1")
holo(810,680,"CONEXIÓN",44,"2")
holo(880,549,"GOBERNANZA",38,"3")
d=ImageDraw.Draw(c)
WH=(248,246,242); RED=(255,60,60)

def relieve(x,y,t,size,front,depth):
    global c
    f=B(size)
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
    gd.text((x,y),t,font=f,fill=(230,0,0,200)); c=Image.alpha_composite(c,gl.filter(ImageFilter.GaussianBlur(18)))
    ex=Image.new("RGBA",(W,H),(0,0,0,0)); ed=ImageDraw.Draw(ex)
    for i in range(depth,0,-1):
        sh=int(70+90*(1-i/depth)); ed.text((x+i,y+i),t,font=f,fill=(sh,0,6,255))
    c=Image.alpha_composite(c,ex)
    fr=Image.new("RGBA",(W,H),(0,0,0,0)); fd=ImageDraw.Draw(fr); fd.text((x,y),t,font=f,fill=front)
    c=Image.alpha_composite(c,fr)
    hl=Image.new("RGBA",(W,H),(0,0,0,0)); hd=ImageDraw.Draw(hl); hd.text((x-1,y-1),t,font=f,fill=(255,255,255,90)); c=Image.alpha_composite(c,hl)
relieve(56,40,"LAS 3 FASES",128,(255,255,255,255),10)
relieve(60,190,"DE LA IA EMPRESARIAL",62,(255,70,70,255),6)
d=ImageDraw.Draw(c)
d.text((60,1196),"Medir antes. El criterio humano",font=B(40),fill=WH)
d.text((60,1246),"decide dónde entra la IA.",font=B(40),fill=RED)
t="Sandra Curvelo · IAM™"; d.text((60,1302),t,font=R(24),fill=(200,196,190))
c.convert("RGB").save(D+"/lun-23-am-v5.jpg",quality=92)
