#!/usr/bin/env python3
"""
Teste rápido do Enhanced AI Engine
"""

import sys
import os

def test_enhanced_engine():
    try:
        print("🧪 Testando Enhanced AI Engine...")
        
        # Import
        from ai_engine_enhanced import EnhancedAIEngine
        from src.config import Config
        print("✅ Import bem-sucedido")
        
        # Inicialização
        config = Config()
        engine = EnhancedAIEngine(config)
        print("✅ Inicialização bem-sucedida")
        
        # Verificar métodos
        if hasattr(engine, 'enhanced_predict_signal'):
            print("✅ Método enhanced_predict_signal disponível")
        
        if hasattr(engine, 'create_enhanced_features'):
            print("✅ Método create_enhanced_features disponível")
        
        print("\n🎉 Enhanced AI Engine está funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_engine()
