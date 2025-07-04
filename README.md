# 🎯 NEXTVISION - Algorithme de Matching IA Révolutionnaire

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> **Premier système au monde avec pondération adaptative contextuelle**

## 🌉 Innovation Révolutionnaire : Bridge Commitment-Nextvision

**NEXTVISION** fait partie de l'écosystème **NEXTEN**, un système révolutionnaire qui connecte intelligemment :

```
📋 Commitment- (Job Parser + CV Parser GPT) ←→ 🎯 Nextvision (Matching IA Adaptatif)
                                 🌉 Bridge Zéro Redondance
```

### 🚀 Avantages Compétitifs Uniques

- ✅ **Double parsing GPT mature** déjà opérationnel (Job + CV)
- ✅ **Algorithme de matching révolutionnaire** avec pondération adaptative
- ✅ **Architecture zéro redondance** qui valorise l'existant
- ✅ **Time-to-market optimisé** en réutilisant l'infrastructure
- ✅ **Innovation contextuelle** jamais vue sur le marché

## 🎯 Pondération Adaptative Contextuelle

L'algorithme ajuste **automatiquement** les poids selon le "pourquoi_ecoute" du candidat :

| Raison d'écoute | Adaptation | Impact |
|------------------|------------|--------|
| **"Rémunération trop faible"** | Priorité rémunération | +43% vs base |
| **"Poste ne coïncide pas"** | Priorité sémantique | +28% vs base |
| **"Poste trop loin"** | Priorité localisation | +100% vs base |
| **"Manque de flexibilité"** | Priorité environnement | +200% vs base |
| **"Manque perspectives"** | Priorité motivations | +200% vs base |

## 🏗️ Architecture NEXTEN Complète

```
🎯 ÉCOSYSTÈME NEXTEN
├── 📋 Commitment- (Frontend + Backend)
│   ├── ✅ Job Parser GPT v6.2.0 (100% opérationnel)
│   ├── ✅ CV Parser GPT (100% opérationnel)
│   └── ✅ Infrastructure GPT mature
│
├── 🌉 Bridge CommitmentNextvisionBridge
│   ├── 🔍 Détection automatique des services
│   ├── 🔄 Transformation des formats
│   ├── ⚡ Processing asynchrone
│   └── 📊 Monitoring des performances
│
└── 🎯 Nextvision (Backend IA)
    ├── ✅ API FastAPI avec pondération adaptative
    ├── ✅ Algorithme révolutionnaire unique
    └── ✅ Endpoints d'intégration Bridge
```

## 🚀 Démarrage Rapide

### 1. Installation

```bash
git clone https://github.com/Bapt252/Nextvision.git
cd Nextvision
pip install -r requirements.txt
```

### 2. Configuration

Copier et adapter le fichier `.env` :

```bash
cp .env .env.local
# Adapter les URLs des services Commitment- selon votre configuration
```

### 3. Démarrage

```bash
python main.py
```

🌐 **API disponible sur** : http://localhost:8000
📚 **Documentation** : http://localhost:8000/docs

## 🌉 Endpoints Bridge Révolutionnaires

### Workflow Complet
```http
POST /api/v1/integration/complete-workflow
Content-Type: multipart/form-data

pourquoi_ecoute: "Rémunération trop faible"
job_text: "Développeur Full Stack - 45k€"
cv_file: @cv.pdf
```

### Parse Job via Commitment-
```http
POST /api/v1/integration/parse-job-from-commitment
Content-Type: multipart/form-data

job_text: "Développeur Python - TechCorp - Paris"
```

### CV → Matching Adaptatif
```http
POST /api/v1/integration/cv-to-matching
Content-Type: multipart/form-data

pourquoi_ecoute: "Poste ne coïncide pas avec poste proposé"
cv_file: @candidat.pdf
```

### Health Check Intégration
```http
GET /api/v1/integration/health
```

## 🎯 Endpoints Matching Adaptatif

### Matching Principal
```http
POST /api/v1/matching/candidate/{id}
Content-Type: application/json

{
  "pourquoi_ecoute": "Rémunération trop faible",
  "candidate_profile": {
    "personal_info": {
      "firstName": "Marie",
      "lastName": "Dubois",
      "email": "marie@example.com"
    },
    "skills": ["JavaScript", "React", "Node.js"],
    "experience_years": 5
  },
  "preferences": {
    "salary_expectations": {
      "min": 45000,
      "max": 55000
    },
    "location_preferences": {
      "city": "Paris"
    }
  }
}
```

