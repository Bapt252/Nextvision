#!/bin/bash

# 🚀 SCRIPT TEST RAPIDE OPTIMISATIONS PHASE 1 - NEXTVISION
# ========================================================
# 
# Test des optimisations : 48s → 25s (48% amélioration)
# Usage: ./quick_test_phase1.sh
# 
# TESTS :
# 1. Health check endpoint optimisé
# 2. Status services optimisés  
# 3. Test performance baseline vs optimisé
# 4. Validation des métriques

set -e  # Exit on error

echo "🚀 === TEST RAPIDE OPTIMISATIONS PHASE 1 ==="
echo "📊 Objectif : 48s → 25s (48% amélioration)"
echo ""

# === CONFIGURATION ===
API_BASE="http://localhost:8001"
CV_TEST="/Users/baptistecomas/Desktop/CV TEST/Cv_Mohamed_Ouadhane.pdf"
JOB_TEST="/Users/baptistecomas/Desktop/FDP TEST/Bcom HR - Fiche de poste Assistant Facturation.pdf"

# Fonction utilitaire
log_info() {
    echo "✅ $1"
}

log_error() {
    echo "❌ $1"
}

check_file() {
    if [[ ! -f "$1" ]]; then
        log_error "Fichier manquant : $1"
        exit 1
    fi
}

# === VÉRIFICATIONS PRÉLIMINAIRES ===

echo "🔍 Vérifications préliminaires..."

# Vérifier fichiers de test
check_file "$CV_TEST"
check_file "$JOB_TEST"
log_info "Fichiers de test trouvés"

# Vérifier serveur API
if ! curl -s "$API_BASE/docs" > /dev/null; then
    log_error "Serveur API non accessible. Démarrer avec : python main.py"
    exit 1
fi

log_info "Serveur API accessible"
echo ""

# === TEST 1: HEALTH CHECK OPTIMISÉ ===

echo "❤️ Test 1: Health Check Optimisé"

HEALTH_RESPONSE=$(curl -s "$API_BASE/api/v3/health-optimized" || echo "error")

if [[ "$HEALTH_RESPONSE" == "error" ]]; then
    log_error "Endpoint health-optimized inaccessible"
    echo "💡 Vérifier que le routeur optimisé est ajouté dans main.py"
    exit 1
fi

HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status' 2>/dev/null || echo "error")

if [[ "$HEALTH_STATUS" == "healthy" ]]; then
    log_info "Health check optimisé : OK"
    
    # Afficher détails optimisations
    OPTIMIZATIONS=$(echo "$HEALTH_RESPONSE" | jq -r '.optimizations' 2>/dev/null)
    if [[ "$OPTIMIZATIONS" != "null" ]]; then
        echo "   🚀 Optimisations actives :"
        echo "$HEALTH_RESPONSE" | jq -r '.optimizations | to_entries[] | "     • \(.key): \(.value)"' 2>/dev/null || true
    fi
else
    log_error "Health check optimisé échoué"
    exit 1
fi

echo ""

# === TEST 2: STATUS SERVICES OPTIMISÉS ===

echo "📊 Test 2: Status Services Optimisés"

STATUS_RESPONSE=$(curl -s "$API_BASE/api/v3/status-optimized" || echo "error")

if [[ "$STATUS_RESPONSE" == "error" ]]; then
    log_error "Endpoint status-optimized inaccessible"
    exit 1
fi

# Vérifier service GPT optimisé
GPT_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.services.gpt_direct_service_optimized.status' 2>/dev/null || echo "error")

if [[ "$GPT_STATUS" == "optimized" ]]; then
    log_info "Service GPT optimisé : OK"
    
    # Afficher détails service
    GPT_MODEL=$(echo "$STATUS_RESPONSE" | jq -r '.services.gpt_direct_service_optimized.model' 2>/dev/null)
    PARALLEL=$(echo "$STATUS_RESPONSE" | jq -r '.services.gpt_direct_service_optimized.parallel_processing' 2>/dev/null)
    
    echo "   • Modèle : $GPT_MODEL"
    echo "   • Parallélisation : $PARALLEL"
