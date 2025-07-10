#!/usr/bin/env python3
"""
🎯 Nextvision Results Parser - Extracteur de données spécialisé
Parse les résultats Nextvision depuis les chaînes sérialisées

Author: Assistant  
Version: 2.0 - String data parser
"""

import json
import sys
import re
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

def extract_from_string(text: str, pattern: str) -> str:
    """Extrait une valeur depuis une chaîne avec regex"""
    match = re.search(pattern, text)
    return match.group(1) if match else "N/A"

def extract_list_from_string(text: str, list_name: str) -> List[str]:
    """Extrait une liste depuis une chaîne"""
    pattern = f"'{list_name}':\s*\[(.*?)\]"
    match = re.search(pattern, text)
    if match:
        items_str = match.group(1)
        # Extraire les éléments entre quotes
        items = re.findall(r"'([^']*)'", items_str)
        return items
    return []

def extract_dict_from_string(text: str, dict_name: str) -> Dict:
    """Extrait un dictionnaire depuis une chaîne"""
    pattern = f"'{dict_name}':\s*\{{([^}}]*)\}}"
    match = re.search(pattern, text)
    if match:
        dict_content = match.group(1)
        result = {}
        # Extraire les paires clé-valeur
        pairs = re.findall(r"'([^']*)'\s*:\s*([^,}]+)", dict_content)
        for key, value in pairs:
            # Nettoyer la valeur
            value = value.strip().strip("'\"")
            try:
                # Essayer de convertir en nombre
                if '.' in value:
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except ValueError:
                result[key] = value
        return result
    return {}

def parse_cv_data(cv_str: str) -> Dict:
    """Parse les données d'un CV depuis la chaîne"""
    data = {
        'file_name': extract_from_string(cv_str, r"file_name='([^']*)'"),
        'file_size': extract_from_string(cv_str, r"file_size=(\d+)"),
        'file_type': extract_from_string(cv_str, r"file_type='([^']*)'"),
        'success': 'success=True' in cv_str,
        'processing_time': extract_from_string(cv_str, r"processing_time=([0-9.]+)"),
    }
    
    # Extraire les compétences
    data['competences'] = extract_list_from_string(cv_str, 'competences')
    
    # Extraire l'expérience
    exp_match = re.search(r"'annees_experience':\s*(\d+)", cv_str)
    data['experience_years'] = int(exp_match.group(1)) if exp_match else 0
    
    # Extraire formation
    data['formation_niveau'] = extract_from_string(cv_str, r"'niveau':\s*'([^']*)'")
    data['formation_domaine'] = extract_from_string(cv_str, r"'domaine':\s*'([^']*)'")
    
    # Extraire préférences salariales
    sal_min_match = re.search(r"'salary_min':\s*(\d+)", cv_str)
    sal_max_match = re.search(r"'salary_max':\s*(\d+)", cv_str)
    data['salary_min'] = int(sal_min_match.group(1)) if sal_min_match else 0
    data['salary_max'] = int(sal_max_match.group(1)) if sal_max_match else 0
    
    return data

def parse_fdp_data(fdp_str: str) -> Dict:
    """Parse les données d'une FDP depuis la chaîne"""
    data = {
        'file_name': extract_from_string(fdp_str, r"file_name='([^']*)'"),
        'file_size': extract_from_string(fdp_str, r"file_size=(\d+)"),
        'success': 'success=True' in fdp_str,
        'processing_time': extract_from_string(fdp_str, r"processing_time=([0-9.]+)"),
    }
    
    # Extraire les détails du poste
    data['titre_poste'] = extract_from_string(fdp_str, r"'titre_poste':\s*'([^']*)'")
    data['entreprise'] = extract_from_string(fdp_str, r"'entreprise':\s*'([^']*)'")
    data['localisation'] = extract_from_string(fdp_str, r"'localisation':\s*'([^']*)'")
    data['type_contrat'] = extract_from_string(fdp_str, r"'type_contrat':\s*'([^']*)'")
    
    # Extraire compétences requises
    data['competences_requises'] = extract_list_from_string(fdp_str, 'competences_requises')
    
    # Extraire salaire
    sal_min_match = re.search(r"'min':\s*(\d+)", fdp_str)
    sal_max_match = re.search(r"'max':\s*(\d+)", fdp_str)
    data['salaire_min'] = int(sal_min_match.group(1)) if sal_min_match else 0
    data['salaire_max'] = int(sal_max_match.group(1)) if sal_max_match else 0
    
    # Extraire avantages
    data['avantages'] = extract_list_from_string(fdp_str, 'avantages')
    
    return data

