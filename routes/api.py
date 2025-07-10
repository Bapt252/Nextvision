"""
Routes API Nextvision pour parsing GPT V3.2.1
==============================================

Routes Flask pour exposer les parsers GPT via API REST
Compatible avec le frontend Commitment- déployé sur GitHub Pages
MISE À JOUR: Compatible avec CV Parser v4.0.3 (gestion robuste des salaires)

Version: 1.0.1 (SALARY FIXED)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
import tempfile
import time
from typing import Dict, Any, Optional

# Import des modules GPT existants
from gpt_modules.cv_parser import CVParserGPT
from gpt_modules.job_parser import JobParserGPT
from gpt_modules.integration import GPTNextvisionIntegrator
import openai

# Configuration
app = Flask(__name__)

# Configuration CORS pour GitHub Pages
CORS(app, origins=[
    'https://bapt252.github.io',  # Commitment- GitHub Pages
    'http://localhost:3000',      # Développement local
    'http://127.0.0.1:5500'       # Live Server
])

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    logger.warning("OPENAI_API_KEY non configurée - mode fallback activé")

# Configuration upload
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialisation des parsers avec nouvelles versions
cv_parser = CVParserGPT(openai_client=openai)
job_parser = JobParserGPT(openai_client=openai)
integrator = GPTNextvisionIntegrator(
    cv_parser=cv_parser,
    job_parser=job_parser
)

def allowed_file(filename):
    """Vérifie si le fichier est autorisé"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path: str) -> str:
    """Extrait le texte d'un fichier uploadé"""
    try:
        # Pour les PDF, utiliser pdfplumber
        if file_path.lower().endswith('.pdf'):
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                logger.warning("pdfplumber non disponible, utilisation du fallback")
                return f"[PDF non lisible - {os.path.basename(file_path)}]"
        
        # Pour les fichiers texte
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
    except Exception as e:
        logger.error(f"Erreur extraction texte: {str(e)}")
        return f"[Erreur extraction - {os.path.basename(file_path)}]"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de santé de l'API"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.1',
        'timestamp': time.time(),
        'parsers': {
            'cv_parser': cv_parser.version if cv_parser else 'N/A',
            'job_parser': job_parser.version if job_parser else 'N/A',
            'integrator': integrator.version if integrator else 'N/A'
        },
        'openai_configured': bool(openai.api_key),
        'features': [
            'CV Parser v4.0.3 - Gestion robuste des salaires',
            'Parsing "Non mentionné", N/A, valeurs vides',
            'Estimation automatique des salaires manquants',
            'Integration v1.0.2 compatible',
            'API endpoints complets'
        ]
    })

@app.route('/api/parse/cv', methods=['POST'])
def parse_cv():
    """
    Parse un CV via GPT avec gestion robuste des salaires
    
    Paramètres:
    - file: Fichier CV (PDF, DOC, TXT)
    
    Réponse:
    - Format Nextvision compatible avec validation de salaires améliorée
    """
    start_time = time.time()
    
    try:
        # Vérification du fichier
        if 'file' not in request.files:
            return jsonify({
                'error': 'Aucun fichier fourni',
                'code': 'NO_FILE'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'Nom de fichier vide',
                'code': 'EMPTY_FILENAME'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Type de fichier non autorisé. Formats acceptés: {", ".join(ALLOWED_EXTENSIONS)}',
                'code': 'INVALID_FILE_TYPE'
            }), 400
        
        # Sauvegarde temporaire
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extraction du texte
            cv_text = extract_text_from_file(filepath)
            logger.info(f"Texte extrait du CV: {len(cv_text)} caractères")
            
            # Parsing avec GPT v4.0.3 (gestion salaires robuste)
            cv_data = cv_parser.parse_cv_text(cv_text)
            
            # Log du résultat de parsing pour debugging
            logger.info(f"CV parsé: {cv_data.nom_complet} - Salaires: {cv_data.salaire_actuel}€/{cv_data.salaire_souhaite}€")
            
            # Conversion au format Nextvision
            nextvision_format = cv_parser.to_nextvision_format(cv_data)
            
            # Ajout des métadonnées avec informations de validation
            processing_time = (time.time() - start_time) * 1000
            
            response = {
                'success': True,
                'data': nextvision_format,
                'metadata': {
                    'processing_time_ms': processing_time,
                    'file_name': filename,
                    'file_size': os.path.getsize(filepath),
                    'text_length': len(cv_text),
                    'parser_version': cv_parser.version,
                    'salary_validation': {
                        'current_salary': cv_data.salaire_actuel,
                        'expected_salary': cv_data.salaire_souhaite,
                        'validation_method': 'robust_conversion_v4.0.3'
                    },
                    'candidate_profile': {
                        'name': cv_data.nom_complet,
                        'hierarchical_level': cv_data.niveau_hierarchique,
                        'experience_years': cv_data.experience_years
                    },
                    'timestamp': time.time()
                }
            }
            
            success_emoji = "✅" if cv_data.nom_complet != "Dorothée Lim" else "🔄"
            logger.info(f"{success_emoji} CV parsé: {cv_data.nom_complet} en {processing_time:.1f}ms")
            return jsonify(response)
            
        finally:
            # Nettoyage du fichier temporaire
            try:
                os.remove(filepath)
            except:
                pass
    
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Erreur parsing CV: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'PARSING_ERROR',
            'metadata': {
                'processing_time_ms': processing_time,
                'parser_version': cv_parser.version if cv_parser else 'N/A',
                'fallback_used': True,
                'timestamp': time.time()
            }
        }), 500

