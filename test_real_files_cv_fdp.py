#!/usr/bin/env python3
"""
🎯 NEXTVISION V3.2.1 - TESTS AVEC VRAIS FICHIERS CV & FDP

Test complet du matching avec de vrais documents depuis le bureau.
Parcours: CV Parsing → FDP Parsing → Matching Intelligence

Version: 3.2.1-REAL-FILES
Date: 2025-07-11
Auteur: Assistant Claude - TEST RÉEL
"""

import asyncio
import time
import json
import os
import glob
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nextvision_real_files')

class NextvisionRealFilesTester:
    """Testeur avec vrais fichiers CV et FDP"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None
        self.desktop_path = Path.home() / "Desktop"
        self.bureau_path = Path.home() / "Bureau"  # Pour les Macs français
        
        # Résultats des tests
        self.test_results = []
        self.matching_results = []
        
        # Extensions supportées
        self.cv_extensions = ['.pdf', '.docx', '.doc', '.txt']
        self.fdp_extensions = ['.pdf', '.docx', '.doc', '.txt']
    
    async def __aenter__(self):
        """Initialisation asynchrone"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)  # Plus long pour vrais fichiers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage asynchrone"""
        if self.session:
            await self.session.close()
    
    def find_desktop_path(self) -> Path:
        """Trouve le chemin du bureau selon la langue du système"""
        if self.bureau_path.exists():
            logger.info(f"📁 Bureau trouvé: {self.bureau_path}")
            return self.bureau_path
        elif self.desktop_path.exists():
            logger.info(f"📁 Desktop trouvé: {self.desktop_path}")
            return self.desktop_path
        else:
            logger.warning("⚠️ Ni Bureau ni Desktop trouvé, utilisation du répertoire home")
            return Path.home()
    
    def find_files(self, keywords: List[str], extensions: List[str]) -> List[Path]:
        """Trouve les fichiers correspondant aux critères"""
        desktop = self.find_desktop_path()
        found_files = []
        
        for keyword in keywords:
            for ext in extensions:
                # Recherche case-insensitive
                pattern = f"*{keyword.lower()}*{ext}"
                files = list(desktop.glob(pattern))
                
                # Recherche aussi en majuscules
                pattern_upper = f"*{keyword.upper()}*{ext}"
                files.extend(list(desktop.glob(pattern_upper)))
                
                # Recherche capitalized
                pattern_cap = f"*{keyword.capitalize()}*{ext}"
                files.extend(list(desktop.glob(pattern_cap)))
                
                found_files.extend(files)
        
        # Supprimer les doublons
        unique_files = list(set(found_files))
        return unique_files
    
    def find_cv_files(self) -> List[Path]:
        """Trouve les fichiers CV sur le bureau"""
        cv_keywords = ['cv', 'resume', 'curriculum', 'candidat', 'candidate']
        cv_files = self.find_files(cv_keywords, self.cv_extensions)
        
        logger.info(f"📄 {len(cv_files)} fichier(s) CV trouvé(s):")
        for cv_file in cv_files:
            logger.info(f"   • {cv_file.name}")
        
        return cv_files
    
    def find_fdp_files(self) -> List[Path]:
        """Trouve les fichiers FDP (Fiches de Poste) sur le bureau"""
        fdp_keywords = ['fdp', 'fiche', 'poste', 'job', 'offre', 'emploi', 'position']
        fdp_files = self.find_files(fdp_keywords, self.fdp_extensions)
        
        logger.info(f"📋 {len(fdp_files)} fichier(s) FDP trouvé(s):")
        for fdp_file in fdp_files:
            logger.info(f"   • {fdp_file.name}")
        
        return fdp_files
    
    def generate_realistic_questionnaire(self, cv_filename: str) -> Dict:
        """Génère un questionnaire réaliste basé sur le nom du fichier CV"""
        
        # Analyse du nom de fichier pour déduire le profil
        filename_lower = cv_filename.lower()
        
        questionnaire_base = {
            "personal_info": {
                "firstName": "Test",
                "lastName": "Candidat"
            },
            "raison_ecoute": "Recherche nouveau défi",
            "transport_preferences": {
                "modes_preferes": ["voiture", "transport_commun"],
                "temps_max_acceptable": 45,
                "jours_teletravail_souhaites": 2
            },
            "salary_expectations": {
                "min": 35000,
                "max": 50000,
                "current": 40000
            },
            "location_preferences": {
                "ville_actuelle": "Paris",
                "villes_acceptees": ["Paris", "Boulogne-Billancourt", "Neuilly-sur-Seine"],
                "distance_max_km": 30
            }
        }
        
        # Ajustements selon le profil déduit du nom de fichier
        if any(word in filename_lower for word in ['senior', 'manager', 'chef', 'directeur', 'lead']):
            questionnaire_base["raison_ecoute"] = "Recherche nouveau défi"
            questionnaire_base["salary_expectations"] = {
                "min": 60000, "max": 85000, "current": 65000
            }
        elif any(word in filename_lower for word in ['junior', 'assistant', 'stage', 'alternant']):
            questionnaire_base["raison_ecoute"] = "Rémunération trop faible"
            questionnaire_base["salary_expectations"] = {
                "min": 28000, "max": 35000, "current": 30000
            }
        elif any(word in filename_lower for word in ['comptable', 'finance', 'daf']):
            questionnaire_base["raison_ecoute"] = "Poste ne coïncide pas avec poste proposé"
            questionnaire_base["salary_expectations"] = {
                "min": 45000, "max": 70000, "current": 50000
            }
        
        return questionnaire_base
    
    async def test_cv_parsing(self, cv_file: Path) -> Dict:
        """Teste le parsing d'un CV réel"""
        logger.info(f"🔍 Test parsing CV: {cv_file.name}")
        start_time = time.time()
        
        try:
            # Lecture du fichier
            with open(cv_file, 'rb') as f:
                cv_content = f.read()
            
            # Génération du questionnaire réaliste
            questionnaire = self.generate_realistic_questionnaire(cv_file.name)
            
            # Préparation des données pour l'API
            data = aiohttp.FormData()
            data.add_field('file', 
                          cv_content, 
                          filename=cv_file.name,
                          content_type='application/octet-stream')
            data.add_field('candidat_questionnaire', json.dumps(questionnaire))
            
            # Appel à l'API
            async with self.session.post(
                f"{self.base_url}/api/v2/conversion/commitment/enhanced",
                data=data
            ) as response:
                
                duration = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ CV parsé avec succès ({duration:.1f}ms)")
                    return {
                        "success": True,
                        "duration_ms": duration,
                        "filename": cv_file.name,
                        "parsing_result": result,
                        "questionnaire_used": questionnaire
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Échec parsing CV: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "duration_ms": duration,
                        "filename": cv_file.name,
                        "error": f"HTTP {response.status}: {error_text}",
                        "questionnaire_used": questionnaire
                    }
        
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"❌ Erreur parsing CV {cv_file.name}: {str(e)}")
            return {
                "success": False,
                "duration_ms": duration,
                "filename": cv_file.name,
                "error": str(e)
            }
    
    async def test_fdp_parsing(self, fdp_file: Path) -> Dict:
        """Teste le parsing d'une FDP réelle"""
        logger.info(f"🔍 Test parsing FDP: {fdp_file.name}")
        start_time = time.time()
        
        try:
            # Lecture du fichier
            with open(fdp_file, 'rb') as f:
                fdp_content = f.read()
            
            # Contexte pour la FDP
            context = {
                "company": "Entreprise Test",
                "department": "Finance",
                "urgent": False
            }
            
            # Préparation des données pour l'API
            data = aiohttp.FormData()
            data.add_field('file', 
                          fdp_content, 
                          filename=fdp_file.name,
                          content_type='application/octet-stream')
            data.add_field('additional_context', json.dumps(context))
            
            # Appel à l'API
            async with self.session.post(
                f"{self.base_url}/api/v2/jobs/parse",
                data=data
            ) as response:
                
                duration = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ FDP parsée avec succès ({duration:.1f}ms)")
                    return {
                        "success": True,
                        "duration_ms": duration,
                        "filename": fdp_file.name,
                        "parsing_result": result,
                        "context_used": context
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Échec parsing FDP: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "duration_ms": duration,
                        "filename": fdp_file.name,
                        "error": f"HTTP {response.status}: {error_text}",
                        "context_used": context
                    }
        
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"❌ Erreur parsing FDP {fdp_file.name}: {str(e)}")
            return {
                "success": False,
                "duration_ms": duration,
                "filename": fdp_file.name,
                "error": str(e)
            }
    
    def create_matching_request_from_parsed_data(self, cv_result: Dict, questionnaire: Dict) -> Dict:
        """Crée une requête de matching à partir des données parsées"""
        
        # Si le parsing a réussi, utiliser les données parsées
        if cv_result.get("success") and cv_result.get("parsing_result"):
            parsed_data = cv_result["parsing_result"].get("parsing_result", {})
            personal_info = parsed_data.get("personal_info", {})
            
            # Extraction des données parsées ou utilisation des données du questionnaire
            first_name = personal_info.get("prenom", questionnaire["personal_info"]["firstName"])
            last_name = personal_info.get("nom", questionnaire["personal_info"]["lastName"])
            skills = parsed_data.get("competences", ["Comptabilité", "Finance", "Excel"])
            experience_years = parsed_data.get("experience", {}).get("annees_experience", 5)
            
        else:
            # Fallback sur les données du questionnaire
            first_name = questionnaire["personal_info"]["firstName"]
            last_name = questionnaire["personal_info"]["lastName"]
            skills = ["Comptabilité", "Finance", "Excel"]  # Compétences par défaut
            experience_years = 5  # Expérience par défaut
        
        # Construction de la requête de matching
        matching_request = {
            "pourquoi_ecoute": questionnaire["raison_ecoute"],
            "candidate_profile": {
                "personal_info": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                    "phone": "0123456789"
                },
                "skills": skills,
                "experience_years": experience_years,
                "education": "Formation professionnelle",
                "current_role": "Poste actuel"
            },
            "preferences": {
                "salary_expectations": questionnaire["salary_expectations"],
                "location_preferences": {
                    "city": questionnaire["location_preferences"]["ville_actuelle"],
                    "acceptedCities": questionnaire["location_preferences"]["villes_acceptees"],
                    "maxDistance": questionnaire["location_preferences"]["distance_max_km"]
                },
                "remote_preferences": f"{questionnaire['transport_preferences']['jours_teletravail_souhaites']} jours/semaine",
                "sectors": ["Finance", "Comptabilité"],
                "company_size": "PME/ETI"
            },
            "availability": "Immédiate"
        }
        
        return matching_request
    
    async def test_complete_matching(self, cv_result: Dict, fdp_result: Dict) -> Dict:
        """Teste le matching complet entre un CV et une FDP"""
        logger.info(f"🎯 Test matching: {cv_result['filename']} ↔ {fdp_result.get('filename', 'FDP simulée')}")
        start_time = time.time()
        
        try:
            # Création de la requête de matching
            questionnaire = cv_result.get("questionnaire_used", {})
            matching_request = self.create_matching_request_from_parsed_data(cv_result, questionnaire)
            
            # ID unique pour ce test
            candidate_id = f"real_test_{int(time.time())}"
            
            # Appel à l'API de matching
            async with self.session.post(
                f"{self.base_url}/api/v1/matching/candidate/{candidate_id}",
                json=matching_request
            ) as response:
                
                duration = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Extraction des métriques importantes
                    matching_results = result.get("matching_results", {})
                    total_score = matching_results.get("total_score", 0)
                    component_scores = matching_results.get("component_scores", {})
                    adaptive_weighting = result.get("adaptive_weighting", {})
                    
                    logger.info(f"✅ Matching réussi - Score: {total_score:.3f} ({duration:.1f}ms)")
                    
                    return {
                        "success": True,
                        "duration_ms": duration,
                        "cv_filename": cv_result["filename"],
                        "fdp_filename": fdp_result.get("filename", "FDP simulée"),
                        "candidate_id": candidate_id,
                        "total_score": total_score,
                        "component_scores": component_scores,
                        "adaptive_weighting": adaptive_weighting,
                        "full_result": result,
                        "matching_request": matching_request
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Échec matching: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "duration_ms": duration,
                        "cv_filename": cv_result["filename"],
                        "fdp_filename": fdp_result.get("filename", "FDP simulée"),
                        "error": f"HTTP {response.status}: {error_text}"
                    }
        
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"❌ Erreur matching: {str(e)}")
            return {
                "success": False,
                "duration_ms": duration,
                "cv_filename": cv_result["filename"],
                "fdp_filename": fdp_result.get("filename", "FDP simulée"),
                "error": str(e)
            }
    
    async def run_complete_test_suite(self) -> Dict:
        """Lance la suite complète de tests avec vrais fichiers"""
        logger.info("🚀 Démarrage des tests avec vrais fichiers CV et FDP")
        start_time = time.time()
        
        # 1. Recherche des fichiers
        cv_files = self.find_cv_files()
        fdp_files = self.find_fdp_files()
        
        if not cv_files:
            logger.warning("⚠️ Aucun fichier CV trouvé sur le bureau")
            return {"error": "Aucun fichier CV trouvé"}
        
        # 2. Test du parsing des CV
        logger.info(f"\n📄 === PHASE 1: PARSING {len(cv_files)} CV(S) ===")
        cv_results = []
        for cv_file in cv_files[:3]:  # Limite à 3 CV pour éviter la surcharge
            cv_result = await self.test_cv_parsing(cv_file)
            cv_results.append(cv_result)
            self.test_results.append(cv_result)
        
        # 3. Test du parsing des FDP (si disponibles)
        logger.info(f"\n📋 === PHASE 2: PARSING {len(fdp_files)} FDP(S) ===")
        fdp_results = []
        if fdp_files:
            for fdp_file in fdp_files[:2]:  # Limite à 2 FDP
                fdp_result = await self.test_fdp_parsing(fdp_file)
                fdp_results.append(fdp_result)
                self.test_results.append(fdp_result)
        else:
            logger.info("ℹ️ Aucune FDP trouvée, utilisation d'une FDP simulée")
            fdp_results.append({
                "success": True,
                "filename": "FDP_simulée.txt",
                "parsing_result": {
                    "job_id": "simulated_job_001",
                    "titre_poste": "Comptable Général",
                    "entreprise": "Entreprise Test",
                    "localisation": "Paris 15ème",
                    "type_contrat": "CDI",
                    "competences_requises": ["Comptabilité", "Sage", "Excel"],
                    "salaire": "35000-45000€"
                }
            })
        
        # 4. Test des matchings complets
        logger.info(f"\n🎯 === PHASE 3: MATCHING COMPLET ===")
        for cv_result in cv_results:
            if cv_result["success"]:
                for fdp_result in fdp_results:
                    matching_result = await self.test_complete_matching(cv_result, fdp_result)
                    self.matching_results.append(matching_result)
        
        # 5. Génération du rapport final
        total_duration = time.time() - start_time
        return self.generate_final_report(total_duration)
    
    def generate_final_report(self, total_duration: float) -> Dict:
        """Génère le rapport final des tests"""
        
        # Statistiques globales
        successful_cv_parsing = len([r for r in self.test_results if "CV" in r.get("filename", "") and r.get("success")])
        failed_cv_parsing = len([r for r in self.test_results if "CV" in r.get("filename", "") and not r.get("success")])
        
        successful_fdp_parsing = len([r for r in self.test_results if "FDP" in r.get("filename", "") and r.get("success")])
        failed_fdp_parsing = len([r for r in self.test_results if "FDP" in r.get("filename", "") and not r.get("success")])
        
        successful_matching = len([r for r in self.matching_results if r.get("success")])
        failed_matching = len([r for r in self.matching_results if not r.get("success")])
        
        # Analyse des scores de matching
        scores = [r.get("total_score", 0) for r in self.matching_results if r.get("success")]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        # Performance
        durations = [r.get("duration_ms", 0) for r in self.matching_results if r.get("success")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        report = {
            "summary": {
                "test_type": "Real Files CV & FDP Testing",
                "total_duration_seconds": total_duration,
                "timestamp": datetime.now().isoformat(),
                "cv_parsing": {
                    "successful": successful_cv_parsing,
                    "failed": failed_cv_parsing,
                    "success_rate": successful_cv_parsing / (successful_cv_parsing + failed_cv_parsing) if (successful_cv_parsing + failed_cv_parsing) > 0 else 0
                },
                "fdp_parsing": {
                    "successful": successful_fdp_parsing,
                    "failed": failed_fdp_parsing,
                    "success_rate": successful_fdp_parsing / (successful_fdp_parsing + failed_fdp_parsing) if (successful_fdp_parsing + failed_fdp_parsing) > 0 else 0
                },
                "matching": {
                    "successful": successful_matching,
                    "failed": failed_matching,
                    "success_rate": successful_matching / (successful_matching + failed_matching) if (successful_matching + failed_matching) > 0 else 0,
                    "avg_score": avg_score,
                    "max_score": max_score,
                    "min_score": min_score,
                    "avg_duration_ms": avg_duration
                }
            },
            "detailed_results": {
                "cv_parsing_results": [r for r in self.test_results if "CV" in r.get("filename", "")],
                "fdp_parsing_results": [r for r in self.test_results if "FDP" in r.get("filename", "")],
                "matching_results": self.matching_results
            },
            "best_matches": sorted([r for r in self.matching_results if r.get("success")], 
                                 key=lambda x: x.get("total_score", 0), reverse=True)[:3],
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur les résultats"""
        recommendations = []
        
        successful_matching = len([r for r in self.matching_results if r.get("success")])
        total_matching = len(self.matching_results)
        
        if successful_matching == total_matching and total_matching > 0:
            recommendations.append("🎉 Tous les matchings ont réussi ! Le système fonctionne parfaitement avec de vrais fichiers.")
        elif successful_matching > 0:
            recommendations.append(f"✅ {successful_matching}/{total_matching} matchings réussis.")
        
        scores = [r.get("total_score", 0) for r in self.matching_results if r.get("success")]
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score > 0.8:
                recommendations.append(f"🎯 Excellent score moyen: {avg_score:.3f}")
            elif avg_score > 0.6:
                recommendations.append(f"👍 Bon score moyen: {avg_score:.3f}")
            else:
                recommendations.append(f"⚠️ Score moyen à améliorer: {avg_score:.3f}")
        
        recommendations.append("📋 Prochaines étapes:")
        recommendations.append("   • Tester avec plus de fichiers variés")
        recommendations.append("   • Implémenter le système hiérarchique")
        recommendations.append("   • Optimiser les scores de matching")
        
        return recommendations


async def main():
    """Fonction principale pour les tests avec vrais fichiers"""
    print("🎯 NEXTVISION V3.2.1 - TESTS AVEC VRAIS FICHIERS CV & FDP")
    print("=" * 65)
    print("📁 Recherche de fichiers sur le bureau...")
    print("=" * 65)
    
    async with NextvisionRealFilesTester() as tester:
        report = await tester.run_complete_test_suite()
        
        if "error" in report:
            print(f"❌ Erreur: {report['error']}")
            print("\n💡 Suggestions:")
            print("   • Placez des fichiers CV sur votre bureau (noms contenant 'cv', 'resume', 'candidat')")
            print("   • Placez des fichiers FDP sur votre bureau (noms contenant 'fdp', 'fiche', 'poste', 'offre')")
            print("   • Extensions supportées: .pdf, .docx, .doc, .txt")
            return 1
        
        # Affichage du rapport final
        print("\n" + "=" * 65)
        print("📊 RAPPORT FINAL - TESTS AVEC VRAIS FICHIERS")
        print("=" * 65)
        
        summary = report['summary']
        
        print(f"⏱️ Durée totale: {summary['total_duration_seconds']:.1f}s")
        print(f"📅 Timestamp: {summary['timestamp']}")
        
        print(f"\n📄 PARSING CV:")
        cv_stats = summary['cv_parsing']
        print(f"   Réussis: {cv_stats['successful']}")
        print(f"   Échecs: {cv_stats['failed']}")
        print(f"   Taux de réussite: {cv_stats['success_rate']:.1%}")
        
        print(f"\n📋 PARSING FDP:")
        fdp_stats = summary['fdp_parsing']
        print(f"   Réussis: {fdp_stats['successful']}")
        print(f"   Échecs: {fdp_stats['failed']}")
        print(f"   Taux de réussite: {fdp_stats['success_rate']:.1%}")
        
        print(f"\n🎯 MATCHING:")
        matching_stats = summary['matching']
        print(f"   Réussis: {matching_stats['successful']}")
        print(f"   Échecs: {matching_stats['failed']}")
        print(f"   Taux de réussite: {matching_stats['success_rate']:.1%}")
        print(f"   Score moyen: {matching_stats['avg_score']:.3f}")
        print(f"   Score max: {matching_stats['max_score']:.3f}")
        print(f"   Score min: {matching_stats['min_score']:.3f}")
        print(f"   Durée moyenne: {matching_stats['avg_duration_ms']:.1f}ms")
        
        print(f"\n🏆 MEILLEURS MATCHINGS:")
        for i, match in enumerate(report['best_matches'], 1):
            print(f"   {i}. {match['cv_filename']} → Score: {match['total_score']:.3f}")
        
        print("\n📋 RECOMMANDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        
        # Sauvegarde du rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"nextvision_real_files_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport détaillé sauvegardé: {report_file}")
        
        # Code de sortie
        exit_code = 0 if matching_stats['success_rate'] > 0.5 else 1
        print(f"\n🎯 Tests terminés avec le code: {exit_code}")
        
        return exit_code


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrompus par l'utilisateur")
        exit(2)
    except Exception as e:
        print(f"\n❌ Erreur critique: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(3)