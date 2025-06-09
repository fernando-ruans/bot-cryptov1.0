#!/usr/bin/env python3
"""
Teste do botão web com thresholds reduzidos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator
from src.market_analyzer import MarketAnalyzer
import requests
import json

def test_with_reduced_thresholds():
    """Teste com thresholds reduzidos"""
    
    print("=== TESTE COM THRESHOLDS REDUZIDOS ===")
    
    # 1. Configurar thresholds mais baixos
    config = Config()
    
    # Backup dos valores originais
    original_ai_confidence = config.RISK_MANAGEMENT.get('min_ai_confidence', 0.85)
    original_market_score = config.SIGNAL_CONFIG.get('min_market_score', 0.80)
    original_min_confidence = config.SIGNAL_CONFIG.get('min_confidence', 0.70)
    
    print(f"Thresholds ORIGINAIS:")
    print(f"  - Min AI confidence: {original_ai_confidence}")
    print(f"  - Min market score: {original_market_score}")  
    print(f"  - Min confidence: {original_min_confidence}")
    
    # Definir thresholds mais baixos
    config.RISK_MANAGEMENT['min_ai_confidence'] = 0.40  # Era 0.85
    config.SIGNAL_CONFIG['min_market_score'] = 0.30      # Era 0.80
    config.SIGNAL_CONFIG['min_confidence'] = 0.40        # Era 0.70
    
    print(f"\nThresholds REDUZIDOS:")
    print(f"  - Min AI confidence: {config.RISK_MANAGEMENT['min_ai_confidence']}")
    print(f"  - Min market score: {config.SIGNAL_CONFIG['min_market_score']}")
    print(f"  - Min confidence: {config.SIGNAL_CONFIG['min_confidence']}")
    
    # 2. Testar geração local
    print(f"\n=== TESTE LOCAL COM THRESHOLDS REDUZIDOS ===")
    
    try:
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        ai_engine.load_models()
        signal_gen = SignalGenerator(ai_engine, market_data)
        
        # Limpar cooldown
        signal_gen.last_signal_times = {}
        
        print("Tentando gerar sinal...")
        signal = signal_gen.generate_signal('BTCUSDT')
        
        if signal:
            print("🎯 SINAL GERADO COM SUCESSO!")
            print(f"  Tipo: {signal.signal_type}")
            print(f"  Confiança: {signal.confidence:.2f}")
            print(f"  Entry: ${signal.entry_price:.2f}")
            print(f"  Stop Loss: ${signal.stop_loss:.2f}")
            print(f"  Take Profit: ${signal.take_profit:.2f}")
            if hasattr(signal, 'reasons'):
                print(f"  Razões: {len(signal.reasons)} fatores")
            return True
        else:
            print("❌ Ainda não conseguiu gerar sinal")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste local: {e}")
        return False
    
    finally:
        # Restaurar valores originais
        config.RISK_MANAGEMENT['min_ai_confidence'] = original_ai_confidence
        config.SIGNAL_CONFIG['min_market_score'] = original_market_score
        config.SIGNAL_CONFIG['min_confidence'] = original_min_confidence

def test_web_api():
    """Teste via API web"""
    print(f"\n=== TESTE VIA API WEB ===")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/generate_signal",
            headers={"Content-Type": "application/json"},
            json={"symbol": "BTCUSDT"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('signal'):
                print("🎯 API WEB GEROU SINAL!")
                return True
            else:
                print(f"❌ API web: {result.get('message', 'Nenhum sinal')}")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

if __name__ == "__main__":
    print("Testando geração de sinais com diferentes configurações...")
    
    # Teste local com thresholds reduzidos
    local_success = test_with_reduced_thresholds()
    
    # Teste via API (com configuração do servidor)
    api_success = test_web_api()
    
    print(f"\n🎯 RESULTADOS:")
    print(f"  - Teste local (thresholds baixos): {'✅' if local_success else '❌'}")
    print(f"  - Teste API web (configuração atual): {'✅' if api_success else '❌'}")
    
    if local_success and not api_success:
        print(f"\n💡 DIAGNÓSTICO: Os thresholds do servidor estão muito altos!")
        print(f"   Para resolver, você pode:")
        print(f"   1. Ajustar os thresholds na configuração")
        print(f"   2. Treinar modelos com melhor performance")
        print(f"   3. Aguardar condições de mercado mais favoráveis")
    elif api_success:
        print(f"\n✅ BOTÃO WEB ESTÁ FUNCIONANDO PERFEITAMENTE!")
    else:
        print(f"\n❌ Há um problema mais profundo na geração de sinais")
