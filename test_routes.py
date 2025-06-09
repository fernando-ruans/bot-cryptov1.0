#!/usr/bin/env python3
"""
Teste para verificar rotas registradas no Flask
"""

import sys
sys.path.append('.')

from main import app

if __name__ == '__main__':
    print("🔍 Rotas registradas no Flask:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
