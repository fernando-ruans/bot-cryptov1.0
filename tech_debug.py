#!/usr/bin/env python3
"""
Debug detalhado da análise técnica e geração de sinais
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 DEBUG ANÁLISE TÉCNICA")
print("=" * 50)

try:
    from src.config import Config
    from src.market_data import MarketDataManager
    from src.technical_indicators import TechnicalIndicators
    from src.ai_engine import AITradingEngine
    from src.signal_generator import SignalGenerator
    
    # Configuração
    config = Config()
    market_data = MarketDataManager(config)
    
    # Dados do BTC
    print("📊 Obtendo dados do BTC...")
    df = market_data.get_historical_data('BTCUSDT', '1h', 100)
    print(f"✅ Dados obtidos: {len(df)} registros")
    print(f"Preço atual: ${df['close'].iloc[-1]:.2f}")    # Análise técnica
    print("\n🔧 Executando análise técnica...")
    tech_indicators = TechnicalIndicators(config)
    df_with_indicators = tech_indicators.calculate_all_indicators(df)
    signal_strength = tech_indicators.get_signal_strength(df_with_indicators)
    
    print(f"Indicadores calculados: {len(df_with_indicators.columns)} colunas")
    print(f"Força dos sinais: {signal_strength}")
    
    # Verificar alguns indicadores específicos
    latest = df_with_indicators.iloc[-1]
    print(f"RSI: {latest.get('rsi', 'N/A')}")
    print(f"MACD: {latest.get('macd', 'N/A')}")
    print(f"BB Position: {latest.get('bb_position', 'N/A')}")
    if 'volume_ratio' in latest:
        print(f"Volume Spike: {latest['volume_ratio'] > 1.5}")
    else:
        print(f"Volume Spike: N/A")
    
    # AI Engine
    print("\n🤖 Testando AI Engine...")
    ai_engine = AITradingEngine(config)
    prediction = ai_engine.predict(df, 'BTCUSDT')
    print(f"Predição AI: {prediction}")
    
    # Signal Generator
    print("\n🎯 Testando Signal Generator...")
    signal_gen = SignalGenerator(ai_engine, market_data)
      # Verificar cooldown
    print("Verificando cooldown...")
    is_in_cooldown = signal_gen._is_in_cooldown('BTCUSDT')
    print(f"Em cooldown: {is_in_cooldown}")
    
    can_generate = not is_in_cooldown
    print(f"Pode gerar sinal: {can_generate}")
    
    # Tentar gerar sinal
    print("\nTentando gerar sinal...")
    signal = signal_gen.generate_signal('BTCUSDT')
    print(f"Resultado: {signal}")
    
    if signal is None:
        print("\n❌ NENHUM SINAL GERADO - Investigando motivos...")
          # Verificar análise técnica detalhada
        print("\n🔍 Análise técnica detalhada:")
        print(f"  Força dos sinais: {signal_strength}")
          # Verificar thresholds
        print(f"\n⚙️ Configurações atuais:")
        signal_config = config.SIGNAL_CONFIG
        print(f"  Min confidence: {signal_config['min_confidence']}")
        print(f"  Enable confluence: {signal_config.get('enable_confluence', True)}")
        print(f"  Cooldown: {signal_config.get('signal_cooldown_minutes', 15)} min")
        
        print("\n🔧 Para forçar um sinal, use o script force_signal.py")
    
except Exception as e:
    print(f"❌ ERRO: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n✅ Debug concluído")
