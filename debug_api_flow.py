#!/usr/bin/env python3
"""
Script para debugar o fluxo completo da API de geração de sinais
"""

import logging
import sys
from datetime import datetime

# Configurar logging igual à aplicação
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Importar módulos
from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.config import Config

def test_api_flow():
    """Simular exatamente o fluxo da API"""
    print("=== INICIANDO DEBUG DO FLUXO DA API ===")
    
    try:
        # Inicializar componentes (igual ao main.py)
        print("1. Inicializando componentes...")
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        print("✓ Componentes inicializados")
        
        # Verificar configurações atuais
        print("\n2. Verificando configurações...")
        print(f"   min_confidence: {config.SIGNAL_CONFIG['min_confidence']}")
        print(f"   enable_confluence: {config.SIGNAL_CONFIG['enable_confluence']}")
        print(f"   min_confluence_count: {config.SIGNAL_CONFIG['min_confluence_count']}")
        print(f"   signal_cooldown_minutes: {config.SIGNAL_CONFIG['signal_cooldown_minutes']}")
        print(f"   max_signals_per_hour: {config.SIGNAL_CONFIG['max_signals_per_hour']}")
        
        # Simular parâmetros da API
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        print(f"\n3. Tentando gerar sinal para {symbol} {timeframe}...")
        
        # Chamar o método exato da API
        signal = signal_generator.generate_signal(symbol, timeframe)
        
        print(f"\n4. Resultado:")
        if signal is None:
            print("   ❌ Nenhum sinal gerado")
            
            # Vamos testar cada etapa individualmente
            print("\n5. Testando etapas individuais:")
            
            # 5.1 Verificar cooldown
            print("   5.1 Verificando cooldown...")
            is_cooldown = signal_generator._is_in_cooldown(symbol)
            print(f"       Em cooldown: {is_cooldown}")
            
            # 5.2 Verificar dados de mercado
            print("   5.2 Verificando dados de mercado...")
            df = market_data.get_historical_data(symbol, timeframe, 100)
            if df is None or df.empty:
                print("       ❌ Dados não disponíveis")
                return
            else:
                print(f"       ✓ Dados disponíveis: {len(df)} registros")
            
            # 5.3 Calcular indicadores
            print("   5.3 Calculando indicadores técnicos...")
            df = signal_generator.technical_indicators.calculate_all_indicators(df)
            print(f"       ✓ Indicadores calculados")
            
            # 5.4 Testar análise técnica
            print("   5.4 Testando análise técnica...")
            technical_analysis = signal_generator._analyze_technical_indicators(df)
            print(f"       Resultado: {technical_analysis['signal']} (confiança: {technical_analysis['confidence']:.2f})")
            print(f"       Razões: {technical_analysis['reasons']}")
            
            # 5.5 Testar predição de IA
            print("   5.5 Testando predição de IA...")
            ai_prediction = ai_engine.predict_signal(df, symbol)
            print(f"       Resultado IA: {ai_prediction}")
            
            # 5.6 Testar análise de volume
            print("   5.6 Testando análise de volume...")
            volume_analysis = signal_generator._analyze_volume(df)
            print(f"       Volume: {volume_analysis['signal']} (confiança: {volume_analysis['confidence']:.2f})")
            
            # 5.7 Testar análise de volatilidade
            print("   5.7 Testando análise de volatilidade...")
            volatility_analysis = signal_generator._analyze_volatility(df)
            print(f"       Volatilidade: {volatility_analysis['signal']} (confiança: {volatility_analysis['confidence']:.2f})")
            
            # 5.8 Testar combinação de análises
            print("   5.8 Testando combinação de análises...")
            market_context = signal_generator._analyze_market_context(symbol, timeframe)
            combined_signal = signal_generator._combine_analyses(
                technical_analysis,
                ai_prediction,
                volume_analysis,
                volatility_analysis,
                market_context
            )
            print(f"       Sinal combinado: {combined_signal['signal']} (confiança: {combined_signal['confidence']:.2f})")
            print(f"       Razões combinadas: {combined_signal['reasons']}")
            
            # 5.9 Verificar confluência
            print("   5.9 Verificando confluência...")
            if config.SIGNAL_CONFIG['enable_confluence']:
                confluence_check = signal_generator._check_confluence(combined_signal)
                print(f"       Confluência OK: {confluence_check}")
            else:
                print("       Confluência desabilitada")
            
            # 5.10 Verificar confiança mínima
            print("   5.10 Verificando confiança mínima...")
            min_confidence = config.SIGNAL_CONFIG['min_confidence']
            meets_confidence = combined_signal['confidence'] >= min_confidence
            print(f"       Confiança atual: {combined_signal['confidence']:.2f}")
            print(f"       Confiança mínima: {min_confidence:.2f}")
            print(f"       Atende requisito: {meets_confidence}")
            
        else:
            print(f"   ✓ Sinal gerado: {signal.signal_type}")
            print(f"     Confiança: {signal.confidence:.2f}")
            print(f"     Preço entrada: ${signal.entry_price:.2f}")
            print(f"     Stop Loss: ${signal.stop_loss:.2f}")
            print(f"     Take Profit: ${signal.take_profit:.2f}")
            print(f"     Razões: {signal.reasons}")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_flow()
