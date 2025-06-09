from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator

print("=== TESTE COMPLETO DE GERAÇÃO DE SINAIS ===")

try:
    # Inicializar componentes
    print("1. Inicializando componentes...")
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_gen = SignalGenerator(ai_engine, market_data)
    print("✅ Componentes inicializados")
      # Verificar configurações
    print(f"2. Min confidence: {config.SIGNAL_CONFIG['min_confidence']}")
    print(f"   Cooldown: {config.SIGNAL_CONFIG.get('signal_cooldown_minutes', 15)} min")
    print(f"   Enable confluence: {config.SIGNAL_CONFIG.get('enable_confluence', True)}")
    
    # Obter dados
    print("3. Obtendo dados do BTC...")
    df = market_data.get_historical_data('BTCUSDT', '1h', 500)
    print(f"✅ Dados obtidos: {len(df)} registros, preço: ${df['close'].iloc[-1]:.2f}")    # Verificar cooldown
    print("4. Verificando cooldown...")
    can_generate = not signal_gen._is_in_cooldown('BTCUSDT')
    print(f"✅ Pode gerar sinal: {can_generate}")
    
    if not can_generate:
        print("ℹ️  Removendo cooldown para teste...")
        signal_gen.last_signal_time = {}
    
    # Tentar gerar sinal
    print("5. Tentando gerar sinal...")
    signal = signal_gen.generate_signal('BTCUSDT')
    
    if signal:
        print(f"✅ SINAL GERADO!")
        print(f"   Tipo: {signal.signal_type}")
        print(f"   Confiança: {signal.confidence:.2%}")
        print(f"   Preço de entrada: ${signal.entry_price:.2f}")
        print(f"   Stop Loss: ${signal.stop_loss:.2f}")
        print(f"   Take Profit: ${signal.take_profit:.2f}")
        print(f"   Razões: {signal.reasons}")
    else:
        print("❌ NENHUM SINAL GERADO")
        
        # Debug detalhado
        print("\n🔍 DEBUG DETALHADO:")
        
        # Calcular indicadores
        df_with_indicators = signal_gen.technical_indicators.calculate_all_indicators(df.copy())
        print(f"   Indicadores calculados: {len(df_with_indicators.columns)} colunas")
        
        # Análise técnica
        technical_analysis = signal_gen._analyze_technical_indicators(df_with_indicators)
        print(f"   Análise técnica: {technical_analysis}")
        
        # Predição AI
        ai_prediction = ai_engine.predict_signal(df_with_indicators, 'BTCUSDT')
        print(f"   Predição AI: {ai_prediction}")
        
        # Análise de volume
        volume_analysis = signal_gen._analyze_volume(df_with_indicators)
        print(f"   Análise volume: {volume_analysis}")
        
        # Análise de volatilidade
        volatility_analysis = signal_gen._analyze_volatility(df_with_indicators)
        print(f"   Análise volatilidade: {volatility_analysis}")
        
        # Contexto de mercado
        market_context = signal_gen._analyze_market_context('BTCUSDT', '1h')
        print(f"   Contexto mercado: {market_context}")
        
        # Combinação
        combined = signal_gen._combine_analyses(
            technical_analysis, ai_prediction, volume_analysis,
            volatility_analysis, market_context
        )
        print(f"   Análise combinada: {combined}")
          # Verificar se atende confiança mínima
        min_conf = config.SIGNAL_CONFIG['min_confidence']
        print(f"   Confiança do sinal: {combined.get('confidence', 0):.4f}")
        print(f"   Confiança mínima: {min_conf:.4f}")
        print(f"   Atende limiar: {combined.get('confidence', 0) >= min_conf}")

except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIM DO TESTE ===")
