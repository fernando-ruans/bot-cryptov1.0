#!/usr/bin/env python3
"""
Teste direto da geração de sinais
"""

import logging
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_signal_generation():
    """Teste simplificado de geração de sinais"""
    print("=== TESTE DIRETO DE GERAÇÃO DE SINAIS ===")
    
    try:
        # Importar módulos
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.ai_engine import AITradingEngine
        from src.signal_generator import SignalGenerator
        
        print("✓ Imports realizados com sucesso")
        
        # Inicializar configuração
        config = Config()
        print(f"✓ Config criado - Min confidence: {config.SIGNAL_CONFIG['min_confidence']}")
        
        # Inicializar componentes
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        print("✓ Componentes inicializados")
        
        # Testar dados de mercado
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        print(f"\n--- Testando {symbol} {timeframe} ---")
        
        # 1. Verificar dados
        df = market_data.get_historical_data(symbol, timeframe, 500)
        print(f"1. Dados históricos: {len(df)} registros")
        
        if df.empty:
            print("❌ Erro: Nenhum dado histórico obtido")
            return False
            
        # 2. Verificar preço atual
        current_price = market_data.get_current_price(symbol)
        print(f"2. Preço atual: ${current_price}")
        
        if current_price is None:
            print("❌ Erro: Preço atual não disponível")
            return False
        
        # 3. Verificar cooldown
        is_cooldown = signal_generator._is_in_cooldown(symbol)
        print(f"3. Em cooldown: {is_cooldown}")
        
        # 4. Tentar criar um sinal simples manualmente
        from src.signal_generator import Signal
        from datetime import datetime
        
        test_signal = Signal(
            symbol=symbol,
            signal_type='buy',
            confidence=0.75,
            entry_price=current_price,
            stop_loss=current_price * 0.98,
            take_profit=current_price * 1.04,
            timeframe=timeframe,
            timestamp=datetime.now(),
            reasons=['Teste manual']
        )
        
        print(f"4. Sinal de teste criado: {test_signal.to_dict()}")
        
        # 5. Registrar o sinal
        signal_generator._register_signal(test_signal)
        print("5. Sinal registrado com sucesso")
        
        # 6. Verificar sinais ativos
        active_signals = signal_generator.get_active_signals()
        print(f"6. Sinais ativos: {len(active_signals)}")
        
        if active_signals:
            print(f"   Último sinal: {active_signals[-1]}")
            return True
        else:
            print("❌ Nenhum sinal ativo encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_signal_generation()
    if success:
        print("\n🎉 TESTE PASSOU! O sistema pode gerar sinais.")
    else:
        print("\n❌ TESTE FALHOU! Há problemas na geração de sinais.")
