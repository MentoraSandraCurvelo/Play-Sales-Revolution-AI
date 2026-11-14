import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=sys.argv[1]; F="/mnt/skills/examples/canvas-design/canvas-fonts/"
B=lambda s: ImageFont.truetype(F+"Outfit-Bold.ttf",s); R=lambda s: ImageFont.truetype(F+"Outfit-Regular.ttf",s)
W,H=1080,1350
c=Image.open(D+"/s1.png").convert("RGB").resize((W,H),Image.LANCZOS)
ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
for y in range(H):
    a=0
    if y<260: a=int(200*(1-y/260))
    if y>1150: a=max(a,int(225*(y-1150)/200))
    od.line([(0,y),(W,y)],fill=(5,5,8,a))
c=Image.alpha_composite(c.convert("RGBA"),ov)
d=ImageDraw.Draw(c)
WH=(246,244,240); RED=(255,70,70); MU=(200,196,190)
d.text((60,48),"IAM™ · INTELIGENCIA ARTIFICIAL EMPRESARIAL",font=B(22),fill=RED)
d.text((60,82),"Las 3 fases de",font=B(60),fill=WH)
d.text((60,146),"la IA empresarial",font=B(60),fill=WH)
def label(x,y,n,t,s):
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.text((x+2,y+3),f"{n}  {t}",font=B(s),fill=(0,0,0,230)); sh=sh.filter(ImageFilter.GaussianBlur(4))
    c.alpha_composite(sh)
    d.text((x,y),n,font=B(s),fill=RED); w=d.textlength(n+"  ",font=B(s)); d.text((x+w,y),t,font=B(s),fill=WH)
label(300,1100,"1","ADOPCIÓN",42)
label(615,920,"2","CONEXIÓN",34)
label(640,795,"3","GOBERNANZA",28)
d.text((60,1238),"Medir antes. El criterio humano decide",font=B(30),fill=WH)
d.text((60,1276),"dónde entra la IA.",font=B(30),fill=RED)
d.text((W-60-d.textlength("Sandra Curvelo · IAM™",font=R(20)),1288),"Sandra Curvelo · IAM™",font=R(20),fill=MU)
c.convert("RGB").save(D+"/lun-23-am-v2.jpg",quality=92)
