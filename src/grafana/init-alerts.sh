#!/bin/sh
set -e

echo "🔍 Attente que Grafana soit disponible..."
until curl -s -o /dev/null -w "%{http_code}" http://admin:admin@grafana:3000/api/health | grep -q "200"; do
  sleep 2
done
echo "✅ Grafana est en ligne !"

GRAFANA_URL="http://admin:admin@grafana:3000"
CONTACT_NAME="Discord-MLOps"
FOLDER_NAME="MLOps_Alerts"
FOLDER_UID="mlops-alerts-folder" # On définit un UID fixe pour notre dossier

# 0. CRÉATION DU DOSSIER D'ALERTES (Prérequis obligatoire)
echo "📁 Vérification/Création du dossier d'alertes : $FOLDER_NAME..."
# On tente de créer le dossier avec l'UID choisi. Si 409 (existe), on continue.
RESP_FOLDER=$(curl -s -w "\n%{http_code}" -X POST "$GRAFANA_URL/api/folders" \
  -H "Content-Type: application/json" \
  -d "{
    \"uid\": \"$FOLDER_UID\",
    \"title\": \"$FOLDER_NAME\"
  }")

CODE_FOLDER=$(echo "$RESP_FOLDER" | tail -n1)
if [ "$CODE_FOLDER" -eq 200 ] || [ "$CODE_FOLDER" -eq 201 ]; then
  echo "✅ Dossier créé avec UID: $FOLDER_UID"
elif [ "$CODE_FOLDER" -eq 409 ]; then
  echo "ℹ️  Dossier déjà existant (UID: $FOLDER_UID). On l'utilise."
else
  echo "⚠️  Erreur création dossier (Code: $CODE_FOLDER). On tente quand même la suite."
  # En cas d'erreur inattendue, on essaie de récupérer l'UID du dossier "General" par défaut si besoin,
  # mais ici on force notre UID car les règles le référenceront.
fi

# 1. CONFIGURATION DU CONTACT POINT
if [ -n "$DISCORD_WEBHOOK_URL" ]; then
  echo "📞 Configuration du Contact Point Discord..."
  
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$GRAFANA_URL/api/v1/provisioning/contact-points" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"$CONTACT_NAME\",
      \"type\": \"discord\",
      \"settings\": {
        \"url\": \"$DISCORD_WEBHOOK_URL\",
        \"use_discord_username\": false
      },
      \"disableResolveMessage\": false
    }")
  
  CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | head -n -1)
  
  if [ "$CODE" -eq 200 ] || [ "$CODE" -eq 201 ] || [ "$CODE" -eq 202 ]; then
    echo "✅ Contact Point créé avec succès ! (Code: $CODE)"
  elif [ "$CODE" -eq 409 ]; then
    echo "ℹ️  Contact Point déjà existant."
  else
    echo "❌ Erreur création Contact Point (Code: $CODE). Réponse: $BODY"
  fi
else
  echo "❌ ERREUR CRITIQUE : DISCORD_WEBHOOK_URL manquante."
  exit 1
fi

sleep 2

# 2. CONFIGURATION DES NOTIFICATION POLICIES
echo "📢 Configuration des Notification Policies..."
RESP_POLICY=$(curl -s -w "\n%{http_code}" -X PUT "$GRAFANA_URL/api/v1/provisioning/policies" \
  -H "Content-Type: application/json" \
  -d "{
    \"routes\": [
      {
        \"receiver\": \"$CONTACT_NAME\",
        \"object_matchers\": [[\"severity\", \"=\", \"critical\"]],
        \"group_by\": [\"alertname\"],
        \"group_wait\": \"30s\",
        \"group_interval\": \"5m\",
        \"repeat_interval\": \"4h\"
      },
      {
        \"receiver\": \"$CONTACT_NAME\",
        \"object_matchers\": [[\"severity\", \"=\", \"warning\"]],
        \"group_by\": [\"alertname\"],
        \"group_wait\": \"30s\",
        \"group_interval\": \"5m\",
        \"repeat_interval\": \"4h\"
      }
    ],
    \"receiver\": \"$CONTACT_NAME\",
    \"group_by\": [\"alertname\"],
    \"group_wait\": \"30s\",
    \"group_interval\": \"5m\",
    \"repeat_interval\": \"4h\"
  }")

CODE_POLICY=$(echo "$RESP_POLICY" | tail -n1)
if [ "$CODE_POLICY" -eq 200 ] || [ "$CODE_POLICY" -eq 202 ]; then
  echo "✅ Policies configurées."
else
  echo "❌ Erreur Policies (Code: $CODE_POLICY). Réponse: $(echo "$RESP_POLICY" | head -n -1)"
fi

# 3. CONFIGURATION DES RÈGLES D'ALERTE (Avec folderUID)
echo "🚨 Injection des règles d'alerte dans le dossier '$FOLDER_NAME'..."

# Fonction helper pour injecter une règle
inject_rule() {
  FILE=$1
  RULE_NAME=$2
  
  # Le fichier JSON contient déjà le "folderUID". On l'envoie tel quel.
  # Plus besoin de l'astuce sed qui risquerait de dupliquer la clé.
  
  RESP=$(curl -s -w "\n%{http_code}" -X POST "$GRAFANA_URL/api/v1/provisioning/alert-rules" \
    -H "Content-Type: application/json" \
    -d @"$FILE")

  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | head -n -1)

  if [ "$CODE" -eq 200 ] || [ "$CODE" -eq 201 ]; then
    echo "   ✅ Règle [$RULE_NAME] injectée."
  elif [ "$CODE" -eq 409 ]; then
    echo "   ℹ️  Règle [$RULE_NAME] existe déjà."
  else
    echo "   ❌ Erreur Règle [$RULE_NAME] (Code: $CODE). Réponse: $BODY"
  fi
}

# Injection Règle 1
inject_rule "/alert-rules/alert-error-rate.json" "Taux d'erreur"

# Injection Règle 2
inject_rule "/alert-rules/alert-latency.json" "Latence P95"

echo "✅ Initialisation terminée."