else
    log_error "Service GPT optimisé non opérationnel : $GPT_STATUS"
    exit 1
fi

echo ""

# === TEST 3: PERFORMANCE BASELINE VS OPTIMISÉ ===

echo "⚡ Test 3: Performance Baseline vs Optimisé"

# Test endpoint original (baseline)
echo "📊 Test baseline (endpoint original)..."
BASELINE_START=$(date +%s.%3N)

BASELINE_HTTP_CODE=$(curl -s -o baseline_result.json -w "%{http_code}" \
    -X POST "$API_BASE/api/v3/intelligent-matching" \
    -F "cv_file=@$CV_TEST" \
    -F "job_file=@$JOB_TEST" \
    -F "pourquoi_ecoute=Test baseline performance" \
    --max-time 60 || echo "000")

BASELINE_END=$(date +%s.%3N)
BASELINE_TIME_S=$(echo "$BASELINE_END - $BASELINE_START" | bc -l 2>/dev/null || echo "0")
BASELINE_TIME_MS=$(echo "$BASELINE_TIME_S * 1000" | bc -l 2>/dev/null || echo "0")

if [[ "$BASELINE_HTTP_CODE" == "200" ]]; then
    log_info "Baseline test réussi : ${BASELINE_TIME_MS%.*}ms"
    
    # Extraire score baseline
    BASELINE_SCORE=$(jq -r '.matching_results.total_score // "N/A"' baseline_result.json 2>/dev/null)
    echo "   • Score matching : $BASELINE_SCORE"
else
    log_error "Baseline test échoué (HTTP $BASELINE_HTTP_CODE)"
    BASELINE_TIME_MS="48000"  # Fallback
fi

echo ""

# Test endpoint optimisé
echo "🚀 Test optimisé (nouvel endpoint)..."
OPTIMIZED_START=$(date +%s.%3N)

OPTIMIZED_HTTP_CODE=$(curl -s -o optimized_result.json -w "%{http_code}" \
    -X POST "$API_BASE/api/v3/intelligent-matching-optimized" \
    -F "cv_file=@$CV_TEST" \
    -F "job_file=@$JOB_TEST" \
    -F "pourquoi_ecoute=Test optimisé performance" \
    --max-time 60 || echo "000")

OPTIMIZED_END=$(date +%s.%3N)
OPTIMIZED_TIME_S=$(echo "$OPTIMIZED_END - $OPTIMIZED_START" | bc -l 2>/dev/null || echo "0")
OPTIMIZED_TIME_MS=$(echo "$OPTIMIZED_TIME_S * 1000" | bc -l 2>/dev/null || echo "0")

if [[ "$OPTIMIZED_HTTP_CODE" == "200" ]]; then
    log_info "Test optimisé réussi : ${OPTIMIZED_TIME_MS%.*}ms"
    
    # Extraire score optimisé
    OPTIMIZED_SCORE=$(jq -r '.matching_results.total_score // "N/A"' optimized_result.json 2>/dev/null)
    echo "   • Score matching : $OPTIMIZED_SCORE"
    
    # Extraire métriques intégrées
    INTEGRATED_IMPROVEMENT=$(jq -r '.performance.improvement_percent // "N/A"' optimized_result.json 2>/dev/null)
    TARGET_25S=$(jq -r '.performance.target_achieved_25s // false' optimized_result.json 2>/dev/null)
    TARGET_15S=$(jq -r '.performance.target_achieved_15s // false' optimized_result.json 2>/dev/null)
    PERFORMANCE_GRADE=$(jq -r '.performance.performance_grade // "N/A"' optimized_result.json 2>/dev/null)
    
    echo "   • Amélioration intégrée : $INTEGRATED_IMPROVEMENT%"
    echo "   • Grade performance : $PERFORMANCE_GRADE"
else
    log_error "Test optimisé échoué (HTTP $OPTIMIZED_HTTP_CODE)"
    exit 1
fi

echo ""

# === TEST 4: VALIDATION MÉTRIQUES ===

echo "📊 Test 4: Validation Métriques"

