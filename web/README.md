# Página web IAM™ · iamlatam.co

Copia de trabajo de la página principal de IAM™. El sitio en producción está en Netlify (proyecto `papaya-chebakia-04e1af`) y se publica por carga manual.

## Qué hay aquí

| Archivo | Para qué sirve |
|---|---|
| `index.html` | Página principal, con el mensaje de IA empresarial y la sección IAE™ |
| `assets/tablero-iae-*.webp` | Pantallazos del Tablero IAE™ de demostración (datos simulados) |
| `assets/logo-iam.png` | Logo, antes incrustado 16 veces dentro del HTML |
| `og-image.png` | Imagen que aparece al compartir el enlace en LinkedIn y WhatsApp |
| `favicon.ico`, `assets/apple-touch-icon.png` | Ícono de la pestaña del navegador |
| `robots.txt`, `sitemap.xml` | Archivos para Google |

## Qué NO hay aquí

Los videos (`sandra-curvelo-video.mp4`, `fabian-gonzalez.mp4`, `testimonio-drummond.mp4`), `iam-globe.html` y la carpeta `guias/` solo existen en Netlify.

**Para publicar:** copia el contenido de esta carpeta dentro de la carpeta completa del sitio (la que ya tiene los videos y las guías), reemplaza `index.html`, y sube esa carpeta completa a Netlify. Si subes solo esta carpeta, se pierden los videos y las guías.

## Auditar

```bash
python3 scripts/web_ia_auditar.py https://iamlatam.co/
python3 scripts/web_ia_auditar.py web/index.html
```

El agente `web-ia` (en `.claude/agents/web-ia.md`) usa este auditor y además revisa la página a ojo en escritorio y celular.
