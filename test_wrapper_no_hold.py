#!/usr/bin/env python3
"""
Wrapper para eliminar sinais HOLD do sistema de trading
"""

import sys
import os

# Adicionar o diretório raiz ao path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# Agora importar do src
try:
    from src.signal_generator import SignalGenerator
    from src.config import Config
except ImportError as e:
    print(f"Erro de import: {e}")
    print("Tentando import alternativo...")
    # Fallback: adicionar src ao path
    sys.path.insert(0, os.path.join(project_root, 'src'))
    from signal_generator import SignalGenerator
    from config import Config

import logging

logger = logging.getLogger(__name__)

class NoHoldSignalGenerator:
    """Wrapper que converte todos os sinais HOLD em BUY ou SELL"""
    
    def __init__(self, config=None):
        if config is None:
            config = Config()
          # Criar o gerador original
        self.original_generator = SignalGenerator(config)
        self.config = config
        
    def generate_signal(self, market_data):
        """Gerar sinal garantindo que nunca retorne HOLD"""
        try:
            # Obter sinal original
            original_signal = self.original_generator.generate_signal(market_data)
            
            # Se não é HOLD, retornar normalmente
            if original_signal and original_signal.get('signal') != 'hold':
                return original_signal
            
            # Se é HOLD ou None, forçar geração de BUY/SELL
            return self._force_signal(market_data, original_signal)
            
        except Exception as e:
            logger.error(f"Erro na geração de sinal: {e}")
            return self._emergency_signal(market_data)
    
    def _force_signal(self, market_data, original_signal):
        """Forçar geração de BUY ou SELL quando signal original é HOLD"""
        try:
            symbol = market_data.get('symbol', 'UNKNOWN')
            
            # Estratégia 1: Análise simples de momentum de preço
            prices = market_data.get('close', [])
            if len(prices) >= 2:
                price_change = (prices[-1] - prices[-2]) / prices[-2]
                
                if price_change > 0.001:  # Alta de mais de 0.1%
                    return {
                        'signal': 'buy',
                        'confidence': 0.15,
                        'reasons': ['forced_signal_price_momentum_up'],
                        'original_signal': 'hold'
                    }
                else:
                    return {
                        'signal': 'sell', 
                        'confidence': 0.15,
                        'reasons': ['forced_signal_price_momentum_down'],
                        'original_signal': 'hold'
                    }
            
            # Estratégia 2: Análise de volume
            volumes = market_data.get('volume', [])
            if len(volumes) >= 2:
                volume_change = (volumes[-1] - volumes[-2]) / volumes[-2] if volumes[-2] > 0 else 0
                
                if volume_change > 0.1:  # Volume subiu 10%
                    return {
                        'signal': 'buy',
                        'confidence': 0.12,
                        'reasons': ['forced_signal_volume_increase'],
                        'original_signal': 'hold'
                    }
            
            # Estratégia 3: Baseado no último dígito do preço (aleatoriedade controlada)
            if prices:
                last_price = prices[-1]
                last_digit = int(str(last_price).replace('.', '')[-1])
                
                if last_digit % 2 == 0:  # Dígito par = BUY
                    return {
                        'signal': 'buy',
                        'confidence': 0.10,
                        'reasons': ['forced_signal_price_digit_even'],
                        'original_signal': 'hold'
                    }
                else:  # Dígito ímpar = SELL
                    return {
                        'signal': 'sell',
                        'confidence': 0.10,
                        'reasons': ['forced_signal_price_digit_odd'],
                        'original_signal': 'hold'
                    }
            
            # Fallback final
            return self._emergency_signal(market_data)
            
        except Exception as e:
            logger.error(f"Erro ao forçar sinal: {e}")
            return self._emergency_signal(market_data)
    
    def _emergency_signal(self, market_data):
        """Sinal de emergência quando tudo falha"""
        return {
            'signal': 'sell',  # Default conservador
            'confidence': 0.05,
            'reasons': ['emergency_signal'],
            'original_signal': 'error'
        }

def test_no_hold_wrapper():
    """Testar o wrapper que elimina HOLD"""
    print("🧪 Testando wrapper NoHoldSignalGenerator...")
    
    # Configuração
    config = Config()
    
    # Criar wrapper
    signal_generator = NoHoldSignalGenerator(config)
    
    # Dados de teste
    test_data = {
        'symbol': 'BTCUSDT',
        'close': [50000, 50100, 50200, 50150, 50300, 50250, 50400, 50350, 50500, 50450],
        'volume': [1000, 1100, 1050, 1200, 1150, 1300, 1250, 1400, 1350, 1500],
        'high': [50100, 50200, 50300, 50250, 50400, 50350, 50500, 50450, 50600, 50550],
        'low': [49900, 50000, 50100, 50050, 50200, 50150, 50300, 50250, 50400, 50350],
        'timestamp': list(range(10))
    }
    
    signals_generated = []
    
    # Gerar 20 sinais
    for i in range(20):
        try:
            # Simular variações nos dados
            variation = (i % 5 - 2) * 50  # -100, -50, 0, 50, 100
            test_data['close'][-1] = 50450 + variation
            test_data['high'][-1] = 50550 + variation
            test_data['low'][-1] = 50350 + variation
            
            signal = signal_generator.generate_signal(test_data)
            
            if signal and 'signal' in signal:
                signal_type = signal['signal']
                confidence = signal.get('confidence', 0)
                original = signal.get('original_signal', 'normal')
                signals_generated.append(signal_type)
                
                status = "FORÇADO" if original == 'hold' else "NORMAL"
                print(f"Teste {i+1:2d}: {signal_type.upper():4s} (conf: {confidence:.3f}) [{status}]")
            else:
                print(f"Teste {i+1:2d}: ERRO - Sinal inválido")
                signals_generated.append('ERROR')
                
        except Exception as e:
            print(f"Teste {i+1:2d}: ERRO - {e}")
            signals_generated.append('ERROR')
    
    # Análise dos resultados
    print("\n" + "="*50)
    print("📊 RESULTADOS:")
    
    buy_count = signals_generated.count('buy')
    sell_count = signals_generated.count('sell')
    hold_count = signals_generated.count('hold')
    error_count = signals_generated.count('ERROR')
    
    print(f"BUY:   {buy_count:2d} ({buy_count/len(signals_generated)*100:.1f}%)")
    print(f"SELL:  {sell_count:2d} ({sell_count/len(signals_generated)*100:.1f}%)")
    print(f"HOLD:  {hold_count:2d} ({hold_count/len(signals_generated)*100:.1f}%)")
    print(f"ERRO:  {error_count:2d} ({error_count/len(signals_generated)*100:.1f}%)")
    
    # Verificar se objetivo foi alcançado
    success = hold_count == 0 and error_count == 0
    
    if success:
        print("\n✅ SUCESSO: Wrapper eliminou todos os sinais HOLD!")
        print("🎯 Sistema agora gera apenas BUY/SELL para decisões de trading!")
    else:
        if hold_count > 0:
            print(f"\n❌ FALHA: Ainda há {hold_count} sinais HOLD!")
        if error_count > 0:
            print(f"\n❌ FALHA: {error_count} erros durante geração!")
    
    return success

if __name__ == "__main__":
    test_no_hold_wrapper()
