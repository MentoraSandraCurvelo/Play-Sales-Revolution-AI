/* ---- La conversación, encima del archivo ----------------------------------

   El archivo de Comfacesar es de solo lectura: trae los mensajes dentro del
   propio documento y no espera que nadie escriba. Para un cliente que arranca
   de cero eso no sirve de nada, porque el archivo está vacío y la app queda
   muerta. Aquí se le añade la conversación **sin tocar el componente**: los
   mensajes nuevos viven en `db`, y al llegar se mezclan con los del archivo
   antes de que el componente los agrupe por día.

   Por qué así y no reescribiendo la plantilla: la plantilla es la misma para
   todos los clientes y es lo que garantiza que las tres apps se vean igual.
   Si se bifurca, vuelve a pasar lo que pasó, que cada cliente terminó con una
   app distinta.

   Si la página se publica sin la capacidad `db` —el caso de Comfacesar— este
   archivo no hace absolutamente nada y la app sigue siendo el archivo de
   siempre. Esa es la razón de que el primer `return` sea el más importante.

   Nombres: se guarda el identificador de quien escribe, nunca su nombre. El
   nombre se resuelve al pintar, porque cambia según quién mire y se queda
   viejo si se congela dentro del mensaje. */
(function () {
  'use strict';

  /* Dos colecciones, y la diferencia es de permisos, no de pantalla.
     `mensajes` la lee cualquiera que pueda abrir el espacio. `privado` solo la
     leen y escriben los editores, por la regla que se declara al publicar:
     privado read admin, write admin. Un canal cerrado no trae nada dentro de la
     página: todo lo suyo vive en `privado`, porque lo que va en la página lo ve
     quien mire el código. */
  var COL = 'mensajes';
  var COL_CERRADA = 'privado';
  /* Los canales que se crean desde dentro viven en `db`, no en la página. Van
     en dos colecciones y no en una con un campo `cerrado`, porque un canal
     cerrado no se tiene que poder ni nombrar: si la lista fuera una sola y
     legible por todos, cualquiera vería que existe un canal llamado Dirección
     aunque no pudiera leerlo. */
  var COL_CANALES = 'canales';
  var COL_CANALES_CERRADOS = 'canales_cerrados';
  var LIMITE = 4000;

  function esCerrado(canal) {
    var A = window.ARCHIVO;
    if (!A || !A.canales) return false;
    for (var i = 0; i < A.canales.length; i++) {
      if (A.canales[i].canal === canal) return !!A.canales[i].cerrado;
    }
    return false;
  }

  function dos(n) { return (n < 10 ? '0' : '') + n; }
  function fechaDe(d) { return d.getFullYear() + '-' + dos(d.getMonth() + 1) + '-' + dos(d.getDate()); }
  function horaDe(d) { return dos(d.getHours()) + ':' + dos(d.getMinutes()); }

  /* El componente no se expone en ninguna parte, así que para pedirle que
     repinte hay que encontrarlo. Se busca el nodo de React y se sube por el
     árbol hasta el que tiene `msgCache`, que es el nuestro. Si cambia la
     versión de React y esto deja de encontrarlo, no se rompe nada: los
     mensajes siguen guardándose y aparecen la próxima vez que se abra. */
  var _inst = null;
  var puedeEditar = false;   /* se aplica en cada repintado, ver repintar() */
  function instancia() {
    if (_inst) return _inst;
    if (typeof document === 'undefined' || !document.body) return null;
    var pila = [document.body], vistos = 0;
    while (pila.length && vistos < 4000) {
      var el = pila.shift(); vistos++;
      var claves = Object.keys(el);
      for (var i = 0; i < claves.length; i++) {
        if (claves[i].indexOf('__reactFiber$') !== 0 && claves[i].indexOf('__reactInternalInstance$') !== 0) continue;
        var f = el[claves[i]];
        while (f) {
            /* La plataforma envuelve el componente: el stateNode de la fibra es
             un contenedor y lo nuestro cuelga de `.logic`. Se miran los dos,
             porque el envoltorio puede cambiar y el componente suelto también
             es válido. */
          var sn = f.stateNode;
          var cand = (sn && sn.logic && typeof sn.logic.setState === 'function') ? sn.logic : sn;
          if (cand && typeof cand.setState === 'function' && cand.msgCache && cand.by) return (_inst = cand);
          f = f.return;
        }
      }
      for (var j = 0; j < el.children.length; j++) pila.push(el.children[j]);
    }
    return null;
  }

  function repintar() {
    var inst = instancia();
    if (!inst) return false;
    inst.puedeEditar = puedeEditar;
    /* El componente guarda su propio índice de canales, hecho al construirse.
       Un canal creado después no está ahí, y al abrirlo la vista se cae
       buscando un canal que para ella no existe. Se rehace en cada repintado. */
    var A = window.ARCHIVO;
    if (A && A.canales && inst.by) {
      A.canales.forEach(function (c) { inst.by[c.canal] = c; });
    }
    inst.msgCache = {};
    try { inst.setState({}); } catch (e) { return false; }
    return true;
  }

  /* Un canal recién creado tiene que traer todo lo que la vista lee, o la
     pantalla se cae al abrirlo. Es la misma forma que arma el constructor de
     clientes nuevos, escrita aquí para el que nace en caliente. */
  function canalNuevo(d, cerrado) {
    return {
      canal: String(d.canal || ''),
      id: String(d.id || d.canal || ''),
      nombre: String(d.nombre || d.canal || ''),
      icono: String(d.icono || ''),
      cerrado: !!cerrado,
      mensajes: [], conteo: 0, conteo_total: 0,
      desde: '', hasta: '', adjuntos: 0,
      actas: [], fijados: [], grabaciones: [], informes: [], pulso: []
    };
  }

  /* ---- mezcla ------------------------------------------------------------
     Los del archivo se guardan aparte una sola vez. En cada snapshot se
     reconstruye la lista entera, para que un mensaje no se duplique ni se
     quede pegado cuando alguien lo borra. */
  var base = null;
  function guardarBase(A) {
    if (base) return;
    base = {};
    (A.canales || []).forEach(function (c) { base[c.canal] = c.mensajes.slice(); });
  }

  /* Los canales de `db` se rehacen enteros en cada aviso, como los mensajes.
     Los de la página no se tocan nunca. */
  var baseCanales = null;
  function mezclarCanales(A, vivos) {
    if (!baseCanales) baseCanales = (A.canales || []).slice();
    var porSlug = {};
    baseCanales.forEach(function (c) { porSlug[c.canal] = c; });
    var suma = baseCanales.slice();
    vivos.forEach(function (c) {
      var ya = porSlug[c.canal];
      if (ya) {
        /* Un canal de la página no se duplica ni se reemplaza: lo que llega de
           `db` con su mismo nombre corto es un cambio de nombre o de icono, y
           se aplica encima. Así se puede renombrar un canal que nació dentro
           del archivo, sin tocar el archivo. */
        if (c.nombre) ya.nombre = c.nombre;
        if (typeof c.icono === 'string') ya.icono = c.icono;
        return;
      }
      porSlug[c.canal] = c;
      suma.push(c);
    });
    A.canales = suma;
  }

  function mezclar(A, vivos) {
    guardarBase(A);
    var porCanal = {};
    vivos.forEach(function (m) { (porCanal[m.canal] = porCanal[m.canal] || []).push(m); });
    (A.canales || []).forEach(function (c) {
      var nuevos = porCanal[c.canal] || [];
      var todos = (base[c.canal] || []).concat(nuevos);
      todos.sort(function (a, b) { return parseFloat(a.ts) - parseFloat(b.ts); });
      c.mensajes = todos;
      c.conteo = todos.filter(function (m) { return !m.sistema; }).length;
    });
  }

  /* ---- el compositor -----------------------------------------------------
     Barra fija abajo. Se muestra solo cuando se está viendo un canal, que se
     sabe por el hash: `#/<canal>/<pestaña>`. El componente cambia el hash con
     `replaceState`, que no dispara `hashchange`, así que además se mira cada
     tanto. Es una lectura de cadena, no cuesta nada. */
  var CAJA = 'position:fixed;left:0;right:0;bottom:0;z-index:35;display:none;'
    + 'padding:10px 16px calc(10px + env(safe-area-inset-bottom));'
    + 'background:var(--bg,#09090b);border-top:1px solid var(--line2,rgba(255,255,255,.12))';
  var FILA = 'display:flex;gap:10px;align-items:flex-end;max-width:900px;margin:0 auto';
  var CAMPO = 'flex:1;min-height:42px;max-height:140px;padding:11px 14px;border-radius:14px;resize:none;'
    + 'background:var(--card2,#17171a);border:1px solid var(--line2,rgba(255,255,255,.14));'
    + 'color:var(--ink,#f2f2f3);font:500 14.5px Geist,system-ui,sans-serif;line-height:1.5;outline:0';
  var BOTON = 'flex:none;height:42px;padding:0 18px;border-radius:999px;border:0;background:#C00000;'
    + 'color:#fff;font:620 14px Geist,system-ui,sans-serif;cursor:pointer';
  var NOTA = 'max-width:900px;margin:6px auto 0;font:500 12px Geist,system-ui,sans-serif;color:var(--ink3,#8a8a92)';
  var CLIP = 'flex:none;width:42px;height:42px;border-radius:999px;border:1px solid var(--linea,#2a2a30);'
    + 'background:transparent;color:var(--ink2,#b9b9c0);font:400 19px Geist,system-ui,sans-serif;cursor:pointer';
  var FICHA = 'max-width:900px;margin:0 auto 8px;display:flex;align-items:center;gap:10px;padding:9px 12px;'
    + 'border:1px solid var(--linea,#2a2a30);border-radius:12px;background:var(--fondo2,#121216)';
  var QUITA = 'flex:none;width:24px;height:24px;border-radius:999px;border:0;background:transparent;'
    + 'color:var(--ink3,#8a8a92);font:400 17px Geist,system-ui,sans-serif;cursor:pointer;line-height:1'

  /* ---- archivos ----------------------------------------------------------
     El almacén del artefacto acepta un juego cerrado de tipos, y no están los
     de ofimática: nada de .docx, .xlsx, .pptx ni .zip. Para esos el equipo
     sigue pegando el enlace de la nube, que es lo que ya hace. Aquí se eligen
     por extensión porque el tipo que declara el navegador no es de fiar: un
     .csv en Windows llega como application/vnd.ms-excel y el almacén lo
     rechaza. */
  var TIPOS = {
    png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif',
    webp: 'image/webp', svg: 'image/svg+xml',
    mp4: 'video/mp4', webm: 'video/webm',
    pdf: 'application/pdf',
    csv: 'text/csv', md: 'text/markdown', json: 'application/json',
    txt: 'text/plain', css: 'text/css', js: 'text/javascript'
  };
  var TOPE = { 'image/svg+xml': 2, 'text/css': 16, 'text/javascript': 16 };

  function extDe(nombre) {
    var m = /\.([A-Za-z0-9]+)$/.exec(String(nombre || ''));
    return m ? m[1].toLowerCase() : '';
  }

  function pesoDe(b) {
    if (b >= 1048576) return (b / 1048576).toFixed(1) + ' MB';
    if (b >= 1024) return Math.round(b / 1024) + ' KB';
    return b + ' B';
  }

  /* El almacén devuelve su propio motivo. Se traduce aquí para que la persona
     lea qué hacer y no un código. */
  function porQueNo(err) {
    var c = err && err.code;
    if (c === 'too_large') return 'El archivo pesa demasiado. El tope son 20 MB.';
    if (c === 'unsupported_type') return 'Ese tipo de archivo no se puede subir aquí.';
    if (c === 'quota_or_state') return 'El espacio de archivos está lleno. Avísame y lo reviso.';
    if (c === 'rate_limited') return 'Vas muy rápido. Espera un momento y vuelve a intentarlo.';
    if (c === 'upstream_auth') return 'Se perdió la sesión. Recarga la página y entra otra vez.';
    if (c === 'not_granted' || c === 'capability_disabled' || c === 'capability_removed')
      return 'No tienes permiso para subir archivos en este espacio.';
    return 'No se pudo subir el archivo. Vuelve a intentarlo.';
  }

  function canalDelHash() {
    var t = decodeURIComponent(String(location.hash || '').replace(/^#\/?/, '')).split('/').filter(Boolean);
    if (!t.length) return null;
    if (['actas', 'personas', 'archivos', 'grabaciones', 'asistencia'].indexOf(t[0]) >= 0) return null;
    return t[0];
  }

  function montar(enviar, almacen) {
    var caja = document.createElement('div');
    caja.id = 'iam-escribir';
    caja.style.cssText = CAJA;
    var fila = document.createElement('div');
    fila.style.cssText = FILA;
    var campo = document.createElement('textarea');
    campo.rows = 1;
    campo.style.cssText = CAMPO;
    campo.setAttribute('aria-label', 'Escribe un mensaje');
    var boton = document.createElement('button');
    boton.type = 'button';
    boton.textContent = 'Enviar';
    boton.style.cssText = BOTON;
    var nota = document.createElement('div');
    nota.style.cssText = NOTA;

    /* El clip solo existe si el almacén respondió. A quien solo lee le
       resuelve nulo, así que no ve el botón en vez de verlo y que falle. */
    var clip = null, archivo = null, ficha = null, subiendo = false;
    if (almacen) {
      clip = document.createElement('button');
      clip.type = 'button';
      clip.textContent = '\uD83D\uDCCE';
      clip.title = 'Adjuntar un archivo';
      clip.setAttribute('aria-label', 'Adjuntar un archivo');
      clip.style.cssText = CLIP;
      archivo = document.createElement('input');
      archivo.type = 'file';
      archivo.style.display = 'none';
      archivo.accept = Object.keys(TIPOS).map(function (e) { return '.' + e; }).join(',');
      ficha = document.createElement('div');
      ficha.style.cssText = FICHA;
      ficha.style.display = 'none';
      caja.appendChild(ficha);
      fila.appendChild(clip);
    }

    fila.appendChild(campo); fila.appendChild(boton);
    caja.appendChild(fila); caja.appendChild(nota);
    if (archivo) caja.appendChild(archivo);
    document.body.appendChild(caja);

    function crecer() {
      campo.style.height = 'auto';
      campo.style.height = Math.min(campo.scrollHeight, 140) + 'px';
    }
    function decir(t) { nota.textContent = t || ''; }

    /* El adjunto ya subido y todavía sin enviar. Se sube al elegirlo, no al
       enviar, para que la espera se vea y no parezca que el botón se colgó. */
    var puesto = null;

    function pintarFicha() {
      if (!ficha) return;
      ficha.innerHTML = '';
      if (!puesto) { ficha.style.display = 'none'; return; }
      ficha.style.display = 'flex';
      var txt = document.createElement('div');
      txt.style.cssText = 'flex:1;min-width:0;font:500 13px Geist,system-ui,sans-serif;color:var(--ink,#f2f2f3);'
        + 'overflow:hidden;text-overflow:ellipsis;white-space:nowrap';
      txt.textContent = puesto.nombre + '  ·  ' + puesto.peso;
      var x = document.createElement('button');
      x.type = 'button';
      x.textContent = '\u00D7';
      x.title = 'Quitar el archivo';
      x.setAttribute('aria-label', 'Quitar el archivo');
      x.style.cssText = QUITA;
      x.addEventListener('click', quitar);
      ficha.appendChild(txt); ficha.appendChild(x);
    }

    /* Quitarlo lo borra del almacén de verdad. Es una acción deliberada de la
       persona, que es la única vez que se puede borrar un archivo. */
    function quitar() {
      if (!puesto || subiendo) return;
      var id = puesto.id;
      puesto = null; pintarFicha(); decir('');
      if (almacen && almacen['delete']) {
        Promise.resolve(almacen['delete'](id))['catch'](function () { /* queda huérfano, no es grave */ });
      }
    }

    function elegido() {
      var f = archivo.files && archivo.files[0];
      archivo.value = '';
      if (!f || subiendo) return;
      if (puesto) quitar();
      var tipo = TIPOS[extDe(f.name)];
      if (!tipo) {
        decir('Ese tipo de archivo no se puede subir. Para un Word, un Excel o una presentación, pega el enlace de la nube.');
        return;
      }
      var tope = (TOPE[tipo] || 20) * 1048576;
      if (f.size > tope) { decir('El archivo pesa ' + pesoDe(f.size) + ' y el tope para este tipo son ' + (tope / 1048576) + ' MB.'); return; }
      subiendo = true; clip.disabled = true; boton.disabled = true;
      decir('Subiendo ' + f.name + '\u2026');
      Promise.resolve(almacen.upload(f, { type: tipo })).then(function (r) {
        puesto = { id: r.id, nombre: f.name, tipo: r.contentType, peso: pesoDe(r.sizeBytes) };
        decir(''); pintarFicha();
      })['catch'](function (err) { decir(porQueNo(err)); })
        .then(function () { subiendo = false; clip.disabled = false; boton.disabled = false; });
    }

    if (clip) {
      clip.addEventListener('click', function () { archivo.click(); });
      archivo.addEventListener('change', elegido);
    }

    var mandando = false;
    function manda() {
      var txt = campo.value.trim();
      /* Con un archivo puesto, el texto deja de ser obligatorio. */
      if ((!txt && !puesto) || mandando || subiendo) return;
      if (txt.length > LIMITE) { decir('El mensaje es muy largo, quedan ' + (txt.length - LIMITE) + ' caracteres de más.'); return; }
      var canal = canalDelHash();
      if (!canal) return;
      mandando = true; boton.disabled = true; if (clip) clip.disabled = true;
      decir('Enviando\u2026');
      enviar(canal, txt, puesto).then(function () {
        campo.value = ''; puesto = null; pintarFicha(); crecer(); decir('');
      })['catch'](function (err) {
        var c = err && err.code;
        decir(c === 'permission_denied' || c === 'not_granted'
          ? 'No tienes permiso para escribir en este espacio.'
          : 'No se pudo enviar. Vuelve a intentarlo.');
      }).then(function () { mandando = false; boton.disabled = false; if (clip) clip.disabled = false; });
    }

    campo.addEventListener('input', crecer);
    campo.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' && !ev.shiftKey) { ev.preventDefault(); manda(); }
    });
    boton.addEventListener('click', manda);

    var ultimo = null;
    function revisar() {
      var canal = canalDelHash();
      if (canal === ultimo) return;
      ultimo = canal;
      caja.style.display = canal ? 'block' : 'none';
      campo.placeholder = canal ? 'Escribe en #' + canal : '';
      document.body.style.paddingBottom = canal ? '96px' : '';
    }
    revisar();
    addEventListener('hashchange', revisar);
    setInterval(revisar, 400);
  }

  /* ---- crear un canal, desde dentro --------------------------------------
     Un botón fijo y un panel pequeño, que solo aparecen para quien puede
     editar. Se dibujan a mano y no dentro del componente: la barra lateral la
     pinta la plantilla, que es la misma para todos los clientes, y meterle
     mano por aquí la rompería para los que no llevan esto. */
  var BOTON_NUEVO = 'position:fixed;left:16px;bottom:116px;z-index:36;display:none;'
    + 'align-items:center;gap:8px;padding:9px 14px;border-radius:999px;border:0;'
    + 'background:#C00000;color:#fff;font:620 13px Geist,system-ui,sans-serif;'
    + 'cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,.35)';
  var PANEL = 'position:fixed;left:16px;bottom:116px;z-index:37;display:none;width:280px;'
    + 'padding:14px;border-radius:16px;background:var(--card2,#17171a);'
    + 'border:1px solid var(--line2,rgba(255,255,255,.14));'
    + 'box-shadow:0 12px 40px rgba(0,0,0,.5);font:500 13px Geist,system-ui,sans-serif;'
    + 'color:var(--ink,#f2f2f3)';
  var CAMPO_N = 'width:100%;margin-top:6px;padding:9px 11px;border-radius:10px;'
    + 'background:var(--bg,#09090b);border:1px solid var(--line2,rgba(255,255,255,.14));'
    + 'color:var(--ink,#f2f2f3);font:500 13.5px Geist,system-ui,sans-serif;outline:0';
  var ETIQ = 'display:block;margin-top:10px;font:600 11px Geist,system-ui,sans-serif;'
    + 'letter-spacing:.06em;text-transform:uppercase;color:var(--ink3,#8a8a92)';

  function montarCanales(crear, renombrar) {
    var boton = document.createElement('button');
    boton.type = 'button';
    boton.textContent = '+  Canales';
    boton.style.cssText = BOTON_NUEVO;

    var panel = document.createElement('div');
    panel.style.cssText = PANEL;

    var lSel = document.createElement('label'); lSel.style.cssText = ETIQ; lSel.textContent = 'Qué quieres hacer';
    var sel = document.createElement('select'); sel.style.cssText = CAMPO_N;

    var lNom = document.createElement('label'); lNom.style.cssText = ETIQ; lNom.textContent = 'Nombre del canal';
    var nom = document.createElement('input'); nom.type = 'text'; nom.style.cssText = CAMPO_N; nom.maxLength = 60;
    var lIco = document.createElement('label'); lIco.style.cssText = ETIQ; lIco.textContent = 'Icono';
    var ico = document.createElement('input'); ico.type = 'text'; ico.style.cssText = CAMPO_N; ico.maxLength = 4;
    ico.placeholder = 'un emoji, o nada para \u{1F465}';

    var fila = document.createElement('label');
    fila.style.cssText = 'display:flex;align-items:center;gap:8px;margin-top:12px;cursor:pointer';
    var cerr = document.createElement('input'); cerr.type = 'checkbox';
    cerr.style.cssText = 'width:16px;height:16px;accent-color:#C00000';
    var txtCerr = document.createElement('span');
    txtCerr.innerHTML = 'Canal cerrado \u{1F512}';
    fila.appendChild(cerr); fila.appendChild(txtCerr);

    var aviso = document.createElement('div');
    aviso.style.cssText = 'margin-top:8px;font:500 11.5px Geist,system-ui,sans-serif;color:var(--ink3,#8a8a92);line-height:1.45';

    var pie = document.createElement('div');
    pie.style.cssText = 'display:flex;gap:8px;margin-top:14px';
    var ok = document.createElement('button');
    ok.type = 'button';
    ok.style.cssText = 'flex:1;height:36px;border-radius:10px;border:0;background:#C00000;'
      + 'color:#fff;font:620 13px Geist,system-ui,sans-serif;cursor:pointer;text-align:center';
    var cancelar = document.createElement('button');
    cancelar.type = 'button'; cancelar.textContent = 'Cerrar';
    cancelar.style.cssText = 'flex:none;height:36px;padding:0 12px;border-radius:10px;'
      + 'border:1px solid var(--line2,rgba(255,255,255,.14));background:transparent;'
      + 'color:var(--ink3,#8a8a92);font:600 13px Geist,system-ui,sans-serif;cursor:pointer';
    pie.appendChild(ok); pie.appendChild(cancelar);

    var nota = document.createElement('div');
    nota.style.cssText = 'margin-top:8px;font:500 11.5px Geist,system-ui,sans-serif;color:var(--ink3,#8a8a92);line-height:1.45';

    /* Invitar no es cosa del canal: se invita al espacio entero, desde el menú
       de compartir de la página, y solo lo puede hacer quien es dueño. Aquí no
       se finge un botón que no existe: se dice dónde está el que sí existe. */
    var invitar = document.createElement('div');
    invitar.style.cssText = 'margin-top:14px;padding-top:12px;border-top:1px solid var(--line2,rgba(255,255,255,.12));'
      + 'font:500 11.5px Geist,system-ui,sans-serif;color:var(--ink3,#8a8a92);line-height:1.5';
    invitar.innerHTML = '<b style="color:var(--ink,#f2f2f3)">Para invitar a alguien</b><br>'
      + 'se invita al espacio entero, no al canal, desde el men\u00fa de compartir de esta p\u00e1gina. '
      + 'Como <b style="color:var(--ink,#f2f2f3)">colaborador</b> para que escriba, como lector para que solo lea.';

    [lSel, sel, lNom, nom, lIco, ico, fila, aviso, pie, nota, invitar]
      .forEach(function (e) { panel.appendChild(e); });
    document.body.appendChild(boton);
    document.body.appendChild(panel);

    function listaCanales() {
      var A = window.ARCHIVO;
      return ((A && A.canales) || []).filter(function (c) { return !c.cerrado || puedeEditar; });
    }

    function llenarSelect() {
      var antes = sel.value;
      sel.innerHTML = '';
      var o0 = document.createElement('option');
      o0.value = ''; o0.textContent = 'Crear un canal nuevo';
      sel.appendChild(o0);
      listaCanales().slice().sort(function (a, b) {
        return (a.nombre || a.canal).localeCompare(b.nombre || b.canal, 'es', { sensitivity: 'base' });
      }).forEach(function (c) {
        var o = document.createElement('option');
        o.value = c.canal;
        o.textContent = 'Renombrar  ' + (c.cerrado ? '\u{1F512} ' : (c.icono || '\u{1F465}') + ' ') + (c.nombre || c.canal);
        sel.appendChild(o);
      });
      if (antes) sel.value = antes;
    }

    function modo() {
      var slug = sel.value;
      var editando = !!slug;
      ok.textContent = editando ? 'Guardar' : 'Crear';
      fila.style.display = editando ? 'none' : 'flex';
      nota.textContent = '';
      if (editando) {
        var c = listaCanales().filter(function (x) { return x.canal === slug; })[0];
        nom.value = c ? (c.nombre || c.canal) : '';
        ico.value = c ? (c.icono || '') : '';
        aviso.textContent = 'Cambia el nombre y el icono. Si quieres que pase de abierto a cerrado o al rev\u00e9s, d\u00edmelo: eso mueve los mensajes de sitio y no se hace con un clic.';
      } else {
        nom.value = ''; ico.value = ''; cerr.checked = false;
        aviso.textContent = 'Un canal cerrado solo lo ven y lo escriben quienes pueden editar este espacio.';
      }
    }
    sel.addEventListener('change', modo);

    function abrir(si) {
      panel.style.display = si ? 'block' : 'none';
      boton.style.display = si ? 'none' : (puedeEditar ? 'inline-flex' : 'none');
      if (si) { llenarSelect(); sel.value = ''; modo(); nom.focus(); }
    }
    boton.addEventListener('click', function () { abrir(true); });
    cancelar.addEventListener('click', function () { abrir(false); });

    var trabajando = false;
    function hacer() {
      var n = nom.value.trim();
      if (trabajando) return;
      if (!n) { nota.textContent = 'Ponle un nombre.'; return; }
      trabajando = true; ok.disabled = true;
      nota.textContent = sel.value ? 'Guardando\u2026' : 'Creando\u2026';
      var p = sel.value ? renombrar(sel.value, n, ico.value) : crear(n, ico.value, cerr.checked);
      p.then(function () {
        trabajando = false; ok.disabled = false;
        abrir(false);
      })['catch'](function (err) {
        trabajando = false; ok.disabled = false;
        var c = err && err.code;
        nota.textContent =
          c === 'ya_existe' ? 'Ya hay un canal con ese nombre.' :
          c === 'nombre_vacio' ? 'Ese nombre no deja ning\u00fan texto utilizable.' :
          (c === 'permission_denied' || c === 'not_granted')
            ? 'No tienes permiso para esto aqu\u00ed.'
            : 'No se pudo guardar. Vuelve a intentarlo.';
      });
    }
    ok.addEventListener('click', hacer);
    nom.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') hacer(); });

    setInterval(function () {
      if (panel.style.display === 'block') return;
      boton.style.display = puedeEditar ? 'inline-flex' : 'none';
    }, 500);
  }

  /* ---- arranque ---------------------------------------------------------- */
  function arrancar() {
    if (typeof window === 'undefined' || !window.claude || typeof window.claude.use !== 'function') return;

    Promise.all([window.claude.use('db'), window.claude.use('user'),
                 window.claude.use('assets')]).then(function (par) {
      /* El almacén resuelve nulo para quien solo lee, y también cuando no se
         declaró la capacidad. En los dos casos el clip no se dibuja. */
      var db = par[0], user = par[1], almacen = par[2];
      if (!db) return;               /* archivo de solo lectura: no se toca nada */

      var yo = null;
      var pendiente = Promise.resolve();
      if (user) { pendiente = user.id().then(function (id) { yo = id; })['catch'](function () {}); }

      /* La vista esconde los canales cerrados mientras no conste que quien mira
         puede editar. Se falla cerrado a propósito: si esto no responde, de más
         está no enseñarlos. El permiso de verdad no es este, es la regla de la
         colección: aunque alguien forzara la vista, `privado` no le devuelve
         nada. */
      if (user && typeof user.canEdit === 'function') {
        Promise.resolve(user.canEdit())['catch'](function () { return false; })
          .then(function (puede) { puedeEditar = !!puede; repintar(); });
      }

      pendiente.then(function () {
        /* Guarda. Se escribe el identificador, nunca el nombre. */
        function enviar(canal, texto, adjunto) {
          var ahora = new Date();
          var doc = {
            canal: canal,
            uid: yo || 'anon',
            texto: texto,
            fecha: fechaDe(ahora),
            hora: horaDe(ahora),
            ts: String(ahora.getTime() / 1000),
            creado: ahora.toISOString()
          };
          /* Del archivo se guarda el identificador, nunca la dirección: la
             dirección vale para la vista de quien lo subió y se arma luego a
             partir del identificador, que no caduca. */
          if (adjunto) {
            doc.adjunto = {
              id: adjunto.id, nombre: adjunto.nombre,
              tipo: adjunto.tipo, peso: adjunto.peso
            };
          }
          return db.collection(esCerrado(canal) ? COL_CERRADA : COL).add(doc);
        }

        if (document.body) montar(enviar, almacen);
        else document.addEventListener('DOMContentLoaded', function () { montar(enviar, almacen); });

        /* ---- los canales, creados desde dentro -----------------------------
           Dos suscripciones, una por colección. La de los cerrados le devuelve
           vacío a quien no es editor, así que no hace falta preguntar nada: la
           lista que llega ya es la que esa persona puede ver. */
        var canalesVivos = {};
        /* slug -> {col, id}, para poder renombrar después sin volver a buscar. */
        var dondeVive = {};

        function alLlegarCanales(cual, cerrado) {
          return function (snap) {
            var A = window.ARCHIVO;
            if (!A || !A.canales) return;
            canalesVivos[cual] = snap.docs.map(function (d) {
              var o = d.data() || {};
              if (o.canal) dondeVive[String(o.canal)] = { col: cual, id: d.id };
              return canalNuevo(o, cerrado);
            }).filter(function (c) { return !!c.canal; });
            var todos = [];
            for (var k in canalesVivos) { if (canalesVivos[k]) todos = todos.concat(canalesVivos[k]); }
            mezclarCanales(A, todos);
            repintar();
          };
        }

        [[COL_CANALES, false], [COL_CANALES_CERRADOS, true]].forEach(function (par) {
          db.collection(par[0]).orderBy('creado').onSnapshot(
            alLlegarCanales(par[0], par[1]),
            function () { /* el reintento lo hace la propia suscripción */ });
        });

        function crearCanal(nombre, icono, cerrado) {
          var slug = String(nombre).toLowerCase()
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
          if (!slug) return Promise.reject({ code: 'nombre_vacio' });
          var hay = (window.ARCHIVO && window.ARCHIVO.canales || []).some(function (c) {
            return c.canal === slug;
          });
          if (hay) return Promise.reject({ code: 'ya_existe' });
          return db.collection(cerrado ? COL_CANALES_CERRADOS : COL_CANALES).add({
            canal: slug,
            nombre: String(nombre).trim(),
            icono: String(icono || '').trim(),
            id: slug.toUpperCase(),
            creado: new Date().toISOString()
          });
        }

        /* Renombrar. Si el canal nació en `db` se actualiza su documento. Si
           nació dentro de la página no hay documento que tocar, así que se
           crea uno con su mismo nombre corto: la mezcla lo lee como un cambio
           de nombre y lo aplica encima, sin tocar el archivo. */
        function renombrarCanal(slug, nombre, icono) {
          var n = String(nombre || '').trim();
          if (!n) return Promise.reject({ code: 'nombre_vacio' });
          var donde = dondeVive[slug];
          var campos = { nombre: n, icono: String(icono || '').trim() };
          if (donde) return db.collection(donde.col).doc(donde.id).update(campos);
          campos.canal = slug;
          campos.id = slug.toUpperCase();
          campos.creado = new Date().toISOString();
          return db.collection(COL_CANALES).add(campos);
        }

        if (document.body) montarCanales(crearCanal, renombrarCanal);
        else document.addEventListener('DOMContentLoaded', function () { montarCanales(crearCanal, renombrarCanal); });

        /* Una suscripción por colección, fuera del pintado. Cada una guarda
           lo suyo y en cada aviso se rehace la lista entera: así un mensaje no
           se duplica ni se queda pegado cuando alguien lo borra.

           La colección cerrada se suscribe igual para todos. A quien no es
           editor el servidor le devuelve vacío, que es justo lo que tiene que
           pasar, y la página no necesita saber de permisos para comportarse
           bien. */
        var guardados = {};

        function alLlegar(cual) {
          return function (snap) {
            var A = window.ARCHIVO;
            if (!A || !A.canales) return;

            var crudos = [];
            snap.docs.forEach(function (d) {
              var o = d.data(); if (!o) return;
              /* La primera versión del espacio de Novasoft guardaba el
                 identificador en `autor` y la marca de tiempo en milisegundos.
                 No quedó ningún mensaje de entonces, pero si alguien tiene esa
                 página abierta todavía, lo que escriba se lee igual. */
              var ts = parseFloat(o.ts) || 0;
              if (ts > 1e12) ts = ts / 1000;
              crudos.push({
                id: d.id,
                canal: String(o.canal || (A.canales[0] && A.canales[0].canal) || ''),
                uid: String(o.uid || o.autor || 'anon'),
                texto: String(o.texto || ''),
                fecha: String(o.fecha || fechaDe(new Date(ts * 1000))),
                hora: String(o.hora || horaDe(new Date(ts * 1000))),
                ts: String(ts),
                adjunto: o.adjunto || null
              });
            });

            var ids = [];
            crudos.forEach(function (m) { if (m.uid && ids.indexOf(m.uid) < 0) ids.push(m.uid); });

            var nombres = user && user.profiles && ids.length
              ? user.profiles(ids)['catch'](function () { return {}; })
              : Promise.resolve({});

            nombres.then(function (ps) {
              guardados[cual] = crudos.map(function (m) {
                var p = ps && ps[m.uid];
                return {
                  /* `canal` tiene que viajar: `mezclar` agrupa por él, y sin él
                     todos los mensajes caían en el grupo `undefined` y ningún
                     canal recibía ninguno. Se guardaban bien y no se veían. */
                  canal: m.canal,
                  ts: m.ts, fecha: m.fecha, hora: m.hora,
                  autor: (p && p.name) || 'Alguien',
                  correo: '', uid: m.uid, texto: m.texto,
                  /* `/_blob/<id>` es la única ruta desde la raíz que el
                     artefacto sirve, y resuelve en todas sus versiones. Por eso
                     se arma aquí y no se guarda. */
                  adjuntos: m.adjunto && m.adjunto.id ? [{
                    id: m.adjunto.id,
                    nombre: String(m.adjunto.nombre || 'archivo'),
                    tipo: String(m.adjunto.tipo || ''),
                    peso: String(m.adjunto.peso || ''),
                    url: '/_blob/' + m.adjunto.id
                  }] : [],
                  hilo: null, reacciones: [], sistema: false
                };
              });
              var todos = [];
              for (var k in guardados) { if (guardados[k]) todos = todos.concat(guardados[k]); }
              mezclar(A, todos);
              repintar();
            });
          };
        }

        [COL, COL_CERRADA].forEach(function (cual) {
          db.collection(cual).orderBy('ts').onSnapshot(
            alLlegar(cual),
            function () { /* el reintento lo hace la propia suscripción */ });
        });
      });
    })['catch'](function () { /* sin capacidades: la app sigue siendo el archivo */ });
  }

  arrancar();
})();
