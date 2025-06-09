#!/usr/bin/env python3
"""
Demo Simples do Sistema Refinado de Paper Trading
"""

import sys
sys.path.append('.')

from src.paper_trading import PaperTradingManager, PaperTrade
from datetime import datetime
import uuid

def simple_demo():
    """Demo simples das funcionalidades refinadas"""
    print("🔔 SISTEMA DE PAPER TRADING REFINADO")
    print("═" * 50)
    
    # Criar paper trading manager
    manager = PaperTradingManager(None, initial_balance=10000.0)
    print(f"💰 Saldo inicial: ${manager.current_balance:.2f}\n")
    
    # Criar trade de exemplo
    trade = PaperTrade(
        id=str(uuid.uuid4()),
        symbol="BTCUSDT",
        trade_type="buy",
        entry_price=50000.0,
        quantity=0.02,
        stop_loss=49000.0,
        take_profit=52000.0,
        timeframe="1h",
        signal_confidence=0.85
    )
    
    # Adicionar trade ao manager
    manager.active_trades[trade.id] = trade
    manager.current_balance -= 1000.0  # Simular investimento
    
    print("📈 TRADE CRIADO:")
    print(f"   ID: {trade.id[:8]}")
    print(f"   Symbol: {trade.symbol}")
    print(f"   Tipo: {trade.trade_type.upper()}")
    print(f"   Entry: ${trade.entry_price:.2f}")
    print(f"   Stop Loss: ${trade.stop_loss:.2f}")
    print(f"   Take Profit: ${trade.take_profit:.2f}")
    print(f"   Quantidade: {trade.quantity:.6f}")
    print(f"   Timeframe: {trade.timeframe}")
    print(f"   Confiança: {trade.signal_confidence:.1%}\n")
    
    # Simular movimento de preço até take profit
    print("🎯 SIMULANDO TAKE PROFIT:")
    print(f"   Preço atual: ${trade.current_price:.2f}")
    print(f"   Movendo para: ${trade.take_profit:.2f}")
    
    # Atualizar preço
    hit_target = trade.update_current_price(52000.0)
    
    if hit_target and trade.status == 'closed':
        print(f"   ✅ Take Profit atingido!")
        print(f"   💰 P&L Realizado: ${trade.realized_pnl:.2f}")
        print(f"   📊 Retorno: {trade.pnl_percent:.2f}%")
        
        # Processar trade fechado
        manager._process_closed_trade(trade)
        
        # Mostrar estatísticas
        stats = manager.get_detailed_stats()
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Saldo atual: ${stats['current_balance']:.2f}")
        print(f"   Total trades: {stats['total_trades']}")
        print(f"   Taxa de acerto: {stats['win_rate']:.1f}%")
        print(f"   Retorno total: {stats['total_return']:.2f}%")
        
        # Mostrar notificações
        notifications = manager.get_trade_notifications()
        if notifications:
            print(f"\n🔔 NOTIFICAÇÕES:")
            for notif in notifications:
                timestamp = datetime.fromisoformat(notif['timestamp']).strftime('%H:%M:%S')
                print(f"   [{timestamp}] {notif['emoji']} {notif['symbol']}")
                print(f"   P&L: ${notif['realized_pnl']:.2f} | {notif['exit_reason_description']}")
                print(f"   Novo saldo: ${notif['new_balance']:.2f}")
    
    print("\n✨ FUNCIONALIDADES IMPLEMENTADAS:")
    print("   🔔 Notificações automáticas")
    print("   📊 Histórico detalhado")
    print("   💰 Cálculo automático de P&L")
    print("   📈 Estatísticas avançadas")
    print("   🎯 Detecção automática de SL/TP")
    print("   ⏱️ Tracking de duração")
    
    print("\n🎉 Demo concluída com sucesso!")

if __name__ == "__main__":
    simple_demo()