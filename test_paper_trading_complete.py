#!/usr/bin/env python3
"""
Teste completo do sistema de Paper Trading
Este script demonstra o fluxo completo:
1. Gerar sinal
2. Confirmar sinal no paper trading
3. Verificar portfolio
4. Verificar trades ativos
5. Fechar trade manualmente
6. Verificar histórico
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_paper_trading_flow():
    print("🚀 Iniciando teste completo do Paper Trading...")
    print("=" * 60)
    
    # 1. Gerar um sinal
    print("\n📊 1. Gerando sinal para BTCUSDT...")
    response = requests.post(
        f"{BASE_URL}/api/generate_signal",
        json={"symbol": "BTCUSDT"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        signal_data = response.json()
        if signal_data.get('success'):
            signal = signal_data['signal']
            print(f"✅ Sinal gerado: {signal['signal_type'].upper()} em ${signal['entry_price']:.2f}")
            print(f"   📈 Confiança: {signal['confidence']:.2%}")
            print(f"   🛑 Stop Loss: ${signal['stop_loss']:.2f}")
            print(f"   🎯 Take Profit: ${signal['take_profit']:.2f}")
        else:
            print("❌ Falha ao gerar sinal")
            return
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return
    
    # 2. Confirmar sinal no paper trading
    print("\n🤝 2. Confirmando sinal no Paper Trading...")
    confirm_data = {
        "symbol": signal['symbol'],
        "signal": signal['signal_type'],
        "entry_price": signal['entry_price'],
        "stop_loss": signal['stop_loss'],
        "take_profit": signal['take_profit'],
        "confidence": signal['confidence'],
        "timeframe": signal['timeframe']
    }
    
    response = requests.post(
        f"{BASE_URL}/api/paper_trading/confirm_signal",
        json=confirm_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        trade_data = response.json()
        if trade_data.get('success'):
            trade_id = trade_data['trade_id']
            print(f"✅ Trade criado com sucesso! ID: {trade_id}")
        else:
            print("❌ Falha ao criar trade")
            return
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return
    
    # 3. Verificar portfolio
    print("\n💼 3. Verificando Portfolio...")
    response = requests.get(f"{BASE_URL}/api/paper_trading/portfolio")
    
    if response.status_code == 200:
        portfolio_data = response.json()
        if portfolio_data.get('success'):
            stats = portfolio_data['portfolio']
            active_trades = portfolio_data['active_trades']
            
            print(f"   💰 Saldo: ${stats['current_balance']:.2f}")
            print(f"   📊 Trades Ativos: {stats['active_trades']}")
            print(f"   📈 P&L Total: ${stats['total_pnl']:.2f}")
            print(f"   🏆 Win Rate: {stats['win_rate']:.1f}%")
            
            if active_trades:
                trade = active_trades[0]
                print(f"\n📋 Trade Ativo:")
                print(f"   🏷️  ID: {trade['id']}")
                print(f"   📊 {trade['symbol']} - {trade['side']}")
                print(f"   💵 Entrada: ${trade['entry_price']:.2f}")
                print(f"   💰 Atual: ${trade['current_price']:.2f}")
                print(f"   📈 P&L: ${trade['unrealized_pnl']:.2f}")
        else:
            print("❌ Falha ao obter portfolio")
            return
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return
    
    # 4. Aguardar um pouco para simular trade ativo
    print("\n⏳ 4. Aguardando 5 segundos para simular trade ativo...")
    time.sleep(5)
    
    # 5. Fechar trade manualmente
    print("\n🔐 5. Fechando trade manualmente...")
    response = requests.post(
        f"{BASE_URL}/api/paper_trading/close_trade",
        json={"trade_id": trade_id},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        close_data = response.json()
        if close_data.get('success'):
            print("✅ Trade fechado com sucesso!")
        else:
            print("❌ Falha ao fechar trade")
            return
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return
    
    # 6. Verificar histórico
    print("\n📚 6. Verificando Histórico de Trades...")
    response = requests.get(f"{BASE_URL}/api/paper_trading/history")
    
    if response.status_code == 200:
        history_data = response.json()
        if history_data.get('success'):
            trades = history_data['trades']
            total_count = history_data['total_count']
            
            print(f"   📊 Total de Trades: {total_count}")
            
            if trades:
                for trade in trades[-3:]:  # Últimos 3 trades
                    status_emoji = {
                        'completed': '✅',
                        'stopped_out': '🛑',
                        'took_profit': '🎯',
                        'manual': '🔐'
                    }.get(trade['exit_reason'], '📊')
                    
                    pnl_emoji = '📈' if trade['realized_pnl'] >= 0 else '📉'
                    
                    print(f"\n   {status_emoji} Trade {trade['id'][:8]}...")
                    print(f"      📊 {trade['symbol']} - {trade['side']}")
                    print(f"      💵 Entrada: ${trade['entry_price']:.2f}")
                    print(f"      💰 Saída: ${trade['exit_price']:.2f}")
                    print(f"      {pnl_emoji} P&L: ${trade['realized_pnl']:.2f} ({trade['pnl_percentage']:.2f}%)")
                    print(f"      🕐 Duração: {trade['entry_timestamp']} → {trade['exit_timestamp']}")
        else:
            print("❌ Falha ao obter histórico")
            return
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return
    
    # 7. Portfolio final
    print("\n💼 7. Portfolio Final...")
    response = requests.get(f"{BASE_URL}/api/paper_trading/portfolio")
    
    if response.status_code == 200:
        portfolio_data = response.json()
        if portfolio_data.get('success'):
            stats = portfolio_data['portfolio']
            
            print(f"   💰 Saldo Final: ${stats['current_balance']:.2f}")
            print(f"   📊 Total de Trades: {stats['total_trades']}")
            print(f"   🏆 Trades Vencedores: {stats['profitable_trades']}")
            print(f"   💔 Trades Perdedores: {stats['losing_trades']}")
            print(f"   📈 Win Rate: {stats['win_rate']:.1f}%")
            print(f"   🚀 Retorno Total: {stats['total_return']:.2f}%")
    
    print("\n" + "=" * 60)
    print("🎉 Teste completo do Paper Trading finalizado!")
    print("✅ Todos os endpoints funcionando corretamente!")
    print("🌐 Interface web disponível em: http://127.0.0.1:5000")

if __name__ == "__main__":
    try:
        test_paper_trading_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
        print("🚀 Certifique-se de que a aplicação está rodando: python main.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
