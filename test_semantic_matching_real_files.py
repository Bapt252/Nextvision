#!/usr/bin/env python3
"""
🧠 TEST MATCHING SÉMANTIQUE AVEC CV ET FDP RÉELS (FIXED)
Test spécialisé pour valider le scoring sémantique avec vrais documents

Author: Assistant Claude  
Version: 1.0.1-fixed
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
    PersonalInfoBidirectional, CompetencesProfessionnelles, AttentesCandidat,
    MotivationsCandidat, InformationsEntreprise, DescriptionPoste,
    ExigencesPoste, ConditionsTravail, CriteresRecrutement,
    NiveauExperience, TypeContrat, RaisonEcouteCandidat, UrgenceRecrutement
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
            for cv in documents["cv_files"][:10]:  # Afficher seulement les 10 premiers
                print(f"   • {cv.name}")
            if len(documents["cv_files"]) > 10:
                print(f"   ... et {len(documents['cv_files']) - 10} autres")
        else:
            print(f"⚠️ Dossier CV TEST non trouvé: {self.cv_folder}")
        
        # Scanner dossier FDP TEST  
        if self.fdp_folder.exists():
            for ext in ['*.pdf', '*.docx', '*.doc', '*.txt']:
                documents["fdp_files"].extend(self.fdp_folder.glob(ext))
            print(f"📋 FDP trouvées: {len(documents['fdp_files'])}")
            for fdp in documents["fdp_files"][:10]:  # Afficher seulement les 10 premières
                print(f"   • {fdp.name}")
            if len(documents["fdp_files"]) > 10:
                print(f"   ... et {len(documents['fdp_files']) - 10} autres")
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
                # PDF (avec fallback si PyPDF2 non disponible)
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    # Fallback : utiliser nom fichier comme contenu de base
                    filename_content = file_path.stem.replace('_', ' ').replace('-', ' ')
                    return f"Contenu PDF non extractible - Nom fichier: {filename_content}"
                except Exception as e:
                    return f"Erreur lecture PDF - Nom fichier: {file_path.stem}"
            
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                # Documents Word (avec fallback si python-docx non disponible)
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    # Fallback : utiliser nom fichier comme contenu de base
                    filename_content = file_path.stem.replace('_', ' ').replace('-', ' ')
                    return f"Contenu DOCX non extractible - Nom fichier: {filename_content}"
                except Exception as e:
                    return f"Erreur lecture DOCX - Nom fichier: {file_path.stem}"
            
            else:
                return f"Format non supporté - Nom fichier: {file_path.stem}"
                
        except Exception as e:
            print(f"❌ Erreur extraction {file_path.name}: {e}")
            return f"Erreur extraction - Nom fichier: {file_path.stem}"
    
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
            'gestion', 'marketing', 'vente', 'commercial', 'rh', 'finance',
            'comptable', 'facturation', 'paie', 'fiscal', 'juridique'
        ]
        
        cv_lower = cv_text.lower()
        for keyword in keywords_tech:
            if keyword in cv_lower:
                competences_techniques.append(keyword.title())
        
        # Extraction nom depuis le nom de fichier
        filename_clean = filename.replace('.pdf', '').replace('.docx', '').replace('.txt', '')
        parts = filename_clean.replace('_', ' ').replace('-', ' ').split()
        
        first_name = parts[0] if parts else "Candidat"
        last_name = parts[1] if len(parts) > 1 else "Test"
        
        # Si le nom commence par "CV", prendre les suivants
        if first_name.upper() == "CV" and len(parts) > 2:
            first_name = parts[1]
            last_name = parts[2] if len(parts) > 2 else "Test"
        
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
        
        # Création profil candidat (FIXÉ: avec objets valides au lieu de None)
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
            # FIXÉ: Objets par défaut au lieu de None
            attentes=AttentesCandidat(
                salaire_min=35000,
                salaire_max=50000,
                localisation_preferee="Paris",
                distance_max_km=30,
                remote_accepte=True
            ),
            motivations=MotivationsCandidat(
                raison_ecoute=RaisonEcouteCandidat.MANQUE_PERSPECTIVES,
                motivations_principales=["Test sémantique"]
            )
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
            'gestion', 'marketing', 'vente', 'commercial', 'rh', 'finance',
            'comptable', 'facturation', 'paie', 'fiscal', 'juridique'
        ]
        
        fdp_lower = fdp_text.lower()
        for keyword in keywords_tech:
            if keyword in fdp_lower:
                competences_requises.append(keyword.title())
        
        # Extraction titre de poste depuis le nom de fichier
        filename_clean = filename.replace('.pdf', '').replace('.docx', '').replace('.txt', '')
        titre_poste = filename_clean.replace('_', ' ').replace('-', ' ')
        
        # Extraction nom entreprise (cherche patterns)
        nom_entreprise = "Entreprise Test"
        import re
        # Patterns pour entreprises (SA, SARL, SAS, etc.)
        company_patterns = re.findall(r'([A-Z][a-zA-Z\s]+(?:SA|SARL|SAS|EURL|Group|Corp|Inc|Ltd))', fdp_text)
        if company_patterns:
            nom_entreprise = company_patterns[0].strip()
        elif "bcom" in fdp_text.lower():
            nom_entreprise = "Bcom HR"
        
        # Création profil entreprise (FIXÉ: avec objets valides au lieu de None)
        entreprise = BiDirectionalCompanyProfile(
            entreprise=InformationsEntreprise(
                nom=nom_entreprise,
                secteur="Services" if "comptable" in fdp_lower else "Technologie",
                localisation="Paris"
            ),
            poste=DescriptionPoste(
                titre=titre_poste,
                localisation="Paris",
                type_contrat=TypeContrat.CDI,
                salaire_min=40000,
                salaire_max=60000,
                competences_requises=competences_requises if competences_requises else ["Compétences générales"]
            ),
            # FIXÉ: Objets par défaut au lieu de None
            exigences=ExigencesPoste(
                experience_requise="2-5 ans",
                competences_obligatoires=competences_requises[:3] if len(competences_requises) > 3 else competences_requises,
                competences_souhaitees=competences_requises[3:] if len(competences_requises) > 3 else []
            ),
            conditions=ConditionsTravail(
                remote_possible=True,
                avantages=["Mutuelle", "Tickets restaurant"]
            ),
            recrutement=CriteresRecrutement(
                urgence=UrgenceRecrutement.NORMAL,
                criteres_prioritaires=["competences"]
            )
        )
        
        return entreprise
    
    async def test_semantic_matching(self, candidat: BiDirectionalCandidateProfile, 
                                   entreprise: BiDirectionalCompanyProfile,
                                   cv_filename: str, fdp_filename: str) -> Dict[str, Any]:
        """🧠 Test matching sémantique entre CV et FDP"""
        
        start_time = time.time()
        
        # Calcul score sémantique
        try:
            semantic_result = self.semantic_scorer.calculate_score(candidat, entreprise)
            calc_time = (time.time() - start_time) * 1000
            
            # Compétences candidat vs requises
            candidat_competences = set([c.lower() for c in candidat.competences.competences_techniques])
            requises_competences = set([c.lower() for c in entreprise.poste.competences_requises])
            
            correspondances = candidat_competences.intersection(requises_competences)
            manquantes = requises_competences - candidat_competences
            bonus = candidat_competences - requises_competences
            
            # Évaluation globale
            if semantic_result.score >= 0.8:
                evaluation = "🎉 EXCELLENT MATCH"
            elif semantic_result.score >= 0.6:
                evaluation = "✅ BON MATCH"  
            elif semantic_result.score >= 0.4:
                evaluation = "⚠️ MATCH MOYEN"
            else:
                evaluation = "❌ MATCH FAIBLE"
            
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
            print(f"❌ Erreur calcul sémantique {cv_filename} vs {fdp_filename}: {e}")
            return {
                "error": str(e),
                "cv_filename": cv_filename,
                "fdp_filename": fdp_filename
            }
    
    async def run_semantic_test_sample(self, max_cv: int = 5, max_fdp: int = 5):
        """🚀 Test sémantique échantillon (pour éviter 2346 matchings)"""
        
        # Scanner documents
        documents = self.scan_documents()
        
        if not documents["cv_files"]:
            print("❌ Aucun CV trouvé dans le dossier CV TEST")
            return
        
        if not documents["fdp_files"]:
            print("❌ Aucune FDP trouvée dans le dossier FDP TEST")
            return
        
        # Prendre échantillon
        cv_sample = documents["cv_files"][:max_cv]
        fdp_sample = documents["fdp_files"][:max_fdp]
        
        print(f"\n🧠 === TESTS SÉMANTIQUES ÉCHANTILLON ===")
        print(f"📊 {len(cv_sample)} CV × {len(fdp_sample)} FDP = {len(cv_sample) * len(fdp_sample)} matchings")
        
        # Résultats de tous les matchings
        all_results = []
        total_start = time.time()
        
        # Test chaque CV contre chaque FDP
        for i, cv_file in enumerate(cv_sample, 1):
            print(f"\n📄 [{i}/{len(cv_sample)}] CV: {cv_file.name}")
            
            # Extraction contenu CV
            cv_text = self.extract_text_from_file(cv_file)
            candidat = self.parse_cv_content(cv_text, cv_file.name)
            
            for j, fdp_file in enumerate(fdp_sample, 1):
                print(f"   📋 [{j}/{len(fdp_sample)}] vs FDP: {fdp_file.name[:50]}...")
                
                # Extraction contenu FDP
                fdp_text = self.extract_text_from_file(fdp_file)
                entreprise = self.parse_fdp_content(fdp_text, fdp_file.name)
                
                # Test matching sémantique
                result = await self.test_semantic_matching(
                    candidat, entreprise, cv_file.name, fdp_file.name
                )
                all_results.append(result)
                
                # Affichage rapide du résultat
                if "error" not in result:
                    print(f"      🎯 Score: {result['semantic_score']:.3f} | ✅ Correspondances: {len(result['correspondances'])}")
        
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
        if len(results) > 0:
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
                print(f"   {i}. {result['candidat_name']} → {result['poste_titre'][:50]}...")
                print(f"      📊 Score: {result['semantic_score']:.3f} | ✅ Correspondances: {len(result['correspondances'])}")
                if result['correspondances']:
                    print(f"      🔗 Compétences communes: {', '.join(list(result['correspondances'])[:5])}")
        
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
    
    # Test échantillon (5 CV × 5 FDP = 25 matchings)
    await tester.run_semantic_test_sample(max_cv=5, max_fdp=5)
    
    print(f"\n💡 Notes:")
    print(f"• Test effectué sur échantillon (5×5) pour éviter 2346 matchings")
    print(f"• Pour installer PDF/DOCX: pip install PyPDF2 python-docx")
    print(f"• Modifiez max_cv et max_fdp pour tester plus de fichiers")

if __name__ == "__main__":
    asyncio.run(main())