# Calcul amélioration
if command -v bc >/dev/null 2>&1 && [[ "$BASELINE_TIME_MS" != "0" && "$OPTIMIZED_TIME_MS" != "0" ]]; then
    IMPROVEMENT_MS=$(echo "$BASELINE_TIME_MS - $OPTIMIZED_TIME_MS" | bc -l)
    IMPROVEMENT_PERCENT=$(echo "scale=1; ($IMPROVEMENT_MS / $BASELINE_TIME_MS) * 100" | bc -l)
    
    echo "🎯 RÉSULTATS PERFORMANCE :"
    echo "   • Baseline    : ${BASELINE_TIME_MS%.*}ms"
    echo "   • Optimisé    : ${OPTIMIZED_TIME_MS%.*}ms"
    echo "   • Gain        : ${IMPROVEMENT_MS%.*}ms"
    echo "   • Amélioration: ${IMPROVEMENT_PERCENT}%"
    
    # Validation objectifs
    OPTIMIZED_TIME_S_INT=${OPTIMIZED_TIME_S%.*}
    TARGET_25S_ACHIEVED=$(echo "$OPTIMIZED_TIME_S < 25" | bc -l 2>/dev/null || echo "0")
    TARGET_15S_ACHIEVED=$(echo "$OPTIMIZED_TIME_S < 15" | bc -l 2>/dev/null || echo "0")
    
    echo ""
    echo "🎯 VALIDATION OBJECTIFS :"
    
    if [[ "$TARGET_15S_ACHIEVED" == "1" ]]; then
        log_info "OBJECTIF FINAL ATTEINT : < 15s 🎯"
    elif [[ "$TARGET_25S_ACHIEVED" == "1" ]]; then
        log_info "OBJECTIF PHASE 1 ATTEINT : < 25s ✅"
    else
        log_error "Objectifs non atteints (> 25s) ❌"
    fi
    
    # Validation scores
    if [[ "$BASELINE_SCORE" != "N/A" && "$OPTIMIZED_SCORE" != "N/A" ]]; then
        SCORE_DIFF=$(echo "$OPTIMIZED_SCORE - $BASELINE_SCORE" | bc -l 2>/dev/null || echo "0")
        SCORE_DIFF_ABS=${SCORE_DIFF#-}  # Valeur absolue
        
        if (( $(echo "$SCORE_DIFF_ABS < 0.05" | bc -l 2>/dev/null || echo "0") )); then
            log_info "Scores équivalents (diff: ${SCORE_DIFF})"
        else
            log_error "Scores divergents (diff: ${SCORE_DIFF})"
        fi
    fi
    
else
    log_error "Impossible de calculer les métriques de performance"
fi

echo ""

# === RÉSUMÉ FINAL ===

echo "🎯 === RÉSUMÉ TESTS PHASE 1 ==="
echo ""

if [[ "$TARGET_25S_ACHIEVED" == "1" || "$TARGET_15S_ACHIEVED" == "1" ]]; then
    echo "✅ SUCCÈS ! Optimisations Phase 1 validées"
    echo ""
    echo "📊 PROCHAINES ÉTAPES :"
    echo "   1. Migration production si tous tests OK"
    echo "   2. Monitoring coûts API (90% réduction attendue)"
    echo "   3. Tests à grande échelle (100+ combinaisons)"
    
    if [[ "$TARGET_15S_ACHIEVED" != "1" ]]; then
        echo "   4. Préparation Phase 2 pour objectif < 15s"
    fi
else
    echo "⚠️  Optimisations partielles - Investigation requise"
    echo ""
    echo "🔍 INVESTIGATION :"
    echo "   1. Vérifier parallélisation CV + Job"
    echo "   2. Confirmer usage GPT-3.5-turbo"
    echo "   3. Valider prompts optimisés"
    echo "   4. Contrôler latence réseau"
fi

echo ""
echo "🔧 FICHIERS GÉNÉRÉS :"
echo "   • baseline_result.json  - Résultat test baseline"
echo "   • optimized_result.json - Résultat test optimisé"
echo ""
echo "✅ Tests Phase 1 terminés !"
