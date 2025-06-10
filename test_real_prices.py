#!/usr/bin/env python3
"""
Teste para verificar se os preços são reais vs mockados
"""

import sys
import os
sys.path.append(os.getcwd())

import requests
import json
from datetime import datetime
from src.realtime_price_api import RealTimePriceAPI

def test_real_vs_cached():
    print("=== TESTE: DADOS REAIS VS CACHE ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. Verificar API externa diretamente
    print("1. TESTANDO API EXTERNA DIRETA:")
    try:
        response = requests.get('https://open.er-api.com/v6/latest/USD', timeout=10)
        data = response.json()
        if 'rates' in data and 'JPY' in data['rates']:
            external_usd_jpy = data['rates']['JPY']
            print(f"   ✅ USD/JPY (API Externa): {external_usd_jpy}")
        else:
            print(f"   ❌ API Externa falhou: {data}")
            external_usd_jpy = None
    except Exception as e:
        print(f"   ❌ Erro API Externa: {e}")
        external_usd_jpy = None

    print()

    # 2. Testar nossa API - primeira chamada (pode usar cache)
    print("2. NOSSA API - PRIMEIRA CHAMADA (cache):")
    try:
        response = requests.get('http://localhost:5000/api/price/realtime/USDJPY', timeout=10)
        data = response.json()
        if data['success']:
            our_price_1 = data['price']
            age_1 = data['age_seconds']
            source_1 = data['source']
            print(f"   ✅ USDJPY: {our_price_1} (idade: {age_1:.1f}s, fonte: {source_1})")
        else:
            print(f"   ❌ Nossa API falhou: {data}")
            our_price_1 = None
    except Exception as e:
        print(f"   ❌ Erro nossa API: {e}")
        our_price_1 = None

    print()

    # 3. Forçar limpeza de cache e nova busca
    print("3. LIMPANDO CACHE E FORÇANDO NOVA BUSCA:")
    try:
        api = RealTimePriceAPI()
        # Limpar cache
        if 'USDJPY' in api.price_cache:
            del api.price_cache['USDJPY']
            print("   ✅ Cache limpo para USDJPY")
        
        # Buscar imediatamente
        fresh_price = api._fetch_price_immediate('USDJPY')
        if fresh_price:
            print(f"   ✅ USDJPY (fresh): {fresh_price}")
        else:
            print("   ❌ Falha ao buscar preço fresh")
            
    except Exception as e:
        print(f"   ❌ Erro ao limpar cache: {e}")
        fresh_price = None

    print()

    # 4. Comparação final
    print("4. COMPARAÇÃO FINAL:")
    if external_usd_jpy and our_price_1:
        diff = abs(external_usd_jpy - our_price_1)
        diff_percent = (diff / external_usd_jpy) * 100
        print(f"   API Externa: {external_usd_jpy}")
        print(f"   Nossa API:   {our_price_1}")
        print(f"   Diferença:   {diff:.6f} ({diff_percent:.3f}%)")
        
        if diff_percent < 0.1:  # Menos de 0.1% de diferença
            print("   ✅ PREÇOS COMPATÍVEIS - Dados parecem reais")
        else:
            print("   ⚠️  DIFERENÇA SIGNIFICATIVA - Investigar")
    else:
        print("   ❌ Não foi possível comparar")

if __name__ == "__main__":
    test_real_vs_cached()
