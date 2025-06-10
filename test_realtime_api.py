#!/usr/bin/env python3
"""
Teste da API de preços em tempo real
"""

import sys
import os
sys.path.append(os.getcwd())

import requests
import json
from src.realtime_price_api import RealTimePriceAPI

def test_direct_apis():
    """Testar APIs diretamente"""
    print("=== TESTE DIRETO DAS APIs ===")
    
    # Teste exchangerate.host
    try:
        url = 'https://api.exchangerate.host/convert?from=EUR&to=USD&amount=1'
        response = requests.get(url, timeout=3)
        data = response.json()
        print(f"exchangerate.host status: {response.status_code}")
        if data.get('success'):
            print(f"✅ EURUSD: {data.get('result', 'N/A')}")
        else:
            print("❌ exchangerate.host falhou")
            print(f"Resposta: {data}")
    except Exception as e:
        print(f"❌ Erro exchangerate.host: {e}")

    print()

    # Teste Binance crypto
    try:
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
        response = requests.get(url, timeout=3)
        data = response.json()
        print(f"Binance status: {response.status_code}")
        if 'price' in data:
            print(f"✅ BTCUSDT: ${float(data['price']):,.2f}")
        else:
            print("❌ Binance falhou")
            print(f"Resposta: {data}")
    except Exception as e:
        print(f"❌ Erro Binance: {e}")

def test_realtime_api():
    """Testar RealTimePriceAPI"""
    print("\n=== TESTE DA REALTIME API ===")
    
    try:
        api = RealTimePriceAPI()
        print("✅ RealTimePriceAPI inicializada")
        
        # Teste forex
        forex_pairs = ['EURUSD', 'GBPUSD']
        for pair in forex_pairs:
            try:
                print(f"Testando {pair}...")
                price = api._fetch_price_immediate(pair)
                if price:
                    print(f"✅ {pair}: {price:.5f}")
                else:
                    print(f"❌ {pair}: Sem preço")
            except Exception as e:
                print(f"❌ {pair}: Erro - {e}")
        
        print()
        
        # Teste crypto
        crypto_pairs = ['BTCUSDT']
        for pair in crypto_pairs:
            try:
                print(f"Testando {pair}...")
                price = api._fetch_price_immediate(pair)
                if price:
                    print(f"✅ {pair}: ${price:,.2f}")
                else:
                    print(f"❌ {pair}: Sem preço")
            except Exception as e:
                print(f"❌ {pair}: Erro - {e}")
                
    except Exception as e:
        print(f"❌ Erro ao inicializar RealTimePriceAPI: {e}")

if __name__ == "__main__":
    test_direct_apis()
    test_realtime_api()
