# -*- coding: utf-8 -*-
"""Arma un HTML único y autónomo a partir de la plantilla v2.

La plantilla vive en `plantilla_v2/` repartida en cuatro archivos. Aquí se
incrustan los tres scripts locales dentro del HTML —en el orden que exige el
runtime: support, utilidades, datos— para que el resultado se abra con doble
clic, sin servidor y sin carpeta al lado.

    python3 empaquetar.py                  normal
    python3 empaquetar.py --sin-internet   que abra también sin conexión

**La versión normal necesita internet para abrirse.** No por las fuentes: el
runtime de la plantilla descarga React, React DOM y Babel de `unpkg.com` cada
vez que se abre el archivo, y sin eso la página queda en negro. Con
`--sin-internet` esas tres librerías y three.js quedan dentro del HTML — lo
pesa unos 4 MB más y a cambio el archivo sobrevive a que cambie un CDN o a que
la red del cliente lo bloquee. Para un archivo que debe durar más que el propio
espacio de Slack, esa es la versión que vale.

Antes de usar `--sin-internet` hay que correr `traer-librerias.py` una vez.
"""
import os, sys, json

AQUI = os.path.dirname(os.path.abspath(__file__))
PLANTILLA = os.path.join(AQUI, 'plantilla_v2')
VENDOR = os.path.join(PLANTILLA, 'vendor')

# cada etiqueta del HTML con el archivo que la reemplaza, en orden de carga
SCRIPTS = (
    ('<script src="./support.js"></script>',    'support.js'),
    ('<script src="lib/iam.js"></script>',       os.path.join('lib', 'iam.js')),
    ('<script src="data/archivo.js"></script>',  os.path.join('data', 'archivo.js')),
)

CDN_THREE = '<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>'

# el runtime lee `window.__resources` y, si encuentra la URL, carga de ahí en
# vez de ir al CDN. Es el gancho que trae el propio support.js.
CDN_RUNTIME = {
    'https://unpkg.com/react@18.3.1/umd/react.production.min.js': 'react.js',
    'https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js': 'react-dom.js',
    'https://unpkg.com/@babel/standalone@7.29.0/babel.min.js': 'babel.js',
}


def en_linea(js):
    """Un `</script` dentro del código cerraría la etiqueta antes de tiempo.
    Puede venir en el texto de un mensaje de Slack, así que se parte la
    secuencia; para JavaScript es el mismo texto."""
    return js.replace('</script', '<\\/script').replace('<!--', '<\\!--')


def lee(*partes):
    return open(os.path.join(*partes), encoding='utf-8').read()


def sin_internet(html):
    """Mete las librerías del CDN dentro del HTML."""
    faltan = [f for f in list(CDN_RUNTIME.values()) + ['three.js']
              if not os.path.exists(os.path.join(VENDOR, f))]
    if faltan:
        raise SystemExit('faltan en plantilla_v2/vendor/: %s\ncorre antes:  python3 traer-librerias.py'
                         % ', '.join(faltan))

    # Cada librería entra como texto plano —no se ejecuta— y el arranque la
    # convierte en una URL local que el runtime usa en lugar del CDN.
    bloques, mapa = [], {}
    for url, archivo in CDN_RUNTIME.items():
        ident = 'lib-' + archivo.replace('.js', '')
        bloques.append('<script type="text/plain" id="%s">%s</script>'
                       % (ident, en_linea(lee(VENDOR, archivo))))
        mapa[url] = ident
    arranque = (
        '<script>\n'
        'window.__resources = (function () {\n'
        '  var de = %s, urls = {};\n'
        '  for (var url in de) {\n'
        '    var texto = document.getElementById(de[url]).textContent;\n'
        '    urls[url] = URL.createObjectURL(new Blob([texto], {type: "text/javascript"}));\n'
        '  }\n'
        '  return urls;\n'
        '})();\n'
        '</script>' % json.dumps(mapa, ensure_ascii=False, indent=2)
    )
    html = html.replace('<script src="./support.js"></script>',
                        '\n'.join(bloques) + '\n' + arranque
                        + '\n<script src="./support.js"></script>')
    # three.js no pasa por ese gancho: se carga con su propia etiqueta
    return html.replace(CDN_THREE, '<script>\n' + en_linea(lee(VENDOR, 'three.js')) + '\n</script>')


def copiar_actas(dest):
    """Lleva los PDF de las actas a `<dest>/actas/`, con el nombre con el que se
    publicaron — que es el que aparece como adjunto en los mensajes."""
    import shutil
    origen = os.path.join(os.path.dirname(AQUI), 'salida')
    destino = os.path.join(dest, 'actas')
    os.makedirs(destino, exist_ok=True)
    n = 0
    for f in sorted(os.listdir(origen)):
        if f.endswith('.pdf'):
            shutil.copy(os.path.join(origen, f), os.path.join(destino, f))
            n += 1
    return n


def main():
    suelta = '--sin-internet' in sys.argv
    con_pdfs = '--con-pdfs' in sys.argv
    resto = [a for a in sys.argv[1:] if not a.startswith('--')]
    dest = resto[0] if resto else os.path.join(AQUI, 'entregable')
    os.makedirs(dest, exist_ok=True)

    html = lee(PLANTILLA, 'IAM Archivo.dc.html')
    datos = lee(PLANTILLA, 'data', 'archivo.js')

    a = json.loads(datos[datos.index('{'):datos.rindex('}') + 1])
    if con_pdfs:
        # Los PDF viajan en una carpeta `actas/` al lado del HTML, que es a donde
        # ya apuntan tanto el botón del acta como los adjuntos de los mensajes.
        copiados = copiar_actas(dest)
        print('  %d actas copiadas a actas/' % copiados)
    else:
        # Sin esa carpeta no hay nada que abrir, así que se quitan los enlaces en
        # vez de dejar botones que no llevan a ninguna parte.
        for c in a['canales']:
            for acta in c['actas']:
                acta.pop('pdf', None)
            for m in c['mensajes']:
                for adj in m['adjuntos']:
                    adj.pop('url', None)
    sin_pdf = 'window.ARCHIVO=' + json.dumps(a, ensure_ascii=False, separators=(',', ':')) + ';'

    if suelta:
        html = sin_internet(html)

    for etiqueta, archivo in SCRIPTS:
        if etiqueta not in html:
            raise SystemExit('la plantilla ya no trae la etiqueta %s' % etiqueta)
        js = sin_pdf if archivo.endswith('archivo.js') else lee(PLANTILLA, archivo)
        html = html.replace(etiqueta, '<script>\n' + en_linea(js) + '\n</script>')

    nombre = 'IAM-Hello-comfacesar%s.html' % ('' if suelta else '-con-internet')
    ruta = os.path.join(dest, nombre)
    open(ruta, 'w', encoding='utf-8').write(html)
    print('%s\n  %.1f MB · %d canales · %d mensajes · %d actas · %d grabaciones · %d personas%s'
          % (ruta, os.path.getsize(ruta) / 1048576, len(a['canales']),
             sum(c['conteo'] for c in a['canales']),
             sum(len(c['actas']) for c in a['canales']),
             a['n_grabaciones'], len(a['asistencia']),
             '' if suelta else '\n  necesita internet para abrirse (React y Babel salen de unpkg.com)'))


if __name__ == '__main__':
    main()
