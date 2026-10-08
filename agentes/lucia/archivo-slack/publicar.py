# -*- coding: utf-8 -*-
"""Prepara la app para publicarla como página web.

Lo publicado no es un documento completo sino un **fragmento**: el esqueleto
(`<!doctype>`, `<head>`, `<body>`) lo pone la plataforma al publicar. Así que
aquí se quita ese envoltorio y se dejan, en orden, los tres scripts locales y
el componente.

Las librerías salen del CDN —en la web sí se alcanzan—, de modo que el
fragmento pesa 2 MB y no 6. Los PDF viajan aparte, en `actas/`, que es a donde
ya apuntan los enlaces.
"""
import json, os, re, shutil, sys
import empaquetar, marca

AQUI = os.path.dirname(os.path.abspath(__file__))
PLANTILLA = os.path.join(AQUI, 'plantilla_v2')


def argumentos():
    """`--cliente <slug>` y, opcional, la carpeta destino.

    Sin `--cliente` se publica Comfacesar, que es el espacio original. El
    destino por defecto es `publicado/<slug>`, para que publicar un cliente no
    pise lo del anterior."""
    args = sys.argv[1:]
    slug = 'comfacesar'
    if '--cliente' in args:
        i = args.index('--cliente')
        if i + 1 >= len(args):
            raise SystemExit('falta el nombre del cliente después de --cliente')
        slug = args[i + 1]
        del args[i:i + 2]
    dest = args[0] if args else os.path.join(AQUI, 'publicado', slug)
    return slug, dest

SCRIPTS = (('<script src="./support.js"></script>', 'support.js'),
           ('<script src="lib/iam.js"></script>', os.path.join('lib', 'iam.js')))

# El paquete de datos es lo único que cambia de un cliente a otro. Comfacesar
# trae el suyo dentro de la plantilla porque es el espacio original; los demás
# lo declaran en `fuente_datos` de su archivo de cliente.
ETIQUETA_DATOS = '<script src="data/archivo.js"></script>'


def ruta_datos(cfg):
    rel = cfg.get('fuente_datos')
    if rel:
        ruta = os.path.join(os.path.dirname(AQUI), rel) if not os.path.isabs(rel) else rel
        if not os.path.exists(ruta):
            raise SystemExit(
                'el paquete de datos de %s no existe: %s\n'
                'Córrelo primero: python3 construir_cliente.py %s'
                % (cfg['nombre'], ruta, cfg['slug']))
        return ruta
    return os.path.join(PLANTILLA, 'data', 'archivo.js')


def copiar(rel, destino, extension):
    """Copia los archivos de una carpeta del cliente. Sin carpeta, no copia nada:
    un cliente nuevo empieza sin actas y sin adjuntos, que es lo correcto."""
    if not rel:
        return 0
    origen = rel if os.path.isabs(rel) else os.path.join(os.path.dirname(AQUI), rel)
    if not os.path.isdir(origen):
        raise SystemExit('la carpeta declarada no existe: %s' % origen)
    os.makedirs(destino, exist_ok=True)
    n = 0
    for f in sorted(os.listdir(origen)):
        if extension and not f.endswith(extension):
            continue
        shutil.copy(os.path.join(origen, f), os.path.join(destino, f))
        n += 1
    return n


MES = ('ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic')


def periodo(ruta_js):
    """El rango de fechas y la cinta, sacados de los datos del propio cliente.

    Estaban escritos a mano dentro de la plantilla, así que la app de cualquier
    cliente mostraba el rango de Comfacesar y su número de semanas. Se calculan
    aquí para que cada uno muestre lo suyo, y un cliente que arranca no muestre
    un periodo que no ha vivido."""
    crudo = open(ruta_js, encoding='utf-8').read()
    i, j = crudo.find('{'), crudo.rfind('}')
    datos = json.loads(crudo[i:j + 1]) if i >= 0 < j else {}

    fechas = []
    for c in datos.get('canales', []):
        for k in ('desde', 'hasta'):
            if c.get(k):
                fechas.append(c[k])
    def bonito(iso):
        a, m, d = iso.split('-')
        return '%d %s' % (int(d), MES[int(m) - 1]), a
    if fechas:
        (d1, a1), (d2, a2) = bonito(min(fechas)), bonito(max(fechas))
        rango = d1 + ' – ' + d2 + ' ' + a2 if a1 == a2 else d1 + ' ' + a1 + ' – ' + d2 + ' ' + a2
    else:
        rango = 'Sin mensajes todavía'

    n = len(datos.get('semanas') or [])
    cinta = 'EN VIVO · %d SEMANAS' % n if n else 'EN VIVO'
    return rango, cinta


