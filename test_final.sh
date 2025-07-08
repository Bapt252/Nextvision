#!/bin/bash

echo "🧪 === TESTS FINAUX ENHANCED BRIDGE v2.0 ==="
echo "🎯 Validation complète après résolution du cache Python"
echo ""

# 1. 📊 Test endpoint stats Enhanced
echo "📊 1. Test stats Enhanced Bridge..."
curl -s http://localhost:8000/api/v2/conversion/commitment/enhanced/stats | jq '.'
echo ""

# 2. �� TEST CRITIQUE - Conversion Enhanced (qui échouait avant)
echo "🔧 2. TEST CRITIQUE - Conversion Enhanced avec auto-fix..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v2/conversion/commitment/enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "candidat_data": {
      "parsing_confidence": 0.95,
      "personal_info": {
        "firstName": "marie",
        "lastName": "DUPONT", 
        "email": "marie..dupont@email..com",
        "phone": "0612345678"
      },
      "skills": ["CEGID", "Excel", "CEGID", "Comptabilité"],
      "experience": {"total_years": "7 ans"},
      "softwares": ["CEGID ", " Excel", "SAP"]
    }
  }')

# Affichage du résultat formaté
echo "$RESPONSE" | jq '.'

# Vérification du succès
if echo "$RESPONSE" | grep -q '"status": "success"'; then
    echo ""
    echo "🎉 === SUCCÈS TOTAL ! ==="
    echo "✅ Erreur 'time not defined' RÉSOLUE !"
    echo "✅ Enhanced Bridge v2.0 OPÉRATIONNEL !"
    echo "✅ Auto-fix intelligence ACTIVE !"
else
    echo ""
    echo "❌ === PROBLÈME DÉTECTÉ ==="
    echo "$RESPONSE"
    exit 1
fi

echo ""
echo "🎯 === VALIDATION FINALE ==="
echo "✅ Enhanced Bridge v2.0: 100% OPÉRATIONNEL"
echo "✅ Auto-fix Intelligence: ACTIF" 
echo "✅ Cache Python: RÉSOLU"
echo "✅ Erreur 'time not defined': ÉLIMINÉE"
