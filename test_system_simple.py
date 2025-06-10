#!/usr/bin/env python3
"""
Teste Simples do Sistema Principal
Sem caracteres especiais para compatibilidade com Windows
"""

import sys
import os
import time
import subprocess
import tempfile
from datetime import datetime

def test_core_imports():
    """Testar importacoes principais do sistema"""
    print("\nTESTE 1: IMPORTACOES PRINCIPAIS")
    print("="*50)
    
    test_script = '''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config import Config
    print("OK: Config importado")
    
    from src.database import DatabaseManager
    print("OK: DatabaseManager importado")
    
    from src.market_data import MarketDataManager
    print("OK: MarketDataManager importado")
    
    from src.ai_engine import AITradingEngine
    print("OK: AITradingEngine importado")
    
    from src.signal_generator import SignalGenerator
    print("OK: SignalGenerator importado")
    
    from src.paper_trading import PaperTradingManager
    print("OK: PaperTradingManager importado")
    
    from src.realtime_updates import RealTimeUpdates
    print("OK: RealTimeUpdates importado")
    
    print("SUCCESS: Todas as importacoes funcionaram!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())
'''
    
    return run_test_script(test_script, "SUCCESS: Todas as importacoes funcionaram!")

def test_system_initialization():
    """Testar inicializacao basica do sistema"""
    print("\nTESTE 2: INICIALIZACAO DO SISTEMA")
    print("="*50)
    
    test_script = '''
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Iniciando componentes...")
    
    from src.config import Config
    from src.database import DatabaseManager
    from src.market_data import MarketDataManager
    from src.ai_engine import AITradingEngine
    
    # Inicializar componentes
    config = Config()
    print("OK: Config inicializado")
    
    db_manager = DatabaseManager()
    print("OK: DatabaseManager inicializado")
    
    market_data = MarketDataManager(config)
    print("OK: MarketDataManager inicializado")
    
    ai_engine = AITradingEngine(config)
    print("OK: AITradingEngine inicializado")
    
    # Inicializar database
    db_manager.initialize()
    print("OK: Database inicializado")
    
    print("SUCCESS: Sistema inicializado com sucesso!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())
'''
    
    return run_test_script(test_script, "SUCCESS: Sistema inicializado com sucesso!")

def test_signal_generation():
    """Testar geracao de sinais"""
    print("\nTESTE 3: GERACAO DE SINAIS")
    print("="*50)
    
    test_script = '''
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config import Config
    from src.database import DatabaseManager
    from src.market_data import MarketDataManager
    from src.ai_engine import AITradingEngine
    from src.signal_generator import SignalGenerator
    
    print("Inicializando componentes para sinais...")
    
    config = Config()
    db_manager = DatabaseManager()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    print("OK: Componentes inicializados")
    
    # Inicializar sistemas
    db_manager.initialize()
    market_data.start_data_feed()
    ai_engine.load_models()
    
    print("OK: Sistemas iniciados")
    
    # Aguardar carregamento
    time.sleep(3)
    
    # Testar geracao de sinal
    print("Gerando sinal para BTCUSDT...")
    signal = signal_generator.generate_signal('BTCUSDT', '1h')
    
    if signal:
        print(f"OK: Sinal gerado - {signal.signal_type} @ ${signal.entry_price:.4f}")
        print(f"    Confianca: {signal.confidence:.3f}")
    else:
        print("INFO: Nenhum sinal gerado (normal)")
    
    # Parar sistemas
    market_data.stop_data_feed()
    
    print("SUCCESS: Teste de sinais concluido!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())
'''
    
    return run_test_script(test_script, "SUCCESS: Teste de sinais concluido!", timeout=40)

