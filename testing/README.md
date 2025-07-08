# 🚀 Guide d'Installation et d'Utilisation - Nextvision v2.0 Test Suite

## 📋 Vue d'ensemble

Ce système de test massif permet de valider Nextvision v2.0 à grande échelle avec :
- **2,346 combinaisons** (69 CVs × 34 FDPs)
- **Simulations questionnaires** réalistes
- **Analytics avancées** et visualisations
- **Monitoring temps réel**
- **Comparaisons A/B** de scénarios

## 🛠️ Installation

### 1. Prérequis

```bash
# Python 3.13.4 requis
python3 --version

# Environnement virtuel Nextvision
source nextvision-env/bin/activate

# Vérification API Nextvision v2.0
cd /path/to/nextvision
git checkout feature/bidirectional-matching-v2
```

### 2. Installation des dépendances

```bash
# Dépendances principales
pip install requests pandas numpy matplotlib seaborn plotly
pip install psutil scikit-learn scipy aiohttp

# Pour les visualisations avancées
pip install jupyter notebook  # optionnel
```

### 3. Configuration des chemins

Modifiez les chemins dans `nextvision_master_controller.py` :

```python
# Configuration globale
API_URL = "http://localhost:8000"
CV_DIR = "/Users/baptistecomas/Desktop/CV TEST"
FDP_DIR = "/Users/baptistecomas/Desktop/FDP TEST"
```

## 🚀 Démarrage Rapide

### Option 1: Interface Unifiée (Recommandée)

```bash
python nextvision_master_controller.py
```

Cette interface vous permet de :
- ✅ Vérifier automatiquement l'API
- 🎯 Lancer tous types de tests
- 📊 Générer visualisations
- 📈 Monitoring temps réel

### Option 2: Scripts Individuels

```bash
# Test massif personnalisé
python nextvision_mass_testing.py

# Visualisations uniquement
python nextvision_visualizer.py

# Analytics avancées
python nextvision_advanced_analyzer.py
```

## 📊 Types de Tests Disponibles

### 1. 🧪 Test Massif Standard
- **Objectif**: Validation de performance à grande échelle
- **Données**: 69 CVs × 34 FDPs = 2,346 combinaisons
- **Temps estimé**: 3-5 minutes complet
- **Résultats**: Scores, temps, analytics

```bash
# Via l'interface principale
Choix 3: Test Massif Complet
```

### 2. 🎯 Test Rapide (100 combinaisons)
- **Objectif**: Validation rapide de fonctionnement
- **Temps estimé**: 10-30 secondes
- **Utilisation**: Tests de régression, debug

```bash
# Via l'interface principale  
Choix 2: Test Massif Rapide
```

### 3. 🧪 Comparaison de Scénarios
- **Objectif**: A/B testing de profils utilisateurs
- **Scénarios inclus**:
  - Candidats motivés salaire
  - Startups urgentes
  - Reconversions professionnelles

```bash
# Via l'interface principale
Choix 5: Comparaison Scénarios
```

### 4. 📈 Monitoring Temps Réel
- **Objectif**: Surveillance continue de l'API
- **Métriques**: Temps réponse, mémoire, CPU, erreurs
- **Fréquence**: Toutes les 5 secondes

```bash
# Via l'interface principale
Choix 6: Monitoring Temps Réel
```

## 📊 Interprétation des Résultats

### Scores de Matching

| Score | Interprétation | Action |
|-------|----------------|--------|
| > 0.8 | ✅ Excellent match | Candidat prioritaire |
| 0.6-0.8 | 🟡 Bon match | À considérer |
| 0.4-0.6 | 🟠 Match moyen | Évaluation cas par cas |
| < 0.4 | ❌ Match faible | Pas de suite |

### Performances Système

| Métrique | Seuil Optimal | Seuil Alerte |
|----------|---------------|-------------|
| Temps réponse | < 0.1s | > 2.0s |
| Taux succès | > 95% | < 90% |
| Variance scores | 0.1-0.3 | > 0.3 |
| Utilisation RAM | < 60% | > 80% |

## 📁 Structure des Résultats

