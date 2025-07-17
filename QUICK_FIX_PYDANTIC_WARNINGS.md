# 🚀 Nextvision V3.0 - Correction Rapide Warnings Pydantic

## 🎯 Correction Immédiate - nextvision/models/questionnaire_advanced.py

Les warnings Pydantic V1 peuvent être corrigés rapidement en modifiant le fichier :
`nextvision/models/questionnaire_advanced.py`

### Changements à effectuer :

#### 1. Imports (en haut du fichier) :
```python
# Remplacer cette ligne :
from pydantic import BaseModel, Field, validator

# Par :
from pydantic import BaseModel, Field, field_validator
```

#### 2. Conversions @validator → @field_validator :

**Ligne ~71** :
```python
# Avant :
@validator('preavis')
def validate_preavis(cls, v):

# Après :
@field_validator('preavis')
@classmethod
def validate_preavis(cls, v):
```

**Ligne ~83** :
```python
# Avant :
@validator('preferes', 'redhibitoires')
def validate_lists(cls, v):

# Après :
@field_validator('preferes', 'redhibitoires')
@classmethod
def validate_lists(cls, v):
```

**Ligne ~96** :
```python
# Avant :
@validator('temps_max')
def validate_temps_max(cls, v):

# Après :
@field_validator('temps_max')
@classmethod
def validate_temps_max(cls, v):
```

**Ligne ~108** :
```python
# Avant :
@validator('ordre_preference')
def validate_ordre(cls, v):

# Après :
@field_validator('ordre_preference')
@classmethod
def validate_ordre(cls, v):
```

**Ligne ~120** :
```python
# Avant :
@validator('priorites')
def validate_priorites(cls, v):

# Après :
@field_validator('priorites')
@classmethod
def validate_priorites(cls, v):
```

**Ligne ~134** :
```python
# Avant :
@validator('max')
def validate_max(cls, v):

# Après :
@field_validator('max')
@classmethod
def validate_max(cls, v):
```

### 🔧 Script de Correction Automatique :

```bash
# Créer script de correction rapide
cat > fix_pydantic_validators.py << 'EOF'
#!/usr/bin/env python3
import re

def fix_questionnaire_advanced():
    file_path = 'nextvision/models/questionnaire_advanced.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup original
        with open(file_path + '.backup', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 1. Fix import
        content = re.sub(
            r'from pydantic import (.*?)validator',
            r'from pydantic import \1field_validator',
            content
        )
        
        # 2. Fix @validator → @field_validator + @classmethod
        content = re.sub(
            r'@validator\(([^)]+)\)\s*\n\s*def (validate_\w+)\(cls,',
            r'@field_validator(\1)\n    @classmethod\n    def \2(cls,',
            content
        )
        
        # Write fixed version
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fichier corrigé: {file_path}")
        print(f"📁 Backup créé: {file_path}.backup")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_questionnaire_advanced()
EOF

# Exécuter correction
python3 fix_pydantic_validators.py

# Vérifier résultat
python3 -c "
try:
    from nextvision.models.questionnaire_advanced import TransportQuestionnaireAvance
    print('✅ Import OK - Warnings corrigés')
except Exception as e:
    print(f'❌ Import failed: {e}')
"
```

### ⚡ Test Rapide après Correction :

```bash
# Test import sans warnings
python3 -W error::DeprecationWarning -c "
import nextvision.models.questionnaire_advanced
print('✅ Aucun warning Pydantic')
"

# Test coverage optimisée
./run_tests_v3.sh real
```

---

**Cette correction éliminera immédiatement les 6 warnings Pydantic V1 visibles dans vos logs de test.**
