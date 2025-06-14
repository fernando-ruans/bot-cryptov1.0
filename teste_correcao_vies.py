#!/usr/bin/env python3
"""
Script de teste para validar as correções do viés BUY
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import logging
from datetime import datetime
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bias_correction():
    """Testa se as correções resolveram o viés de 100% BUY"""
    
    print("🧪 TESTE DE CORREÇÃO DE VIÉS")
    print("=" * 50)
    
    try:
        # Configuração
        config = Config()
        
        # Inicializar componentes
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        # Lista de ativos para teste
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT']
        timeframes = ['1h', '4h']
        
        results = {
            'buy': 0,
            'sell': 0,
            'hold': 0,
            'none': 0,
            'details': []
        }
        
        total_tests = len(symbols) * len(timeframes)
        print(f"📊 Executando {total_tests} testes...")
        print()
        
        for symbol in symbols:
            for timeframe in timeframes:
                print(f"🔍 Testando {symbol} {timeframe}...")
                
                try:
                    # Gerar sinal
                    signal = signal_generator.generate_signal(symbol, timeframe)
                    
                    if signal is None:
                        signal_type = 'none'
                        confidence = 0.0
                        reason = 'Nenhum sinal gerado'
                    else:
                        signal_type = signal.signal_type
                        confidence = signal.confidence
                        reason = getattr(signal, 'reason', 'N/A')
                    
                    # Contar resultado
                    results[signal_type] += 1
                    
                    # Armazenar detalhes
                    results['details'].append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal': signal_type,
                        'confidence': confidence,
                        'reason': reason
                    })
                    
                    print(f"  ✅ {signal_type.upper()} (confiança: {confidence:.2f})")
                    
                except Exception as e:
                    print(f"  ❌ Erro: {e}")
                    results['none'] += 1
                    results['details'].append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal': 'error',
                        'confidence': 0.0,
                        'reason': str(e)
                    })
        
        print()
        print("📊 RESULTADOS:")
        print("=" * 30)
        print(f"BUY:  {results['buy']:2d} ({results['buy']/total_tests*100:.1f}%)")
        print(f"SELL: {results['sell']:2d} ({results['sell']/total_tests*100:.1f}%)")
        print(f"HOLD: {results['hold']:2d} ({results['hold']/total_tests*100:.1f}%)")
        print(f"NONE: {results['none']:2d} ({results['none']/total_tests*100:.1f}%)")
        print()
        
        # Análise de viés
        total_signals = results['buy'] + results['sell'] + results['hold']
        if total_signals > 0:
            buy_pct = results['buy'] / total_signals * 100
            sell_pct = results['sell'] / total_signals * 100
            hold_pct = results['hold'] / total_signals * 100
            
            print("🎯 ANÁLISE DE VIÉS:")
            print(f"  BUY:  {buy_pct:.1f}%")
            print(f"  SELL: {sell_pct:.1f}%")
            print(f"  HOLD: {hold_pct:.1f}%")
            print()
            
            # Verificar se o viés foi corrigido
            if buy_pct > 80:
                print("❌ VIÉS BUY AINDA PRESENTE!")
                status = "FAILED"
            elif sell_pct > 80:
                print("❌ NOVO VIÉS SELL DETECTADO!")
                status = "FAILED"
            elif hold_pct > 80:
                print("❌ VIÉS HOLD DETECTADO!")
                status = "FAILED"
            else:
                print("✅ DISTRIBUIÇÃO BALANCEADA!")
                status = "SUCCESS"
        else:
            print("❌ NENHUM SINAL GERADO!")
            status = "FAILED"
        
        # Salvar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'teste_correcao_vies_{timestamp}.json'
        
        test_results = {
            'timestamp': timestamp,
            'status': status,
            'total_tests': total_tests,
            'summary': results,
            'buy_percentage': buy_pct if total_signals > 0 else 0,
            'sell_percentage': sell_pct if total_signals > 0 else 0,
            'hold_percentage': hold_pct if total_signals > 0 else 0
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Resultados salvos em: {filename}")
        print()
        
        if status == "SUCCESS":
            print("🎉 CORREÇÃO APLICADA COM SUCESSO!")
        else:
            print("⚠️ CORREÇÃO AINDA NECESSÁRIA!")
        
        return status == "SUCCESS"
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_bias_correction()
