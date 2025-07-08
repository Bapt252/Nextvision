# 🚀 Guide d'Utilisation Nextvision V3.0

## 📋 Démarrage Rapide

### Installation et Configuration

```bash
# 1. Cloner le repository
git clone https://github.com/Bapt252/Nextvision.git
cd Nextvision

# 2. Basculer sur la branche V3.0
git checkout feature/bidirectional-matching-v2

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Vérification installation
python -c "from nextvision.engines.adaptive_weighting_engine_v3 import AdaptiveWeightingEngine; print('✅ Nextvision V3.0 OK')"
```

### Test de Validation

```bash
# Validation matrices adaptatives
python nextvision/config/adaptive_weighting_config.py

# Test scorers avancés
python nextvision/engines/advanced_scorers_v3.py

# Démonstration complète
python demo_nextvision_v3_complete.py

# Test production complet (2,346 matchings)
python test_nextvision_v3_production_final.py
```

---

## 🎯 Utilisation de Base

### Import et Initialisation

```python
from nextvision.engines.adaptive_weighting_engine_v3 import AdaptiveWeightingEngine
from nextvision.config.adaptive_weighting_config import ListeningReasonType

# Initialisation engine V3.0
engine = AdaptiveWeightingEngine(validate_matrices=True)
print("✅ Engine V3.0 prêt")
```

### Matching Simple

```python
# Données candidat
candidate_data = {
    "skills": ["python", "django", "react"],
    "years_experience": 5,
    "current_salary": 55000,
    "desired_salary": 65000,
    "location": "Paris",
    "listening_reasons": ["remuneration_faible"],
    "secteurs_preferes": ["fintech", "tech"],
    "contract_ranking": ["cdi", "freelance"],
    "office_preference": "hybrid"
}

# Données poste
position_data = {
    "required_skills": ["python", "django", "vue"],
    "salary_min": 60000,
    "salary_max": 75000,
    "location": "Paris",
    "company_sector": "fintech",
    "contract_type": "cdi",
    "remote_policy": "hybrid"
}

# Calcul matching adaptatif
result = engine.calculate_adaptive_matching_score(
    candidate_data, 
    position_data
)

print(f"Score: {result.total_score:.3f}")
print(f"Temps: {result.total_processing_time_ms:.1f}ms")
print(f"Raison: {result.listening_reason.value}")
```

---

## 🔄 Pondération Adaptative

### Raisons d'Écoute Disponibles

| Raison | Impact Principal | Composants Boostés |
|--------|------------------|-------------------|
| **REMUNERATION_FAIBLE** | Salary +68% | Salary (32%), Salary Progression (5%) |
| **POSTE_INADEQUAT** | Semantic +25% | Semantic (30%), Sector Compatibility (10%) |
| **MANQUE_PERSPECTIVES** | Experience +57% | Experience (22%), Motivations (14%) |
| **LOCALISATION** | Location +178% | Location (25%), Work Modality (8%) |
| **FLEXIBILITE** | Modality +150% | Work Modality (10%), Contract (10%), Timing (7%) |

### Utilisation Raison Spécifique

```python
# Force une raison d'écoute spécifique
result = engine.calculate_adaptive_matching_score(
    candidate_data,
    position_data,
    listening_reason=ListeningReasonType.REMUNERATION_FAIBLE
)

# Voir l'impact des boosts
for component in result.component_scores:
    if component.boost_applied > 0:
        print(f"{component.name}: {component.base_weight:.2f} → {component.weight:.2f} (+{component.boost_applied:.2f})")
```

---

## 🎯 Scorers Spécialisés V3.0

### 1. SectorCompatibilityScorer

```python
from nextvision.engines.advanced_scorers_v3 import SectorCompatibilityScorer

scorer = SectorCompatibilityScorer()

candidate_prefs = {
    "preferred_sectors": ["fintech", "startup"],
    "avoided_sectors": ["defense", "tobacco"],
    "current_sector": "banking",
    "openness_to_change": 4,  # 1-5 scale
    "sector_experience": {"finance": 3, "tech": 2}
}

result = scorer.score_sector_compatibility(candidate_prefs, "fintech")
print(f"Score: {result.score:.2f}")
print(f"Qualité: {result.quality.value}")
print(f"Raison: {result.reason}")
```

### 2. TimingCompatibilityScorer

```python
from nextvision.engines.advanced_scorers_v3 import TimingCompatibilityScorer

scorer = TimingCompatibilityScorer()

candidate_timing = {
    "availability_date": "2025-08-15",
    "notice_period_weeks": 6,
    "flexibility_weeks": 2,
    "urgency_level": 4
}

company_timing = {
    "desired_start_date": "2025-08-01",
    "recruitment_urgency": 4,
    "max_wait_weeks": 8
}

result = scorer.score_timing_compatibility(candidate_timing, company_timing)
print(f"Score: {result.score:.2f}")
print(f"Gap: {result.details.get('gap_weeks', 0):.1f} semaines")
```

