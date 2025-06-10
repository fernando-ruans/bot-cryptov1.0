#!/usr/bin/env python3
"""
Debug específico do problema de P&L não atualizando
"""

import requests
import time

def debug_pnl_update():
    print("🔧 DEBUG - PROBLEMA DE P&L NÃO ATUALIZANDO")
    print("="*60)
    
    base_url = "http://localhost:5000"
    
    # 1. Verificar se a API de preços em tempo real está funcionando
    print("\n1. 🔍 Testando API de preços em tempo real...")
    try:
        # Tentar obter preço atual via endpoint direto (se existir)
        r = requests.get(f"{base_url}/api/realtime/price/BTCUSDT", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"   ✅ Preço em tempo real: ${data.get('price', 'N/A')}")
        else:
            print(f"   ⚠️ Endpoint direto não disponível: {r.status_code}")
    except:
        print("   ⚠️ Erro ao acessar API de preços direta")
    
    # 2. Criar trade e verificar se P&L é calculado
    print("\n2. 🎯 Criando trade de teste...")
    
    # Gerar sinal
    try:
        r = requests.post(f"{base_url}/api/generate_signal",
                         json={"symbol": "BTCUSDT", "timeframe": "1m"},
                         headers={"Content-Type": "application/json"},
                         timeout=30)
        
        if r.status_code == 200:
            signal_data = r.json()
            if signal_data.get("success"):
                signal = signal_data["signal"]
                print(f"   ✅ Sinal: {signal['signal_type']} @ ${signal['entry_price']:.2f}")
            else:
                print(f"   ❌ Erro no sinal: {signal_data.get('error')}")
                return
        else:
            print(f"   ❌ Erro HTTP: {r.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # Confirmar trade
    try:
        r = requests.post(f"{base_url}/api/paper_trading/confirm_signal",
                         json={"signal": signal, "amount": 1000},
                         headers={"Content-Type": "application/json"},
                         timeout=15)
        
        if r.status_code == 200:
            confirm_data = r.json()
            if confirm_data.get("success"):
                trade_id = confirm_data.get("trade_id")
                print(f"   ✅ Trade criado: {trade_id}")
            else:
                print(f"   ❌ Erro na confirmação: {confirm_data.get('error')}")
                return
        else:
            print(f"   ❌ Erro HTTP: {r.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # 3. Verificar estado inicial do trade
    print(f"\n3. 📊 Estado inicial do trade...")
    try:
        r = requests.get(f"{base_url}/api/paper_trading/portfolio", timeout=5)
        if r.status_code == 200:
            data = r.json()
            active_trades = data.get("active_trades", [])
            
            our_trade = None
            for trade in active_trades:
                if trade["id"] == trade_id:
                    our_trade = trade
                    break
            
            if our_trade:
                print(f"   📊 Entry Price: ${our_trade.get('entry_price', 0):.2f}")
                print(f"   📊 Current Price: ${our_trade.get('current_price', 0):.2f}")
                print(f"   📊 Quantity: {our_trade.get('quantity', 0):.6f}")
                print(f"   📊 Unrealized P&L: ${our_trade.get('unrealized_pnl', 0):.2f}")
                print(f"   📊 Stop Loss: ${our_trade.get('stop_loss', 0):.2f}")
                print(f"   📊 Take Profit: ${our_trade.get('take_profit', 0):.2f}")
            else:
                print("   ❌ Trade não encontrado!")
                return
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # 4. Forçar atualização manual de preços
    print(f"\n4. 🔄 Forçando atualização manual de preços...")
    try:
        r = requests.post(f"{base_url}/api/paper_trading/update_prices",
                         headers={"Content-Type": "application/json"},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"   ✅ Atualização forçada: {data.get('success', False)}")
            if "message" in data:
                print(f"   📝 Mensagem: {data['message']}")
        else:
            print(f"   ❌ Endpoint não disponível: {r.status_code}")
            print("   💡 Vou tentar aguardar ciclo natural do monitor...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        print("   💡 Vou aguardar ciclo natural do monitor...")
    
    # 5. Aguardar e verificar se P&L foi atualizado
    print(f"\n5. ⏱️ Aguardando 40 segundos (1+ ciclo do monitor)...")
    time.sleep(40)
    
    print(f"\n6. 📊 Verificando se P&L foi atualizado...")
    try:
        r = requests.get(f"{base_url}/api/paper_trading/portfolio", timeout=5)
        if r.status_code == 200:
            data = r.json()
            active_trades = data.get("active_trades", [])
            
            our_trade = None
            for trade in active_trades:
                if trade["id"] == trade_id:
                    our_trade = trade
                    break
            
            if our_trade:
                entry_price = our_trade.get('entry_price', 0)
                current_price = our_trade.get('current_price', 0)
                unrealized_pnl = our_trade.get('unrealized_pnl', 0)
                
                print(f"   📊 Entry Price: ${entry_price:.2f}")
                print(f"   📊 Current Price: ${current_price:.2f}")
                print(f"   📊 Unrealized P&L: ${unrealized_pnl:.2f}")
                
                # Verificar se houve mudança
                price_changed = abs(current_price - entry_price) > 0.01
                pnl_calculated = abs(unrealized_pnl) > 0.01
                
                if price_changed:
                    print(f"   ✅ Preço foi atualizado!")
                else:
                    print(f"   ❌ Preço não mudou!")
                
                if pnl_calculated:
                    print(f"   ✅ P&L foi calculado!")
                else:
                    print(f"   ❌ P&L não foi calculado!")
                
                if not price_changed and not pnl_calculated:
                    print(f"\n   🚨 PROBLEMA IDENTIFICADO:")
                    print(f"   - O sistema de atualização de preços não está funcionando")
                    print(f"   - Monitor automático pode não estar chamando update_prices()")
                    print(f"   - API de tempo real pode não estar retornando preços")
                
            else:
                print("   ℹ️ Trade foi finalizado automaticamente!")
                return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Limpeza
    print(f"\n7. 🧹 Limpeza...")
    try:
        r = requests.post(f"{base_url}/api/paper_trading/close_trade",
                         json={"trade_id": trade_id},
                         headers={"Content-Type": "application/json"})
        if r.status_code == 200:
            print("   ✅ Trade fechado para limpeza")
    except:
        pass

if __name__ == "__main__":
    debug_pnl_update()
