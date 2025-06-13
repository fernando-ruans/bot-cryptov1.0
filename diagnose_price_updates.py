#!/usr/bin/env python3
"""
Diagnóstico de problemas com atualizações de preços
"""

import requests
import time
import json
from datetime import datetime

def check_price_updates():
    """Verificar se os preços estão sendo atualizados automaticamente"""
    
    print("🔍 DIAGNÓSTICO DE ATUALIZAÇÕES DE PREÇOS")
    print("="*50)
    
    base_url = "http://localhost:5000"
    
    # 1. Verificar status do monitor
    print("\n1. VERIFICANDO STATUS DO MONITOR...")
    try:
        response = requests.get(f"{base_url}/api/monitor/status")
        monitor_status = response.json()
        print(f"   ✅ Monitor status: {monitor_status}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar monitor: {e}")
        return
    
    # 2. Verificar trades ativos
    print("\n2. VERIFICANDO TRADES ATIVOS...")
    try:
        response = requests.get(f"{base_url}/api/paper_trading/portfolio")
        portfolio = response.json()
        active_trades = portfolio.get('active_trades', [])
        
        if not active_trades:
            print("   ❓ Nenhum trade ativo para monitorar")
            return
            
        print(f"   ✅ {len(active_trades)} trades ativos encontrados")
        
        # Guardar preços iniciais
        initial_prices = {}
        for trade in active_trades:
            symbol = trade['symbol']
            price = trade['current_price']
            initial_prices[symbol] = price
            print(f"      {symbol}: ${price:,.2f} (PnL: {trade['pnl_percent']:.2f}%)")
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar trades: {e}")
        return
    
    # 3. Monitorar por 2 minutos
    print(f"\n3. MONITORANDO ATUALIZAÇÕES POR 2 MINUTOS...")
    print("   (O monitor deveria atualizar a cada 30 segundos)")
    
    start_time = datetime.now()
    check_count = 0
    update_count = 0
    
    while (datetime.now() - start_time).total_seconds() < 120:  # 2 minutos
        time.sleep(10)  # Verificar a cada 10 segundos
        check_count += 1
        
        try:
            response = requests.get(f"{base_url}/api/paper_trading/portfolio")
            portfolio = response.json()
            current_trades = portfolio.get('active_trades', [])
            
            print(f"\n   🔍 Verificação #{check_count} ({datetime.now().strftime('%H:%M:%S')})")
            
            price_changed = False
            for trade in current_trades:
                symbol = trade['symbol']
                current_price = trade['current_price']
                initial_price = initial_prices.get(symbol, 0)
                
                if abs(current_price - initial_price) > 0.01:  # Mudança > 1 centavo
                    price_changed = True
                    update_count += 1
                    print(f"      ✅ {symbol}: ${initial_price:,.2f} → ${current_price:,.2f}")
                    initial_prices[symbol] = current_price  # Atualizar referência
                else:
                    print(f"      ➖ {symbol}: ${current_price:,.2f} (sem mudança)")
            
            if not price_changed:
                print("      ⚠️ Nenhum preço mudou desde a última verificação")
                
        except Exception as e:
            print(f"      ❌ Erro na verificação: {e}")
    
    # 4. Resultado final
    print(f"\n4. RESULTADO DO DIAGNÓSTICO:")
    print("-"*30)
    print(f"   Verificações realizadas: {check_count}")
    print(f"   Atualizações detectadas: {update_count}")
    
    if update_count > 0:
        print("   ✅ PREÇOS ESTÃO SENDO ATUALIZADOS")
        print("   💡 O sistema está funcionando normalmente")
    else:
        print("   ❌ PREÇOS NÃO ESTÃO SENDO ATUALIZADOS")
        print("   💡 Possíveis causas:")
        print("      - Monitor parou de funcionar")
        print("      - API de preços com problema")
        print("      - Preços realmente estáveis (raro)")
        
        # Tentar forçar atualização
        print("\n   🔧 TENTANDO FORÇAR ATUALIZAÇÃO...")
        try:
            response = requests.post(f"{base_url}/api/paper_trading/update_prices")
            result = response.json()
            print(f"      ✅ Resultado: {result.get('message', 'OK')}")
        except Exception as e:
            print(f"      ❌ Erro ao forçar atualização: {e}")

if __name__ == "__main__":
    check_price_updates()
