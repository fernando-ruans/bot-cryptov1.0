#!/usr/bin/env python3
"""
Teste do Sistema Refinado de Paper Trading
Demonstra notificações automáticas e histórico detalhado
"""

import sys
import time
import threading
from datetime import datetime
sys.path.append('.')

from src.paper_trading import PaperTradingManager, PaperTrade
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator

def simulate_price_movement(paper_trading, trade_id, target_price, steps=5):
    """Simula movimento de preço gradual até atingir o alvo"""
    if trade_id not in paper_trading.active_trades:
        return
    
    trade = paper_trading.active_trades[trade_id]
    current_price = trade.current_price
    
    # Calcular incremento por step
    price_diff = target_price - current_price
    step_increment = price_diff / steps
    
    print(f"\n🎬 Simulando movimento de preço: ${current_price:.2f} → ${target_price:.2f}")
    
    for i in range(steps + 1):
        if trade_id not in paper_trading.active_trades:
            break
            
        new_price = current_price + (step_increment * i)
        print(f"   📊 Preço atual: ${new_price:.2f}")
        
        # Atualizar preço no trade
        paper_trading.update_prices({trade.symbol: new_price})
        
        time.sleep(1)  # Pausa para simular tempo real
    
    print(f"   ✅ Movimento concluído")

