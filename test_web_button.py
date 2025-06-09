#!/usr/bin/env python3
"""
Teste específico do botão web "Gerar Sinal"
"""

import requests
import json

def test_web_button():
    """Simular clique no botão web"""
    
    print("=== TESTE DO BOTÃO WEB 'GERAR SINAL' ===")
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. Verificar se servidor está funcionando
        print("1. Verificando servidor...")
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            print("   ✅ Servidor funcionando")
        else:
            print(f"   ❌ Servidor não está funcionando: {response.status_code}")
            return
        
        # 2. Obter preço atual
        print("2. Obtendo preço atual...")
        response = requests.get(f"{base_url}/api/price/BTCUSDT", timeout=10)
        if response.status_code == 200:
            price_data = response.json()
            print(f"   ✅ Preço BTCUSDT: ${price_data['price']:,.2f}")
        else:
            print(f"   ❌ Erro ao obter preço: {response.status_code}")
        
        # 3. Testar geração de sinal (simulando clique no botão)
        print("3. Clicando no botão 'Gerar Sinal'...")
        
        # Esta é a mesma chamada que o botão web faz
        response = requests.post(
            f"{base_url}/api/generate_signal",
            headers={"Content-Type": "application/json"},
            json={"symbol": "BTCUSDT"},
            timeout=30
        )
        
        print(f"   Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Resposta do servidor:")
            print(f"      Success: {result.get('success', False)}")
            print(f"      Message: {result.get('message', 'N/A')}")
            
            if result.get('signal'):
                signal = result['signal']
                print("   🎯 SINAL GERADO COM SUCESSO!")
                print(f"      Tipo: {signal.get('signal_type', 'N/A')}")
                print(f"      Confiança: {signal.get('confidence', 0):.1f}%")
                print(f"      Entry: ${signal.get('entry_price', 0):.2f}")
                print(f"      Stop Loss: ${signal.get('stop_loss', 0):.2f}")
                print(f"      Take Profit: ${signal.get('take_profit', 0):.2f}")
                print(f"      Razões: {len(signal.get('reasons', []))} fatores")
                
                return "SUCCESS"
            else:
                print("   ⚠️  Nenhum sinal foi gerado")
                return "NO_SIGNAL"
        else:
            print(f"   ❌ Erro HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"      Erro: {error_data}")
            except:
                print(f"      Resposta: {response.text}")
            return "ERROR"
    
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erro de conexão: {e}")
        return "CONNECTION_ERROR"
    
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return "UNEXPECTED_ERROR"

if __name__ == "__main__":
    result = test_web_button()
    print(f"\n🎯 RESULTADO FINAL: {result}")
    
    if result == "SUCCESS":
        print("✅ BOTÃO WEB FUNCIONANDO PERFEITAMENTE!")
    elif result == "NO_SIGNAL":
        print("⚠️  Botão funciona, mas não gerou sinal (pode ser normal)")
    else:
        print("❌ BOTÃO WEB NÃO ESTÁ FUNCIONANDO")
