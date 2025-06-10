#!/usr/bin/env python3
"""
Teste rápido de bias após correção do modo de teste da IA
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_quick_bias():
    """Teste rápido para verificar se o bias foi corrigido"""
    print("=== TESTE RÁPIDO DE BIAS PÓS-CORREÇÃO ===")
    
    try:
        # Primeiro, vou restaurar manualmente a função predict_signal 
        # removendo apenas o modo de teste
        
        from src.config import Config
        from src.market_data import MarketDataManager
        
        config = Config()
        market_data = MarketDataManager(config)
        
        print("✅ Config e MarketData carregados")
        
        # Vou simular o que a IA deveria retornar (sem modo de teste)
        # Em vez de sempre retornar BUY, ela deveria analisar os dados
        
        # Para testar se o problema foi a IA em modo de teste,
        # vou verificar se ao menos conseguimos importar
        print("🧪 Tentando importar AITradingEngine...")
        
        try:
            from src.ai_engine import AITradingEngine
            print("❌ Ainda há problema de sintaxe no ai_engine.py")
            return False
        except IndentationError as e:
            print(f"❌ Erro de indentação: {e}")
            print("🔧 Vou criar uma versão corrigida...")
            return "NEEDS_FIX"
        except Exception as e:
            print(f"❌ Outro erro: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    result = test_quick_bias()
    
    if result == "NEEDS_FIX":
        print("\n🛠️  AÇÃO NECESSÁRIA:")
        print("   1. O arquivo ai_engine.py precisa ser corrigido")
        print("   2. O problema identificado foi: IA em modo de teste")
        print("   3. Solução: Remover o código de teste forçado")
        print("\n🎯 PROGRESSO:")
        print("   ✅ Fonte do bias identificada (IA forçando BUY)")
        print("   🔧 Correção em andamento...")
    elif result:
        print("\n✅ PROBLEMA RESOLVIDO!")
    else:
        print("\n❌ AINDA HÁ PROBLEMAS")
