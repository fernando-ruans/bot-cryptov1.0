#!/usr/bin/env python3
"""
Debug detalhado do endpoint após correção do cooldown
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_endpoint_detailed():
    """Teste detalhado do endpoint com análise de resposta"""
    print("🔍 DEBUG DETALHADO DO ENDPOINT")
    print("=" * 50)
    
    url = "http://localhost:5000/api/generate_signal"
    payload = {"symbol": "BTCUSDT", "timeframe": "1h"}
    
    print(f"🎯 URL: {url}")
    print(f"📊 Payload: {payload}")
    print()
    
    for i in range(1, 4):
        print(f"📞 TESTE {i}/3")
        print(f"   ⏰ {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        
        try:
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=30)
            duration = time.time() - start_time
            
            print(f"   ⚡ Duração: {duration:.3f}s")
            print(f"   📈 Status: {response.status_code}")
            
            # Analisar response detalhadamente
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📋 Response JSON: {json.dumps(data, indent=2)}")
                    
                    if data.get('success'):
                        signal = data.get('signal', {})
                        print(f"   ✅ SUCESSO!")
                        print(f"      Signal Type: {signal.get('signal_type')}")
                        print(f"      Confidence: {signal.get('confidence')}")
                        print(f"      Entry Price: {signal.get('entry_price')}")
                        print(f"      Stop Loss: {signal.get('stop_loss')}")
                        print(f"      Take Profit: {signal.get('take_profit')}")
                    else:
                        print(f"   ❌ FALHA na resposta:")
                        print(f"      Success: {data.get('success')}")
                        print(f"      Error: {data.get('error')}")
                        print(f"      Message: {data.get('message')}")
                        print(f"      Signal: {data.get('signal')}")
                        
                except json.JSONDecodeError as e:
                    print(f"   💥 ERRO JSON: {e}")
                    print(f"   📄 Raw response: {response.text[:500]}")
            else:
                print(f"   ❌ Status HTTP {response.status_code}")
                print(f"   📄 Response: {response.text[:300]}")
        
        except Exception as e:
            print(f"   💥 ERRO: {e}")
        
        print()
        
        if i < 3:
            time.sleep(1)  # 1 segundo entre testes

def test_direct_generation():
    """Teste de geração direta para comparação"""
    print("🔧 TESTE DIRETO PARA COMPARAÇÃO")
    print("=" * 40)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.ai_engine import AITradingEngine
        from src.signal_generator import SignalGenerator
        
        # Configurar logging para ver detalhes
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        print(f"   📊 Config cooldown: {config.SIGNAL_CONFIG['signal_cooldown_minutes']}")
        print(f"   📊 Config min_confidence: {config.SIGNAL_CONFIG['min_confidence']}")
        print()
        
        for i in range(1, 4):
            print(f"🔧 Execução Direta {i}/3")
            
            # Verificar cooldown antes
            is_cooldown = signal_generator._is_in_cooldown('BTCUSDT')
            print(f"   ⏱️ Em cooldown: {is_cooldown}")
            
            start_time = time.time()
            signal = signal_generator.generate_signal('BTCUSDT', '1h')
            duration = time.time() - start_time
            
            print(f"   ⚡ Duração: {duration:.3f}s")
            
            if signal:
                print(f"   ✅ SUCESSO: {signal.signal_type} ({signal.confidence:.2%})")
                print(f"      Entry: ${signal.entry_price:.2f}")
                print(f"      SL: ${signal.stop_loss:.2f}")
                print(f"      TP: ${signal.take_profit:.2f}")
            else:
                print(f"   ❌ FALHA: Nenhum sinal gerado")
            
            print()
            
            if i < 3:
                time.sleep(1)
    
    except Exception as e:
        print(f"💥 Erro no teste direto: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 DEBUG ENDPOINT PÓS-CORREÇÃO COOLDOWN")
    print("=" * 60)
    
    # Verificar servidor
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print("✅ Servidor Flask está rodando")
    except:
        print("❌ Servidor Flask não está rodando!")
        sys.exit(1)
    
    print()
    
    # Teste endpoint
    test_endpoint_detailed()
    
    # Teste direto para comparação
    test_direct_generation()
    
    print("🎉 DEBUG CONCLUÍDO!")
