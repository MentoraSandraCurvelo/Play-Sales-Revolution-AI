"""Conectores MCP de la junta directiva.

Externos (stdio): Airtable, Notion.
In-process (SDK MCP): Gmail + Drive, WhatsApp Cloud API, Meta Graph API, memoria Supabase.
"""

from junta.conectores.registry import Conectores, construir_conectores

__all__ = ["Conectores", "construir_conectores"]
