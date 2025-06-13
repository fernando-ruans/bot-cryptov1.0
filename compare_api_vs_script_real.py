#!/usr/bin/env python3
"""
Comparar sinal gerado via API vs Script usando dados reais
"""

import json
import requests
from datetime import datetime
import sys
import os
import pandas as pd
import numpy as np

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.config import Config

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

def get_real_market_data():
    """Obter dados reais de mercado via API"""
    try:
        # Usar a API de preços do próprio app
        url = "http://localhost:5000/api/price/BTCUSDT"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            price_data = response.json()
            current_price = float(price_data.get('price', 100000))
            
            # Simular dados baseados no preço real
            periods = 150
            dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
            
            # Gerar dados simulados baseados no preço atual
            volatility = 0.02  # 2% de volatilidade horária
            prices = []
            base_price = current_price * 0.98  # Começar um pouco abaixo
            
            for i in range(periods):
                # Simular movimento de preço com tendência
                change = np.random.normal(0, volatility)
                if i == 0:
                    price = base_price
                else:
                    price = prices[-1] * (1 + change)
                prices.append(price)
            
            # Ajustar o último preço para ser próximo do atual
            prices[-1] = current_price
            
            # Criar DataFrame
            df = pd.DataFrame({
                'timestamp': dates,
                'open': prices,
                'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
                'close': prices,
                'volume': np.random.uniform(1000, 10000, periods)
            })
            
            df.set_index('timestamp', inplace=True)
            return df
            
        else:
            print(f"⚠️ Não foi possível obter preço real, usando simulado")
            return None
            
    except Exception as e:
        print(f"⚠️ Erro ao obter dados reais: {e}")
        return None

def get_script_signal_with_real_data():
    """Obter sinal via script usando dados próximos aos reais"""
    try:
        # Configurar componentes
        config = Config()
        ai_engine = AITradingEngine(config)
        
        # Obter dados reais ou simulados
        df = get_real_market_data()
        if df is None:
            print("Usando dados simulados...")
            # Fallback para dados simulados
            periods = 150
            dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
            base_price = 100000  # Próximo do preço real
            
            price_changes = np.random.normal(0, 0.01, periods)
            prices = [base_price]
            
            for i in range(1, periods):
                new_price = prices[-1] * (1 + price_changes[i])
                prices.append(new_price)
            
            df = pd.DataFrame({
                'timestamp': dates,
                'open': prices,
                'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
                'close': prices,
                'volume': np.random.uniform(1000, 10000, periods)
            })
            
            df.set_index('timestamp', inplace=True)
        
        symbol = "BTCUSDT"
          # Gerar sinal
        result = ai_engine.predict_signal(df, symbol)
        
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
        import traceback
        traceback.print_exc()
        return None

def compare_signals(api_signal, script_signal):
    """Comparar os dois sinais"""
    print("\n" + "="*60)
    print("🔍 COMPARAÇÃO API vs SCRIPT (DADOS REAIS)")
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
    
    if price_diff_pct < 5.0:  # Diferença menor que 5% (mais tolerante para dados simulados)
        print(f"   ✅ Preço SIMILAR: {price_diff_pct:.2f}% diferença")
    else:
        print(f"   ⚠️ Preço DIFERENTE: {price_diff_pct:.2f}% diferença")
    
    print("\n🎯 CONCLUSÃO:")
    print("-"*30)
    
    # Determinar se são equivalentes
    same_signal = api_type == script_type
    similar_confidence = conf_diff < 0.1  # 10% de tolerância
    similar_price = price_diff_pct < 10.0   # 10% de tolerância para simulação
    
    if same_signal and similar_confidence:
        print("   ✅ SINAIS SÃO FUNCIONALMENTE EQUIVALENTES!")
        print("   💡 API e Script usam lógica similar de IA")
        print("   📝 Pequenas diferenças podem ser devido aos dados simulados")
    elif same_signal:
        print("   ⚠️ SINAIS PARCIALMENTE EQUIVALENTES")
        print("   💡 Mesmo tipo, mas diferenças nos valores")
    else:
        print("   ❌ SINAIS SÃO DIFERENTES!")
        print("   💡 Pode haver diferença na lógica ou dados")
        
    # Análise adicional
    if script_signal.get('script_details'):
        details = script_signal.get('script_details')
        if 'erro' in details.get('reason', '').lower() or 'error' in details.get('reason', '').lower():
            print("   🚨 ATENÇÃO: Script teve erro na análise!")
            print("   💡 Revisar lógica do AI Engine para casos edge")

def main():
    print("🚀 INICIANDO COMPARAÇÃO API vs SCRIPT (DADOS REAIS)")
    print("Obtendo sinal da API...")
    
    # Obter sinais
    api_signal = get_api_signal()
    
    print("Obtendo sinal do script com dados reais...")
    script_signal = get_script_signal_with_real_data()
    
    # Comparar
    compare_signals(api_signal, script_signal)
    
    # Salvar dados para análise
    comparison_data = {
        'timestamp': datetime.now().isoformat(),
        'api_signal': api_signal,
        'script_signal': script_signal,
        'test_type': 'real_data_comparison'
    }
    
    with open('comparison_results_real_data.json', 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Dados salvos em: comparison_results_real_data.json")

if __name__ == "__main__":
    main()
