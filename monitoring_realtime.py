#!/usr/bin/env python3
"""
📊 NEXTVISION V3.2.1 - MONITORING TEMPS RÉEL

Surveillance continue de l'API pendant les tests :
- Health checks automatiques
- Métriques de performance
- Alertes en temps réel
- Dashboard console
- Logs structurés

Version: 3.2.1
Date: 2025-07-11
Auteur: Assistant Claude
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse
import signal
import sys
import os

@dataclass
class HealthMetrics:
    """Métriques de santé de l'API"""
    timestamp: datetime
    response_time_ms: float
    status_code: int
    success: bool
    endpoint: str
    error_message: Optional[str] = None

@dataclass
class PerformanceSnapshot:
    """Instantané des performances"""
    timestamp: datetime
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    success_rate: float
    requests_per_minute: float
    active_endpoints: int
    total_requests: int

class NextvisionMonitor:
    """Monitoring en temps réel de Nextvision V3.2.1"""
    
    def __init__(self, base_url: str = "http://localhost:8001", interval: int = 5):
        self.base_url = base_url
        self.interval = interval
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        
        # Stockage des métriques
        self.health_history: List[HealthMetrics] = []
        self.performance_history: List[PerformanceSnapshot] = []
        
        # Configuration des endpoints à surveiller
        self.endpoints = [
            "/api/v1/health",
            "/api/v2/maps/health",
            "/api/v1/integration/health",
            "/docs"
        ]
        
        # Statistiques globales
        self.start_time = None
        self.total_requests = 0
        self.total_errors = 0
        
        # Configuration des alertes
        self.alert_thresholds = {
            'response_time_ms': 2000,
            'success_rate': 0.95,
            'consecutive_failures': 3
        }
        
        self.consecutive_failures = 0
        self.last_alert_time = None
        
    async def __aenter__(self):
        """Initialisation asynchrone"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage asynchrone"""
        if self.session:
            await self.session.close()
    
    async def check_endpoint_health(self, endpoint: str) -> HealthMetrics:
        """Vérifie la santé d'un endpoint"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.base_url}{endpoint}") as response:
                response_time = (time.time() - start_time) * 1000
                success = response.status == 200
                
                return HealthMetrics(
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    status_code=response.status,
                    success=success,
                    endpoint=endpoint,
                    error_message=None
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthMetrics(
                timestamp=datetime.now(),
                response_time_ms=response_time,
                status_code=0,
                success=False,
                endpoint=endpoint,
                error_message=str(e)
            )
    
    async def check_all_endpoints(self) -> List[HealthMetrics]:
        """Vérifie tous les endpoints"""
        tasks = [self.check_endpoint_health(endpoint) for endpoint in self.endpoints]
        results = await asyncio.gather(*tasks)
        
        # Ajouter à l'historique
        self.health_history.extend(results)
        
        # Nettoyer l'historique (garder seulement les 1000 dernières mesures)
        if len(self.health_history) > 1000:
            self.health_history = self.health_history[-1000:]
        
        self.total_requests += len(results)
        
        return results
    
    def calculate_performance_snapshot(self) -> PerformanceSnapshot:
        """Calcule un instantané des performances"""
        if not self.health_history:
            return PerformanceSnapshot(
                timestamp=datetime.now(),
                avg_response_time=0,
                max_response_time=0,
                min_response_time=0,
                success_rate=0,
                requests_per_minute=0,
                active_endpoints=0,
                total_requests=0
            )
        
        # Calculer sur les 10 dernières minutes
        cutoff_time = datetime.now() - timedelta(minutes=10)
        recent_metrics = [m for m in self.health_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            recent_metrics = self.health_history[-50:]  # Au moins les 50 dernières
        
        # Métriques de performance
        response_times = [m.response_time_ms for m in recent_metrics]
        successful_requests = [m for m in recent_metrics if m.success]
        
        # Calcul du taux de requêtes par minute
        if len(recent_metrics) >= 2:
            time_span_minutes = (recent_metrics[-1].timestamp - recent_metrics[0].timestamp).total_seconds() / 60
            requests_per_minute = len(recent_metrics) / max(time_span_minutes, 1)
        else:
            requests_per_minute = 0
        
        # Endpoints actifs (ayant répondu dans les 5 dernières minutes)
        recent_cutoff = datetime.now() - timedelta(minutes=5)
        active_endpoints = len(set(
            m.endpoint for m in self.health_history 
            if m.timestamp >= recent_cutoff and m.success
        ))
        
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            success_rate=len(successful_requests) / len(recent_metrics) if recent_metrics else 0,
            requests_per_minute=requests_per_minute,
            active_endpoints=active_endpoints,
            total_requests=self.total_requests
        )
        
        self.performance_history.append(snapshot)
        
        # Nettoyer l'historique des performances
        if len(self.performance_history) > 200:
            self.performance_history = self.performance_history[-200:]
        
        return snapshot
    
    def check_alerts(self, current_metrics: List[HealthMetrics], performance: PerformanceSnapshot):
        """Vérifie et déclenche les alertes"""
        alerts = []
        
        # Alerte sur le temps de réponse
        if performance.avg_response_time > self.alert_thresholds['response_time_ms']:
            alerts.append(f"🐌 Temps de réponse élevé: {performance.avg_response_time:.0f}ms")
        
        # Alerte sur le taux de succès
        if performance.success_rate < self.alert_thresholds['success_rate']:
            alerts.append(f"⚠️ Taux de succès faible: {performance.success_rate:.1%}")
        
        # Alerte sur les échecs consécutifs
        current_failures = sum(1 for m in current_metrics if not m.success)
        if current_failures > 0:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.alert_thresholds['consecutive_failures']:
                alerts.append(f"🚨 {self.consecutive_failures} échecs consécutifs")
        else:
            self.consecutive_failures = 0
        
        # Alerte sur les endpoints inactifs
        if performance.active_endpoints < len(self.endpoints) / 2:
            alerts.append(f"📡 Endpoints inactifs: {performance.active_endpoints}/{len(self.endpoints)}")
        
        # Afficher les alertes (avec limitation de fréquence)
        if alerts and (not self.last_alert_time or 
                      datetime.now() - self.last_alert_time > timedelta(minutes=1)):
            self.display_alerts(alerts)
            self.last_alert_time = datetime.now()
    
    def display_alerts(self, alerts: List[str]):
        """Affiche les alertes"""
        print("\n" + "🚨 " * 10 + " ALERTES " + "🚨 " * 10)
        for alert in alerts:
            print(f"  {alert}")
        print("🚨 " * 30 + "\n")
    
    def display_dashboard(self, current_metrics: List[HealthMetrics], performance: PerformanceSnapshot):
        """Affiche le dashboard en temps réel"""
        # Effacer l'écran (compatible Unix/Windows)
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # En-tête
        print("📊 NEXTVISION V3.2.1 - MONITORING TEMPS RÉEL")
        print("=" * 60)
        print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Intervalle: {self.interval}s")
        print()
        
        # État global
        global_status = "🟢 SAIN" if performance.success_rate >= 0.95 else "🟡 DÉGRADÉ" if performance.success_rate >= 0.8 else "🔴 CRITIQUE"
        print(f"État global: {global_status}")
        print(f"Temps de fonctionnement: {self._format_uptime()}")
        print()
        
        # Métriques en temps réel
        print("📈 PERFORMANCES ACTUELLES")
        print("-" * 30)
        print(f"Temps de réponse moyen: {performance.avg_response_time:.0f}ms")
        print(f"Temps de réponse max:   {performance.max_response_time:.0f}ms")
        print(f"Taux de succès:         {performance.success_rate:.1%}")
        print(f"Requêtes/minute:        {performance.requests_per_minute:.1f}")
        print(f"Endpoints actifs:       {performance.active_endpoints}/{len(self.endpoints)}")
        print()
        
        # État des endpoints
        print("🔗 ÉTAT DES ENDPOINTS")
        print("-" * 30)
        for metric in current_metrics:
            status_icon = "✅" if metric.success else "❌"
            status_text = f"({metric.status_code})" if metric.success else f"({metric.error_message[:30]}...)"
            print(f"{status_icon} {metric.endpoint:<25} {metric.response_time_ms:>6.0f}ms {status_text}")
        print()
        
        # Historique des performances (graphique ASCII simple)
        print("📊 HISTORIQUE TEMPS DE RÉPONSE (10 dernières mesures)")
        print("-" * 30)
        if len(self.performance_history) >= 2:
            recent_history = self.performance_history[-10:]
            max_time = max(p.avg_response_time for p in recent_history)
            
            for i, perf in enumerate(recent_history):
                bar_length = int((perf.avg_response_time / max_time) * 20) if max_time > 0 else 0
                bar = "█" * bar_length + "░" * (20 - bar_length)
                timestamp = perf.timestamp.strftime("%H:%M:%S")
                print(f"{timestamp} |{bar}| {perf.avg_response_time:>6.0f}ms")
        else:
            print("Collecte des données en cours...")
        print()
        
        # Statistiques globales
        print("📊 STATISTIQUES GLOBALES")
        print("-" * 30)
        print(f"Total requêtes:      {self.total_requests}")
        print(f"Requêtes réussies:   {self.total_requests - self.total_errors}")
        print(f"Requêtes échouées:   {self.total_errors}")
        if self.total_requests > 0:
            print(f"Taux de réussite:    {((self.total_requests - self.total_errors) / self.total_requests):.1%}")
        print()
        
        # Instructions
        print("🎛️ CONTRÔLES")
        print("-" * 30)
        print("Ctrl+C pour arrêter le monitoring")
        print("Ctrl+Z pour mettre en pause (puis 'fg' pour reprendre)")
        print()
    
    def _format_uptime(self) -> str:
        """Formate le temps de fonctionnement"""
        if not self.start_time:
            return "0s"
        
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def save_monitoring_report(self):
        """Sauvegarde un rapport de monitoring"""
        if not self.performance_history:
            return
        
        report = {
            "monitoring_session": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                "total_requests": self.total_requests,
                "total_errors": self.total_errors
            },
            "performance_summary": {
                "avg_response_time": statistics.mean([p.avg_response_time for p in self.performance_history]),
                "max_response_time": max([p.max_response_time for p in self.performance_history]),
                "avg_success_rate": statistics.mean([p.success_rate for p in self.performance_history]),
                "avg_requests_per_minute": statistics.mean([p.requests_per_minute for p in self.performance_history])
            },
            "performance_history": [asdict(p) for p in self.performance_history[-50:]],  # 50 dernières mesures
            "health_history": [asdict(h) for h in self.health_history[-200:]]  # 200 dernières mesures
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nextvision_monitoring_report_{timestamp}.json"
        
        # Convertir les datetime en string pour JSON
        def datetime_converter(o):
            if isinstance(o, datetime):
                return o.isoformat()
            raise TypeError(f"Object of type {type(o)} is not JSON serializable")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=datetime_converter)
        
        print(f"\n💾 Rapport de monitoring sauvegardé: {filename}")
    
    async def monitor_loop(self):
        """Boucle principale de monitoring"""
        self.running = True
        self.start_time = datetime.now()
        
        print("🚀 Démarrage du monitoring Nextvision V3.2.1...")
        print(f"URL cible: {self.base_url}")
        print(f"Intervalle: {self.interval}s")
        print("Appuyez sur Ctrl+C pour arrêter\n")
        
        while self.running:
            try:
                # Vérifier tous les endpoints
                current_metrics = await self.check_all_endpoints()
                
                # Calculer les performances
                performance = self.calculate_performance_snapshot()
                
                # Vérifier les alertes
                self.check_alerts(current_metrics, performance)
                
                # Afficher le dashboard
                self.display_dashboard(current_metrics, performance)
                
                # Attendre l'intervalle suivant
                await asyncio.sleep(self.interval)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"❌ Erreur dans la boucle de monitoring: {e}")
                await asyncio.sleep(1)
    
    async def run(self):
        """Lance le monitoring"""
        try:
            await self.monitor_loop()
        except KeyboardInterrupt:
            pass
        finally:
            print("\n🛑 Arrêt du monitoring...")
            self.save_monitoring_report()
            print("✅ Monitoring terminé")


async def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Monitoring temps réel Nextvision V3.2.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python monitoring_realtime.py                    # Monitoring standard (5s)
  python monitoring_realtime.py --interval 2      # Monitoring rapide (2s)
  python monitoring_realtime.py --url http://localhost:8002  # URL personnalisée
        """
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:8001',
        help='URL de base de l\'API Nextvision (défaut: http://localhost:8001)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Intervalle entre les vérifications en secondes (défaut: 5)'
    )
    
    args = parser.parse_args()
    
    # Validation des arguments
    if args.interval < 1:
        print("❌ L'intervalle doit être d'au moins 1 seconde")
        return 1
    
    if args.interval > 60:
        print("⚠️ Intervalle très élevé (>60s), êtes-vous sûr ?")
    
    # Configuration des signaux pour arrêt propre
    def signal_handler(sig, frame):
        print("\n🛑 Arrêt demandé par l'utilisateur...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Lancement du monitoring
    async with NextvisionMonitor(args.url, args.interval) as monitor:
        await monitor.run()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring interrompu")
        exit(0)
    except Exception as e:
        print(f"\n❌ Erreur critique: {str(e)}")
        exit(1)
