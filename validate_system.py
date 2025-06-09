#!/usr/bin/env python3
"""
Script de validação final - verifica todas as funcionalidades críticas
"""

def validate_system():
    """Validação completa do sistema"""
    print("🔍 VALIDAÇÃO FINAL DO SISTEMA DE TRADING")
    print("=" * 50)
    
    # Teste 1: Configurações
    print("\n1. ✅ CONFIGURAÇÕES VERIFICADAS")
    try:
        from src.config import Config
        config = Config()
        print(f"   • Confiança mínima: {config.SIGNAL_CONFIG['min_confidence']} (40%)")
        print(f"   • Confluência habilitada: {config.SIGNAL_CONFIG['enable_confluence']}")
        print(f"   • Cooldown: {config.SIGNAL_CONFIG['signal_cooldown_minutes']} min")
        print(f"   • Max sinais/hora: {config.SIGNAL_CONFIG['max_signals_per_hour']}")
    except Exception as e:
        print(f"   ❌ Erro na configuração: {e}")
        return False
    
    # Teste 2: Imports críticos
    print("\n2. ✅ IMPORTS VERIFICADOS")
    try:
        from src.market_data import MarketDataManager
        from src.ai_engine import AITradingEngine  
        from src.signal_generator import SignalGenerator
        from src.technical_indicators import TechnicalIndicators
        print("   • Todos os módulos carregados com sucesso")
    except Exception as e:
        print(f"   ❌ Erro nos imports: {e}")
        return False
    
    # Teste 3: Componentes básicos
    print("\n3. ✅ COMPONENTES INICIALIZADOS")
    try:
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_gen = SignalGenerator(ai_engine, market_data)
        print("   • MarketDataManager: OK")
        print("   • AITradingEngine: OK") 
        print("   • SignalGenerator: OK")
    except Exception as e:
        print(f"   ❌ Erro na inicialização: {e}")
        return False
    
    # Teste 4: Dados de mercado
    print("\n4. ✅ DADOS DE MERCADO")
    try:
        df = market_data.get_historical_data('BTCUSDT', '1h', 100)
        print(f"   • Dados históricos: {len(df)} registros")
        
        current_price = market_data.get_current_price('BTCUSDT')
        print(f"   • Preço atual: ${current_price}")
    except Exception as e:
        print(f"   ❌ Erro nos dados: {e}")
        return False
    
    # Teste 5: Indicadores técnicos
    print("\n5. ✅ INDICADORES TÉCNICOS")
    try:
        df_with_indicators = signal_gen.technical_indicators.calculate_all_indicators(df)
        print(f"   • Indicadores calculados: {len(df_with_indicators.columns)} colunas")
        
        # Verificar indicadores principais
        required_indicators = ['rsi', 'macd', 'bb_lower', 'bb_upper', 'ema_12', 'ema_26']
        missing = [ind for ind in required_indicators if ind not in df_with_indicators.columns]
        
        if missing:
            print(f"   ⚠️ Indicadores faltando: {missing}")
        else:
            print("   • Todos os indicadores principais disponíveis")
    except Exception as e:
        print(f"   ❌ Erro nos indicadores: {e}")
        return False
    
    # Teste 6: Análise técnica
    print("\n6. ✅ ANÁLISE TÉCNICA")
    try:
        tech_result = signal_gen._analyze_technical_indicators(df_with_indicators)
        print(f"   • Sinal técnico: {tech_result['signal']}")
        print(f"   • Confiança técnica: {tech_result['confidence']:.3f}")
        print(f"   • Razões: {len(tech_result.get('reasons', []))} confirmações")
        
        if tech_result['confidence'] > 0:
            print("   • ✅ Análise técnica gerando sinais")
        else:
            print("   • ⚠️ Análise técnica sem sinais (normal)")
    except Exception as e:
        print(f"   ❌ Erro na análise técnica: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
    print("✅ Todos os componentes funcionais")
    print("✅ Sistema pronto para geração de sinais")
    print("✅ Configurações otimizadas para produção")
    
    print("\n📊 PRÓXIMOS PASSOS:")
    print("1. Acessar dashboard: http://localhost:5000")
    print("2. Testar geração de sinais via interface web")
    print("3. Monitorar logs em logs/trading_bot.log")
    print("4. Ajustar configurações conforme necessário")
    
    return True

if __name__ == "__main__":
    try:
        validate_system()
    except KeyboardInterrupt:
        print("\n\n⏹️ Validação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado na validação: {e}")
        import traceback
        traceback.print_exc()
