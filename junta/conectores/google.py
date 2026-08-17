"""Servidor MCP in-process: Gmail y Google Drive.

Habla directamente con las APIs REST usando un refresh token OAuth, en vez de
depender de `google-api-python-client`. Menos dependencias y el flujo de token es
explícito y auditable.

Alcances (scopes) que debe tener el refresh token:
- https://www.googleapis.com/auth/gmail.readonly     (leer correo)
- https://www.googleapis.com/auth/gmail.send         (enviar, solo si no hay modo lectura)
- https://www.googleapis.com/auth/drive              (leer y crear en Drive)
"""

from __future__ import annotations

import base64
import json
import time
from email.message import EmailMessage
from typing import Any

import httpx
from claude_agent_sdk import create_sdk_mcp_server, tool

from junta.conectores._util import (
    bloqueado_por_modo_lectura,
    datos,
    error,
    pedir_json,
    texto,
)
from junta.config import Settings

URL_TOKEN = "https://oauth2.googleapis.com/token"
API_GMAIL = "https://gmail.googleapis.com/gmail/v1/users/me"
API_DRIVE = "https://www.googleapis.com/drive/v3"
API_DRIVE_UPLOAD = "https://www.googleapis.com/upload/drive/v3"

# Documentos nativos de Google: hay que exportarlos, no descargarlos tal cual.
EXPORTABLES = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}


