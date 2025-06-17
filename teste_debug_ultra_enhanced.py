#!/usr/bin/env python3
"""
🔧 TESTE SIMPLES - Debug da UltraEnhancedAIEngine
================================================

Teste focado para identificar onde exatamente a engine está falhando.
"""

import sys
import os
import pandas as pd
import numpy as np
import time

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_engine_ultra_enhanced import UltraEnhancedAIEngine

def gerar_dados_completos(periods=200):
    """Gerar dados mais completos para teste"""
    np.random.seed(42)
    
    data = []
    base_price = 50000
    
    for i in range(periods):
        change = np.random.normal(0, 0.02)
        base_price *= (1 + change)
        
        # Gerar OHLC realista
        spread = base_price * 0.005
        high = base_price + abs(np.random.normal(0, spread))
        low = base_price - abs(np.random.normal(0, spread))
        open_price = base_price + np.random.normal(0, spread/2)
        
        volume = 1000 * np.random.uniform(0.5, 2.0)
        
        data.append({
            'timestamp': int(time.time() * 1000) - (periods - i) * 60000,
            'open': open_price,
            'high': high,
            'low': low, 
            'close': base_price,
            'volume': volume
        })
    
    return pd.DataFrame(data)

def teste_debug():
    """Teste de debug detalhado"""
    print("🔧 TESTE DEBUG - UltraEnhancedAIEngine")
    print("=" * 50)
    
    # Configuração
    config = {
        'ai_engine': {
            'confidence_threshold': 0.65,
            'max_signals_per_hour': 12
        }
    }
    
    try:
        # 1. Inicializar engine
        print("\n1️⃣ Inicializando engine...")
        engine = UltraEnhancedAIEngine(config)
        print("✅ Engine inicializada")
        
        # 2. Gerar dados
        print("\n2️⃣ Gerando dados de teste...")
        df = gerar_dados_completos(200)
        print(f"✅ Dados gerados: {len(df)} períodos")
        print(f"   Colunas: {list(df.columns)}")
        
        # 3. Testar criação de features
        print("\n3️⃣ Testando criação de features...")
        try:
            df_features = engine.create_ultra_features(df.copy())
            print(f"✅ Features criadas: {len(df_features.columns)} colunas")
            print(f"   Primeiras 10 colunas: {list(df_features.columns[:10])}")
            
            # Verificar se future_direction existe
            if 'future_direction' in df_features.columns:
                print("✅ future_direction criado")
                print(f"   Valores únicos: {df_features['future_direction'].dropna().unique()}")
            else:
                print("❌ future_direction NÃO criado")
                
            # Verificar atr_percent
            if 'atr_percent' in df_features.columns:
                print("✅ atr_percent criado")
            else:
                print("❌ atr_percent NÃO criado")
                
        except Exception as e:
            print(f"❌ Erro na criação de features: {e}")
            return
        
        # 4. Testar treinamento
        print("\n4️⃣ Testando treinamento...")
        try:
            training_result = engine.train_ultra_model(df_features, 'BTCUSDT')
            print(f"✅ Treinamento: {training_result}")
            
            if training_result.get('success'):
                print("✅ Modelo treinado com sucesso")
            else:
                print(f"❌ Falha no treinamento: {training_result.get('reason', 'Desconhecido')}")
                
        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")
        
        # 5. Testar predição direta
        print("\n5️⃣ Testando predição...")
        try:
            resultado = engine.ultra_predict_signal(df, 'BTCUSDT')
            print(f"✅ Resultado da predição:")
            
            for key, value in resultado.items():
                if isinstance(value, (list, dict)):
                    print(f"   {key}: {type(value)} (tamanho: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                else:
                    print(f"   {key}: {value}")
                    
        except Exception as e:
            print(f"❌ Erro na predição: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_debug()
