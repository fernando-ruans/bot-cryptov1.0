#!/usr/bin/env python3
"""
Teste direto das APIs de sinal para resolver problemas
"""

import requests
import json
import sys
import os

def test_api_endpoints():
    """Testar todos os endpoints relacionados a sinais"""
    base_url = "http://localhost:5000"
    
    print("=== TESTE COMPLETO DAS APIS DE SINAL ===")
    
    # 1. Testar status do sistema
    print("\n1. Testando status do sistema:")
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"   Status: {response.status_code}")
        print(f"   Dados: {response.json()}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 2. Testar preços
    print("\n2. Testando preços:")
    try:
        response = requests.get(f"{base_url}/api/price/BTCUSDT")
        print(f"   Preço Status: {response.status_code}")
        print(f"   Preço Dados: {response.json()}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 3. Testar sinais ativos (antes de gerar)
    print("\n3. Testando sinais ativos (inicial):")
    try:
        response = requests.get(f"{base_url}/api/signals/active")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Sinais ativos: {data.get('count', 0)}")
        if data.get('signals'):
            for signal in data['signals']:
                print(f"   - {signal['symbol']} {signal['signal_type']} ({signal['confidence']:.1%})")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 4. Tentar gerar sinal
    print("\n4. Tentando gerar sinal:")
    try:
        payload = {"symbol": "BTCUSDT", "timeframe": "1h"}
        response = requests.post(f"{base_url}/api/generate_signal", 
                               json=payload, 
                               headers={'Content-Type': 'application/json'})
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {data}")
        
        if data.get('success') and data.get('signal'):
            signal = data['signal']
            print(f"   SINAL GERADO:")
            print(f"   - Tipo: {signal['signal_type']}")
            print(f"   - Confiança: {signal['confidence']:.1%}")
            print(f"   - Preço: ${signal['entry_price']}")
            print(f"   - Stop Loss: ${signal['stop_loss']}")
            print(f"   - Take Profit: ${signal['take_profit']}")
        else:
            print(f"   SINAL NÃO GERADO: {data.get('message', 'Sem detalhes')}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 5. Testar sinais ativos (depois de gerar)
    print("\n5. Testando sinais ativos (após tentativa):")
    try:
        response = requests.get(f"{base_url}/api/signals/active")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Sinais ativos: {data.get('count', 0)}")
        if data.get('signals'):
            for signal in data['signals']:
                print(f"   - {signal['symbol']} {signal['signal_type']} ({signal['confidence']:.1%})")
        else:
            print("   Nenhum sinal ativo encontrado")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 6. Testar portfolio
    print("\n6. Testando portfolio:")
    try:
        response = requests.get(f"{base_url}/api/paper_trading/portfolio")
        data = response.json()
        print(f"   Status: {response.status_code}")
        if data.get('success'):
            portfolio = data.get('portfolio', {})
            print(f"   Total trades: {portfolio.get('total_trades', 0)}")
            print(f"   Win rate: {portfolio.get('win_rate', 0):.1f}%")
            print(f"   Trades ativos: {len(data.get('active_trades', []))}")
        else:
            print(f"   Erro no portfolio: {data}")
    except Exception as e:
        print(f"   Erro: {e}")

def force_signal_via_api():
    """Forçar geração de sinal usando método direto"""
    print("\n=== FORÇANDO SINAL VIA SCRIPT DIRETO ===")
    
    try:
        # Importar e executar força bruta
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from force_signal import create_test_signal
        
        print("Executando criação de sinal forçado...")
        signal = create_test_signal()
        print(f"Sinal criado: {signal.id}")
        
        # Testar novamente a API
        base_url = "http://localhost:5000"
        response = requests.get(f"{base_url}/api/signals/active")
        data = response.json()
        print(f"Sinais ativos após forçar: {data.get('count', 0)}")
        
    except Exception as e:
        print(f"Erro ao forçar sinal: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    force_signal_via_api()
