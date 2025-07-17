# 🚀 Guide Migration Pydantic V1 → V2 - Nextvision V3.0

## 📋 Objectif

Éliminer complètement les warnings Pydantic V1 deprecated dans Nextvision V3.0 et migrer vers Pydantic V2 pour :
- ✅ **Performance améliorée** (30-50% plus rapide)
- ✅ **API plus claire** et moderne
- ✅ **Meilleure validation** des types
- ✅ **Élimination des warnings** dans les tests

---

## 🔍 Diagnostic Warnings Actuels

### Warnings identifiés :
```
DeprecationWarning: 
- `@validator` is deprecated, use `@field_validator` instead
- `Config` class is deprecated, use `model_config` instead  
- `.dict()` is deprecated, use `.model_dump()` instead
- `parse_obj()` is deprecated, use `.model_validate()` instead
- `json_encoders` is deprecated, use model serialization instead
```

---

## 🛠️ Plan de Migration

### Phase 1 : Installation Pydantic V2
```bash
# 1. Mise à jour requirements
pip install "pydantic>=2.0.0,<3.0.0"
pip install pydantic-settings>=2.0.0

# 2. Vérification installation
python -c "import pydantic; print(f'Pydantic V{pydantic.__version__}')"
```

### Phase 2 : Migration Code par Code
**Fichiers prioritaires à migrer :**
- `nextvision/models/questionnaire_advanced.py` ⭐ **PRIORITÉ 1**
- `nextvision/models/*.py` (tous les modèles)
- `nextvision/services/*.py` (si utilisent Pydantic)

---

## 📝 Guide de Conversion - Syntaxe

### 1. **Migration @validator → @field_validator**

#### ❌ Ancien (V1)
```python
from pydantic import BaseModel, validator

class QuestionnaireAvance(BaseModel):
    email: str
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email invalide')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0:
            raise ValueError('Age doit être positif')
        return v
```

#### ✅ Nouveau (V2)
```python
from pydantic import BaseModel, field_validator

class QuestionnaireAvance(BaseModel):
    email: str
    age: int
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email invalide')
        return v
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 0:
            raise ValueError('Age doit être positif')
        return v
```

### 2. **Migration Config → model_config**

#### ❌ Ancien (V1)
```python
from pydantic import BaseModel

class TransportQuestionnaireAvance(BaseModel):
    moyens_transport: List[str]
    temps_max: int
    
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

#### ✅ Nouveau (V2)
```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TransportQuestionnaireAvance(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        validate_assignment=True,
    )
    
    moyens_transport: List[str]
    temps_max: int
    
    # json_encoders remplacé par model_serializer si nécessaire
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # Custom serialization logic here if needed
        return data
```

### 3. **Migration Méthodes d'Instance**

#### ❌ Ancien (V1)
```python
# Utilisation des modèles
questionnaire = TransportQuestionnaireAvance(
    moyens_transport=['metro', 'bus'],
    temps_max=45
)

# Sérialisation
data_dict = questionnaire.dict()
json_str = questionnaire.json()

# Parsing
new_questionnaire = TransportQuestionnaireAvance.parse_obj(data_dict)
from_json = TransportQuestionnaireAvance.parse_raw(json_str)
```

#### ✅ Nouveau (V2)
```python
# Utilisation des modèles (INCHANGÉ)
questionnaire = TransportQuestionnaireAvance(
    moyens_transport=['metro', 'bus'],
    temps_max=45
)

# Sérialisation (NOUVELLE SYNTAXE)
data_dict = questionnaire.model_dump()
json_str = questionnaire.model_dump_json()

# Parsing (NOUVELLE SYNTAXE)
new_questionnaire = TransportQuestionnaireAvance.model_validate(data_dict)
from_json = TransportQuestionnaireAvance.model_validate_json(json_str)
```

### 4. **Migration Field avec validation**

#### ❌ Ancien (V1)
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class MotivationsQuestionnaireAvance(BaseModel):
    priorites: List[str] = Field(..., description="Priorités professionnelles")
    salaire_min: Optional[int] = Field(None, ge=0, description="Salaire minimum")
    
    @validator('priorites')
    def validate_priorites(cls, v):
        if not v:
            raise ValueError('Au moins une priorité requise')
        return v
```

#### ✅ Nouveau (V2)
```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class MotivationsQuestionnaireAvance(BaseModel):
    priorites: List[str] = Field(..., description="Priorités professionnelles")
    salaire_min: Optional[int] = Field(None, ge=0, description="Salaire minimum")
    
    @field_validator('priorites')
    @classmethod
    def validate_priorites(cls, v):
        if not v:
            raise ValueError('Au moins une priorité requise')
        return v
```

---

## 🔧 Script de Migration Automatique