class _Credenciales:
    """Gestiona el access token, renovándolo cuando caduca."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._token: str | None = None
        self._expira_en: float = 0.0

    async def token(self) -> tuple[bool, str]:
        if self._token and time.time() < self._expira_en - 60:
            return True, self._token

        cuerpo = {
            "client_id": self._settings.google_client_id,
            "client_secret": self._settings.google_client_secret,
            "refresh_token": self._settings.google_refresh_token,
            "grant_type": "refresh_token",
        }
        async with httpx.AsyncClient(timeout=30.0) as c:
            ok, payload = await pedir_json(c, "POST", URL_TOKEN, data=cuerpo)
        if not ok:
            return False, (
                f"no se pudo renovar el token de Google ({payload}). Revisa "
                "GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET y GOOGLE_REFRESH_TOKEN."
            )
        self._token = payload.get("access_token")
        self._expira_en = time.time() + float(payload.get("expires_in", 3600))
        if not self._token:
            return False, "Google no devolvió access_token."
        return True, self._token


def _extraer_cuerpo(payload: dict[str, Any]) -> str:
    """Recorre el árbol MIME de un mensaje de Gmail y saca el texto plano."""
    partes = [payload]
    textos: list[str] = []
    while partes:
        parte = partes.pop(0)
        if parte.get("parts"):
            partes.extend(parte["parts"])
        cuerpo = parte.get("body", {})
        datos_b64 = cuerpo.get("data")
        if datos_b64 and parte.get("mimeType", "").startswith("text/plain"):
            textos.append(
                base64.urlsafe_b64decode(datos_b64 + "==").decode("utf-8", "replace")
            )
    return "\n".join(textos).strip()


def construir_servidor_google(settings: Settings) -> Any:
    credenciales = _Credenciales(settings)

    async def autorizado() -> tuple[bool, Any]:
        ok, valor = await credenciales.token()
        if not ok:
            return False, valor
        return True, {"Authorization": f"Bearer {valor}"}

    # ------------------------------------------------------------------
    # Gmail
    # ------------------------------------------------------------------
    @tool(
        "gmail_buscar",
        "Busca correos en Gmail con la sintaxis de búsqueda de Gmail y devuelve "
        "remitente, asunto, fecha y extracto. Ejemplos de consulta: "
        "'from:cliente@empresa.com', 'subject:propuesta newer_than:30d', "
        "'is:unread category:primary'. Úsalo para reconstruir el historial con un "
        "cliente o prospecto antes de opinar sobre esa relación.",
        {
            "type": "object",
            "properties": {
                "consulta": {
                    "type": "string",
                    "description": "Consulta en sintaxis de búsqueda de Gmail.",
                },
                "limite": {"type": "integer", "default": 10, "maximum": 30},
            },
            "required": ["consulta"],
            "additionalProperties": False,
        },
    )
    async def gmail_buscar(args: dict[str, Any]) -> dict[str, Any]:
        ok, cab = await autorizado()
        if not ok:
            return error(str(cab))
        limite = int(args.get("limite", 10))
        async with httpx.AsyncClient(headers=cab, timeout=45.0) as c:
            ok, lista = await pedir_json(
                c,
                "GET",
                f"{API_GMAIL}/messages",
                params={"q": args["consulta"], "maxResults": limite},
            )
            if not ok:
                return error(str(lista))
            ids = [m["id"] for m in lista.get("messages", [])]
            if not ids:
                return texto(f"Sin resultados para: {args['consulta']}")

            resumenes: list[dict[str, Any]] = []
            for mensaje_id in ids:
                ok_m, msg = await pedir_json(
                    c,
                    "GET",
                    f"{API_GMAIL}/messages/{mensaje_id}",
                    params={
                        "format": "metadata",
                        "metadataHeaders": ["From", "To", "Subject", "Date"],
                    },
                )
                if not ok_m:
                    continue
                cabeceras = {
                    h["name"]: h["value"]
                    for h in msg.get("payload", {}).get("headers", [])
                }
                resumenes.append(
                    {
                        "id": mensaje_id,
                        "de": cabeceras.get("From"),
                        "para": cabeceras.get("To"),
                        "asunto": cabeceras.get("Subject"),
                        "fecha": cabeceras.get("Date"),
                        "extracto": msg.get("snippet"),
                    }
                )
        return datos(resumenes, f"{len(resumenes)} correo(s)")

    @tool(
        "gmail_leer",
        "Lee el contenido completo de un correo por su id (el que devuelve "
        "`gmail_buscar`).",
        {
            "type": "object",
            "properties": {"mensaje_id": {"type": "string"}},
            "required": ["mensaje_id"],
            "additionalProperties": False,
        },
    )
    async def gmail_leer(args: dict[str, Any]) -> dict[str, Any]:
        ok, cab = await autorizado()
        if not ok:
            return error(str(cab))
        async with httpx.AsyncClient(headers=cab, timeout=45.0) as c:
            ok, msg = await pedir_json(
                c,
                "GET",
                f"{API_GMAIL}/messages/{args['mensaje_id']}",
                params={"format": "full"},
            )
        if not ok:
            return error(str(msg))
        cabeceras = {
            h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])
        }
        return datos(
            {
                "de": cabeceras.get("From"),
                "para": cabeceras.get("To"),
                "asunto": cabeceras.get("Subject"),
                "fecha": cabeceras.get("Date"),
                "cuerpo": _extraer_cuerpo(msg.get("payload", {})) or msg.get("snippet"),
            },
            "Correo",
        )

    @tool(
        "gmail_enviar",
        "Envía un correo desde la cuenta configurada. Acción de escritura hacia el "
        "exterior: requiere que la junta NO esté en modo lectura. En modo lectura, "
        "entrega el borrador redactado para que Sandra lo revise y lo envíe.",
        {
            "type": "object",
            "properties": {
                "para": {"type": "string", "description": "Destinatario."},
                "asunto": {"type": "string"},
                "cuerpo": {"type": "string", "description": "Texto plano del correo."},
                "cc": {"type": "string"},
            },
            "required": ["para", "asunto", "cuerpo"],
            "additionalProperties": False,
        },
    )
    async def gmail_enviar(args: dict[str, Any]) -> dict[str, Any]:
        if settings.modo_lectura:
            return bloqueado_por_modo_lectura("gmail_enviar")
        ok, cab = await autorizado()
        if not ok:
            return error(str(cab))
        mensaje = EmailMessage()
        mensaje["To"] = args["para"]
        mensaje["Subject"] = args["asunto"]
        if args.get("cc"):
            mensaje["Cc"] = args["cc"]
        mensaje.set_content(args["cuerpo"])
        crudo = base64.urlsafe_b64encode(mensaje.as_bytes()).decode()
        async with httpx.AsyncClient(headers=cab, timeout=45.0) as c:
            ok, payload = await pedir_json(
                c, "POST", f"{API_GMAIL}/messages/send", json={"raw": crudo}
            )
        if not ok:
            return error(str(payload))
        return datos(payload, "Correo enviado")

    # ------------------------------------------------------------------
    # Drive
    # ------------------------------------------------------------------
    @tool(
        "drive_buscar",
        "Busca archivos en Google Drive. Acepta texto simple (busca por nombre) o una "
        "consulta con la sintaxis de Drive, por ejemplo "
        "\"name contains 'propuesta' and modifiedTime > '2026-01-01T00:00:00'\".",
        {
            "type": "object",
            "properties": {
                "consulta": {
                    "type": "string",
                    "description": "Texto a buscar en el nombre, o consulta Drive completa.",
                },
                "limite": {"type": "integer", "default": 20, "maximum": 100},
            },
            "required": ["consulta"],
            "additionalProperties": False,
        },
    )
    async def drive_buscar(args: dict[str, Any]) -> dict[str, Any]:
        ok, cab = await autorizado()
        if not ok:
            return error(str(cab))
        consulta = args["consulta"]
        # Si no parece una consulta de Drive, la tratamos como búsqueda por nombre.
        if not any(op in consulta for op in ("contains", "=", ">", "<", " and ", " or ")):
            consulta = f"name contains '{consulta.replace(chr(39), '')}'"
        params = {
            "q": f"{consulta} and trashed = false",
            "pageSize": int(args.get("limite", 20)),
            "fields": "files(id,name,mimeType,modifiedTime,size,webViewLink,owners(displayName))",
            "orderBy": "modifiedTime desc",
        }
        async with httpx.AsyncClient(headers=cab, timeout=45.0) as c:
            ok, payload = await pedir_json(c, "GET", f"{API_DRIVE}/files", params=params)
        if not ok:
            return error(str(payload))
        archivos = payload.get("files", [])
        if not archivos:
            return texto(f"Sin archivos que coincidan con: {args['consulta']}")
        return datos(archivos, f"{len(archivos)} archivo(s)")

    @tool(
        "drive_leer",
        "Lee el contenido de un archivo de Drive por su id. Los documentos nativos de "
        "Google (Docs, Sheets, Slides) se exportan a texto o CSV automáticamente.",
        {
            "type": "object",
            "properties": {"archivo_id": {"type": "string"}},
            "required": ["archivo_id"],
            "additionalProperties": False,
        },
    )
    async def drive_leer(args: dict[str, Any]) -> dict[str, Any]:
        ok, cab = await autorizado()
        if not ok:
            return error(str(cab))
        archivo_id = args["archivo_id"]
        async with httpx.AsyncClient(headers=cab, timeout=60.0) as c:
            ok, meta = await pedir_json(
                c,
                "GET",
                f"{API_DRIVE}/files/{archivo_id}",
                params={"fields": "id,name,mimeType"},
            )
            if not ok:
                return error(str(meta))
            tipo = meta.get("mimeType", "")
            if tipo in EXPORTABLES:
                url = f"{API_DRIVE}/files/{archivo_id}/export"
                params = {"mimeType": EXPORTABLES[tipo]}
            elif tipo.startswith("application/vnd.google-apps"):
                return error(
                    f"'{meta.get('name')}' es de tipo {tipo}, que no se puede exportar "
                    "a texto. Ábrelo manualmente en Drive."
                )
            else:
                url = f"{API_DRIVE}/files/{archivo_id}"
                params = {"alt": "media"}
            try:
                respuesta = await c.get(url, params=params)
            except Exception as exc:
                return error(f"fallo al descargar el archivo: {exc}")
            if respuesta.status_code >= 400:
                return error(f"HTTP {respuesta.status_code}: {respuesta.text[:600]}")
            contenido = respuesta.text
        return texto(f"# {meta.get('name')}\n\n{contenido}")

    @tool(
        "drive_crear_documento",
        "Crea un archivo de texto o Markdown en Google Drive. Úsalo para dejar en "
        "Drive las actas de junta, reportes y propuestas que produce la junta. "
        "Escribe en el Drive de Sandra, no envía nada a terceros.",
        {
            "type": "object",
            "properties": {
                "nombre": {
                    "type": "string",
                    "description": "Nombre del archivo, incluida la extensión (.md, .txt).",
                },
                "contenido": {"type": "string"},
                "carpeta_id": {
                    "type": "string",
                    "description": "Id de la carpeta destino. Si se omite, va a la raíz.",
                },
            },
            "required": ["nombre", "contenido"],
            "additionalProperties": False,
        },
    )
    async def drive_crear_documento(args: dict[str, Any]) -> dict[str, Any]:
        ok, cab = await autorizado()
        if not ok:
            return error(str(cab))

        metadatos: dict[str, Any] = {"name": args["nombre"]}
        if args.get("carpeta_id"):
            metadatos["parents"] = [args["carpeta_id"]]

        # Drive espera `multipart/related` para uploadType=multipart, no el
        # `multipart/form-data` que produciría httpx con `files=`. Se construye el
        # cuerpo a mano para que la subida no dependa de ese detalle.
        frontera = "iam-junta-boundary-7f3a1c"
        cuerpo = (
            f"--{frontera}\r\n"
            "Content-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{json.dumps(metadatos, ensure_ascii=False)}\r\n"
            f"--{frontera}\r\n"
            "Content-Type: text/plain; charset=UTF-8\r\n\r\n"
            f"{args['contenido']}\r\n"
            f"--{frontera}--\r\n"
        ).encode("utf-8")

        cabeceras = {**cab, "Content-Type": f"multipart/related; boundary={frontera}"}
        async with httpx.AsyncClient(headers=cabeceras, timeout=60.0) as c:
            ok, payload = await pedir_json(
                c,
                "POST",
                f"{API_DRIVE_UPLOAD}/files",
                params={"uploadType": "multipart", "fields": "id,name,webViewLink"},
                content=cuerpo,
            )
        if not ok:
            return error(str(payload))
        return datos(payload, "Documento creado en Drive")

    return create_sdk_mcp_server(
        name="google",
        version="1.0.0",
        tools=[
            gmail_buscar,
            gmail_leer,
            gmail_enviar,
            drive_buscar,
            drive_leer,
            drive_crear_documento,
        ],
    )
