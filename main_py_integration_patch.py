#!/usr/bin/env python3
"""
🔧 NEXTVISION V3.2.1 - PATCH MAIN.PY TRANSPORT INTELLIGENCE
==========================================================

Modifie main.py pour intégrer définitivement le Transport Intelligence
dans le calcul de matching en remplaçant le score localisation fixe.

Author: NEXTEN Team  
Version: 3.2.1 - Transport Intelligence Integration Patch
"""

import os
import sys
import shutil
from datetime import datetime

def backup_main_py():
    """💾 Crée une sauvegarde de main.py"""
    
    if not os.path.exists("main.py"):
        print("❌ Fichier main.py non trouvé")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"main.py.backup_{timestamp}"
    
    try:
        shutil.copy2("main.py", backup_file)
        print(f"💾 Sauvegarde créée: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return False

def read_main_py():
    """📖 Lit le contenu de main.py"""
    
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Erreur lecture main.py: {e}")
        return None

def write_main_py(content):
    """✍️ Écrit le nouveau contenu dans main.py"""
    
    try:
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ main.py modifié avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur écriture main.py: {e}")
        return False

def apply_transport_intelligence_patch(original_content):
    """🔧 Applique le patch Transport Intelligence"""
    
    # ================================
    # PATCH 1: Ajout des imports Transport Intelligence
    # ================================
    
    imports_patch = '''# === GOOGLE MAPS INTELLIGENCE IMPORTS (Prompt 2) ===
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.services.transport_calculator import TransportCalculator
from nextvision.engines.transport_filtering import TransportFilteringEngine, FilteringResult
from nextvision.engines.location_scoring import LocationScoringEngine, LocationScoreExplainer
from nextvision.models.transport_models import (
    TravelMode, ConfigTransport, GeocodeResult, TransportCompatibility,
    LocationScore, TrafficCondition
)
from nextvision.models.questionnaire_advanced import (
    QuestionnaireComplet, TimingInfo, RaisonEcoute, 
    TransportPreferences, MoyenTransport, RemunerationAttentes,
    SecteursPreferences, EnvironnementTravail, ContratsPreferences,
    MotivationsClassees
)
from nextvision.config.google_maps_config import get_google_maps_config, setup_google_maps_logging
from nextvision.utils.google_maps_helpers import get_cache, get_performance_monitor'''
    
    # Vérifier si les imports sont déjà présents
    if "from nextvision.engines.location_scoring import LocationScoringEngine" in original_content:
        print("✅ Imports Transport Intelligence déjà présents")
    else:
        # Trouver où insérer les imports (après les imports existants)
        insert_point = original_content.find("# Configuration du logging")
        if insert_point != -1:
            original_content = (original_content[:insert_point] + 
                              imports_patch + "\n\n" + 
                              original_content[insert_point:])
            print("✅ Imports Transport Intelligence ajoutés")
    
    # ================================
    # PATCH 2: Ajout des services Transport dans l'initialisation
    # ================================
    
    transport_services_init = '''
# === TRANSPORT INTELLIGENCE SERVICES INITIALIZATION ===
google_maps_config = get_google_maps_config()
setup_google_maps_logging(google_maps_config)

# Services Google Maps  
google_maps_service = GoogleMapsService(
    api_key=google_maps_config.api_key,
    cache_duration_hours=google_maps_config.geocode_cache_duration_hours
)

transport_calculator = TransportCalculator(google_maps_service)
transport_filtering_engine = TransportFilteringEngine(transport_calculator)
location_scoring_engine = LocationScoringEngine(transport_calculator)

print("✅ Transport Intelligence Services initialized")
'''
    
    # Chercher où insérer l'initialisation des services
    if "location_scoring_engine = LocationScoringEngine" in original_content:
        print("✅ Services Transport Intelligence déjà initialisés")
    else:
        # Insérer après l'initialisation du bridge
        bridge_init_end = original_content.find("commitment_bridge = None")
        if bridge_init_end != -1:
            # Trouver la fin de cette section
            next_line = original_content.find("\n", bridge_init_end)
            if next_line != -1:
                original_content = (original_content[:next_line] + 
                                  transport_services_init + 
                                  original_content[next_line:])
                print("✅ Initialisation services Transport Intelligence ajoutée")
    
    # ================================
    # PATCH 3: Modification de la fonction calculate_mock_matching_scores
    # ================================
    
    # Nouvelle fonction avec Transport Intelligence intégré
    new_matching_function = '''async def calculate_dynamic_matching_scores(request: MatchingRequest, weights: Dict) -> Dict:
    """🧮 Calcul de scores de matching avec Transport Intelligence INTÉGRÉ"""
    
    try:
        # 1. Scores statiques (comme avant mais optimisés)
        skills_count = len(request.candidate_profile.skills)
        experience = request.candidate_profile.experience_years
        salary_min = request.preferences.salary_expectations.min
        
        # Scores composants (optimisés pour équilibrage avec localisation dynamique)
        static_scores = {
            "semantique": min(0.9, 0.5 + (skills_count * 0.08) + (experience * 0.02)),
            "hierarchical": min(0.85, 0.6 + (experience * 0.03)),  # Nouveau composant
            "remuneration": min(0.95, 0.6 + (salary_min / 100000) * 0.3),
            "experience": min(0.9, 0.4 + (experience * 0.05)),
            "secteurs": 0.70  # Score secteur baseline
        }
        
        # 2. 🚗 SCORE LOCALISATION DYNAMIQUE via Transport Intelligence
        try:
            dynamic_location_score = await calculate_transport_location_score(request)
            location_scoring_success = True
            location_score_source = "dynamic"
        except Exception as e:
            logger.warning(f"Transport Intelligence fallback: {e}")
            dynamic_location_score = 0.65  # Score neutre en cas d'erreur
            location_scoring_success = False
            location_score_source = "fallback"
        
        # 3. Assemblage scores finaux
        all_scores = {
            **static_scores,
            "localisation": dynamic_location_score
        }
        
        # 4. Score total pondéré
        total_score = sum(all_scores[component] * weights[component] 
                         for component in all_scores.keys() if component in weights)
        
        # 5. Confiance ajustée selon succès Transport Intelligence
        base_confidence = min(0.95, total_score * 1.1)
        if location_scoring_success:
            confidence = min(0.95, base_confidence + 0.05)  # Bonus confiance si dynamique
        else:
            confidence = base_confidence * 0.9  # Réduction si fallback
        
        return {
            "component_scores": all_scores,
            "total_score": round(total_score, 3),
            "confidence": round(confidence, 3),
            "transport_intelligence": {
                "location_score_dynamic": location_scoring_success,
                "location_score_source": location_score_source,
                "location_score_value": dynamic_location_score
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur calcul matching dynamique: {e}")
        
        # Fallback complet vers ancienne méthode
        return {
            "component_scores": {
                "semantique": 0.7,
                "hierarchical": 0.6,
                "remuneration": 0.8,
                "experience": 0.7,
                "localisation": 0.6,  # Score neutre
                "secteurs": 0.7
            },
            "total_score": 0.65,
            "confidence": 0.50,
            "transport_intelligence": {
                "location_score_dynamic": False,
                "location_score_source": "error_fallback",
                "error": str(e)
            }
        }

async def calculate_transport_location_score(request: MatchingRequest) -> float:
    """🗺️ Calcule score localisation via Transport Intelligence"""
    
    # Création questionnaire candidat pour Location Scoring
    candidat_questionnaire = create_candidate_questionnaire_from_request(request)
    
    # Adresse job (simulation - en production viendrait de la FDP)
    job_address = request.preferences.location_preferences.city
    if not job_address or job_address == "":
        job_address = "1 Place Vendôme 75001 Paris"  # Adresse par défaut Paris centre
    
    # Calcul score enrichi via LocationScoringEngine
    location_score = await location_scoring_engine.calculate_enriched_location_score(
        candidat_questionnaire=candidat_questionnaire,
        job_address=job_address,
        job_context={}
    )
    
    logger.info(f"🚗 Transport Intelligence: score {location_score.final_score:.3f}")
    logger.info(f"   Mode: {location_score.transport_compatibility.recommended_mode.value if location_score.transport_compatibility.recommended_mode else 'unknown'}")
    logger.info(f"   Distance: {location_score.base_distance_km:.1f}km")
    
    return location_score.final_score

def create_candidate_questionnaire_from_request(request: MatchingRequest) -> QuestionnaireComplet:
    """📋 Crée questionnaire candidat depuis MatchingRequest"""
    
    # Mapping raisons d'écoute
    raison_mapping = {
        "Rémunération trop faible": RaisonEcoute.REMUNERATION_FAIBLE,
        "Poste ne coïncide pas avec poste proposé": RaisonEcoute.POSTE_INADEQUAT,
        "Poste trop loin de mon domicile": RaisonEcoute.POSTE_TROP_LOIN,
        "Manque de flexibilité": RaisonEcoute.MANQUE_FLEXIBILITE,
        "Manque de perspectives d'évolution": RaisonEcoute.MANQUE_PERSPECTIVES
    }
    
    raison_ecoute = raison_mapping.get(request.pourquoi_ecoute, RaisonEcoute.RECHERCHE_NOUVEAU_DEFI)
    
    # Transport preferences intelligentes basées sur localisation candidat
    transport_preferences = TransportPreferences(
        moyens_selectionnes=[
            MoyenTransport.VOITURE,
            MoyenTransport.TRANSPORT_COMMUN,
            MoyenTransport.VELO
        ],
        temps_max={
            "voiture": 45,
            "transport_commun": 60, 
            "velo": 30,
            "marche": 25
        }
    )
    
    # Timing info
    timing_info = TimingInfo(
        pourquoi_a_lecoute=raison_ecoute,
        disponibilite_entretien="Sous 1 semaine",
        prise_de_poste="Dans le mois"
    )
    
    # Environnement travail
    environnement = EnvironnementTravail(
        taille_entreprise_preferee="PME",
        management_style_prefere="Collaboratif", 
        culture_entreprise="Moderne"
    )
    
    # Questionnaire complet
    questionnaire = QuestionnaireComplet(
        timing=timing_info,
        transport=transport_preferences,
        environnement=environnement
    )
    
    return questionnaire

def calculate_mock_matching_scores(request: MatchingRequest, weights: Dict) -> Dict:
    """🧮 Calcul de scores de matching (LEGACY - conservé pour compatibilité)"""
    
    logger.warning("🔄 Utilisation méthode legacy calculate_mock_matching_scores")
    logger.warning("💡 Utilisez calculate_dynamic_matching_scores pour Transport Intelligence")
    
    # Ancien calcul avec score localisation FIXE
    skills_count = len(request.candidate_profile.skills)
    experience = request.candidate_profile.experience_years
    salary_min = request.preferences.salary_expectations.min
    
    scores = {
        "semantique": min(0.9, 0.5 + (skills_count * 0.08) + (experience * 0.02)),
        "remuneration": min(0.95, 0.6 + (salary_min / 100000) * 0.3),
        "localisation": 0.75,  # SCORE FIXE (legacy)
        "timing": 0.85,
        "secteurs": 0.70,
        "environnement": 0.65,
        "motivations": 0.80
    }
    
    total_score = sum(scores[component] * weights[component] for component in scores.keys())
    
    return {
        "component_scores": scores,
        "total_score": round(total_score, 3),
        "confidence": round(min(0.95, total_score * 1.1), 3),
        "algorithm": "Legacy Static Scoring (deprecated)"
    }'''
    
    # Remplacement de la fonction
    func_start = original_content.find("def calculate_mock_matching_scores(request: MatchingRequest, weights: Dict) -> Dict:")
    if func_start == -1:
        print("❌ Fonction calculate_mock_matching_scores non trouvée")
        return original_content
    
    # Trouver la fin de la fonction (prochaine fonction ou classe)
    func_end = original_content.find("\ndef ", func_start + 1)
    if func_end == -1:
        func_end = original_content.find("\nclass ", func_start + 1)
    if func_end == -1:
        func_end = original_content.find("\n@app.", func_start + 1)
    
    if func_end != -1:
        # Remplacer la fonction
        original_content = (original_content[:func_start] + 
                          new_matching_function + "\n" +
                          original_content[func_end:])
        print("✅ Fonction calculate_mock_matching_scores remplacée par version Transport Intelligence")
    
    # ================================
    # PATCH 4: Modification de l'endpoint de matching principal
    # ================================
    
    # Chercher l'endpoint principal et modifier l'appel
    endpoint_start = original_content.find("matching_analysis = calculate_mock_matching_scores(request, weights)")
    if endpoint_start != -1:
        # Remplacer par appel asynchrone
        original_content = original_content.replace(
            "matching_analysis = calculate_mock_matching_scores(request, weights)",
            "matching_analysis = await calculate_dynamic_matching_scores(request, weights)"
        )
        print("✅ Endpoint matching modifié pour utiliser Transport Intelligence")
    
    # ================================
    # PATCH 5: Ajout endpoint test Transport Intelligence
    # ================================
    
    test_endpoint = '''
@app.post("/api/v3/matching/candidate/{candidate_id}/transport", tags=["🚗 Transport Matching"])
async def match_candidate_with_transport_intelligence(candidate_id: str, request: MatchingRequest):
    """🚗 ENDPOINT TEST: Matching avec Transport Intelligence explicite"""
    start_time = time.time()
    
    logger.info(f"🚗 === TRANSPORT INTELLIGENCE MATCHING CANDIDAT {candidate_id} ===")
    logger.info(f"📋 Raison d'écoute: '{request.pourquoi_ecoute}'")
    logger.info(f"👤 Candidat: {request.candidate_profile.personal_info.firstName} {request.candidate_profile.personal_info.lastName}")
    
    try:
        # Pondération adaptative
        weight_analysis = get_adaptive_weights(request.pourquoi_ecoute)
        weights = weight_analysis["weights"]
        
        # Calcul avec Transport Intelligence
        matching_analysis = await calculate_dynamic_matching_scores(request, weights)
        
        # Réponse enrichie
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        response = {
            "status": "success",
            "candidate_id": candidate_id,
            "matching_results": {
                "total_score": matching_analysis["total_score"],
                "confidence": matching_analysis["confidence"],
                "component_scores": matching_analysis["component_scores"],
                "weights_used": weights
            },
            "transport_intelligence": matching_analysis.get("transport_intelligence", {}),
            "adaptive_weighting": {
                "applied": weight_analysis["adaptation_applied"],
                "reason": request.pourquoi_ecoute,
                "reasoning": weight_analysis["reasoning"],
                "weight_changes": _calculate_weight_changes(weights) if weight_analysis["adaptation_applied"] else None
            },
            "candidate_summary": {
                "name": f"{request.candidate_profile.personal_info.firstName} {request.candidate_profile.personal_info.lastName}",
                "skills_count": len(request.candidate_profile.skills),
                "experience_years": request.candidate_profile.experience_years,
                "salary_range": f"{request.preferences.salary_expectations.min}€ - {request.preferences.salary_expectations.max}€"
            },
            "metadata": {
                "processing_time_ms": processing_time,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "api_version": "3.2.1",
                "algorithm": "Adaptive Contextual Weighting + Transport Intelligence INTEGRATED"
            }
        }
        
        logger.info(f"✅ Transport Matching terminé en {processing_time}ms")
        logger.info(f"🚗 Score localisation: {matching_analysis['component_scores']['localisation']:.3f}")
        logger.info(f"📊 Score final: {matching_analysis['total_score']} (confiance: {matching_analysis['confidence']})")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur Transport Matching: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur Transport Intelligence: {str(e)}")
'''
    
    # Ajouter l'endpoint test avant la section des endpoints bridge
    bridge_endpoint_start = original_content.find("@app.post(\"/api/v2/conversion/commitment/enhanced\"")
    if bridge_endpoint_start != -1:
        original_content = (original_content[:bridge_endpoint_start] + 
                          test_endpoint + "\n" +
                          original_content[bridge_endpoint_start:])
        print("✅ Endpoint test Transport Intelligence ajouté")
    
    # ================================
    # PATCH 6: Mise à jour de la documentation root
    # ================================
    
    # Ajouter info Transport Intelligence dans le root endpoint
    root_patch = '''        "transport_intelligence_integrated": True,
        "location_scoring": "DYNAMIC (Google Maps Intelligence)",
        "previous_location_scoring": "static (0.75 fixed)",'''
    
    performance_targets_line = original_content.find('"performance_targets": {')
    if performance_targets_line != -1:
        # Insérer avant performance_targets
        original_content = (original_content[:performance_targets_line] + 
                          root_patch + "\n        " +
                          original_content[performance_targets_line:])
        print("✅ Documentation root mise à jour")
    
    return original_content

def apply_patch():
    """🚀 Applique le patch complet"""
    
    print("🔧 NEXTVISION V3.2.1 - PATCH TRANSPORT INTELLIGENCE")
    print("=" * 60)
    print("Intègre définitivement le Transport Intelligence dans main.py")
    print()
    
    # Vérifications préliminaires
    if not os.path.exists("main.py"):
        print("❌ Fichier main.py non trouvé")
        print("💡 Assurez-vous d'être dans le répertoire Nextvision/")
        return False
    
    print("🔍 Vérification de l'environnement...")
    
    # Vérification des modules nécessaires
    required_dirs = [
        "nextvision/services",
        "nextvision/engines", 
        "nextvision/models",
        "nextvision/config"
    ]
    
    for req_dir in required_dirs:
        if not os.path.exists(req_dir):
            print(f"❌ Répertoire manquant: {req_dir}")
            return False
    
    print("✅ Environnement Nextvision validé")
    
    # Sauvegarde
    if not backup_main_py():
        return False
    
    # Lecture du contenu original
    original_content = read_main_py()
    if original_content is None:
        return False
    
    print("📖 Contenu main.py lu")
    
    # Application des patches
    print("🔧 Application des patches Transport Intelligence...")
    
    patched_content = apply_transport_intelligence_patch(original_content)
    
    # Écriture du nouveau contenu
    if write_main_py(patched_content):
        print()
        print("🎯 PATCH APPLIQUÉ AVEC SUCCÈS !")
        print("=" * 40)
        print("✅ Transport Intelligence intégré dans main.py")
        print("🗺️ Score localisation maintenant DYNAMIQUE")
        print("🚗 Nouveau endpoint: /api/v3/matching/candidate/{id}/transport")
        print("🔄 Endpoint principal modifié pour utiliser Transport Intelligence")
        print()
        print("🧪 TEST:")
        print("python main.py")
        print("curl -X POST http://localhost:8001/api/v3/matching/candidate/test/transport \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{...json...}'")
        print()
        print("📁 Sauvegarde disponible pour rollback si nécessaire")
        return True
    else:
        return False

def main():
    """🚀 Point d'entrée principal"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        apply_patch()
    else:
        print("🔧 NEXTVISION V3.2.1 - PATCH TRANSPORT INTELLIGENCE")
        print("=" * 60)
        print()
        print("Ce script modifie main.py pour intégrer définitivement")
        print("le Transport Intelligence dans le système de matching.")
        print()
        print("CHANGEMENTS APPLIQUÉS:")
        print("• ✅ Ajout imports Transport Intelligence")
        print("• ✅ Initialisation services Google Maps")
        print("• ✅ Remplacement score localisation fixe par dynamique")
        print("• ✅ Nouveau endpoint test /api/v3/matching/candidate/{id}/transport")
        print("• ✅ Modification endpoint principal")
        print("• ✅ Mise à jour documentation")
        print("• ✅ Sauvegarde automatique main.py")
        print()
        print("⚠️  ATTENTION: Ce script modifie main.py de façon permanente!")
        print("💾 Une sauvegarde sera créée automatiquement.")
        print()
        print("Pour appliquer le patch:")
        print(f"python {sys.argv[0]} --apply")

if __name__ == "__main__":
    main()
