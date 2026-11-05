# MATIA · Agente de toques de valor (demo para clase)

Todo es **simulado**: el CRM tipo Pipedrive, los clientes, los correos y las respuestas. Nada sale a internet.

## Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

En el menú lateral entra a **MATIA Agente de Correos**.

## Guion para la clase

1. **Conectar CRM**: pantalla de login de mentira, se sincroniza un pipeline de 41 deals ficticios.
2. **Pipeline**: tablero por etapas. El *Cliente Demo* aparece resaltado en rojo.
3. **MATIA: jornada de hoy**: muestra los 10 deals elegidos y por qué (prioridad = valor ponderado en millones COP × días sin toque). Botón *Ejecutar MATIA* genera los 10 correos con el layout de marca y los 3 dolores.
4. **Cliente Demo**: la ficha se actualiza sola: nuevo correo en la línea de tiempo, respuesta simulada y cambio de etapa.
5. **Avanzar al día siguiente**: repite la jornada y el Cliente Demo sigue avanzando hasta Negociación.

## Dónde se edita

- `matia/contenido.py`: colores de marca, firma, link de agenda y los 3 dolores con su toque de valor.
- `matia/crm_simulado.py`: clientes ficticios y etapas del pipeline.
- `matia/agente.py`: reglas (10 correos por día, mínimo 3 días entre toques) y el HTML del correo.

Versión terminal: `python run_matia.py 5` guarda 5 días de correos en `salida_matia/`.
