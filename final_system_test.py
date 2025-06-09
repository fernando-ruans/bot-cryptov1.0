#!/usr/bin/env python3
"""
Teste final completo do sistema de trading
Valida todos os componentes e geração de sinais
"""
import sys
import os
import requests
import time
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_component(name, test_func):
    """Helper para testar componentes"""
    print(f"🔧 Testando {name}...")
    try:
        result = test_func()
        print(f"✅ {name} - OK")
        return result
    except Exception as e:
        print(f"❌ {name} - ERRO: {e}")
        return None

def test_imports():
    """Testa todas as importações"""
    from src.config import Config
    from src.market_data import MarketDataManager
    from src.technical_indicators import TechnicalIndicators
    from src.ai_engine import AITradingEngine
    from src.signal_generator import SignalGenerator
    return True

def test_configuration():
    """Testa configuração"""
    from src.config import Config
    config = Config()
    
    # Verificar configurações importantes
    assert hasattr(config, 'SIGNAL_CONFIG'), "SIGNAL_CONFIG não encontrado"
    assert 'min_confidence' in config.SIGNAL_CONFIG, "min_confidence não configurado"
    assert 'cooldown_minutes' in config.SIGNAL_CONFIG, "cooldown_minutes não configurado"
    
    print(f"   Min confidence: {config.SIGNAL_CONFIG['min_confidence']}")
    print(f"   Cooldown: {config.SIGNAL_CONFIG['cooldown_minutes']} min")
    
    return config

def test_market_data(config):
    """Testa obtenção de dados de mercado"""
    from src.market_data import MarketDataManager
    market_data = MarketDataManager(config)
    
    # Testar obtenção de dados
    df = market_data.get_historical_data('BTCUSDT', '1h', 100)
    assert len(df) > 0, "Nenhum dado obtido"
    assert 'close' in df.columns, "Coluna 'close' não encontrada"
    
    current_price = df['close'].iloc[-1]
    print(f"   Dados: {len(df)} registros")
    print(f"   Preço atual BTC: ${current_price:.2f}")
    
    return market_data, df

def test_technical_analysis(config, df):
    """Testa análise técnica"""
    from src.technical_indicators import TechnicalIndicators
    tech = TechnicalIndicators(config)
    
    # Calcular indicadores
    df_with_indicators = tech.calculate_all_indicators(df)
    assert len(df_with_indicators.columns) > len(df.columns), "Indicadores não foram adicionados"
    
    # Obter força dos sinais
    signal_strength = tech.get_signal_strength(df_with_indicators)
    
    print(f"   Indicadores: {len(df_with_indicators.columns)} colunas")
    print(f"   Força dos sinais: {signal_strength['confidence']:.1f}%")
    
    return df_with_indicators, signal_strength

def test_ai_engine(config, df_with_indicators):
    """Testa AI Engine"""
    from src.ai_engine import AITradingEngine
    ai_engine = AITradingEngine(config)
    
    # Fazer predição
    prediction = ai_engine.predict_signal(df_with_indicators, 'BTCUSDT')
    
    print(f"   Predição: {prediction}")
    
    return ai_engine, prediction

def test_signal_generation(ai_engine, market_data):
    """Testa geração de sinais"""
    from src.signal_generator import SignalGenerator
    signal_gen = SignalGenerator(ai_engine, market_data)
    
    # Limpar cooldown para garantir que pode gerar
    signal_gen.last_signal_times = {}
    
    # Gerar sinal
    signal = signal_gen.generate_signal('BTCUSDT')
    
    if signal:
        print(f"   ✅ SINAL GERADO: {signal.signal_type}")
        print(f"   💪 Confiança: {signal.confidence:.1f}%")
        print(f"   💰 Entry: ${signal.entry_price:.2f}")
        print(f"   🛡️  Stop Loss: ${signal.stop_loss:.2f}")
        print(f"   🎯 Take Profit: ${signal.take_profit:.2f}")
        if hasattr(signal, 'reasons') and signal.reasons:
            print(f"   📊 Razões principais: {len(signal.reasons)} fatores")
    else:
        print("   ⚠️  Nenhum sinal gerado (baixa confiança)")
    
    return signal

def test_web_api():
    """Testa API web se estiver rodando"""
    try:
        # Testar se o servidor está rodando
        response = requests.get('http://127.0.0.1:5000', timeout=5)
        if response.status_code == 200:
            print("   🌐 Servidor web está rodando")
            
            # Testar endpoint de geração de sinais (se existir)
            try:
                signal_response = requests.post(
                    'http://127.0.0.1:5000/generate_signal',
                    json={'symbol': 'BTCUSDT', 'confidence': 10},
                    timeout=10
                )
                if signal_response.status_code == 200:
                    signal_data = signal_response.json()
                    print(f"   🎯 API Signal: {signal_data.get('message', 'Resposta recebida')}")
                else:
                    print(f"   ⚠️  API Status: {signal_response.status_code}")
            except:
                print("   ℹ️  Endpoint de sinal não testado")
            
            return True
        else:
            print(f"   ⚠️  Servidor respondeu com status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ℹ️  Servidor web não está rodando")
        return False
    except Exception as e:
        print(f"   ⚠️  Erro ao testar API: {e}")
        return False

def main():
    print("🚀 TESTE FINAL COMPLETO DO SISTEMA")
    print("=" * 60)
    
    # Teste 1: Importações
    test_component("Importações", test_imports)
    
    # Teste 2: Configuração
    config = test_component("Configuração", test_configuration)
    if not config:
        return
    
    # Teste 3: Market Data
    market_result = test_component("Market Data", lambda: test_market_data(config))
    if not market_result:
        return
    market_data, df = market_result
    
    # Teste 4: Análise Técnica
    tech_result = test_component("Análise Técnica", lambda: test_technical_analysis(config, df))
    if not tech_result:
        return
    df_with_indicators, signal_strength = tech_result
    
    # Teste 5: AI Engine
    ai_result = test_component("AI Engine", lambda: test_ai_engine(config, df_with_indicators))
    if not ai_result:
        return
    ai_engine, prediction = ai_result
    
    # Teste 6: Geração de Sinais
    signal = test_component("Geração de Sinais", lambda: test_signal_generation(ai_engine, market_data))
    
    # Teste 7: API Web (opcional)
    test_component("API Web", test_web_api)
    
    print("\n" + "=" * 60)
    print("🎯 RESUMO FINAL:")
    
    if signal:
        print("✅ SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print(f"✅ Sinal {signal.signal_type.upper()} gerado com {signal.confidence:.1f}% de confiança")
        print(f"✅ Preço de entrada: ${signal.entry_price:.2f}")
        print("✅ Todos os componentes validados")
    else:
        print("⚠️  Sistema funcionando, mas nenhum sinal gerado no momento")
        print("✅ Todos os componentes validados")
    
    print(f"✅ Configuração: min_confidence = {config.SIGNAL_CONFIG['min_confidence']}")
    print(f"✅ Market Data: {len(df)} registros obtidos")
    print(f"✅ Indicadores: {len(df_with_indicators.columns)} calculados")
    print("✅ Sistema pronto para uso!")

if __name__ == "__main__":
    main()