### 3. WorkModalityScorer

```python
from nextvision.engines.advanced_scorers_v3 import WorkModalityScorer

scorer = WorkModalityScorer()

candidate_prefs = {
    "preferred_modality": "hybrid",
    "remote_days_per_week": 3,
    "max_commute_minutes": 45,
    "flexibility_level": 4
}

company_policy = {
    "work_modality": "hybrid",
    "remote_days_allowed": 2,
    "commute_distance_km": 20
}

result = scorer.score_work_modality(candidate_prefs, company_policy)
print(f"Score: {result.score:.2f}")
print(f"Compatibilité: {result.quality.value}")
```

---

## 📊 Analyse des Résultats

### Résultat Détaillé

```python
result = engine.calculate_adaptive_matching_score(candidate_data, position_data)

# Score global
print(f"Score total: {result.total_score:.3f}/1.000")
print(f"Confiance: {result.confidence_level:.2f}")

# Top contributeurs
print("\\nTop contributeurs:")
for component_name in result.top_contributors:
    component = next(cs for cs in result.component_scores if cs.name == component_name)
    print(f"- {component_name}: {component.weighted_score:.3f}")

# Détail par composant
print("\\nDétail composants:")
for component in result.component_scores:
    boost_info = f" (+{component.boost_applied:.2f})" if component.boost_applied > 0 else ""
    print(f"- {component.name}: {component.raw_score:.2f} × {component.weight:.2f}{boost_info} = {component.weighted_score:.3f}")

# Suggestions d'amélioration
if result.improvement_suggestions:
    print("\\nSuggestions:")
    for suggestion in result.improvement_suggestions:
        print(f"- {suggestion}")
```

### Export pour API

```python
# Export JSON pour API/logs
result_dict = result.to_dict()

# Sauvegarde
import json
with open("matching_result.json", "w") as f:
    json.dump(result_dict, f, indent=2)
```

---

## ⚡ Performance et Monitoring

### Statistiques Performance

```python
# Rapport performance engine
perf_report = engine.get_performance_report()

print(f"Matches traités: {perf_report['total_matches_processed']}")
print(f"Temps moyen: {perf_report['avg_processing_time_ms']:.1f}ms")
print(f"Target <175ms: {'✅' if perf_report['performance_ok'] else '❌'}")

# Timing par composant
for component, timing in perf_report['component_avg_timings'].items():
    print(f"- {component}: {timing:.2f}ms")
```

### Optimisation Performance

```python
# Pour production high-volume, désactiver validation
engine = AdaptiveWeightingEngine(validate_matrices=False)

# Batch processing
results = []
for candidate, position in candidate_position_pairs:
    result = engine.calculate_adaptive_matching_score(candidate, position)
    results.append(result)
    
    # Check performance périodique
    if len(results) % 100 == 0:
        avg_time = sum(r.total_processing_time_ms for r in results[-100:]) / 100
        print(f"Avg last 100: {avg_time:.1f}ms")
```

---

## 🔧 Configuration Avancée

### Personnalisation Matrices

```python
from nextvision.config.adaptive_weighting_config import AdaptiveWeightingConfigV3

# Configuration personnalisée
config = AdaptiveWeightingConfigV3()

# Modification matrices (attention: doit totaliser 1.0)
custom_matrix = {
    "salary": 0.40,  # Focus salary encore plus fort
    "semantic": 0.25,
    "experience": 0.15,
    "location": 0.10,
    "motivations": 0.05,
    "sector_compatibility": 0.03,
    "contract_flexibility": 0.02
    # ... total = 1.00
}

# Validation avant utilisation
total = sum(custom_matrix.values())
assert abs(total - 1.0) < 0.001, f"Matrice invalide: {total}"
```

### Logs et Debugging

```python
import logging

# Configuration logs Nextvision
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('nextvision')

# Engine avec logs
engine = AdaptiveWeightingEngine(validate_matrices=True)

# Matching avec logs détaillés
result = engine.calculate_adaptive_matching_score(candidate_data, position_data)

# Log résultat
logger.info(f"Matching {candidate_data.get('candidate_id', 'unknown')} x {position_data.get('position_id', 'unknown')}: {result.total_score:.3f}")
```

---

## 🚀 Intégration Production

### API REST Exemple

```python
from flask import Flask, request, jsonify
from nextvision.engines.adaptive_weighting_engine_v3 import AdaptiveWeightingEngine

app = Flask(__name__)
engine = AdaptiveWeightingEngine()

@app.route('/api/v3/matching', methods=['POST'])
def calculate_matching():
    data = request.json
    
    try:
        result = engine.calculate_adaptive_matching_score(
            data['candidate'],
            data['position'],
            data.get('listening_reason')
        )
        
        return jsonify({
            'success': True,
            'result': result.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=False, threaded=True)
```

### Exemple Appel API

