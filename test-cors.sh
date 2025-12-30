#!/bin/bash

# Script de test pour vérifier la configuration CORS sur Google Cloud Storage

BUCKET="dadoonet-talks"
PDF_PATH="slides/2012/2012-10-13-elasticsearch-osdc.pdf"
URL="https://storage.googleapis.com/${BUCKET}/${PDF_PATH}"

echo "=== Test de la configuration CORS ==="
echo ""
echo "URL testée: ${URL}"
echo ""

# Test 1: Vérifier la configuration CORS du bucket
echo "1. Vérification de la configuration CORS du bucket:"
echo "   Commande: gsutil cors get gs://${BUCKET}"
gsutil cors get gs://${BUCKET} 2>&1
echo ""

# Test 2: Tester avec curl depuis localhost
echo "2. Test avec curl (Origin: http://localhost:1313):"
curl -I -H "Origin: http://localhost:1313" "${URL}" 2>&1 | grep -i "access-control\|content-type\|http/"
echo ""

# Test 3: Tester avec curl depuis le domaine de production
echo "3. Test avec curl (Origin: https://david.pilato.fr):"
curl -I -H "Origin: https://david.pilato.fr" "${URL}" 2>&1 | grep -i "access-control\|content-type\|http/"
echo ""

# Test 4: Vérifier les permissions du bucket
echo "4. Vérification des permissions IAM du bucket:"
gsutil iam get gs://${BUCKET} 2>&1 | head -20
echo ""

echo "=== Fin des tests ==="
echo ""
echo "Si vous ne voyez pas 'Access-Control-Allow-Origin' dans les tests curl,"
echo "la configuration CORS n'est pas correctement appliquée."

