#!/usr/bin/env python3
"""
Debug passo a passo da geração de sinais
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_step(step_name, func):
    print(f"🔧 {step_name}...")
    try:
        result = func()
        print(f"✅ {step_name} - OK")
        return result
    except Exception as e:
        print(f"❌ {step_name} - ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🔍 DEBUG PASSO A PASSO")
    print("=" * 50)
    
    # Passo 1: Importações
    def import_modules():
        print("   Tentando importar Config...")
        from src.config import Config
        print("   Config importado!")
        
        print("   Tentando importar MarketDataManager...")
        from src.market_data import MarketDataManager
        print("   MarketDataManager importado!")
        
        print("   Tentando importar TechnicalIndicators...")
        from src.technical_indicators import TechnicalIndicators
        print("   TechnicalIndicators importado!")
        
        return Config, MarketDataManager, TechnicalIndicators
    
    modules = test_step("Importações", import_modules)
    if not modules:
        print("❌ Falha nas importações - parando execução")
        return
    
    Config, MarketDataManager, TechnicalIndicators = modules
    
    # Passo 2: Configuração
    config = test_step("Criação Config", lambda: Config())
    if not config:
        return
    
    # Passo 3: Market Data
    market_data = test_step("Criação MarketData", lambda: MarketDataManager(config))
    if not market_data:
        return
    
    # Passo 4: Obter dados
    def get_data():
        df = market_data.get_historical_data('BTCUSDT', '1h', 100)
        print(f"   Dados: {len(df)} registros, preço: ${df['close'].iloc[-1]:.2f}")
        return df
    
    df = test_step("Obter dados BTC", get_data)
    if df is None or len(df) == 0:
        return
    
    # Passo 5: Análise técnica
    def analyze_technical():
        tech = TechnicalIndicators(config)
        df_with_indicators = tech.calculate_all_indicators(df)
        signal_strength = tech.get_signal_strength(df_with_indicators)
        print(f"   Indicadores calculados: {len(df_with_indicators.columns)} colunas")
        print(f"   Força dos sinais: {signal_strength}")
        return df_with_indicators, signal_strength
    
    analysis = test_step("Análise técnica", analyze_technical)
    if not analysis:
        return
    
    # Passo 6: AI Engine
    def test_ai():
        from src.ai_engine import AITradingEngine
        ai_engine = AITradingEngine(config)
        df_with_indicators, signal_strength = analysis
        prediction = ai_engine.predict_signal(df_with_indicators, 'BTCUSDT')
        print(f"   Predição: {prediction}")
        return ai_engine, prediction
    
    ai_result = test_step("AI Engine", test_ai)
    if not ai_result:
        return
    
    ai_engine, prediction = ai_result
    
    # Passo 7: Signal Generator
    def test_signal_gen():
        from src.signal_generator import SignalGenerator
        signal_gen = SignalGenerator(ai_engine, market_data)
          # Verificar se está em cooldown
        in_cooldown = signal_gen._is_in_cooldown('BTCUSDT')
        can_generate = not in_cooldown
        print(f"   Pode gerar sinal: {can_generate}")
        
        if can_generate:
            signal = signal_gen.generate_signal('BTCUSDT')
            if signal:
                print(f"   Sinal gerado: {signal.signal_type} com {signal.confidence:.1f}% confiança")
                print(f"   Entry: ${signal.entry_price:.2f}, SL: ${signal.stop_loss:.2f}, TP: ${signal.take_profit:.2f}")
            else:
                print("   Nenhum sinal gerado (baixa confiança)")
        else:
            print("   ⚠️  Não pode gerar sinal devido ao cooldown")
            
            # Verificar último sinal
            last_time = signal_gen._get_last_signal_time('BTCUSDT')
            print(f"   Último sinal: {last_time}")
              # Forçar geração removendo cooldown
            print("   🔧 Forçando geração (sem cooldown)...")
            signal_gen.last_signal_times = {}  # Limpar cache de cooldown
            signal = signal_gen.generate_signal('BTCUSDT')
            if signal:
                print(f"   Sinal forçado: {signal.signal_type} com {signal.confidence:.1f}% confiança")
                print(f"   Entry: ${signal.entry_price:.2f}, SL: ${signal.stop_loss:.2f}, TP: ${signal.take_profit:.2f}")
            else:
                print("   Nenhum sinal forçado gerado")
        
        return signal
      signal = test_step("Signal Generator", test_signal_gen)
    
    print(f"\n🎯 RESULTADO FINAL:")
    if signal:
        print(f"   ✅ SINAL GERADO: {signal.signal_type}")
        print(f"   💪 Confiança: {signal.confidence:.1f}%")
        print(f"   💰 Entry: ${signal.entry_price:.2f}")
        print(f"   🛡️  Stop Loss: ${signal.stop_loss:.2f}")
        print(f"   🎯 Take Profit: ${signal.take_profit:.2f}")
        if hasattr(signal, 'reasons') and signal.reasons:
            print(f"   📊 Razões: {', '.join(signal.reasons)}")
    else:
        print("   ❌ NENHUM SINAL GERADO")
    
    if signal is None:
        print("\n🔍 ANÁLISE DO PROBLEMA:")
        print(f"   Min confidence: {config.SIGNAL_CONFIG['min_confidence']}")
        print(f"   Confluence enabled: {config.SIGNAL_CONFIG.get('enable_confluence', True)}")
        
        # Mostrar detalhes da análise
        print("\n📊 Análise técnica completa:")
        df_with_indicators, signal_strength = analysis
        print(f"   Signal strength: {signal_strength}")
        print(f"   DataFrame shape: {df_with_indicators.shape}")
        print(f"   Latest close price: ${df_with_indicators['close'].iloc[-1]:.2f}")

if __name__ == "__main__":
    main()
