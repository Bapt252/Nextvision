#!/usr/bin/env python3
"""
🧠 TEST MATCHING SÉMANTIQUE AVEC CV ET FDP RÉELS
Test spécialisé pour valider le scoring sémantique avec vrais documents

Author: Assistant Claude  
Version: 1.0.0-semantic-focus
"""

import os
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Import du semantic scorer
from nextvision.services.bidirectional_scorer import SemanticScorer
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    PersonalInfoBidirectional, CompetencesProfessionnelles, 
    InformationsEntreprise, DescriptionPoste,
    NiveauExperience, TypeContrat
)

class SemanticMatchingTester:
    """🧠 Testeur spécialisé matching sémantique"""
    
    def __init__(self):
        self.semantic_scorer = SemanticScorer()
        self.bureau_path = Path.home() / "Desktop"
        self.cv_folder = self.bureau_path / "CV TEST"
        self.fdp_folder = self.bureau_path / "FDP TEST"
        
        print("🧠 === TESTEUR MATCHING SÉMANTIQUE ===")
        print(f"📂 Dossier CV: {self.cv_folder}")
        print(f"📂 Dossier FDP: {self.fdp_folder}")
    
    def scan_documents(self) -> Dict[str, List[Path]]:
        """📂 Scanner les dossiers CV et FDP"""
        
        documents = {
            "cv_files": [],
            "fdp_files": []
        }
        
        # Scanner dossier CV TEST
        if self.cv_folder.exists():
            for ext in ['*.pdf', '*.docx', '*.doc', '*.txt']:
                documents["cv_files"].extend(self.cv_folder.glob(ext))
            print(f"📄 CV trouvés: {len(documents['cv_files'])}")
            for cv in documents["cv_files"]:
                print(f"   • {cv.name}")
        else:
            print(f"⚠️ Dossier CV TEST non trouvé: {self.cv_folder}")
        
        # Scanner dossier FDP TEST  
        if self.fdp_folder.exists():
            for ext in ['*.pdf', '*.docx', '*.doc', '*.txt']:
                documents["fdp_files"].extend(self.fdp_folder.glob(ext))
            print(f"📋 FDP trouvées: {len(documents['fdp_files'])}")
            for fdp in documents["fdp_files"]:
                print(f"   • {fdp.name}")
        else:
            print(f"⚠️ Dossier FDP TEST non trouvé: {self.fdp_folder}")
        
        return documents
    
    def extract_text_from_file(self, file_path: Path) -> str:
        """📝 Extraction texte depuis différents formats"""
        
        try:
            if file_path.suffix.lower() == '.txt':
                # Fichiers texte
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_path.suffix.lower() in ['.pdf']:
                # PDF (nécessite PyPDF2 ou pdfplumber)
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    print(f"⚠️ PyPDF2 non installé pour lire {file_path.name}")
                    return f"CONTENU PDF NON EXTRACTIBLE - {file_path.name}"
                except Exception as e:
                    print(f"⚠️ Erreur lecture PDF {file_path.name}: {e}")
                    return f"ERREUR LECTURE PDF - {file_path.name}"
            
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                # Documents Word (nécessite python-docx)
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    print(f"⚠️ python-docx non installé pour lire {file_path.name}")
                    return f"CONTENU DOCX NON EXTRACTIBLE - {file_path.name}"
                except Exception as e:
                    print(f"⚠️ Erreur lecture DOCX {file_path.name}: {e}")
                    return f"ERREUR LECTURE DOCX - {file_path.name}"
            
            else:
                return f"FORMAT NON SUPPORTÉ - {file_path.name}"
                
        except Exception as e:
            print(f"❌ Erreur extraction {file_path.name}: {e}")
            return f"ERREUR EXTRACTION - {file_path.name}"
    
    def parse_cv_content(self, cv_text: str, filename: str) -> BiDirectionalCandidateProfile:
        """🔍 Parser basique du contenu CV pour créer un profil candidat"""
        
        # Extraction basique des compétences (mots-clés techniques)
        competences_techniques = []
        keywords_tech = [
            'python', 'java', 'javascript', 'react', 'node', 'angular', 'vue',
            'php', 'sql', 'mysql', 'postgresql', 'mongodb', 'docker', 'kubernetes',
            'aws', 'azure', 'git', 'jenkins', 'linux', 'windows', 'html', 'css',
            'bootstrap', 'jquery', 'typescript', 'c++', 'c#', 'ruby', 'go',
            'comptabilité', 'cegid', 'sage', 'excel', 'powerpoint', 'word',
            'gestion', 'marketing', 'vente', 'commercial', 'rh', 'finance'
        ]
        
        cv_lower = cv_text.lower()
        for keyword in keywords_tech:
            if keyword in cv_lower:
                competences_techniques.append(keyword.title())
        
        # Extraction nom (basique - premier mot en majuscules)
        lines = cv_text.strip().split('\n')
        first_name = "Candidat"
        last_name = filename.replace('.pdf', '').replace('.docx', '').replace('.txt', '')
        
        # Tentative extraction nom plus intelligente
        for line in lines[:5]:  # Check premières lignes
            words = line.strip().split()
            if len(words) >= 2 and words[0].isupper() and words[1].isupper():
                first_name = words[0].title()
                last_name = words[1].title()
                break
        
        # Estimation expérience (cherche patterns d'années)
        experience_globale = NiveauExperience.CONFIRME  # Défaut
        import re
        experience_patterns = re.findall(r'(\d+)\s*an[s]?', cv_lower)
        if experience_patterns:
            max_exp = max([int(x) for x in experience_patterns])
            if max_exp <= 2:
                experience_globale = NiveauExperience.JUNIOR
            elif max_exp <= 5:
                experience_globale = NiveauExperience.CONFIRME
            else:
                experience_globale = NiveauExperience.SENIOR
        
        # Création profil candidat
        candidat = BiDirectionalCandidateProfile(
            personal_info=PersonalInfoBidirectional(
                firstName=first_name,
                lastName=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}@test.com",
                phone="0123456789"
            ),
            experience_globale=experience_globale,
            competences=CompetencesProfessionnelles(
                competences_techniques=competences_techniques if competences_techniques else ["Compétences générales"],
                logiciels_maitrise=competences_techniques[:5],  # Top 5
                langues={"Français": "Natif", "Anglais": "Courant"}
            ),
            attentes=None,  # Pas nécessaire pour test sémantique
            motivations=None  # Pas nécessaire pour test sémantique
        )
        
        return candidat
    
    def parse_fdp_content(self, fdp_text: str, filename: str) -> BiDirectionalCompanyProfile:
        """🏢 Parser basique du contenu FDP pour créer un profil entreprise"""
        
        # Extraction compétences requises (mêmes mots-clés)
        competences_requises = []
        keywords_tech = [
            'python', 'java', 'javascript', 'react', 'node', 'angular', 'vue',
            'php', 'sql', 'mysql', 'postgresql', 'mongodb', 'docker', 'kubernetes',
            'aws', 'azure', 'git', 'jenkins', 'linux', 'windows', 'html', 'css',
            'bootstrap', 'jquery', 'typescript', 'c++', 'c#', 'ruby', 'go',
            'comptabilité', 'cegid', 'sage', 'excel', 'powerpoint', 'word',
            'gestion', 'marketing', 'vente', 'commercial', 'rh', 'finance'
        ]
        
        fdp_lower = fdp_text.lower()
        for keyword in keywords_tech:
            if keyword in fdp_lower:
                competences_requises.append(keyword.title())
        
        # Extraction titre de poste (première ligne contenant des mots comme "développeur", "comptable", etc.)
        titre_poste = filename.replace('.pdf', '').replace('.docx', '').replace('.txt', '')
        poste_keywords = ['développeur', 'comptable', 'commercial', 'manager', 'chef', 'responsable', 'analyst']
        
        lines = fdp_text.strip().split('\n')
        for line in lines[:10]:  # Check premières lignes
            line_lower = line.lower()
            for keyword in poste_keywords:
                if keyword in line_lower and len(line.strip()) < 100:  # Pas trop long = probablement titre
                    titre_poste = line.strip()
                    break
        
        # Extraction nom entreprise (cherche patterns)
        nom_entreprise = "Entreprise Test"
        import re
        # Patterns pour entreprises (SA, SARL, SAS, etc.)
        company_patterns = re.findall(r'([A-Z][a-zA-Z\s]+(?:SA|SARL|SAS|EURL|Group|Corp|Inc|Ltd))', fdp_text)
        if company_patterns:
            nom_entreprise = company_patterns[0].strip()
        
        # Création profil entreprise
        entreprise = BiDirectionalCompanyProfile(
            entreprise=InformationsEntreprise(
                nom=nom_entreprise,
                secteur="Technologie",  # Défaut
                localisation="Paris"  # Défaut
            ),
            poste=DescriptionPoste(
                titre=titre_poste,
                localisation="Paris",
                type_contrat=TypeContrat.CDI,
                salaire_min=40000,  # Défaut
                salaire_max=60000,  # Défaut
                competences_requises=competences_requises if competences_requises else ["Compétences générales"]
            ),
            exigences=None,  # Pas nécessaire pour test sémantique
            conditions=None,  # Pas nécessaire pour test sémantique
            recrutement=None  # Pas nécessaire pour test sémantique
        )
        
        return entreprise
    
    async def test_semantic_matching(self, candidat: BiDirectionalCandidateProfile, 
                                   entreprise: BiDirectionalCompanyProfile,
                                   cv_filename: str, fdp_filename: str) -> Dict[str, Any]:
        """🧠 Test matching sémantique entre CV et FDP"""
        
        print(f"\n🧠 === MATCHING SÉMANTIQUE ===")
        print(f"📄 CV: {cv_filename}")
        print(f"📋 FDP: {fdp_filename}")
        print(f"👤 {candidat.personal_info.firstName} {candidat.personal_info.lastName} ({candidat.experience_globale.value})")
        print(f"🏢 {entreprise.entreprise.nom} - {entreprise.poste.titre}")
        
        start_time = time.time()
        
        # Calcul score sémantique
        try:
            semantic_result = self.semantic_scorer.calculate_score(candidat, entreprise)
            calc_time = (time.time() - start_time) * 1000
            
            print(f"\n📊 RÉSULTATS SÉMANTIQUES:")
            print(f"⚡ Temps calcul: {calc_time:.1f}ms")
            print(f"🎯 Score sémantique: {semantic_result.score:.3f}")
            print(f"🧠 Confiance: {semantic_result.confidence:.3f}")
            
            # Détails du matching
            if semantic_result.details:
                print(f"\n🔍 DÉTAILS MATCHING:")
                for key, value in semantic_result.details.items():
                    if isinstance(value, (int, float)):
                        print(f"   • {key}: {value:.3f}")
                    else:
                        print(f"   • {key}: {value}")
            
            # Compétences candidat vs requises
            print(f"\n💼 ANALYSE COMPÉTENCES:")
            candidat_competences = set([c.lower() for c in candidat.competences.competences_techniques])
            requises_competences = set([c.lower() for c in entreprise.poste.competences_requises])
            
            correspondances = candidat_competences.intersection(requises_competences)
            manquantes = requises_competences - candidat_competences
            bonus = candidat_competences - requises_competences
            
            print(f"   ✅ Correspondances ({len(correspondances)}): {', '.join(correspondances) if correspondances else 'Aucune'}")
            print(f"   ❌ Manquantes ({len(manquantes)}): {', '.join(manquantes) if manquantes else 'Aucune'}")
            print(f"   🎁 Bonus candidat ({len(bonus)}): {', '.join(list(bonus)[:5]) if bonus else 'Aucune'}")
            
            # Évaluation globale
            if semantic_result.score >= 0.8:
                evaluation = "🎉 EXCELLENT MATCH"
            elif semantic_result.score >= 0.6:
                evaluation = "✅ BON MATCH"  
            elif semantic_result.score >= 0.4:
                evaluation = "⚠️ MATCH MOYEN"
            else:
                evaluation = "❌ MATCH FAIBLE"
            
            print(f"\n{evaluation}")
            
            return {
                "cv_filename": cv_filename,
                "fdp_filename": fdp_filename,
                "candidat_name": f"{candidat.personal_info.firstName} {candidat.personal_info.lastName}",
                "entreprise_name": entreprise.entreprise.nom,
                "poste_titre": entreprise.poste.titre,
                "semantic_score": semantic_result.score,
                "confidence": semantic_result.confidence,
                "calculation_time_ms": calc_time,
                "correspondances": list(correspondances),
                "manquantes": list(manquantes),
                "bonus": list(bonus),
                "evaluation": evaluation,
                "details": semantic_result.details
            }
            
        except Exception as e:
            print(f"❌ Erreur calcul sémantique: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "cv_filename": cv_filename,
                "fdp_filename": fdp_filename
            }
    
    async def run_full_semantic_test(self):
        """🚀 Test complet matching sémantique tous CV vs toutes FDP"""
        
        # Scanner documents
        documents = self.scan_documents()
        
        if not documents["cv_files"]:
            print("❌ Aucun CV trouvé dans le dossier CV TEST")
            return
        
        if not documents["fdp_files"]:
            print("❌ Aucune FDP trouvée dans le dossier FDP TEST")
            return
        
        # Résultats de tous les matchings
        all_results = []
        
        print(f"\n🧠 === DÉBUT TESTS SÉMANTIQUES ===")
        print(f"📊 {len(documents['cv_files'])} CV × {len(documents['fdp_files'])} FDP = {len(documents['cv_files']) * len(documents['fdp_files'])} matchings")
        
        total_start = time.time()
        
        # Test chaque CV contre chaque FDP
        for cv_file in documents["cv_files"]:
            print(f"\n📄 Traitement CV: {cv_file.name}")
            
            # Extraction contenu CV
            cv_text = self.extract_text_from_file(cv_file)
            candidat = self.parse_cv_content(cv_text, cv_file.name)
            
            for fdp_file in documents["fdp_files"]:
                print(f"   📋 vs FDP: {fdp_file.name}")
                
                # Extraction contenu FDP
                fdp_text = self.extract_text_from_file(fdp_file)
                entreprise = self.parse_fdp_content(fdp_text, fdp_file.name)
                
                # Test matching sémantique
                result = await self.test_semantic_matching(
                    candidat, entreprise, cv_file.name, fdp_file.name
                )
                all_results.append(result)
        
        total_time = (time.time() - total_start) * 1000
        
        # Rapport final
        self.generate_final_report(all_results, total_time)
    
    def generate_final_report(self, results: List[Dict], total_time_ms: float):
        """📊 Génération rapport final des matchings sémantiques"""
        
        print(f"\n" + "="*70)
        print(f"📊 RAPPORT FINAL - MATCHING SÉMANTIQUE")
        print(f"="*70)
        
        successful_results = [r for r in results if "error" not in r]
        failed_results = [r for r in results if "error" in r]
        
        print(f"📈 Statistiques générales:")
        print(f"   🎯 Total matchings: {len(results)}")
        print(f"   ✅ Réussis: {len(successful_results)}")
        print(f"   ❌ Échoués: {len(failed_results)}")
        print(f"   ⏱️ Temps total: {total_time_ms:.0f}ms")
        print(f"   ⚡ Temps moyen: {total_time_ms/len(results):.1f}ms par matching")
        
        if successful_results:
            scores = [r["semantic_score"] for r in successful_results]
            confidences = [r["confidence"] for r in successful_results]
            
            print(f"\n📊 Distribution des scores:")
            print(f"   🎯 Score moyen: {sum(scores)/len(scores):.3f}")
            print(f"   📈 Score max: {max(scores):.3f}")
            print(f"   📉 Score min: {min(scores):.3f}")
            print(f"   🧠 Confiance moyenne: {sum(confidences)/len(confidences):.3f}")
            
            # Top 3 meilleurs matchings
            top_results = sorted(successful_results, key=lambda x: x["semantic_score"], reverse=True)[:3]
            print(f"\n🏆 TOP 3 MEILLEURS MATCHINGS:")
            for i, result in enumerate(top_results, 1):
                print(f"   {i}. {result['candidat_name']} → {result['poste_titre']}")
                print(f"      📊 Score: {result['semantic_score']:.3f} | ✅ Correspondances: {len(result['correspondances'])}")
        
        # Sauvegarde résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"semantic_matching_results_{timestamp}.json"
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Résultats sauvés: {results_file}")
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde: {e}")
        
        print(f"="*70)

async def main():
    """🚀 Point d'entrée principal"""
    
    print("🧠 === TEST MATCHING SÉMANTIQUE CV/FDP RÉELS ===")
    print("📂 Lecture des dossiers CV TEST et FDP TEST sur le bureau")
    print("="*60)
    
    tester = SemanticMatchingTester()
    await tester.run_full_semantic_test()
    
    print(f"\n💡 Notes:")
    print(f"• Assurez-vous d'avoir les dossiers 'CV TEST' et 'FDP TEST' sur votre bureau")
    print(f"• Formats supportés: PDF, DOCX, TXT")
    print(f"• Pour PDF: installer 'pip install PyPDF2'")
    print(f"• Pour DOCX: installer 'pip install python-docx'")

if __name__ == "__main__":
    asyncio.run(main())
