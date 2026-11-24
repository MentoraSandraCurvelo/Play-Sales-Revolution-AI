import sys
P=[
("agentica","conectores.jpg","dark","Claude no solo escribe.","Trabaja por ti.","Tips de Claude",(1250,0,50)),
("iae","iae2.jpg","dark","Pagaste la IA.","¿Alguien la usa?","Método IAE™",(1080,-40,50)),
("matia","robot.jpg","light","Claude actualiza","mi CRM.","Tips de Claude · Demo simulada",(1450,0,62)),
("prospecta","gorra.jpg","light","Claude prospecta.","Yo apruebo.","Tips de Claude · Demo simulada",(1080,-170,50)),
("alpina","alpina.jpg","dark","No llames en frío.","Llega sabiendo.","Recuerdos",(1300,-540,50)),
("udes","udes.jpg","light","Instagram: interrupción.","LinkedIn: intención.","Recuerdos",(1300,-430,58)),
("correo","correo.jpg","dark","Claude lee mi correo.","Yo solo apruebo.","Tips de Claude · Demo simulada",(1080,-40,50)),
]
css="""*{margin:0;padding:0;box-sizing:border-box}body{width:1080px}
.c{position:relative;width:1080px;height:1920px;overflow:hidden;margin-bottom:10px}
.ph{position:absolute;left:0;right:0;top:340px;height:830px;overflow:hidden}
.ph img{position:absolute}
.dark{background:#07090c;color:#fff}.light{background:#f4efe7;color:#111}
.f{position:absolute;inset:0}
.dark .f{background:linear-gradient(180deg,#07090c 340px,rgba(7,9,12,0) 470px,rgba(7,9,12,0) 900px,#07090c 1170px)}
.light .f{background:linear-gradient(180deg,#f4efe7 340px,rgba(244,239,231,0) 470px,rgba(244,239,231,0) 900px,#f4efe7 1170px)}
.b{position:absolute;top:285px;left:70px;font:700 26px/1 Inter,Arial,sans-serif;letter-spacing:.24em;text-transform:uppercase;display:flex;gap:16px;align-items:center}
.r{width:24px;height:24px;border:5px solid #e3262b;border-radius:50%}
.l{position:absolute;left:72px;top:1205px;width:76px;height:5px;background:#e3262b}
.t{position:absolute;left:70px;right:70px;top:1245px;font:400 76px/1.1 Georgia,"DejaVu Serif",serif}
.t em{font-style:normal;background:linear-gradient(90deg,#e3262b,#ffb020);-webkit-background-clip:text;background-clip:text;color:transparent}
.g{position:absolute;left:72px;top:1600px;font:700 25px/1 Inter,Arial,sans-serif;letter-spacing:.26em;text-transform:uppercase;color:#e3262b;display:flex;gap:16px;align-items:center}
.g:before{content:"";width:52px;height:3px;background:#e3262b}
.k{position:absolute;right:72px;top:1600px;font:700 25px/1 Inter,Arial,sans-serif;letter-spacing:.22em;text-transform:uppercase;opacity:.55}
"""
h="<!doctype html><html><head><meta charset=utf-8><style>"+css+"</style></head><body>"
for i,img,m,t,e,g,(w,off,lp) in P:
    h+=f'<div class="c {m}" id="{i}"><div class="ph"><img src="{img}" style="width:{w}px;top:{off}px;left:calc({lp}% - {w*lp/100}px)"></div><div class="f"></div><div class="b"><span class="r"></span>Sandra Curvelo · IAM™</div><div class="l"></div><div class="t" style="{'font-size:66px' if i=='udes' else ''}">{t}<br><em>{e}</em></div><div class="g">{g}</div><div class="k">Reel</div></div>'
open(sys.argv[1],"w").write(h+"</body></html>")
