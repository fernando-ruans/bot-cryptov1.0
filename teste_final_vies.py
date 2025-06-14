#!/usr/bin/env python3
"""
Teste da estrutura correta da API
"""

import requests
import json

def test_single():
    """Teste simples"""
    print("🔬 TESTE SIMPLES")
    print("=" * 30)
    
    try:
        response = requests.post(
            "http://localhost:5000/api/generate_signal",
            json={"symbol": "BTCUSDT", "timeframe": "1h"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            signal_obj = data.get('signal', {})
            signal_type = signal_obj.get('signal_type')
            confidence = signal_obj.get('confidence', 0)
            
            print(f"Signal: {signal_type}")
            print(f"Confidence: {confidence:.1f}%")
            
            reasons = signal_obj.get('reasons', [])
            print(f"Reasons: {len(reasons)}")
            for reason in reasons[:3]:  # Primeiras 3
                print(f"  - {reason}")
        else:
            print(f"Erro: {response.status_code}")
    
    except Exception as e:
        print(f"Erro: {e}")

def test_multiple():
    """Teste múltiplo"""
    print(f"\n🎲 TESTE MÚLTIPLO")
    print("=" * 30)
    
    tests = [
        ("BTCUSDT", "1h"),
        ("ETHUSDT", "1h"), 
        ("BTCUSDT", "5m"),
        ("ETHUSDT", "5m")
    ]
    
    results = []
    
    for symbol, tf in tests:
        try:
            response = requests.post(
                "http://localhost:5000/api/generate_signal",
                json={"symbol": symbol, "timeframe": tf},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                signal_obj = data.get('signal', {})
                signal_type = signal_obj.get('signal_type', 'UNKNOWN')
                confidence = signal_obj.get('confidence', 0)
                
                results.append(signal_type)
                print(f"{symbol} {tf}: {signal_type} ({confidence:.1f}%)")
            else:
                print(f"{symbol} {tf}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"{symbol} {tf}: {e}")
    
    # Estatísticas
    if results:
        unique = set(results)
        print(f"\n📊 RESULTADOS:")
        print(f"Total: {len(results)}")
        for signal in unique:
            count = results.count(signal)
            pct = (count/len(results))*100
            print(f"{signal}: {count} ({pct:.1f}%)")

if __name__ == "__main__":
    test_single()
    test_multiple()