@app.route('/api/parse/job', methods=['POST'])
def parse_job():
    """
    Parse une fiche de poste via GPT
    
    Paramètres:
    - text: Texte de la fiche de poste (JSON)
    
    Réponse:
    - Format Nextvision compatible
    """
    start_time = time.time()
    
    try:
        # Vérification des données
        if not request.json or 'text' not in request.json:
            return jsonify({
                'error': 'Texte de la fiche de poste manquant',
                'code': 'NO_TEXT'
            }), 400
        
        job_text = request.json['text']
        
        if not job_text or len(job_text.strip()) < 50:
            return jsonify({
                'error': 'Texte de la fiche de poste trop court (minimum 50 caractères)',
                'code': 'TEXT_TOO_SHORT'
            }), 400
        
        logger.info(f"Parsing fiche de poste: {len(job_text)} caractères")
        
        # Parsing avec GPT
        job_data = job_parser.parse_job_text(job_text)
        
        # Conversion au format Nextvision
        nextvision_format = job_parser.to_nextvision_format(job_data)
        
        # Ajout des métadonnées
        processing_time = (time.time() - start_time) * 1000
        
        response = {
            'success': True,
            'data': nextvision_format,
            'metadata': {
                'processing_time_ms': processing_time,
                'text_length': len(job_text),
                'parser_version': job_parser.version,
                'job_profile': {
                    'title': job_data.titre,
                    'hierarchical_level': job_data.niveau_hierarchique,
                    'salary_range': f"{job_data.salaire_min}€-{job_data.salaire_max}€"
                },
                'timestamp': time.time()
            }
        }
        
        logger.info(f"✅ Fiche de poste parsée: {job_data.titre} en {processing_time:.1f}ms")
        return jsonify(response)
    
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Erreur parsing fiche de poste: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'PARSING_ERROR',
            'metadata': {
                'processing_time_ms': processing_time,
                'parser_version': job_parser.version if job_parser else 'N/A',
                'timestamp': time.time()
            }
        }), 500

