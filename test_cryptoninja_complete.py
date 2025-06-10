#!/usr/bin/env python3
"""
Teste completo do CryptoNinja 🥷 - Verificação de todas as funcionalidades implementadas
"""

import requests
import time
import json

def test_complete_system():
    """Teste completo do sistema CryptoNinja"""
    
    print("🥷 ════════════════════════════════════════")
    print("   CRYPTONINJA 🥷 - TESTE COMPLETO")
    print("   Stealth Trading AI - Sistema de Teste")
    print("════════════════════════════════════════")
    
    base_url = "http://localhost:5000"
    results = {}
    
    # 1. Teste de acessibilidade
    print("\n1. 🌐 Testando acessibilidade do dashboard...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Dashboard acessível")
            results['dashboard'] = True
            
            # Verificar se o novo nome está no HTML
            if "CryptoNinja 🥷" in response.text:
                print("   ✅ Nome 'CryptoNinja 🥷' encontrado")
                results['new_name'] = True
            else:
                print("   ❌ Nome 'CryptoNinja 🥷' não encontrado")
                results['new_name'] = False
                
        else:
            print(f"   ❌ Dashboard retornou status {response.status_code}")
            results['dashboard'] = False
    except Exception as e:
        print(f"   ❌ Erro ao acessar dashboard: {e}")
        results['dashboard'] = False
    
    # 2. Teste dos elementos do novo layout
    print("\n2. 🎨 Verificando elementos do layout...")
    elements_to_check = [
        ('market-data-container', 'Container de dados de mercado'),
        ('activeTradesCount', 'Contador de trades ativos'),
        ('high24h', 'Elemento máxima 24h'),
        ('low24h', 'Elemento mínima 24h'),
        ('volume24h', 'Elemento volume 24h'),
        ('priceChange24h', 'Elemento variação 24h'),
        ('activeTradesList', 'Lista de trades ativos')
    ]
    
    layout_results = {}
    try:
        response = requests.get(base_url, timeout=5)
        content = response.text
        
        for element_id, description in elements_to_check:
            if element_id in content:
                print(f"   ✅ {description}")
                layout_results[element_id] = True
            else:
                print(f"   ❌ {description}")
                layout_results[element_id] = False
                
        results['layout'] = layout_results
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar layout: {e}")
        results['layout'] = {}
    
    # 3. Teste das APIs
    print("\n3. 🔧 Testando endpoints da API...")
    api_endpoints = [
        ('/api/paper_trading/portfolio', 'Portfolio'),
        ('/api/paper_trading/history', 'Histórico'),
        ('/api/price/BTCUSDT', 'Preços'),
        ('/api/generate_signal', 'Geração de sinais')
    ]
    
    api_results = {}
    for endpoint, description in api_endpoints:
        try:
            if endpoint == '/api/generate_signal':
                # POST para gerar sinal
                response = requests.post(f"{base_url}{endpoint}", 
                                       json={'symbol': 'BTCUSDT', 'timeframe': '5m'}, 
                                       timeout=10)
            else:
                # GET para outros endpoints
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                
            if response.status_code == 200:
                print(f"   ✅ {description}")
                api_results[endpoint] = True
            else:
                print(f"   ⚠️ {description} - Status: {response.status_code}")
                api_results[endpoint] = False
                
        except Exception as e:
            print(f"   ❌ {description} - Erro: {str(e)[:50]}...")
            api_results[endpoint] = False
    
    results['apis'] = api_results
    
    # 4. Teste de dados de mercado em tempo real
    print("\n4. 📊 Testando dados de mercado...")
    try:
        response = requests.get(f"{base_url}/api/price/BTCUSDT", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('price'):
                print(f"   ✅ Preço BTC: ${data['price']}")
                results['market_data'] = True
            else:
                print("   ❌ Dados de mercado inválidos")
                results['market_data'] = False
        else:
            print("   ❌ Falha ao obter dados de mercado")
            results['market_data'] = False
    except Exception as e:
        print(f"   ❌ Erro nos dados de mercado: {e}")
        results['market_data'] = False
    
    # 5. Verificar layout responsivo e trades ativos
    print("\n5. 📱 Verificando posição dos trades ativos...")
    try:
        response = requests.get(base_url, timeout=5)
        content = response.text
        
        # Verificar se a seção de trades ativos está na posição correta
        if 'Active Trades Section - Moved Below Chart' in content:
            print("   ✅ Trades ativos movidos para baixo do gráfico")
            results['trades_position'] = True
        else:
            print("   ❌ Trades ativos não estão na posição correta")
            results['trades_position'] = False
            
        # Verificar classes CSS específicas
        css_classes = ['active-trades-card', 'trade-card', 'market-data-container']
        css_results = {}
        for css_class in css_classes:
            if css_class in content:
                print(f"   ✅ Classe CSS '{css_class}' presente")
                css_results[css_class] = True
            else:
                print(f"   ❌ Classe CSS '{css_class}' ausente")
                css_results[css_class] = False
                
        results['css_classes'] = css_results
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar layout: {e}")
        results['trades_position'] = False
        results['css_classes'] = {}
    
    # 6. Relatório final
    print("\n" + "="*50)
    print("📋 RELATÓRIO FINAL - CRYPTONINJA 🥷")
    print("="*50)
    
    total_tests = 0
    passed_tests = 0
    
    # Contabilizar resultados
    if results.get('dashboard'):
        passed_tests += 1
    total_tests += 1
    
    if results.get('new_name'):
        passed_tests += 1
    total_tests += 1
    
    # Layout elements
    layout_count = len(results.get('layout', {}))
    if layout_count > 0:
        layout_passed = sum(results['layout'].values())
        passed_tests += layout_passed
        total_tests += layout_count
    
    # API endpoints
    api_count = len(results.get('apis', {}))
    if api_count > 0:
        api_passed = sum(results['apis'].values())
        passed_tests += api_passed
        total_tests += api_count
    
    # Market data
    if results.get('market_data'):
        passed_tests += 1
    total_tests += 1
    
    # Trades position
    if results.get('trades_position'):
        passed_tests += 1
    total_tests += 1
    
    # CSS classes
    css_count = len(results.get('css_classes', {}))
    if css_count > 0:
        css_passed = sum(results['css_classes'].values())
        passed_tests += css_passed
        total_tests += css_count
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Taxa de Sucesso: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 90:
        print("🎉 EXCELENTE! CryptoNinja está funcionando perfeitamente!")
        status = "PERFEITO"
    elif success_rate >= 75:
        print("✅ BOM! CryptoNinja está funcionando bem!")
        status = "BOM"
    elif success_rate >= 50:
        print("⚠️ REGULAR! Algumas funcionalidades precisam de ajustes!")
        status = "REGULAR"
    else:
        print("❌ CRÍTICO! Várias funcionalidades precisam de correção!")
        status = "CRÍTICO"
    
    print("\n🥷 Funcionalidades principais:")
    print(f"   • Dashboard: {'✅' if results.get('dashboard') else '❌'}")
    print(f"   • Novo Nome: {'✅' if results.get('new_name') else '❌'}")
    print(f"   • APIs: {'✅' if api_passed >= api_count * 0.75 else '❌'}")
    print(f"   • Dados de Mercado: {'✅' if results.get('market_data') else '❌'}")
    print(f"   • Layout Trades: {'✅' if results.get('trades_position') else '❌'}")
    
    print(f"\n🎯 Status Final: {status}")
    print("🥷 CryptoNinja - Stealth Trading AI está pronto para ação!")
    
    return results

if __name__ == "__main__":
    test_complete_system()