### Créer `migrate_pydantic_v2.py`
```python
#!/usr/bin/env python3
"""
Script de migration automatique Pydantic V1 → V2 pour Nextvision
"""

import re
import os
from pathlib import Path

def migrate_file(file_path: Path) -> bool:
    """Migre un fichier Python vers Pydantic V2"""
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # 1. Migration @validator → @field_validator
        content = re.sub(
            r'@validator\(',
            r'@field_validator(',
            content
        )
        
        # 2. Ajout @classmethod si @field_validator présent
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '@field_validator(' in line:
                # Chercher la fonction suivante
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('def '):
                    j += 1
                if j < len(lines) and 'def ' in lines[j]:
                    # Ajouter @classmethod si pas déjà présent
                    if '@classmethod' not in lines[j-1]:
                        lines.insert(j, '    @classmethod')
        content = '\n'.join(lines)
        
        # 3. Migration imports
        content = re.sub(
            r'from pydantic import (.*?)validator',
            r'from pydantic import \1field_validator',
            content
        )
        
        # 4. Migration .dict() → .model_dump()
        content = re.sub(
            r'\.dict\(\)',
            r'.model_dump()',
            content
        )
        
        # 5. Migration .parse_obj() → .model_validate()
        content = re.sub(
            r'\.parse_obj\(',
            r'.model_validate(',
            content
        )
        
        # 6. Migration class Config → model_config
        content = re.sub(
            r'class Config:',
            r'model_config = ConfigDict(',
            content
        )
        
        # Ajout import ConfigDict si nécessaire
        if 'model_config = ConfigDict(' in content and 'ConfigDict' not in content:
            content = re.sub(
                r'from pydantic import',
                r'from pydantic import ConfigDict,',
                content,
                count=1
            )
        
        # Écriture si changements
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Migré: {file_path}")
            return True
        else:
            print(f"📋 Déjà à jour: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur migration {file_path}: {e}")
        return False

def main():
    """Migration automatique du projet"""
    
    print("🚀 Migration Pydantic V1 → V2 - Nextvision V3.0")
    print("=" * 50)
    
    # Fichiers à migrer
    files_to_migrate = [
        "nextvision/models/questionnaire_advanced.py",
        # Ajouter autres fichiers au besoin
    ]
    
    migrated_count = 0
    
    for file_path_str in files_to_migrate:
        file_path = Path(file_path_str)
        if file_path.exists():
            if migrate_file(file_path):
                migrated_count += 1
        else:
            print(f"⚠️ Fichier non trouvé: {file_path}")
    
    print(f"\n🎯 Résumé: {migrated_count} fichier(s) migré(s)")
    print("\n📋 Étapes suivantes:")
    print("1. Vérifier compilation: python -m py_compile nextvision/models/*.py")
    print("2. Lancer tests: pytest tests/ -v")
    print("3. Vérifier warnings: pytest tests/ -W error::DeprecationWarning")

if __name__ == "__main__":
    main()
```

---

## 🧪 Tests Post-Migration

### 1. **Vérification Compilation**
```bash
# Test compilation de tous les modèles
python -m py_compile nextvision/models/*.py
```

### 2. **Tests avec Warnings Stricts**
```bash
# Tests avec warnings comme erreurs
pytest tests/ -W error::DeprecationWarning
```

### 3. **Test Fonctionnement Modèles**
```python
# test_pydantic_v2_migration.py
import pytest
from nextvision.models.questionnaire_advanced import (
    TransportQuestionnaireAvance,
    MotivationsQuestionnaireAvance
)

def test_transport_questionnaire_v2():
    """Test modèle transport avec Pydantic V2"""
    data = {
        'moyens_transport': ['metro', 'bus'],
        'temps_max': 45
    }
    
    # Nouvelle syntaxe V2
    questionnaire = TransportQuestionnaireAvance.model_validate(data)
    
    assert questionnaire.temps_max == 45
    assert len(questionnaire.moyens_transport) == 2
    
    # Sérialisation V2
    result = questionnaire.model_dump()
    assert result['temps_max'] == 45

def test_motivations_questionnaire_v2():
    """Test modèle motivations avec Pydantic V2"""
    data = {
        'priorites': ['salaire', 'evolution'],
        'salaire_min': 50000
    }
    
    questionnaire = MotivationsQuestionnaireAvance.model_validate(data)
    assert questionnaire.salaire_min == 50000
```

---

## 📊 Checklist Migration

### ✅ **Phase 1 : Préparation**
- [ ] Installation Pydantic V2
- [ ] Backup code existant
- [ ] Tests actuels passent

### ✅ **Phase 2 : Migration Code**
- [ ] `nextvision/models/questionnaire_advanced.py`
- [ ] Autres modèles Pydantic
- [ ] Services utilisant Pydantic

### ✅ **Phase 3 : Validation**
- [ ] Compilation sans erreurs
- [ ] Tests passent avec Pydantic V2
- [ ] Aucun warning DeprecationWarning
- [ ] Performance maintenue/améliorée

### ✅ **Phase 4 : Finalisation**
- [ ] Update requirements.txt
- [ ] Documentation mise à jour
- [ ] Intégration dans CI/CD

---

## 🚨 Points d'Attention

### **1. Validateurs Complexes**
```python
# Attention : syntaxe classmethod obligatoire en V2
@field_validator('field_name')
@classmethod  # ← OBLIGATOIRE
def validate_field(cls, v):
    return v
```

### **2. Config Avancée**
```python
# Migration manuelle nécessaire pour Config complexe
model_config = ConfigDict(
    arbitrary_types_allowed=True,
    use_enum_values=True,
    validate_assignment=True,
    # json_encoders supprimé → utiliser model_serializer
)
```

### **3. Compatibilité Temporaire**
```python
# Pendant transition, code compatible V1/V2 :
try:
    # V2
    data = model.model_dump()
except AttributeError:
    # V1 fallback
    data = model.dict()
```

---

## 🎯 Résultat Attendu

Après migration complète :
- ✅ **0 warnings** Pydantic dans tests
- ✅ **Performance améliorée** 30-50%
- ✅ **Code plus moderne** et maintenable
- ✅ **Compatibilité future** assurée

---

## 📞 Support

Pour questions ou problèmes :
1. **Documentation officielle** : https://docs.pydantic.dev/migration/
2. **Issues GitHub** : Créer ticket avec tag `pydantic-migration`
3. **Tests locaux** : `pytest tests/ -k pydantic -v`

---

**🚀 Migration Pydantic V2 - Nextvision V3.0 prêt pour l'avenir !**
