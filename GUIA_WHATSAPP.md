# Cómo conectar tu agente de IA a WhatsApp

Guía completa, de cero a funcionando. No necesitas saber programar: el código ya
está escrito. Lo que sigue es conectar las cuentas.

**Tiempo estimado:** 1 a 2 horas la primera vez.

---

## Antes de empezar: lo que tienes que entender

WhatsApp **no permite** que un programa se conecte a tu WhatsApp normal (el de tu
celular). Está prohibido por sus términos y las herramientas que lo prometen
terminan con el número bloqueado.

La vía legítima es la **WhatsApp Business Platform** (antes "Cloud API") de Meta.
Es gratuita de instalar y funciona así:

```
Cliente escribe  →  Meta  →  tu servidor (este código)  →  Claude
                                      ↓
Cliente recibe  ←  Meta  ←  respuesta del agente
```

### Requisitos

| Necesitas | Detalle |
|---|---|
| **Un número de teléfono** | **No puede estar registrado en WhatsApp** (ni normal ni Business). Si tu número actual ya tiene WhatsApp, usa uno nuevo, o borra la cuenta de ese número antes (perderás su historial). |
| **Cuenta de Meta Business** | Gratis, en business.facebook.com |
| **Tarjeta de crédito** | Meta la pide para verificar, aunque no gastes al inicio. |
| **Cuenta de Anthropic** | console.anthropic.com, con crédito cargado. |
| **Un servidor** | Donde vive este código. Render tiene plan gratis. |

> **Consejo:** compra una eSIM o una línea prepago solo para el bot. Así tu número
> personal sigue siendo tuyo y el del negocio queda separado.

---

## Paso 1 · Crea la app en Meta

1. Entra a **developers.facebook.com** e inicia sesión con tu Facebook.
2. Arriba a la derecha: **Mis apps** → **Crear app**.
3. En "¿Qué quieres que haga tu app?" elige **Otro** → **Siguiente**.
4. Tipo de app: **Negocio** → **Siguiente**.
5. Ponle nombre (ej. `Agente IAM`), tu correo, y vincula tu cuenta de Meta Business.
6. **Crear app**.

---

## Paso 2 · Añade WhatsApp

1. Dentro de tu app, busca la tarjeta **WhatsApp** → **Configurar**.
2. Meta te da un **número de prueba** gratuito. Úsalo para todas las pruebas.
3. En **WhatsApp → Configuración de la API** anota:
   - **Identificador del número de teléfono** (`Phone number ID`) → es tu `WHATSAPP_PHONE_NUMBER_ID`
   - **Identificador de la cuenta de WhatsApp Business**
4. Ahí mismo, en "Para", agrega tu número personal a la lista de destinatarios de
   prueba (hasta 5). Solo esos números pueden recibir mensajes mientras pruebas.

---

## Paso 3 · Consigue las 3 credenciales

### 3.1 · App Secret

**Configuración de la app → Básica → Clave secreta de la app → Mostrar.**
Cópiala. Es tu `WHATSAPP_APP_SECRET`.

*Esto es lo que impide que un desconocido haga que tu agente responda y te
genere costos. No la compartas nunca.*

### 3.2 · Token permanente

El token que te muestra Meta en pantalla **caduca en 24 horas**. Para uno que no
expire:

1. Ve a **business.facebook.com** → **Configuración del negocio**.
2. Menú izquierdo: **Usuarios** → **Usuarios del sistema** → **Agregar**.
3. Nombre: `agente-whatsapp`. Rol: **Administrador** → **Crear**.
4. Selecciónalo → **Agregar activos** → pestaña **Apps** → marca tu app →
   activa **Control total** → **Guardar cambios**.
5. **Generar nuevo token** → elige tu app → marca estos dos permisos:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
6. **Generar token** → **cópialo ahora**, no se vuelve a mostrar.

Ese es tu `WHATSAPP_TOKEN`.

### 3.3 · Verify Token

Este te lo inventas tú. Cualquier frase larga, por ejemplo:
`iam-sandra-2026-verificacion-xk92`. Es tu `WHATSAPP_VERIFY_TOKEN`.

Sirve para que Meta y tu servidor se reconozcan la primera vez.

