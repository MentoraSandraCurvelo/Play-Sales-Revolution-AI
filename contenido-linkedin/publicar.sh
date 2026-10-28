#!/usr/bin/env bash
# Publica en LinkedIn un post de la cola SOLO si Sandra lo aprobó.
# Uso: bash contenido-linkedin/publicar.sh <id>   (ej. jue-29-am)
set -euo pipefail

ID="${1:?Falta el id del post}"
DIR="$(cd "$(dirname "$0")" && pwd)"
FILE="$DIR/cola/$ID.json"
[ -f "$FILE" ] || { echo "No existe $FILE"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 -I - "$FILE" "$TMP/payload.json" <<'EOF'
import json, sys
q = json.load(open(sys.argv[1], encoding='utf-8'))
if q.get("estado") != "aprobado":
    sys.exit(f"No se publica: estado '{q.get('estado')}' (debe ser 'aprobado')")
if q.get("urn"):
    sys.exit(f"Ya publicado: {q['urn']}")
json.dump(q["payload"], open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False)
EOF

CODE=$(curl -sS -D "$TMP/headers" -o "$TMP/body" -w "%{http_code}" -X POST https://api.linkedin.com/rest/posts \
  -H "Content-Type: application/json" \
  -H "LinkedIn-Version: 202601" \
  -H "X-Restli-Protocol-Version: 2.0.0" \
  --data-binary @"$TMP/payload.json")

if [ "$CODE" != "201" ]; then
  echo "Error HTTP $CODE"; cat "$TMP/body"; exit 1
fi

URN=$(grep -i '^x-restli-id:' "$TMP/headers" | awk '{print $2}' | tr -d '\r')
python3 -I - "$FILE" "$URN" <<'EOF'
import json, sys, datetime
q = json.load(open(sys.argv[1], encoding='utf-8'))
q["estado"] = "publicado"
q["urn"] = sys.argv[2]
q["publicado_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
json.dump(q, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
EOF
echo "Publicado: https://www.linkedin.com/feed/update/$URN/"
