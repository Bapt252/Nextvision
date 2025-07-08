#!/usr/bin/env python3
"""
Visualiseur Analytics pour Nextvision v2.0
Génère des graphiques et analyses visuelles des résultats de test
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

class NextvisionVisualizer:
    """Générateur de visualisations pour les résultats Nextvision"""
    
    def __init__(self, results_file: str):
        """Initialise avec un fichier de résultats JSON"""
        with open(results_file, 'r') as f:
            self.raw_results = json.load(f)
        
        # Filtrage des résultats réussis
        successful_results = [r for r in self.raw_results if r.get('status') == 'success']
        self.df = pd.DataFrame(successful_results) if successful_results else pd.DataFrame()
        
        if not self.df.empty:
            self._prepare_dataframe()
        
        # Configuration style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def _prepare_dataframe(self):
        """Prépare le DataFrame pour l'analyse"""
        # Extraction des données imbriquées
        candidate_data = pd.json_normalize(self.df['candidate_profile'])
        company_data = pd.json_normalize(self.df['company_profile'])
        
        # Ajout des préfixes pour éviter les conflits
        candidate_data.columns = ['candidate_' + col for col in candidate_data.columns]
        company_data.columns = ['company_' + col for col in company_data.columns]
        
        # Fusion avec le DataFrame principal
        self.df = pd.concat([
            self.df.drop(['candidate_profile', 'company_profile'], axis=1),
            candidate_data,
            company_data
        ], axis=1)
        
        # Extraction des composants de score si disponible
        if 'components' in self.df.columns:
            components_data = pd.json_normalize(self.df['components'])
            components_data.columns = ['score_' + col for col in components_data.columns]
            self.df = pd.concat([self.df, components_data], axis=1)
    
    def generate_dashboard(self, output_dir: str = "visualizations"):
        """Génère un dashboard complet"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if self.df.empty:
            print("❌ Aucune donnée à visualiser")
            return
        
        print("🎨 Génération du dashboard Nextvision...")
        
        # 1. Distribution des scores
        self._plot_score_distribution(output_path)
        
        # 2. Analyse des performances
        self._plot_performance_analysis(output_path)
        
        # 3. Impact des questionnaires
        self._plot_questionnaire_impact(output_path)
        
        # 4. Heatmap des corrélations
        self._plot_correlation_heatmap(output_path)
        
        # 5. Analyse temporelle
        self._plot_temporal_analysis(output_path)
        
        # 6. Dashboard interactif Plotly
        self._create_interactive_dashboard(output_path)
        
        print(f"✅ Dashboard généré dans {output_path}")
    
    def _plot_score_distribution(self, output_path: Path):
        """Distribution des scores avec stats descriptives"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('📊 Distribution des Scores Nextvision v2.0', fontsize=16, fontweight='bold')
        
        scores = self.df['score']
        
        # Histogramme
        ax1.hist(scores, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(scores.mean(), color='red', linestyle='--', label=f'Moyenne: {scores.mean():.3f}')
        ax1.axvline(scores.median(), color='green', linestyle='--', label=f'Médiane: {scores.median():.3f}')
        ax1.set_xlabel('Score')
        ax1.set_ylabel('Fréquence')
        ax1.set_title('Distribution des Scores')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot
        ax2.boxplot(scores, vert=True, patch_artist=True, 
                   boxprops=dict(facecolor='lightblue', alpha=0.7))
        ax2.set_ylabel('Score')
        ax2.set_title('Box Plot des Scores')
        ax2.grid(True, alpha=0.3)
        
        # Q-Q plot pour normalité
        from scipy import stats
        stats.probplot(scores, dist="norm", plot=ax3)
        ax3.set_title('Q-Q Plot (Test de Normalité)')
        ax3.grid(True, alpha=0.3)
        
        # Pie chart par catégorie
        categories = {
            'Excellent (>0.8)': (scores > 0.8).sum(),
            'Bon (0.6-0.8)': ((scores >= 0.6) & (scores <= 0.8)).sum(),
            'Moyen (0.4-0.6)': ((scores >= 0.4) & (scores < 0.6)).sum(),
            'Faible (<0.4)': (scores < 0.4).sum()
        }
        
        colors = ['#2ecc71', '#f39c12', '#e74c3c', '#95a5a6']
        ax4.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', 
                colors=colors, startangle=90)
        ax4.set_title('Répartition par Catégorie')
        
        plt.tight_layout()
        plt.savefig(output_path / 'score_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_performance_analysis(self, output_path: Path):
        """Analyse des performances temporelles"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('⚡ Analyse des Performances', fontsize=16, fontweight='bold')
        
        exec_times = self.df['execution_time']
        
        # Scatter plot temps vs score
        ax1.scatter(exec_times, self.df['score'], alpha=0.6, color='coral')
        ax1.set_xlabel('Temps d\'exécution (s)')
        ax1.set_ylabel('Score')
        ax1.set_title('Corrélation Temps vs Score')
        ax1.grid(True, alpha=0.3)
        
        # Distribution des temps
        ax2.hist(exec_times, bins=25, alpha=0.7, color='lightgreen', edgecolor='black')
        ax2.axvline(exec_times.mean(), color='red', linestyle='--', 
                   label=f'Moyenne: {exec_times.mean():.3f}s')
        ax2.set_xlabel('Temps d\'exécution (s)')
        ax2.set_ylabel('Fréquence')
        ax2.set_title('Distribution des Temps')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Performance par CV (top 10)
        cv_perf = self.df.groupby('cv_file')['execution_time'].mean().sort_values().head(10)
        ax3.barh(range(len(cv_perf)), cv_perf.values, color='steelblue')
        ax3.set_yticks(range(len(cv_perf)))
        ax3.set_yticklabels([name[:15] + '...' if len(name) > 15 else name 
                            for name in cv_perf.index], fontsize=8)
        ax3.set_xlabel('Temps moyen (s)')
        ax3.set_title('CVs les Plus Rapides')
        ax3.grid(True, alpha=0.3)
        
        # Performance par FDP (top 10)
        fdp_perf = self.df.groupby('fdp_file')['execution_time'].mean().sort_values().head(10)
        ax4.barh(range(len(fdp_perf)), fdp_perf.values, color='darkorange')
        ax4.set_yticks(range(len(fdp_perf)))
        ax4.set_yticklabels([name[:15] + '...' if len(name) > 15 else name 
                            for name in fdp_perf.index], fontsize=8)
        ax4.set_xlabel('Temps moyen (s)')
        ax4.set_title('FDPs les Plus Rapides')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / 'performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_questionnaire_impact(self, output_path: Path):
        """Impact des réponses questionnaires sur les scores"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('🎯 Impact des Questionnaires sur les Scores', fontsize=16, fontweight='bold')
        
        # Impact raison d'écoute candidat
        if 'candidate_listening_reason' in self.df.columns:
            listening_scores = self.df.groupby('candidate_listening_reason')['score'].agg(['mean', 'std', 'count'])
            
            ax1.bar(listening_scores.index, listening_scores['mean'], 
                   yerr=listening_scores['std'], capsize=5, alpha=0.7, color='lightcoral')
            ax1.set_ylabel('Score Moyen')
            ax1.set_title('Impact Raison d\'Écoute Candidat')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            
            # Annotations avec effectifs
            for i, (idx, row) in enumerate(listening_scores.iterrows()):
                ax1.annotate(f'n={row["count"]}', 
                           xy=(i, row['mean'] + row['std']), 
                           ha='center', fontsize=8)
        
        # Impact urgence entreprise
        if 'company_urgency_level' in self.df.columns:
            urgency_scores = self.df.groupby('company_urgency_level')['score'].agg(['mean', 'std', 'count'])
            
            ax2.bar(urgency_scores.index, urgency_scores['mean'],
                   yerr=urgency_scores['std'], capsize=5, alpha=0.7, color='lightblue')
            ax2.set_ylabel('Score Moyen')
            ax2.set_title('Impact Urgence Entreprise')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
            
            for i, (idx, row) in enumerate(urgency_scores.iterrows()):
                ax2.annotate(f'n={row["count"]}', 
                           xy=(i, row['mean'] + row['std']), 
                           ha='center', fontsize=8)
        
        # Heatmap croisée raison écoute × urgence
        if 'candidate_listening_reason' in self.df.columns and 'company_urgency_level' in self.df.columns:
            cross_table = self.df.pivot_table(
                values='score', 
                index='candidate_listening_reason',
                columns='company_urgency_level',
                aggfunc='mean'
            )
            
            sns.heatmap(cross_table, annot=True, fmt='.3f', cmap='RdYlBu_r', ax=ax3)
            ax3.set_title('Heatmap Croisée: Raison × Urgence')
            ax3.set_xlabel('Urgence Entreprise')
            ax3.set_ylabel('Raison Écoute Candidat')
        
        # Box plot par niveau d'expérience
        if 'candidate_experience_level' in self.df.columns:
            exp_data = [self.df[self.df['candidate_experience_level'] == level]['score'].values 
                       for level in self.df['candidate_experience_level'].unique()]
            
            bp = ax4.boxplot(exp_data, labels=self.df['candidate_experience_level'].unique(),
                           patch_artist=True)
            
            colors = ['lightgreen', 'lightcoral', 'lightblue', 'lightyellow']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
            
            ax4.set_ylabel('Score')
            ax4.set_title('Distribution par Niveau d\'Expérience')
            ax4.tick_params(axis='x', rotation=45)
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / 'questionnaire_impact.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_correlation_heatmap(self, output_path: Path):
        """Heatmap des corrélations entre variables"""
        # Sélection des colonnes numériques pour corrélation
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        correlation_data = self.df[numeric_cols]
        
        # Calcul matrice de corrélation
        corr_matrix = correlation_data.corr()
        
        # Création de la figure
        plt.figure(figsize=(12, 10))
        
        # Heatmap avec annotations
        sns.heatmap(corr_matrix, 
                   annot=True, 
                   fmt='.2f', 
                   cmap='RdYlBu_r',
                   center=0,
                   square=True,
                   cbar_kws={"shrink": .8})
        
        plt.title('🔗 Matrice de Corrélation des Variables Numériques', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(output_path / 'correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_temporal_analysis(self, output_path: Path):
        """Analyse temporelle si applicable"""
        # Simulation d'ordre temporel basé sur l'index
        self.df['test_order'] = range(len(self.df))
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle('📈 Analyse Temporelle des Tests', fontsize=16, fontweight='bold')
        
        # Évolution des scores dans le temps
        window_size = max(1, len(self.df) // 20)  # Fenêtre mobile 5% des données
        rolling_score = self.df['score'].rolling(window=window_size, center=True).mean()
        
        ax1.plot(self.df['test_order'], self.df['score'], alpha=0.3, color='lightblue', label='Scores individuels')
        ax1.plot(self.df['test_order'], rolling_score, color='red', linewidth=2, label=f'Moyenne mobile ({window_size})')
        ax1.axhline(self.df['score'].mean(), color='green', linestyle='--', label='Moyenne globale')
        ax1.set_xlabel('Ordre de Test')
        ax1.set_ylabel('Score')
        ax1.set_title('Évolution des Scores')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Évolution des temps d'exécution
        rolling_time = self.df['execution_time'].rolling(window=window_size, center=True).mean()
        
        ax2.plot(self.df['test_order'], self.df['execution_time'], alpha=0.3, color='lightcoral', label='Temps individuels')
        ax2.plot(self.df['test_order'], rolling_time, color='blue', linewidth=2, label=f'Moyenne mobile ({window_size})')
        ax2.axhline(self.df['execution_time'].mean(), color='orange', linestyle='--', label='Moyenne globale')
        ax2.set_xlabel('Ordre de Test')
        ax2.set_ylabel('Temps d\'exécution (s)')
        ax2.set_title('Évolution des Performances')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / 'temporal_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_interactive_dashboard(self, output_path: Path):
        """Crée un dashboard interactif avec Plotly"""
        # Création des sous-graphiques
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribution des Scores', 'Performance vs Score', 
                          'Impact Questionnaires', 'Évolution Temporelle'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Histogramme interactif des scores
        fig.add_trace(
            go.Histogram(x=self.df['score'], name='Scores', nbinsx=30,
                        marker_color='rgba(55, 83, 109, 0.6)'),
            row=1, col=1
        )
        
        # 2. Scatter plot performance vs score
        fig.add_trace(
            go.Scatter(x=self.df['execution_time'], y=self.df['score'],
                      mode='markers', name='Tests',
                      marker=dict(color=self.df['score'], colorscale='Viridis',
                                showscale=True),
                      text=[f"CV: {cv}<br>FDP: {fdp}" 
                           for cv, fdp in zip(self.df['cv_file'], self.df['fdp_file'])]),
            row=1, col=2
        )
        
        # 3. Box plot par raison d'écoute (si disponible)
        if 'candidate_listening_reason' in self.df.columns:
            for reason in self.df['candidate_listening_reason'].unique():
                data = self.df[self.df['candidate_listening_reason'] == reason]['score']
                fig.add_trace(
                    go.Box(y=data, name=reason, showlegend=False),
                    row=2, col=1
                )
        
        # 4. Ligne temporelle
        fig.add_trace(
            go.Scatter(x=self.df.index, y=self.df['score'],
                      mode='lines+markers', name='Évolution Score',
                      line=dict(color='rgb(205, 12, 24)', width=2)),
            row=2, col=2
        )
        
        # Mise à jour du layout
        fig.update_layout(
            height=800,
            title_text="🚀 Dashboard Interactif Nextvision v2.0",
            title_x=0.5,
            showlegend=True
        )
        
        # Sauvegarde du dashboard interactif
        pyo.plot(fig, filename=str(output_path / 'interactive_dashboard.html'), auto_open=False)
        
    def generate_summary_report(self) -> str:
        """Génère un rapport textuel résumé"""
        if self.df.empty:
            return "❌ Aucune donnée disponible pour le rapport"
        
        total_tests = len(self.df)
        avg_score = self.df['score'].mean()
        avg_time = self.df['execution_time'].mean()
        
        report = f"""
🚀 RAPPORT DE SYNTHÈSE NEXTVISION v2.0
{'='*50}

📊 STATISTIQUES GÉNÉRALES:
• Total tests réussis: {total_tests:,}
• Score moyen: {avg_score:.3f} ± {self.df['score'].std():.3f}
• Temps moyen: {avg_time:.3f}s
• Débit: {total_tests/self.df['execution_time'].sum():.1f} tests/s

🎯 DISTRIBUTION DES SCORES:
• Excellent (>0.8): {(self.df['score'] > 0.8).sum():,} ({(self.df['score'] > 0.8).mean()*100:.1f}%)
• Bon (0.6-0.8): {((self.df['score'] >= 0.6) & (self.df['score'] <= 0.8)).sum():,} ({((self.df['score'] >= 0.6) & (self.df['score'] <= 0.8)).mean()*100:.1f}%)
• Moyen (0.4-0.6): {((self.df['score'] >= 0.4) & (self.df['score'] < 0.6)).sum():,} ({((self.df['score'] >= 0.4) & (self.df['score'] < 0.6)).mean()*100:.1f}%)
• Faible (<0.4): {(self.df['score'] < 0.4).sum():,} ({(self.df['score'] < 0.4).mean()*100:.1f}%)

⚡ PERFORMANCES:
• Temps min: {self.df['execution_time'].min():.3f}s
• Temps max: {self.df['execution_time'].max():.3f}s
• P95: {self.df['execution_time'].quantile(0.95):.3f}s
• Variance: {self.df['execution_time'].var():.6f}

🔍 COHÉRENCE:
• CVs uniques: {self.df['cv_file'].nunique()}
• FDPs uniques: {self.df['fdp_file'].nunique()}
• Tests par CV: {total_tests / self.df['cv_file'].nunique():.1f}
• Tests par FDP: {total_tests / self.df['fdp_file'].nunique():.1f}
"""
        
        # Ajout statistiques questionnaires si disponibles
        if 'candidate_listening_reason' in self.df.columns:
            report += f"\n🎮 IMPACT QUESTIONNAIRES CANDIDAT:\n"
            for reason in self.df['candidate_listening_reason'].unique():
                avg_score_reason = self.df[self.df['candidate_listening_reason'] == reason]['score'].mean()
                count = (self.df['candidate_listening_reason'] == reason).sum()
                report += f"• {reason}: {avg_score_reason:.3f} (n={count})\n"
        
        if 'company_urgency_level' in self.df.columns:
            report += f"\n🏢 IMPACT QUESTIONNAIRES ENTREPRISE:\n"
            for urgency in self.df['company_urgency_level'].unique():
                avg_score_urgency = self.df[self.df['company_urgency_level'] == urgency]['score'].mean()
                count = (self.df['company_urgency_level'] == urgency).sum()
                report += f"• {urgency}: {avg_score_urgency:.3f} (n={count})\n"
        
        return report

def main():
    """Fonction principale de visualisation"""
    print("🎨 NEXTVISION v2.0 - GÉNÉRATEUR DE VISUALISATIONS")
    print("=" * 55)
    
    # Sélection du fichier de résultats
    import glob
    
    result_files = glob.glob("nextvision_test_results/raw_results_*.json")
    
    if not result_files:
        print("❌ Aucun fichier de résultats trouvé dans nextvision_test_results/")
        print("💡 Exécutez d'abord le test massif")
        return
    
    # Sélection du fichier le plus récent par défaut
    latest_file = max(result_files, key=lambda x: Path(x).stat().st_mtime)
    print(f"📁 Fichier trouvé: {latest_file}")
    
    # Création du visualiseur
    try:
        visualizer = NextvisionVisualizer(latest_file)
        
        # Génération du dashboard
        visualizer.generate_dashboard()
        
        # Affichage du rapport résumé
        print("\n" + visualizer.generate_summary_report())
        
        print(f"\n✅ Visualisations générées dans le dossier 'visualizations/'")
        print("🌐 Ouvrez 'interactive_dashboard.html' pour le dashboard interactif")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")

if __name__ == "__main__":
    main()