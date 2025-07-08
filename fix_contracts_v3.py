#!/usr/bin/env python3
"""
🔧 Correction types de contrats français V3.0
"""

# Lire le fichier des modèles
with open('nextvision/models/extended_matching_models_v3.py', 'r') as f:
    content = f.read()

# Corrections
corrections = [
    ('INTERNSHIP = "internship"', 'INTERIM = "interim"'),
    ('STAGE = "stage"', 'STAGE = "stage"'),  # Gardé si présent
    ('ContractPreference', 'ContractType'),  # Renommage plus logique
]

for old, new in corrections:
    content = content.replace(old, new)

# Ajouter la classe manquante si pas présente
if 'class ContractType(Enum):' not in content:
    contract_enum = '''
class ContractType(Enum):
    """Types de contrats français"""
    CDI = "cdi"
    CDD = "cdd"
    FREELANCE = "freelance"
    INTERIM = "interim"
    STAGE = "stage"
'''
    
    # Insérer après TransportMethod
    content = content.replace(
        'class ContractPreference(Enum):',
        contract_enum + '\nclass ContractPreference(Enum):'
    )

# Sauvegarder
with open('nextvision/models/extended_matching_models_v3.py', 'w') as f:
    f.write(content)

print("✅ Types de contrats français corrigés!")
