#!/usr/bin/env python3
"""
DIAGNÓSTICO PROFUNDO DE VIÉS
Teste detalhado para encontrar a fonte do viés nos sinais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def detailed_bias_analysis():
    """Análise detalhada dos componentes de sinal"""
    print("🔬 DIAGNÓSTICO PROFUNDO DE VIÉS")
    print("=" * 50)
    
    try:
        # Importar classes necessárias
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.ai_engine import AITradingEngine
        from src.signal_generator import SignalGenerator
        
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        # Testar 10 ativos
        test_assets = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 
                      'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT']
        
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0, 'ERROR': 0}
        detailed_results = []
        
        for i, asset in enumerate(test_assets, 1):
            print(f"\n📊 [{i:2d}/10] Analisando {asset}...")
            
            try:
                # Obter dados
                df = market_data.get_historical_data(asset, '1h', 500)
                if df is None or df.empty:
                    print(f"  ❌ Sem dados para {asset}")
                    signal_counts['ERROR'] += 1
                    continue
                
                # Testar análise técnica isoladamente
                technical_result = signal_generator._analyze_technical_indicators(df)
                tech_signal = technical_result.get('signal', 'hold')
                tech_confidence = technical_result.get('confidence', 0)
                
                # Testar IA isoladamente
                ai_result = ai_engine.predict_signal(df, asset)
                ai_signal_num = ai_result.get('signal', 0)
                ai_signal = {1: 'buy', -1: 'sell', 0: 'hold'}.get(ai_signal_num, 'hold')
                ai_confidence = ai_result.get('confidence', 0)
                
                # Sinal completo
                full_signal = signal_generator.generate_signal(asset, '1h')
                
                if full_signal:
                    final_signal = full_signal.signal_type
                    final_confidence = full_signal.confidence
                    signal_counts[final_signal] += 1
                else:
                    final_signal = 'NONE'
                    final_confidence = 0
                    signal_counts['ERROR'] += 1
                
                result = {
                    'asset': asset,
                    'technical': {'signal': tech_signal, 'confidence': tech_confidence},
                    'ai': {'signal': ai_signal, 'confidence': ai_confidence},
                    'final': {'signal': final_signal, 'confidence': final_confidence}
                }
                detailed_results.append(result)
                
                # Exibir resultado com cores
                tech_emoji = {'buy': '🟢', 'sell': '🔴', 'hold': '🟡'}.get(tech_signal, '❓')
                ai_emoji = {'buy': '🟢', 'sell': '🔴', 'hold': '🟡'}.get(ai_signal, '❓')
                final_emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡', 'NONE': '⚪'}.get(final_signal, '❓')
                
                print(f"  📈 Técnico: {tech_emoji} {tech_signal.upper()} ({tech_confidence:.2f})")
                print(f"  🤖 IA:      {ai_emoji} {ai_signal.upper()} ({ai_confidence:.2f})")
                print(f"  🎯 Final:   {final_emoji} {final_signal} ({final_confidence:.2f})")
                
            except Exception as e:
                print(f"  ❌ Erro: {e}")
                signal_counts['ERROR'] += 1
        
        # Análise final
        print(f"\n📊 RESULTADO FINAL:")
        print("=" * 30)
        
        total_valid = sum(signal_counts[k] for k in ['BUY', 'SELL', 'HOLD'])
        
        for signal_type, count in signal_counts.items():
            if total_valid > 0:
                percentage = (count / total_valid * 100) if signal_type != 'ERROR' else 0
            else:
                percentage = 0
            
            emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡', 'ERROR': '❌'}.get(signal_type, '❓')
            bar = "█" * int(percentage // 5)
            print(f"{emoji} {signal_type:5s}: {count:2d} ({percentage:5.1f}%) {bar}")
        
        # Detectar viés
        if total_valid > 0:
            buy_pct = (signal_counts['BUY'] / total_valid) * 100
            sell_pct = (signal_counts['SELL'] / total_valid) * 100
            
            print(f"\n🔍 ANÁLISE DE VIÉS:")
            if buy_pct > 80:
                print(f"⚠️ VIÉS DETECTADO: Favorece BUY ({buy_pct:.1f}%)")
            elif sell_pct > 80:
                print(f"⚠️ VIÉS DETECTADO: Favorece SELL ({sell_pct:.1f}%)")
            elif abs(buy_pct - sell_pct) <= 20:
                print(f"✅ DISTRIBUIÇÃO BALANCEADA! (BUY: {buy_pct:.1f}%, SELL: {sell_pct:.1f}%)")
            else:
                print(f"⚖️ LIGEIRO DESEQUILÍBRIO (BUY: {buy_pct:.1f}%, SELL: {sell_pct:.1f}%)")
        
        # Análise por componente
        print(f"\n🔍 ANÁLISE POR COMPONENTE:")
        print("-" * 30)
        
        tech_signals = [r['technical']['signal'] for r in detailed_results]
        ai_signals = [r['ai']['signal'] for r in detailed_results]
        
        from collections import Counter
        tech_counts = Counter(tech_signals)
        ai_counts = Counter(ai_signals)
        
        print(f"📈 Análise Técnica:")
        for signal in ['buy', 'sell', 'hold']:
            count = tech_counts.get(signal, 0)
            pct = (count / len(tech_signals) * 100) if tech_signals else 0
            print(f"   {signal.upper()}: {count} ({pct:.1f}%)")
        
        print(f"🤖 IA:")
        for signal in ['buy', 'sell', 'hold']:
            count = ai_counts.get(signal, 0)
            pct = (count / len(ai_signals) * 100) if ai_signals else 0
            print(f"   {signal.upper()}: {count} ({pct:.1f}%)")
        
        return detailed_results
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    detailed_bias_analysis()
