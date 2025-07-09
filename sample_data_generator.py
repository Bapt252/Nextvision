#!/usr/bin/env python3
"""
📁 Générateur de Données d'Exemple pour Nextvision V3.0
Crée des CVs et FDPs d'exemple pour tester le système si vous n'avez pas de vraies données

Author: Assistant
Version: 1.0
"""

import os
from pathlib import Path
from datetime import datetime
import json

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Configuration
DESKTOP_PATH = Path.home() / "Desktop"
CV_FOLDER = DESKTOP_PATH / "CV TEST"
FDP_FOLDER = DESKTOP_PATH / "FDP TEST"

# Données d'exemple pour CVs
CV_EXAMPLES = [
    {
        "filename": "cv_marie_comptable.txt",
        "content": """MARIE DUPONT
Comptable Senior
marie.dupont@email.com | +33 6 12 34 56 78
Paris, France

EXPÉRIENCE PROFESSIONNELLE

Comptable Senior | Entreprise ABC | 2020 - Présent
• Gestion de la comptabilité générale et analytique
• Préparation des déclarations fiscales (TVA, IS)
• Supervision d'une équipe de 3 comptables juniors
• Maîtrise de CEGID et SAP
• Clôtures mensuelles et annuelles

Comptable | Société XYZ | 2018 - 2020
• Saisie et vérification des écritures comptables
• Rapprochements bancaires et gestion des comptes clients
• Préparation des liasses fiscales
• Utilisation d'Excel avancé et QuickBooks

Assistant Comptable | Cabinet DEF | 2016 - 2018
• Support à l'équipe comptable
• Archivage et classement des documents
• Première expérience avec les logiciels comptables

FORMATION
Master en Comptabilité, Contrôle et Audit | Université Paris Dauphine | 2016
Licence en Gestion | Université Paris-Sorbonne | 2014

COMPÉTENCES
• Logiciels : CEGID, SAP, Excel, QuickBooks, Sage
• Langues : Français (natif), Anglais (courant)
• Certifications : DCG (Diplôme de Comptabilité et Gestion)

QUALITÉS
• Rigueur et précision
• Sens de l'organisation
• Capacité à travailler en équipe
• Respect des délais
"""
    },
    {
        "filename": "cv_jean_developpeur.txt",
        "content": """JEAN MARTIN
Développeur Full-Stack Senior
jean.martin@email.com | +33 6 98 76 54 32
Lyon, France

EXPÉRIENCE PROFESSIONNELLE

Développeur Full-Stack Senior | TechCorp | 2021 - Présent
• Développement d'applications web avec React et Node.js
• Architecture microservices avec Docker et Kubernetes
• API REST et GraphQL
• Encadrement d'une équipe de 4 développeurs juniors
• Méthodologies Agile/Scrum

Développeur Full-Stack | StartupTech | 2019 - 2021
• Développement front-end avec React, Vue.js
• Backend avec Python (Django/Flask) et Node.js
• Bases de données PostgreSQL et MongoDB
• Déploiement AWS et intégration CI/CD

Développeur Junior | WebAgency | 2017 - 2019
• Sites web avec HTML, CSS, JavaScript
• CMS WordPress et Drupal
• Maintenance et debug d'applications existantes
• Collaboration avec les équipes design et marketing

FORMATION
Master en Informatique | École Centrale Lyon | 2017
Licence en Informatique | Université Claude Bernard Lyon 1 | 2015

COMPÉTENCES TECHNIQUES
• Languages : Python, JavaScript, TypeScript, Java, PHP
• Frontend : React, Vue.js, Angular, HTML5, CSS3, SASS
• Backend : Node.js, Django, Flask, Express.js
• Databases : PostgreSQL, MongoDB, MySQL, Redis
• DevOps : Docker, Kubernetes, AWS, GitLab CI/CD
• Tools : Git, JIRA, Figma, Postman

PROJETS PERSONNELS
• Application de gestion de tâches (React + Node.js)
• API de recommandations (Python + Machine Learning)
• Contributions open source sur GitHub

LANGUES
• Français (natif)
• Anglais (courant)
• Espagnol (intermédiaire)
"""
    },
    {
        "filename": "cv_sophie_manager.txt",
        "content": """SOPHIE BERNARD
Manager Marketing Digital
sophie.bernard@email.com | +33 6 11 22 33 44
Marseille, France

EXPÉRIENCE PROFESSIONNELLE

Manager Marketing Digital | GrandGroupe SA | 2020 - Présent
• Management d'une équipe de 8 personnes
• Stratégies marketing multicanales (SEO, SEM, Social Media)
• Budget annuel de 500K€
• Augmentation du trafic web de 150% en 2 ans
• Outils : Google Analytics, AdWords, Facebook Ads

Responsable Marketing | MoyenneEntreprise | 2018 - 2020
• Gestion des campagnes publicitaires digitales
• Création de contenus pour les réseaux sociaux
• Analyse des performances et ROI
• Collaboration avec les équipes ventes et produit
• CRM HubSpot et Salesforce

Chargée de Communication | PetiteAgence | 2016 - 2018
• Communication interne et externe
• Gestion des relations presse
• Événementiel et salons professionnels
• Rédaction de communiqués de presse

FORMATION
Master en Marketing Digital | ESCP Business School | 2016
Licence en Communication | Université Aix-Marseille | 2014

COMPÉTENCES
• Marketing Digital : SEO, SEM, Social Media, Email Marketing
• Analytics : Google Analytics, Adobe Analytics, Mixpanel
• CRM : HubSpot, Salesforce, Pipedrive
• Design : Photoshop, Canva, Figma
• Management : Leadership, Gestion d'équipe, Budgets

CERTIFICATIONS
• Google Analytics Certified
• Google Ads Certified
• HubSpot Inbound Marketing
• Facebook Blueprint

RÉALISATIONS
• Augmentation du taux de conversion de 45%
• Réduction du coût d'acquisition client de 30%
• Lancement réussi de 3 produits
• Prix "Meilleure Campagne Digitale 2022"
"""
    },
    {
        "filename": "cv_thomas_commercial.txt",
        "content": """THOMAS LEROY
Commercial Senior BtoB
thomas.leroy@email.com | +33 6 55 44 33 22
Toulouse, France

EXPÉRIENCE PROFESSIONNELLE

Commercial Senior BtoB | TechSolutions | 2019 - Présent
• Développement commercial grands comptes (CA 2M€/an)
• Prospection et négociation avec les décideurs
• Suivi d'un portefeuille de 50 clients stratégiques
• Atteinte des objectifs à 125% en moyenne
• CRM Salesforce et HubSpot

Commercial | ServicesPro | 2017 - 2019
• Vente de services aux PME/ETI
• Prospection téléphonique et terrain
• Présentation de solutions personnalisées
• Négociation et closing
• Reporting hebdomadaire

Assistant Commercial | StartupVente | 2015 - 2017
• Support à l'équipe commerciale
• Qualification des leads
• Préparation des propositions commerciales
• Suivi administratif des ventes
• Participation aux salons professionnels

FORMATION
Master en Commerce International | Toulouse Business School | 2015
Licence en Économie-Gestion | Université Toulouse 1 Capitole | 2013

COMPÉTENCES
• Négociation et closing
• Prospection multicanale
• Gestion de la relation client
• Présentation et pitch
• Analyse des besoins clients

OUTILS
• CRM : Salesforce, HubSpot, Pipedrive
• Prospection : LinkedIn Sales Navigator, Hunter.io
• Présentation : PowerPoint, Prezi, Canva
• Communication : Slack, Teams, Zoom

RÉSULTATS
• CA généré : 8M€ sur 5 ans
• Taux de conversion : 35% (moyenne secteur 20%)
• Nouveaux clients : 150+ sur 3 ans
• Fidélisation : 85% de rétention client

LANGUES
• Français (natif)
• Anglais (courant)
• Allemand (intermédiaire)
"""
    },
    {
        "filename": "cv_laura_rh.txt",
        "content": """LAURA RODRIGUEZ
Responsable Ressources Humaines
laura.rodriguez@email.com | +33 6 77 88 99 00
Nantes, France

EXPÉRIENCE PROFESSIONNELLE

Responsable RH | InnovCorp | 2021 - Présent
• Management RH d'une équipe de 150 personnes
• Recrutement et intégration des nouveaux talents
• Gestion de la paie et des avantages sociaux
• Développement des compétences et formations
• SIRH Workday et ADP

Chargée de Recrutement | ConseilRH | 2019 - 2021
• Recrutement de profils IT et commerciaux
• Entretiens de sélection et évaluation
• Sourcing sur LinkedIn et job boards
• Suivi des candidatures et onboarding
• Partenariat avec les managers opérationnels

Assistante RH | GrandeEntreprise | 2017 - 2019
• Administration du personnel
• Gestion des congés et absences
• Préparation des contrats de travail
• Veille juridique et réglementaire
• Organisation des événements d'entreprise

FORMATION
Master en GRH | IAE Nantes | 2017
Licence en Psychologie du Travail | Université de Nantes | 2015

COMPÉTENCES
• Recrutement et sélection
• Droit du travail
• Gestion de la paie
• Formation et développement
• Relations sociales

CERTIFICATIONS
• CNAM - Certificat en Gestion des RH
• Formation en Droit Social
• Certification LinkedIn Recruiter
• MBTI Praticien

OUTILS
• SIRH : Workday, ADP, Sage Paie
• Recrutement : LinkedIn Recruiter, Indeed, Monster
• Évaluation : AssessFirst, Central Test
• Bureautique : Suite Office, G Suite

RÉALISATIONS
• Réduction du turnover de 40% à 15%
• Amélioration du process de recrutement (-30% de temps)
• Mise en place d'un plan de formation annuel
• Satisfaction employés : 4.2/5 (enquête interne)
"""
    }
]

