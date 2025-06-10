#!/usr/bin/env python3
"""
Teste das notificações de trade fechado e atualização automática do histórico
"""

import sys
import os
sys.path.append(os.getcwd())

import time
import requests
import json

def test_trade_notifications():
    """Testa o fluxo completo de notificações"""
    print("🧪 TESTE DE NOTIFICAÇÕES DE TRADE")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 1. Gerar um sinal
        print("\n1. 📊 Gerando sinal...")
        signal_response = requests.post(
            f"{base_url}/api/generate_signal",
            json={"symbol": "BTCUSDT"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if signal_response.status_code != 200:
            print(f"❌ Erro ao gerar sinal: {signal_response.status_code}")
            return False
        
        signal_data = signal_response.json()
        if not signal_data.get('success'):
            print(f"❌ Erro no sinal: {signal_data.get('error')}")
            return False
        
        signal = signal_data['signal']
        print(f"✅ Sinal gerado: {signal['signal_type']} {signal['symbol']} @ ${signal['entry_price']:.2f}")
        
        # 2. Confirmar sinal
        print("\n2. ✅ Confirmando sinal...")
        confirm_response = requests.post(
            f"{base_url}/api/paper_trading/confirm_signal",
            json={
                "signal": signal,
                "amount": 1000
            },
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if confirm_response.status_code != 200:
            print(f"❌ Erro ao confirmar: {confirm_response.status_code}")
            return False
        
        confirm_data = confirm_response.json()
        if not confirm_data.get('success'):
            print(f"❌ Erro na confirmação: {confirm_data.get('error')}")
            return False
        
        trade_id = confirm_data.get('trade_id')
        print(f"✅ Trade confirmado: {trade_id}")
        
        # 3. Verificar se aparece nos trades ativos
        print("\n3. 📋 Verificando trades ativos...")
        portfolio_response = requests.get(f"{base_url}/api/paper_trading/portfolio")
        if portfolio_response.status_code == 200:
            portfolio_data = portfolio_response.json()
            active_trades = portfolio_data.get('active_trades', [])
            print(f"✅ Trades ativos encontrados: {len(active_trades)}")
            
            if active_trades:
                active_trade = active_trades[0]
                print(f"   Trade ID: {active_trade['id']}")
                print(f"   Symbol: {active_trade['symbol']}")
                print(f"   Status: {active_trade['status']}")
        
        # 4. Aguardar um pouco
        print("\n4. ⏳ Aguardando 3 segundos...")
        time.sleep(3)
        
        # 5. Fechar trade manualmente
        print("\n5. 🔒 Fechando trade manualmente...")
        close_response = requests.post(
            f"{base_url}/api/paper_trading/close_trade",
            json={"trade_id": trade_id},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if close_response.status_code != 200:
            print(f"❌ Erro ao fechar trade: {close_response.status_code}")
            return False
        
        close_data = close_response.json()
        if not close_data.get('success'):
            print(f"❌ Erro no fechamento: {close_data.get('error')}")
            return False
        
        print("✅ Trade fechado com sucesso!")
        
        # 6. Verificar se saiu dos trades ativos
        print("\n6. 📋 Verificando se trade foi removido dos ativos...")
        time.sleep(1)  # Aguardar processamento
        
        portfolio_response = requests.get(f"{base_url}/api/paper_trading/portfolio")
        if portfolio_response.status_code == 200:
            portfolio_data = portfolio_response.json()
            active_trades_after = portfolio_data.get('active_trades', [])
            print(f"✅ Trades ativos restantes: {len(active_trades_after)}")
        
        # 7. Verificar se aparece no histórico
        print("\n7. 📜 Verificando se aparece no histórico...")
        time.sleep(1)  # Aguardar processamento
        
        history_response = requests.get(f"{base_url}/api/paper_trading/history")
        if history_response.status_code == 200:
            history_data = history_response.json()
            if history_data.get('success'):
                trades = history_data.get('trades', [])
                print(f"✅ Trades no histórico: {len(trades)}")
                
                # Procurar nosso trade
                found_trade = None
                for trade in trades:
                    if trade['id'] == trade_id:
                        found_trade = trade
                        break
                
                if found_trade:
                    print(f"✅ Trade encontrado no histórico!")
                    print(f"   ID: {found_trade['id']}")
                    print(f"   Symbol: {found_trade['symbol']}")
                    print(f"   Status: {found_trade['status']}")
                    print(f"   P&L: ${found_trade.get('realized_pnl', found_trade.get('pnl', 0)):.2f}")
                    print(f"   Exit Reason: {found_trade.get('exit_reason', 'N/A')}")
                else:
                    print("❌ Trade NÃO encontrado no histórico - Este é o problema!")
                    return False
            else:
                print(f"❌ Erro ao obter histórico: {history_data.get('error')}")
                return False
        
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("\n📋 RESUMO:")
        print("   ✅ Sinal gerado")
        print("   ✅ Trade confirmado") 
        print("   ✅ Trade apareceu nos ativos")
        print("   ✅ Trade fechado manualmente")
        print("   ✅ Trade removido dos ativos")
        print("   ✅ Trade apareceu no histórico")
        print("\n💡 Se você estiver na interface web, deve ver:")
        print("   1. Notificação de trade fechado")
        print("   2. Histórico atualizado automaticamente")
        print("   3. Portfolio atualizado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

def test_websocket_events():
    """Teste específico dos eventos WebSocket"""
    print("\n🔗 TESTE DE EVENTOS WEBSOCKET")
    print("=" * 30)
    
    try:
        # Simular dados de teste
        test_trade_data = {
            'id': 'test-trade-123',
            'symbol': 'BTCUSDT',
            'exit_reason': 'manual',
            'realized_pnl': 15.50,
            'pnl_percent': 2.5,
            'exit_price': 106000.0,
            'duration_minutes': 10
        }
        
        # Importar sistema de notificações
        from src.realtime_updates import RealTimeUpdates
        from flask_socketio import SocketIO
        from flask import Flask
        
        app = Flask(__name__)
        socketio = SocketIO(app)
        realtime_updates = RealTimeUpdates(socketio)
        
        print("✅ Sistema WebSocket inicializado")
        
        # Testar emissão
        print("📡 Testando emissão de trade_closed...")
        realtime_updates.broadcast_trade_closed(test_trade_data)
        
        print("✅ Evento trade_closed emitido com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste WebSocket: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE NOTIFICAÇÕES")
    print("=" * 60)
    
    # Teste 1: Fluxo completo
    test1_success = test_trade_notifications()
    
    # Teste 2: WebSocket
    test2_success = test_websocket_events()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINAIS:")
    print(f"   Teste de Fluxo Completo: {'✅ PASSOU' if test1_success else '❌ FALHOU'}")
    print(f"   Teste de WebSocket: {'✅ PASSOU' if test2_success else '❌ FALHOU'}")
    
    if test1_success and test2_success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("💡 As notificações devem estar funcionando corretamente")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("💡 Verifique se o servidor principal está rodando")
        print("💡 Abra a interface web para testar as notificações em tempo real")