@app.route('/api/match', methods=['POST'])
def match_profiles():
    """
    Effectue le matching entre un candidat et un poste
    Compatible avec CV Parser v4.0.3 (gestion robuste des salaires)
    
    Paramètres:
    - candidate: Données candidat (format Nextvision)
    - job: Données poste (format Nextvision)
    
    Réponse:
    - Résultat de matching avec score détaillé
    """
    start_time = time.time()
    
    try:
        # Vérification des données
        if not request.json:
            return jsonify({
                'error': 'Données JSON manquantes',
                'code': 'NO_JSON'
            }), 400
        
        candidate_data = request.json.get('candidate')
        job_data = request.json.get('job')
        
        if not candidate_data or not job_data:
            return jsonify({
                'error': 'Données candidat ou poste manquantes',
                'code': 'MISSING_DATA'
            }), 400
        
        candidate_name = candidate_data.get('personal_info', {}).get('name', 'Candidat')
        job_title = job_data.get('job_info', {}).get('title', 'Poste')
        logger.info(f"Matching: {candidate_name} vs {job_title}")
        
        # Matching avec l'intégrateur v1.0.2 (compatible salaires v4.0.3)
        match_result = integrator.perform_complete_matching(candidate_data, job_data)
        
        # Conversion en format JSON sérialisable
        result_dict = {
            'candidate_name': match_result.candidate_name,
            'job_title': match_result.job_title,
            'total_score': match_result.total_score,
            'scores_breakdown': match_result.scores_breakdown,
            'hierarchical_compatibility': match_result.hierarchical_compatibility,
            'alerts': match_result.alerts,
            'performance_ms': match_result.performance_ms,
            'recommendation': match_result.recommendation
        }
        
        processing_time = (time.time() - start_time) * 1000
        
        # Analyse du résultat pour le logging
        is_charlotte_test = "charlotte" in candidate_name.lower() and "comptable" in job_title.lower()
        score_ok = match_result.total_score < 0.4 if is_charlotte_test else match_result.total_score > 0.6
        
        response = {
            'success': True,
            'data': result_dict,
            'metadata': {
                'processing_time_ms': processing_time,
                'integrator_version': integrator.version,
                'weights_used': integrator.weights_v31,
                'salary_compatibility': {
                    'candidate_salaries': {
                        'current': candidate_data.get('professional_info', {}).get('current_salary'),
                        'expected': candidate_data.get('professional_info', {}).get('expected_salary')
                    },
                    'job_salary_range': {
                        'min': job_data.get('requirements', {}).get('salary_min'),
                        'max': job_data.get('requirements', {}).get('salary_max')
                    },
                    'salary_score': match_result.scores_breakdown.get('salary', 0)
                },
                'timestamp': time.time()
            }
        }
        
        success_emoji = "✅" if score_ok else "⚠️"
        logger.info(f"{success_emoji} Matching: {candidate_name} vs {job_title} = {match_result.total_score:.3f} en {processing_time:.1f}ms")
        
        return jsonify(response)
    
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Erreur matching: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'MATCHING_ERROR',
            'metadata': {
                'processing_time_ms': processing_time,
                'integrator_version': integrator.version if integrator else 'N/A',
                'timestamp': time.time()
            }
        }), 500

@app.route('/api/test/charlotte', methods=['GET'])
def test_charlotte_vs_comptable():
    """
    Test spécifique Charlotte DARMON vs Comptable
    Validation du système avec CV Parser v4.0.3 (gestion robuste des salaires)
    """
    start_time = time.time()
    
    try:
        logger.info("🧪 Exécution du test Charlotte DARMON vs Comptable (v4.0.3)")
        
        # Exécution du test
        test_result = integrator.test_charlotte_darmon_vs_comptable()
        
        processing_time = (time.time() - start_time) * 1000
        
        # Validation spécifique des objectifs V3.2.1
        objectives_count = sum(test_result['objectives_validation'].values())
        all_objectives_met = test_result['success']
        
        response = {
            'success': True,
            'data': {
                'test_name': test_result['test_name'],
                'test_success': test_result['success'],
                'objectives_validation': test_result['objectives_validation'],
                'objectives_met': f"{objectives_count}/5",
                'score': test_result['result'].total_score,
                'recommendation': test_result['result'].recommendation,
                'alerts': test_result['result'].alerts,
                'scores_breakdown': test_result['result'].scores_breakdown,
                'performance_ms': test_result['result'].performance_ms,
                'charlotte_profile': {
                    'hierarchical_level': 'EXECUTIVE',
                    'salary_handling': 'v4.0.3_robust_validation'
                }
            },
            'metadata': {
                'processing_time_ms': processing_time,
                'system_version': test_result['system_version'],
                'validation_criteria': {
                    '1_score_below_0.4': test_result['result'].total_score < 0.4,
                    '2_critical_hierarchical': 'CRITICAL' in test_result['result'].hierarchical_compatibility,
                    '3_critical_mismatch_alert': any('CRITICAL_MISMATCH' in alert for alert in test_result['result'].alerts),
                    '4_performance_under_100ms': test_result['result'].performance_ms < 100,
                    '5_sector_scoring_included': 'sector' in test_result['result'].scores_breakdown
                },
                'timestamp': time.time()
            }
        }
        
        success_emoji = "✅" if all_objectives_met else "❌"
        logger.info(f"{success_emoji} Test Charlotte: {test_result['result'].total_score:.3f} - {objectives_count}/5 objectifs")
        
        return jsonify(response)
    
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Erreur test Charlotte: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'TEST_ERROR',
            'metadata': {
                'processing_time_ms': processing_time,
                'timestamp': time.time()
            }
        }), 500

