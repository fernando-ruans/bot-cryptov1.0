#!/usr/bin/env python3
"""
Teste específico do endpoint /api/generate_signal exatamente como o botão web chama
"""

import requests
import json

def test_endpoint_exact():
    """Testa o endpoint exatamente como o botão web faz"""
    print("=== TESTE ENDPOINT EXATO ===")
    
    try:
        url = "http://localhost:5000/api/generate_signal"
        
        # Dados exatos que o frontend envia
        data = {'symbol': 'BTCUSDT'}
        
        print(f"🔗 URL: {url}")
        print(f"📦 Data: {data}")
        
        # Fazer requisição POST como o frontend
        response = requests.post(url, data=data, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        try:
            result = response.json()
            print(f"✅ JSON Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                print(f"\n🎉 SUCESSO! Sinal gerado:")
                signal = result.get('signal', {})
                print(f"   Tipo: {signal.get('signal_type')}")
                print(f"   Confiança: {signal.get('confidence')}")
                print(f"   Preço: ${signal.get('entry_price')}")
            else:
                print(f"\n❌ FALHOU: {result.get('message', 'Erro desconhecido')}")
                
        except json.JSONDecodeError:
            print(f"❌ Resposta não é JSON válido:")
            print(f"Text: {response.text}")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")

if __name__ == "__main__":
    test_endpoint_exact()