def test_realtime_system():
    """Testar sistema de tempo real"""
    print("\nTESTE 4: SISTEMA TEMPO REAL")
    print("="*50)
    
    test_script = '''
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.realtime_price_api import realtime_price_api
    
    print("Testando sistema de precos em tempo real...")
    
    # Contador de atualizacoes
    price_count = 0
    
    def test_callback(symbol, price):
        global price_count
        price_count += 1
        if price_count <= 3:
            print(f"Preco recebido: {symbol} = ${price:.4f}")
    
    # Adicionar callback
    realtime_price_api.add_callback(test_callback)
    
    # Iniciar sistema
    realtime_price_api.start()
    print("OK: Sistema de precos iniciado")
    
    # Aguardar atualizacoes
    print("Aguardando precos por 8 segundos...")
    time.sleep(8)
    
    # Parar sistema
    realtime_price_api.stop()
    
    print(f"OK: Recebidas {price_count} atualizacoes de preco")
    
    if price_count > 0:
        print("SUCCESS: Sistema tempo real funcionando!")
    else:
        print("WARNING: Nenhuma atualizacao recebida")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())
'''
    
    return run_test_script(test_script, "SUCCESS: Sistema tempo real funcionando!", timeout=15)

def run_test_script(script_content, success_marker, timeout=30):
    """Executar script de teste e verificar resultado"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            result = subprocess.run([
                sys.executable, script_path
            ], cwd=os.path.dirname(__file__), capture_output=True, text=True, timeout=timeout, encoding='utf-8')
            
            print("Saida do teste:")
            print(result.stdout)
            
            if result.stderr:
                print("Erros:")
                print(result.stderr)
            
            # Verificar sucesso
            success = success_marker in result.stdout
            return success
            
        finally:
            try:
                os.unlink(script_path)
            except:
                pass
                
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: Teste excedeu {timeout} segundos")
        return False
    except Exception as e:
        print(f"ERROR: Erro ao executar teste - {e}")
        return False

def test_paper_trading():
    """Testar sistema de paper trading"""
    print("\nTESTE 5: PAPER TRADING")
    print("="*50)
    
    test_script = '''
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config import Config
    from src.database import DatabaseManager
    from src.market_data import MarketDataManager
    from src.ai_engine import AITradingEngine
    from src.signal_generator import SignalGenerator
    from src.paper_trading import PaperTradingManager
    
    print("Inicializando paper trading...")
    
    config = Config()
    db_manager = DatabaseManager()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    paper_trading = PaperTradingManager(market_data, None)
    
    print("OK: Componentes inicializados")
    
    # Inicializar
    db_manager.initialize()
    market_data.start_data_feed()
    ai_engine.load_models()
    
    time.sleep(2)
    
    # Verificar balance inicial
    balance = paper_trading.get_balance()
    print(f"OK: Balance inicial: ${balance:.2f}")
    
    # Verificar trades ativos
    active_trades = paper_trading.get_active_trades()
    print(f"OK: Trades ativos: {len(active_trades)}")
    
    market_data.stop_data_feed()
    
    print("SUCCESS: Paper trading testado com sucesso!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())
'''
    
    return run_test_script(test_script, "SUCCESS: Paper trading testado com sucesso!")

def main():
    """Executar suite completa de testes"""
    print("SISTEMA DE TRADING - TESTE COMPLETO")
    print("="*80)
    
    start_time = datetime.now()
    
    # Executar testes
    test_results = {
        'imports': test_core_imports(),
        'initialization': test_system_initialization(), 
        'signals': test_signal_generation(),
        'realtime': test_realtime_system(),
        'paper_trading': test_paper_trading()
    }
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "PASSOU" if result else "FALHOU"
        print(f"{test_name.replace('_', ' ').title():<20} {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    duration = datetime.now() - start_time
    
    print(f"\nTaxa de sucesso: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"Duracao total: {duration.total_seconds():.1f} segundos")
    
    if success_rate >= 80:
        print("\nSISTEMA FUNCIONANDO CORRETAMENTE!")
        print("O bot de trading esta pronto para uso.")
    elif success_rate >= 60:
        print("\nSISTEMA PARCIALMENTE FUNCIONAL")
        print("Alguns componentes podem precisar de ajustes.")
    else:
        print("\nSISTEMA COM PROBLEMAS")
        print("Verificar componentes que falharam.")
    
    return test_results

if __name__ == '__main__':
    main()
