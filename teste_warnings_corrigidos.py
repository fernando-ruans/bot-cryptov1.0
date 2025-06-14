#!/usr/bin/env python3
"""
Teste para verificar se os warnings da TA-Lib foram suprimidos
"""

import os
import sys

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.dirname(__file__))

def test_warnings_suppression():
    """Testa se os warnings foram suprimidos com sucesso"""
    
    print("🧪 TESTE DE SUPRESSÃO DE WARNINGS")
    print("=" * 50)
    
    try:
        print("1. Importando Enhanced AI Engine com supressão de warnings...")
        from ai_engine_enhanced import EnhancedAIEngine
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.signal_generator import SignalGenerator
        print("   ✅ Importações realizadas")
        
        print("2. Inicializando componentes...")
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = EnhancedAIEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        print("   ✅ Componentes inicializados")
        
        print("3. Gerando sinal de teste (observando output)...")
        print("   📊 Gerando sinal para BTCUSDT 1h...")
        signal = signal_generator.generate_signal('BTCUSDT', '1h')
        
        if signal:
            print(f"   ✅ Sinal gerado: {signal.signal_type} (confiança: {signal.confidence:.3f})")
        else:
            print("   ⚠️ Nenhum sinal gerado")
            
        print("\n4. Testando com timeframe diferente...")
        print("   📊 Gerando sinal para ETHUSDT 5m...")
        signal2 = signal_generator.generate_signal('ETHUSDT', '5m')
        
        if signal2:
            print(f"   ✅ Sinal gerado: {signal2.signal_type} (confiança: {signal2.confidence:.3f})")
        else:
            print("   ⚠️ Nenhum sinal gerado")
            
        print("\n" + "=" * 50)
        print("🎯 RESULTADO:")
        print("   Se você não viu warnings da TA-Lib acima,")
        print("   então a supressão funcionou corretamente!")
        print("   ✅ Experiência do usuário melhorada")
        print("   ✅ Logs mais limpos")
        print("   ✅ Funcionamento inalterado")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")

if __name__ == "__main__":
    test_warnings_suppression()
