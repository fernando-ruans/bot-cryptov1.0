#!/usr/bin/env python3
"""
Teste simples da API forex
"""

import requests
import sys
import os
sys.path.append(os.getcwd())

from src.realtime_price_api import RealTimePriceAPI

def test_forex_direct():
    """Testar APIs forex diretamente"""
    print("=== TESTE APIs FOREX DIRETO ===")
    
    # Teste exchangerate-api.com
    try:
        url = 'https://api.exchangerate-api.com/v4/latest/EUR'
        response = requests.get(url, timeout=5)
        data = response.json()
        print(f"exchangerate-api.com: {response.status_code}")
        
        if 'rates' in data and 'USD' in data['rates']:
            print(f"✅ EURUSD: {data['rates']['USD']}")
        else:
            print(f"❌ Falha: {data}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_realtime_forex():
    """Testar RealTimePriceAPI com forex"""
    print("\n=== TESTE REALTIME FOREX ===")
    
    try:
        api = RealTimePriceAPI()
        print("✅ API inicializada")
        
        # Teste EURUSD
        price = api._fetch_price_immediate('EURUSD')
        if price:
            print(f"✅ EURUSD: {price:.5f}")
        else:
            print("❌ EURUSD: Falhou")
            
        # Teste BTCUSDT
        price_btc = api._fetch_price_immediate('BTCUSDT')
        if price_btc:
            print(f"✅ BTCUSDT: ${price_btc:,.2f}")
        else:
            print("❌ BTCUSDT: Falhou")
            
    except Exception as e:
        print(f"❌ Erro API: {e}")

if __name__ == "__main__":
    test_forex_direct()
    test_realtime_forex()
