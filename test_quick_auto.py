#!/usr/bin/env python3
"""
Teste Rápido de Trade Automático
"""

import requests
import time

def test_auto_trade():
    print("=== TESTE DE TRADE AUTOMÁTICO ===")
    base_url = "http://localhost:5000"
    
    # 1. Gerar sinal
    print("1. Gerando sinal...")
    try:
        r = requests.post(f"{base_url}/api/generate_signal",
                         json={"symbol": "BTCUSDT", "timeframe": "1m"},
                         headers={"Content-Type": "application/json"},
                         timeout=30)
        
        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                signal = data["signal"]
                print(f"   ✅ Sinal: {signal['signal_type']} @ ${signal['entry_price']:.2f}")
                print(f"   📊 SL: ${signal['stop_loss']:.2f}")
                print(f"   📊 TP: ${signal['take_profit']:.2f}")
                
                # Calcular distâncias
                entry = signal["entry_price"]
                sl_dist = abs(signal["stop_loss"] - entry) / entry * 100
                tp_dist = abs(signal["take_profit"] - entry) / entry * 100
                print(f"   📏 SL distância: {sl_dist:.3f}%")
                print(f"   📏 TP distância: {tp_dist:.3f}%")
            else:
                print(f"   ❌ Erro no sinal: {data.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {r.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    # 2. Confirmar trade
    print("\n2. Confirmando trade...")
    try:
        r = requests.post(f"{base_url}/api/paper_trading/confirm_signal",
                         json={"signal": signal, "amount": 1000},
                         headers={"Content-Type": "application/json"},
                         timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                trade_id = data.get("trade_id")
                print(f"   ✅ Trade criado: {trade_id}")
            else:
                print(f"   ❌ Erro na confirmação: {data.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {r.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    # 3. Monitorar
    print(f"\n3. 👀 Monitorando trade {trade_id} por 45 segundos...")
    start_time = time.time()
    
    for i in range(9):  # 9 checks de 5 segundos
        elapsed = time.time() - start_time
        
        try:
            r = requests.get(f"{base_url}/api/paper_trading/portfolio", timeout=5)
            if r.status_code == 200:
                data = r.json()
                active_trades = data.get("active_trades", [])
                
                # Verificar se nosso trade ainda está ativo
                trade_active = any(t["id"] == trade_id for t in active_trades)
                
                if not trade_active:
                    print(f"\n   🎉 TRADE FINALIZADO AUTOMATICAMENTE!")
                    print(f"   ⏱️ Tempo até finalização: {elapsed:.1f} segundos")
                    
                    # Verificar histórico
                    try:
                        r = requests.get(f"{base_url}/api/paper_trading/history", timeout=5)
                        if r.status_code == 200:
                            history_data = r.json()
                            if history_data.get("success"):
                                trades = history_data.get("trades", [])
                                for trade in trades:
                                    if trade.get("id") == trade_id:
                                        print(f"   📊 Motivo: {trade.get('exit_reason', 'N/A')}")
                                        print(f"   💰 P&L: ${trade.get('realized_pnl', 0):.2f}")
                                        print(f"   📈 Preço saída: ${trade.get('exit_price', 0):.2f}")
                                        break
                    except:
                        pass
                    
                    return True
                else:
                    # Trade ainda ativo - mostrar status
                    current_trade = next((t for t in active_trades if t["id"] == trade_id), None)
                    if current_trade:
                        current_price = current_trade.get("current_price", 0)
                        unrealized_pnl = current_trade.get("unrealized_pnl", 0)
                        print(f"   ⏱️ {elapsed:.0f}s - Preço: ${current_price:.2f} | P&L: ${unrealized_pnl:.2f}")
        except Exception as e:
            print(f"   ⚠️ Erro ao verificar portfolio: {e}")
        
        time.sleep(5)
    
    # Trade não foi finalizado automaticamente
    print(f"\n   ⚠️ Trade não finalizado automaticamente em 45 segundos")
    
    # Tentar fechar manualmente
    print("   🔒 Fechando manualmente para limpeza...")
    try:
        r = requests.post(f"{base_url}/api/paper_trading/close_trade",
                         json={"trade_id": trade_id},
                         headers={"Content-Type": "application/json"})
        if r.status_code == 200:
            print("   ✅ Trade fechado manualmente")
        else:
            print(f"   ❌ Erro ao fechar: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao fechar: {e}")
    
    return False

if __name__ == "__main__":
    success = test_auto_trade()
    
    print("\n" + "="*50)
    if success:
        print("🎉 FINALIZAÇÃO AUTOMÁTICA FUNCIONANDO!")
    else:
        print("❌ PROBLEMA: Finalização automática não está funcionando")
        print("💡 Possíveis causas:")
        print("   - Alvos muito distantes do preço atual")
        print("   - Monitor não está atualizando preços")
        print("   - Erro na lógica de SL/TP")
