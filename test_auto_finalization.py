#!/usr/bin/env python3
"""
Teste do Sistema de Monitoramento Automático de Trades
Verifica se os trades estão sendo finalizados automaticamente
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

def test_automatic_trade_finalization():
    """Testa se os trades estão sendo finalizados automaticamente"""
    print("🔄 TESTE DE FINALIZAÇÃO AUTOMÁTICA DE TRADES")
    print("="*60)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. Verificar se o monitor automático está rodando
        print("\n1. 📊 Verificando status do monitor automático...")
        monitor_response = requests.get(f"{base_url}/api/monitor/status")
        
        if monitor_response.status_code == 200:
            monitor_data = monitor_response.json()
            print(f"   Status: {'ATIVO' if monitor_data.get('running') else 'INATIVO'}")
            print(f"   Intervalo: {monitor_data.get('interval', 'N/A')} segundos")
            print(f"   Trades ativos: {monitor_data.get('active_trades_count', 0)}")
        else:
            print(f"   ❌ Erro ao verificar monitor: {monitor_response.status_code}")
        
        # 2. Gerar sinal de teste
        print("\n2. 🎯 Gerando sinal de teste...")
        signal_response = requests.post(
            f"{base_url}/api/generate_signal",
            json={"symbol": "BTCUSDT", "timeframe": "1h"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if signal_response.status_code != 200:
            print(f"   ❌ Erro ao gerar sinal: {signal_response.status_code}")
            return False
        
        signal_data = signal_response.json()
        if not signal_data.get('success'):
            print(f"   ❌ Erro no sinal: {signal_data.get('error')}")
            return False
        
        signal = signal_data['signal']
        print(f"   ✅ Sinal gerado: {signal['signal_type']} @ ${signal['entry_price']:.2f}")
        print(f"   📊 Stop Loss: ${signal['stop_loss']:.2f}")
        print(f"   📊 Take Profit: ${signal['take_profit']:.2f}")
        
        # 3. Confirmar trade
        print("\n3. ✅ Confirmando trade...")
        confirm_response = requests.post(
            f"{base_url}/api/paper_trading/confirm_signal",
            json={"signal": signal, "amount": 1000},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if confirm_response.status_code != 200:
            print(f"   ❌ Erro ao confirmar: {confirm_response.status_code}")
            return False
        
        confirm_data = confirm_response.json()
        if not confirm_data.get('success'):
            print(f"   ❌ Erro na confirmação: {confirm_data.get('error')}")
            return False
        
        trade_id = confirm_data.get('trade_id')
        print(f"   ✅ Trade confirmado: {trade_id}")
        
        # 4. Monitorar por alguns ciclos
        print(f"\n4. 👀 Monitorando trade por 2 minutos...")
        print(f"   Trade ID: {trade_id}")
        print(f"   Esperando finalização automática...")
        
        monitoring_start = time.time()
        monitoring_duration = 120  # 2 minutos
        check_interval = 10  # verificar a cada 10 segundos
        
        while time.time() - monitoring_start < monitoring_duration:
            # Verificar portfolio atual
            portfolio_response = requests.get(f"{base_url}/api/paper_trading/portfolio")
            
            if portfolio_response.status_code == 200:
                portfolio_data = portfolio_response.json()
                active_trades = portfolio_data.get('active_trades', [])
                
                # Verificar se nosso trade ainda está ativo
                trade_still_active = any(trade['id'] == trade_id for trade in active_trades)
                
                if not trade_still_active:
                    elapsed = time.time() - monitoring_start
                    print(f"\n   ✅ TRADE FINALIZADO AUTOMATICAMENTE!")
                    print(f"   ⏱️ Tempo até finalização: {elapsed:.1f} segundos")
                    
                    # Verificar no histórico
                    history_response = requests.get(f"{base_url}/api/paper_trading/history")
                    if history_response.status_code == 200:
                        history_data = history_response.json()
                        if history_data.get('success'):
                            trades_history = history_data.get('trades', [])
                            
                            # Encontrar nosso trade no histórico
                            closed_trade = None
                            for trade in trades_history:
                                if trade.get('id') == trade_id:
                                    closed_trade = trade
                                    break
                            
                            if closed_trade:
                                print(f"   📊 Motivo do fechamento: {closed_trade.get('exit_reason', 'N/A')}")
                                print(f"   💰 P&L: ${closed_trade.get('realized_pnl', 0):.2f}")
                                print(f"   📈 Preço de saída: ${closed_trade.get('exit_price', 0):.2f}")
                                
                                return True
                    
                    return True
                else:
                    # Trade ainda ativo - mostrar status
                    current_trade = None
                    for trade in active_trades:
                        if trade['id'] == trade_id:
                            current_trade = trade
                            break
                    
                    if current_trade:
                        elapsed = time.time() - monitoring_start
                        current_price = current_trade.get('current_price', 0)
                        unrealized_pnl = current_trade.get('unrealized_pnl', 0)
                        
                        print(f"   ⏱️ {elapsed:.0f}s - Preço atual: ${current_price:.2f} | P&L: ${unrealized_pnl:.2f}")
            
            time.sleep(check_interval)
        
        # Se chegou aqui, o trade não foi finalizado no tempo esperado
        print(f"\n   ⚠️ Trade não foi finalizado automaticamente em {monitoring_duration} segundos")
        print(f"   📋 Verificando se ainda está ativo...")
        
        # Verificação final
        portfolio_response = requests.get(f"{base_url}/api/paper_trading/portfolio")
        if portfolio_response.status_code == 200:
            portfolio_data = portfolio_response.json()
            active_trades = portfolio_data.get('active_trades', [])
            
            trade_still_active = any(trade['id'] == trade_id for trade in active_trades)
            
            if trade_still_active:
                print(f"   ❌ PROBLEMA: Trade ainda ativo após {monitoring_duration} segundos")
                print(f"   🔧 Possíveis causas:")
                print(f"      - Monitor automático não está funcionando")
                print(f"      - Preços não atingiram SL/TP")
                print(f"      - Erro no sistema de atualização de preços")
                
                # Fechar manualmente para limpeza
                print(f"\n   🔒 Fechando trade manualmente para limpeza...")
                close_response = requests.post(
                    f"{base_url}/api/paper_trading/close_trade",
                    json={"trade_id": trade_id},
                    headers={"Content-Type": "application/json"}
                )
                
                if close_response.status_code == 200:
                    print(f"   ✅ Trade fechado manualmente")
                
                return False
            else:
                print(f"   ✅ Trade foi finalizado (verificação final)")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

def test_monitor_status():
    """Testa apenas o status do monitor"""
    print("\n🔍 TESTE RÁPIDO - STATUS DO MONITOR")
    print("="*40)
    
    base_url = "http://localhost:5000"
    
    try:
        # Status do monitor
        monitor_response = requests.get(f"{base_url}/api/monitor/status", timeout=10)
        
        if monitor_response.status_code == 200:
            monitor_data = monitor_response.json()
            print(f"✅ Monitor Status:")
            print(f"   🔄 Rodando: {'SIM' if monitor_data.get('running') else 'NÃO'}")
            print(f"   ⏱️ Intervalo: {monitor_data.get('interval', 'N/A')} segundos")
            print(f"   📊 Trades ativos: {monitor_data.get('active_trades_count', 0)}")
            
            return monitor_data.get('running', False)
        else:
            print(f"❌ Erro ao verificar monitor: {monitor_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Executar testes do sistema de monitoramento"""
    print("🚀 DIAGNÓSTICO DO SISTEMA DE MONITORAMENTO AUTOMÁTICO")
    print("="*80)
    
    # Teste 1: Status do monitor
    monitor_ok = test_monitor_status()
    
    if not monitor_ok:
        print("\n❌ PROBLEMA IDENTIFICADO: Monitor automático não está rodando!")
        print("💡 SOLUÇÕES:")
        print("   1. Reiniciar o servidor main.py")
        print("   2. Verificar logs de erro")
        print("   3. Chamar POST /api/monitor/start")
        return
    
    # Teste 2: Finalização automática
    print("\n" + "="*80)
    auto_finalization_ok = test_automatic_trade_finalization()
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("="*80)
    print(f"Monitor Automático: {'✅ FUNCIONANDO' if monitor_ok else '❌ PROBLEMA'}")
    print(f"Finalização Automática: {'✅ FUNCIONANDO' if auto_finalization_ok else '❌ PROBLEMA'}")
    
    if monitor_ok and auto_finalization_ok:
        print("\n🎉 SISTEMA DE MONITORAMENTO FUNCIONANDO CORRETAMENTE!")
    elif monitor_ok and not auto_finalization_ok:
        print("\n⚠️ PROBLEMA: Monitor ativo mas trades não finalizam automaticamente")
        print("💡 Verificar:")
        print("   - Sistema de preços em tempo real")
        print("   - Lógica de Stop Loss / Take Profit")
        print("   - Logs do servidor para erros")
    else:
        print("\n❌ PROBLEMA: Sistema de monitoramento não está funcionando")
        print("💡 Reiniciar o servidor e verificar logs")

if __name__ == "__main__":
    main()
