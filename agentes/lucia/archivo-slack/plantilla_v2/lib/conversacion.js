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

  var COL = 'mensajes';
  var LIMITE = 4000;

  function dos(n) { return (n < 10 ? '0' : '') + n; }
  function fechaDe(d) { return d.getFullYear() + '-' + dos(d.getMonth() + 1) + '-' + dos(d.getDate()); }
  function horaDe(d) { return dos(d.getHours()) + ':' + dos(d.getMinutes()); }

  /* El componente no se expone en ninguna parte, así que para pedirle que
     repinte hay que encontrarlo. Se busca el nodo de React y se sube por el
     árbol hasta el que tiene `msgCache`, que es el nuestro. Si cambia la
     versión de React y esto deja de encontrarlo, no se rompe nada: los
     mensajes siguen guardándose y aparecen la próxima vez que se abra. */
  var _inst = null;
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
          var sn = f.stateNode;
          if (sn && typeof sn.setState === 'function' && sn.msgCache && sn.by) return (_inst = sn);
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
    inst.msgCache = {};
    try { inst.setState({}); } catch (e) { return false; }
    return true;
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

  function mezclar(A, vivos) {
    guardarBase(A);
    var porCanal = {};
    vivos.forEach(function (m) { (porCanal[m.canal] = porCanal[m.canal] || []).push(m); });
    (A.canales || []).forEach(function (c) {
      var nuevos = porCanal[c.canal] || [];
      var todos = base[c.canal].concat(nuevos);
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

  function canalDelHash() {
    var t = decodeURIComponent(String(location.hash || '').replace(/^#\/?/, '')).split('/').filter(Boolean);
    if (!t.length) return null;
    if (['actas', 'personas', 'archivos', 'grabaciones', 'asistencia'].indexOf(t[0]) >= 0) return null;
    return t[0];
  }

  function montar(enviar) {
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
    fila.appendChild(campo); fila.appendChild(boton);
    caja.appendChild(fila); caja.appendChild(nota);
    document.body.appendChild(caja);

    function crecer() {
      campo.style.height = 'auto';
      campo.style.height = Math.min(campo.scrollHeight, 140) + 'px';
    }
    function decir(t) { nota.textContent = t || ''; }

    var mandando = false;
    function manda() {
      var txt = campo.value.trim();
      if (!txt || mandando) return;
      if (txt.length > LIMITE) { decir('El mensaje es muy largo, quedan ' + (txt.length - LIMITE) + ' caracteres de más.'); return; }
      var canal = canalDelHash();
      if (!canal) return;
      mandando = true; boton.disabled = true; decir('Enviando…');
      enviar(canal, txt).then(function () {
        campo.value = ''; crecer(); decir('');
      })['catch'](function (err) {
        var c = err && err.code;
        decir(c === 'permission_denied' || c === 'not_granted'
          ? 'No tienes permiso para escribir en este espacio.'
          : 'No se pudo enviar. Vuelve a intentarlo.');
      }).then(function () { mandando = false; boton.disabled = false; });
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

  /* ---- arranque ---------------------------------------------------------- */
  function arrancar() {
    if (typeof window === 'undefined' || !window.claude || typeof window.claude.use !== 'function') return;

    Promise.all([window.claude.use('db'), window.claude.use('user')]).then(function (par) {
      var db = par[0], user = par[1];
      if (!db) return;               /* archivo de solo lectura: no se toca nada */

      var yo = null;
      var pendiente = Promise.resolve();
      if (user) { pendiente = user.id().then(function (id) { yo = id; })['catch'](function () {}); }

      pendiente.then(function () {
        /* Guarda. Se escribe el identificador, nunca el nombre. */
        function enviar(canal, texto) {
          var ahora = new Date();
          return db.collection(COL).add({
            canal: canal,
            uid: yo || 'anon',
            texto: texto,
            fecha: fechaDe(ahora),
            hora: horaDe(ahora),
            ts: String(ahora.getTime() / 1000),
            creado: ahora.toISOString()
          });
        }

        if (document.body) montar(enviar);
        else document.addEventListener('DOMContentLoaded', function () { montar(enviar); });

        /* Una suscripción, fuera del pintado. */
        db.collection(COL).orderBy('ts').onSnapshot(function (snap) {
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
              ts: String(ts)
            });
          });

          var ids = [];
          crudos.forEach(function (m) { if (m.uid && ids.indexOf(m.uid) < 0) ids.push(m.uid); });

          var nombres = user && user.profiles && ids.length
            ? user.profiles(ids)['catch'](function () { return {}; })
            : Promise.resolve({});

          nombres.then(function (ps) {
            var vivos = crudos.map(function (m) {
              var p = ps && ps[m.uid];
              return {
                ts: m.ts, fecha: m.fecha, hora: m.hora,
                autor: (p && p.name) || 'Alguien',
                correo: '', uid: m.uid, texto: m.texto,
                adjuntos: [], hilo: null, reacciones: [], sistema: false
              };
            });
            mezclar(A, vivos);
            repintar();
          });
        }, function () { /* el reintento lo hace la propia suscripción */ });
      });
    })['catch'](function () { /* sin capacidades: la app sigue siendo el archivo */ });
  }

  arrancar();
})();
