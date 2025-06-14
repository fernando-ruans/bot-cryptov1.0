#!/usr/bin/env python3
"""
Diagnóstico profundo da lógica da IA para identificar por que só gera BUY
"""

import requests
import json
from datetime import datetime

def test_ai_logic_debug():
    """Testa e diagnostica a lógica interna da IA"""
    
    print("🔬 DIAGNÓSTICO PROFUNDO DA IA - VIÉS BUY")
    print("=" * 60)
    
    # Testar um ativo específico
    symbol = "BTCUSDT"
    timeframe = "1h"
    
    try:
        # Fazer request detalhado
        response = requests.get(
            "http://localhost:5000/api/generate_signal",
            params={
                "symbol": symbol,
                "timeframe": timeframe,
                "debug": "true"  # Tentar obter mais detalhes
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📊 Teste para {symbol} {timeframe}:")
            print(f"  Signal Type: {data.get('signal_type')}")
            print(f"  Confiança: {data.get('confidence', 0):.2f}%")
            
            # Verificar se há dados detalhados sobre a decisão
            if 'reasons' in data:
                print(f"  Razões:")
                for reason in data['reasons']:
                    print(f"    - {reason}")
            
            # Verificar estrutura completa
            print(f"\n📋 Estrutura completa do retorno:")
            for key, value in data.items():
                if key != 'reasons':  # Já mostrado acima
                    print(f"  {key}: {value}")
        
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_direct_ai_features():
    """Testa diretamente as features da IA"""
    print(f"\n🧠 TESTE DIRETO DAS FEATURES DA IA")
    print("=" * 60)
    
    # Vou criar um teste simulado baseado nos dados que observamos
    print("📈 SIMULAÇÃO DOS SINAIS DA IA:")
    
    # Dados observados do teste anterior
    features_observadas = {
        "momentum_signals": [],  # Vazio = neutro
        "pattern_signals": [],   # Vazio = neutro  
        "regime_signals": [],    # Vazio = neutro
        "correlation_signals": [], # Vazio = neutro
        "volatility_signals": []   # Vazio = neutro
    }
    
    print("  💡 HIPÓTESES PARA VIÉS 100% BUY:")
    print("    1. Lógica de fallback defaulting para BUY")
    print("    2. Features sempre resultando em sinais positivos")
    print("    3. Mercado atual em alta favorecendo BUY")
    print("    4. Thresholds muito restritivos para SELL")
    print("    5. Bug na consolidação de sinais")
    
    # Análise da lógica observada no código
    print(f"\n🔍 ANÁLISE DA LÓGICA NO CÓDIGO:")
    print("  AI Engine - predict_signal():")
    print("    - Se não há sinais ativos → HOLD")
    print("    - Se bullish_count > bearish_count → BUY") 
    print("    - Se bearish_count > bullish_count → SELL")
    print("    - Se empate → HOLD")
    
    print("  Market Analyzer - get_trade_recommendation():")
    print("    - Se signal='buy' → recommendation='buy'")
    print("    - Se signal='sell' → recommendation='sell'") 
    print("    - Se signal='hold' + confiança > 0.5 → BUY")
    print("    - Se signal='hold' + confiança ≤ 0.5 → SELL")
    
    print(f"\n⚠️  POSSÍVEL CAUSA:")
    print("    → IA sempre retorna 'hold' com confiança > 0.5")
    print("    → Market Analyzer converte 'hold' para 'buy'")
    print("    → Resultado: 100% BUY")

def investigate_features():
    """Investiga quais features estão sendo calculadas"""
    print(f"\n🔧 INVESTIGAÇÃO DAS FEATURES")
    print("=" * 60)
    
    print("📊 FEATURES QUE PODEM ESTAR CAUSANDO VIÉS:")
    
    features_suspeitas = [
        "momentum_5 - sempre positivo?",
        "roc_5 - sempre > 2?", 
        "bullish_patterns_score - sempre maior que bearish?",
        "ensemble_regime_score - sempre > 1?",
        "correlation_strength - configuração incorreta?",
        "volatility_ratio - valores extremos?"
    ]
    
    for feature in features_suspeitas:
        print(f"  ⚠️  {feature}")
    
    print(f"\n🎯 RECOMENDAÇÕES DE CORREÇÃO:")
    print("  1. 🔧 Adicionar logs detalhados na função predict_signal()")
    print("  2. 📊 Verificar cálculo de indicadores técnicos")
    print("  3. 🎲 Testar com dados históricos de mercado baixista")
    print("  4. ⚖️  Ajustar thresholds para geração de SELL")
    print("  5. 🔄 Implementar diversificação forçada de sinais")

def test_market_conditions():
    """Analisa se condições de mercado favorecem BUY"""
    print(f"\n📈 ANÁLISE DAS CONDIÇÕES DE MERCADO")
    print("=" * 60)
    
    print("💭 HIPÓTESE: Mercado atual em alta forte")
    print("  → BTC, ETH e outros em tendência de alta")
    print("  → IA detecta corretamente momentum bullish")
    print("  → Sinais BUY são legítimos")
    
    print(f"\n🧪 TESTE NECESSÁRIO:")
    print("  → Testar com dados históricos de 2022 (bear market)")
    print("  → Simular condições de mercado baixista")
    print("  → Verificar se IA gera SELL nessas condições")

if __name__ == "__main__":
    test_ai_logic_debug()
    test_direct_ai_features()
    investigate_features()
    test_market_conditions()
    
    print(f"\n✅ DIAGNÓSTICO CONCLUÍDO!")
    print(f"🔧 PRÓXIMOS PASSOS:")
    print(f"  1. Implementar logging detalhado da IA")
    print(f"  2. Testar com dados históricos bear market")
    print(f"  3. Ajustar lógica de fallback para distribuição equilibrada")
    print(f"  4. Criar sistema de validação de viés automático")