# Données d'exemple pour FDPs
FDP_EXAMPLES = [
    {
        "filename": "fdp_comptable_senior.txt",
        "content": """FICHE DE POSTE
Comptable Senior H/F
CDI - Paris 8ème

ENTREPRISE
Cabinet comptable de taille moyenne (50 personnes)
Spécialisé dans l'accompagnement des PME/ETI
Ambiance familiale et conviviale

MISSION PRINCIPALE
Nous recherchons un(e) Comptable Senior pour rejoindre notre équipe et prendre en charge un portefeuille de clients variés.

RESPONSABILITÉS
• Gestion complète de la comptabilité de 15-20 clients
• Révision et validation des comptes annuels
• Établissement des déclarations fiscales (TVA, IS, CVAE)
• Conseil et accompagnement des clients
• Encadrement d'assistants comptables
• Participation aux missions d'audit

PROFIL RECHERCHÉ
• Formation comptable de niveau Bac+3 minimum (DCG apprécié)
• 5 à 8 ans d'expérience en cabinet ou entreprise
• Maîtrise des logiciels CEGID et Sage
• Connaissance approfondie de la fiscalité française
• Autonomie, rigueur et sens du relationnel

COMPÉTENCES TECHNIQUES
• Comptabilité générale et analytique
• Déclarations fiscales et sociales
• Consolidation et reporting
• Contrôle de gestion
• Audit et révision des comptes

RÉMUNÉRATION
42 000€ à 48 000€ brut annuel
Variable sur objectifs (jusqu'à 3 000€/an)
Participation aux bénéfices

AVANTAGES
• Tickets restaurant (8€/jour)
• Mutuelle entreprise prise en charge à 100%
• RTT (12 jours/an)
• Formation continue
• Télétravail possible (2 jours/semaine)

ÉVOLUTION
Possibilité d'évolution vers un poste de Chef de Mission
Perspective d'association à moyen terme

LIEU
Métro Miromesnil (ligne 9/13)
Bureaux modernes et climatisés
"""
    },
    {
        "filename": "fdp_developpeur_fullstack.txt",
        "content": """FICHE DE POSTE
Développeur Full-Stack Senior H/F
CDI - Lyon Part-Dieu

ENTREPRISE
Scale-up technologique (100 personnes)
Produit SaaS B2B en forte croissance
Environnement agile et innovant

CONTEXTE
Nous développons une plateforme de gestion pour les entreprises.
Croissance de 200% en 2 ans, levée de fonds récente.

MISSION
Développement et maintenance de notre plateforme web
Participation à l'architecture technique
Mentorat des développeurs juniors

RESPONSABILITÉS TECHNIQUES
• Développement front-end avec React/TypeScript
• API REST avec Node.js et Express
• Base de données PostgreSQL
• Déploiement sur AWS avec Docker
• Tests unitaires et intégration

RESPONSABILITÉS TRANSVERSES
• Participation aux rituels Agile (Scrum)
• Code review et pair programming
• Veille technologique
• Formation des nouveaux arrivants

STACK TECHNIQUE
• Frontend: React, TypeScript, Redux, Styled Components
• Backend: Node.js, Express, PostgreSQL
• Cloud: AWS (EC2, RDS, S3), Docker
• Outils: Git, GitHub, JIRA, Figma

PROFIL RECHERCHÉ
• 5+ ans d'expérience en développement web
• Expertise React et Node.js
• Connaissance des architectures microservices
• Expérience avec les méthodologies Agile
• Anglais technique courant

SOFT SKILLS
• Esprit d'équipe et collaboration
• Autonomie et pro-activité
• Curiosité et passion pour la tech
• Capacité à mentorer

RÉMUNÉRATION
50 000€ à 65 000€ brut annuel
Stock-options (BSPCE)
Bonus sur objectifs

AVANTAGES
• Télétravail full remote possible
• MacBook Pro fourni
• Formation (5 jours/an, budget 2000€)
• Tickets restaurant (11€/jour)
• Mutuelle Famille prise en charge
• Congés illimités

ÉVOLUTION
Lead Developer dans 18-24 mois
Possible évolution vers CTO

PROCESS DE RECRUTEMENT
1. Entretien RH (30min)
2. Test technique (2h)
3. Entretien technique (1h)
4. Entretien avec le CTO (45min)
5. Entretien final équipe (30min)
"""
    },
    {
        "filename": "fdp_manager_marketing.txt",
        "content": """FICHE DE POSTE
Manager Marketing Digital H/F
CDI - Paris 9ème

ENTREPRISE
Groupe international (5000 personnes)
Leader sur son marché B2B
Filiale française en transformation digitale

CONTEXTE
Accélération de la transformation digitale
Nouvelle stratégie marketing omnicanale
Équipe marketing en restructuration

MISSION PRINCIPALE
Définir et mettre en œuvre la stratégie marketing digital
Manager une équipe de 6 personnes
Atteindre les objectifs de génération de leads

RESPONSABILITÉS STRATÉGIQUES
• Stratégie marketing digital et omnicanale
• Pilotage du budget marketing (800K€/an)
• Définition des KPIs et reporting
• Veille concurrentielle et market intelligence

RESPONSABILITÉS OPÉRATIONNELLES
• Campagnes digitales (SEO, SEM, Social Media)
• Marketing automation et lead nurturing
• Content marketing et communication
• Événementiel et salons professionnels

MANAGEMENT
• Encadrement d'une équipe de 6 personnes
• Recrutement et développement des talents
• Définition des objectifs et évaluation
• Coaching et formation

PROFIL RECHERCHÉ
• Formation supérieure Marketing/Commerce (Bac+5)
• 8-10 ans d'expérience en marketing digital
• Expérience de management d'équipe (5+ personnes)
• Connaissance du secteur B2B
• Anglais courant indispensable

COMPÉTENCES TECHNIQUES
• Marketing digital: SEO, SEM, Social Media, Email
• Analytics: Google Analytics, Adobe Analytics
• CRM/Marketing Automation: HubSpot, Salesforce
• Project Management: Asana, Monday, Trello

COMPÉTENCES MANAGÉRIALES
• Leadership et gestion d'équipe
• Communication et présentation
• Gestion de projets complexes
• Négociation et budget

RÉMUNÉRATION
65 000€ à 80 000€ brut annuel
Variable sur objectifs (jusqu'à 15K€)
Participation et intéressement

AVANTAGES
• Voiture de fonction ou indemnité transport
• Tickets restaurant (9€/jour)
• Mutuelle famille prise en charge
• RTT (15 jours/an)
• Formation continue
• Télétravail hybride (3 jours/semaine)

ÉVOLUTION
Directeur Marketing dans 2-3 ans
Possible mobilité internationale

LIEU
Proche République (métro 3/5/8/9/11)
Bureaux modernes avec terrasse
"""
    },
    {
        "filename": "fdp_commercial_btob.txt",
        "content": """FICHE DE POSTE
Commercial Senior BtoB H/F
CDI - Toulouse

ENTREPRISE
PME dynamique (80 personnes)
Solutions digitales pour les entreprises
Croissance soutenue depuis 5 ans

CONTEXTE
Développement commercial ambitieux
Nouveaux marchés à conquérir
Équipe commerciale en renforcement

MISSION
Développer le chiffre d'affaires sur la région Sud-Ouest
Conquérir de nouveaux comptes stratégiques
Fidéliser le portefeuille existant

RESPONSABILITÉS COMMERCIALES
• Prospection et développement grands comptes
• Négociation et closing des ventes
• Suivi et fidélisation client
• Reporting commercial hebdomadaire
• Participation aux salons professionnels

OBJECTIFS QUANTITATIFS
• CA annuel : 1,2M€ minimum
• Nouveaux clients : 20+ par an
• Taux de conversion : 30% minimum
• Portefeuille : 60 comptes actifs

PROFIL RECHERCHÉ
• Formation commerciale Bac+3/5
• 5-8 ans d'expérience en vente BtoB
• Connaissance du secteur IT/Digital appréciée
• Maîtrise des outils CRM (Salesforce)
• Permis B et véhicule indispensable

COMPÉTENCES COMMERCIALES
• Prospection multicanale
• Négociation et closing
• Présentation et pitch
• Analyse des besoins clients
• Gestion de la relation client

COMPÉTENCES TECHNIQUES
• CRM : Salesforce, HubSpot
• Prospection : LinkedIn Sales Navigator
• Bureautique : Suite Office
• Présentation : PowerPoint, Prezi

RÉMUNÉRATION
Fixe : 35 000€ à 40 000€ brut annuel
Variable : 15 000€ à 25 000€ (non plafonné)
Voiture de fonction + carte essence

AVANTAGES
• Commission attractive sans plafond
• Primes sur objectifs trimestriels
• Mutuelle entreprise
• Tickets restaurant (8€/jour)
• RTT (10 jours/an)
• Formation commerciale continue

TERRITOIRE
Occitanie (Toulouse, Montpellier, Nîmes)
Déplacements 2-3 jours/semaine
Clientèle : PME/ETI 50-500 salariés

ÉVOLUTION
Responsable Commercial Régional
Directeur Commercial adjoint
"""
    },
    {
        "filename": "fdp_responsable_rh.txt",
        "content": """FICHE DE POSTE
Responsable RH Généraliste H/F
CDI - Nantes

ENTREPRISE
Groupe industriel (300 personnes)
Secteur agroalimentaire
Valeurs familiales et humaines

CONTEXTE
Modernisation des pratiques RH
Digitalisation des processus
Accompagnement de la croissance

MISSION PRINCIPALE
Piloter la fonction RH en autonomie
Accompagner les managers dans leurs défis RH
Développer les talents et la culture d'entreprise

RESPONSABILITÉS RH
• Recrutement et intégration (40+ postes/an)
• Gestion administrative du personnel
• Paie et avantages sociaux
• Formation et développement des compétences
• Relations sociales et dialogue social

RESPONSABILITÉS STRATÉGIQUES
• Définition de la politique RH
• Pilotage des indicateurs RH
• Gestion prévisionnelle des emplois
• Projets d'organisation et changement

PROFIL RECHERCHÉ
• Formation RH/Psychologie/Droit (Bac+5)
• 5-8 ans d'expérience RH généraliste
• Connaissance du droit du travail
• Expérience en industrie appréciée
• Maîtrise des SIRH (de préférence Workday)

COMPÉTENCES TECHNIQUES
• Recrutement et évaluation
• Droit du travail et paie
• Formation et développement
• SIRH et digitalisation RH
• Indicateurs et reporting RH

COMPÉTENCES RELATIONNELLES
• Écoute et communication
• Négociation et médiation
• Confidentialité et éthique
• Adaptabilité et résilience

RÉMUNÉRATION
45 000€ à 52 000€ brut annuel
Prime annuelle sur objectifs
Participation aux bénéfices

AVANTAGES
• Véhicule de fonction
• Tickets restaurant (9€/jour)
• Mutuelle famille prise en charge
• RTT (12 jours/an)
• Formation continue
• Épargne salariale

ENVIRONNEMENT
Bureaux dans zone industrielle
Parking gratuit
Restaurant d'entreprise
Salle de sport sur site

ÉVOLUTION
DRH dans 3-5 ans
Possible mobilité dans le groupe
Missions internationales possibles
"""
    }
]

