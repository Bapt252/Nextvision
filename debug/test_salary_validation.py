#!/usr/bin/env python3
"""
Test de validation des salaires - CV Parser GPT v4.0.3
======================================================

Script de test pour vérifier que la correction des salaires fonctionne
avec tous les cas de figure possibles.

Usage: python debug/test_salary_validation.py
"""

import sys
import os
import re
from typing import Any, Optional

# Ajout du chemin parent pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _safe_int_conversion(value: Any, field_name: str = "") -> Optional[int]:
    """
    Version identique à celle du CV Parser pour les tests
    """
    if value is None:
        print(f"  🔍 Champ {field_name}: valeur None")
        return None
        
    if isinstance(value, int):
        return value
        
    if isinstance(value, float):
        return int(value)
        
    if isinstance(value, str):
        # Cas spéciaux pour les valeurs non numériques
        value_lower = value.lower().strip()
        non_numeric_indicators = [
            'non mentionné', 'non mentionnÉ', 'non mentione',
            'n/a', 'na', 'néant', 'neant', 
            'inconnu', 'non spécifié', 'non specifie',
            'à définir', 'a definir', 'à négocier', 'a negocier',
            'selon profil', 'variable', 'confidentiel', '',
            'non renseigné', 'non renseigne'
        ]
        
        if value_lower in non_numeric_indicators:
            print(f"  🔍 Champ {field_name}: valeur non numérique détectée: '{value}'")
            return None
        
        # Tentative d'extraction numérique
        # Supprimer espaces, €, K, k, etc.
        cleaned = re.sub(r'[^\d]', '', value)
        if cleaned:
            try:
                num_value = int(cleaned)
                # Gestion des abréviations K (milliers)
                if 'k' in value_lower or '€k' in value_lower:
                    num_value *= 1000
                print(f"  🔍 Champ {field_name}: '{value}' converti en {num_value}")
                return num_value
            except ValueError:
                pass
        
        print(f"  🔍 Champ {field_name}: impossible de convertir '{value}' en entier")
        return None
    
    print(f"  🔍 Champ {field_name}: type non supporté {type(value)}")
    return None


def test_salary_validation():
    """
    Tests complets de validation des salaires
    """
    print("🧪 TEST DE VALIDATION DES SALAIRES - CV PARSER V4.0.3")
    print("=" * 60)
    
    test_cases = [
        # Cas numériques valides
        ("45000", "Salaire numérique normal"),
        (45000, "Entier direct"),
        (45000.0, "Float"),
        ("55K€", "Format avec K"),
        ("60k", "Format k minuscule"),
        ("70 000 €", "Avec espaces et €"),
        ("80,000", "Avec virgule"),
        
        # Cas non numériques
        ("Non mentionné", "Non mentionné standard"),
        ("non mentionné", "non mentionné minuscule"),
        ("Non mentionnÉ", "Avec accent"),
        ("N/A", "N/A"),
        ("n/a", "n/a minuscule"),
        ("", "Chaîne vide"),
        (None, "Valeur None"),
        ("Néant", "Néant"),
        ("Inconnu", "Inconnu"),
        ("À négocier", "À négocier"),
        ("Variable", "Variable"),
        ("Confidentiel", "Confidentiel"),
        
        # Cas limites
        ("0", "Zéro"),
        ("abc123def", "Texte avec chiffres"),
        ("123abc", "Chiffres avec texte"),
        ("€€€", "Symboles uniquement")
    ]
    
    results = {"success": 0, "expected_none": 0, "total": 0}
    
    for i, (value, description) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. {description:<25} | Valeur: {repr(value)}")
        
        try:
            result = _safe_int_conversion(value, f"test_{i}")
            
            # Vérification des résultats attendus
            if isinstance(value, (int, float)) and value != 0:
                expected = "number"
            elif isinstance(value, str) and any(char.isdigit() for char in value):
                # Contient des chiffres - peut être converti
                if any(indicator in value.lower() for indicator in ['non', 'n/a', 'inconnu', 'néant']):
                    expected = "none"
                else:
                    expected = "number"
            else:
                expected = "none"
            
            if result is not None:
                print(f"     ✅ Résultat: {result}€")
                if expected == "number":
                    results["success"] += 1
                else:
                    print(f"     ⚠️  Attendu None mais reçu {result}")
            else:
                print(f"     ❌ Résultat: None")
                if expected == "none":
                    results["expected_none"] += 1
                else:
                    print(f"     ⚠️  Attendu un nombre mais reçu None")
                    
        except Exception as e:
            print(f"     💥 ERREUR: {str(e)}")
        
        results["total"] += 1
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print(f"Total des tests: {results['total']}")
    print(f"Conversions réussies: {results['success']}")
    print(f"None attendus: {results['expected_none']}")
    print(f"Taux de réussite: {((results['success'] + results['expected_none']) / results['total'] * 100):.1f}%")
    
    # Test d'intégration avec données GPT simulées
    print("\n" + "=" * 60)
    print("🤖 TEST D'INTÉGRATION - SIMULATION RÉPONSE GPT")
    
    gpt_responses = [
        {
            "nom_complet": "Marie Martin",
            "salaire_actuel": "Non mentionné", 
            "salaire_souhaite": "45000"
        },
        {
            "nom_complet": "Jean Dupont",
            "salaire_actuel": "55K€", 
            "salaire_souhaite": "60K€"
        },
        {
            "nom_complet": "Sophie Bernard",
            "salaire_actuel": 48000, 
            "salaire_souhaite": "N/A"
        }
    ]
    
    for i, response in enumerate(gpt_responses, 1):
        print(f"\nCandidat {i}: {response['nom_complet']}")
        
        salaire_actuel = _safe_int_conversion(response['salaire_actuel'], "salaire_actuel")
        salaire_souhaite = _safe_int_conversion(response['salaire_souhaite'], "salaire_souhaite")
        
        print(f"  Actuel: {salaire_actuel}€ | Souhaité: {salaire_souhaite}€")
        
        # Simulation de la logique du parser
        if salaire_actuel is not None and salaire_souhaite is not None:
            print("  ✅ Les deux salaires disponibles")
        elif salaire_actuel is not None:
            estimated_souhaite = int(salaire_actuel * 1.15)
            print(f"  🔄 Salaire souhaité estimé: {estimated_souhaite}€ (+15%)")
        elif salaire_souhaite is not None:
            estimated_actuel = int(salaire_souhaite * 0.85)
            print(f"  🔄 Salaire actuel estimé: {estimated_actuel}€ (-15%)")
        else:
            print("  🔄 Estimation complète nécessaire basée sur niveau/secteur")


if __name__ == "__main__":
    test_salary_validation()
