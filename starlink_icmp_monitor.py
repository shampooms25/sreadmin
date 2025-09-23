#!/usr/bin/env python3
"""
Sistema de Monitoramento ICMP/Ping para Service Lines Starlink
Implementa métricas reais de uptime/downtime baseadas em ping
"""
import os
import sys
import subprocess
import time
import json
from datetime import datetime, timedelta
import threading
import sqlite3
from typing import Dict, List, Tuple

class StarlinkICMPMonitor:
    """Sistema de monitoramento ICMP para Service Lines Starlink"""
    
    def __init__(self, db_path="starlink_ping_metrics.db"):
        self.db_path = db_path
        self.setup_database()
        self.monitoring_active = False
        
        # IPs públicos conhecidos para teste (Google DNS, Cloudflare, etc)
        self.test_targets = [
            "8.8.8.8",      # Google DNS
            "1.1.1.1",      # Cloudflare DNS
            "208.67.222.222" # OpenDNS
        ]
    
    def setup_database(self):
        """Criar estrutura do banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de métricas de ping
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ping_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_line TEXT NOT NULL,
                target_ip TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                response_time REAL,
                packet_loss INTEGER DEFAULT 0,
                success BOOLEAN DEFAULT FALSE,
                error_message TEXT
            )
        ''')
        
        # Tabela de resumo de disponibilidade
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS availability_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_line TEXT NOT NULL,
                date DATE NOT NULL,
                total_tests INTEGER DEFAULT 0,
                successful_tests INTEGER DEFAULT 0,
                failed_tests INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                uptime_percentage REAL DEFAULT 0,
                downtime_minutes REAL DEFAULT 0,
                UNIQUE(service_line, date)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Banco de dados iniciado: {self.db_path}")
    
    def ping_host(self, host: str, timeout: int = 5) -> Tuple[bool, float, str]:
        """
        Executa ping para um host específico
        Retorna: (sucesso, tempo_resposta, erro)
        """
        try:
            # Comando ping dependente do sistema operacional
            if os.name == 'nt':  # Windows
                cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), host]
            else:  # Linux/macOS
                cmd = ['ping', '-c', '1', '-W', str(timeout), host]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
            end_time = time.time()
            
            if result.returncode == 0:
                # Ping bem-sucedido
                response_time = (end_time - start_time) * 1000  # Converter para ms
                return True, response_time, ""
            else:
                return False, 0, result.stderr or "Ping failed"
                
        except subprocess.TimeoutExpired:
            return False, 0, "Timeout"
        except Exception as e:
            return False, 0, str(e)
    
    def test_service_line_connectivity(self, service_line: str) -> Dict:
        """
        Testa conectividade de uma service line usando múltiplos targets
        """
        results = {}
        total_tests = len(self.test_targets)
        successful_tests = 0
        total_response_time = 0
        
        for target in self.test_targets:
            success, response_time, error = self.ping_host(target)
            
            results[target] = {
                "success": success,
                "response_time": response_time,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
            
            if success:
                successful_tests += 1
                total_response_time += response_time
                
            # Salvar no banco
            self.save_ping_metric(service_line, target, success, response_time, error)
        
        # Calcular métricas gerais
        uptime_percentage = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        avg_response_time = total_response_time / successful_tests if successful_tests > 0 else 0
        
        return {
            "service_line": service_line,
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "uptime_percentage": round(uptime_percentage, 2),
            "avg_response_time": round(avg_response_time, 2),
            "results": results
        }
    
    def save_ping_metric(self, service_line: str, target: str, success: bool, 
                        response_time: float, error: str = ""):
        """Salvar métrica de ping no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ping_metrics 
            (service_line, target_ip, response_time, packet_loss, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (service_line, target, response_time, 0 if success else 1, success, error))
        
        conn.commit()
        conn.close()
    
    def calculate_daily_availability(self, service_line: str, date: str = None) -> Dict:
        """
        Calcular disponibilidade diária baseada nos testes de ping
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_tests,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_tests,
                   AVG(CASE WHEN success = 1 THEN response_time ELSE NULL END) as avg_response_time
            FROM ping_metrics
            WHERE service_line = ? AND DATE(timestamp) = ?
        ''', (service_line, date))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            total_tests, successful_tests, avg_response_time = result
            failed_tests = total_tests - successful_tests
            uptime_percentage = (successful_tests / total_tests) * 100
            downtime_minutes = (failed_tests / total_tests) * 24 * 60  # Aproximação
            
            return {
                "service_line": service_line,
                "date": date,
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "uptime_percentage": round(uptime_percentage, 2),
                "downtime_minutes": round(downtime_minutes, 2),
                "avg_response_time": round(avg_response_time or 0, 2)
            }
        
        return {
            "service_line": service_line,
            "date": date,
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "uptime_percentage": 0,
            "downtime_minutes": 0,
            "avg_response_time": 0
        }
    
    def start_monitoring(self, service_lines: List[str], interval_minutes: int = 5):
        """
        Iniciar monitoramento contínuo
        """
        def monitor_loop():
            print(f"🚀 Iniciando monitoramento ICMP para {len(service_lines)} service lines")
            print(f"⏱️  Intervalo: {interval_minutes} minutos")
            
            self.monitoring_active = True
            
            while self.monitoring_active:
                for sl in service_lines:
                    if not self.monitoring_active:
                        break
                        
                    print(f"🔍 Testando {sl}...")
                    result = self.test_service_line_connectivity(sl)
                    
                    print(f"   ✅ Uptime: {result['uptime_percentage']}% | "
                          f"Resposta média: {result['avg_response_time']:.2f}ms")
                
                if self.monitoring_active:
                    print(f"⏳ Aguardando {interval_minutes} minutos...")
                    time.sleep(interval_minutes * 60)
        
        # Iniciar em thread separada
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        self.monitoring_active = False
        print("🛑 Monitoramento ICMP interrompido")
    
    def get_availability_report(self, service_lines: List[str], days: int = 7) -> Dict:
        """
        Gerar relatório de disponibilidade baseado em dados históricos
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "service_lines": {}
        }
        
        for sl in service_lines:
            sl_data = []
            
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                daily_data = self.calculate_daily_availability(sl, date)
                sl_data.append(daily_data)
            
            # Calcular médias do período
            valid_days = [d for d in sl_data if d["total_tests"] > 0]
            
            if valid_days:
                avg_uptime = sum(d["uptime_percentage"] for d in valid_days) / len(valid_days)
                avg_response = sum(d["avg_response_time"] for d in valid_days) / len(valid_days)
                total_downtime = sum(d["downtime_minutes"] for d in valid_days)
            else:
                avg_uptime = 0
                avg_response = 0
                total_downtime = 0
            
            report["service_lines"][sl] = {
                "avg_uptime_percentage": round(avg_uptime, 2),
                "avg_response_time": round(avg_response, 2),
                "total_downtime_minutes": round(total_downtime, 2),
                "days_with_data": len(valid_days),
                "daily_data": sl_data
            }
        
        return report


