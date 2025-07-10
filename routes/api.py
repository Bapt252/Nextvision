"""
Routes API Nextvision pour parsing GPT
=====================================

Routes Flask pour exposer les parsers GPT via API REST
Compatible avec le frontend Commitment- déployé sur GitHub Pages

Version: 1.0.0
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

# Initialisation des parsers
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
        'version': '1.0.0',
        'timestamp': time.time(),
        'parsers': {
            'cv_parser': cv_parser.version if cv_parser else 'N/A',
            'job_parser': job_parser.version if job_parser else 'N/A',
            'integrator': integrator.version if integrator else 'N/A'
        },
        'openai_configured': bool(openai.api_key)
    })

@app.route('/api/parse/cv', methods=['POST'])
def parse_cv():
    """
    Parse un CV via GPT
    
    Paramètres:
    - file: Fichier CV (PDF, DOC, TXT)
    
    Réponse:
    - Format Nextvision compatible
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
            
            # Parsing avec GPT
            cv_data = cv_parser.parse_cv_text(cv_text)
            
            # Conversion au format Nextvision
            nextvision_format = cv_parser.to_nextvision_format(cv_data)
            
            # Ajout des métadonnées
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
                    'timestamp': time.time()
                }
            }
            
            logger.info(f"CV parsé avec succès en {processing_time:.1f}ms")
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
                'timestamp': time.time()
            }
        }
        
        logger.info(f"Fiche de poste parsée avec succès en {processing_time:.1f}ms")
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
                'timestamp': time.time()
            }
        }), 500

@app.route('/api/match', methods=['POST'])
def match_profiles():
    """
    Effectue le matching entre un candidat et un poste
    
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
        
        logger.info(f"Matching: {candidate_data.get('personal_info', {}).get('name', 'Candidat')} vs {job_data.get('job_info', {}).get('title', 'Poste')}")
        
        # Matching avec l'intégrateur
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
        
        response = {
            'success': True,
            'data': result_dict,
            'metadata': {
                'processing_time_ms': processing_time,
                'integrator_version': integrator.version,
                'weights_used': integrator.weights_v31,
                'timestamp': time.time()
            }
        }
        
        logger.info(f"Matching terminé: score {match_result.total_score:.3f} en {processing_time:.1f}ms")
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
                'timestamp': time.time()
            }
        }), 500

@app.route('/api/test/charlotte', methods=['GET'])
def test_charlotte_vs_comptable():
    """
    Test spécifique Charlotte DARMON vs Comptable
    Endpoint pour validation du système
    """
    start_time = time.time()
    
    try:
        logger.info("🧪 Exécution du test Charlotte DARMON vs Comptable")
        
        # Exécution du test
        test_result = integrator.test_charlotte_darmon_vs_comptable()
        
        processing_time = (time.time() - start_time) * 1000
        
        response = {
            'success': True,
            'data': {
                'test_name': test_result['test_name'],
                'test_success': test_result['success'],
                'objectives_validation': test_result['objectives_validation'],
                'score': test_result['result'].total_score,
                'recommendation': test_result['result'].recommendation,
                'alerts': test_result['result'].alerts,
                'scores_breakdown': test_result['result'].scores_breakdown,
                'performance_ms': test_result['result'].performance_ms
            },
            'metadata': {
                'processing_time_ms': processing_time,
                'system_version': test_result['system_version'],
                'timestamp': time.time()
            }
        }
        
        success_emoji = "✅" if test_result['success'] else "❌"
        logger.info(f"{success_emoji} Test Charlotte terminé: {test_result['result'].total_score:.3f}")
        
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
    Statut complet de l'intégration GPT
    """
    try:
        status = integrator.integration_status()
        
        return jsonify({
            'success': True,
            'data': status,
            'metadata': {
                'timestamp': time.time(),
                'api_version': '1.0.0'
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
            'GET /api/health',
            'GET /api/status',
            'POST /api/parse/cv',
            'POST /api/parse/job',
            'POST /api/match',
            'GET /api/test/charlotte'
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
    logger.info("🚀 Démarrage de l'API Nextvision Parsing GPT")
    logger.info(f"OpenAI configuré: {bool(openai.api_key)}")
    
    # Test de démarrage
    try:
        status = integrator.integration_status()
        logger.info(f"✅ Intégration initialisée: {status['integration_version']}")
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {str(e)}")
    
    app.run(
        host='0.0.0.0',
        port=5051,
        debug=True,
        threaded=True
    )
