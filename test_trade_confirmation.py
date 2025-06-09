#!/usr/bin/env python3
"""
Teste para verificar confirmação de trades e exibição de trades ativos
"""

import requests
import json
import time

def test_trade_confirmation():
    base_url = "http://localhost:5000"
    
    print("🧪 Testando confirmação de trade e trades ativos...")
    
    # 1. Gerar um sinal primeiro
    print("\n1. Gerando sinal...")
    signal_response = requests.post(f"{base_url}/api/generate_signal", 
                                   json={"symbol": "BTCUSDT", "timeframe": "1h"})
    
    if signal_response.status_code != 200:
        print(f"❌ Erro ao gerar sinal: {signal_response.status_code}")
        return
    
    signal_data = signal_response.json()
    print(f"✅ Sinal gerado: {json.dumps(signal_data, indent=2)}")
    
    if not signal_data.get('success'):
        print(f"❌ Falha na geração do sinal: {signal_data.get('error')}")
        return
    
    signal = signal_data.get('signal')
    if not signal:
        print("❌ Nenhum sinal retornado")
        return
    
    # 2. Verificar trades ativos antes da confirmação
    print("\n2. Verificando trades ativos antes da confirmação...")
    portfolio_response = requests.get(f"{base_url}/api/paper_trading/portfolio")
    
    if portfolio_response.status_code == 200:
        portfolio_data = portfolio_response.json()
        active_trades_before = portfolio_data.get('active_trades', [])
        print(f"📊 Trades ativos antes: {len(active_trades_before)}")
        for trade in active_trades_before:
            print(f"   - {trade['symbol']} {trade['trade_type']} @ ${trade['entry_price']:.2f}")
    else:
        print(f"❌ Erro ao obter portfolio: {portfolio_response.status_code}")
    
    # 3. Confirmar o sinal
    print("\n3. Confirmando sinal...")
    confirm_data = {
        "signal": signal,
        "amount": 1000
    }
    
    confirm_response = requests.post(f"{base_url}/api/paper_trading/confirm_signal",
                                   json=confirm_data)
    
    print(f"Status da confirmação: {confirm_response.status_code}")
    
    if confirm_response.status_code == 200:
        confirm_result = confirm_response.json()
        print(f"✅ Resposta da confirmação: {json.dumps(confirm_result, indent=2)}")
        
        if confirm_result.get('success'):
            trade_id = confirm_result.get('trade_id')
            print(f"📈 Trade criado com ID: {trade_id}")
        else:
            print(f"❌ Erro na confirmação: {confirm_result.get('error')}")
            return
    else:
        print(f"❌ Erro HTTP na confirmação: {confirm_response.status_code}")
        print(f"Resposta: {confirm_response.text}")
        return
    
    # 4. Aguardar um pouco e verificar trades ativos novamente
    print("\n4. Aguardando 2 segundos e verificando trades ativos...")
    time.sleep(2)
    
    portfolio_response = requests.get(f"{base_url}/api/paper_trading/portfolio")
    
    if portfolio_response.status_code == 200:
        portfolio_data = portfolio_response.json()
        active_trades_after = portfolio_data.get('active_trades', [])
        print(f"📊 Trades ativos depois: {len(active_trades_after)}")
        
        if active_trades_after:
            print("✅ Trades ativos encontrados:")
            for trade in active_trades_after:
                print(f"   - ID: {trade['id']}")
                print(f"   - {trade['symbol']} {trade['trade_type']} @ ${trade['entry_price']:.2f}")
                print(f"   - Status: {trade['status']}")
                print(f"   - P&L: ${trade['pnl']:.2f} ({trade['pnl_percent']:.2f}%)")
                print(f"   - Timestamp: {trade['timestamp']}")
                print()
        else:
            print("❌ Nenhum trade ativo encontrado após confirmação!")
            
        # Mostrar estatísticas do portfolio
        portfolio_stats = portfolio_data.get('portfolio', {})
        print(f"📈 Estatísticas do Portfolio:")
        print(f"   - Total de trades: {portfolio_stats.get('total_trades', 0)}")
        print(f"   - Trades ativos: {portfolio_stats.get('active_trades', 0)}")
        print(f"   - Win rate: {portfolio_stats.get('win_rate', 0):.1f}%")
        print(f"   - P&L total: ${portfolio_stats.get('total_pnl', 0):.2f}")
        
    else:
        print(f"❌ Erro ao obter portfolio após confirmação: {portfolio_response.status_code}")
        print(f"Resposta: {portfolio_response.text}")

if __name__ == "__main__":
    try:
        test_trade_confirmation()
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor. Certifique-se de que está rodando em localhost:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")