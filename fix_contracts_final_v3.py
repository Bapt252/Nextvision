#!/usr/bin/env python3
"""
🔧 Correction finale types de contrats français V3.0 - SANS STAGE
"""

# Lire le fichier des modèles
with open('nextvision/models/extended_matching_models_v3.py', 'r') as f:
    content = f.read()

# Définir la classe ContractType correcte
correct_contract_enum = '''class ContractType(Enum):
    """Types de contrats français (questionnaire)"""
    CDI = "cdi"
    CDD = "cdd"
    FREELANCE = "freelance"
    INTERIM = "interim"'''

# Remplacer toutes les variantes existantes
import re

# Supprimer anciennes définitions ContractType/ContractPreference
patterns_to_remove = [
    r'class ContractType\(Enum\):.*?(?=class|\Z)',
    r'class ContractPreference\(Enum\):.*?(?=class|\Z)',
]

for pattern in patterns_to_remove:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Insérer la bonne définition après TransportMethod
insertion_point = content.find('class WorkModalityType(Enum):')
if insertion_point != -1:
    content = content[:insertion_point] + correct_contract_enum + '\n\n' + content[insertion_point:]
else:
    # Sinon insérer après TransportMethod
    insertion_point = content.find('class MotivationType(Enum):')
    if insertion_point != -1:
        content = content[:insertion_point] + correct_contract_enum + '\n\n' + content[insertion_point:]

# Supprimer références à STAGE
content = content.replace('STAGE = "stage"', '')
content = content.replace(', STAGE', '')
content = content.replace('STAGE, ', '')

# Nettoyer lignes vides multiples
content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

# Sauvegarder
with open('nextvision/models/extended_matching_models_v3.py', 'w') as f:
    f.write(content)

print("✅ Types de contrats français corrigés (sans STAGE)!")
print("🇫🇷 CDI, CDD, FREELANCE, INTERIM opérationnels")
