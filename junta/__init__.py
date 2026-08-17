"""Junta Directiva Agéntica IAM™.

Sistema multi-agente que opera como una junta directiva para el negocio de
Sandra Curvelo: consejeros especializados (finanzas, comercial, marca,
operaciones, legal, IA) que deliberan sobre el contexto real del negocio,
consultan sus sistemas vía conectores MCP y dejan memoria en Supabase.
"""

from junta.config import Settings, cargar_settings
from junta.junta import JuntaDirectiva

__all__ = ["JuntaDirectiva", "Settings", "cargar_settings"]
__version__ = "1.0.0"
