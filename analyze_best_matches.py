#!/usr/bin/env python3
"""
🏆 ANALYSE DES MEILLEURS MATCHINGS CV/FDP
Extraction et analyse des meilleurs matchings candidat/fiche de poste

Author: Assistant Claude
Version: 1.0.0-best-matches
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

def load_latest_results() -> List[Dict]:
    """📁 Charger les derniers résultats de matching"""
    
    # Chercher le fichier de résultats le plus récent
    current_dir = Path(".")
    result_files = list(current_dir.glob("semantic_matching_results_*.json"))
    
    if not result_files:
        print("❌ Aucun fichier de résultats trouvé")
        return []
    
    # Prendre le plus récent
    latest_file = max(result_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 Chargement: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        print(f"✅ {len(results)} résultats chargés")
        return results
    except Exception as e:
        print(f"❌ Erreur chargement: {e}")
        return []

def analyze_best_matches(results: List[Dict], top_n: int = 10) -> None:
    """🏆 Analyser et afficher les meilleurs matchings"""
    
    # Filtrer les résultats réussis
    successful_results = [r for r in results if "error" not in r and "semantic_score" in r]
    
    if not successful_results:
        print("❌ Aucun résultat valide trouvé")
        return
    
    # Trier par score décroissant
    sorted_results = sorted(successful_results, key=lambda x: x["semantic_score"], reverse=True)
    
    print(f"\n🏆 === TOP {top_n} MEILLEURS MATCHINGS ===")
    print("="*80)
    
    for i, result in enumerate(sorted_results[:top_n], 1):
        score = result["semantic_score"]
        correspondances = result.get("correspondances", [])
        candidat = result["candidat_name"]
        poste = result["poste_titre"]
        fdp_file = result["fdp_filename"]
        
        # Déterminer la qualité du match
        if score >= 0.8:
            quality = "🎉 EXCELLENT"
            color = "🟢"
        elif score >= 0.6:
            quality = "✅ TRÈS BON"
            color = "🟡"
        elif score >= 0.4:
            quality = "⚠️ MOYEN"
            color = "🟠"
        else:
            quality = "❌ FAIBLE"
            color = "🔴"
        
        print(f"\n{color} {i}. {quality} MATCH")
        print(f"👤 Candidat : {candidat}")
        print(f"📋 Poste    : {poste}")
        print(f"📄 FDP      : {fdp_file[:60]}...")
        print(f"🎯 Score    : {score:.3f}")
        print(f"✅ Correspondances ({len(correspondances)}) : {', '.join(correspondances) if correspondances else 'Aucune détectée'}")
        print("-" * 80)

def analyze_by_candidate(results: List[Dict]) -> None:
    """👤 Analyser les meilleurs matchings par candidat"""
    
    successful_results = [r for r in results if "error" not in r and "semantic_score" in r]
    
    # Regrouper par candidat
    candidates = {}
    for result in successful_results:
        candidat = result["candidat_name"]
        if candidat not in candidates:
            candidates[candidat] = []
        candidates[candidat].append(result)
    
    print(f"\n👤 === ANALYSE PAR CANDIDAT ===")
    print("="*80)
    
    # Trier les candidats par leur meilleur score
    sorted_candidates = sorted(candidates.items(), 
                             key=lambda x: max(r["semantic_score"] for r in x[1]), 
                             reverse=True)
    
    for candidat, matchings in sorted_candidates[:5]:  # Top 5 candidats
        best_score = max(r["semantic_score"] for r in matchings)
        avg_score = sum(r["semantic_score"] for r in matchings) / len(matchings)
        best_match = max(matchings, key=lambda x: x["semantic_score"])
        
        print(f"\n🌟 {candidat}")
        print(f"   📊 Meilleur score: {best_score:.3f}")
        print(f"   📈 Score moyen: {avg_score:.3f}")
        print(f"   🎯 Meilleur poste: {best_match['poste_titre']}")
        print(f"   ✅ Correspondances: {len(best_match.get('correspondances', []))}")
        
        # Top 3 matchings pour ce candidat
        top_matchings = sorted(matchings, key=lambda x: x["semantic_score"], reverse=True)[:3]
        for j, match in enumerate(top_matchings, 1):
            print(f"      {j}. {match['poste_titre'][:40]}... → {match['semantic_score']:.3f}")

def analyze_by_position(results: List[Dict]) -> None:
    """📋 Analyser les meilleurs candidats par poste"""
    
    successful_results = [r for r in results if "error" not in r and "semantic_score" in r]
    
    # Regrouper par poste
    positions = {}
    for result in successful_results:
        poste = result["poste_titre"]
        if poste not in positions:
            positions[poste] = []
        positions[poste].append(result)
    
    print(f"\n📋 === ANALYSE PAR POSTE ===")
    print("="*80)
    
    for poste, matchings in positions.items():
        best_score = max(r["semantic_score"] for r in matchings)
        avg_score = sum(r["semantic_score"] for r in matchings) / len(matchings)
        
        print(f"\n💼 {poste}")
        print(f"   📊 Meilleur score: {best_score:.3f}")
        print(f"   📈 Score moyen: {avg_score:.3f}")
        print(f"   👥 Candidats testés: {len(matchings)}")
        
        # Top 3 candidats pour ce poste
        top_candidates = sorted(matchings, key=lambda x: x["semantic_score"], reverse=True)[:3]
        for j, match in enumerate(top_candidates, 1):
            correspondances = len(match.get('correspondances', []))
            print(f"      {j}. {match['candidat_name']} → {match['semantic_score']:.3f} ({correspondances} correspondances)")

def generate_recruitment_recommendations(results: List[Dict]) -> None:
    """💡 Générer des recommandations de recrutement"""
    
    successful_results = [r for r in results if "error" not in r and "semantic_score" in r]
    
    print(f"\n💡 === RECOMMANDATIONS DE RECRUTEMENT ===")
    print("="*80)
    
    # Identifier les matchings excellents (≥0.6)
    excellent_matches = [r for r in successful_results if r["semantic_score"] >= 0.6]
    
    if excellent_matches:
        print(f"\n🎯 ACTIONS PRIORITAIRES ({len(excellent_matches)} matchings excellents):")
        
        for match in sorted(excellent_matches, key=lambda x: x["semantic_score"], reverse=True):
            score = match["semantic_score"]
            candidat = match["candidat_name"]
            poste = match["poste_titre"]
            correspondances = len(match.get('correspondances', []))
            
            if score >= 0.65:
                urgence = "🔥 URGENT"
            else:
                urgence = "⚡ PRIORITAIRE"
            
            print(f"   {urgence} - Contacter {candidat}")
            print(f"     📋 Poste: {poste}")
            print(f"     🎯 Score: {score:.3f} ({correspondances} compétences communes)")
            print()
    
    # Identifier les candidats polyvalents
    candidates_versatility = {}
    for result in successful_results:
        candidat = result["candidat_name"]
        if candidat not in candidates_versatility:
            candidates_versatility[candidat] = []
        if result["semantic_score"] >= 0.5:  # Bon score
            candidates_versatility[candidat].append(result)
    
    versatile_candidates = {k: v for k, v in candidates_versatility.items() if len(v) >= 3}
    
    if versatile_candidates:
        print(f"\n🔄 CANDIDATS POLYVALENTS (matchent sur plusieurs postes):")
        for candidat, matches in sorted(versatile_candidates.items(), 
                                      key=lambda x: len(x[1]), reverse=True):
            avg_score = sum(m["semantic_score"] for m in matches) / len(matches)
            print(f"   🌟 {candidat} - {len(matches)} postes compatibles (score moyen: {avg_score:.3f})")

def main():
    """🚀 Point d'entrée principal"""
    
    print("🏆 === ANALYSE DES MEILLEURS MATCHINGS CV/FDP ===")
    print("📊 Extraction des résultats de matching sémantique")
    print("="*70)
    
    # Charger les résultats
    results = load_latest_results()
    
    if not results:
        print("\n❌ Aucun résultat à analyser")
        print("💡 Lancez d'abord: python3 test_semantic_matching_real_files.py")
        return
    
    # Analyses
    analyze_best_matches(results, top_n=10)
    analyze_by_candidate(results)
    analyze_by_position(results)
    generate_recruitment_recommendations(results)
    
    print(f"\n✅ Analyse terminée !")
    print(f"📁 Basée sur {len(results)} matchings candidat/poste")

if __name__ == "__main__":
    main()
