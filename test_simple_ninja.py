#!/usr/bin/env python3
"""
Teste simples do CryptoNinja 🥷
"""

import requests

try:
    print("🥷 Testando CryptoNinja...")
    
    # Teste básico de acesso
    response = requests.get('http://localhost:5000', timeout=5)
    
    if response.status_code == 200:
        print("✅ Dashboard acessível")
        
        if "CryptoNinja 🥷" in response.text:
            print("✅ Nome CryptoNinja encontrado!")
        else:
            print("❌ Nome CryptoNinja não encontrado")
            
        if "Stealth Trading AI" in response.text:
            print("✅ Subtítulo encontrado!")
        else:
            print("⚠️ Subtítulo não encontrado")
            
        # Verificar elementos chave
        elements = [
            'activeTradesCount',
            'high24h', 
            'low24h',
            'volume24h'
        ]
        
        for element in elements:
            if element in response.text:
                print(f"✅ {element} presente")
            else:
                print(f"❌ {element} ausente")
                
        print("🎉 CryptoNinja está funcionando!")
        
    else:
        print(f"❌ Erro: Status {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
