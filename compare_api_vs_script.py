#!/usr/bin/env python3
"""
Comparar sinal gerado via API vs Script
"""

import json
import requests
from datetime import datetime
import sys
import os

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.config import Config
from test_signal_fixed import create_sample_data

def get_api_signal():
    """Obter sinal via API"""
    try:
        url = "http://localhost:5000/api/generate_signal"
        payload = {
            "symbol": "BTCUSDT",
            "timeframe": "1h"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('signal')
            else:
                print(f"❌ API retornou erro: {data.get('message')}")
                return None
        else:
            print(f"❌ API retornou status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao chamar API: {e}")
        return None

def get_script_signal():
    """Obter sinal via script direto"""
    try:        # Configurar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        
        # Criar dados de teste
        symbol = "BTCUSDT"
        df = create_sample_data(symbol)
        
        # Gerar sinal
        result = ai_engine.predict_signal(symbol, df)
        
        if result and isinstance(result, dict):
            # Simular estrutura similar à API
            current_price = df['close'].iloc[-1]
            
            # Converter para formato similar ao sinal da API
            signal_data = {
                'signal_type': result.get('signal'),
                'confidence': result.get('confidence'),
                'entry_price': current_price,
                'symbol': symbol,
                'timeframe': '1h',
                'timestamp': datetime.now().isoformat(),
                'reasons': [result.get('reason', 'IA prediction')],
                'script_details': result  # Incluir dados completos do script
            }
            
            return signal_data
        else:
            print(f"❌ Script não retornou sinal válido: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Erro no script: {e}")
        return None

def compare_signals(api_signal, script_signal):
    """Comparar os dois sinais"""
    print("\n" + "="*60)
    print("🔍 COMPARAÇÃO API vs SCRIPT")
    print("="*60)
    
    if not api_signal:
        print("❌ Sinal da API não disponível")
        return
        
    if not script_signal:
        print("❌ Sinal do script não disponível")
        return
    
    print("\n📊 SINAL DA API:")
    print("-"*30)
    print(f"   Tipo: {api_signal.get('signal_type')}")
    print(f"   Confiança: {api_signal.get('confidence', 0):.4f}")
    print(f"   Preço: ${api_signal.get('entry_price', 0):,.2f}")
    print(f"   Timestamp: {api_signal.get('timestamp')}")
    if api_signal.get('reasons'):
        print(f"   Razões: {len(api_signal.get('reasons', []))} motivos")
        for i, reason in enumerate(api_signal.get('reasons', [])[:3], 1):
            print(f"     {i}. {reason}")
    
    print("\n🤖 SINAL DO SCRIPT:")
    print("-"*30)
    print(f"   Tipo: {script_signal.get('signal_type')}")
    print(f"   Confiança: {script_signal.get('confidence', 0):.4f}")
    print(f"   Preço: ${script_signal.get('entry_price', 0):,.2f}")
    print(f"   Timestamp: {script_signal.get('timestamp')}")
    if script_signal.get('script_details'):
        details = script_signal.get('script_details')
        print(f"   Razão IA: {details.get('reason')}")
        print(f"   Features: {details.get('ai_features', 0)}")
        if details.get('signals_breakdown'):
            breakdown = details.get('signals_breakdown')
            print(f"   Breakdown: {breakdown}")
    
    print("\n🔬 ANÁLISE DE DIFERENÇAS:")
    print("-"*30)
    
    # Comparar tipos de sinal
    api_type = api_signal.get('signal_type', '').lower()
    script_type = script_signal.get('signal_type', '').lower()
    
    if api_type == script_type:
        print(f"   ✅ Tipo de sinal IDÊNTICO: {api_type}")
    else:
        print(f"   ❌ Tipo de sinal DIFERENTE: API={api_type} vs Script={script_type}")
    
    # Comparar confiança
    api_conf = api_signal.get('confidence', 0)
    script_conf = script_signal.get('confidence', 0)
    conf_diff = abs(api_conf - script_conf)
    
    if conf_diff < 0.01:  # Diferença menor que 1%
        print(f"   ✅ Confiança SIMILAR: {conf_diff:.4f} diferença")
    else:
        print(f"   ⚠️ Confiança DIFERENTE: {conf_diff:.4f} diferença")
    
    # Comparar preços
    api_price = api_signal.get('entry_price', 0)
    script_price = script_signal.get('entry_price', 0)
    price_diff = abs(api_price - script_price)
    price_diff_pct = (price_diff / max(api_price, script_price)) * 100 if max(api_price, script_price) > 0 else 0
    
    if price_diff_pct < 0.1:  # Diferença menor que 0.1%
        print(f"   ✅ Preço SIMILAR: {price_diff_pct:.4f}% diferença")
    else:
        print(f"   ⚠️ Preço DIFERENTE: {price_diff_pct:.4f}% diferença")
    
    # Análise temporal
    try:
        api_time = datetime.fromisoformat(api_signal.get('timestamp', '').replace('Z', '+00:00'))
        script_time = datetime.fromisoformat(script_signal.get('timestamp', ''))
        time_diff = abs((api_time - script_time).total_seconds())
        
        if time_diff < 60:  # Menos de 1 minuto
            print(f"   ✅ Timestamp PRÓXIMO: {time_diff:.1f}s diferença")
        else:
            print(f"   ⚠️ Timestamp DISTANTE: {time_diff:.1f}s diferença")
    except:
        print(f"   ❓ Não foi possível comparar timestamps")
    
    print("\n🎯 CONCLUSÃO:")
    print("-"*30)
    
    # Determinar se são equivalentes
    same_signal = api_type == script_type
    similar_confidence = conf_diff < 0.05  # 5% de tolerância
    similar_price = price_diff_pct < 1.0   # 1% de tolerância
    
    if same_signal and similar_confidence and similar_price:
        print("   ✅ SINAIS SÃO EQUIVALENTES!")
        print("   💡 API e Script usam a mesma lógica de IA")
    elif same_signal:
        print("   ⚠️ SINAIS PARCIALMENTE EQUIVALENTES")
        print("   💡 Mesmo tipo, mas pequenas diferenças nos valores")
    else:
        print("   ❌ SINAIS SÃO DIFERENTES!")
        print("   💡 Pode haver diferença na lógica ou dados")

def main():
    print("🚀 INICIANDO COMPARAÇÃO API vs SCRIPT")
    print("Obtendo sinal da API...")
    
    # Obter sinais
    api_signal = get_api_signal()
    
    print("Obtendo sinal do script...")
    script_signal = get_script_signal()
    
    # Comparar
    compare_signals(api_signal, script_signal)
    
    # Salvar dados para análise
    comparison_data = {
        'timestamp': datetime.now().isoformat(),
        'api_signal': api_signal,
        'script_signal': script_signal
    }
    
    with open('comparison_results.json', 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Dados salvos em: comparison_results.json")

if __name__ == "__main__":
    main()
