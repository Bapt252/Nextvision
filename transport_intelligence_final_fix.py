#!/usr/bin/env python3
"""
🔧 PATCH FINAL - SCORE LOCALISATION DYNAMIQUE
==============================================

Corrige la fonction de calcul de matching pour utiliser vraiment
le Transport Intelligence au lieu du fallback 0.65.

Le problème: La conversion API → QuestionnaireComplet échoue,
causant un fallback vers score fixe.

Author: NEXTEN Team  
Version: 3.2.1 - Final Transport Intelligence Fix
"""

import os
import sys
from typing import Dict, Any, Optional

def add_nextvision_path():
    """Ajoute le répertoire Nextvision au PYTHONPATH"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    nextvision_dir = os.path.join(current_dir)
    if nextvision_dir not in sys.path:
        sys.path.insert(0, nextvision_dir)

add_nextvision_path()

def create_corrected_matching_function():
    """🔧 Génère la fonction de matching corrigée avec Transport Intelligence"""
    
    return '''
async def calculate_mock_matching_scores_with_transport_intelligence(
    request_data: Dict,
    candidate_id: str,
    job_location: Optional[str] = None
) -> Dict[str, Any]:
    """🎯 Calcul de matching avec Transport Intelligence OPÉRATIONNEL"""
    
    import time
    from datetime import datetime
    
    # Import des services Transport Intelligence
    try:
        from nextvision.services.google_maps_service import GoogleMapsService
        from nextvision.services.transport_calculator import TransportCalculator
        from nextvision.engines.location_scoring import LocationScoringEngine
        from nextvision.models.questionnaire_advanced import (
            QuestionnaireComplet, TransportPreferences, MoyenTransport,
            TimingInfo, RaisonEcoute, EnvironnementTravail, DisponibiliteType,
            SecteursPreferences, ContratsPreferences, MotivationsClassees, 
            RemunerationAttentes
        )
        from nextvision.config.google_maps_config import get_google_maps_config
        
        transport_intelligence_available = True
    except ImportError as e:
        logger.warning(f"Transport Intelligence non disponible: {e}")
        transport_intelligence_available = False
    
    start_time = time.time()
    
    # Extraction des données candidat
    candidate_profile = request_data.get("candidate_profile", {})
    preferences = request_data.get("preferences", {})
    pourquoi_ecoute = request_data.get("pourquoi_ecoute", "Manque de perspectives d'évolution")
    
    skills = candidate_profile.get("skills", [])
    experience_years = candidate_profile.get("experience_years", 0)
    
    # Extraction salary depuis preferences (structure API)
    salary_expectations = preferences.get("salary_expectations", {})
    salary_min = salary_expectations.get("min", 50000)
    
    # Extraction localisation candidat
    location_prefs = preferences.get("location_preferences", {})
    candidate_city = location_prefs.get("city", "Paris")
    candidate_location = f"{candidate_city}, France"
    
    # Job location depuis paramètre ou preferences
    if not job_location:
        job_location = f"1 Place Vendôme, 75001 Paris"  # Default pour demo
    
    # === CALCULS SCORES STATIQUES ===
    static_scores = {
        "semantique": min(0.9, 0.5 + (len(skills) * 0.08) + (experience_years * 0.02)),
        "hierarchical": min(0.85, 0.6 + (experience_years * 0.03)),
        "remuneration": min(0.95, 0.6 + (salary_min / 100000) * 0.3),
        "experience": min(0.9, 0.4 + (experience_years * 0.05)),
        "secteurs": 0.70
    }
    
    # === CALCUL SCORE LOCALISATION DYNAMIQUE ===
    location_score = 0.65  # Fallback par défaut
    transport_intelligence_data = {
        "location_score_dynamic": False,
        "location_score_source": "fallback",
        "location_score_value": 0.65
    }
    
    if transport_intelligence_available:
        try:
            # Initialisation Transport Intelligence
            google_maps_config = get_google_maps_config()
            google_maps_service = GoogleMapsService(
                api_key=google_maps_config.api_key,
                cache_duration_hours=google_maps_config.geocode_cache_duration_hours
            )
            transport_calculator = TransportCalculator(google_maps_service)
            location_scoring_engine = LocationScoringEngine(transport_calculator)
            
            # Création questionnaire candidat SIMPLIFIÉ
            candidat_questionnaire = create_simplified_questionnaire(
                candidate_location, pourquoi_ecoute, salary_min
            )
            
            # Calcul score enrichi via LocationScoringEngine
            location_score_result = await location_scoring_engine.calculate_enriched_location_score(
                candidat_questionnaire=candidat_questionnaire,
                job_address=job_location,
                job_context={}
            )
            
            # Extraction du score final
            location_score = location_score_result.final_score
            
            # Mise à jour métadonnées Transport Intelligence
            transport_intelligence_data = {
                "location_score_dynamic": True,
                "location_score_source": "google_maps_calculation",
                "location_score_value": location_score,
                "transport_mode": location_score_result.transport_compatibility.recommended_mode.value if location_score_result.transport_compatibility.recommended_mode else "unknown",
                "distance_km": location_score_result.base_distance_km,
                "time_score": location_score_result.time_score,
                "cost_score": location_score_result.cost_score,
                "comfort_score": location_score_result.comfort_score
            }
            
            logger.info(f"✅ Transport Intelligence: score {location_score:.3f} pour {job_location}")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur Transport Intelligence: {e}")
            # Garde le fallback défini plus haut
    
    # === ASSEMBLAGE SCORES FINAUX ===
    all_scores = {
        **static_scores,
        "localisation": location_score
    }
    
    # === PONDÉRATION ADAPTATIVE ===
    weights = apply_adaptive_weighting(pourquoi_ecoute)
    
    # === SCORE TOTAL ===
    total_score = sum(all_scores[component] * weights[component] 
                     for component in all_scores.keys() if component in weights)
    
    # === CONFIANCE ===
    base_confidence = 0.85
    if transport_intelligence_data["location_score_dynamic"]:
        base_confidence += 0.10  # Bonus pour calcul dynamique
    confidence = min(0.95, base_confidence)
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "status": "success",
        "candidate_id": candidate_id,
        "matching_results": {
            "total_score": round(total_score, 3),
            "confidence": round(confidence, 3),
            "component_scores": all_scores,
            "weights_used": weights
        },
        "transport_intelligence": transport_intelligence_data,
        "adaptive_weighting": get_adaptive_weighting_details(pourquoi_ecoute),
        "candidate_summary": {
            "name": f"{candidate_profile.get('personal_info', {}).get('firstName', 'Candidat')} {candidate_profile.get('personal_info', {}).get('lastName', 'Test')}",
            "skills_count": len(skills),
            "experience_years": experience_years,
            "salary_range": f"{salary_min}€ - {salary_expectations.get('max', salary_min + 15000)}€"
        },
        "metadata": {
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat() + "Z",
            "api_version": "3.2.1",
            "algorithm": "Adaptive Contextual Weighting + Transport Intelligence INTEGRATED"
        }
    }

def create_simplified_questionnaire(candidate_location: str, pourquoi_ecoute: str, salary_min: int):
    """📋 Crée questionnaire candidat simplifié pour Transport Intelligence"""
    
    from nextvision.models.questionnaire_advanced import (
        QuestionnaireComplet, TransportPreferences, MoyenTransport,
        TimingInfo, RaisonEcoute, EnvironnementTravail, DisponibiliteType,
        SecteursPreferences, ContratsPreferences, MotivationsClassees, 
        RemunerationAttentes
    )
    
    # Mapping raisons d'écoute
    raison_mapping = {
        "Rémunération trop faible": RaisonEcoute.REMUNERATION_FAIBLE,
        "Poste ne coïncide pas avec poste proposé": RaisonEcoute.POSTE_INADEQUAT,
        "Poste trop loin de mon domicile": RaisonEcoute.POSTE_TROP_LOIN,
        "Manque de flexibilité": RaisonEcoute.MANQUE_FLEXIBILITE,
        "Manque de perspectives d'évolution": RaisonEcoute.MANQUE_PERSPECTIVES
    }
    
    raison_ecoute = raison_mapping.get(pourquoi_ecoute, RaisonEcoute.MANQUE_PERSPECTIVES)
    
    # Questionnaire avec tous les champs requis
    questionnaire = QuestionnaireComplet(
        timing=TimingInfo(
            disponibilite=DisponibiliteType.DANS_1_MOIS,
            pourquoi_a_lecoute=raison_ecoute,
            preavis={"durée": "1 mois", "négociable": True}
        ),
        secteurs=SecteursPreferences(
            preferes=["Technologie"],
            redhibitoires=[]
        ),
        environnement_travail=EnvironnementTravail.HYBRIDE,
        transport=TransportPreferences(
            moyens_selectionnes=[MoyenTransport.VOITURE, MoyenTransport.TRANSPORT_COMMUN],
            temps_max={"voiture": 45, "transport_commun": 60}
        ),
        contrats=ContratsPreferences(ordre_preference=[]),
        motivations=MotivationsClassees(
            classees=["Évolution", "Salaire"],
            priorites=[1, 2]
        ),
        remuneration=RemunerationAttentes(
            min=salary_min,
            max=int(salary_min * 1.3),
            actuel=salary_min
        )
    )
    
    return questionnaire
'''

def apply_patch_to_main():
    """🔧 Applique le patch à main.py"""
    
    print("🔧 APPLICATION DU PATCH FINAL - TRANSPORT INTELLIGENCE")
    print("=" * 60)
    
    # Vérification environnement
    if not os.path.exists("main.py"):
        print("❌ Erreur: main.py non trouvé")
        print("💡 Exécutez depuis le répertoire Nextvision/")
        return False
    
    # Sauvegarde
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"main.py.backup_final_{timestamp}"
    shutil.copy("main.py", backup_file)
    print(f"💾 Sauvegarde créée: {backup_file}")
    
    # Lecture main.py
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remplacement de la fonction de matching
    new_function = create_corrected_matching_function()
    
    # Pattern de remplacement (plus flexible)
    import re
    
    # Cherche la fonction calculate_mock_matching_scores existante
    pattern = r'async def calculate_mock_matching_scores.*?(?=async def|\nclass |\n@app\.|\nif __name__|$)'
    
    if re.search(pattern, content, re.DOTALL):
        # Remplace la fonction existante
        content = re.sub(pattern, new_function.strip() + '\n\n', content, flags=re.DOTALL)
        print("✅ Fonction calculate_mock_matching_scores remplacée")
    else:
        # Ajoute la fonction avant la fin du fichier
        insertion_point = content.rfind('\nif __name__ == "__main__":')
        if insertion_point == -1:
            insertion_point = len(content)
        
        content = content[:insertion_point] + '\n' + new_function + '\n' + content[insertion_point:]
        print("✅ Fonction calculate_mock_matching_scores ajoutée")
    
    # Sauvegarde du fichier modifié
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ main.py modifié avec succès")
    print()
    print("🎯 CHANGEMENTS APPLIQUÉS:")
    print("• ✅ Transport Intelligence intégré dans le calcul de matching")
    print("• ✅ Score localisation dynamique remplace 0.65 fixe")
    print("• ✅ Gestion d'erreurs robuste avec fallback")
    print("• ✅ Questionnaire candidat simplifié pour éviter les erreurs")
    print()
    print("🚀 REDÉMARRAGE NÉCESSAIRE:")
    print("1. Arrêter l'API (Ctrl+C)")
    print("2. Relancer: python main.py")
    print("3. Tester avec les mêmes commandes curl")
    print()
    print("📊 RÉSULTAT ATTENDU:")
    print("• 🗺️ location_score_dynamic: true")
    print("• 📍 Scores localisation variables selon distance")
    print("• 🚗 Détails transport dans les réponses")
    
    return True

def main():
    """🚀 Point d'entrée principal"""
    
    print("🔧 PATCH FINAL - TRANSPORT INTELLIGENCE DYNAMIQUE")
    print("=" * 60)
    print("Corrige le calcul de matching pour utiliser vraiment")
    print("le Transport Intelligence au lieu du fallback 0.65")
    print()
    
    if apply_patch_to_main():
        print("\n🎉 PATCH APPLIQUÉ AVEC SUCCÈS !")
        print("Redémarrez l'API pour voir les scores dynamiques !")
    else:
        print("\n❌ Échec application du patch")

if __name__ == "__main__":
    main()
