#!/usr/bin/env python3
"""
Teste específico para verificar se o problema de cooldown foi resolvido
Testa múltiplas chamadas consecutivas ao endpoint de geração de sinais
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cooldown_fix():
    """Testa se o cooldown foi resolvido fazendo múltiplas chamadas"""
    print("🔧 TESTE DE RESOLUÇÃO DO COOLDOWN")
    print("=" * 50)
    
    # URL do endpoint
    url = "http://localhost:5000/api/generate_signal"
    
    # Dados da requisição
    payload = {
        "symbol": "BTCUSDT",
        "timeframe": "1h"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🎯 Testando endpoint: {url}")
    print(f"📊 Dados: {payload}")
    print()
    
    # Fazer 5 chamadas consecutivas
    for i in range(1, 6):
        print(f"📞 CHAMADA {i}/5")
        print(f"   ⏰ Hora: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        
        start_time = time.time()
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   ⚡ Duração: {duration:.3f}s")
            print(f"   📈 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    signal = data.get('signal', {})
                    print(f"   ✅ SUCESSO!")
                    print(f"      Tipo: {signal.get('signal_type', 'N/A')}")
                    print(f"      Confiança: {signal.get('confidence', 0):.2%}")
                    print(f"      Preço: ${signal.get('entry_price', 0):.2f}")
                else:
                    print(f"   ❌ FALHA: {data.get('error', 'Erro desconhecido')}")
                    error_type = data.get('error_type', 'unknown')
                    print(f"      Tipo: {error_type}")
                    
                    if error_type == 'cooldown':
                        print(f"      🚨 PROBLEMA DE COOLDOWN AINDA EXISTE!")
                        return False
            
            elif response.status_code == 429:
                print(f"   🚨 COOLDOWN ATIVO! Status 429")
                return False
            
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                print(f"      Resposta: {response.text[:200]}")
        
        except requests.exceptions.RequestException as e:
            print(f"   💥 ERRO DE CONEXÃO: {e}")
            return False
        
        except Exception as e:
            print(f"   💥 ERRO GERAL: {e}")
            return False
        
        print()
        
        # Pequeno delay entre chamadas para simular uso real
        if i < 5:
            time.sleep(0.5)
    
    print("🎉 TESTE CONCLUÍDO!")
    print("✅ Problema de cooldown parece estar resolvido!")
    return True

def test_direct_vs_endpoint_comparison():
    """Comparar execução direta vs endpoint após fix"""
    print("\n🔄 TESTE COMPARATIVO PÓS-FIX")
    print("=" * 40)
    
    try:
        # Teste direto
        print("1️⃣ Testando execução DIRETA...")
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.ai_engine import AITradingEngine
        from src.signal_generator import SignalGenerator
        
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        start_time = time.time()
        signal_direct = signal_generator.generate_signal('BTCUSDT', '1h')
        direct_duration = time.time() - start_time
        
        if signal_direct:
            print(f"   ✅ Direto: {signal_direct.signal_type} ({signal_direct.confidence:.2%}) em {direct_duration:.2f}s")
        else:
            print(f"   ❌ Direto: Nenhum sinal em {direct_duration:.2f}s")
        
        # Teste endpoint
        print("2️⃣ Testando via ENDPOINT...")
        payload = {"symbol": "BTCUSDT", "timeframe": "1h"}
        
        start_time = time.time()
        response = requests.post("http://localhost:5000/api/generate_signal", 
                               json=payload, timeout=30)
        endpoint_duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                signal = data.get('signal', {})
                print(f"   ✅ Endpoint: {signal.get('signal_type')} ({signal.get('confidence', 0):.2%}) em {endpoint_duration:.2f}s")
            else:
                print(f"   ❌ Endpoint: {data.get('error')} em {endpoint_duration:.2f}s")
        else:
            print(f"   ❌ Endpoint: Status {response.status_code} em {endpoint_duration:.2f}s")
        
        print(f"\n📊 COMPARAÇÃO:")
        print(f"   Direto: {direct_duration:.3f}s")
        print(f"   Endpoint: {endpoint_duration:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"💥 Erro no teste comparativo: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE CORREÇÃO DO COOLDOWN")
    print("=" * 60)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print("✅ Servidor Flask está rodando")
    except:
        print("❌ ERRO: Servidor Flask não está rodando!")
        print("   Execute: python main.py")
        sys.exit(1)
    
    print()
    
    # Teste principal de cooldown
    success = test_cooldown_fix()
    
    if success:
        # Teste comparativo
        test_direct_vs_endpoint_comparison()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        print("✅ O problema de cooldown foi resolvido com sucesso!")
    else:
        print("\n❌ PROBLEMA AINDA EXISTE!")
        print("   O sistema de cooldown ainda está bloqueando chamadas.")
    
    print("\n" + "=" * 60)