def parse_matching_data(match_str: str) -> Dict:
    """Parse les données de matching depuis la chaîne"""
    data = {
        'success': 'success=True' in match_str,
        'message': extract_from_string(match_str, r"message='([^']*)'"),
        'processing_time': extract_from_string(match_str, r"processing_time=([0-9.]+)"),
    }
    
    # Extraire les scores
    score_match = re.search(r"'total_score':\s*([0-9.]+)", match_str)
    data['total_score'] = float(score_match.group(1)) if score_match else 0
    
    conf_match = re.search(r"'confidence':\s*([0-9.]+)", match_str)
    data['confidence'] = float(conf_match.group(1)) if conf_match else 0
    
    # Extraire les scores par composant
    component_patterns = [
        ('semantique', r"'semantique':\s*([0-9.]+)"),
        ('remuneration', r"'remuneration':\s*([0-9.]+)"),
        ('localisation', r"'localisation':\s*([0-9.]+)"),
        ('timing', r"'timing':\s*([0-9.]+)"),
        ('secteurs', r"'secteurs':\s*([0-9.]+)"),
        ('environnement', r"'environnement':\s*([0-9.]+)"),
        ('motivations', r"'motivations':\s*([0-9.]+)")
    ]
    
    data['component_scores'] = {}
    for component, pattern in component_patterns:
        match = re.search(pattern, match_str)
        if match:
            data['component_scores'][component] = float(match.group(1))
    
    return data

def parse_transport_data(transport_str: str) -> Dict:
    """Parse les données de transport depuis la chaîne"""
    data = {
        'success': 'success=True' in transport_str,
        'message': extract_from_string(transport_str, r"message='([^']*)'"),
        'processing_time': extract_from_string(transport_str, r"processing_time=([0-9.]+)"),
    }
    
    # Extraire compatibilité
    compat_match = re.search(r"'is_compatible':\s*(True|False)", transport_str)
    data['is_compatible'] = compat_match.group(1) == 'True' if compat_match else False
    
    score_match = re.search(r"'compatibility_score':\s*([0-9.]+)", transport_str)
    data['compatibility_score'] = float(score_match.group(1)) if score_match else 0
    
    data['recommended_mode'] = extract_from_string(transport_str, r"'recommended_mode':\s*'([^']*)'")
    
    # Extraire détails transport
    data['transport_details'] = {}
    modes = ['voiture', 'transport_commun', 'velo', 'marche']
    for mode in modes:
        if f"'{mode}'" in transport_str:
            mode_data = {}
            # Pattern pour extraire les détails du mode
            mode_pattern = f"'{mode}':\s*\{{([^}}]*)\}}"
            mode_match = re.search(mode_pattern, transport_str)
            if mode_match:
                mode_content = mode_match.group(1)
                
                time_match = re.search(r"'time_minutes':\s*(\d+)", mode_content)
                mode_data['time_minutes'] = int(time_match.group(1)) if time_match else 0
                
                cost_match = re.search(r"'cost_per_day':\s*([0-9.]+)", mode_content)
                mode_data['cost_per_day'] = float(cost_match.group(1)) if cost_match else 0
                
                compat_match = re.search(r"'is_compatible':\s*(True|False)", mode_content)
                mode_data['is_compatible'] = compat_match.group(1) == 'True' if compat_match else False
                
                data['transport_details'][mode] = mode_data
    
    return data

