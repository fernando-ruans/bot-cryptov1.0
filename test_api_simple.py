#!/usr/bin/env python3
"""
Teste simples da API web
"""
import requests
import json

def test_api():
    print("🌐 TESTE DA API WEB")
    print("=" * 40)
    
    try:
        # Testar se o servidor está respondendo
        print("🔧 Verificando servidor...")
        response = requests.get('http://127.0.0.1:5000', timeout=5)
        print(f"✅ Servidor respondeu: {response.status_code}")
        
        # Testar geração de sinal via API
        print("\n🎯 Testando geração de sinal...")
        signal_data = {
            'symbol': 'BTCUSDT',
            'confidence': 5  # 5% de confiança mínima        }
        
        signal_response = requests.post(
            'http://127.0.0.1:5000/api/generate_signal',
            json=signal_data,
            timeout=15
        )
        
        print(f"Status da resposta: {signal_response.status_code}")
        
        if signal_response.status_code == 200:
            result = signal_response.json()
            print("✅ SINAL GERADO VIA API!")
            print(f"Resposta: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Erro na API: {signal_response.status_code}")
            print(f"Resposta: {signal_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print("Certifique-se de que o servidor está rodando em http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_api()
