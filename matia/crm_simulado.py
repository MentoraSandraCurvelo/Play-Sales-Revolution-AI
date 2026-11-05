"""CRM simulado estilo Pipedrive para la clase de MATIA.

Todo es de mentira: empresas, personas y correos son ficticios.
Los correos usan el dominio reservado example.com para que nunca lleguen a nadie real.
"""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta

ETAPAS = ["Prospecto", "Contactado", "Reunión agendada", "Propuesta enviada", "Negociación"]

# Probabilidad de cierre por etapa (supuesto didáctico, no es un benchmark real)
PROBABILIDAD_ETAPA = {
    "Prospecto": 0.10,
    "Contactado": 0.20,
    "Reunión agendada": 0.40,
    "Propuesta enviada": 0.60,
    "Negociación": 0.80,
}


@dataclass
class Actividad:
    fecha: str
    tipo: str
    detalle: str


@dataclass
class Deal:
    id: int
    empresa: str
    contacto: str
    cargo: str
    email: str
    industria: str
    ciudad: str
    valor_cop: int
    etapa: str
    dolor_principal: int  # índice 0, 1 o 2 de DOLORES
    ultimo_toque: str
    toques_matia: int = 0
    demo: bool = False
    actividades: list = field(default_factory=list)

    @property
    def probabilidad(self) -> float:
        return PROBABILIDAD_ETAPA[self.etapa]

    @property
    def valor_ponderado(self) -> int:
        return int(self.valor_cop * self.probabilidad)

    def dias_sin_toque(self, hoy: date) -> int:
        return (hoy - date.fromisoformat(self.ultimo_toque)).days

    def to_dict(self) -> dict:
        d = asdict(self)
        d["probabilidad"] = self.probabilidad
        return d


_EMPRESAS = [
    ("Andina Logística", "Logística"), ("Nexo Seguros", "Seguros"), ("Altamira Software", "Tecnología"),
    ("Cafés del Quindío Export", "Alimentos"), ("Grupo Inmobiliario Prado", "Inmobiliario"),
    ("Clínica Horizonte", "Salud"), ("Banca Futura", "Servicios financieros"),
    ("EduMás Corporativo", "Educación"), ("Textiles Medellín Pro", "Manufactura"),
    ("Energía Solar Caribe", "Energía"), ("Consultores Bolívar", "Consultoría"),
    ("Farmacorp Andes", "Farmacéutica"), ("Telecom Pacífico", "Telecomunicaciones"),
    ("Agroinsumos del Llano", "Agroindustria"), ("Retail Plaza 93", "Retail"),
    ("Automotores Sabana", "Automotriz"), ("Hotelería Cartagena Bay", "Turismo"),
    ("Constructora Altos del Sol", "Construcción"), ("Fintech Pago Ya", "Fintech"),
    ("Laboratorios Vital", "Salud"), ("Distribuidora Norte", "Distribución"),
    ("Cloud Latam Partners", "Tecnología"), ("Seguros Cóndor", "Seguros"),
    ("Mobiliario Nórdico Bogotá", "Retail"), ("Transportes Magdalena", "Logística"),
    ("Aseguradora Guardián", "Seguros"), ("DataPro Analytics", "Tecnología"),
    ("Lácteos La Sabana", "Alimentos"), ("Urbana Propiedades", "Inmobiliario"),
    ("Odonto Sonrisa Red", "Salud"), ("Cooperativa Avanza", "Servicios financieros"),
    ("Academia Líderes 360", "Educación"), ("Plásticos Industriales Cali", "Manufactura"),
    ("Eólica Guajira", "Energía"), ("Estrategia & Talento", "Consultoría"),
    ("Conecta Fibra", "Telecomunicaciones"), ("Flores del Oriente", "Agroindustria"),
    ("Moda Express Andina", "Retail"), ("Motos del Valle", "Automotriz"),
    ("SaaS Contable Pro", "Tecnología"),
]
_NOMBRES = ["Laura", "Andrés", "Camila", "Santiago", "Valentina", "Juan Pablo", "Daniela", "Felipe",
            "Mariana", "Sebastián", "Natalia", "Carlos", "Paula", "Alejandro", "Catalina", "Mateo",
            "Juliana", "Ricardo", "Isabella", "Diego", "Manuela", "Esteban", "Sofía", "Tomás"]
_APELLIDOS = ["Gómez", "Restrepo", "Martínez", "Ospina", "Rodríguez", "Vélez", "Pardo", "Castaño",
              "Herrera", "Zuluaga", "Moreno", "Arango", "Salazar", "Quintero", "Rojas", "Cárdenas"]
_CARGOS = ["Director Comercial", "Gerente de Ventas", "VP de Ventas", "Head of Sales",
           "Gerente General", "Directora de Marketing", "Líder de Desarrollo de Negocio"]
_CIUDADES = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga", "Pereira", "Cartagena"]


def _slug(texto: str) -> str:
    tabla = str.maketrans("áéíóúñÁÉÍÓÚÑ", "aeiounAEIOUN")
    return "".join(c for c in texto.translate(tabla).lower() if c.isalnum())


def crear_pipeline(hoy: date | None = None, semilla: int = 2026) -> list[Deal]:
    """Genera un pipeline ficticio reproducible, con un Cliente Demo fijo de primero."""
    hoy = hoy or date.today()
    rnd = random.Random(semilla)
    deals: list[Deal] = []

    demo = Deal(
        id=1, empresa="Cliente Demo S.A.S.", contacto="Andrea (Cliente Demo)", cargo="Directora Comercial",
        email="cliente.demo@example.com", industria="Servicios B2B", ciudad="Bogotá",
        valor_cop=48_000_000, etapa="Contactado", dolor_principal=0,
        ultimo_toque=(hoy - timedelta(days=9)).isoformat(), demo=True,
    )
    demo.actividades.append(asdict(Actividad(demo.ultimo_toque, "Llamada", "Primera conversación, interés en social selling para su equipo de 12 vendedores.")))
    deals.append(demo)

    for i, (empresa, industria) in enumerate(_EMPRESAS, start=2):
        nombre = rnd.choice(_NOMBRES)
        apellido = rnd.choice(_APELLIDOS)
        etapa = rnd.choices(ETAPAS, weights=[30, 25, 20, 15, 10])[0]
        dias = rnd.randint(1, 30)
        d = Deal(
            id=i, empresa=empresa, contacto=f"{nombre} {apellido}", cargo=rnd.choice(_CARGOS),
            email=f"{_slug(nombre)}.{_slug(apellido)}@{_slug(empresa)}.example.com",
            industria=industria, ciudad=rnd.choice(_CIUDADES),
            valor_cop=rnd.randrange(8_000_000, 120_000_000, 1_000_000), etapa=etapa,
            dolor_principal=rnd.randint(0, 2), ultimo_toque=(hoy - timedelta(days=dias)).isoformat(),
        )
        d.actividades.append(asdict(Actividad(d.ultimo_toque, "Nota", f"Deal creado en etapa {etapa}.")))
        deals.append(d)
    return deals


def clonar(deals: list[Deal]) -> list[Deal]:
    return copy.deepcopy(deals)
