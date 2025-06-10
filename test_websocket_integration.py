#!/usr/bin/env python3
"""
Teste da integração WebSocket - Sistema de preços em tempo real
Testa se o sistema de preços está conectado ao WebSocket corretamente
"""

import sys
import os
sys.path.append(os.getcwd())

import time
import requests
import threading
from src.realtime_price_api import realtime_price_api
from src.realtime_updates import RealTimeUpdates
from flask_socketio import SocketIO
from flask import Flask

def test_websocket_integration():
    """Teste da integração do sistema de preços com WebSocket"""
    print("🚀 TESTE DE INTEGRAÇÃO WEBSOCKET")
    print("=" * 50)
    
    # 1. Testar instância da API de preços
    print("\n1. TESTANDO API DE PREÇOS:")
    print(f"   ✅ RealTimePriceAPI instanciada: {realtime_price_api}")
    print(f"   🔄 Status running: {realtime_price_api.running}")
    print(f"   📊 Callbacks registrados: {len(realtime_price_api.callbacks)}")
    
    # 2. Testar callback system
    print("\n2. TESTANDO SISTEMA DE CALLBACKS:")
    
    callback_triggered = False
    received_symbol = None
    received_price = None
    
    def test_callback(symbol: str, price: float):
        nonlocal callback_triggered, received_symbol, received_price
        callback_triggered = True
        received_symbol = symbol
        received_price = price
        print(f"   📈 Callback acionado: {symbol} = ${price:.2f}")
    
    # Adicionar callback de teste
    realtime_price_api.add_callback(test_callback)
    print(f"   ✅ Callback de teste adicionado")
    print(f"   📊 Total de callbacks: {len(realtime_price_api.callbacks)}")
    
    # 3. Testar notificação manual
    print("\n3. TESTANDO NOTIFICAÇÃO MANUAL:")
    try:
        # Simular uma atualização de preço manual
        realtime_price_api._notify_price_update("BTCUSDT", 106000.50)
        
        # Aguardar um pouco para callback
        time.sleep(0.1)
        
        if callback_triggered:
            print(f"   ✅ Callback funcionando: {received_symbol} = ${received_price}")
        else:
            print("   ❌ Callback não foi acionado")
            
    except Exception as e:
        print(f"   ❌ Erro no teste manual: {e}")
    
    # 4. Testar integração com main.py (se disponível)
    print("\n4. TESTANDO INTEGRAÇÃO MAIN.PY:")
    try:
        from main import sync_active_trade_symbols, price_update_callback
        
        print("   ✅ Funções de integração importadas")
        print(f"   ✅ sync_active_trade_symbols: {sync_active_trade_symbols}")
        print(f"   ✅ price_update_callback: {price_update_callback}")
        
        # Testar callback de integração
        print("\n   🧪 Testando callback de integração:")
        try:
            price_update_callback("ETHUSDT", 4100.25)
            print("   ✅ Callback de integração funcionou")
        except Exception as cb_error:
            print(f"   ❌ Erro no callback de integração: {cb_error}")
            
    except ImportError as import_error:
        print(f"   ⚠️ Não foi possível importar do main.py: {import_error}")
        print("   💡 Execute este teste após iniciar o sistema principal")
    
    # 5. Testar status do sistema
    print("\n5. STATUS DO SISTEMA:")
    try:
        # Verificar cache de preços
        print(f"   📊 Preços em cache: {len(realtime_price_api.price_cache)}")
        
        if realtime_price_api.price_cache:
            print("   💰 Últimos preços:")
            for symbol, data in list(realtime_price_api.price_cache.items())[:3]:
                print(f"      📈 {symbol}: ${data['price']:.2f} ({data['source']})")
        
        # Status da API
        print(f"   🔄 Sistema rodando: {realtime_price_api.running}")
        print(f"   🧵 WebSocket thread: {realtime_price_api.websocket_thread}")
        print(f"   🧵 REST thread: {realtime_price_api.rest_thread}")
        
    except Exception as status_error:
        print(f"   ❌ Erro ao verificar status: {status_error}")
    
    # 6. Teste de sincronização
    print("\n6. TESTE DE SINCRONIZAÇÃO:")
    if not realtime_price_api.running:
        try:
            print("   🚀 Iniciando sistema de preços...")
            realtime_price_api.start()
            time.sleep(2)  # Aguardar inicialização
            
            print(f"   ✅ Sistema iniciado: {realtime_price_api.running}")
            
        except Exception as start_error:
            print(f"   ❌ Erro ao iniciar sistema: {start_error}")
    
    # 7. Testar preços em tempo real
    print("\n7. TESTE DE PREÇOS EM TEMPO REAL:")
    try:
        # Aguardar alguns segundos para receber dados
        print("   ⏳ Aguardando dados em tempo real (5s)...")
        initial_cache_size = len(realtime_price_api.price_cache)
        
        time.sleep(5)
        
        final_cache_size = len(realtime_price_api.price_cache)
        
        if final_cache_size > initial_cache_size:
            print(f"   ✅ Novos preços recebidos: {initial_cache_size} → {final_cache_size}")
            
            # Mostrar alguns preços recentes
            print("   💰 Preços atualizados:")
            for symbol, data in list(realtime_price_api.price_cache.items())[:5]:
                age = (time.time() - data['timestamp'].timestamp()) if hasattr(data['timestamp'], 'timestamp') else 0
                print(f"      📈 {symbol}: ${data['price']:.2f} (há {age:.1f}s)")
                
        else:
            print(f"   ⚠️ Nenhum preço novo recebido")
            
    except Exception as realtime_error:
        print(f"   ❌ Erro no teste de tempo real: {realtime_error}")
    
    # Cleanup
    print("\n8. LIMPEZA:")
    try:
        realtime_price_api.remove_callback(test_callback)
        print("   ✅ Callback de teste removido")
    except Exception as cleanup_error:
        print(f"   ⚠️ Erro na limpeza: {cleanup_error}")
    
    print("\n" + "=" * 50)
    print("🎉 TESTE DE INTEGRAÇÃO CONCLUÍDO")
    print("\n📋 RESUMO:")
    print(f"   🔄 Sistema rodando: {realtime_price_api.running}")
    print(f"   📊 Preços em cache: {len(realtime_price_api.price_cache)}")
    print(f"   🔗 Callbacks ativos: {len(realtime_price_api.callbacks)}")
    
    if callback_triggered:
        print("   ✅ Sistema de callbacks funcionando")
    else:
        print("   ⚠️ Sistema de callbacks não testado")
    
    print("\n💡 Para teste completo, execute o sistema principal (main.py)")

if __name__ == "__main__":
    test_websocket_integration()