---

## Paso 4 · Clave de Claude

1. Entra a **console.anthropic.com**.
2. **Settings → API Keys → Create Key**. Cópiala (empieza por `sk-ant-`).
3. En **Billing**, carga saldo. Con 20 USD tienes para cientos de conversaciones.

Esa es tu `ANTHROPIC_API_KEY`.

> **Importante:** esta clave es distinta de tu suscripción a Claude.ai. La API se
> paga por uso, aparte.

---

## Paso 5 · Prueba el código en tu computador

```bash
git clone https://github.com/MentoraSandraCurvelo/Play-Sales-Revolution-AI.git
cd Play-Sales-Revolution-AI

python -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r whatsapp_agent/requirements.txt
```

Antes de conectar nada, verifica que todo funciona (no gasta dinero, simula
a Meta y a Claude):

```bash
python -m whatsapp_agent.prueba_local
```

Debe terminar en `✅ Todo funciona`.

Ahora crea tu archivo de credenciales:

```bash
cp .env.example .env
```

Abre `.env` y pega los cinco valores de los pasos 3 y 4.

> El archivo `.env` **nunca** se sube a GitHub (ya está en `.gitignore`).
> Si alguna clave se filtra, revócala y genera otra.

Arranca el servidor:

```bash
uvicorn whatsapp_agent.main:app --reload --port 8000
```

Si ves `Agente listo. Modelo: claude-opus-5`, vas bien.

---

## Paso 6 · Publica el servidor en internet

Meta necesita una URL pública con HTTPS. Dos caminos:

### Opción A · Para probar hoy mismo (ngrok)

En otra terminal, con el servidor corriendo:

```bash
ngrok http 8000
```

Te da una URL tipo `https://a1b2c3.ngrok-free.app`. **Ojo:** cambia cada vez que
reinicias ngrok, y tendrás que reconfigurar el webhook en Meta.

### Opción B · Para producción (Render, gratis)

1. Entra a **render.com** → **New → Web Service** → conecta este repositorio.
2. Configura:
   - **Build Command:** `pip install -r whatsapp_agent/requirements.txt`
   - **Start Command:** `uvicorn whatsapp_agent.main:app --host 0.0.0.0 --port $PORT`
3. En **Environment**, agrega una por una las variables de tu `.env`.
4. **Create Web Service**. Te queda una URL fija tipo
   `https://agente-iam.onrender.com`.

> El plan gratuito de Render "duerme" el servicio tras 15 minutos sin uso, y el
> primer mensaje después tarda ~30 segundos. Para uso real, el plan de 7 USD/mes
> lo evita.
>
> Ese plan gratuito también borra el disco en cada despliegue: la base de datos
> `whatsapp_agent.db` (historial y leads) se pierde. Para conservarla, añade un
> disco persistente y apunta `DB_PATH` a él.

---

## Paso 7 · Conecta el webhook

1. En Meta: **tu app → WhatsApp → Configuración**, sección **Webhook** → **Editar**.
2. Rellena:
   - **URL de devolución de llamada:** tu URL **+ `/webhook`**
     → `https://agente-iam.onrender.com/webhook`
   - **Token de verificación:** el `WHATSAPP_VERIFY_TOKEN` que inventaste.
3. **Verificar y guardar**. Si falla, revisa que el servidor esté corriendo y que
   el token sea idéntico en los dos lados.
4. Justo debajo, en **Campos del webhook** → **Administrar** → activa
   **`messages`**. **Sin esto no llega nada.** Es el error más común.

---

## Paso 8 · Pruébalo

Desde tu celular (el número que agregaste como destinatario de prueba), escribe
al número de prueba de Meta.

Deberías ver la respuesta del agente en segundos, y en los logs del servidor:

```
INFO Mensaje de Sandra (573...): Hola
INFO Lead guardado (573...): Sandra
```

**Si no responde**, revisa en orden:

| Síntoma | Causa habitual |
|---|---|
| No llega nada al servidor | Falta activar el campo `messages` en el webhook (paso 7.4) |
| `403 Firma inválida` | El `WHATSAPP_APP_SECRET` está mal copiado |
| `401` al enviar | El `WHATSAPP_TOKEN` caducó — usa el permanente del paso 3.2 |
| El agente responde dos veces | Meta reintentó; el código ya lo evita, revisa que la base de datos no se esté borrando |
| Error de Anthropic | Falta saldo en console.anthropic.com |

