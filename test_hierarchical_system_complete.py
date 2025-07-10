"""
🧪 Test du Système Hiérarchique Nextvision V3.1
Valide la résolution du problème Charlotte DARMON (DAF vs postes comptables)

Author: Assistant Claude
Version: 1.0.1  
Date: 2025-07-10
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Import du nouveau système hiérarchique
from nextvision.services.hierarchical_detector import HierarchicalDetector, HierarchicalScoring
from nextvision.services.enhanced_commitment_bridge_v3_hierarchical import (
    EnhancedCommitmentBridgeV3Hierarchical, HierarchicalBridgeFactory
)

class HierarchicalSystemTester:
    """🧪 Testeur complet du système hiérarchique"""
    
    def __init__(self):
        self.detector = HierarchicalDetector()
        self.scorer = HierarchicalScoring()
        self.bridge = HierarchicalBridgeFactory.create_hierarchical_bridge()
        self.results = {}
    
    async def run_complete_test(self) -> Dict[str, Any]:
        """🚀 Lance tous les tests du système hiérarchique"""
        
        print("=" * 80)
        print("🧪 TEST SYSTÈME HIÉRARCHIQUE NEXTVISION V3.1")
        print("=" * 80)
        print("🎯 OBJECTIF : Valider résolution problème Charlotte DARMON")
        print()
        
        start_time = datetime.now()
        
        # 1. Test détection hiérarchique
        print("📋 1. TEST DÉTECTION HIÉRARCHIQUE")
        print("-" * 50)
        detection_results = await self.test_hierarchical_detection()
        
        # 2. Test scoring hiérarchique
        print("\n📊 2. TEST SCORING HIÉRARCHIQUE")
        print("-" * 50)
        scoring_results = await self.test_hierarchical_scoring()
        
        # 3. Test intégration bridge
        print("\n🌉 3. TEST INTÉGRATION BRIDGE V3.1")
        print("-" * 50)
        bridge_results = await self.test_bridge_integration()
        
        # 4. Test cas réels
        print("\n🎯 4. TEST CAS RÉELS (Charlotte DARMON)")
        print("-" * 50)
        real_case_results = await self.test_real_cases()
        
        # 5. Analyse performance
        print("\n⚡ 5. ANALYSE PERFORMANCES")
        print("-" * 50)
        performance_results = await self.test_performance()
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Compilation des résultats
        final_results = {
            'test_summary': {
                'total_duration_seconds': total_time,
                'timestamp': datetime.now().isoformat(),
                'version': '3.1.0',
                'tests_passed': 0,
                'tests_failed': 0
            },
            'detection_tests': detection_results,
            'scoring_tests': scoring_results,
            'bridge_tests': bridge_results,
            'real_case_tests': real_case_results,
            'performance_tests': performance_results
        }
        
        # Calcul succès global
        all_tests = [detection_results, scoring_results, bridge_results, real_case_results, performance_results]
        passed_tests = sum(1 for test in all_tests if test.get('success', False))
        failed_tests = len(all_tests) - passed_tests
        
        final_results['test_summary']['tests_passed'] = passed_tests
        final_results['test_summary']['tests_failed'] = failed_tests
        
        # Affichage résumé final
        self._print_final_summary(final_results)
        
        return final_results
    
    async def test_hierarchical_detection(self) -> Dict[str, Any]:
        """📋 Test de la détection de niveaux hiérarchiques"""
        
        test_cases = {
            'charlotte_daf': {
                'text': """
                Charlotte DARMON
                Directrice Administrative et Financière (DAF)
                15 ans d'expérience en direction financière
                
                Expérience professionnelle:
                - DAF Groupe ABC (2019-2024): Pilotage stratégique, management équipe de 12 personnes, 
                  reporting conseil d'administration, budget consolidé 50M€, politique financière groupe
                - Directrice Financière DEF (2015-2019): Supervision équipe comptable, contrôle budgétaire
                
                Compétences: CEGID, SAGE, Excel avancé, Consolidation, Management
                Rémunération souhaitée: 75-85K€
                """,
                'expected_level': 'EXECUTIVE',
                'expected_confidence_min': 0.7
            },
            'comptable_general': {
                'text': """
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
                """,
                'expected_level': 'JUNIOR',
                'expected_confidence_min': 0.6
            },
            'responsable_comptable': {
                'text': """
                Poste: Responsable Comptable H/F  
                
                Mission:
                - Supervision équipe comptable (3 personnes)
                - Validation des écritures complexes
                - Reporting mensuel direction
                - Optimisation processus comptables
                - Formation et encadrement équipe
                
                Profil recherché:
                - Formation supérieure en comptabilité/finance
                - 8-12 ans d'expérience dont 3 ans encadrement
                - Leadership et pédagogie
                
                Salaire: 55-65K€
                """,
                'expected_level': 'MANAGER',
                'expected_confidence_min': 0.7
            }
        }
        
        results = {'success': True, 'details': {}}
        
        for case_name, case_data in test_cases.items():
            try:
                analysis = self.detector.detect_hierarchical_level(
                    case_data['text'], 
                    is_job_posting=('poste:' in case_data['text'].lower())
                )
                
                success = (
                    analysis.detected_level.name == case_data['expected_level'] and
                    analysis.confidence_score >= case_data['expected_confidence_min']
                )
                
                results['details'][case_name] = {
                    'detected_level': analysis.detected_level.name,
                    'expected_level': case_data['expected_level'],
                    'confidence_score': analysis.confidence_score,
                    'expected_confidence_min': case_data['expected_confidence_min'],
                    'years_experience': analysis.years_experience,
                    'salary_range': analysis.salary_range,
                    'management_indicators': analysis.management_indicators,
                    'success': success
                }
                
                if success:
                    print(f"✅ {case_name}: {analysis.detected_level.name} (confiance {analysis.confidence_score:.3f})")
                else:
                    print(f"❌ {case_name}: Attendu {case_data['expected_level']}, obtenu {analysis.detected_level.name}")
                    results['success'] = False
                
            except Exception as e:
                print(f"❌ Erreur {case_name}: {e}")
                results['success'] = False
                results['details'][case_name] = {'error': str(e), 'success': False}
        
        return results
    
    async def test_hierarchical_scoring(self) -> Dict[str, Any]:
        """📊 Test du scoring hiérarchique"""
        
        # Cas Charlotte DARMON vs différents postes
        charlotte_cv = """
        Charlotte DARMON - Directrice Administrative et Financière (DAF)
        15 ans d'expérience en direction financière
        DAF Groupe ABC: Pilotage stratégique, management équipe de 12 personnes
        Compétences: CEGID, SAGE, Excel avancé, Consolidation, Management
        Rémunération souhaitée: 75-85K€
        """
        
        test_matchings = {
            'charlotte_vs_comptable': {
                'candidate': charlotte_cv,
                'job': """
                Poste: Comptable Général H/F
                Saisie comptable quotidienne, rapprochements bancaires
                2-5 ans d'expérience, pas de management d'équipe
                Salaire: 32-38K€
                """,
                'expected_score_max': 0.4,  # Doit être faible
                'expected_compatibility': 'Incompatible'
            },
            'charlotte_vs_responsable': {
                'candidate': charlotte_cv,
                'job': """
                Poste: Responsable Comptable H/F
                Supervision équipe comptable (3 personnes)
                8-12 ans d'expérience dont 3 ans encadrement
                Salaire: 55-65K€
                """,
                'expected_score_min': 0.6,  # Doit être acceptable
                'expected_compatibility': 'Match acceptable'
            }
        }
        
        results = {'success': True, 'details': {}}
        
        for case_name, case_data in test_matchings.items():
            try:
                analysis = self.scorer.calculate_hierarchical_score(
                    case_data['candidate'],
                    case_data['job']
                )
                
                score = analysis['hierarchical_score']
                compatibility = analysis['compatibility_level']
                
                # Validation des attentes
                score_ok = True
                if 'expected_score_max' in case_data:
                    score_ok = score <= case_data['expected_score_max']
                elif 'expected_score_min' in case_data:
                    score_ok = score >= case_data['expected_score_min']
                
                compatibility_ok = case_data['expected_compatibility'].lower() in compatibility.lower()
                
                success = score_ok and compatibility_ok
                
                results['details'][case_name] = {
                    'hierarchical_score': score,
                    'compatibility_level': compatibility,
                    'candidate_level': analysis['candidate_level'],
                    'job_level': analysis['job_level'],
                    'salary_warning': analysis.get('salary_warning'),
                    'success': success
                }
                
                if success:
                    print(f"✅ {case_name}: Score {score:.3f}, Compatibilité '{compatibility}'")
                else:
                    print(f"❌ {case_name}: Score {score:.3f} (attendu {'≤' + str(case_data.get('expected_score_max', 'N/A')) if 'expected_score_max' in case_data else '≥' + str(case_data.get('expected_score_min', 'N/A'))})")
                    results['success'] = False
                
            except Exception as e:
                print(f"❌ Erreur {case_name}: {e}")
                results['success'] = False
                results['details'][case_name] = {'error': str(e), 'success': False}
        
        return results
    
    async def test_bridge_integration(self) -> Dict[str, Any]:
        """🌉 Test de l'intégration dans le bridge V3.1"""
        
        # Données de test Charlotte DARMON
        charlotte_data = {
            'name': 'Charlotte DARMON',
            'parsed_content': """
            Directrice Administrative et Financière (DAF)
            15 ans d'expérience en direction financière
            DAF Groupe ABC: Pilotage stratégique, management équipe de 12 personnes
            Compétences: CEGID, SAGE, Excel avancé, Consolidation, Management
            Rémunération souhaitée: 75-85K€
            """,
            'skills': ['CEGID', 'SAGE', 'Excel', 'Consolidation', 'Management'],
            'salary': {'expected': 80000},
            'experience': {'total_years': 15},
            'location': {'city': 'Paris'}
        }
        
        # Poste comptable général (problématique)
        comptable_job = {
            'title': 'Comptable Général H/F',
            'parsed_content': """
            Saisie comptable quotidienne, rapprochements bancaires
            Déclarations TVA mensuelles, assistance bilan annuel
            Formation comptable (BTS/DUT), 2-5 ans d'expérience
            Pas de management d'équipe
            """,
            'competences_requises': ['Comptabilité', 'TVA', 'Bilan'],
            'salary_range': (32000, 38000),
            'experience_requise': '2-5 ans',
            'localisation': 'Paris'
        }
        
        try:
            # Test du matching hiérarchique
            result = await self.bridge.enhanced_matching_with_hierarchy(charlotte_data, comptable_job)
            
            # Validations
            total_score = result['total_score']
            hierarchical_score = result['components']['hierarchical']
            compatibility = result['compatibility']
            alerts = result['alerts']
            
            # Le système doit détecter l'inadéquation
            success = (
                total_score < 0.6 and  # Score total dégradé
                hierarchical_score < 0.4 and  # Score hiérarchique faible
                any(alert['type'] == 'CRITICAL_MISMATCH' for alert in alerts) and  # Alerte critique
                compatibility in ['poor', 'average']  # Compatibilité dégradée
            )
            
            results = {
                'success': success,
                'total_score': total_score,
                'hierarchical_score': hierarchical_score,
                'compatibility': compatibility,
                'alerts_count': len(alerts),
                'critical_alerts': [alert for alert in alerts if alert['type'] == 'CRITICAL_MISMATCH'],
                'processing_time': result['processing_time'],
                'version': result['version']
            }
            
            if success:
                print(f"✅ Bridge V3.1: Score {total_score:.3f}, Hiérarchie {hierarchical_score:.3f}")
                print(f"   Compatibilité: {compatibility}")
                print(f"   Alertes: {len(alerts)} (dont {len(results['critical_alerts'])} critiques)")
            else:
                print(f"❌ Bridge V3.1: Inadéquation non détectée")
                print(f"   Score: {total_score:.3f}, Hiérarchie: {hierarchical_score:.3f}")
                print(f"   Compatibilité: {compatibility}")
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur bridge integration: {e}")
            return {'success': False, 'error': str(e)}
    
    async def test_real_cases(self) -> Dict[str, Any]:
        """🎯 Test avec des cas réels"""
        
        print("🔍 Test comparatif AVANT/APRÈS système hiérarchique")
        
        # Simulation scores AVANT (système V3.0)
        before_scores = {
            'charlotte_comptable': {
                'semantic': 0.85,  # Excellentes compétences
                'salary': 0.1,     # Très mauvais (85K vs 38K)
                'experience': 0.9, # Excellente expérience
                'location': 0.8,   # Bonne localisation
                'total_v30': 0.85 * 0.35 + 0.1 * 0.25 + 0.9 * 0.25 + 0.8 * 0.15  # = 0.645
            }
        }
        
        # Scores APRÈS (système V3.1)
        charlotte_data = {
            'parsed_content': """
            Charlotte DARMON - Directrice Administrative et Financière (DAF)
            15 ans d'expérience, pilotage stratégique, management équipe 12 personnes
            """,
            'skills': ['CEGID', 'SAGE', 'Comptabilité'],
            'salary': {'expected': 85000},
            'experience': {'total_years': 15},
            'location': {'city': 'Paris'}
        }
        
        comptable_job = {
            'parsed_content': """
            Comptable Général - Saisie comptable, 2-5 ans expérience
            Pas de management, salaire 32-38K€
            """,
            'competences_requises': ['Comptabilité', 'Saisie'],
            'salary_range': (32000, 38000),
            'experience_requise': '2-5 ans',
            'localisation': 'Paris'
        }
        
        try:
            result_after = await self.bridge.enhanced_matching_with_hierarchy(charlotte_data, comptable_job)
            
            score_v30 = before_scores['charlotte_comptable']['total_v30']
            score_v31 = result_after['total_score']
            improvement = score_v30 - score_v31
            
            # Le système doit montrer une amélioration (score dégradé pour filtrerer l'inadéquation)
            success = score_v31 < score_v30 and improvement > 0.1
            
            results = {
                'success': success,
                'score_before_v30': score_v30,
                'score_after_v31': score_v31,
                'improvement': improvement,
                'hierarchical_score': result_after['components']['hierarchical'],
                'compatibility_before': 'good' if score_v30 >= 0.6 else 'poor',
                'compatibility_after': result_after['compatibility'],
                'alerts_generated': len(result_after['alerts'])
            }
            
            print(f"📊 Score AVANT V3.0: {score_v30:.3f} ({'✅ Acceptable' if score_v30 >= 0.6 else '❌ Rejeté'})")
            print(f"📊 Score APRÈS V3.1: {score_v31:.3f} ({'✅ Acceptable' if score_v31 >= 0.6 else '❌ Rejeté'})")
            
            # Correction de la ligne problématique
            improvement_status = "✅ Filtrage réussi" if improvement > 0.1 else "❌ Pas d'amélioration"
            print(f"📈 Amélioration: {improvement:.3f} ({improvement_status})")
            
            if success:
                print("✅ Le système hiérarchique filtre correctement l'inadéquation Charlotte DARMON")
            else:
                print("❌ Le système hiérarchique ne filtre pas suffisamment l'inadéquation")
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur test cas réels: {e}")
            return {'success': False, 'error': str(e)}
    
    async def test_performance(self) -> Dict[str, Any]:
        """⚡ Test de performance du système"""
        
        # Test sur plusieurs échantillons
        sample_data = [
            {
                'candidate': {'parsed_content': 'Comptable senior 5 ans expérience', 'skills': ['Comptabilité']},
                'job': {'parsed_content': 'Poste comptable junior 2 ans', 'competences_requises': ['Comptabilité']}
            },
            {
                'candidate': {'parsed_content': 'Directeur financier 10 ans management', 'skills': ['Finance', 'Management']},
                'job': {'parsed_content': 'DAF groupe international', 'competences_requises': ['Finance', 'Leadership']}
            },
            {
                'candidate': {'parsed_content': 'Assistant comptable débutant', 'skills': ['Saisie']},
                'job': {'parsed_content': 'Stage comptabilité', 'competences_requises': ['Formation']}
            }
        ]
        
        try:
            times = []
            
            for i, data in enumerate(sample_data):
                start_time = datetime.now()
                result = await self.bridge.enhanced_matching_with_hierarchy(data['candidate'], data['job'])
                end_time = datetime.now()
                
                processing_time = (end_time - start_time).total_seconds() * 1000
                times.append(processing_time)
                
                print(f"⚡ Test {i+1}: {processing_time:.1f}ms (score: {result['total_score']:.3f})")
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            # Performance acceptable si < 50ms en moyenne
            success = avg_time < 50.0
            
            results = {
                'success': success,
                'average_time_ms': avg_time,
                'max_time_ms': max_time,
                'min_time_ms': min_time,
                'samples_tested': len(sample_data),
                'performance_target_ms': 50.0
            }
            
            print(f"📊 Temps moyen: {avg_time:.1f}ms (objectif: <50ms)")
            print(f"📊 Temps max: {max_time:.1f}ms, min: {min_time:.1f}ms")
            
            if success:
                print("✅ Performance acceptable pour production")
            else:
                print("⚠️ Performance à optimiser")
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur test performance: {e}")
            return {'success': False, 'error': str(e)}
    
    def _print_final_summary(self, results: Dict[str, Any]):
        """📋 Affiche le résumé final des tests"""
        
        print("\n" + "=" * 80)
        print("📋 RÉSUMÉ FINAL DES TESTS")
        print("=" * 80)
        
        summary = results['test_summary']
        passed = summary['tests_passed']
        failed = summary['tests_failed']
        total = passed + failed
        
        print(f"✅ Tests réussis: {passed}/{total}")
        print(f"❌ Tests échoués: {failed}/{total}")
        print(f"⏱️  Durée totale: {summary['total_duration_seconds']:.2f}s")
        print(f"📅 Version testée: {summary['version']}")
        
        if failed == 0:
            print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
            print("✅ Le système hiérarchique est prêt pour la production")
        else:
            print(f"\n⚠️  {failed} test(s) ont échoué")
            print("❌ Corrections nécessaires avant mise en production")
        
        # Sauvegarde des résultats
        filename = f"test_hierarchical_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Résultats sauvegardés dans: {filename}")

async def main():
    """🚀 Point d'entrée principal"""
    
    tester = HierarchicalSystemTester()
    results = await tester.run_complete_test()
    
    return results

if __name__ == "__main__":
    # Lancement des tests
    results = asyncio.run(main())
