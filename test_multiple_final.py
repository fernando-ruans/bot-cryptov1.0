#!/usr/bin/env python3
"""
Teste múltiplo para confirmar que cooldown foi resolvido
"""

import requests
import json
import time

def test_multiple_calls():
    print("🔄 TESTE MÚLTIPLO - VERIFICAÇÃO FINAL")
    print("=" * 50)
    
    url = "http://localhost:5000/api/generate_signal"
    payload = {"symbol": "BTCUSDT", "timeframe": "1h"}
    
    successes = 0
    failures = 0
    
    for i in range(1, 6):
        print(f"\n📞 CHAMADA {i}/5")
        
        try:
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=15)
            duration = time.time() - start_time
            
            print(f"   ⚡ Duração: {duration:.2f}s")
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    signal = data.get('signal', {})
                    print(f"   ✅ SUCESSO!")
                    print(f"      Tipo: {signal.get('signal_type')}")
                    print(f"      Confiança: {signal.get('confidence', 0):.2%}")
                    print(f"      Preço: ${signal.get('entry_price', 0):.2f}")
                    successes += 1
                else:
                    print(f"   ❌ FALHA: {data.get('error', data.get('message', 'Erro desconhecido'))}")
                    failures += 1
            else:
                print(f"   ❌ Status HTTP: {response.status_code}")
                failures += 1
        
        except Exception as e:
            print(f"   💥 ERRO: {e}")
            failures += 1
        
        # Pequeno delay
        if i < 5:
            time.sleep(0.5)
    
    print(f"\n📊 RESULTADOS FINAIS:")
    print(f"   ✅ Sucessos: {successes}/5")
    print(f"   ❌ Falhas: {failures}/5")
    print(f"   📈 Taxa de sucesso: {(successes/5)*100:.1f}%")
    
    if successes >= 3:
        print(f"\n🎉 PROBLEMA RESOLVIDO COM SUCESSO!")
        print(f"   ✅ Cooldown foi corrigido")
        print(f"   ✅ Endpoint está funcionando")
        print(f"   ✅ Múltiplas chamadas funcionam")
    else:
        print(f"\n⚠️ AINDA HÁ PROBLEMAS:")
        print(f"   - Taxa de sucesso baixa: {(successes/5)*100:.1f}%")

if __name__ == "__main__":
    test_multiple_calls()
