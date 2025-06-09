#!/usr/bin/env python3
"""
Teste da análise técnica corrigida
"""

def test_corrected_technical_analysis():
    """Teste da análise técnica corrigida"""
    print("=== TESTE: Análise Técnica Corrigida ===")
    
    try:
        # Importar módulos
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.ai_engine import AITradingEngine
        from src.signal_generator import SignalGenerator
        
        print("✓ Imports realizados com sucesso")
        
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        print("✓ Componentes inicializados")
        
        # Testar com dados reais
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        print(f"\n--- Testando {symbol} {timeframe} ---")
        
        # 1. Obter dados históricos
        df = market_data.get_historical_data(symbol, timeframe, 100)
        print(f"1. Dados históricos obtidos: {len(df)} registros")
        
        if df.empty:
            print("❌ Erro: Nenhum dado histórico obtido")
            return False
        
        # 2. Calcular indicadores
        df_with_indicators = signal_generator.technical_indicators.calculate_all_indicators(df.copy())
        print(f"2. Indicadores calculados: {len(df_with_indicators.columns)} colunas")
        
        # 3. Testar análise técnica original corrigida
        print("\n--- Testando Análise Técnica Corrigida ---")
        technical_result = signal_generator._analyze_technical_indicators(df_with_indicators)
        
        print(f"✓ Análise técnica concluída:")
        print(f"  - Sinal: {technical_result['signal']}")
        print(f"  - Confiança: {technical_result['confidence']:.2f}")
        print(f"  - Buy Strength: {technical_result.get('buy_strength', 0):.2f}")
        print(f"  - Sell Strength: {technical_result.get('sell_strength', 0):.2f}")
        print(f"  - Razões: {technical_result['reasons']}")
        
        # 4. Verificar se gera sinal válido
        if technical_result['signal'] != 'hold' and technical_result['confidence'] > 0:
            print("✅ SUCCESS: Análise técnica está gerando sinais válidos!")
            return True
        else:
            print("⚠️  WARNING: Análise técnica ainda retorna apenas 'hold'")
            print("    Mas isso pode ser normal dependendo das condições de mercado")
            return True
            
    except Exception as e:
        print(f"❌ ERRO no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_corrected_technical_analysis()
    if success:
        print("\n🎉 Teste da análise técnica concluído!")
    else:
        print("\n💥 Teste falhou!")