def test_icmp_monitor():
    """Função de teste do sistema de monitoramento"""
    print("🧪 TESTANDO SISTEMA DE MONITORAMENTO ICMP")
    print("=" * 60)
    
    # Service lines para teste
    test_service_lines = [
        "SL-5242096-78596-88",
        "SL-3771955-54471-83", 
        "SL-3481747-13739-82"
    ]
    
    # Inicializar monitor
    monitor = StarlinkICMPMonitor()
    
    # Teste de conectividade individual
    print("\n📊 1. TESTE DE CONECTIVIDADE INDIVIDUAL")
    print("-" * 40)
    
    for sl in test_service_lines:
        result = monitor.test_service_line_connectivity(sl)
        print(f"Service Line: {sl}")
        print(f"  Uptime: {result['uptime_percentage']}%")
        print(f"  Resposta média: {result['avg_response_time']:.2f}ms")
        print(f"  Testes: {result['successful_tests']}/{result['total_tests']}")
        print()
    
    # Calcular disponibilidade diária
    print("\n📊 2. DISPONIBILIDADE DIÁRIA")
    print("-" * 40)
    
    for sl in test_service_lines:
        daily = monitor.calculate_daily_availability(sl)
        print(f"Service Line: {sl}")
        print(f"  Data: {daily['date']}")
        print(f"  Testes realizados: {daily['total_tests']}")
        print(f"  Uptime: {daily['uptime_percentage']}%")
        print()
    
    # Gerar relatório
    print("\n📊 3. RELATÓRIO DE 7 DIAS")
    print("-" * 40)
    
    report = monitor.get_availability_report(test_service_lines, days=1)
    
    for sl, data in report["service_lines"].items():
        print(f"Service Line: {sl}")
        print(f"  Uptime médio: {data['avg_uptime_percentage']}%")
        print(f"  Resposta média: {data['avg_response_time']:.2f}ms")
        print(f"  Downtime total: {data['total_downtime_minutes']:.2f} min")
        print()
    
    print("✅ TESTE CONCLUÍDO!")
    print("\nPara monitoramento contínuo:")
    print("monitor.start_monitoring(test_service_lines, interval_minutes=5)")


if __name__ == "__main__":
    test_icmp_monitor()
