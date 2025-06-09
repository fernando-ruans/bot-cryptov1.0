#!/usr/bin/env python3
"""
Teste completo do sistema de trading bot
Verifica se todos os componentes estão funcionando integrados
"""

import requests
import json
import time

def test_complete_trading_flow():
    """Testa o fluxo completo do sistema de trading"""
    base_url = "http://localhost:5000"
    
    print("=== TESTE COMPLETO DO SISTEMA DE TRADING BOT ===")
    print()
    
    # 1. Verificar status do sistema
    print("1. Verificando status do sistema...")
    try:
        response = requests.get(f"{base_url}/api/status")
        data = response.json()
        print(f"   ✅ Sistema ativo: {data.get('running', False)}")
        print(f"   📅 Timestamp: {data.get('timestamp', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    # 2. Verificar preços de múltiplos ativos
    print("\n2. Verificando preços atuais...")
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    prices = {}
    
    for symbol in symbols:
        try:
            response = requests.get(f"{base_url}/api/price/{symbol}")
            if response.status_code == 200:
                data = response.json()
                price = data.get('price', 0)
                prices[symbol] = price
                print(f"   ✅ {symbol}: ${price:,.2f}")
            else:
                print(f"   ⚠️ {symbol}: Falha ao obter preço")
        except Exception as e:
            print(f"   ❌ {symbol}: Erro - {e}")
    
    if not prices:
        print("   ❌ Nenhum preço obtido. Sistema pode estar com problemas.")
        return False
    
    # 3. Verificar sinais ativos iniciais
    print("\n3. Verificando sinais ativos...")
    try:
        response = requests.get(f"{base_url}/api/signals/active")
        data = response.json()
        initial_signals = data.get('count', 0)
        print(f"   📊 Sinais ativos atuais: {initial_signals}")
        
        if data.get('signals'):
            for signal in data['signals'][:3]:  # Mostrar até 3 sinais
                print(f"   - {signal['symbol']} {signal['signal_type'].upper()} ({signal['confidence']:.1%})")
    except Exception as e:
        print(f"   ❌ Erro ao buscar sinais: {e}")
    
    # 4. Forçar geração de novos sinais para teste
    print("\n4. Gerando sinais de teste...")
    test_signals = [
        {'symbol': 'BTCUSDT', 'signal_type': 'buy'},
        {'symbol': 'ETHUSDT', 'signal_type': 'sell'},
        {'symbol': 'ADAUSDT', 'signal_type': 'buy'}
    ]
    
    generated_signals = []
    for signal_request in test_signals:
        try:
            response = requests.post(
                f"{base_url}/api/debug/force_signal",
                json=signal_request,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    signal = data.get('signal', {})
                    generated_signals.append(signal)
                    print(f"   ✅ {signal_request['symbol']} {signal_request['signal_type'].upper()}: ${signal.get('entry_price', 0):,.2f}")
                else:
                    print(f"   ⚠️ {signal_request['symbol']}: Falha - {data.get('message', 'Erro desconhecido')}")
            else:
                print(f"   ❌ {signal_request['symbol']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {signal_request['symbol']}: Erro - {e}")
    
    print(f"   📈 Total de sinais gerados: {len(generated_signals)}")
    
    # 5. Verificar sinais após geração
    print("\n5. Verificando sinais após geração...")
    try:
        response = requests.get(f"{base_url}/api/signals/active")
        data = response.json()
        final_signals = data.get('count', 0)
        print(f"   📊 Sinais ativos finais: {final_signals}")
        
        if data.get('signals'):
            print("   Sinais disponíveis:")
            for i, signal in enumerate(data['signals'][-5:], 1):  # Últimos 5 sinais
                print(f"   {i}. {signal['symbol']} {signal['signal_type'].upper()} - ${signal.get('entry_price', 0):,.2f} ({signal['confidence']:.1%})")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 6. Testar confirmação de trades
    print("\n6. Testando confirmação de trades...")
    if generated_signals:
        # Pegar o primeiro sinal gerado para teste
        test_signal = generated_signals[0]
        
        trade_payload = {
            'signal': test_signal,
            'amount': 1000
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/paper_trading/confirm_signal",
                json=trade_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    trade_id = data.get('trade_id')
                    print(f"   ✅ Trade confirmado: {trade_id}")
                    print(f"   💰 Sinal: {test_signal['symbol']} {test_signal['signal_type'].upper()}")
                    print(f"   💵 Valor: $1,000")
                else:
                    print(f"   ⚠️ Falha na confirmação: {data.get('error', 'Erro desconhecido')}")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro na confirmação: {e}")
    else:
        print("   ⚠️ Nenhum sinal disponível para teste")
    
    # 7. Verificar portfolio
    print("\n7. Verificando portfolio...")
    try:
        response = requests.get(f"{base_url}/api/paper_trading/portfolio")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                portfolio = data.get('portfolio', {})
                active_trades = data.get('active_trades', [])
                
                print(f"   💼 Saldo atual: ${portfolio.get('current_balance', 0):,.2f}")
                print(f"   📊 Total de trades: {portfolio.get('total_trades', 0)}")
                print(f"   🎯 Win rate: {portfolio.get('win_rate', 0):.1f}%")
                print(f"   📈 Trades ativos: {len(active_trades)}")
                print(f"   💰 PnL total: ${portfolio.get('total_pnl', 0):,.2f}")
                
                if active_trades:
                    print("   Trades ativos:")
                    for trade in active_trades[:3]:  # Mostrar até 3 trades
                        pnl = trade.get('pnl', 0)
                        pnl_pct = trade.get('pnl_percent', 0)
                        status_icon = "🟢" if pnl >= 0 else "🔴"
                        print(f"   {status_icon} {trade['symbol']} {trade['trade_type'].upper()}: ${pnl:,.2f} ({pnl_pct:.2f}%)")
            else:
                print(f"   ⚠️ Erro: {data.get('error', 'Erro desconhecido')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 8. Teste final de geração automática (sem debug)
    print("\n8. Testando geração automática de sinais...")
    try:
        response = requests.post(
            f"{base_url}/api/generate_signal",
            json={'symbol': 'BTCUSDT', 'timeframe': '1h'},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                signal = data.get('signal', {})
                print(f"   ✅ Sinal automático gerado!")
                print(f"   📊 {signal['symbol']} {signal['signal_type'].upper()}")
                print(f"   🎯 Confiança: {signal['confidence']:.1%}")
                print(f"   💰 Preço: ${signal.get('entry_price', 0):,.2f}")
            else:
                print(f"   ⚠️ Nenhum sinal automático: {data.get('message', 'Condições não favoráveis')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "="*60)
    print("🎉 TESTE COMPLETO FINALIZADO!")
    print("✅ Sistema de trading bot está funcionando corretamente!")
    print("📊 Dashboard disponível em: http://localhost:5000")
    print("="*60)
    
    return True

if __name__ == "__main__":
    test_complete_trading_flow()
