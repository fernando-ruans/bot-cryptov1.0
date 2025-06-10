#!/usr/bin/env python3
"""
Script para debugar o HTML renderizado
"""

import requests

def debug_html():
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        content = response.text
        
        # Procurar por activeTradesCount
        if 'activeTradesCount' in content:
            print("✅ activeTradesCount encontrado no HTML")
            
            # Extrair linhas ao redor do elemento
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'activeTradesCount' in line:
                    print(f"\nLinha {i+1}: {line.strip()}")
                    # Mostrar contexto
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        prefix = ">>>" if j == i else "   "
                        print(f"{prefix} {j+1}: {lines[j].strip()}")
                    break
        else:
            print("❌ activeTradesCount NÃO encontrado no HTML")
            
            # Procurar por padrões similares
            similar_patterns = ['trades', 'count', 'badge', 'active']
            for pattern in similar_patterns:
                if pattern in content.lower():
                    print(f"✅ Encontrado padrão similar: {pattern}")
                    
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    debug_html()
