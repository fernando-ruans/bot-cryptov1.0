#!/usr/bin/env python3
"""
🎯 TESTE ESPECÍFICO DO AI ENGINE ULTRA - Ajuste de Threshold
Teste com múltiplos thresholds para encontrar o ideal
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_multiple_thresholds():
    """Teste com múltiplos thresholds"""
    
    print("🎯 TESTE DE MÚLTIPLOS THRESHOLDS - AI ENGINE ULTRA")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
        
        config = Config()
        market_data = MarketDataManager(config)
        
        # Testar com BTCUSDT
        symbol = 'BTCUSDT'
        timeframe = '5m'
        
        print(f"\n🔍 Testando {symbol} {timeframe}...")
        
        df = market_data.get_historical_data(symbol, timeframe, 500)
        if df is None or len(df) < 200:
            print("❌ Dados insuficientes")
            return
        
        print(f"📊 Dados obtidos: {len(df)} registros")
        
        # Teste com diferentes thresholds
        thresholds = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]
        
        results = []
        
        for threshold in thresholds:
            print(f"\n📏 Testando threshold: {threshold}")
            
            # Criar engine com threshold específico
            ultra_ai = UltraEnhancedAIEngine(config)
            ultra_ai.min_confidence_threshold = threshold
            
            # Fazer predição
            result = ultra_ai.ultra_predict_signal(df, symbol)
            
            signal_type = result.get('signal_type', 'HOLD')
            confidence = result.get('confidence', 0)
            base_confidence = result.get('base_confidence', 0)
            confluence = result.get('confluence', 0)
            
            results.append({
                'threshold': threshold,
                'signal_type': signal_type,
                'confidence': confidence,
                'base_confidence': base_confidence,
                'confluence': confluence,
                'ultra_enhanced': result.get('ultra_enhanced', False)
            })
            
            print(f"   🎯 Sinal: {signal_type}")
            print(f"   📈 Confiança: {confidence:.3f}")
            print(f"   📊 Base: {base_confidence:.3f}")
            print(f"   🤝 Confluence: {confluence:.3f}")
            
            # Avaliar qualidade
            if signal_type != 'HOLD':
                if confidence >= 0.70:
                    quality = "🟢 ALTA"
                elif confidence >= 0.60:
                    quality = "🟡 MÉDIA"
                else:
                    quality = "🟠 BAIXA"
                print(f"   📊 Qualidade: {quality}")
            else:
                print(f"   📊 Resultado: HOLD (sem trade)")
        
        # Análise dos resultados
        print(f"\n📊 ANÁLISE DOS RESULTADOS:")
        
        buy_signals = [r for r in results if r['signal_type'] == 'BUY']
        sell_signals = [r for r in results if r['signal_type'] == 'SELL']
        hold_signals = [r for r in results if r['signal_type'] == 'HOLD']
        
        print(f"   📈 BUY signals: {len(buy_signals)}")
        print(f"   📉 SELL signals: {len(sell_signals)}")
        print(f"   ⏸️ HOLD signals: {len(hold_signals)}")
        
        # Encontrar threshold ideal
        active_signals = [r for r in results if r['signal_type'] != 'HOLD']
        if active_signals:
            best_signal = max(active_signals, key=lambda x: x['confidence'])
            print(f"\n🏆 MELHOR SINAL:")
            print(f"   Threshold: {best_signal['threshold']}")
            print(f"   Tipo: {best_signal['signal_type']}")
            print(f"   Confiança: {best_signal['confidence']:.3f}")
            
            # Recomendar threshold
            recommended_threshold = best_signal['threshold']
            print(f"\n💡 RECOMENDAÇÃO:")
            print(f"   Threshold recomendado: {recommended_threshold}")
            print(f"   Permite sinais com confiança ≥ {best_signal['confidence']:.3f}")
        else:
            print(f"\n⚠️ NENHUM SINAL ATIVO ENCONTRADO")
            print(f"   Considere reduzir ainda mais o threshold")
            print(f"   Ou verificar se há movimento suficiente no mercado")
        
        # Salvar resultados
        filename = f"teste_thresholds_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_live_signals():
    """Teste de sinais em tempo real com threshold otimizado"""
    
    print("\n" + "=" * 60)
    print("🚀 TESTE DE SINAIS EM TEMPO REAL")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
        
        config = Config()
        market_data = MarketDataManager(config)
        
        # Usar threshold otimizado
        ultra_ai = UltraEnhancedAIEngine(config)
        ultra_ai.min_confidence_threshold = 0.45  # Threshold mais agressivo
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        timeframes = ['1m', '5m']
        
        all_signals = []
        
        for symbol in symbols:
            for timeframe in timeframes:
                print(f"\n🔍 {symbol} {timeframe}:")
                
                df = market_data.get_historical_data(symbol, timeframe, 500)
                if df is None or len(df) < 200:
                    print("   ❌ Dados insuficientes")
                    continue
                
                result = ultra_ai.ultra_predict_signal(df, symbol)
                
                signal_type = result.get('signal_type', 'HOLD')
                confidence = result.get('confidence', 0)
                
                print(f"   🎯 {signal_type} (conf: {confidence:.3f})")
                
                if signal_type != 'HOLD':
                    all_signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal': signal_type,
                        'confidence': confidence,
                        'entry_price': result.get('entry_price', 0),
                        'stop_loss': result.get('stop_loss', 0),
                        'take_profit': result.get('take_profit', 0)
                    })
                    
                    print(f"   💰 Entry: ${result.get('entry_price', 0):.2f}")
                    print(f"   🛡️ SL: ${result.get('stop_loss', 0):.2f}")
                    print(f"   🎯 TP: ${result.get('take_profit', 0):.2f}")
        
        print(f"\n📊 RESUMO DE SINAIS ATIVOS:")
        print(f"   Total: {len(all_signals)}")
        
        if all_signals:
            buy_count = len([s for s in all_signals if s['signal'] == 'BUY'])
            sell_count = len([s for s in all_signals if s['signal'] == 'SELL'])
            avg_confidence = np.mean([s['confidence'] for s in all_signals])
            
            print(f"   📈 BUY: {buy_count}")
            print(f"   📉 SELL: {sell_count}")
            print(f"   📊 Confiança média: {avg_confidence:.3f}")
            
            # Mostrar melhores sinais
            best_signals = sorted(all_signals, key=lambda x: x['confidence'], reverse=True)[:3]
            
            print(f"\n🏆 TOP 3 SINAIS:")
            for i, signal in enumerate(best_signals, 1):
                print(f"   {i}. {signal['symbol']} {signal['timeframe']}: {signal['signal']} ({signal['confidence']:.3f})")
        else:
            print("   ⚠️ Nenhum sinal ativo no momento")
        
        return all_signals
        
    except Exception as e:
        print(f"❌ Erro no teste live: {e}")
        return []

def main():
    """Função principal"""
    
    # Teste 1: Múltiplos thresholds
    threshold_results = test_multiple_thresholds()
    
    # Teste 2: Sinais em tempo real
    live_signals = test_live_signals()
    
    print(f"\n✅ TESTES CONCLUÍDOS!")
    
    if threshold_results:
        active_count = len([r for r in threshold_results if r['signal_type'] != 'HOLD'])
        print(f"📊 Thresholds testados: {len(threshold_results)}")
        print(f"📈 Sinais ativos encontrados: {active_count}")
    
    if live_signals:
        print(f"🚀 Sinais de trading disponíveis: {len(live_signals)}")
    else:
        print(f"⚠️ Nenhum sinal de alta confiança no momento")

if __name__ == "__main__":
    main()