def create_folder_structure():
    """Crée la structure des dossiers"""
    print(f"{Colors.YELLOW}📁 Création des dossiers...{Colors.END}")
    
    # Créer les dossiers
    CV_FOLDER.mkdir(exist_ok=True)
    FDP_FOLDER.mkdir(exist_ok=True)
    
    print(f"  ✅ Dossier CV créé : {Colors.GREEN}{CV_FOLDER}{Colors.END}")
    print(f"  ✅ Dossier FDP créé : {Colors.GREEN}{FDP_FOLDER}{Colors.END}")

def generate_cv_files():
    """Génère les fichiers CV d'exemple"""
    print(f"{Colors.YELLOW}📄 Génération des CVs d'exemple...{Colors.END}")
    
    for cv_data in CV_EXAMPLES:
        cv_path = CV_FOLDER / cv_data["filename"]
        
        with open(cv_path, 'w', encoding='utf-8') as f:
            f.write(cv_data["content"])
        
        file_size = cv_path.stat().st_size / 1024  # KB
        print(f"  ✅ {cv_data['filename']} : {Colors.GREEN}{file_size:.1f} KB{Colors.END}")

def generate_fdp_files():
    """Génère les fichiers FDP d'exemple"""
    print(f"{Colors.YELLOW}📋 Génération des FDPs d'exemple...{Colors.END}")
    
    for fdp_data in FDP_EXAMPLES:
        fdp_path = FDP_FOLDER / fdp_data["filename"]
        
        with open(fdp_path, 'w', encoding='utf-8') as f:
            f.write(fdp_data["content"])
        
        file_size = fdp_path.stat().st_size / 1024  # KB
        print(f"  ✅ {fdp_data['filename']} : {Colors.GREEN}{file_size:.1f} KB{Colors.END}")

