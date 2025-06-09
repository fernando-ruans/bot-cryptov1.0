#!/usr/bin/env python3
"""
Debug específico: Endpoint vs Execução Direta
Comparar exatamente o que acontece quando chamamos via endpoint vs direto
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator

def test_direct_signal():
    """Testar SignalGenerator diretamente"""
    print("=== TESTE DIRETO ===")
    
    # Inicializar exatamente como no main.py
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    print("✅ Componentes inicializados")
    
    # Verificar configurações
    print(f"📊 Min AI confidence: {config.SIGNAL_CONFIG.get('min_ai_confidence', 'N/A')}")
    print(f"📊 Min market score: {config.SIGNAL_CONFIG.get('min_market_score', 'N/A')}")
    
    # Testar geração direta
    print("🔄 Gerando sinal diretamente...")
    signal = signal_generator.generate_signal('BTCUSDT', '1h')
    
    if signal:
        print(f"✅ SUCESSO - Sinal direto:")
        print(f"   Tipo: {signal.signal_type}")
        print(f"   Confiança: {signal.confidence:.4f}")
        print(f"   Entry: ${signal.entry_price:.2f}")
        return True
    else:
        print("❌ FALHA - Nenhum sinal direto")
        return False

def test_endpoint_signal():
    """Testar via endpoint Flask"""
    print("\n=== TESTE ENDPOINT ===")
    
    try:
        url = "http://127.0.0.1:5000/api/generate_signal"
        payload = {
            "symbol": "BTCUSDT", 
            "timeframe": "1h"
        }
        
        print(f"🌐 Fazendo requisição para: {url}")
        print(f"📝 Payload: {payload}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Resposta: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                signal = data.get('signal', {})
                print(f"✅ SUCESSO - Sinal endpoint:")
                print(f"   Tipo: {signal.get('signal_type')}")
                print(f"   Confiança: {signal.get('confidence')}")
                print(f"   Entry: ${signal.get('entry_price', 0):.2f}")
                return True
            else:
                print(f"❌ FALHA - Endpoint: {data.get('message')}")
                return False
        else:
            print(f"❌ ERRO HTTP - Status: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO - Servidor não está rodando")
        return False
    except Exception as e:
        print(f"❌ ERRO - Exceção: {e}")
        return False

def main():
    print("🔍 DEBUG: ENDPOINT vs DIRETO")
    print("=" * 50)
    
    # Teste 1: Execução direta
    direct_success = test_direct_signal()
    
    # Teste 2: Via endpoint
    endpoint_success = test_endpoint_signal()
    
    # Comparação
    print("\n" + "=" * 50)
    print("📊 RESUMO DA COMPARAÇÃO:")
    print(f"   Direto: {'✅ Funcionou' if direct_success else '❌ Falhou'}")
    print(f"   Endpoint: {'✅ Funcionou' if endpoint_success else '❌ Falhou'}")
    
    if direct_success and not endpoint_success:
        print("\n🚨 PROBLEMA IDENTIFICADO:")
        print("   - SignalGenerator funciona diretamente")
        print("   - Endpoint Flask NÃO funciona")
        print("   - Suspeita: Problema na integração Flask ou contexto diferente")
        
    elif not direct_success and not endpoint_success:
        print("\n⚠️ PROBLEMA GERAL:")
        print("   - Ambos falharam - problema na lógica do SignalGenerator")
        
    elif direct_success and endpoint_success:
        print("\n🎉 TUDO FUNCIONANDO:")
        print("   - Ambos funcionaram corretamente")
        
    else:
        print("\n🤔 RESULTADO INESPERADO:")
        print("   - Endpoint funcionou mas direto falhou")

if __name__ == "__main__":
    main()
