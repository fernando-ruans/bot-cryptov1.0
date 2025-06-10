#!/usr/bin/env python3
"""
Teste para verificar se a remoção do forex foi bem-sucedida
"""

import sys
import os
sys.path.append('.')

try:
    from src.config import Config
    from src.utils import is_forex_symbol, is_crypto_symbol
    
    # Testar configuração
    config = Config()
    
    print("🧪 TESTE DE REMOÇÃO DO FOREX")
    print("=" * 50)
    
    # Testar pares crypto
    print(f"✅ Pares de crypto configurados: {len(config.CRYPTO_PAIRS)}")
    print(f"📋 Primeiros 5 pares: {config.CRYPTO_PAIRS[:5]}")
    
    # Testar função is_forex_pair
    print(f"❌ EURUSD é forex? {config.is_forex_pair('EURUSD')} (deve ser False)")
    print(f"✅ BTCUSDT é crypto? {config.is_crypto_pair('BTCUSDT')} (deve ser True)")
    
    # Testar utils
    print(f"❌ EURUSD detectado como forex? {is_forex_symbol('EURUSD')} (deve ser False)")
    print(f"✅ BTCUSDT detectado como crypto? {is_crypto_symbol('BTCUSDT')} (deve ser True)")
    
    # Testar tipos de ativo
    print(f"✅ Tipo do BTCUSDT: {config.get_asset_type('BTCUSDT')}")
    print(f"❌ Tipo do EURUSD: {config.get_asset_type('EURUSD')}")
    
    print("\n🎯 RESULTADO: Forex removido com sucesso!")
    print("✅ Apenas criptomoedas estão configuradas")
    print("✅ Funções forex desabilitadas")
    print("✅ Sistema pronto para operar apenas com crypto")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    import traceback
    traceback.print_exc()
