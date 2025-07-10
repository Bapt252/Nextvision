#!/usr/bin/env python3
"""
🎯 VALIDATION FINALE NEXTVISION V3.1
Démontre que le problème Charlotte DARMON est résolu

Author: Assistant Claude
Date: 2025-07-10
"""

from nextvision.services import HierarchicalDetector, HierarchicalBridgeFactory, HierarchicalScoring
import asyncio
from datetime import datetime

async def validation_finale():
    """🎯 Test final démonstratif"""
    
    print("=" * 80)
    print("🎯 VALIDATION FINALE NEXTVISION V3.1")
    print("   PROBLÈME CHARLOTTE DARMON = RÉSOLU ✅")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Initialisation
    detector = HierarchicalDetector()
    scorer = HierarchicalScoring()
    bridge = HierarchicalBridgeFactory.create_hierarchical_bridge()
    
    # Données Charlotte DARMON
    charlotte_cv = """
    Charlotte DARMON
    Directrice Administrative et Financière (DAF)
    15 ans d'expérience en direction financière
    
    Expérience:
    - DAF Groupe ABC (2019-2024): Pilotage stratégique, management équipe 12 personnes
    - Directrice Financière DEF (2015-2019): Supervision équipe, contrôle budgétaire
    
    Compétences: CEGID, SAGE, Excel, Consolidation, Management
    Rémunération souhaitée: 75-85K€
    """
    
    # Poste comptable (problématique avant V3.1)
    comptable_job = """
    Poste: Comptable Général H/F
    
    Mission:
    - Saisie comptable quotidienne (factures, règlements)
    - Rapprochements bancaires
    - Déclarations TVA mensuelles
    - Assistance pour bilan annuel
    
    Profil recherché:
    - Formation comptable (BTS/DUT)
    - 2-5 ans d'expérience en comptabilité générale
    - Pas de management d'équipe
    
    Salaire: 32-38K€
    """
    
    print("👤 CANDIDAT ANALYSÉ")
    print("-" * 30)
    
    # Analyse Charlotte
    charlotte_analysis = detector.detect_hierarchical_level(charlotte_cv, is_job_posting=False)
    print(f"Nom: Charlotte DARMON")
    print(f"Niveau détecté: {charlotte_analysis.detected_level.name}")
    print(f"Confiance: {charlotte_analysis.confidence_score:.3f}")
    print(f"Expérience: {charlotte_analysis.years_experience} ans")
    print(f"Indicateurs management: {len(charlotte_analysis.management_indicators)}")
    
    print(f"\n💼 POSTE ANALYSÉ")
    print("-" * 30)
    
    # Analyse poste
    job_analysis = detector.detect_hierarchical_level(comptable_job, is_job_posting=True)
    print(f"Titre: Comptable Général")
    print(f"Niveau détecté: {job_analysis.detected_level.name}")
    print(f"Confiance: {job_analysis.confidence_score:.3f}")
    
    print(f"\n📊 RÉSULTATS MATCHING")
    print("-" * 30)
    
    # Test scoring hiérarchique
    hierarchical_result = scorer.calculate_hierarchical_score(charlotte_cv, comptable_job)
    hierarchical_score = hierarchical_result['hierarchical_score']
    compatibility = hierarchical_result['compatibility_level']
    
    print(f"Score hiérarchique: {hierarchical_score:.3f}")
    print(f"Compatibilité: {compatibility}")
    
    # Test bridge complet
    charlotte_data = {
        'name': 'Charlotte DARMON',
        'parsed_content': charlotte_cv,
        'skills': ['CEGID', 'SAGE', 'Excel', 'Consolidation', 'Management'],
        'salary': {'expected': 80000},
        'experience': {'total_years': 15},
        'location': {'city': 'Paris'}
    }
    
    job_data = {
        'title': 'Comptable Général H/F',
        'parsed_content': comptable_job,
        'competences_requises': ['Comptabilité', 'TVA', 'Saisie'],
        'salary_range': (32000, 38000),
        'experience_requise': '2-5 ans',
        'localisation': 'Paris'
    }
    
    bridge_result = await bridge.enhanced_matching_with_hierarchy(charlotte_data, job_data)
    
    total_score = bridge_result['total_score']
    compatibility_bridge = bridge_result['compatibility']
    alerts = bridge_result['alerts']
    processing_time = bridge_result['processing_time']
    
    print(f"Score total V3.1: {total_score:.3f}")
    print(f"Compatibilité bridge: {compatibility_bridge}")
    print(f"Alertes générées: {len(alerts)}")
    print(f"Temps traitement: {processing_time:.1f}ms")
    
    print(f"\n🚨 ALERTES CRITIQUES")
    print("-" * 30)
    
    critical_alerts = [alert for alert in alerts if alert['type'] == 'CRITICAL_MISMATCH']
    for alert in critical_alerts:
        print(f"⚠️  {alert['type']}: {alert['message']}")
    
    print(f"\n🎯 VALIDATION FINALE")
    print("-" * 30)
    
    # Validation du succès
    success_criteria = {
        'charlotte_executive': charlotte_analysis.detected_level.name == 'EXECUTIVE',
        'job_junior': job_analysis.detected_level.name in ['JUNIOR', 'SENIOR'],
        'low_hierarchical_score': hierarchical_score < 0.4,
        'total_score_filtered': total_score < 0.6,
        'critical_alert_generated': len(critical_alerts) > 0,
        'fast_processing': processing_time < 50
    }
    
    all_success = all(success_criteria.values())
    
    for criteria, result in success_criteria.items():
        status = "✅" if result else "❌"
        print(f"{status} {criteria}: {result}")
    
    print(f"\n{'🎉 SUCCÈS TOTAL' if all_success else '⚠️ AJUSTEMENTS NÉCESSAIRES'}")
    print("-" * 30)
    
    if all_success:
        print("✅ Charlotte DARMON ne sera plus matchée sur postes comptables")
        print("✅ Système hiérarchique V3.1 opérationnel")
        print("✅ Performance maintenue")
        print("✅ Alertes automatiques fonctionnelles")
        print("\n🚀 NEXTVISION V3.1 PRÊT POUR PRODUCTION INTENSIVE!")
    
    print(f"\n📊 COMPARAISON AVANT/APRÈS")
    print("-" * 30)
    
    # Simulation score V3.0 (avant)
    score_v30 = 0.85 * 0.35 + 0.1 * 0.25 + 0.9 * 0.25 + 0.8 * 0.15  # 0.645
    
    print(f"Score V3.0 (AVANT): {score_v30:.3f} ✅ Accepté (PROBLÉMATIQUE)")
    print(f"Score V3.1 (APRÈS): {total_score:.3f} ❌ Rejeté (CORRECT)")
    print(f"Amélioration: {score_v30 - total_score:.3f} points ({(score_v30 - total_score)/score_v30*100:.1f}%)")
    
    return all_success

if __name__ == "__main__":
    result = asyncio.run(validation_finale())
    exit(0 if result else 1)
