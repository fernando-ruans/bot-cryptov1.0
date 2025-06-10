#!/usr/bin/env python3
"""
Script para testar criação e verificação imediata de trade
"""

import requests
import json
import time

def test_immediate_trade():
    print("🔧 TESTE RÁPIDO - TRADE IMEDIATO")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # Sinal com preços distantes para não fechar imediatamente
    signal = {
        "symbol": "BTCUSDT",
        "signal_type": "buy",
        "entry_price": 100000,
        "stop_loss": 50000,    # SL muito distante
        "take_profit": 150000, # TP muito distante
        "confidence": 0.75,
        "timeframe": "1h"
    }
    
    amount = 1000
    
    print(f"📊 Criando trade com SL/TP muito distantes...")
    print(f"   Entry: ${signal['entry_price']}")
    print(f"   SL: ${signal['stop_loss']} (distância: {((signal['entry_price'] - signal['stop_loss']) / signal['entry_price'] * 100):.1f}%)")
    print(f"   TP: ${signal['take_profit']} (distância: {((signal['take_profit'] - signal['entry_price']) / signal['entry_price'] * 100):.1f}%)")
    
    # Criar trade
    try:
        print("\n🎯 Criando trade...")
        r = requests.post(f"{base_url}/api/paper_trading/confirm_signal",
                         json={"signal": signal, "amount": amount},
                         headers={"Content-Type": "application/json"},
                         timeout=10)
        
        if r.status_code == 200:
            confirm_data = r.json()
            print(f"✅ Trade criado: {confirm_data}")
            
            if confirm_data.get("success"):
                # Verificar imediatamente
                print("\n📊 Verificando imediatamente...")
                portfolio_r = requests.get(f"{base_url}/api/paper_trading/portfolio", timeout=5)
                
                if portfolio_r.status_code == 200:
                    portfolio_data = portfolio_r.json()
                    trades = portfolio_data.get('active_trades', [])
                    
                    print(f"   Trades ativos encontrados: {len(trades)}")
                    
                    if trades:
                        trade = trades[0]
                        print(f"   📋 Campos disponíveis: {list(trade.keys())}")
                        print(f"   🔍 Trade data:")
                        for key, value in trade.items():
                            print(f"      {key}: {value}")
                            
                        # Verificar se quantity está presente
                        if 'quantity' in trade:
                            print(f"\n✅ QUANTITY ENCONTRADO: {trade['quantity']}")
                            if trade['quantity'] == 0:
                                print("❌ MAS QUANTIDADE = 0!")
                            else:
                                print("✅ Quantidade está correta!")
                        else:
                            print("\n❌ QUANTITY NÃO ENCONTRADO!")
                    else:
                        print("❌ Nenhum trade ativo encontrado")
                else:
                    print(f"❌ Erro ao buscar portfolio: {portfolio_r.status_code}")
        else:
            print(f"❌ Erro ao criar trade: {r.status_code}")
            print(f"   Resposta: {r.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_immediate_trade()
