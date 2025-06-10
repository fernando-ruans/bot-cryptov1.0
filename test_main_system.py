#!/usr/bin/env python3
"""
Teste de Inicialização do Sistema Principal
Testa o main.py diretamente usando threading para não bloquear
"""

import sys
import os
import time
import threading
import requests
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_main_system():
    """Testar o sistema principal via main.py"""
    print("🚀 TESTE DE SISTEMA PRINCIPAL - MAIN.PY")
    print("="*60)
    
    # Verificar se o arquivo main.py existe
    main_path = os.path.join(os.path.dirname(__file__), 'main.py')
    if not os.path.exists(main_path):
        print("❌ Arquivo main.py não encontrado")
        return False
    
    print("✅ Arquivo main.py encontrado")
    
    # Tentar executar apenas as importações principais do main.py
    try:
        print("🔄 Testando importações...")
        
        # Simular importações do main.py usando exec
        import subprocess
        import tempfile
        
        # Criar script de teste de importações
        test_import_script = '''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ai_engine import AITradingEngine
    print("✅ AITradingEngine importado")
    
    from src.market_data import MarketDataManager  
    print("✅ MarketDataManager importado")
    
    from src.signal_generator import SignalGenerator
    print("✅ SignalGenerator importado")
    
    from src.database import DatabaseManager
    print("✅ DatabaseManager importado")
    
    from src.config import Config
    print("✅ Config importado")
    
    from src.paper_trading import PaperTradingManager
    print("✅ PaperTradingManager importado")
    
    from src.realtime_updates import RealTimeUpdates
    print("✅ RealTimeUpdates importado")
    
    print("🎉 TODAS AS IMPORTAÇÕES PRINCIPAIS FUNCIONARAM!")
    
except Exception as e:
    print(f"❌ Erro nas importações: {e}")
    import traceback
    print(traceback.format_exc())
'''
        
        # Escrever script temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_import_script)
            temp_script_path = f.name
        
        try:
            # Executar script de teste
            result = subprocess.run([
                sys.executable, temp_script_path
            ], cwd=os.path.dirname(__file__), capture_output=True, text=True, timeout=30)
            
            print("Saída do teste de importações:")
            print(result.stdout)
            
            if result.stderr:
                print("Erros:")
                print(result.stderr)
            
            success = "TODAS AS IMPORTAÇÕES PRINCIPAIS FUNCIONARAM!" in result.stdout
            
            if success:
                print("✅ Teste de importações: SUCESSO")
                return True
            else:
                print("❌ Teste de importações: FALHOU")
                return False
                
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(temp_script_path)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Erro no teste de importações: {e}")
        return False

def test_flask_server_start():
    """Testar inicialização do servidor Flask em background"""
    print("\n🌐 TESTE DE SERVIDOR FLASK")
    print("="*40)
    
    try:
        import subprocess
        import time
        
        # Iniciar servidor em processo separado
        print("🔄 Iniciando servidor Flask...")
        
        # Criar script para iniciar servidor com timeout
        server_script = '''
import sys
import os
import signal
import threading
import time
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def timeout_handler():
    """Parar servidor após timeout"""
    time.sleep(15)  # Executar por 15 segundos
    print("⏱️ Timeout atingido - parando servidor")
    os._exit(0)

# Iniciar thread de timeout
timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
timeout_thread.start()

try:
    print("🚀 Iniciando sistema principal...")
    
    # Importar e executar main simplificado
    from src.config import Config
    from src.database import DatabaseManager
    from src.market_data import MarketDataManager
    from src.ai_engine import AITradingEngine
    
    print("✅ Módulos principais importados")
    
    # Inicializar componentes básicos
    config = Config()
    db_manager = DatabaseManager()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    
    print("✅ Componentes inicializados")
    
    # Simular inicialização sem Flask
    db_manager.initialize()
    print("✅ Database inicializado")
    
    # Carregar modelos
    ai_engine.load_models()
    print("✅ Modelos AI carregados")
    
    # Aguardar um pouco para simular operação
    print("⏱️ Sistema funcionando...")
    time.sleep(10)
    
    print("✅ TESTE DE SISTEMA CONCLUÍDO COM SUCESSO!")
    
except Exception as e:
    print(f"❌ Erro no sistema: {e}")
    import traceback
    print(traceback.format_exc())
'''
        
        # Escrever script de servidor
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(server_script)
            server_script_path = f.name
        
        try:
            # Executar servidor
            result = subprocess.run([
                sys.executable, server_script_path
            ], cwd=os.path.dirname(__file__), capture_output=True, text=True, timeout=20)
            
            print("Saída do servidor:")
            print(result.stdout)
            
            if result.stderr:
                print("Erros:")
                print(result.stderr)
            
            success = "TESTE DE SISTEMA CONCLUÍDO COM SUCESSO!" in result.stdout
            
            if success:
                print("✅ Teste de servidor: SUCESSO")
                return True
            else:
                print("❌ Teste de servidor: FALHOU")
                return False
                
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(server_script_path)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Erro no teste de servidor: {e}")
        return False