```bash
curl -X POST http://localhost:5000/api/v3/matching \\
  -H "Content-Type: application/json" \\
  -d '{
    "candidate": {
      "skills": ["python", "react"],
      "years_experience": 5,
      "desired_salary": 65000,
      "listening_reasons": ["remuneration_faible"]
    },
    "position": {
      "required_skills": ["python", "vue"],
      "salary_max": 70000,
      "company_sector": "tech"
    }
  }'
```

---

## 📚 Structures de Données

### Format Candidat Complet

```python
candidate_data = {
    # Identification
    "candidate_id": "CAND_001",
    
    # V2.0 - Core
    "skills": ["python", "django", "react", "postgresql"],
    "domains": ["fintech", "web development"], 
    "years_experience": 6,
    "current_salary": 55000,
    "desired_salary": 70000,
    "location": "Paris",
    
    # V3.0 - Questionnaire étape 2
    "transport_methods": ["metro", "bus"],
    "max_travel_time": 45,
    "contract_ranking": ["cdi", "freelance", "cdd"],
    "office_preference": "hybrid",
    "remote_days_per_week": 3,
    
    # V3.0 - Questionnaire étape 3  
    "motivations_ranking": {
        "challenge_technique": 1,
        "evolution_carriere": 2,
        "equilibre_vie": 3
    },
    "secteurs_preferes": ["fintech", "tech", "startup"],
    "secteurs_redhibitoires": ["defense", "tobacco"],
    "sector_openness": 4,  # 1-5
    
    # V3.0 - Questionnaire étape 4
    "availability_date": "2025-08-15",
    "notice_period_weeks": 8,
    "employment_status": "en_poste",  # en_poste, demandeur_emploi, freelance
    "listening_reasons": ["remuneration_faible"],
    "job_search_urgency": 4,  # 1-5
    
    # Optionnel - Métadonnées
    "home_office_setup": True,
    "flexibility_weeks": 2,
    "progression_expectations": 3
}
```

### Format Position Complet

```python
position_data = {
    # Identification
    "position_id": "POS_001",
    
    # V2.0 - Core
    "required_skills": ["python", "django", "vue", "postgresql"],
    "domain": "fintech",
    "min_years_experience": 4,
    "max_years_experience": 8,
    "salary_min": 65000,
    "salary_max": 80000,
    "location": "Paris",
    
    # V3.0 - Entreprise
    "company_sector": "fintech",
    "company_size": "scale-up",
    
    # V3.0 - Contrat & Modalités
    "contract_type": "cdi",
    "remote_policy": "hybrid",
    "remote_days_allowed": 2,
    "office_days_required": 3,
    "commute_distance_km": 15,
    
    # V3.0 - Timing & Urgence
    "desired_start_date": "2025-08-01",
    "recruitment_urgency": 4,  # 1-5
    "max_wait_weeks": 8,
    "project_deadline": "2025-12-01",  # Optionnel
    
    # V3.0 - Motivations poste
    "position_motivations": {
        "challenge_technique": 2,
        "evolution_carriere": 1,
        "impact_business": 3
    },
    
    # Optionnel
    "job_benefits": ["restaurant", "transport", "mutuelle"],
    "team_size": 8,
    "company_flexibility": 3
}
```

---

## ✅ Tests et Validation

### Tests Unitaires

```bash
# Tests matrices
python -m pytest tests/test_adaptive_weighting.py

# Tests scorers
python -m pytest tests/test_advanced_scorers.py

# Tests engine complet
python -m pytest tests/test_engine_v3.py
```

### Validation Continue

```python
# Monitoring production
def validate_matching_quality(results):
    avg_confidence = sum(r.confidence_level for r in results) / len(results)
    avg_time = sum(r.total_processing_time_ms for r in results) / len(results)
    
    assert avg_confidence > 0.7, f"Confiance trop faible: {avg_confidence}"
    assert avg_time < 175, f"Performance dégradée: {avg_time}ms"
    
    print(f"✅ Qualité: {avg_confidence:.2f} confiance, {avg_time:.1f}ms")
```

---

## 🎯 Support et Troubleshooting

### Erreurs Courantes

```python
# ImportError - Vérifier PYTHONPATH
import sys
sys.path.append('/path/to/nextvision')

# Matrices non-validées
from nextvision.config.adaptive_weighting_config import validate_all_matrices
validate_all_matrices()  # Doit retourner True pour toutes

# Performance dégradée
engine.get_performance_report()  # Analyser timings par composant
```

### Contact et Contributions

- **Repository**: https://github.com/Bapt252/Nextvision  
- **Branch V3.0**: `feature/bidirectional-matching-v2`
- **Documentation**: `NEXTVISION_V3_PROMPT4_COMPLETED.md`
- **Tests**: `test_nextvision_v3_production_final.py`

---

**🎯 Nextvision V3.0 - Guide d'Utilisation Complet**  
*Version 3.0 - Production Ready*  
*NEXTEN Development Team - 2025*
