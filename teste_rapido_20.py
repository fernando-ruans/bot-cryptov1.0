#!/usr/bin/env python3
"""
TESTE SIMPLIFICADO - 20 ATIVOS
"""

import time
import json
from datetime import datetime
from collections import Counter

def test_simple():
    """Teste simplificado com 20 ativos"""
    
    print("🧪 TESTE SIMPLIFICADO - 20 ATIVOS")
    print("=" * 50)
    
    # Lista de 20 ativos
    assets = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
        'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LUNAUSDT',
        'LINKUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'VETUSDT',
        'EOSUSDT', 'TRXUSDT', 'XLMUSDT', 'AAVEUSDT', 'COMPUSDT'
    ]
    
    results = []
    
    try:        print("🔧 Importando módulos...")
        from src.config import Config
        from src.market_data import MarketDataManager  
        from src.signal_generator import SignalGenerator
        from src.ai_engine import AITradingEngine
        
        print("🔧 Inicializando componentes...")
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        print("🚀 Executando testes...")
        
        for i, asset in enumerate(assets[:5], 1):  # Apenas 5 para teste rápido
            print(f"🔍 [{i}/5] {asset}...")
            
            try:
                signal_result = signal_generator.generate_signal(asset, '1h')
                signal = signal_result.get('signal', 'NONE')
                confidence = signal_result.get('confidence', 0.0)
                
                results.append({
                    'asset': asset,
                    'signal': signal,
                    'confidence': confidence
                })
                
                emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡', 'NONE': '⚪'}.get(signal, '❓')
                print(f"  {emoji} {signal} ({confidence:.2f})")
                
            except Exception as e:
                print(f"  ❌ Erro: {e}")
                results.append({'asset': asset, 'signal': 'ERROR', 'confidence': 0.0})
        
        # Análise rápida
        print("\n📊 RESULTADOS:")
        signal_counts = Counter([r['signal'] for r in results])
        
        for signal_type in ['BUY', 'SELL', 'HOLD', 'NONE', 'ERROR']:
            count = signal_counts.get(signal_type, 0)
            if count > 0:
                emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡', 'NONE': '⚪', 'ERROR': '❌'}.get(signal_type, '❓')
                print(f"{emoji} {signal_type}: {count}")
        
        # Salvar resultado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_rapido_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({'results': results, 'timestamp': timestamp}, f, indent=2)
        
        print(f"\n📁 Resultados salvos: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return False

if __name__ == "__main__":
    test_simple()
