#!/usr/bin/env python3
"""
Teste específico para verificar sincronização de preços EURUSD
"""

import requests
import time
import json

def test_price_consistency():
    """Testar se o preço EURUSD está sendo consistentemente atualizado"""
    
    print("🧪 TESTE DE SINCRONIZAÇÃO DE PREÇOS FOREX")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    symbol = "EURUSD"
    
    # Fazer 10 requisições consecutivas
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/api/price/realtime/{symbol}")
            data = response.json()
            
            if data.get('success'):
                price = data.get('price')
                source = data.get('source')
                age = data.get('age_seconds', 0)
                timestamp = data.get('timestamp', '')
                
                print(f"  #{i+1:2d} | Preço: {price} | Fonte: {source} | Idade: {age:.2f}s | {timestamp[:19]}")
                
                # Verificar se o preço está mudando ou se há variações
                if i == 0:
                    first_price = price
                elif price != first_price:
                    print(f"      ⚠️  VARIAÇÃO DETECTADA: {first_price} -> {price}")
                    
            else:
                print(f"  #{i+1:2d} | ❌ ERRO: {data}")
                
        except Exception as e:
            print(f"  #{i+1:2d} | 🚨 EXCEÇÃO: {e}")
            
        time.sleep(1)
    
    print("\n📊 ANÁLISE:")
    print("✅ Se todas as respostas têm SUCCESS=true, a API está funcionando")
    print("✅ Se há pequenas variações no TIMESTAMP, a API está atualizando")
    print("✅ Se há ALGUMA variação no PREÇO, o valor não está fixo")
    print("⚠️  Se PREÇO=1.14211 sempre, pode ser mercado estável OU cache")
    
    print(f"\n🔗 Frontend: {base_url}")
    print("💡 Abra o navegador e verifique se 'sidebarCurrentPrice' atualiza!")

if __name__ == "__main__":
    test_price_consistency()
