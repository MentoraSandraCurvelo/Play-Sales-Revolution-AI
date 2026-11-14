import sys
from PIL import Image, ImageDraw, ImageFont, ImageChops
D=sys.argv[1]; F="/mnt/skills/examples/canvas-design/canvas-fonts/"
B=lambda s: ImageFont.truetype(F+"Outfit-Bold.ttf",s); R=lambda s: ImageFont.truetype(F+"Outfit-Regular.ttf",s)
W,H=1080,1350
src=Image.open(D+"/r3.png").convert("RGB")
k=W/src.width; p=src.resize((W,int(src.height*k)),Image.LANCZOS)
c=Image.new("RGB",(W,H),(6,6,8)); c.paste(p,(0,0))
my=Image.new("L",(W,H),0); dy=ImageDraw.Draw(my)
for y in range(H):
    v=0
    if y<300: v=int(200*(1-y/300))
    if y>1150: v=min(240,int(240*(y-1150)/110))
    dy.line([(0,y),(W,y)],fill=v)
ov=Image.new("RGBA",(W,H),(6,6,8,255)); ov.putalpha(my)
c=Image.alpha_composite(c.convert("RGBA"),ov)
d=ImageDraw.Draw(c,"RGBA")
WH=(248,246,242); RED=(255,60,60)
d.text((60,52),"IAM™ · INTELIGENCIA ARTIFICIAL EMPRESARIAL",font=B(22),fill=RED)
d.text((60,86),"Las 3 fases de",font=B(62),fill=WH)
d.text((60,152),"la IA empresarial",font=B(62),fill=WH)
def pill(x,y,n,t,s):
    f=B(s); w=d.textlength(f"{n}  {t}",font=f)
    d.rounded_rectangle((x-14,y-8,x+w+14,y+s+12),radius=12,fill=(8,6,8,205),outline=(224,0,0,255),width=2)
    d.text((x,y),n,font=f,fill=RED); d.text((x+d.textlength(n+"  ",font=f),y),t,font=f,fill=WH)
k2=W/928
pill(int(165*k2),int(930*k2),"1","ADOPCIÓN",32)
pill(int(600*k2),int(850*k2),"2","CONEXIÓN",30)
pill(int(640*k2),int(752*k2),"3","GOBERNANZA",28)
d.text((60,1238),"Medir antes. El criterio humano decide",font=B(30),fill=WH)
d.text((60,1276),"dónde entra la IA.",font=B(30),fill=RED)
t="Sandra Curvelo · IAM™"; d.text((W-60-d.textlength(t,font=R(20)),1288),t,font=R(20),fill=(200,196,190))
c.convert("RGB").save(D+"/lun-23-am-v4.jpg",quality=92)
