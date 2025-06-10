#!/usr/bin/env python3
"""
Teste para detectar se o sistema tem viés para sinais de compra
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

def test_signal_bias():
    """Teste para detectar viés nos sinais"""
    print("=== TESTE DE VIÉS DE SINAIS ===")
    
    # Configurar componentes
    config = Config()
    # Reduzir thresholds para forçar mais sinais
    config.SIGNAL_CONFIG['min_ai_confidence'] = 0.01
    config.SIGNAL_CONFIG['min_market_score'] = 0.01
    config.SIGNAL_CONFIG['min_confluence_count'] = 1
    
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    # Símbolos e timeframes para teste
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
    timeframes = ['1h', '4h']
    
    signal_counts = {'buy': 0, 'sell': 0, 'hold': 0, 'error': 0}
    signal_details = []
    
    print(f"Testando {len(symbols)} símbolos x {len(timeframes)} timeframes = {len(symbols) * len(timeframes)} combinações")
    print()
    
    for symbol in symbols:
        for timeframe in timeframes:
            try:
                print(f"Testando {symbol} {timeframe}...", end=" ")
                
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
                        'reasons': signal.reasons[:2]  # Apenas as 2 primeiras razões
                    })
                    print(f"{signal_type.upper()} ({signal.confidence:.2f})")
                else:
                    signal_counts['hold'] += 1
                    print("HOLD")
                    
            except Exception as e:
                signal_counts['error'] += 1
                print(f"ERRO: {str(e)[:50]}...")
    
    # Análise dos resultados
    print()
    print("=== RESULTADOS ===")
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
        
        print(f"Entre sinais acionáveis (BUY/SELL):")
        print(f"BUY:  {buy_percentage:.1f}%")
        print(f"SELL: {sell_percentage:.1f}%")
        print()
        
        # Detectar viés
        if signal_counts['sell'] == 0:
            print("🚨 VIÉS DETECTADO: O sistema NÃO está gerando sinais de VENDA!")
            print("   Possíveis causas:")
            print("   - Lógica de decisão favorece apenas compras")
            print("   - Thresholds muito altos para sinais de venda")
            print("   - Indicadores técnicos não estão detectando condições de venda")
        elif buy_percentage > 80:
            print(f"⚠️  POSSÍVEL VIÉS: {buy_percentage:.1f}% dos sinais são de compra")
        elif buy_percentage < 20:
            print(f"⚠️  POSSÍVEL VIÉS: Muito poucos sinais de compra ({buy_percentage:.1f}%)")
        else:
            print("✅ Distribuição de sinais aparenta estar balanceada")
    else:
        print("⚠️  Nenhum sinal acionável foi gerado")
    
    # Mostrar alguns exemplos de sinais
    if signal_details:
        print()
        print("=== EXEMPLOS DE SINAIS GERADOS ===")
        for detail in signal_details[:5]:  # Mostrar apenas os 5 primeiros
            print(f"{detail['symbol']} {detail['timeframe']}: {detail['signal'].upper()} "
                  f"({detail['confidence']:.2f}) - {', '.join(detail['reasons'])}")

if __name__ == "__main__":
    test_signal_bias()
