#!/usr/bin/env python3
"""
Debug detalhado do endpoint - Adicionar logs específicos para identificar onde o problema ocorre
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
import requests
import json
import time

# Configurar logging muito detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_endpoint_with_detailed_analysis():
    """Testar endpoint e analisar resposta detalhada"""
    print("🔍 DEBUG DETALHADO DO ENDPOINT")
    print("=" * 60)
    
    # Testar se servidor está rodando
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        print(f"✅ Servidor está rodando (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Servidor não está acessível: {e}")
        return
    
    # Testar endpoint de geração de sinal
    url = "http://127.0.0.1:5000/api/generate_signal"
    payload = {"symbol": "BTCUSDT", "timeframe": "1h"}
    
    print(f"\n🌐 Testando: {url}")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Fazer requisição com headers explícitos
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Debug-Script/1.0'
        }
        
        print(f"📤 Headers da requisição: {json.dumps(headers, indent=2)}")
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers,
            timeout=60  # Timeout maior para debug
        )
        
        print(f"\n📥 RESPOSTA RECEBIDA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   JSON Response: {json.dumps(data, indent=4)}")
                
                # Analisar resposta em detalhes
                if data.get('success'):
                    print("\n✅ ENDPOINT FUNCIONOU!")
                    signal = data.get('signal', {})
                    for key, value in signal.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"\n❌ ENDPOINT RETORNOU FALHA:")
                    print(f"   Mensagem: {data.get('message', 'N/A')}")
                    print(f"   Tipo de erro: {data.get('error_type', 'N/A')}")
                    
                    # Verificar se é erro conhecido
                    message = data.get('message', '').lower()
                    if 'cooldown' in message:
                        print("   🔍 Possível causa: COOLDOWN ativo")
                    elif 'confiança' in message or 'confidence' in message:
                        print("   🔍 Possível causa: Confiança insuficiente")
                    elif 'dados' in message or 'data' in message:
                        print("   🔍 Possível causa: Problema nos dados")
                    else:
                        print("   🔍 Causa: Desconhecida - investigar logs do servidor")
                        
            except json.JSONDecodeError as e:
                print(f"   ❌ Erro ao decodificar JSON: {e}")
                print(f"   Raw Response: {response.text}")
        else:
            print(f"\n❌ ERRO HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - Requisição demorou mais de 60s")
    except requests.exceptions.ConnectionError:
        print(f"❌ ERRO DE CONEXÃO - Servidor pode ter caído")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()

def test_multiple_attempts():
    """Testar múltiplas vezes para verificar consistência"""
    print(f"\n🔄 TESTANDO MÚLTIPLAS VEZES")
    print("-" * 40)
    
    for i in range(3):
        print(f"\n📊 Tentativa {i+1}/3:")
        test_endpoint_with_detailed_analysis()
        
        if i < 2:  # Não aguardar na última iteração
            print("   ⏳ Aguardando 5s...")
            time.sleep(5)

def main():
    test_endpoint_with_detailed_analysis()
    test_multiple_attempts()

if __name__ == "__main__":
    main()
