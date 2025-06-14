#!/usr/bin/env python3
"""
TESTE RÁPIDO DE VIÉS
Teste simples para verificar qual sinal está sendo gerado
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_signal_generation():
    """Teste rápido de geração de sinais"""
    print("🧪 TESTE RÁPIDO DE VIÉS")
    print("=" * 40)
    
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
        
        # Testar alguns ativos
        test_assets = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        for asset in test_assets:
            print(f"\n🔍 Testando {asset}...")
            try:
                signal_result = signal_generator.generate_signal(asset, '1h')
                
                if signal_result:
                    signal = signal_result.signal_type
                    confidence = signal_result.confidence
                    
                    emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡'}.get(signal, '❓')
                    print(f"  {emoji} {signal} (confiança: {confidence:.2f})")
                else:
                    print(f"  ⚪ Nenhum sinal gerado")
                    
            except Exception as e:
                print(f"  ❌ Erro: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_signal_generation()
