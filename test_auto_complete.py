#!/usr/bin/env python3
"""
Teste Completo de Finalização Automática
Cria um trade e monitora se é finalizado automaticamente
"""

import requests
import time
import json

def test_complete_auto_finalization():
    """Teste completo de finalização automática"""
    print("🚀 TESTE COMPLETO - FINALIZAÇÃO AUTOMÁTICA DE TRADES")
    print("="*70)
    
    base_url = "http://localhost:5000"
    
    # 1. Verificar se o sistema está ativo
    print("\n1. 🔍 Verificando Sistema...")
    try:
        # Status do monitor
        r = requests.get(f"{base_url}/api/monitor/status", timeout=5)
        if r.status_code == 200:
            data = r.json()
            status = data.get("status", {})
            monitor_running = status.get("running", False)
            print(f"   📊 Monitor Automático: {'✅ ATIVO' if monitor_running else '❌ INATIVO'}")
            print(f"   ⏱️ Intervalo de verificação: {status.get('interval', 'N/A')} segundos")
        else:
            print(f"   ❌ Erro ao verificar monitor: {r.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    if not monitor_running:
        print("\n❌ PROBLEMA: Monitor não está ativo!")
        print("💡 Solução: Reiniciar o servidor ou chamar POST /api/monitor/start")
        return False
    
    # 2. Gerar sinal com timeframe curto para alvos próximos
    print("\n2. 🎯 Gerando Sinal de Teste...")
    try:
        r = requests.post(f"{base_url}/api/generate_signal",
                         json={"symbol": "BTCUSDT", "timeframe": "1m"},  # 1m = alvos muito próximos
                         headers={"Content-Type": "application/json"},
                         timeout=30)
        
        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                signal = data["signal"]
                entry_price = signal["entry_price"]
                stop_loss = signal["stop_loss"]
                take_profit = signal["take_profit"]
                
                print(f"   ✅ Sinal gerado: {signal['signal_type'].upper()} @ ${entry_price:.2f}")
                print(f"   🛑 Stop Loss: ${stop_loss:.2f}")
                print(f"   🎯 Take Profit: ${take_profit:.2f}")
                
                # Calcular distâncias percentuais
                sl_distance = abs(stop_loss - entry_price) / entry_price * 100
                tp_distance = abs(take_profit - entry_price) / entry_price * 100
                
                print(f"   📏 Distância SL: {sl_distance:.3f}%")
                print(f"   📏 Distância TP: {tp_distance:.3f}%")
                
                # Verificar se os alvos são muito distantes
                if sl_distance > 1.0 or tp_distance > 1.0:
                    print(f"   ⚠️ AVISO: Alvos relativamente distantes (>1%)")
                    print(f"   💡 Pode demorar mais para finalizar")
            else:
                print(f"   ❌ Erro no sinal: {data.get('error')}")
                return False
        else:
            print(f"   ❌ Erro HTTP: {r.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    # 3. Confirmar o trade
    print("\n3. ✅ Confirmando Trade...")
    try:
        r = requests.post(f"{base_url}/api/paper_trading/confirm_signal",
                         json={"signal": signal, "amount": 1000},
                         headers={"Content-Type": "application/json"},
                         timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                trade_id = data.get("trade_id")
                print(f"   ✅ Trade confirmado: {trade_id}")
                print(f"   💰 Valor investido: $1000")
            else:
                print(f"   ❌ Erro na confirmação: {data.get('error')}")
                return False
        else:
            print(f"   ❌ Erro HTTP: {r.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    # 4. Monitoramento em tempo real
    print(f"\n4. 👀 MONITORAMENTO EM TEMPO REAL")
    print(f"   🎯 Trade ID: {trade_id}")
    print(f"   ⏱️ Duração máxima: 3 minutos")
    print(f"   🔄 Verificação a cada 10 segundos")
    print(f"   📊 Aguardando finalização automática...")
    
    start_time = time.time()
    max_duration = 180  # 3 minutos
    check_interval = 10  # 10 segundos
    
    check_count = 0
    
    while time.time() - start_time < max_duration:
        check_count += 1
        elapsed = time.time() - start_time
        
        print(f"\n   🔍 Verificação #{check_count} ({elapsed:.0f}s)")
        
        try:
            # Verificar portfolio atual
            r = requests.get(f"{base_url}/api/paper_trading/portfolio", timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                active_trades = data.get("active_trades", [])
                
                # Verificar se nosso trade ainda está ativo
                our_trade = None
                for trade in active_trades:
                    if trade["id"] == trade_id:
                        our_trade = trade
                        break
                
                if our_trade is None:
                    # Trade foi finalizado!
                    print(f"\n   🎉 TRADE FINALIZADO AUTOMATICAMENTE!")
                    print(f"   ⏱️ Tempo até finalização: {elapsed:.1f} segundos")
                    
                    # Buscar no histórico para ver detalhes
                    try:
                        r = requests.get(f"{base_url}/api/paper_trading/history", timeout=5)
                        if r.status_code == 200:
                            history_data = r.json()
                            if history_data.get("success"):
                                trades = history_data.get("trades", [])
                                
                                for trade in trades:
                                    if trade.get("id") == trade_id:
                                        exit_reason = trade.get("exit_reason", "N/A")
                                        realized_pnl = trade.get("realized_pnl", 0)
                                        exit_price = trade.get("exit_price", 0)
                                        
                                        print(f"   📊 Motivo do fechamento: {exit_reason}")
                                        print(f"   💰 P&L realizado: ${realized_pnl:.2f}")
                                        print(f"   📈 Preço de saída: ${exit_price:.2f}")
                                        
                                        reason_emoji = {
                                            'take_profit': '🎯',
                                            'stop_loss': '🛑',
                                            'manual': '🔒'
                                        }.get(exit_reason, '📊')
                                        
                                        print(f"\n   {reason_emoji} RESULTADO: {'LUCRO' if realized_pnl > 0 else 'PREJUÍZO' if realized_pnl < 0 else 'EMPATE'}")
                                        break
                    except:
                        pass
                    
                    return True
                else:
                    # Trade ainda ativo - mostrar status
                    current_price = our_trade.get("current_price", 0)
                    unrealized_pnl = our_trade.get("unrealized_pnl", 0)
                    entry_price = our_trade.get("entry_price", 0)
                    
                    # Calcular movimento percentual
                    if entry_price > 0:
                        price_movement = (current_price - entry_price) / entry_price * 100
                    else:
                        price_movement = 0
                    
                    pnl_indicator = "📈" if unrealized_pnl > 0 else "📉" if unrealized_pnl < 0 else "➡️"
                    
                    print(f"      📊 Preço atual: ${current_price:.2f} ({price_movement:+.3f}%)")
                    print(f"      {pnl_indicator} P&L não realizado: ${unrealized_pnl:.2f}")
            else:
                print(f"      ❌ Erro ao verificar portfolio: {r.status_code}")
        
        except Exception as e:
            print(f"      ⚠️ Erro na verificação: {e}")
        
        # Aguardar próxima verificação
        time.sleep(check_interval)
    
    # Se chegou aqui, o trade não foi finalizado no tempo esperado
    print(f"\n   ⚠️ TIMEOUT: Trade não finalizado em {max_duration} segundos")
    
    # Verificação final e limpeza
    print(f"\n5. 🧹 Limpeza Final...")
    try:
        r = requests.get(f"{base_url}/api/paper_trading/portfolio", timeout=5)
        if r.status_code == 200:
            data = r.json()
            active_trades = data.get("active_trades", [])
            
            trade_still_active = any(t["id"] == trade_id for t in active_trades)
            
            if trade_still_active:
                print(f"   🔒 Fechando trade manualmente...")
                r = requests.post(f"{base_url}/api/paper_trading/close_trade",
                                 json={"trade_id": trade_id},
                                 headers={"Content-Type": "application/json"})
                
                if r.status_code == 200:
                    print(f"   ✅ Trade fechado manualmente")
                else:
                    print(f"   ❌ Erro ao fechar: {r.status_code}")
    except:
        pass
    
    return False

def main():
    """Executar teste principal"""
    print("🤖 SISTEMA DE TRADING - TESTE DE FINALIZAÇÃO AUTOMÁTICA")
    print("="*80)
    
    success = test_complete_auto_finalization()
    
    print("\n" + "="*80)
    print("📊 RESULTADO FINAL")
    print("="*80)
    
    if success:
        print("🎉 SUCESSO: Finalização automática funcionando corretamente!")
        print("✅ O sistema está operacional e finalizando trades automaticamente")
    else:
        print("⚠️ PROBLEMA: Finalização automática não funcionou como esperado")
        print("💡 Possíveis causas:")
        print("   - Monitor automático não está ativo")
        print("   - Alvos muito distantes para o movimento atual do mercado")
        print("   - Baixa volatilidade no período testado")
        print("   - Timeframe longo com alvos conservadores")
        print("\n🔧 Recomendações:")
        print("   - Verificar se monitor está ativo: GET /api/monitor/status")
        print("   - Usar timeframes menores (1m, 5m) para testes")
        print("   - Aguardar maior movimento do mercado")
        print("   - Usar fechamento manual quando necessário")

if __name__ == "__main__":
    main()
