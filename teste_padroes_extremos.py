#!/usr/bin/env python3
"""
🧪 TESTE COM DADOS EXTREMOS - FORÇAR SINAIS
Testa engines com dados que devem gerar sinais claros de compra/venda
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def create_strong_buy_pattern():
    """Criar padrão forte de compra"""
    periods = 100
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='1h')
    
    # Tendência forte de alta
    base_price = 50000
    prices = []
    
    for i in range(periods):
        # Crescimento progressivo com algumas correções
        if i < 20:
            growth = 0.01  # 1% por hora
        elif i < 80:
            growth = 0.005  # 0.5% por hora  
        else:
            growth = 0.02  # Aceleração final
            
        if i == 0:
            prices.append(base_price)
        else:
            new_price = prices[-1] * (1 + growth + np.random.normal(0, 0.002))
            prices.append(new_price)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.005 for p in prices],
        'low': [p * 0.995 for p in prices],
        'close': prices,
        'volume': [1000000 * (1 + i * 0.1) for i in range(periods)]  # Volume crescente
    })
    
    return df

def create_strong_sell_pattern():
    """Criar padrão forte de venda"""
    periods = 100
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='1h')
    
    # Tendência forte de baixa
    base_price = 50000
    prices = []
    
    for i in range(periods):
        # Queda progressiva
        if i < 20:
            decline = -0.015  # -1.5% por hora
        elif i < 80:
            decline = -0.008  # -0.8% por hora
        else:
            decline = -0.025  # Aceleração da queda
            
        if i == 0:
            prices.append(base_price)
        else:
            new_price = prices[-1] * (1 + decline + np.random.normal(0, 0.002))
            prices.append(max(new_price, base_price * 0.3))  # Não cair abaixo de 30%
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.002 for p in prices],
        'low': [p * 0.998 for p in prices],
        'close': prices,
        'volume': [1000000 * (1 + i * 0.05) for i in range(periods)]  # Volume crescente
    })
    
    return df

def test_engine_with_patterns(engine_name, engine_class):
    """Testar engine com padrões extremos"""
    print(f"🧪 Testando {engine_name} com padrões extremos...")
    
    try:
        from src.config import Config
        config = Config()
        engine = engine_class(config)
        
        results = {}
        
        # Teste 1: Padrão de compra forte
        buy_data = create_strong_buy_pattern()
        print(f"📈 Testando padrão de COMPRA (preço {buy_data['close'].iloc[0]:.0f} → {buy_data['close'].iloc[-1]:.0f})")
        
        if hasattr(engine, 'generate_signal'):
            try:
                signal = engine.generate_signal(buy_data, 'BTCUSDT', '1h')
                results['buy_pattern_generate'] = signal
                print(f"   generate_signal: {signal.get('signal', 'N/A')} (conf: {signal.get('confidence', 'N/A')})")
            except Exception as e:
                print(f"   generate_signal: ERRO - {e}")
        
        if hasattr(engine, 'predict_signal'):
            try:
                signal = engine.predict_signal(buy_data, 'BTCUSDT')
                results['buy_pattern_predict'] = signal
                print(f"   predict_signal: {signal.get('signal_type', signal.get('signal', 'N/A'))} (conf: {signal.get('confidence', 'N/A')})")
            except Exception as e:
                print(f"   predict_signal: ERRO - {e}")
        
        # Teste 2: Padrão de venda forte
        sell_data = create_strong_sell_pattern()
        print(f"📉 Testando padrão de VENDA (preço {sell_data['close'].iloc[0]:.0f} → {sell_data['close'].iloc[-1]:.0f})")
        
        if hasattr(engine, 'generate_signal'):
            try:
                signal = engine.generate_signal(sell_data, 'BTCUSDT', '1h')
                results['sell_pattern_generate'] = signal
                print(f"   generate_signal: {signal.get('signal', 'N/A')} (conf: {signal.get('confidence', 'N/A')})")
            except Exception as e:
                print(f"   generate_signal: ERRO - {e}")
        
        if hasattr(engine, 'predict_signal'):
            try:
                signal = engine.predict_signal(sell_data, 'BTCUSDT')
                results['sell_pattern_predict'] = signal
                print(f"   predict_signal: {signal.get('signal_type', signal.get('signal', 'N/A'))} (conf: {signal.get('confidence', 'N/A')})")
            except Exception as e:
                print(f"   predict_signal: ERRO - {e}")
        
        return {
            'engine': engine_name,
            'success': True,
            'results': results
        }
        
    except Exception as e:
        print(f"❌ Erro com {engine_name}: {e}")
        return {
            'engine': engine_name,
            'success': False,
            'error': str(e)
        }

def main():
    """Teste principal com padrões extremos"""
    print("🚀 TESTE COM PADRÕES EXTREMOS")
    print("=" * 40)
    
    engines = [
        ('AITradingEngine', 'src.ai_engine', 'AITradingEngine'),
        ('UltraFastAIEngine', 'ai_engine_ultra_fast', 'UltraFastAIEngine'),
        ('OptimizedAIEngineV3', 'ai_engine_v3_otimizado', 'OptimizedAIEngineV3'),
        ('UltraEnhancedAIEngine', 'ai_engine_ultra_enhanced', 'UltraEnhancedAIEngine')
    ]
    
    all_results = []
    
    for engine_name, module_name, class_name in engines:
        try:
            module = __import__(module_name, fromlist=[class_name])
            engine_class = getattr(module, class_name)
            result = test_engine_with_patterns(engine_name, engine_class)
            all_results.append(result)
            print()
        except Exception as e:
            print(f"❌ Erro ao importar {engine_name}: {e}")
            print()
    
    # Analisar resultados
    print("📊 ANÁLISE DOS RESULTADOS:")
    print("-" * 40)
    
    for result in all_results:
        if result['success']:
            engine_name = result['engine']
            results = result['results']
            
            buy_signals = []
            sell_signals = []
            
            for key, signal in results.items():
                signal_type = signal.get('signal_type', signal.get('signal', 'unknown'))
                confidence = signal.get('confidence', 0)
                
                if 'buy_pattern' in key:
                    buy_signals.append((signal_type, confidence))
                elif 'sell_pattern' in key:
                    sell_signals.append((signal_type, confidence))
            
            print(f"\n🔧 {engine_name}:")
            print(f"   📈 Padrão de Alta: {buy_signals}")
            print(f"   📉 Padrão de Baixa: {sell_signals}")
            
            # Verificar se detectou corretamente
            buy_correct = any(s[0] in ['buy', 'BUY', 1] for s in buy_signals)
            sell_correct = any(s[0] in ['sell', 'SELL', 0] for s in sell_signals)
            
            if buy_correct and sell_correct:
                print("   ✅ DETECTA PADRÕES CORRETAMENTE")
            elif buy_correct or sell_correct:
                print("   ⚠️ DETECTA PARCIALMENTE")
            else:
                print("   ❌ NÃO DETECTA PADRÕES")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_extreme_patterns_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\n💾 Resultados salvos em: {filename}")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
    
    print("\n✅ Teste com padrões extremos concluído!")

if __name__ == "__main__":
    main()
