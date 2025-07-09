#!/usr/bin/env python3
"""
🎯 Nextvision Results Analyzer - Visualiseur de résultats de matching
Analyse et affiche les résultats détaillés des tests Nextvision V3.0

Author: Assistant  
Version: 1.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import glob

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def find_latest_report() -> Path:
    """Trouve le rapport le plus récent"""
    reports = glob.glob("nextvision_real_data_test_report_*.json")
    if not reports:
        print(f"{Colors.RED}❌ Aucun rapport trouvé{Colors.END}")
        sys.exit(1)
    
    latest = max(reports, key=lambda x: Path(x).stat().st_mtime)
    return Path(latest)

def load_report(report_path: Path) -> Dict:
    """Charge le rapport JSON"""
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur lecture rapport: {e}{Colors.END}")
        sys.exit(1)

def display_summary(data: Dict):
    """Affiche le résumé général"""
    summary = data.get('test_summary', {})
    metrics = data.get('performance_metrics', {})
    
    print(f"{Colors.BOLD}{Colors.CYAN}📊 === RÉSUMÉ NEXTVISION V3.0 ==={Colors.END}")
    print(f"{Colors.BOLD}⏱️  Durée totale : {Colors.GREEN}{summary.get('total_duration', 0):.2f}s{Colors.END}")
    print(f"{Colors.BOLD}📁 Fichiers testés : {Colors.BLUE}{summary.get('files_tested', 0)}{Colors.END}")
    print(f"{Colors.BOLD}✅ Tests réussis : {Colors.GREEN}{summary.get('successful_tests', 0)}{Colors.END}")
    print(f"{Colors.BOLD}❌ Tests échoués : {Colors.RED}{summary.get('failed_tests', 0)}{Colors.END}")
    print(f"{Colors.BOLD}📊 Taux de réussite : {Colors.GREEN}{metrics.get('success_rate', 0):.1f}%{Colors.END}")
    print()

def display_file_discovery(data: Dict):
    """Affiche la découverte des fichiers"""
    discovery = data.get('file_discovery', {})
    
    print(f"{Colors.BOLD}{Colors.YELLOW}📁 === DÉCOUVERTE FICHIERS ==={Colors.END}")
    print(f"📄 CVs trouvés : {Colors.GREEN}{len(discovery.get('cv_files', []))}{Colors.END}")
    print(f"📋 FDPs trouvées : {Colors.GREEN}{len(discovery.get('fdp_files', []))}{Colors.END}")
    print(f"📂 Total fichiers : {Colors.BLUE}{discovery.get('total_files', 0)}{Colors.END}")
    print()

def display_cv_results(data: Dict):
    """Affiche les résultats de parsing CV"""
    cv_tests = data.get('test_results', {}).get('cv_tests', [])
    
    print(f"{Colors.BOLD}{Colors.BLUE}🤖 === RÉSULTATS PARSING CV ==={Colors.END}")
    
    successful_cvs = [t for t in cv_tests if t.get('parsing_result', {}).get('success', False)]
    failed_cvs = [t for t in cv_tests if not t.get('parsing_result', {}).get('success', False)]
    
    print(f"✅ CVs parsés avec succès : {Colors.GREEN}{len(successful_cvs)}{Colors.END}")
    print(f"❌ Échecs parsing CV : {Colors.RED}{len(failed_cvs)}{Colors.END}")
    print()
    
    if successful_cvs:
        print(f"{Colors.BOLD}📋 Top 5 CVs analysés :{Colors.END}")
        for i, cv in enumerate(successful_cvs[:5]):
            name = cv.get('file_name', 'Unknown')
            size = cv.get('file_size', 0) / 1024  # KB
            time_ms = cv.get('parsing_result', {}).get('processing_time', 0) * 1000
            print(f"  {i+1}. {name}")
            print(f"     📏 Taille: {size:.1f} KB | ⏱️ Temps: {time_ms:.1f}ms")
            
            # Détails du parsing si disponibles
            details = cv.get('parsing_result', {}).get('details', {})
            parsing_result = details.get('parsing_result', {})
            if parsing_result:
                competences = parsing_result.get('competences', [])
                exp = parsing_result.get('experience', {}).get('annees_experience', 0)
                print(f"     💼 Expérience: {exp} ans | 🔧 Compétences: {len(competences)}")
        print()

def display_fdp_results(data: Dict):
    """Affiche les résultats de parsing FDP"""
    fdp_tests = data.get('test_results', {}).get('fdp_tests', [])
    
    print(f"{Colors.BOLD}{Colors.MAGENTA}🧠 === RÉSULTATS PARSING FDP ==={Colors.END}")
    
    successful_fdps = [t for t in fdp_tests if t.get('parsing_result', {}).get('success', False)]
    failed_fdps = [t for t in fdp_tests if not t.get('parsing_result', {}).get('success', False)]
    
    print(f"✅ FDPs parsées avec succès : {Colors.GREEN}{len(successful_fdps)}{Colors.END}")
    print(f"❌ Échecs parsing FDP : {Colors.RED}{len(failed_fdps)}{Colors.END}")
    print()
    
    if successful_fdps:
        print(f"{Colors.BOLD}📋 Top 5 FDPs analysées :{Colors.END}")
        for i, fdp in enumerate(successful_fdps[:5]):
            name = fdp.get('file_name', 'Unknown')
            size = fdp.get('file_size', 0) / 1024  # KB
            time_ms = fdp.get('parsing_result', {}).get('processing_time', 0) * 1000
            print(f"  {i+1}. {name}")
            print(f"     📏 Taille: {size:.1f} KB | ⏱️ Temps: {time_ms:.1f}ms")
            
            # Détails du parsing si disponibles
            details = fdp.get('parsing_result', {}).get('details', {})
            parsing_result = details.get('parsing_result', {})
            if parsing_result:
                titre = parsing_result.get('titre_poste', 'N/A')
                salaire = parsing_result.get('salaire', {})
                print(f"     💼 Poste: {titre}")
                if salaire:
                    print(f"     💰 Salaire: {salaire.get('min', 0)}-{salaire.get('max', 0)} EUR")
        print()

def display_matching_results(data: Dict):
    """Affiche les résultats de matching avec recommandations"""
    matching_tests = data.get('test_results', {}).get('matching_tests', [])
    
    print(f"{Colors.BOLD}{Colors.CYAN}🎯 === RÉSULTATS MATCHING ==={Colors.END}")
    
    successful_matches = [t for t in matching_tests if t.get('success', False)]
    
    print(f"✅ Matchings réussis : {Colors.GREEN}{len(successful_matches)}{Colors.END}")
    print()
    
    if successful_matches:
        print(f"{Colors.BOLD}🏆 TOP MATCHINGS RECOMMANDÉS :{Colors.END}")
        
        # Trier par score (si disponible dans les détails)
        scored_matches = []
        for match in successful_matches:
            details = match.get('details', {})
            score = details.get('matching_results', {}).get('total_score', 0)
            scored_matches.append((match, score))
        
        scored_matches.sort(key=lambda x: x[1], reverse=True)
        
        for i, (match, score) in enumerate(scored_matches[:10]):
            message = match.get('message', 'N/A')
            time_ms = match.get('processing_time', 0) * 1000
            
            print(f"{Colors.BOLD}#{i+1} - Score: {Colors.GREEN}{score:.2f}{Colors.END}")
            print(f"     🔗 {message}")
            print(f"     ⏱️ Temps: {time_ms:.1f}ms")
            
            # Détails du matching
            details = match.get('details', {})
            matching_results = details.get('matching_results', {})
            if matching_results:
                confidence = matching_results.get('confidence', 0)
                print(f"     📊 Confiance: {confidence:.2f}")
                
                # Scores par composant
                component_scores = matching_results.get('component_scores', {})
                if component_scores:
                    print(f"     📈 Détail scores:")
                    for component, comp_score in component_scores.items():
                        print(f"        • {component}: {comp_score:.2f}")
            print()

def display_transport_results(data: Dict):
    """Affiche les résultats de transport intelligence"""
    transport_tests = data.get('test_results', {}).get('transport_tests', [])
    
    print(f"{Colors.BOLD}{Colors.GREEN}🚗 === TRANSPORT INTELLIGENCE ==={Colors.END}")
    
    successful_transport = [t for t in transport_tests if t.get('success', False)]
    
    print(f"✅ Tests transport réussis : {Colors.GREEN}{len(successful_transport)}{Colors.END}")
    print()
    
    if successful_transport:
        print(f"{Colors.BOLD}🚦 RÉSULTATS COMPATIBILITÉ TRANSPORT :{Colors.END}")
        
        for i, test in enumerate(successful_transport):
            message = test.get('message', 'N/A')
            time_ms = test.get('processing_time', 0) * 1000
            
            print(f"{Colors.BOLD}Test {i+1}: {message}{Colors.END}")
            print(f"⏱️ Temps: {time_ms:.1f}ms")
            
            # Détails du transport
            details = test.get('details', {})
            compatibility_result = details.get('compatibility_result', {})
            if compatibility_result:
                is_compatible = compatibility_result.get('is_compatible', False)
                compat_score = compatibility_result.get('compatibility_score', 0)
                recommended_mode = compatibility_result.get('recommended_mode', 'N/A')
                
                status_color = Colors.GREEN if is_compatible else Colors.RED
                print(f"🚦 Compatible: {status_color}{is_compatible}{Colors.END}")
                print(f"📊 Score: {compat_score:.2f}")
                print(f"🚗 Mode recommandé: {recommended_mode}")
                
                # Détails par mode de transport
                transport_details = compatibility_result.get('transport_details', {})
                if transport_details:
                    print(f"📋 Détails par mode:")
                    for mode, mode_details in transport_details.items():
                        time_min = mode_details.get('time_minutes', 0)
                        cost = mode_details.get('cost_per_day', 0)
                        compatible = mode_details.get('is_compatible', False)
                        status = "✅" if compatible else "❌"
                        print(f"   {status} {mode}: {time_min}min, {cost:.2f}€/jour")
            print()

def display_api_health(data: Dict):
    """Affiche l'état des APIs"""
    api_health = data.get('api_health', {})
    
    print(f"{Colors.BOLD}{Colors.YELLOW}❤️ === ÉTAT DES APIS ==={Colors.END}")
    
    for service, status in api_health.items():
        status_color = Colors.GREEN if status else Colors.RED
        status_text = "✅ OK" if status else "❌ NON DISPONIBLE"
        print(f"  • {service}: {status_color}{status_text}{Colors.END}")
    print()

def main():
    """Point d'entrée principal"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}🎯 NEXTVISION RESULTS ANALYZER v1.0{Colors.END}")
    print(f"{Colors.BLUE}Analyse des résultats de test Nextvision V3.0{Colors.END}")
    print()
    
    # Trouver le rapport le plus récent
    report_path = find_latest_report()
    print(f"📄 Analyse du rapport: {Colors.GREEN}{report_path}{Colors.END}")
    print()
    
    # Charger les données
    data = load_report(report_path)
    
    # Affichage des résultats
    display_summary(data)
    display_file_discovery(data)
    display_api_health(data)
    display_cv_results(data)
    display_fdp_results(data)
    display_matching_results(data)
    display_transport_results(data)
    
    print(f"{Colors.BOLD}{Colors.CYAN}🎉 === ANALYSE TERMINÉE ==={Colors.END}")
    print(f"📄 Rapport complet disponible dans: {report_path}")
    print(f"🔍 Logs détaillés dans: nextvision_test.log")

if __name__ == "__main__":
    main()