def en_linea(js):
    return js.replace('</script', '<\\/script').replace('<!--', '<\\!--')


def main():
    slug, DEST = argumentos()
    cfg = marca.cargar(slug)
    os.makedirs(DEST, exist_ok=True)
    html = open(os.path.join(PLANTILLA, 'IAM Archivo.dc.html'), encoding='utf-8').read()
    html = empaquetar.sin_internet(html)
    html = empaquetar.con_visor(html)
    for etiqueta, archivo in SCRIPTS:
        js = open(os.path.join(PLANTILLA, archivo), encoding='utf-8').read()
        html = html.replace(etiqueta, '<script>\n' + en_linea(js) + '\n</script>')
    datos = ruta_datos(cfg)
    html = html.replace(ETIQUETA_DATOS,
                        '<script>\n' + en_linea(open(datos, encoding='utf-8').read()) + '\n</script>')

    # fuera el envoltorio: lo pone la plataforma
    cuerpo = re.search(r'<body[^>]*>(.*)</body>', html, re.S).group(1)
    cabeza = re.search(r'<head[^>]*>(.*)</head>', html, re.S).group(1)
    # Del <head> hay que rescatar **todos** los scripts y en su orden: ahí viven
    # support.js y, con las librerías dentro, también React, Babel y three.js.
    # Quedándose solo con el primero, el fragmento salía a 2,8 MB en vez de 6 y
    # no arrancaba.
    guiones = re.findall(r'<script(?:\s[^>]*)?>.*?</script>', cabeza, re.S)
    frag = '\n'.join(guiones) + '\n' + cuerpo.strip() + '\n'

    # La identidad del cliente, al final y sobre el fragmento ya armado. Si un
    # texto de la plantilla cambió, esto detiene la publicación en vez de
    # sacarle a un cliente una app con el nombre de otro.
    cfg['rango'], cfg['cinta'] = periodo(datos)
    frag, cambios = marca.aplicar(frag, cfg)
    # El logo del cliente en la baldosa de identidad, como el icono del espacio
    # en Slack. Estaba declarado en el archivo de cliente y no lo metía nadie,
    # así que las tres apps salían con la misma marca.
    frag, puesto = marca.poner_logo(frag, cfg)

    # La conversación. El archivo de Comfacesar es de solo lectura y así se
    # queda; los espacios de cliente llevan además `lib/conversacion.js`, que
    # mezcla en vivo lo que se escribe con lo que ya estaba. Va al final, para
    # que corra cuando el componente y los datos ya están puestos. Sin esto, un
    # cliente nuevo recibe una app vacía y muerta, que es lo que pasó con
    # Novasoft.
    if cfg.get('conversacion'):
        js = open(os.path.join(PLANTILLA, 'lib', 'conversacion.js'), encoding='utf-8').read()
        frag += '\n<script>\n' + en_linea(js) + '\n</script>\n'

    ruta = os.path.join(DEST, 'iam-hello.html')
    open(ruta, 'w', encoding='utf-8').write(frag)

    # Las actas y los adjuntos son del cliente y de nadie más. Sin esto, la
    # publicación de cualquier cliente se llevaba las 81 actas de Comfacesar
    # dentro de su app: el espacio cerrado dejaría de serlo en el primer
    # cliente nuevo.
    n = copiar(cfg.get('fuente_actas'), os.path.join(DEST, 'actas'), '.pdf')
    m = copiar(cfg.get('fuente_archivos'), os.path.join(DEST, 'archivos'), None)
    print('%s  ·  %s  (%.1f MB)\n  %d actas en actas/\n  %d adjuntos en archivos/'
          % (ruta, cfg['nombre'], os.path.getsize(ruta) / 1048576, n, m))
    if cambios:
        for viejo, nuevo in cambios:
            print('  marca: %s  →  %s' % (viejo, nuevo))
    else:
        print('  marca: sin cambios, la plantilla ya es de este cliente')
    print('  datos: %s' % os.path.relpath(datos, os.path.dirname(AQUI)))
    print('  conversacion: %s' % ('encendida, necesita las capacidades db y user'
                                  if cfg.get('conversacion') else 'apagada, archivo de solo lectura'))
    if puesto:
        print('  logo: %s, puesto en la baldosa sobre %s'
              % (os.path.relpath(puesto, os.path.dirname(AQUI)), cfg.get('logo_fondo', '#0A0A0A')))
    else:
        print('  logo: no está (clientes/%s), se queda Halo en la baldosa'
              % cfg.get('logo', '?'))


if __name__ == '__main__':
    main()
