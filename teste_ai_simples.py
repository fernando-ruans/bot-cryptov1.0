#!/usr/bin/env python3
"""
Teste focado para identificar exatamente o que a IA está retornando
"""

import requests
import json

def test_ai_direct_output():
    """Testa diretamente o que a IA está retornando"""
    
    print("🔬 TESTE DIRETO DA SAÍDA DA IA")
    print("=" * 50)
    
    # Fazer um request simples
    try:
        response = requests.post(
            "http://localhost:5000/api/generate_signal",
            json={
                "symbol": "BTCUSDT",
                "timeframe": "1h"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("📋 DADOS RETORNADOS PELA API:")
            for key, value in data.items():
                print(f"  {key}: {value}")
              # Verificar especificamente o signal_type
            signal_obj = data.get('signal', {})
            signal_type = signal_obj.get('signal_type')
            print(f"\n🎯 SIGNAL_TYPE: '{signal_type}'")
            
            # Verificar as razões
            reasons = signal_obj.get('reasons', [])
            print(f"\n📝 RAZÕES ({len(reasons)}):")
            for i, reason in enumerate(reasons):
                print(f"  {i+1}. {reason}")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_multiple_quick():
    """Teste rápido com múltiplos ativos"""
    
    print(f"\n🎲 TESTE RÁPIDO - MÚLTIPLOS ATIVOS")
    print("=" * 50)
    
    ativos = ["BTCUSDT", "ETHUSDT"]
    timeframes = ["1h"]
    
    results = []
    
    for ativo in ativos:
        for tf in timeframes:
            try:
                response = requests.post(
                    "http://localhost:5000/api/generate_signal",
                    json={"symbol": ativo, "timeframe": tf},
                    timeout=15
                )
                  if response.status_code == 200:
                    data = response.json()
                    signal_obj = data.get('signal', {})
                    signal = signal_obj.get('signal_type', 'UNKNOWN')
                    confidence = signal_obj.get('confidence', 0)
                    
                    results.append({
                        'ativo': ativo,
                        'timeframe': tf,
                        'signal': signal,
                        'confidence': confidence
                    })
                    
                    print(f"  {ativo} {tf}: {signal} ({confidence:.1f}%)")
                
            except Exception as e:
                print(f"  {ativo} {tf}: ERRO - {e}")
    
    # Análise dos resultados
    if results:
        signals = [r['signal'] for r in results]
        unique_signals = set(signals)
        
        print(f"\n📊 RESUMO:")
        print(f"  Total de testes: {len(results)}")
        print(f"  Sinais únicos: {unique_signals}")
        
        for signal in unique_signals:
            count = signals.count(signal)
            percentage = (count / len(signals)) * 100
            print(f"  {signal}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    test_ai_direct_output()
    test_multiple_quick()
