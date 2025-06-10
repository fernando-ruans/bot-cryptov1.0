#!/usr/bin/env python3
"""
Script para debug direto do objeto trade
"""

import requests
import json

def debug_trade_object():
    print("🔧 DEBUG DIRETO DO OBJETO TRADE")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # Criar um trade
    signal = {
        "symbol": "BTCUSDT",
        "signal_type": "buy",
        "entry_price": 100000,
        "stop_loss": 50000,
        "take_profit": 150000,
        "confidence": 0.75,
        "timeframe": "1h"
    }
    
    print("🎯 Criando trade...")
    r = requests.post(f"{base_url}/api/paper_trading/confirm_signal",
                     json={"signal": signal, "amount": 1000})
    
    if r.status_code == 200:
        confirm_data = r.json()
        trade_id = confirm_data.get("trade_id")
        print(f"✅ Trade criado: {trade_id}")
        
        # Verificar o log do servidor para ver se quantity foi calculado
        print("\n📋 Verificando logs do servidor...")
        print("💡 Verifique o terminal do servidor para ver se há logs sobre quantidade calculada")
        
        # Testar endpoint específico se existir
        print("\n🔍 Tentando acessar dados do trade via diferentes rotas...")
        
        # Portfolio
        portfolio_r = requests.get(f"{base_url}/api/paper_trading/portfolio")
        if portfolio_r.status_code == 200:
            portfolio_data = portfolio_r.json()
            trades = portfolio_data.get('active_trades', [])
            print(f"📊 Portfolio endpoint - {len(trades)} trades encontrados")
            if trades:
                trade = trades[0]
                print(f"   Keys: {list(trade.keys())}")
                print(f"   Has quantity: {'quantity' in trade}")
                
        # Histórico
        history_r = requests.get(f"{base_url}/api/paper_trading/history")
        if history_r.status_code == 200:
            history_data = history_r.json()
            trades = history_data.get('trades', [])
            print(f"📚 History endpoint - {len(trades)} trades encontrados")
            if trades:
                trade = trades[0]
                print(f"   Keys: {list(trade.keys())}")
                print(f"   Has quantity: {'quantity' in trade}")
        
        # Limpeza
        print(f"\n🧹 Fechando trade {trade_id} para limpeza...")
        close_r = requests.post(f"{base_url}/api/paper_trading/close_trade",
                              json={"trade_id": trade_id})
        if close_r.status_code == 200:
            print("✅ Trade fechado")
        
    else:
        print(f"❌ Erro ao criar trade: {r.status_code}")

if __name__ == "__main__":
    debug_trade_object()