```
nextvision_test_results/
├── raw_results_YYYYMMDD_HHMMSS.json      # Données brutes
├── analysis_report_YYYYMMDD_HHMMSS.json  # Rapport d'analyse
├── results_YYYYMMDD_HHMMSS.csv           # Export CSV
└── scenario_comparison_YYYYMMDD_HHMMSS.json # Comparaisons A/B

visualizations/
├── score_distribution.png                 # Distribution des scores
├── performance_analysis.png               # Analyse performances
├── questionnaire_impact.png               # Impact questionnaires
├── correlation_heatmap.png                # Corrélations
├── temporal_analysis.png                  # Évolution temporelle
└── interactive_dashboard.html             # Dashboard interactif
```

## 🔍 Vérifications de Cohérence

### Indicateurs de Santé

1. **Variance des Scores** ✅
   - Attendu: 0.1 - 0.3
   - Problème si: > 0.3 (instable) ou < 0.1 (trop uniforme)

2. **Performance Temporelle** ✅
   - Attendu: < 0.2s par test
   - Dégradation: > 1s (optimisation requise)

3. **Taux de Réussite** ✅
   - Attendu: > 98%
   - Problème si: < 95% (bugs API)

4. **Cohérence Questionnaires** ✅
   - Impact visible des paramètres
   - Corrélations logiques

## ⚡ Optimisations Performances

### Configuration Recommandée

```python
# Paramètres optimaux trouvés
MAX_CONCURRENT_REQUESTS = 10  # Ne pas dépasser
TIMEOUT_REQUEST = 30          # Secondes
BATCH_SIZE = 100             # Tests par lot
```

### Monitoring Système

```bash
# Surveillance ressources pendant les tests
htop                    # CPU/RAM
iostat -x 1            # I/O disque
netstat -i             # Trafic réseau
```

## 🚨 Résolution de Problèmes

### Erreurs Communes

1. **API non accessible**
   ```bash
   # Vérification
   curl http://localhost:8000/docs
   
   # Redémarrage
   uvicorn main_v2:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Fichiers non trouvés**
   ```bash
   # Vérification chemins
   ls "/Users/baptistecomas/Desktop/CV TEST"
   ls "/Users/baptistecomas/Desktop/FDP TEST"
   ```

3. **Mémoire insuffisante**
   ```bash
   # Réduire concurrence
   MAX_CONCURRENT_REQUESTS = 5
   
   # Tests par petits lots
   max_combinations = 500
   ```

4. **Temps de réponse élevés**
   ```bash
   # Vérification processus
   ps aux | grep uvicorn
   
   # Surveillance ressources
   top -p $(pgrep uvicorn)
   ```

### Debug Avancé

```python
# Mode debug dans les scripts
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs détaillés API
uvicorn main_v2:app --log-level debug
```

## 📈 Métriques de Validation

### Critères de Réussite v2.0

- ✅ **Performance**: < 0.1s par match (objectif: 1000 matchs/s)
- ✅ **Précision**: Score moyen > 0.7
- ✅ **Stabilité**: Variance < 0.2
- ✅ **Fiabilité**: Taux succès > 98%
- ✅ **Cohérence**: Impact questionnaires visible

### KPIs Business

- 🎯 **Matching Quality**: Score moyen par profil
- 📊 **System Efficiency**: Temps traitement global
- 🔄 **Scalability**: Performance avec charge
- 🎮 **UX Impact**: Influence questionnaires

## 🎯 Prochaines Étapes

### Phase 1: Validation Technique ✅
- [x] Architecture bidirectionnelle
- [x] Tests massifs 
- [x] Monitoring performances

### Phase 2: Optimisation (En cours)
- [ ] Machine Learning avancé
- [ ] Cache intelligent
- [ ] API rate limiting

### Phase 3: Production
- [ ] Déploiement containerisé
- [ ] CI/CD intégré
- [ ] Monitoring production

## 📞 Support

### Logs et Debug
```bash
# Logs API
tail -f uvicorn.log

# Logs tests
tail -f nextvision_test.log

# Profiling performance
python -m cProfile nextvision_mass_testing.py
```

### Contacts Équipe
- **Lead Dev**: Baptiste Comas
- **Architecture**: Nextvision v2.0 team
- **Support**: NEXTEN technical team

---

🎉 **Nextvision v2.0 Test Suite - Validation à Grande Échelle Réussie!** 🎉