@app.route('/api/status', methods=['GET'])
def integration_status():
    """
    Statut complet de l'intégration GPT V3.2.1
    """
    try:
        status = integrator.integration_status()
        
        # Ajout d'informations sur les nouvelles capacités
        enhanced_status = {
            **status,
            'salary_validation': {
                'cv_parser_version': cv_parser.version if cv_parser else 'N/A',
                'robust_handling': True,
                'supported_formats': [
                    'Numeric values (45000, 45000.0)',
                    'Formatted strings (55K€, 60k)',
                    'Non-numeric indicators (Non mentionné, N/A, empty)',
                    'Auto-estimation when missing'
                ],
                'fallback_strategy': 'Automatic salary estimation based on hierarchical level and sector'
            }
        }
        
        return jsonify({
            'success': True,
            'data': enhanced_status,
            'metadata': {
                'timestamp': time.time(),
                'api_version': '1.0.1'
            }
        })
    
    except Exception as e:
        logger.error(f"Erreur statut: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'STATUS_ERROR',
            'metadata': {
                'timestamp': time.time()
            }
        }), 500

# Gestion des erreurs globales
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': 'Fichier trop volumineux',
        'code': 'FILE_TOO_LARGE',
        'max_size': f'{MAX_CONTENT_LENGTH / (1024*1024):.0f}MB'
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint non trouvé',
        'code': 'NOT_FOUND',
        'available_endpoints': [
            'GET /api/health - Santé de l\'API',
            'GET /api/status - Statut de l\'intégration',
            'POST /api/parse/cv - Parsing CV avec gestion salaires robuste',
            'POST /api/parse/job - Parsing fiche de poste',
            'POST /api/match - Matching candidat/poste',
            'GET /api/test/charlotte - Test Charlotte vs Comptable (validation V3.2.1)'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Erreur interne: {str(e)}")
    return jsonify({
        'error': 'Erreur interne du serveur',
        'code': 'INTERNAL_ERROR'
    }), 500

if __name__ == '__main__':
    # Configuration pour le développement
    logger.info("🚀 Démarrage de l'API Nextvision Parsing GPT V3.2.1")
    logger.info(f"OpenAI configuré: {bool(openai.api_key)}")
    
    # Test de démarrage avec nouvelles versions
    try:
        status = integrator.integration_status()
        logger.info(f"✅ Intégration initialisée: {status['integration_version']}")
        logger.info(f"CV Parser: {cv_parser.version if cv_parser else 'N/A'}")
        logger.info(f"Job Parser: {job_parser.version if job_parser else 'N/A'}")
        logger.info("🔧 Nouvelle fonctionnalité: Gestion robuste des salaires 'Non mentionné'")
        
        # Test rapide Charlotte si disponible
        if cv_parser and job_parser:
            logger.info("🧪 Test rapide Charlotte vs Comptable au démarrage...")
            try:
                test_result = integrator.test_charlotte_darmon_vs_comptable()
                score = test_result['result'].total_score
                objectives = sum(test_result['objectives_validation'].values())
                status_emoji = "✅" if test_result['success'] else "❌"
                logger.info(f"{status_emoji} Test démarrage: Score {score:.3f} - {objectives}/5 objectifs")
            except Exception as e:
                logger.warning(f"⚠️ Test démarrage échoué: {str(e)}")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {str(e)}")
    
    app.run(
        host='0.0.0.0',
        port=5051,
        debug=True,
        threaded=True
    )
