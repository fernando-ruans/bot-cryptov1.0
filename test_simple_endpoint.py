#!/usr/bin/env python3
"""
Teste simples de endpoint
"""

import requests
import json

def test_simple():
    try:
        print("🔍 Teste simples do endpoint")
        response = requests.post(
            "http://localhost:5000/api/generate_signal",
            json={"symbol": "BTCUSDT", "timeframe": "1h"},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON: {json.dumps(data, indent=2)}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_simple()