def generate_summary_file():
    """Génère un fichier de résumé"""
    summary_data = {
        "generated_at": datetime.now().isoformat(),
        "description": "Données d'exemple générées pour tester Nextvision V3.0",
        "cv_files": [cv["filename"] for cv in CV_EXAMPLES],
        "fdp_files": [fdp["filename"] for fdp in FDP_EXAMPLES],
        "total_files": len(CV_EXAMPLES) + len(FDP_EXAMPLES),
        "profiles_covered": [
            "Comptable Senior",
            "Développeur Full-Stack",
            "Manager Marketing",
            "Commercial BtoB",
            "Responsable RH"
        ],
        "sectors": [
            "Comptabilité/Finance",
            "Technologie/IT",
            "Marketing/Communication",
            "Vente/Commerce",
            "Ressources Humaines"
        ],
        "note": "Ces données sont fictives et créées uniquement pour les tests"
    }
    
    summary_path = DESKTOP_PATH / "nextvision_sample_data_summary.json"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Résumé généré : {Colors.GREEN}{summary_path}{Colors.END}")

def main():
    """Point d'entrée principal"""
    print(f"{Colors.BOLD}{Colors.CYAN}📁 === GÉNÉRATEUR DE DONNÉES D'EXEMPLE - NEXTVISION V3.0 ==={Colors.END}")
    print(f"{Colors.BLUE}Crée des CVs et FDPs d'exemple pour tester le système{Colors.END}")
    print()
    
    # Vérifier si les dossiers existent déjà
    cv_exists = CV_FOLDER.exists() and any(CV_FOLDER.iterdir())
    fdp_exists = FDP_FOLDER.exists() and any(FDP_FOLDER.iterdir())
    
    if cv_exists or fdp_exists:
        print(f"{Colors.YELLOW}⚠️  Des dossiers de test existent déjà :{Colors.END}")
        if cv_exists:
            cv_count = len(list(CV_FOLDER.iterdir()))
            print(f"  📄 {CV_FOLDER} : {cv_count} fichiers")
        if fdp_exists:
            fdp_count = len(list(FDP_FOLDER.iterdir()))
            print(f"  📋 {FDP_FOLDER} : {fdp_count} fichiers")
        
        print()
        choice = input(f"{Colors.BOLD}Remplacer les fichiers existants ? (y/n): {Colors.END}")
        
        if choice.lower() not in ['y', 'yes', 'o', 'oui']:
            print(f"{Colors.YELLOW}⏸️  Génération annulée{Colors.END}")
            return
    
    try:
        # Générer les données
        create_folder_structure()
        generate_cv_files()
        generate_fdp_files()
        generate_summary_file()
        
        print()
        print(f"{Colors.BOLD}{Colors.GREEN}✅ === GÉNÉRATION TERMINÉE ==={Colors.END}")
        print(f"📊 Fichiers générés :")
        print(f"  • {Colors.GREEN}{len(CV_EXAMPLES)} CVs{Colors.END} dans {CV_FOLDER}")
        print(f"  • {Colors.GREEN}{len(FDP_EXAMPLES)} FDPs{Colors.END} dans {FDP_FOLDER}")
        print(f"  • {Colors.GREEN}1 résumé{Colors.END} sur le Bureau")
        
        print()
        print(f"{Colors.BOLD}🚀 Prochaines étapes :{Colors.END}")
        print(f"  1. Lancez l'API : {Colors.CYAN}python api_startup_script.py{Colors.END}")
        print(f"  2. Testez le système : {Colors.CYAN}python test_real_data_nextvision.py{Colors.END}")
        print(f"  3. Consultez les résultats dans les rapports générés")
        
        print()
        print(f"{Colors.YELLOW}💡 Note : Ces données sont fictives et créées uniquement pour les tests{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur lors de la génération : {e}{Colors.END}")
        return

if __name__ == "__main__":
    main()
