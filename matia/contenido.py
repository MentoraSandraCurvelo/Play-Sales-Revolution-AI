"""Los 3 dolores principales y el contenido de valor que MATIA usa en cada toque.

Edita este archivo para ajustar el mensaje a tu oferta real.
Nota: no se incluyen estadísticas dentro de los correos a propósito. Si quieres
agregar una cifra, usa solo datos con fuente verificable.
"""

MARCA = {
    "nombre": "IAM™",
    "firma": "Sandra Curvelo",
    "rol": "Mentora en Social Selling y Marca Profesional",
    "rojo": "#E50914",
    "negro": "#0b0c0f",
    "gris": "#1a1c23",
    "blanco": "#FAFAFA",
    "texto_suave": "#B8BCC8",
    "fuente": "Montserrat, Arial, sans-serif",
    "cta_url": "https://www.linkedin.com/",  # cámbialo por tu link de agenda real
}

DOLORES = [
    {
        "titulo": "Vendedores invisibles en LinkedIn",
        "sintoma": "Tu equipo tiene perfil, pero no tiene presencia: nadie los busca, nadie los recuerda.",
        "consecuencia": "El cliente llega a la reunión ya comparando precios, porque nunca vio autoridad antes.",
        "valor": "Un perfil de vendedor no es una hoja de vida, es una vitrina. Cambia el titular de \"Ejecutivo comercial\" por el problema que resuelves y para quién.",
        "tip": "Reto de 5 minutos: pide a cada vendedor reescribir su titular con la fórmula Ayudo a [cliente] a lograr [resultado] sin [dolor].",
    },
    {
        "titulo": "Prospección en frío que no responde",
        "sintoma": "Mensajes genéricos, plantillas copiadas y la misma lista de contactos de siempre.",
        "consecuencia": "Más actividad no está generando más reuniones, solo más desgaste del equipo.",
        "valor": "El mensaje que funciona no vende en la primera línea, demuestra que investigaste. Primero contexto, después propuesta.",
        "tip": "Antes de escribir, interactúa 2 veces con el contenido del prospecto. Cuando llegue tu mensaje, ya no serás un extraño.",
    },
    {
        "titulo": "Pipeline lleno que no convierte",
        "sintoma": "Muchas oportunidades abiertas, pocas avanzan y nadie sabe exactamente por qué.",
        "consecuencia": "El forecast se vuelve un acto de fe y el cierre de mes depende de la suerte.",
        "valor": "Cada oportunidad necesita un siguiente paso con fecha. Si no tiene próxima acción, no es pipeline, es una lista de deseos.",
        "tip": "Revisa hoy tus 10 oportunidades más grandes y escribe para cada una: siguiente paso, fecha y responsable.",
    },
]

# Ángulo del mensaje según la etapa en el pipeline
ANGULO_ETAPA = {
    "Prospecto": "Te comparto una idea práctica, sin compromiso.",
    "Contactado": "Retomando nuestra conversación, quise dejarte algo útil para tu equipo.",
    "Reunión agendada": "Antes de vernos, te dejo una idea para que llegues con ventaja a la reunión.",
    "Propuesta enviada": "Mientras revisas la propuesta, te comparto el primer paso que trabajaríamos juntos.",
    "Negociación": "Para que tomes la decisión con toda la información, esto es lo que cambia en las primeras semanas.",
}

ASUNTOS = [
    "{nombre}, una idea para {empresa} esta semana",
    "{nombre}: el dolor que más frena a los equipos de {industria}",
    "3 dolores comerciales (y uno es el de {empresa})",
]