### Prévisualisation Poids Adaptatifs
```http
GET /api/v1/weights/preview?pourquoi_ecoute=Rémunération trop faible
```

## 📊 Exemple de Réponse

```json
{
  "status": "success",
  "matching_results": {
    "total_score": 0.847,
    "confidence": 0.932,
    "component_scores": {
      "semantique": 0.85,
      "remuneration": 0.92,
      "localisation": 0.75
    },
    "weights_used": {
      "semantique": 0.30,
      "remuneration": 0.30,
      "localisation": 0.10
    }
  },
  "adaptive_weighting": {
    "applied": true,
    "reason": "Rémunération trop faible",
    "reasoning": "Priorité accordée à l'amélioration salariale",
    "weight_changes": {
      "remuneration": {
        "from": 0.20,
        "to": 0.30,
        "change": 0.10,
        "change_percent": 50.0
      }
    }
  }
}
```

## 🔧 Configuration Avancée

### Variables d'Environnement

```env
# Nextvision
NEXTVISION_HOST=0.0.0.0
NEXTVISION_PORT=8000
DEBUG=true

# Services Commitment-
COMMITMENT_JOB_PARSER_PRIMARY=http://localhost:5053/api/parse-job
COMMITMENT_CV_PARSER_PRIMARY=http://localhost:5055/api/parse-cv

# Bridge
BRIDGE_REQUEST_TIMEOUT=30
BRIDGE_AUTO_DETECT_SERVICES=true

# Pondération Adaptative
ADAPTIVE_WEIGHTING_ENABLED=true
DEFAULT_CONFIDENCE_THRESHOLD=0.7
```

### Personnalisation des Poids

```python
# Dans main.py, adapter ADAPTIVE_WEIGHTS_CONFIG
ADAPTIVE_WEIGHTS_CONFIG = {
    "Ma raison personnalisée": {
        "semantique": 0.40,
        "remuneration": 0.25,
        "reasoning": "Ma stratégie adaptative"
    }
}
```

## 🧪 Tests et Monitoring

### Health Checks

```bash
# Nextvision seul
curl http://localhost:8000/api/v1/health

# Intégration complète
curl http://localhost:8000/api/v1/integration/health

# Status écosystème NEXTEN
curl http://localhost:8000/api/v1/integration/status
```

### Tests d'Intégration

```bash
# Test workflow complet
curl -X POST "http://localhost:8000/api/v1/integration/complete-workflow" \
  -H "Content-Type: multipart/form-data" \
  -F "pourquoi_ecoute=Rémunération trop faible" \
  -F "job_text=Développeur Full Stack - 45k€" \
  -F "cv_file=@tests/cv_test.pdf"
```

## 📈 Performance

- ⚡ **Parsing Job** : ~500ms (via Commitment- GPT)
- ⚡ **Parsing CV** : ~1-2s (via Commitment- GPT)
- ⚡ **Matching Adaptatif** : ~50ms (Nextvision)
- 🔄 **Workflow Complet** : ~2-3s (Job + CV + Matching)

## 🎯 Roadmap

- [x] ✅ **v1.0** : Pondération adaptative révolutionnaire
- [x] ✅ **v1.0** : Bridge Commitment-Nextvision zéro redondance
- [ ] 🔄 **v1.1** : Cache Redis pour optimisation
- [ ] 🔄 **v1.2** : Webhooks temps réel
- [ ] 🔄 **v1.3** : Dashboard monitoring
- [ ] 🔄 **v2.0** : ML avancé pour pondération auto-apprenante

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

## 🔗 Liens Utiles

- 📋 **Commitment- (Frontend + Parsing)** : https://github.com/Bapt252/Commitment-
- 🎯 **Nextvision (Backend IA)** : https://github.com/Bapt252/Nextvision
- 📚 **Documentation API** : http://localhost:8000/docs
- 🌉 **Bridge Health** : http://localhost:8000/api/v1/integration/health

---

<div align="center">

**🎯 NEXTEN - Premier écosystème RH avec pondération adaptative contextuelle au monde**

*Innovation révolutionnaire • Architecture zéro redondance • Avantage compétitif énorme*

</div>