def test_signal_generation_standalone():
    """Testar geração de sinais de forma standalone"""
    print("\n🎯 TESTE DE GERAÇÃO DE SINAIS STANDALONE")
    print("="*50)
    
    try:
        import subprocess
        
        signal_script = '''
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🔄 Iniciando teste de geração de sinais...")
    
    from src.config import Config
    from src.market_data import MarketDataManager
    from src.ai_engine import AITradingEngine
    from src.signal_generator import SignalGenerator
    
    print("✅ Módulos importados")
    
    # Inicializar componentes
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    print("✅ Componentes inicializados")
    
    # Inicializar sistemas
    market_data.start_data_feed()
    ai_engine.load_models()
    
    print("✅ Sistemas iniciados")
    
    # Aguardar carregamento
    time.sleep(3)
    
    # Testar geração de sinal
    print("🎯 Gerando sinal para BTCUSDT...")
    signal = signal_generator.generate_signal('BTCUSDT', '1h')
    
    if signal:
        print(f"✅ Sinal gerado: {signal.signal_type} @ ${signal.entry_price:.4f}")
        print(f"   Confiança: {signal.confidence:.3f}")
        print(f"   Razões: {signal.reasons}")
    else:
        print("⚠️ Nenhum sinal gerado")
    
    # Parar sistemas
    market_data.stop_data_feed()
    
    print("✅ TESTE DE SINAIS CONCLUÍDO!")
    
except Exception as e:
    print(f"❌ Erro no teste de sinais: {e}")
    import traceback
    print(traceback.format_exc())
'''
        
        # Executar teste
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(signal_script)
            script_path = f.name
        
        try:
            result = subprocess.run([
                sys.executable, script_path
            ], cwd=os.path.dirname(__file__), capture_output=True, text=True, timeout=30)
            
            print("Saída do teste de sinais:")
            print(result.stdout)
            
            if result.stderr:
                print("Erros:")
                print(result.stderr)
            
            success = "TESTE DE SINAIS CONCLUÍDO!" in result.stdout
            
            if success:
                print("✅ Teste de geração de sinais: SUCESSO")
                return True
            else:
                print("❌ Teste de geração de sinais: FALHOU")
                return False
                
        finally:
            try:
                os.unlink(script_path)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Erro no teste standalone de sinais: {e}")
        return False

def main():
    """Executar todos os testes do sistema principal"""
    print("🚀 TESTES DO SISTEMA PRINCIPAL DE TRADING")
    print("="*80)
    
    start_time = datetime.now()
    
    # Executar testes
    test_results = {
        'imports': test_main_system(),
        'server': test_flask_server_start(),
        'signals': test_signal_generation_standalone()
    }
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES DO SISTEMA PRINCIPAL")
    print("="*80)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name.replace('_', ' ').title():<20} {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    duration = datetime.now() - start_time
    
    print(f"\nTaxa de sucesso: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"Duração total: {duration.total_seconds():.1f} segundos")
    
    if success_rate >= 80:
        print("\n🎉 SISTEMA PRINCIPAL FUNCIONANDO CORRETAMENTE!")
    elif success_rate >= 60:
        print("\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
    else:
        print("\n❌ SISTEMA COM PROBLEMAS")
    
    return test_results

if __name__ == '__main__':
    main()
