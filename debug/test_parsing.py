"""
Test script pour diagnostiquer le parsing GPT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpt_modules.cv_parser import CVParserGPT
import openai
import logging

# Configuration des logs détaillés
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_openai_direct():
    """Test direct de l'API OpenAI"""
    try:
        logger.info("🧪 Test OpenAI direct...")
        
        # Vérifier la clé
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("❌ OPENAI_API_KEY non définie")
            return False
            
        logger.info(f"✅ Clé OpenAI configurée: {api_key[:8]}...")
        
        # Test simple
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Réponds juste 'OK' si tu me reçois"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        logger.info(f"✅ OpenAI répond: {result}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur OpenAI: {str(e)}")
        return False

def test_cv_parser():
    """Test du parser CV avec debug"""
    try:
        logger.info("🧪 Test CV Parser...")
        
        # Initialiser le parser
        parser = CVParserGPT(openai_client=openai)
        
        # Texte simple
        cv_text = """
        MARIE MARTIN
        Développeuse Full Stack Senior
        marie.martin@email.com
        +33 6 12 34 56 78
        5 ans d'expérience en développement web
        Compétences: JavaScript, React, Node.js
        """
        
        logger.info(f"📝 Parsing CV: {len(cv_text)} caractères")
        
        # Parser
        result = parser.parse_cv_text(cv_text)
        
        logger.info(f"✅ Résultat: {result.nom_complet}")
        logger.info(f"✅ Email: {result.email}")
        logger.info(f"✅ Titre: {result.titre_poste}")
        
        return result.nom_complet == "Marie Martin"
        
    except Exception as e:
        logger.error(f"❌ Erreur parser: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNOSTIC PARSING GPT")
    print("=" * 50)
    
    # Test 1: OpenAI direct
    openai_ok = test_openai_direct()
    print(f"OpenAI direct: {'✅' if openai_ok else '❌'}")
    
    # Test 2: CV Parser
    if openai_ok:
        parser_ok = test_cv_parser()
        print(f"CV Parser: {'✅' if parser_ok else '❌'}")
    else:
        print("CV Parser: ⏭️ Skipped (OpenAI failed)")
    
    print("\n" + "=" * 50)
    print("🎯 RÉSULTATS:")
    if openai_ok and parser_ok:
        print("✅ Tout fonctionne - Problème ailleurs")
    elif openai_ok:
        print("⚠️ OpenAI OK mais Parser KO - Problème dans le code")
    else:
        print("❌ OpenAI KO - Problème de configuration")
