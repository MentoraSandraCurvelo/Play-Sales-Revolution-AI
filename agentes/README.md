# Agentes IAM™ Intelligence

Cada agente hace un trabajo concreto del programa, deja rastro de lo que hizo y reporta
al tablero. Sandra ve el tablero; los agentes hacen el resto.

| Agente | Trabajo | Corre | Estado |
|---|---|---|---|
| **Lucía** | Cierre de sesión: acta con identidad IAM™ → canal de Slack del área → archivo en Dropbox | Diario, 7:00 p.m. | En construcción |
| **Elia** | Seguimiento del programa en Slack: pulso NPS, avance por área, termómetro y alertas de áreas rezagadas | Continuo | Operando |

## Cómo se conectan

```
                    ┌──────────────────────────────┐
   Reunión Teams ──►│  LUCÍA — cierra la sesión    │──► Acta en el canal del área
                    │  19:00 · acta · Slack · PDF  │──► Archivo en Dropbox
                    └──────────────┬───────────────┘
                                   │ registra la sesión cerrada
                                   ▼
                    ┌──────────────────────────────┐
                    │  ELIA — mide el programa     │──► Pulso NPS por área
                    │  avance · NPS · termómetro   │──► Alertas de áreas rezagadas
                    └──────────────┬───────────────┘
                                   ▼
                          TABLERO DE AGENTES
```

Lucía alimenta a Elia: cada acta publicada es una sesión verificable, y el conteo de
sesiones por área es exactamente lo que Elia usa para el avance y para decidir qué áreas
entran al pulso NPS.

## Alcance del programa

21 áreas · 47 funcionarios · agosto → octubre 2026 · un canal de Slack por área.
Contraparte cliente: María Elvira Marulanda.

## Estructura

```
agentes/
├── README.md            este archivo
└── lucia/
    ├── LUCIA.md         especificación del agente
    ├── generar_acta.py  motor de actas: JSON → HTML + PDF con identidad IAM™
    ├── sesiones/        un JSON por sesión
    └── salida/          actas generadas (no se versionan)
```

Elia vive en la rama `claude/nps-survey-slack-comfacesar-h5ekyh`, carpeta `nps_comfacesar/`.

## Tablero

`agentes/tablero/sala-agentes-iam.html` — publicado en
https://claude.ai/code/artifact/a7bbe3e7-4e1f-4c07-997a-e42a834c890c

Muestra el estado de los dos agentes, el circuito de cierre de sesión, la cola de
sesiones sin acta y las 21 áreas con su canal y su estado.
