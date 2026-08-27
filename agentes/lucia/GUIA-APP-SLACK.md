# Cómo hacer que Lucía suba el PDF al canal

> El acuerdo original: el acta llega al canal **como documento PDF**, con el CSV de
> asistencia y el enlace de la grabación. Esta guía es lo que falta para lograrlo.

## Por qué hace falta esto

La conexión de Slack que usa Claude **no tiene ninguna herramienta para subir archivos**.
Envía mensajes, crea canvas y lee archivos que ya están ahí. Nada más. No es una
limitación de permisos: la operación no existe en esa conexión.

La salida es hablarle a Slack directamente con un token propio del workspace, que es lo
que hace `publicar_slack.py`. Para eso hacen falta dos cosas, y **las dos dependen de
Sandra** — ninguna se puede resolver desde aquí.

---

## 1 · Crear la app de Slack

1. Entrar a **api.slack.com/apps** → *Create New App* → *From scratch*.
2. Nombre: `Lucía IAM`. Workspace: `iamteamespacio`.
3. En **OAuth & Permissions → Bot Token Scopes**, agregar exactamente dos:
   - `files:write` — subir archivos
   - `chat:write` — publicar mensajes
4. Arriba en esa misma página, *Install to Workspace* y aceptar.
5. Copiar el **Bot User OAuth Token**. Empieza por `xoxb-`.

> **El token es una llave.** Quien lo tenga puede escribir en el workspace. No va en el
> chat, no va en el código, no va en Dropbox. Solo como variable de entorno.

6. En Slack, invitar al bot a cada canal donde vaya a publicar:
   `/invite @Lucía IAM` en `#contabilidad`, `#cumplimiento`, y los demás.
   **Sin esto, la subida falla con `not_in_channel`.**

## 2 · Guardar el token

En la configuración del entorno de Claude Code, como variable de entorno:

```
SLACK_BOT_TOKEN = xoxb-…
```

Se define al editar el entorno, junto a la política de red. Así el token vive en la
configuración y no aparece en ninguna conversación ni en el repositorio.

## 3 · Abrir la red

Este es el punto que hoy bloquea todo. El entorno tiene una política de red que
**rechaza slack.com**. Comprobado el 27 de agosto:

```
connect_rejected — gateway answered 403 to CONNECT — host: slack.com:443
```

Hay que permitir `slack.com` en la política de red del entorno. Se configura donde se
crea o edita el entorno de Claude Code; la documentación está en
code.claude.com/docs/en/claude-code-on-the-web.

Mientras la red esté cerrada, el script no puede funcionar: no es un problema del
código, es que no hay salida hacia Slack.

---

## Cómo se usa

Primero en seco, para revisar antes de que algo salga:

```bash
python3 agentes/lucia/publicar_slack.py \
    --canal C0BPDN9PKPH \
    --mensaje mensaje.txt \
    --archivo salida/ACTA_Sesion2_Contabilidad_26agosto2026.pdf \
    --archivo "…/Informe de asistencia 8-26-26.csv" \
    --simular
```

Sin `--simular`, publica: el mensaje al canal y los dos archivos detrás.

El script traduce los errores de Slack a algo accionable — si el bot no está en el
canal, si al token le falta un permiso, si la red está cerrada — en vez de devolver un
código suelto.

## Qué queda cuando esto funcione

| Pieza | Quién |
|---|---|
| Acta en PDF con identidad IAM™ | Lucía |
| CSV de asistencia | Lucía |
| Enlace de la grabación | Lucía |
| Arrastrar archivos a mano | **ya no hace falta** |

## Mientras tanto

Sandra arrastra el PDF y el CSV al canal. Es lo único que funciona hoy, y funciona.
