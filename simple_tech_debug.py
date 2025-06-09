#!/usr/bin/env python3
"""
Debug simples da análise técnica
"""

try:
    from src.ai_engine import AITradingEngine
    from src.market_data import MarketDataManager
    from src.signal_generator import SignalGenerator
    from src.config import Config
    
    print("Inicializando...")
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    print("Obtendo dados...")
    df = market_data.get_historical_data('BTCUSDT', '1h', 100)
    print(f"Dados obtidos: {len(df) if df is not None else 0}")
    
    if df is not None and not df.empty:
        print("Calculando indicadores...")
        df = signal_generator.technical_indicators.calculate_all_indicators(df)
        
        print("Executando análise técnica...")
        result = signal_generator._analyze_technical_indicators(df)
        
        print(f"Resultado: {result}")
    else:
        print("Dados não disponíveis")
        
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
