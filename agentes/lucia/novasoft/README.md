# IAM™Hello Novasoft

**El espacio privado del proyecto de Novasoft.** No es el archivo de Comfacesar: aquí la
gente escribe, y lo que escribe se queda.

https://claude.ai/artifact/4LqxApF3bEi8gzJXiy6mgM

## Qué tiene

| Sección | Qué hace |
|---|---|
| **Conversación** | El canal del proyecto. Cada mensaje se guarda fuera de la página, con su autor y su fecha. Nadie lo borra y no caduca. |
| **Documentos** | El material que entrega IAM™. Se abre dentro de la página: el PDF dibujado con pdf.js, el CSV como tabla, la imagen y el vídeo con su etiqueta. |
| **Sesiones** | Grabación, acta y resumen de cada sesión, en orden. |
| **Qué es esto** | Tres tarjetas que explican el espacio a quien entra por primera vez. |

## Cómo se actualiza

**La página no se toca.** Todo lo que cambia vive en `datos.js`:

```js
window.NOVASOFT = {
  cliente: 'Novasoft',
  documentos: [{ titulo: '...', archivo: 'docs/guia.pdf', nota: 'PDF · 2 MB' }],
  sesiones:  [{ numero: 1, titulo: 'Sesión 1', fecha: '...', resumen: '...',
                acta: 'actas/ACTA_S1.pdf', grabacion: 'https://...' }]
};
```

Los archivos viajan como archivos publicados al lado de la página, igual que las actas en
el archivo de Comfacesar, y se referencian por su ruta relativa.

## Lo que hay que saber antes de prometer nada

- **Quien entre tiene que iniciar sesión.** Los invitados por correo sirven, incluidos los de
  fuera de la organización, pero no es un enlace anónimo.
- **No hay notificaciones ni aplicación de celular.** Si alguien escribe, a nadie le suena.
  Esa es la diferencia real con Slack y hay que resolverla por fuera, por ejemplo con un
  correo diario del agente.
- **Escribe quien tenga permiso de colaborar.** Quien entre como lector ve la conversación y
  no puede escribir: la página se lo dice en vez de dejar el botón muerto.
- **Borrar.** La página no ofrece borrar ningún mensaje. Un colaborador con permiso sí podría
  hacerlo por fuera de la interfaz; si eso llega a importar, se cambia la regla para que cada
  quien solo pueda escribir en su propia rama.

## Comprobado el 6 de octubre

Se escribió un mensaje de prueba en la base, se leyó **al nivel de un invitado corriente**
para confirmar que lo ve, y se borró. La conversación en vivo y el visor de documentos se
prueban cuando entre la primera persona invitada.
