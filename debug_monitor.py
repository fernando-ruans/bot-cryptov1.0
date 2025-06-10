#!/usr/bin/env python3
"""
Debug do Monitor Automático
Teste direto dos componentes para identificar o problema
"""

import sys
import os
import time
import requests

def debug_monitor_directly():
    """Debug direto do monitor via APIs"""
    print("🔧 DEBUG DO MONITOR AUTOMÁTICO")
    print("="*50)
    
    base_url = "http://localhost:5000"
    
    print("\n1. 📊 Status inicial do monitor...")
    try:
        r = requests.get(f"{base_url}/api/monitor/status", timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Resposta: {data}")
        else:
            print(f"Erro: {r.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n2. 🚀 Tentando iniciar monitor...")
    try:
        r = requests.post(f"{base_url}/api/monitor/start", 
                         headers={'Content-Type': 'application/json'}, 
                         timeout=15)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Resposta: {data}")
        else:
            print(f"Erro: {r.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n3. ⏱️ Aguardando 3 segundos...")
    time.sleep(3)
    
    print("\n4. 📊 Status após inicialização...")
    try:
        r = requests.get(f"{base_url}/api/monitor/status", timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Resposta: {data}")
            return data.get('running', False)
        else:
            print(f"Erro: {r.text}")
            return False
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_quick_trade_cycle():
    """Teste rápido de ciclo de trade para ver se é finalizado"""
    print("\n🔄 TESTE RÁPIDO DE CICLO DE TRADE")
    print("="*50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. Gerar sinal
        print("\n1. 🎯 Gerando sinal...")
        signal_r = requests.post(f"{base_url}/api/generate_signal",
                                json={"symbol": "BTCUSDT", "timeframe": "1m"},  # timeframe curto para alvos próximos
                                headers={'Content-Type': 'application/json'},
                                timeout=30)
        
        if signal_r.status_code != 200:
            print(f"❌ Erro ao gerar sinal: {signal_r.status_code}")
            return False
            
        signal_data = signal_r.json()
        if not signal_data.get('success'):
            print(f"❌ Erro no sinal: {signal_data.get('error')}")
            return False
            
        signal = signal_data['signal']
        print(f"✅ Sinal: {signal['signal_type']} @ ${signal['entry_price']:.2f}")
        print(f"   SL: ${signal['stop_loss']:.2f}")
        print(f"   TP: ${signal['take_profit']:.2f}")
        
        # Calcular distâncias percentuais
        entry = signal['entry_price']
        sl_dist = abs(signal['stop_loss'] - entry) / entry * 100
        tp_dist = abs(signal['take_profit'] - entry) / entry * 100
        print(f"   Distância SL: {sl_dist:.3f}%")
        print(f"   Distância TP: {tp_dist:.3f}%")
        
        # 2. Confirmar trade
        print("\n2. ✅ Confirmando trade...")
        confirm_r = requests.post(f"{base_url}/api/paper_trading/confirm_signal",
                                 json={"signal": signal, "amount": 1000},
                                 headers={'Content-Type': 'application/json'},
                                 timeout=15)
        
        if confirm_r.status_code != 200:
            print(f"❌ Erro ao confirmar: {confirm_r.status_code}")
            return False
            
        confirm_data = confirm_r.json()
        if not confirm_data.get('success'):
            print(f"❌ Erro na confirmação: {confirm_data.get('error')}")
            return False
            
        trade_id = confirm_data.get('trade_id')
        print(f"✅ Trade criado: {trade_id}")
        
        # 3. Monitorar por 60 segundos
        print(f"\n3. 👀 Monitorando por 60 segundos...")
        start_time = time.time()
        
        for i in range(12):  # 12 checks de 5 segundos cada
            elapsed = time.time() - start_time
            
            # Verificar portfolio
            portfolio_r = requests.get(f"{base_url}/api/paper_trading/portfolio", timeout=10)
            if portfolio_r.status_code == 200:
                portfolio_data = portfolio_r.json()
                active_trades = portfolio_data.get('active_trades', [])
                
                # Verificar se nosso trade ainda está ativo
                trade_active = any(t['id'] == trade_id for t in active_trades)
                
                if not trade_active:
                    print(f"\n🎉 Trade finalizado automaticamente após {elapsed:.1f}s!")
                    
                    # Verificar histórico
                    history_r = requests.get(f"{base_url}/api/paper_trading/history", timeout=10)
                    if history_r.status_code == 200:
                        history_data = history_r.json()
                        if history_data.get('success'):
                            trades = history_data.get('trades', [])
                            for trade in trades:
                                if trade.get('id') == trade_id:
                                    print(f"📊 Motivo: {trade.get('exit_reason', 'N/A')}")
                                    print(f"💰 P&L: ${trade.get('realized_pnl', 0):.2f}")
                                    break
                    
                    return True
                else:
                    # Trade ainda ativo
                    current_trade = next((t for t in active_trades if t['id'] == trade_id), None)
                    if current_trade:
                        current_price = current_trade.get('current_price', 0)
                        unrealized_pnl = current_trade.get('unrealized_pnl', 0)
                        print(f"   {elapsed:.0f}s - Preço: ${current_price:.2f} | P&L: ${unrealized_pnl:.2f}")
            
            time.sleep(5)
        
        print(f"\n⚠️ Trade não finalizado em 60 segundos")
        
        # Fechar manualmente para limpeza
        print("🔒 Fechando manualmente...")
        close_r = requests.post(f"{base_url}/api/paper_trading/close_trade",
                               json={"trade_id": trade_id},
                               headers={'Content-Type': 'application/json'})
        
        if close_r.status_code == 200:
            print("✅ Trade fechado manualmente")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🚀 DEBUG COMPLETO DO SISTEMA DE MONITORAMENTO")
    print("="*80)
    
    # Teste 1: Debug do monitor
    monitor_working = debug_monitor_directly()
    
    if monitor_working:
        print("\n✅ Monitor está funcionando!")
        
        # Teste 2: Ciclo de trade
        trade_working = test_quick_trade_cycle()
        
        if trade_working:
            print("\n🎉 SISTEMA FUNCIONANDO CORRETAMENTE!")
        else:
            print("\n⚠️ Monitor ativo mas trades não finalizam")
            print("💡 Problema pode ser:")
            print("   - Alvos muito distantes")
            print("   - Sistema de atualização de preços")
            print("   - Lógica de SL/TP")
    else:
        print("\n❌ PROBLEMA: Monitor não consegue iniciar")
        print("💡 Verificar:")
        print("   - Logs do servidor")
        print("   - Implementação do AutoTradeMonitor")
        print("   - Threading issues")

if __name__ == "__main__":
    main()
