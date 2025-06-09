#!/usr/bin/env python3
"""
Debug detalhado do endpoint generate_signal
"""

import requests
import json
import sys
import os

# Adicionar o src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar módulos diretamente
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Carregar módulos
signal_gen_module = load_module("signal_generator", "src/signal_generator.py")
ai_engine_module = load_module("ai_engine", "src/ai_engine.py")

print("=== DEBUG DETALHADO DO ENDPOINT GENERATE_SIGNAL ===")

# 1. Testar endpoint diretamente
print("\n1. Testando endpoint via HTTP...")
try:
    response = requests.post("http://localhost:5000/api/generate_signal")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. Testar SignalGenerator diretamente
print("\n2. Testando SignalGenerator diretamente...")
try:
    SignalGenerator = signal_gen_module.SignalGenerator
    signal_gen = SignalGenerator()
    signal = signal_gen.generate_signal("BTCUSDT")
    print(f"   ✅ Sinal gerado: {signal}")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# 3. Testar AI Engine diretamente  
print("\n3. Testando AI Engine diretamente...")
try:
    AIEngine = ai_engine_module.AIEngine
    ai_engine = AIEngine()
    
    # Obter dados fictícios para teste
    import pandas as pd
    import numpy as np
    
    # Criar DataFrame de teste
    df_test = pd.DataFrame({
        'close': np.random.rand(100) * 100000,
        'volume': np.random.rand(100) * 1000000,
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='1H')
    })
    
    prediction = ai_engine.predict_signal(df_test, "BTCUSDT")
    print(f"   ✅ Predição AI: {prediction}")
    
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIM DO DEBUG ===")
