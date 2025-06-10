#!/usr/bin/env python3
"""
Script de teste para verificar as mudanças de layout
- Verifica se o template enhanced está funcionando
- Testa a nova posição dos trades ativos
- Verifica se os dados de mercado estão sendo exibidos
"""

import requests
import time
import json

def test_dashboard_accessibility():
    """Testa se o dashboard está acessível"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard acessível")
            return True
        else:
            print(f"❌ Dashboard retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar dashboard: {e}")
        return False

def test_api_endpoints():
    """Testa os endpoints da API"""
    endpoints = [
        '/api/paper_trading/portfolio',
        '/api/paper_trading/history'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"✅ Endpoint {endpoint} funcionando")
            else:
                print(f"❌ Endpoint {endpoint} retornou status {response.status_code}")
        except Exception as e:
            print(f"❌ Erro no endpoint {endpoint}: {e}")

def test_enhanced_template():
    """Verifica se o template enhanced está sendo usado"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        content = response.text
        
        # Verificar elementos específicos do enhanced template
        checks = [
            ('Trading Bot AI - Enhanced', 'Título enhanced presente'),
            ('market-data-container', 'Container de dados de mercado presente'),
            ('activeTradesCount', 'Contador de trades ativos presente'),
            ('high24h', 'Elemento de máxima 24h presente'),
            ('low24h', 'Elemento de mínima 24h presente'),
            ('volume24h', 'Elemento de volume 24h presente')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                
    except Exception as e:
        print(f"❌ Erro ao verificar template: {e}")

def main():
    print("🧪 Testando mudanças de layout...")
    print("=" * 50)
    
    print("\n1. Testando acessibilidade do dashboard:")
    test_dashboard_accessibility()
    
    print("\n2. Testando endpoints da API:")
    test_api_endpoints()
    
    print("\n3. Verificando template enhanced:")
    test_enhanced_template()
    
    print("\n" + "=" * 50)
    print("✅ Testes de layout concluídos!")

if __name__ == "__main__":
    main()
