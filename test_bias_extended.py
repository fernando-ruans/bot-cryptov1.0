#!/usr/bin/env python3
"""
Teste abrangente com 10 símbolos para detectar viés de sinais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator
import logging

# Configurar log para mostrar apenas info importante
logging.getLogger().setLevel(logging.WARNING)

def test_bias_with_10_results():
    """Teste extensivo com 10 símbolos para detectar viés"""
    print("=== TESTE DE VIÉS COM 10 SÍMBOLOS ===")
    
    # Configurar componentes
    config = Config()
    # Reduzir thresholds para forçar mais sinais
    config.SIGNAL_CONFIG['min_ai_confidence'] = 0.01
    config.SIGNAL_CONFIG['min_market_score'] = 0.01
    config.SIGNAL_CONFIG['min_confluence_count'] = 1
    
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    # 10 símbolos diferentes para teste abrangente
    symbols = [
        'BTCUSDT',  # Bitcoin
        'ETHUSDT',  # Ethereum
        'ADAUSDT',  # Cardano
        'SOLUSDT',  # Solana
        'DOTUSDT',  # Polkadot
        'LINKUSDT', # Chainlink
        'MATICUSDT',# Polygon
        'AVAXUSDT', # Avalanche
        'ATOMUSDT', # Cosmos
        'NEARUSDT'  # Near Protocol
    ]
    
    timeframes = ['1h', '4h']  # 2 timeframes para cada símbolo
    
    signal_counts = {'buy': 0, 'sell': 0, 'hold': 0, 'error': 0}
    signal_details = []
    
    total_tests = len(symbols) * len(timeframes)
    print(f"Testando {len(symbols)} símbolos x {len(timeframes)} timeframes = {total_tests} combinações")
    print()
    
    test_count = 0
    for symbol in symbols:
        for timeframe in timeframes:
            test_count += 1
            try:
                print(f"[{test_count:2d}/{total_tests}] {symbol} {timeframe}...", end=" ")
                
                # Tentar gerar sinal real
                signal = signal_generator.generate_signal(symbol, timeframe)
                
                if signal:
                    signal_type = signal.signal_type
                    signal_counts[signal_type] += 1
                    signal_details.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal': signal_type,
                        'confidence': signal.confidence,
                        'reasons': signal.reasons[:2] if signal.reasons else []
                    })
                    print(f"{signal_type.upper()} ({signal.confidence:.2f})")
                else:
                    signal_counts['hold'] += 1
                    print("HOLD")
                    
            except Exception as e:
                signal_counts['error'] += 1
                error_msg = str(e)[:30]
                print(f"ERRO: {error_msg}...")
    
    # Análise detalhada dos resultados
    print()
    print("=== ANÁLISE DETALHADA DOS RESULTADOS ===")
    total_signals = signal_counts['buy'] + signal_counts['sell'] + signal_counts['hold']
    total_actionable = signal_counts['buy'] + signal_counts['sell']
    
    print(f"Sinais BUY:  {signal_counts['buy']:2d}")
    print(f"Sinais SELL: {signal_counts['sell']:2d}")
    print(f"Sinais HOLD: {signal_counts['hold']:2d}")
    print(f"Erros:       {signal_counts['error']:2d}")
    print(f"Total:       {total_signals:2d}")
    print()
    
    if total_actionable > 0:
        buy_percentage = (signal_counts['buy'] / total_actionable) * 100
        sell_percentage = (signal_counts['sell'] / total_actionable) * 100
        
        print(f"DISTRIBUIÇÃO DOS SINAIS ACIONÁVEIS:")
        print(f"BUY:  {buy_percentage:5.1f}% ({signal_counts['buy']} sinais)")
        print(f"SELL: {sell_percentage:5.1f}% ({signal_counts['sell']} sinais)")
        print()
        
        # Análise de viés detalhada
        if signal_counts['sell'] == 0:
            print("🚨 VIÉS CRÍTICO DETECTADO: O sistema NÃO gera sinais de VENDA!")
            print("   ⚠️  100% dos sinais são de COMPRA")
            print("   📊 Isso indica um problema sério na lógica de decisão")
            print()
            print("   🔍 POSSÍVEIS CAUSAS:")
            print("   1. Multiplicador de risco duplicado para sell_score")
            print("   2. Thresholds diferentes para buy vs sell")
            print("   3. Indicadores técnicos tendenciosos")
            print("   4. IA treinada com dados tendenciosos")
            print("   5. Lógica de combinação de análises favorece compras")
            
        elif signal_counts['buy'] == 0:
            print("🚨 VIÉS CRÍTICO DETECTADO: O sistema NÃO gera sinais de COMPRA!")
            print("   ⚠️  100% dos sinais são de VENDA")
            
        elif buy_percentage > 80:
            print(f"⚠️  VIÉS FORTE DETECTADO: {buy_percentage:.1f}% dos sinais são de compra")
            print("   📊 Distribuição muito desequilibrada")
            
        elif buy_percentage < 20:
            print(f"⚠️  VIÉS FORTE DETECTADO: Apenas {buy_percentage:.1f}% dos sinais são de compra")
            print("   📊 Sistema favorece muito as vendas")
            
        elif abs(buy_percentage - 50) > 20:
            print(f"⚠️  VIÉS MODERADO: Distribuição {buy_percentage:.1f}% BUY / {sell_percentage:.1f}% SELL")
            
        else:
            print("✅ DISTRIBUIÇÃO BALANCEADA")
            print(f"   📊 {buy_percentage:.1f}% BUY / {sell_percentage:.1f}% SELL")
            print("   ✅ Sistema aparenta estar funcionando corretamente")
            
    else:
        print("⚠️  PROBLEMA: Nenhum sinal acionável foi gerado")
        print("   🔍 Verifique se os thresholds não estão muito altos")
    
    # Mostrar exemplos de sinais gerados
    if signal_details:
        print()
        print("=== EXEMPLOS DE SINAIS GERADOS ===")
        
        buy_signals = [s for s in signal_details if s['signal'] == 'buy']
        sell_signals = [s for s in signal_details if s['signal'] == 'sell']
        
        if buy_signals:
            print(f"\n📈 SINAIS DE COMPRA ({len(buy_signals)}):")
            for detail in buy_signals[:3]:  # Mostrar até 3 exemplos
                reasons_str = ', '.join(detail['reasons']) if detail['reasons'] else 'N/A'
                print(f"   • {detail['symbol']} {detail['timeframe']}: "
                      f"BUY ({detail['confidence']:.2f}) - {reasons_str}")
        
        if sell_signals:
            print(f"\n📉 SINAIS DE VENDA ({len(sell_signals)}):")
            for detail in sell_signals[:3]:  # Mostrar até 3 exemplos
                reasons_str = ', '.join(detail['reasons']) if detail['reasons'] else 'N/A'
                print(f"   • {detail['symbol']} {detail['timeframe']}: "
                      f"SELL ({detail['confidence']:.2f}) - {reasons_str}")
        
        if not sell_signals:
            print(f"\n📉 SINAIS DE VENDA: NENHUM ❌")
    
    # Recomendações baseadas nos resultados
    print()
    print("=== RECOMENDAÇÕES ===")
    if signal_counts['sell'] == 0 and signal_counts['buy'] > 0:
        print("🔧 AÇÃO NECESSÁRIA:")
        print("   1. Verificar e corrigir lógica de cálculo de sell_score")
        print("   2. Revisar thresholds para sinais de venda")
        print("   3. Analisar indicadores técnicos para condições de venda")
        print("   4. Verificar se IA está gerando sinais de venda")
    elif total_actionable == 0:
        print("🔧 AJUSTAR CONFIGURAÇÕES:")
        print("   1. Reduzir thresholds de confiança")
        print("   2. Verificar dados de mercado")
        print("   3. Validar cálculos de indicadores técnicos")
    else:
        print("✅ Sistema funcionando adequadamente")

if __name__ == "__main__":
    test_bias_with_10_results()
