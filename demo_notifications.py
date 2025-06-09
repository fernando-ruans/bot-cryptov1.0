#!/usr/bin/env python3
"""
Demo das Notificações do Sistema de Paper Trading Refinado
"""

import sys
sys.path.append('.')

from src.paper_trading import PaperTradingManager, PaperTrade
from datetime import datetime
import uuid

def demo_notifications():
    """Demonstra as funcionalidades de notificação do paper trading"""
    print("🔔 ═══ DEMO: SISTEMA DE NOTIFICAÇÕES REFINADO ═══\n")
    
    # Criar instância do paper trading
    paper_trading = PaperTradingManager(None, initial_balance=10000.0)
    
    print(f"💰 Saldo inicial: ${paper_trading.current_balance:.2f}\n")
    
    # Simular trade 1 - Take Profit
    print("📈 Simulando Trade 1 - Take Profit")
    trade1 = PaperTrade(
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
    
    # Adicionar ao paper trading
    paper_trading.active_trades[trade1.id] = trade1
    paper_trading.current_balance -= 1000.0  # Simular investimento
    
    print(f"   ✅ Trade criado: {trade1.id[:8]}")
    print(f"   💵 Entry: ${trade1.entry_price:.2f}")
    print(f"   🎯 Take Profit: ${trade1.take_profit:.2f}")
    
    # Simular atingir take profit
    print("\n🎯 Simulando atingir Take Profit...")
    trade1.update_current_price(52000.0)
    if trade1.status == 'closed':
        paper_trading._process_closed_trade(trade1)
    
    # Simular trade 2 - Stop Loss
    print("\n📉 Simulando Trade 2 - Stop Loss")
    trade2 = PaperTrade(
        id=str(uuid.uuid4()),
        symbol="ETHUSDT",
        trade_type="sell",
        entry_price=3000.0,
        quantity=0.5,
        stop_loss=3100.0,
        take_profit=2800.0,
        timeframe="4h",
        signal_confidence=0.75
    )
    
    # Adicionar ao paper trading
    paper_trading.active_trades[trade2.id] = trade2
    paper_trading.current_balance -= 1500.0  # Simular investimento
    
    print(f"   ✅ Trade criado: {trade2.id[:8]}")
    print(f"   💵 Entry: ${trade2.entry_price:.2f}")
    print(f"   🛑 Stop Loss: ${trade2.stop_loss:.2f}")
    
    # Simular atingir stop loss
    print("\n🛑 Simulando atingir Stop Loss...")
    trade2.update_current_price(3100.0)
    if trade2.status == 'closed':
        paper_trading._process_closed_trade(trade2)
    
    # Simular trade 3 - Fechamento Manual
    print("\n🔒 Simulando Trade 3 - Fechamento Manual")
    trade3 = PaperTrade(
        id=str(uuid.uuid4()),
        symbol="ADAUSDT",
        trade_type="buy",
        entry_price=0.50,
        quantity=2000,
        stop_loss=0.45,
        take_profit=0.60,
        timeframe="2h",
        signal_confidence=0.70
    )
    
    # Adicionar ao paper trading
    paper_trading.active_trades[trade3.id] = trade3
    paper_trading.current_balance -= 1000.0  # Simular investimento
    
    print(f"   ✅ Trade criado: {trade3.id[:8]}")
    print(f"   💵 Entry: ${trade3.entry_price:.2f}")
    
    # Atualizar preço e fechar manualmente
    trade3.update_current_price(0.55)
    print("\n🔒 Fechando trade manualmente...")
    trade3.close_manually(0.55)
    paper_trading._process_closed_trade(trade3)
    
    # Mostrar estatísticas finais
    print("\n📊 ═══ ESTATÍSTICAS FINAIS ═══")
    stats = paper_trading.get_detailed_stats()
    
    print(f"💰 Saldo final: ${stats['current_balance']:.2f}")
    print(f"📈 Saldo inicial: ${stats['initial_balance']:.2f}")
    print(f"💹 P&L total: ${stats['total_pnl']:.2f}")
    print(f"📊 Total de trades: {stats['total_trades']}")
    print(f"🎯 Trades lucrativos: {stats['profitable_trades']}")
    print(f"📉 Trades perdedores: {stats['losing_trades']}")
    print(f"🏆 Taxa de acerto: {stats['win_rate']:.1f}%")
    print(f"💎 Retorno total: {stats['total_return']:.2f}%")
    
    # Análise por motivo de saída
    if 'exit_reasons' in stats:
        print("\n🔍 Análise por motivo de saída:")
        for reason, data in stats['exit_reasons'].items():
            print(f"   {reason}: {data['count']} trades (P&L: ${data['total_pnl']:.2f})")
    
    # Análise por timeframe
    if 'timeframe_stats' in stats:
        print("\n⏰ Análise por timeframe:")
        for tf, data in stats['timeframe_stats'].items():
            print(f"   {tf}: {data['count']} trades | Win Rate: {data['win_rate']:.1f}% | P&L: ${data['total_pnl']:.2f}")
    
    # Mostrar histórico de notificações
    print("\n🔔 ═══ HISTÓRICO DE NOTIFICAÇÕES ═══")
    notifications = paper_trading.get_trade_notifications()
    
    if notifications:
        for i, notif in enumerate(notifications, 1):
            timestamp = datetime.fromisoformat(notif['timestamp']).strftime('%H:%M:%S')
            print(f"{i:2d}. [{timestamp}] {notif['emoji']} {notif['symbol']} | "
                  f"P&L: ${notif['realized_pnl']:.2f} | {notif['exit_reason_description']}")
            print(f"     💰 Novo saldo: ${notif['new_balance']:.2f} | "
                  f"⏱️ Duração: {notif['duration_formatted']} | "
                  f"📊 Mudança: {notif['price_change_percent']:.2f}%")
            print()
    else:
        print("   📭 Nenhuma notificação encontrada")
    
    print("🎉 Demo das notificações concluída!")
    print("\n✨ Funcionalidades implementadas:")
    print("   🔔 Notificações automáticas quando SL/TP são atingidos")
    print("   📊 Histórico detalhado de todas as operações")
    print("   📈 Estatísticas avançadas por timeframe e motivo de saída")
    print("   💰 Cálculo automático de P&L e atualização de saldo")
    print("   ⏱️ Tracking de duração e performance dos trades")
    print("   🎯 Análise de taxa de acerto e profit factor")

if __name__ == "__main__":
    demo_notifications()