def test_refined_paper_trading():
    """Testa o sistema refinado de paper trading"""
    print("🧪 ═══ TESTE DO SISTEMA REFINADO DE PAPER TRADING ═══\n")
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_gen = SignalGenerator(ai_engine, market_data)
        
        # Inicializar Paper Trading com saldo inicial
        paper_trading = PaperTradingManager(market_data, initial_balance=10000.0)
        
        print(f"💰 Saldo inicial: ${paper_trading.current_balance:.2f}\n")
        
        # Gerar sinal de teste
        print("📡 Gerando sinal de teste...")
        signal = signal_gen.generate_signal('BTCUSDT', '1h')
        
        if not signal:
            print("❌ Não foi possível gerar sinal")
            return
        
        print(f"✅ Sinal gerado: {signal.signal_type.upper()} @ ${signal.entry_price:.2f}")
        print(f"   🛑 Stop Loss: ${signal.stop_loss:.2f}")
        print(f"   🎯 Take Profit: ${signal.take_profit:.2f}")
        
        # Confirmar trade
        print("\n📋 Confirmando trade...")
        trade = paper_trading.confirm_signal({
            'symbol': signal.symbol,
            'signal_type': signal.signal_type,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'confidence': signal.confidence,
            'timeframe': signal.timeframe
        }, amount=1000.0)
        
        if not trade:
            print("❌ Falha ao confirmar trade")
            return
        
        print(f"✅ Trade confirmado: {trade.id[:8]}")
        print(f"   💵 Quantidade: {trade.quantity:.6f} {signal.symbol}")
        print(f"   💰 Valor investido: $1000.00")
        
        # Mostrar trades ativos
        print("\n📊 Trades ativos:")
        active_trades = paper_trading.get_active_trades()
        for active_trade in active_trades:
            print(f"   🔄 {active_trade['id'][:8]} | {active_trade['symbol']} | ${active_trade['entry_price']:.2f}")
        
        # Teste 1: Simular Take Profit
        print("\n🎯 ═══ TESTE 1: TAKE PROFIT ═══")
        print("Simulando movimento de preço até atingir Take Profit...")
        
        # Executar simulação em thread separada
        tp_thread = threading.Thread(
            target=simulate_price_movement,
            args=(paper_trading, trade.id, signal.take_profit)
        )
        tp_thread.start()
        tp_thread.join()
        
        # Verificar se trade foi fechado
        if trade.id not in paper_trading.active_trades:
            print("✅ Trade fechado automaticamente por Take Profit!")
        
        # Mostrar estatísticas após primeiro trade
        print("\n📈 Estatísticas após Take Profit:")
        stats = paper_trading.get_detailed_stats()
        print(f"   💰 Saldo atual: ${stats['current_balance']:.2f}")
        print(f"   📊 Total de trades: {stats['total_trades']}")
        print(f"   🎯 Taxa de acerto: {stats['win_rate']:.1f}%")
        print(f"   💹 Retorno total: {stats['total_return']:.2f}%")
        
        # Criar segundo trade para testar Stop Loss
        print("\n🛑 ═══ TESTE 2: STOP LOSS ═══")
        print("Gerando segundo sinal para teste de Stop Loss...")
        
        signal2 = signal_gen.generate_signal('BTCUSDT', '4h')
        if signal2:
            trade2 = paper_trading.confirm_signal({
                'symbol': signal2.symbol,
                'signal_type': signal2.signal_type,
                'entry_price': signal2.entry_price,
                'stop_loss': signal2.stop_loss,
                'take_profit': signal2.take_profit,
                'confidence': signal2.confidence,
                'timeframe': signal2.timeframe
            }, amount=1500.0)
            
            if trade2:
                print(f"✅ Segundo trade criado: {trade2.id[:8]}")
                print("Simulando movimento de preço até atingir Stop Loss...")
                
                # Simular movimento para Stop Loss
                sl_thread = threading.Thread(
                    target=simulate_price_movement,
                    args=(paper_trading, trade2.id, signal2.stop_loss)
                )
                sl_thread.start()
                sl_thread.join()
        
        # Teste 3: Fechamento Manual
        print("\n🔒 ═══ TESTE 3: FECHAMENTO MANUAL ═══")
        signal3 = signal_gen.generate_signal('BTCUSDT', '2h')
        if signal3:
            trade3 = paper_trading.confirm_signal({
                'symbol': signal3.symbol,
                'signal_type': signal3.signal_type,
                'entry_price': signal3.entry_price,
                'stop_loss': signal3.stop_loss,
                'take_profit': signal3.take_profit,
                'confidence': signal3.confidence,
                'timeframe': signal3.timeframe
            }, amount=800.0)
            
            if trade3:
                print(f"✅ Terceiro trade criado: {trade3.id[:8]}")
                print("Aguardando 3 segundos antes do fechamento manual...")
                time.sleep(3)
                
                # Fechar manualmente
                success = paper_trading.close_trade_manually(trade3.id)
                if success:
                    print("✅ Trade fechado manualmente!")
        
        # Mostrar estatísticas finais
        print("\n📊 ═══ ESTATÍSTICAS FINAIS ═══")
        final_stats = paper_trading.get_detailed_stats()
        
        print(f"💰 Saldo final: ${final_stats['current_balance']:.2f}")
        print(f"📈 Saldo inicial: ${final_stats['initial_balance']:.2f}")
        print(f"💹 P&L total: ${final_stats['total_pnl']:.2f}")
        print(f"📊 Total de trades: {final_stats['total_trades']}")
        print(f"🎯 Trades lucrativos: {final_stats['profitable_trades']}")
        print(f"📉 Trades perdedores: {final_stats['losing_trades']}")
        print(f"🏆 Taxa de acerto: {final_stats['win_rate']:.1f}%")
        print(f"💎 Retorno total: {final_stats['total_return']:.2f}%")
        
        if 'exit_reasons' in final_stats:
            print("\n🔍 Análise por motivo de saída:")
            for reason, data in final_stats['exit_reasons'].items():
                print(f"   {reason}: {data['count']} trades (P&L: ${data['total_pnl']:.2f})")
        
        if 'timeframe_stats' in final_stats:
            print("\n⏰ Análise por timeframe:")
            for tf, data in final_stats['timeframe_stats'].items():
                print(f"   {tf}: {data['count']} trades | Win Rate: {data['win_rate']:.1f}% | P&L: ${data['total_pnl']:.2f}")
        
        # Mostrar histórico de notificações
        print("\n🔔 ═══ HISTÓRICO DE NOTIFICAÇÕES ═══")
        notifications = paper_trading.get_trade_notifications(limit=10)
        
        if notifications:
            for i, notif in enumerate(notifications, 1):
                timestamp = datetime.fromisoformat(notif['timestamp']).strftime('%H:%M:%S')
                print(f"{i:2d}. [{timestamp}] {notif['emoji']} {notif['symbol']} | "
                      f"P&L: ${notif['realized_pnl']:.2f} | {notif['exit_reason_description']}")
        else:
            print("   📭 Nenhuma notificação encontrada")
        
        print("\n🎉 Teste do sistema refinado concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_refined_paper_trading()