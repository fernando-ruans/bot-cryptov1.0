#!/usr/bin/env python3
"""
Teste simples para verificar se o sistema ainda gera sinais HOLD
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.WARNING)

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_signal():
    """Teste simples de sinal"""
    try:
        # Tentar importar os módulos necessários
        print("🔍 Tentando imports...")
        
        # Mudar imports relativos para absolutos temporariamente
        import signal_generator
        print("✅ signal_generator importado")
        
        # Verificar se a classe existe
        if hasattr(signal_generator, 'SignalGenerator'):
            print("✅ Classe SignalGenerator encontrada")
            
            # Tentar criar uma instância
            from config import Config
            config = Config()
            
            # Criar configuração mínima para teste
            config.THRESHOLDS = {
                'min_confidence': 0.01,
                'strong_signal': 0.6,
                'medium_signal': 0.4,
                'weak_signal': 0.2
            }
            
            generator = signal_generator.SignalGenerator(config)
            print("✅ SignalGenerator criado com sucesso")
            
            # Dados de teste simples
            test_data = {
                'symbol': 'BTCUSDT',
                'close': [50000, 50100, 50200, 50150, 50300],
                'volume': [1000, 1100, 1050, 1200, 1150],
                'high': [50100, 50200, 50300, 50250, 50400],
                'low': [49900, 50000, 50100, 50050, 50200],
                'timestamp': [1, 2, 3, 4, 5]
            }
            
            # Tentar gerar um sinal
            signal = generator.generate_signal(test_data)
            print(f"✅ Sinal gerado: {signal}")
            
            if signal and hasattr(signal, 'signal_type'):
                print(f"📊 Tipo de sinal: {signal.signal_type}")
                print(f"📊 Confiança: {getattr(signal, 'confidence', 'N/A')}")
                
                if signal.signal_type == 'hold':
                    print("⚠️ Sistema ainda gera sinais HOLD")
                    return False
                else:
                    print("✅ Sistema não gerou HOLD")
                    return True
            else:
                print("❌ Sinal inválido gerado")
                return False
                
        else:
            print("❌ Classe SignalGenerator não encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Teste simples de verificação de HOLD...")
    success = test_simple_signal()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou!")
