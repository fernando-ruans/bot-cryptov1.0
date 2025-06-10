#!/usr/bin/env python3
"""
Script para debugar especificamente o problema de quantidade = 0
"""

import requests
import json
import time
import sys

def test_quantity_calculation():
    print("🔧 DEBUG - PROBLEMA DE QUANTIDADE = 0")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Sinal de teste com valores claros
    signal = {
        "symbol": "BTCUSDT",
        "signal_type": "buy",
        "entry_price": 100000,  # Preço redondo para facilitar cálculo
        "stop_loss": 95000,
        "take_profit": 105000,
        "confidence": 0.75,
        "timeframe": "1h"
    }
    
    amount = 1000  # $1000
    expected_quantity = amount / signal["entry_price"]  # 1000 / 100000 = 0.01
    
    print(f"📊 Dados do teste:")
    print(f"   Amount: ${amount}")
    print(f"   Entry Price: ${signal['entry_price']}")
    print(f"   Quantidade esperada: {expected_quantity}")
    print()
    
    # Confirmar trade
    try:
        print("🎯 Enviando requisição...")
        r = requests.post(f"{base_url}/api/paper_trading/confirm_signal",
                         json={"signal": signal, "amount": amount},
                         headers={"Content-Type": "application/json"},
                         timeout=15)
        
        print(f"📡 Status da resposta: {r.status_code}")
        
        if r.status_code == 200:
            confirm_data = r.json()
            print(f"📦 Resposta: {json.dumps(confirm_data, indent=2)}")
            
            if confirm_data.get("success"):
                trade_id = confirm_data.get("trade_id")
                print(f"✅ Trade criado: {trade_id}")
                
                # Aguardar um momento e verificar trade
                time.sleep(2)
                  # Buscar trade via portfolio
                portfolio_r = requests.get(f"{base_url}/api/paper_trading/portfolio")
                if portfolio_r.status_code == 200:
                    portfolio_data = portfolio_r.json()
                    print(f"\n📊 Trades ativos: {len(portfolio_data.get('active_trades', []))}")
                    
                    for trade in portfolio_data.get('active_trades', []):
                        if trade['id'] == trade_id:
                            print(f"🔍 Trade encontrado:")
                            print(f"   ID: {trade['id']}")
                            print(f"   Symbol: {trade['symbol']}")
                            print(f"   Entry Price: ${trade['entry_price']}")
                            print(f"   Quantity: {trade['quantity']}")
                            print(f"   Current Price: ${trade.get('current_price', 'N/A')}")
                            print(f"   Unrealized P&L: ${trade.get('unrealized_pnl', 'N/A')}")
                            
                            # Verificar se quantidade está correta
                            if trade['quantity'] == 0:
                                print("❌ PROBLEMA CONFIRMADO: Quantidade = 0!")
                                print(f"   Deveria ser: {expected_quantity}")
                            elif abs(trade['quantity'] - expected_quantity) < 0.000001:
                                print("✅ Quantidade calculada corretamente!")
                            else:
                                print(f"⚠️ Quantidade incorreta: {trade['quantity']} (esperado: {expected_quantity})")
                            
                            break
                    else:
                        print("❌ Trade não encontrado na lista de trades ativos")
                else:
                    print(f"❌ Erro ao buscar portfolio: {portfolio_r.status_code}")
                
                # Limpeza
                close_r = requests.post(f"{base_url}/api/paper_trading/close_trade",
                                      json={"trade_id": trade_id})
                if close_r.status_code == 200:
                    print("🧹 Trade fechado para limpeza")
                    
            else:
                print(f"❌ Erro na confirmação: {confirm_data.get('error')}")
        else:
            print(f"❌ Erro HTTP: {r.status_code}")
            print(f"   Resposta: {r.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_quantity_calculation()
