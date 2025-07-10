#!/usr/bin/env python3
"""
🧪 Test Transport Intelligence V3.0 avec VRAIES DONNÉES
Script pour tester CV TEST et FDP TEST depuis le bureau

PROMPT 5+ - Test données réelles utilisateur
Usage: python test_real_data_transport_intelligence.py

Author: NEXTEN Team
Version: 3.0.0 - Real Data Testing
"""

import asyncio
import os
import logging
import sys
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class RealDataTransportTester:
    """🧪 Testeur Transport Intelligence avec vraies données utilisateur"""
    
    def __init__(self):
        self.desktop_path = self._get_desktop_path()
        self.supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.json']
        
        # Configuration extraction données
        self.extraction_patterns = {
            "address": [
                r"(?:adresse|domicile|résidence|habite|situé|localisation)\s*:?\s*([^,\n]+(?:,\s*[^,\n]+)*)",
                r"(\d+(?:\s+\w+)*\s+(?:rue|avenue|boulevard|place|chemin|impasse)\s+[^,\n]+(?:,\s*\d{5}\s*[^,\n]+)?)",
                r"(\d{5}\s+[A-Za-zÀ-ÿ\s\-]+)"
            ],
            "transport_preferences": [
                r"(?:transport|déplacement|mobilité)\s*:?\s*([^.\n]+)",
                r"(?:véhicule|voiture|transport\s+public|vélo|marche|moto)\b",
                r"(?:permis|conducteur|transport\s+en\s+commun)"
            ],
            "flexibility": [
                r"(?:télétravail|remote|distance|flexible|hybride)\s*:?\s*([^.\n]+)",
                r"(?:déplacement|trajet)\s+(?:max|maximum)\s*:?\s*(\d+)\s*(?:min|km)"
            ]
        }
    
    def _get_desktop_path(self) -> Path:
        """📂 Détecte le chemin vers le bureau selon l'OS"""
        
        home = Path.home()
        
        # macOS/Linux
        desktop_candidates = [
            home / "Desktop",
            home / "Bureau",  # Français
            home / "Escritorio",  # Espagnol
            home / "Schreibtisch"  # Allemand
        ]
        
        for candidate in desktop_candidates:
            if candidate.exists():
                return candidate
        
        # Fallback
        return home
    
    async def run_real_data_tests(self):
        """🚀 Lance tests avec vraies données utilisateur"""
        
        print("🧪 TEST TRANSPORT INTELLIGENCE V3.0 - VRAIES DONNÉES")
        print("=" * 65)
        print(f"📂 Recherche fichiers sur: {self.desktop_path}")
        print()
        
        # 1. Recherche fichiers CV et FDP
        cv_files, fdp_files = self._find_test_files()
        
        if not cv_files and not fdp_files:
            print("❌ Aucun fichier trouvé. Créons des fichiers de test...")
            await self._create_sample_files()
            cv_files, fdp_files = self._find_test_files()
        
        # 2. Extraction données
        cv_data = []
        fdp_data = []
        
        for cv_file in cv_files:
            try:
                data = await self._extract_cv_data(cv_file)
                if data:
                    cv_data.append(data)
                    print(f"✅ CV extrait: {cv_file.name}")
            except Exception as e:
                print(f"❌ Erreur extraction CV {cv_file.name}: {e}")
        
        for fdp_file in fdp_files:
            try:
                data = await self._extract_fdp_data(fdp_file)
                if data:
                    fdp_data.append(data)
                    print(f"✅ FDP extraite: {fdp_file.name}")
            except Exception as e:
                print(f"❌ Erreur extraction FDP {fdp_file.name}: {e}")
        
        print()
        
        # 3. Test Transport Intelligence V3.0
        if cv_data and fdp_data:
            await self._run_transport_intelligence_tests(cv_data, fdp_data)
        else:
            print("⚠️ Données insuffisantes pour tests. Affichage données extraites:")
            self._display_extracted_data(cv_data, fdp_data)
    
    def _find_test_files(self) -> tuple[List[Path], List[Path]]:
        """🔍 Trouve fichiers CV TEST et FDP TEST"""
        
        cv_files = []
        fdp_files = []
        
        print("🔍 Recherche fichiers...")
        
        # Patterns de recherche
        cv_patterns = ['*CV*TEST*', '*cv*test*', '*CV*', '*candidat*']
        fdp_patterns = ['*FDP*TEST*', '*fdp*test*', '*FDP*', '*fiche*poste*', '*job*']
        
        for pattern in cv_patterns:
            for ext in self.supported_extensions:
                files = list(self.desktop_path.glob(f"{pattern}{ext}"))
                cv_files.extend(files)
        
        for pattern in fdp_patterns:
            for ext in self.supported_extensions:
                files = list(self.desktop_path.glob(f"{pattern}{ext}"))
                fdp_files.extend(files)
        
        # Dédoublonnage
        cv_files = list(set(cv_files))
        fdp_files = list(set(fdp_files))
        
        print(f"   📄 CV trouvés: {len(cv_files)}")
        for cv in cv_files:
            print(f"      - {cv.name}")
        
        print(f"   📋 FDP trouvées: {len(fdp_files)}")
        for fdp in fdp_files:
            print(f"      - {fdp.name}")
        
        return cv_files, fdp_files
    
    async def _create_sample_files(self):
        """📝 Crée fichiers de test exemples"""
        
        print("📝 Création fichiers de test exemples...")
        
        # CV TEST
        cv_content = """CV TEST - Transport Intelligence

INFORMATIONS PERSONNELLES
Nom: Jean Dupont
Adresse: 45 rue de Rivoli, 75001 Paris
Email: jean.dupont@email.com

MOBILITÉ
Transport: Voiture, Transport public, Vélo
Temps de trajet max: 30 minutes
Télétravail: 2 jours par semaine accepté
Permis B: Oui

EXPÉRIENCE
- Développeur Senior (2020-2024)
- Consultant IT (2018-2020)

COMPÉTENCES
Python, JavaScript, SQL
"""
        
        # FDP TEST
        fdp_content = """FICHE DE POSTE TEST - Transport Intelligence

ENTREPRISE TechCorp
Adresse: 1 Place de la Défense, 92400 Courbevoie

POSTE: Développeur Full Stack Senior

EXIGENCES
- 5+ années d'expérience
- Python, React, Node.js
- Télétravail: 3 jours max par semaine

CONDITIONS
- Salaire: 55k-70k€
- Parking fourni
- Transport: RER A accessible
- Horaires flexibles: Oui

MISSIONS
- Développement applications web
- Architecture microservices
- Encadrement équipe junior
"""
        
        # Sauvegarde fichiers
        cv_file = self.desktop_path / "CV_TEST.txt"
        fdp_file = self.desktop_path / "FDP_TEST.txt"
        
        try:
            cv_file.write_text(cv_content, encoding='utf-8')
            fdp_file.write_text(fdp_content, encoding='utf-8')
            
            print(f"✅ Créé: {cv_file}")
            print(f"✅ Créé: {fdp_file}")
            
        except Exception as e:
            print(f"❌ Erreur création fichiers: {e}")
    
    async def _extract_cv_data(self, cv_file: Path) -> Optional[Dict]:
        """📄 Extrait données CV"""
        
        try:
            # Lecture fichier selon extension
            if cv_file.suffix.lower() == '.txt':
                content = cv_file.read_text(encoding='utf-8')
            elif cv_file.suffix.lower() == '.json':
                with open(cv_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Pour PDF/DOCX, utiliser lecture simple pour demo
                try:
                    content = cv_file.read_text(encoding='utf-8')
                except:
                    print(f"⚠️ Format {cv_file.suffix} nécessite librairie spécialisée")
                    return None
            
            # Extraction données
            extracted = {
                "file_name": cv_file.name,
                "candidate_name": self._extract_name(content),
                "address": self._extract_address(content),
                "transport_methods": self._extract_transport_methods(content),
                "travel_times": self._extract_travel_times(content),
                "remote_preferences": self._extract_remote_preferences(content),
                "raw_content": content[:500] + "..." if len(content) > 500 else content
            }
            
            return extracted
            
        except Exception as e:
            logger.error(f"Erreur extraction CV {cv_file}: {e}")
            return None
    
    async def _extract_fdp_data(self, fdp_file: Path) -> Optional[Dict]:
        """📋 Extrait données FDP"""
        
        try:
            # Lecture fichier
            if fdp_file.suffix.lower() == '.txt':
                content = fdp_file.read_text(encoding='utf-8')
            elif fdp_file.suffix.lower() == '.json':
                with open(fdp_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                try:
                    content = fdp_file.read_text(encoding='utf-8')
                except:
                    print(f"⚠️ Format {fdp_file.suffix} nécessite librairie spécialisée")
                    return None
            
            # Extraction données
            extracted = {
                "file_name": fdp_file.name,
                "company_name": self._extract_company_name(content),
                "job_title": self._extract_job_title(content),
                "address": self._extract_address(content),
                "remote_policy": self._extract_remote_policy(content),
                "transport_info": self._extract_transport_info(content),
                "raw_content": content[:500] + "..." if len(content) > 500 else content
            }
            
            return extracted
            
        except Exception as e:
            logger.error(f"Erreur extraction FDP {fdp_file}: {e}")
            return None
    
    def _extract_address(self, content: str) -> Optional[str]:
        """📍 Extrait adresse depuis le contenu"""
        
        for pattern in self.extraction_patterns["address"]:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Nettoyage et validation
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    
                    # Validation basique adresse
                    if len(match) > 10 and any(keyword in match.lower() for keyword in ['rue', 'avenue', 'place', 'boulevard', 'paris', 'france']):
                        return match.strip()
        
        return None
    
    def _extract_transport_methods(self, content: str) -> List[str]:
        """🚗 Extrait modes de transport préférés"""
        
        methods = []
        content_lower = content.lower()
        
        # Mapping mots-clés → transport_methods
        transport_mapping = {
            'voiture': 'vehicle',
            'véhicule': 'vehicle',
            'auto': 'vehicle',
            'permis': 'vehicle',
            'transport public': 'public-transport',
            'transport en commun': 'public-transport',
            'métro': 'public-transport',
            'rer': 'public-transport',
            'bus': 'public-transport',
            'vélo': 'bike',
            'bicyclette': 'bike',
            'cyclisme': 'bike',
            'marche': 'walking',
            'piéton': 'walking',
            'pied': 'walking'
        }
        
        for keyword, method in transport_mapping.items():
            if keyword in content_lower:
                if method not in methods:
                    methods.append(method)
        
        # Valeurs par défaut si rien trouvé
        if not methods:
            methods = ['public-transport', 'vehicle']
        
        return methods
    
    def _extract_travel_times(self, content: str) -> Dict[str, int]:
        """⏰ Extrait temps de trajet acceptables"""
        
        # Recherche temps max mentionné
        time_patterns = [
            r'(\d+)\s*(?:min|minutes?)',
            r'temps\s+(?:de\s+)?trajet\s+(?:max|maximum)\s*:?\s*(\d+)',
            r'déplacement\s+(?:max|maximum)\s*:?\s*(\d+)'
        ]
        
        max_time = 45  # Défaut
        
        for pattern in time_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    max_time = int(matches[0])
                    break
                except:
                    continue
        
        # Times par défaut basés sur le max trouvé
        return {
            'public-transport': max_time,
            'vehicle': max_time - 5,
            'bike': max(20, max_time - 15),
            'walking': max(15, max_time - 20)
        }
    
    def _extract_remote_preferences(self, content: str) -> Dict[str, Any]:
        """🏠 Extrait préférences télétravail"""
        
        content_lower = content.lower()
        remote_days = 0
        
        # Recherche jours télétravail
        remote_patterns = [
            r'télétravail\s*:?\s*(\d+)\s*jours?',
            r'remote\s*:?\s*(\d+)\s*jours?',
            r'(\d+)\s*jours?\s+(?:de\s+)?télétravail'
        ]
        
        for pattern in remote_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                try:
                    remote_days = int(matches[0])
                    break
                except:
                    continue
        
        return {
            'remote_days_per_week': remote_days,
            'flexible_hours': 'flexible' in content_lower or 'souple' in content_lower
        }
    
    def _extract_name(self, content: str) -> Optional[str]:
        """👤 Extrait nom candidat"""
        
        name_patterns = [
            r'nom\s*:?\s*([A-Za-zÀ-ÿ\s\-]+)',
            r'candidat\s*:?\s*([A-Za-zÀ-ÿ\s\-]+)',
            r'^([A-Za-zÀ-ÿ]+\s+[A-Za-zÀ-ÿ]+)'
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                name = matches[0].strip()
                if len(name) > 3:
                    return name
        
        return "Candidat Anonyme"
    
    def _extract_company_name(self, content: str) -> Optional[str]:
        """🏢 Extrait nom entreprise"""
        
        company_patterns = [
            r'entreprise\s*:?\s*([A-Za-zÀ-ÿ\s\-&]+)',
            r'société\s*:?\s*([A-Za-zÀ-ÿ\s\-&]+)',
            r'company\s*:?\s*([A-Za-zÀ-ÿ\s\-&]+)'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return "Entreprise Inconnue"
    
    def _extract_job_title(self, content: str) -> Optional[str]:
        """💼 Extrait titre poste"""
        
        job_patterns = [
            r'poste\s*:?\s*([A-Za-zÀ-ÿ\s\-]+)',
            r'titre\s*:?\s*([A-Za-zÀ-ÿ\s\-]+)',
            r'position\s*:?\s*([A-Za-zÀ-ÿ\s\-]+)'
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return "Poste Non Spécifié"
    
    def _extract_remote_policy(self, content: str) -> Dict[str, Any]:
        """🏠 Extrait politique télétravail entreprise"""
        
        content_lower = content.lower()
        
        remote_info = {
            'remote_possible': 'télétravail' in content_lower or 'remote' in content_lower,
            'max_remote_days': 0,
            'flexible_hours': 'flexible' in content_lower or 'souple' in content_lower
        }
        
        # Recherche nombre jours télétravail max
        remote_patterns = [
            r'télétravail\s*:?\s*(\d+)\s*jours?\s*max',
            r'(\d+)\s*jours?\s+(?:de\s+)?télétravail\s+max'
        ]
        
        for pattern in remote_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                try:
                    remote_info['max_remote_days'] = int(matches[0])
                    break
                except:
                    continue
        
        return remote_info
    
    def _extract_transport_info(self, content: str) -> Dict[str, Any]:
        """🚌 Extrait infos transport entreprise"""
        
        content_lower = content.lower()
        
        return {
            'parking_provided': 'parking' in content_lower,
            'public_transport_access': any(keyword in content_lower for keyword in ['métro', 'rer', 'bus', 'transport public']),
            'transport_reimbursement': 'remboursement' in content_lower
        }
    
    async def _run_transport_intelligence_tests(self, cv_data: List[Dict], fdp_data: List[Dict]):
        """🚀 Lance tests Transport Intelligence V3.0"""
        
        print("🚀 LANCEMENT TESTS TRANSPORT INTELLIGENCE V3.0")
        print("=" * 55)
        
        try:
            # Import du système
            sys.path.insert(0, '.')
            from nextvision.engines.transport_intelligence_engine import TransportIntelligenceEngine
            from nextvision.services.google_maps_service import GoogleMapsService
            from nextvision.services.transport_calculator import TransportCalculator
            
            # Initialisation
            google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            if not google_maps_api_key:
                print("⚠️ GOOGLE_MAPS_API_KEY non configurée - mode simulation")
                return
            
            google_maps_service = GoogleMapsService(api_key=google_maps_api_key)
            transport_calculator = TransportCalculator(google_maps_service)
            engine = TransportIntelligenceEngine(google_maps_service, transport_calculator)
            
            print("✅ Transport Intelligence Engine initialisé")
            print()
            
            # Tests croisés CV × FDP
            for i, cv in enumerate(cv_data, 1):
                for j, fdp in enumerate(fdp_data, 1):
                    await self._test_cv_fdp_match(engine, cv, fdp, i, j)
            
        except ImportError as e:
            print(f"❌ Erreur import Transport Intelligence: {e}")
            print("💡 Assurez-vous que le système V3.0 est installé")
        except Exception as e:
            print(f"❌ Erreur tests: {e}")
    
    async def _test_cv_fdp_match(self, engine, cv: Dict, fdp: Dict, cv_num: int, fdp_num: int):
        """🎯 Test matching CV × FDP"""
        
        print(f"🎯 TEST {cv_num}×{fdp_num}: {cv['candidate_name']} → {fdp['company_name']}")
        print(f"   CV: {cv['file_name']}")
        print(f"   FDP: {fdp['file_name']}")
        
        try:
            # Validation adresses
            if not cv.get('address') or not fdp.get('address'):
                print("   ❌ Adresse manquante - test impossible")
                print()
                return
            
            # Préparation contexte
            context = {
                'remote_days_per_week': cv.get('remote_preferences', {}).get('remote_days_per_week', 0),
                'flexible_hours': cv.get('remote_preferences', {}).get('flexible_hours', False),
                'parking_provided': fdp.get('transport_info', {}).get('parking_provided', False),
                'supports_remote': fdp.get('remote_policy', {}).get('remote_possible', False)
            }
            
            # Lancement test
            result = await engine.calculate_intelligent_location_score(
                candidat_address=cv['address'],
                entreprise_address=fdp['address'],
                transport_methods=cv.get('transport_methods', ['public-transport', 'vehicle']),
                travel_times=cv.get('travel_times', {'public-transport': 45, 'vehicle': 40}),
                context=context
            )
            
            # Affichage résultats
            score = result.get('final_score', 0)
            compatible_modes = result.get('compatibility_analysis', {}).get('compatible_modes', [])
            best_option = result.get('best_transport_option', {})
            
            print(f"   📊 Score: {score:.3f}/1.0")
            print(f"   ✅ Modes compatibles: {compatible_modes}")
            if best_option.get('mode'):
                print(f"   🌟 Recommandé: {best_option['mode']} ({best_option.get('duration_minutes', '?')}min)")
            
            # Top explications
            explanations = result.get('explanations', [])[:3]
            for explanation in explanations:
                print(f"   {explanation}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Erreur test: {e}")
            print()
    
    def _display_extracted_data(self, cv_data: List[Dict], fdp_data: List[Dict]):
        """📋 Affiche données extraites"""
        
        print("📋 DONNÉES EXTRAITES:")
        print()
        
        print("👤 CV CANDIDATS:")
        for i, cv in enumerate(cv_data, 1):
            print(f"   {i}. {cv['candidate_name']} ({cv['file_name']})")
            print(f"      📍 Adresse: {cv.get('address', 'Non trouvée')}")
            print(f"      🚗 Transport: {cv.get('transport_methods', [])}")
            print(f"      ⏰ Temps max: {cv.get('travel_times', {})}")
            print(f"      🏠 Télétravail: {cv.get('remote_preferences', {})}")
            print()
        
        print("🏢 FICHES DE POSTE:")
        for i, fdp in enumerate(fdp_data, 1):
            print(f"   {i}. {fdp['company_name']} - {fdp['job_title']} ({fdp['file_name']})")
            print(f"      📍 Adresse: {fdp.get('address', 'Non trouvée')}")
            print(f"      🏠 Remote: {fdp.get('remote_policy', {})}")
            print(f"      🚌 Transport: {fdp.get('transport_info', {})}")
            print()

async def main():
    """🎯 Point d'entrée principal"""
    
    try:
        tester = RealDataTransportTester()
        await tester.run_real_data_tests()
        
    except KeyboardInterrupt:
        print("\n👋 Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur tests: {e}")
    
    print("\n🎉 Tests terminés")
    print("💡 Pour ajouter vos fichiers, placez-les sur le Bureau avec:")
    print("   - 'CV' dans le nom pour les CV")
    print("   - 'FDP' ou 'fiche' dans le nom pour les fiches de poste")

if __name__ == "__main__":
    asyncio.run(main())
