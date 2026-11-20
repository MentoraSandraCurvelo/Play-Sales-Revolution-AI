import csv,re,sys,collections,datetime
src,out=sys.argv[1],sys.argv[2]
lines=open(src,encoding='utf-8').read().splitlines()
i=next(k for k,l in enumerate(lines) if l.startswith('First Name,'))
rows=list(csv.DictReader(lines[i:]))
def n(s): 
    import unicodedata
    return unicodedata.normalize('NFKD',(s or '').lower()).encode('ascii','ignore').decode()
EXC=re.compile(r'\b(tecnolog|ti\b|it\b|sistemas|informatica|cto\b|cio\b|transformacion digital|digital transformation|software|data\b|datos|ciberseg|talento|recursos humanos|human|rrhh|hr\b|people|gestion humana|personas\b|formacion|capacitacion|learning|training|nomina|bienestar|seleccion|recruit)')
TOP=re.compile(r'\b(ceo\b|chief executive|gerente general|general manager|presidente|presidenta|president\b|country manager|director general|directora general|managing director|director ejecutivo|directora ejecutiva|executive director)')
VP=re.compile(r'\b(vicepresident|vice president|vicepresidenta|vp\b|svp\b|evp\b)')
COM=re.compile(r'\b(director|directora|head|gerente|chief|cmo\b|cco\b|lider|leader)\b.*\b(comercial|ventas|sales|marketing|mercadeo|comunicacion|comunicaciones|communications|marca|brand|desarrollo de negocio|business development|commercial|revenue|cliente|customer|relaciones corporativas|asuntos corporativos)|\b(cmo|cco|cro)\b')
CLIENT=re.compile(r'comfacesar|drummond|klaren|bimbo|bavaria|brinsa|abstract')
STRAT=re.compile(r'alqueria|colanta|alpina|nutresa|postobon|alimentos|lacteo|caja de compensacion|comfa|camara de comercio|andi\b|fenalco|gremio|probarranquilla|procolombia|keralty|corona|grupo|holding')
seg=collections.Counter(); A=[]
for r in rows:
    pos=n(r['Position']); comp=n(r['Company'])
    name=(r['First Name']+' '+r['Last Name']).strip()
    if 'ivorra' in n(name): seg['excluido (competencia)']+=1; continue
    if CLIENT.search(comp): cat='cliente actual'
    elif EXC.search(pos): cat='excluido (TI, tecnologia, talento humano o formacion)'
    elif TOP.search(pos) and not VP.search(pos): cat='A1 gerente general / presidente'
    elif VP.search(pos): cat='A2 vicepresidente (no tech)'
    elif COM.search(pos): cat='A3 director comercial, marketing o comunicacion'
    else: cat='otros'
    seg[cat]+=1
    if cat.startswith('A'):
        try: d=datetime.datetime.strptime(r['Connected On'],'%d %b %Y').date()
        except: d=datetime.date(1900,1,1)
        w={'A1':3,'A2':2,'A3':2}[cat[:2]]+(2 if STRAT.search(comp) else 0)
        A.append(dict(segmento=cat,nombre=name,cargo=r['Position'],empresa=r['Company'],url=r['URL'],conectado=r['Connected On'],prioridad=w,_d=d))
A.sort(key=lambda x:(-x['prioridad'],-x['_d'].toordinal()))
with open(out,'w',newline='',encoding='utf-8') as fh:
    w=csv.DictWriter(fh,fieldnames=['segmento','nombre','cargo','empresa','url','conectado','prioridad']); w.writeheader()
    for a in A: a.pop('_d'); w.writerow(a)
print('TOTAL',len(rows))
for k,v in sorted(seg.items()): print(f'{v:6d}  {k}')
print('---TOP 15')
for a in A[:15]: print(a['segmento'][:2],'|',a['nombre'],'|',a['cargo'][:60],'|',a['empresa'][:40],'|',a['conectado'])
print('---STRAT companies in A:', sum(1 for a in A if a['prioridad']>=4))
