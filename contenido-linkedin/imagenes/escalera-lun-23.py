import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=sys.argv[1]
F="/mnt/skills/examples/canvas-design/canvas-fonts/"
B=lambda s: ImageFont.truetype(F+"Outfit-Bold.ttf",s)
R=lambda s: ImageFont.truetype(F+"Outfit-Regular.ttf",s)
W,H=1080,1350
c=Image.new("RGB",(W,H),(8,8,10))
src=Image.open(D+"/v1.png").convert("RGB")
k=W/1280
crop=src.resize((W,int(720*k)))
top=250; c.paste(crop,(0,top))
# gradients top and bottom
g=Image.new("L",(W,H),0); gd=ImageDraw.Draw(g)
for y in range(H):
    a=0
    if y<top+90: a=255 if y<top else int(255*(1-(y-top)/90))
    if y>720: a=max(a,min(255,int(255*(y-720)/140)))
    gd.line([(0,y),(W,y)],fill=a)
c=Image.composite(Image.new("RGB",(W,H),(8,8,10)),c,g)
d=ImageDraw.Draw(c)
RED=(224,0,0); WH=(244,242,238); MU=(170,166,160)
d.text((70,70),"IAM™ · INTELIGENCIA ARTIFICIAL EMPRESARIAL",font=B(24),fill=(255,77,77))
d.text((70,112),"Las 3 fases de la IA",font=B(64),fill=WH)
d.text((70,184),"empresarial",font=B(64),fill=WH)
# badges on steps (crop coords -> canvas)
def badge(x,y,n):
    x=int(x*k); y=int(y*k)+top
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gdw=ImageDraw.Draw(glow)
    gdw.ellipse((x-46,y-46,x+46,y+46),fill=(224,0,0,140)); glow=glow.filter(ImageFilter.GaussianBlur(14))
    c.paste(glow,(0,0),glow)
    d.ellipse((x-30,y-30,x+30,y+30),fill=RED,outline=WH,width=3)
    t=str(n); w=d.textlength(t,font=B(34)); d.text((x-w/2,y-22),t,font=B(34),fill=WH)
badge(440,470,1); badge(700,380,2); badge(940,288,3)
y0=870
rows=[("1","ADOPCIÓN","Las horas que recupera cada persona"),("2","CONEXIÓN","IA integrada a tu ERP, tu CRM y tus sistemas"),("3","GOBERNANZA","El plan, con lo que ya probaste y mediste")]
for i,(n,t,s) in enumerate(rows):
    y=y0+i*98
    d.ellipse((70,y,124,y+54),fill=RED); w=d.textlength(n,font=B(30)); d.text((97-w/2,y+8),n,font=B(30),fill=WH)
    d.text((150,y-4),t,font=B(34),fill=WH); d.text((150,y+38),s,font=R(26),fill=MU)
d.line([(70,1162),(W-70,1162)],fill=(60,60,64),width=2)
d.text((70,1185),"Medir antes. Mapear el proceso.",font=B(30),fill=WH)
d.text((70,1225),"El criterio humano decide dónde entra la IA.",font=B(30),fill=(255,77,77))
d.text((70,1285),"Sandra Curvelo · IAM™",font=R(22),fill=MU)
c.save(D+"/lun-23-am.jpg",quality=92)
