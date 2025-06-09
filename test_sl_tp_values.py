#!/usr/bin/env python3
"""
Teste específico para verificar se os valores de SL e TP estão corretos
"""

import requests
import json

def test_sl_tp_values():
    base_url = "http://localhost:5000"
    
    print("🧪 Testando valores de Stop Loss e Take Profit...")
    
    # 1. Gerar um sinal
    print("\n1. Gerando sinal...")
    signal_response = requests.post(f"{base_url}/api/generate_signal", 
                                   json={"symbol": "BTCUSDT", "timeframe": "5m"})
    
    if signal_response.status_code != 200:
        print(f"❌ Erro ao gerar sinal: {signal_response.status_code}")
        return
    
    signal_data = signal_response.json()
    
    if not signal_data.get('success'):
        print(f"❌ Falha na geração do sinal: {signal_data.get('error')}")
        return
    
    signal = signal_data.get('signal')
    if not signal:
        print("❌ Nenhum sinal retornado")
        return
    
    print(f"✅ Sinal gerado para timeframe 5m:")
    print(f"   - Símbolo: {signal['symbol']}")
    print(f"   - Tipo: {signal['signal_type']}")
    print(f"   - Entry Price: ${signal['entry_price']:.2f}")
    print(f"   - Stop Loss: ${signal['stop_loss']:.2f}")
    print(f"   - Take Profit: ${signal['take_profit']:.2f}")
    print(f"   - Timeframe: {signal['timeframe']}")
    
    # Calcular diferenças percentuais
    entry_price = signal['entry_price']
    stop_loss = signal['stop_loss']
    take_profit = signal['take_profit']
    
    if signal['signal_type'] == 'buy':
        sl_percent = ((entry_price - stop_loss) / entry_price) * 100
        tp_percent = ((take_profit - entry_price) / entry_price) * 100
    else:
        sl_percent = ((stop_loss - entry_price) / entry_price) * 100
        tp_percent = ((entry_price - take_profit) / entry_price) * 100
    
    print(f"   - SL Distance: {sl_percent:.3f}% (esperado ~0.03% para 5m)")
    print(f"   - TP Distance: {tp_percent:.3f}% (esperado ~0.05% para 5m)")
    
    # 2. Confirmar o sinal
    print("\n2. Confirmando sinal...")
    confirm_data = {
        "signal": signal,
        "amount": 1000
    }
    
    confirm_response = requests.post(f"{base_url}/api/paper_trading/confirm_signal", 
                                   json=confirm_data)
    
    if confirm_response.status_code != 200:
        print(f"❌ Erro ao confirmar sinal: {confirm_response.status_code}")
        print(confirm_response.text)
        return
    
    confirm_result = confirm_response.json()
    print(f"✅ Sinal confirmado: {confirm_result.get('message')}")
    trade_id = confirm_result.get('trade_id')
    
    # 3. Verificar trade ativo
    print("\n3. Verificando trade ativo...")
    portfolio_response = requests.get(f"{base_url}/api/paper_trading/portfolio")
    
    if portfolio_response.status_code == 200:
        portfolio_data = portfolio_response.json()
        active_trades = portfolio_data.get('active_trades', [])
        
        # Encontrar o trade recém criado
        trade_found = None
        for trade in active_trades:
            if trade['id'] == trade_id:
                trade_found = trade
                break
        
        if trade_found:
            print(f"✅ Trade encontrado:")
            print(f"   - ID: {trade_found['id']}")
            print(f"   - Entry Price: ${trade_found['entry_price']:.2f}")
            print(f"   - Stop Loss: ${trade_found['stop_loss']:.2f}")
            print(f"   - Take Profit: ${trade_found['take_profit']:.2f}")
            
            # Verificar se os valores estão corretos
            trade_entry = trade_found['entry_price']
            trade_sl = trade_found['stop_loss']
            trade_tp = trade_found['take_profit']
            
            print(f"\n🔍 COMPARAÇÃO DE VALORES:")
            print(f"   SINAL ORIGINAL:")
            print(f"   - Entry: ${entry_price:.2f}")
            print(f"   - SL: ${stop_loss:.2f}")
            print(f"   - TP: ${take_profit:.2f}")
            print(f"   TRADE ATIVO:")
            print(f"   - Entry: ${trade_entry:.2f}")
            print(f"   - SL: ${trade_sl:.2f}")
            print(f"   - TP: ${trade_tp:.2f}")
            
            # Verificar se são iguais
            if abs(entry_price - trade_entry) < 0.01 and abs(stop_loss - trade_sl) < 0.01 and abs(take_profit - trade_tp) < 0.01:
                print(f"✅ SUCESSO! Os valores são idênticos - problema resolvido!")
            else:
                print(f"❌ PROBLEMA! Os valores são diferentes:")
                print(f"   - Diferença Entry: ${abs(entry_price - trade_entry):.2f}")
                print(f"   - Diferença SL: ${abs(stop_loss - trade_sl):.2f}")
                print(f"   - Diferença TP: ${abs(take_profit - trade_tp):.2f}")
                
        else:
            print(f"❌ Trade não encontrado nos trades ativos")
    else:
        print(f"❌ Erro ao obter portfolio: {portfolio_response.status_code}")

if __name__ == "__main__":
    test_sl_tp_values()
