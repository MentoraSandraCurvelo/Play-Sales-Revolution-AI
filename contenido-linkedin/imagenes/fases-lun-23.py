import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src,out=sys.argv[1],sys.argv[2]
F="/mnt/skills/examples/canvas-design/canvas-fonts/"
B=lambda s: ImageFont.truetype(F+"Outfit-Bold.ttf",s); R=lambda s: ImageFont.truetype(F+"Outfit-Regular.ttf",s)
W,H=1080,1350
p=Image.open(src).convert("RGB"); k=H/p.height; p=p.resize((int(p.width*k),H),Image.LANCZOS)
c=Image.new("RGB",(W,H),(10,8,9)); c.paste(p,(-230,0))
bl=c.filter(ImageFilter.GaussianBlur(10))
m=Image.new('L',(W,H),0); md=ImageDraw.Draw(m)
md.ellipse((140,250,470,640),fill=255); md.polygon([(20,560),(520,520),(560,1350),(0,1350)],fill=255)
m=m.filter(ImageFilter.GaussianBlur(40))
c=Image.composite(c,bl,m)
from PIL import ImageChops
mx=Image.new("L",(W,H),0); dx=ImageDraw.Draw(mx)
for x in range(W): dx.line([(x,0),(x,H)],fill=0 if x<400 else min(250,int(250*(x-400)/170)))
my=Image.new("L",(W,H),0); dy=ImageDraw.Draw(my)
for y in range(H):
    v=0
    if y<330: v=int(150*(1-y/330))
    if y>1040: v=int(245*(y-1040)/200) if y<1240 else 245
    dy.line([(0,y),(W,y)],fill=v)
al=ImageChops.lighter(mx,my)
ov=Image.new("RGBA",(W,H),(12,8,10,255)); ov.putalpha(al)
c=Image.alpha_composite(c.convert("RGBA"),ov); d=ImageDraw.Draw(c)
WH=(246,244,240); RED=(255,60,60); MU=(190,186,180); X=590
d.text((X,90),"IAM™ · IA EMPRESARIAL",font=B(22),fill=RED)
for i,t in enumerate(["Las 3 fases","de la IA","empresarial"]): d.text((X,128+i*66),t,font=B(60),fill=WH)
d.text((X,345),"No empieza con la herramienta.",font=R(25),fill=MU)
d.text((X,377),"Empieza midiendo.",font=B(25),fill=WH)
rows=[("1","ADOPCIÓN","Horas recuperadas","por persona"),("2","CONEXIÓN","IA integrada a tu ERP,","CRM y sistemas"),("3","GOBERNANZA","El plan, con lo que","ya probaste y mediste")]
y=480
for n,t,s1,s2 in rows:
    d.rounded_rectangle((X,y,X+64,y+64),radius=14,fill=(224,0,0))
    w=d.textlength(n,font=B(36)); d.text((X+32-w/2,y+9),n,font=B(36),fill=WH)
    d.text((X+86,y-2),t,font=B(32),fill=WH); d.text((X+86,y+38),s1,font=R(24),fill=MU); d.text((X+86,y+66),s2,font=R(24),fill=MU)
    if n!="3": d.line([(X+32,y+74),(X+32,y+150)],fill=(224,0,0),width=3)
    y+=160
d.line([(X,995),(W-50,995)],fill=(70,64,66),width=2)
d.text((X,1020),"El criterio humano",font=B(30),fill=WH)
d.text((X,1058),"decide dónde",font=B(30),fill=WH)
d.text((X,1096),"entra la IA.",font=B(30),fill=RED)
d.text((60,1290),"Sandra Curvelo · Fundadora IAM™",font=B(24),fill=WH)
c.convert("RGB").save(out,quality=92)