---

## Paso 9 · Pasa a tu número real

Cuando estés conforme:

1. **WhatsApp → Configuración de la API → Agregar número de teléfono.**
2. Verifícalo por SMS o llamada.
3. Completa la **verificación del negocio** de Meta (te piden documentos de la
   empresa; tarda de horas a días).
4. Cambia el `WHATSAPP_PHONE_NUMBER_ID` en tus variables por el del número nuevo.

Con el número de prueba solo puedes escribirle a 5 contactos. Con el tuyo
verificado, a cualquiera.

---

## Cuánto cuesta

**Meta:** hoy las conversaciones que inicia el cliente (te escribe primero y tú
respondes dentro de 24 horas) no tienen costo. Las plantillas de marketing o
utilidad que tú inicias sí se cobran, y varía por país. Meta cambia esta
política con cierta frecuencia: confirma en
`developers.facebook.com/docs/whatsapp/pricing` antes de proyectar números.

**Claude:** con Opus 5, alrededor de **1 centavo de dólar por mensaje**
respondido. Una conversación completa de 10 mensajes ≈ 10 centavos. Cien
conversaciones al mes ≈ 10 USD.

¿Quieres bajarlo? En tus variables cambia:

```
AGENTE_MODELO=claude-sonnet-5     # menos de la mitad del costo
```

---

## Cómo lo ajustas tú

### Cambiar la personalidad, los servicios o cómo califica

Todo está en **`whatsapp_agent/prompts.py`**, escrito en español y comentado.
Edita el texto de `SISTEMA` y reinicia. No necesitas tocar nada más.

Ahí puedes cambiar el tono, agregar tus servicios con sus descripciones, ajustar
las preguntas de calificación o poner tus propios límites.

### Compartir tu Calendly

En `.env`, pon tu enlace en `LINK_AGENDA`. El agente lo comparte solo cuando
detecta interés real, no en el primer mensaje.

### Ver los leads capturados

Pon un `ADMIN_TOKEN` (una clave larga que inventes) en tus variables y consulta:

```bash
curl -H "Authorization: Bearer TU_ADMIN_TOKEN" https://tu-servidor.com/leads
```

### Cuando el agente te pasa un chat

Si alguien pide hablar contigo, el agente **se calla en ese chat** y lo verás en
los logs marcado como `ESCALAMIENTO`, con un resumen de la conversación. A partir
de ahí respondes tú desde la app de WhatsApp Business.

Para devolverle el control al agente en ese chat:

```bash
curl -X POST -H "Authorization: Bearer TU_ADMIN_TOKEN" \
  https://tu-servidor.com/reanudar/573001112233
```

---

## Lo que este agente hace y lo que no

**Sí hace:**
- Responde en español con tu voz de marca, en mensajes cortos de WhatsApp.
- Recuerda la conversación completa con cada persona.
- Califica al lead (nombre, empresa, necesidad, urgencia, temperatura) y lo guarda.
- Comparte tu agenda cuando detecta interés real.
- Te pasa el chat cuando el caso lo amerita, y se calla hasta que tú digas.
- No inventa precios ni promete resultados: son reglas explícitas del prompt.
- Ignora mensajes duplicados y verifica la firma de cada webhook.

**No hace (todavía):**
- Escuchar notas de voz ni leer imágenes o PDFs. Responde pidiendo texto.
- Enviar plantillas para iniciar conversaciones en frío.
- Escribir en tu CRM. Los leads quedan en la base local.

Cualquiera de esas se puede agregar. Pídemelo cuando lo necesites.

---

## Seguridad: tres reglas

1. **Nunca subas el `.env` a GitHub.** Ya está bloqueado, no lo desbloquees.
2. **Si una clave se filtra, revócala inmediatamente** y genera otra. Una clave
   de Anthropic filtrada la gasta un desconocido a tu costa.
3. **No quites la verificación de firma.** Es lo único que impide que cualquiera
   que descubra tu URL dispare conversaciones que tú pagas.