def display_results(data: Dict):
    """Affiche les résultats parsés de manière lisible"""
    
    print(f"{Colors.BOLD}{Colors.CYAN}🎯 === NEXTVISION V3.0 - RÉSULTATS DÉTAILLÉS ==={Colors.END}")
    print()
    
    # Résumé général
    summary = data.get('test_summary', {})
    metrics = data.get('performance_metrics', {})
    
    print(f"{Colors.BOLD}📊 RÉSUMÉ GLOBAL :{Colors.END}")
    print(f"⏱️ Durée totale : {Colors.GREEN}{summary.get('total_duration', 0):.2f}s{Colors.END}")
    print(f"📁 Fichiers testés : {Colors.BLUE}{summary.get('files_tested', 0)}{Colors.END}")
    print(f"✅ Tests réussis : {Colors.GREEN}{summary.get('successful_tests', 0)}{Colors.END}")
    print(f"📊 Taux de réussite : {Colors.GREEN}{metrics.get('success_rate', 0):.1f}%{Colors.END}")
    print()
    
    # Parse et affiche les CVs
    cv_tests = data.get('test_results', {}).get('cv_tests', [])
    if cv_tests:
        print(f"{Colors.BOLD}{Colors.BLUE}🤖 === CVs ANALYSÉS (Top 5) ==={Colors.END}")
        for i, cv_str in enumerate(cv_tests[:5]):
            if isinstance(cv_str, str):
                cv_data = parse_cv_data(cv_str)
                if cv_data['success']:
                    print(f"{Colors.BOLD}#{i+1} - {cv_data['file_name']}{Colors.END}")
                    print(f"     📏 Taille: {int(cv_data['file_size'])/1024:.1f} KB")
                    print(f"     ⏱️ Temps: {float(cv_data['processing_time'])*1000:.1f}ms")
                    print(f"     💼 Expérience: {cv_data['experience_years']} ans")
                    print(f"     🎓 Formation: {cv_data['formation_niveau']} {cv_data['formation_domaine']}")
                    print(f"     💰 Attentes: {cv_data['salary_min']}-{cv_data['salary_max']} EUR")
                    print(f"     🔧 Compétences: {', '.join(cv_data['competences'][:3])}...")
                    print()
    
    # Parse et affiche les FDPs
    fdp_tests = data.get('test_results', {}).get('fdp_tests', [])
    if fdp_tests:
        print(f"{Colors.BOLD}{Colors.MAGENTA}🧠 === FDPs ANALYSÉES (Top 5) ==={Colors.END}")
        for i, fdp_str in enumerate(fdp_tests[:5]):
            if isinstance(fdp_str, str):
                fdp_data = parse_fdp_data(fdp_str)
                if fdp_data['success']:
                    print(f"{Colors.BOLD}#{i+1} - {fdp_data['file_name'][:50]}...{Colors.END}")
                    print(f"     💼 Poste: {fdp_data['titre_poste']}")
                    print(f"     🏢 Entreprise: {fdp_data['entreprise']} ({fdp_data['localisation']})")
                    print(f"     📋 Contrat: {fdp_data['type_contrat']}")
                    print(f"     💰 Salaire: {fdp_data['salaire_min']}-{fdp_data['salaire_max']} EUR")
                    print(f"     🔧 Requis: {', '.join(fdp_data['competences_requises'][:3])}...")
                    print(f"     🎁 Avantages: {', '.join(fdp_data['avantages'][:2])}...")
                    print()
    
    # Parse et affiche les matchings
    matching_tests = data.get('test_results', {}).get('matching_tests', [])
    if matching_tests:
        print(f"{Colors.BOLD}{Colors.CYAN}🎯 === TOP MATCHINGS RECOMMANDÉS ==={Colors.END}")
        for i, match_str in enumerate(matching_tests):
            if isinstance(match_str, str):
                match_data = parse_matching_data(match_str)
                if match_data['success']:
                    print(f"{Colors.BOLD}#{i+1} - Score: {Colors.GREEN}{match_data['total_score']:.3f} ({match_data['total_score']*100:.1f}%){Colors.END}")
                    print(f"     🔗 {match_data['message']}")
                    print(f"     📊 Confiance: {match_data['confidence']:.3f} ({match_data['confidence']*100:.1f}%)")
                    print(f"     ⏱️ Temps: {float(match_data['processing_time'])*1000:.1f}ms")
                    
                    if match_data['component_scores']:
                        print(f"     📈 Détail scores:")
                        for component, score in match_data['component_scores'].items():
                            print(f"        • {component}: {score:.2f} ({score*100:.0f}%)")
                    print()
    
    # Parse et affiche les transports
    transport_tests = data.get('test_results', {}).get('transport_tests', [])
    if transport_tests:
        print(f"{Colors.BOLD}{Colors.GREEN}🚗 === TRANSPORT INTELLIGENCE ==={Colors.END}")
        for i, transport_str in enumerate(transport_tests):
            if isinstance(transport_str, str):
                transport_data = parse_transport_data(transport_str)
                if transport_data['success']:
                    status_color = Colors.GREEN if transport_data['is_compatible'] else Colors.RED
                    print(f"{Colors.BOLD}#{i+1} - {transport_data['message']}{Colors.END}")
                    print(f"     🚦 Compatible: {status_color}{transport_data['is_compatible']}{Colors.END}")
                    print(f"     📊 Score: {transport_data['compatibility_score']:.2f}")
                    print(f"     🎯 Mode recommandé: {transport_data['recommended_mode']}")
                    
                    if transport_data['transport_details']:
                        print(f"     📋 Détails par mode:")
                        for mode, details in transport_data['transport_details'].items():
                            status = "✅" if details.get('is_compatible', False) else "❌"
                            print(f"        {status} {mode}: {details.get('time_minutes', 0)}min, {details.get('cost_per_day', 0):.2f}€/jour")
                    print()

def main():
    """Point d'entrée principal"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}🎯 NEXTVISION RESULTS PARSER v2.0{Colors.END}")
    print(f"{Colors.BLUE}Parser spécialisé pour données Nextvision V3.0{Colors.END}")
    print()
    
    # Trouver le rapport le plus récent
    report_path = find_latest_report()
    print(f"📄 Analyse du rapport: {Colors.GREEN}{report_path}{Colors.END}")
    print()
    
    # Charger les données
    data = load_report(report_path)
    
    # Afficher les résultats parsés
    display_results(data)
    
    print(f"{Colors.BOLD}{Colors.CYAN}🎉 === ANALYSE TERMINÉE ==={Colors.END}")
    print(f"📄 Rapport complet disponible dans: {report_path}")

if __name__ == "__main__":
    main()
