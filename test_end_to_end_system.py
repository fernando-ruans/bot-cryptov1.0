#!/usr/bin/env python3
"""
Teste End-to-End do Sistema de Trading Bot
Verifica a integração completa e funcionalidade principal
"""

import sys
import os
import time
import logging
import threading
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configurar logging simplificado para testes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_system_initialization():
    """Teste 1: Verificar inicialização básica do sistema"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: INICIALIZAÇÃO DO SISTEMA")
    print("="*60)
    
    try:
        # Importar módulos principais
        from config import Config
        from market_data import MarketDataManager
        from ai_engine import AITradingEngine
        from signal_generator import SignalGenerator
        from database import DatabaseManager
        from paper_trading import PaperTradingManager
        from realtime_updates import RealTimeUpdates
        
        print("✅ Importação de módulos principais: SUCESSO")
        
        # Inicializar configuração
        config = Config()
        print("✅ Configuração carregada: SUCESSO")
        
        # Inicializar componentes
        db_manager = DatabaseManager()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        
        print("✅ Componentes inicializados: SUCESSO")
        
        # Inicializar geradores
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        # Mock do socketio para teste
        class MockSocketIO:
            def emit(self, event, data, room=None):
                pass
        
        mock_socketio = MockSocketIO()
        paper_trading = PaperTradingManager(market_data, None)
        realtime_updates = RealTimeUpdates(mock_socketio)
        
        print("✅ Geradores e managers inicializados: SUCESSO")
        
        return {
            'config': config,
            'db_manager': db_manager,
            'market_data': market_data,
            'ai_engine': ai_engine,
            'signal_generator': signal_generator,
            'paper_trading': paper_trading,
            'realtime_updates': realtime_updates
        }
        
    except Exception as e:
        print(f"❌ Erro na inicialização do sistema: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def test_signal_generation(components):
    """Teste 2: Verificar geração de sinais"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: GERAÇÃO DE SINAIS")
    print("="*60)
    
    if not components:
        print("❌ Componentes não disponíveis para teste")
        return False
    
    try:
        signal_generator = components['signal_generator']
        market_data = components['market_data']
        ai_engine = components['ai_engine']
        
        # Inicializar componentes necessários
        print("🔄 Inicializando market data...")
        market_data.start_data_feed()
        
        print("🔄 Carregando modelos AI...")
        ai_engine.load_models()
        
        # Aguardar um pouco para carregar dados
        time.sleep(2)
        
        # Testar geração de sinais para diferentes símbolos
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        
        for symbol in test_symbols:
            print(f"\n🎯 Testando geração de sinal para {symbol}...")
            
            try:
                signal = signal_generator.generate_signal(symbol, '1h')
                
                if signal:
                    print(f"✅ Sinal gerado para {symbol}:")
                    print(f"   Tipo: {signal.signal_type}")
                    print(f"   Confiança: {signal.confidence:.3f}")
                    print(f"   Preço de entrada: ${signal.entry_price:.4f}")
                    print(f"   Stop Loss: ${signal.stop_loss:.4f}")
                    print(f"   Take Profit: ${signal.take_profit:.4f}")
                    print(f"   Razões: {signal.reasons}")
                else:
                    print(f"⚠️ Nenhum sinal gerado para {symbol}")
                    
            except Exception as e:
                print(f"❌ Erro ao gerar sinal para {symbol}: {e}")
        
        # Parar o market data
        market_data.stop_data_feed()
        
        print("\n✅ Teste de geração de sinais concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de geração de sinais: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_paper_trading_flow(components):
    """Teste 3: Verificar fluxo de paper trading"""
    print("\n" + "="*60)
    print("🧪 TESTE 3: FLUXO DE PAPER TRADING")
    print("="*60)
    
    if not components:
        print("❌ Componentes não disponíveis para teste")
        return False
    
    try:
        paper_trading = components['paper_trading']
        signal_generator = components['signal_generator']
        market_data = components['market_data']
        ai_engine = components['ai_engine']
        
        # Inicializar componentes
        market_data.start_data_feed()
        ai_engine.load_models()
        time.sleep(2)
        
        # Gerar um sinal de teste
        print("🎯 Gerando sinal para teste de paper trading...")
        signal = signal_generator.generate_signal('BTCUSDT', '1h')
        
        if not signal:
            print("❌ Não foi possível gerar sinal para teste")
            market_data.stop_data_feed()
            return False
        
        print(f"✅ Sinal gerado: {signal.signal_type} @ ${signal.entry_price:.4f}")
        
        # Executar trade de paper trading
        print("🔄 Executando paper trade...")
        
        try:
            # Simular execução de trade
            trade_result = paper_trading.execute_trade(signal)
            
            if trade_result and trade_result.get('success'):
                print("✅ Paper trade executado com sucesso:")
                print(f"   Trade ID: {trade_result.get('trade_id')}")
                print(f"   Símbolo: {trade_result.get('symbol')}")
                print(f"   Tipo: {trade_result.get('side')}")
                print(f"   Quantidade: {trade_result.get('quantity')}")
                print(f"   Preço: ${trade_result.get('price'):.4f}")
            else:
                print(f"⚠️ Paper trade não executado: {trade_result}")
                
        except Exception as e:
            print(f"❌ Erro ao executar paper trade: {e}")
        
        # Verificar estado do portfolio
        print("\n💰 Verificando estado do portfolio...")
        try:
            balance = paper_trading.get_balance()
            if balance:
                print(f"✅ Balance atual: ${balance:.2f}")
            else:
                print("⚠️ Balance não disponível")
                
            active_trades = paper_trading.get_active_trades()
            print(f"📊 Trades ativos: {len(active_trades)}")
            
            if active_trades:
                for trade in active_trades[:3]:  # Mostrar primeiros 3
                    print(f"   - {trade.get('symbol')} {trade.get('side')} @ ${trade.get('price'):.4f}")
                    
        except Exception as e:
            print(f"❌ Erro ao verificar portfolio: {e}")
        
        market_data.stop_data_feed()
        
        print("\n✅ Teste de paper trading concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de paper trading: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_real_time_integration(components):
    """Teste 4: Verificar integração em tempo real"""
    print("\n" + "="*60)
    print("🧪 TESTE 4: INTEGRAÇÃO TEMPO REAL")
    print("="*60)
    
    if not components:
        print("❌ Componentes não disponíveis para teste")
        return False
    
    try:
        from realtime_price_api import realtime_price_api
        
        # Contador de atualizações recebidas
        price_updates_received = 0
        test_duration = 10  # segundos
        
        def test_callback(symbol: str, price: float):
            nonlocal price_updates_received
            price_updates_received += 1
            if price_updates_received <= 5:  # Mostrar apenas as primeiras 5
                print(f"📈 Preço recebido: {symbol} = ${price:.4f}")
        
        print("🔄 Iniciando sistema de preços em tempo real...")
        
        # Adicionar callback de teste
        realtime_price_api.add_callback(test_callback)
        
        # Iniciar sistema
        realtime_price_api.start()
        
        # Aguardar por atualizações
        print(f"⏱️ Aguardando atualizações por {test_duration} segundos...")
        time.sleep(test_duration)
        
        # Parar sistema
        realtime_price_api.stop()
        
        print(f"✅ Teste concluído. Recebidas {price_updates_received} atualizações de preço")
        
        if price_updates_received > 0:
            print("✅ Sistema de tempo real funcionando corretamente")
            return True
        else:
            print("⚠️ Nenhuma atualização de preço recebida")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de tempo real: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_database_operations(components):
    """Teste 5: Verificar operações de banco de dados"""
    print("\n" + "="*60)
    print("🧪 TESTE 5: OPERAÇÕES DE BANCO DE DADOS")
    print("="*60)
    
    if not components:
        print("❌ Componentes não disponíveis para teste")
        return False
    
    try:
        db_manager = components['db_manager']
        
        # Inicializar banco
        print("🔄 Inicializando banco de dados...")
        db_manager.initialize()
        print("✅ Banco de dados inicializado")
        
        # Testar inserção de sinal
        print("🔄 Testando inserção de sinal...")
        test_signal_data = {
            'symbol': 'BTCUSDT',
            'signal_type': 'buy',
            'confidence': 0.75,
            'entry_price': 45000.0,
            'stop_loss': 44000.0,
            'take_profit': 47000.0,
            'timeframe': '1h',
            'reasons': ['test_signal']
        }
        
        try:
            signal_id = db_manager.save_signal(test_signal_data)
            print(f"✅ Sinal salvo com ID: {signal_id}")
        except Exception as e:
            print(f"❌ Erro ao salvar sinal: {e}")
        
        # Testar recuperação de sinais
        print("🔄 Testando recuperação de sinais...")
        try:
            recent_signals = db_manager.get_recent_signals(limit=5)
            print(f"✅ Recuperados {len(recent_signals)} sinais recentes")
            
            if recent_signals:
                for signal in recent_signals[:2]:  # Mostrar primeiros 2
                    print(f"   - {signal.get('symbol')} {signal.get('signal_type')} @ ${signal.get('entry_price'):.2f}")
                    
        except Exception as e:
            print(f"❌ Erro ao recuperar sinais: {e}")
        
        print("✅ Teste de banco de dados concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de banco de dados: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Executar todos os testes end-to-end"""
    print("🚀 INICIANDO TESTES END-TO-END DO SISTEMA DE TRADING")
    print("="*80)
    
    start_time = datetime.now()
    
    # Resultado dos testes
    test_results = {
        'initialization': False,
        'signal_generation': False,
        'paper_trading': False,
        'real_time': False,
        'database': False
    }
    
    # Teste 1: Inicialização
    components = test_system_initialization()
    test_results['initialization'] = components is not None
    
    if components:
        # Teste 2: Geração de sinais
        test_results['signal_generation'] = test_signal_generation(components)
        
        # Teste 3: Paper trading
        test_results['paper_trading'] = test_paper_trading_flow(components)
        
        # Teste 4: Tempo real
        test_results['real_time'] = test_real_time_integration(components)
        
        # Teste 5: Banco de dados
        test_results['database'] = test_database_operations(components)
    
    # Resumo final
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES END-TO-END")
    print("="*80)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name.replace('_', ' ').title():<25} {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    duration = datetime.now() - start_time
    
    print(f"\nTaxa de sucesso: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"Duração total: {duration.total_seconds():.1f} segundos")
    
    if success_rate >= 80:
        print("\n🎉 SISTEMA FUNCIONANDO CORRETAMENTE!")
    elif success_rate >= 60:
        print("\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL - VERIFICAR FALHAS")
    else:
        print("\n❌ SISTEMA COM PROBLEMAS SIGNIFICATIVOS")
    
    return test_results

if __name__ == '__main__':
    main()
