#!/usr/bin/env python3
"""
Teste de inicializacao do servidor principal main.py
"""

import subprocess
import sys
import time
import threading
import os

def test_main_server():
    """Testar inicializacao do servidor main.py"""
    print("TESTE DO SERVIDOR PRINCIPAL - MAIN.PY")
    print("="*60)
    
    try:
        # Iniciar o main.py em processo separado
        print("Iniciando servidor main.py...")
        
        process = subprocess.Popen([
            sys.executable, 'main.py'
        ], cwd=os.path.dirname(__file__), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Aguardar inicializacao
        time.sleep(10)
        
        # Verificar se o processo ainda esta rodando
        if process.poll() is None:
            print("OK: Servidor iniciado e rodando")
            
            # Tentar fazer uma requisicao simples
            try:
                import requests
                response = requests.get('http://localhost:5000/api/status', timeout=5)
                if response.status_code == 200:
                    print("OK: API respondendo")
                    print(f"Status: {response.json()}")
                else:
                    print(f"WARNING: API retornou status {response.status_code}")
            except Exception as e:
                print(f"INFO: Nao foi possivel testar API: {e}")
            
            # Terminar processo
            process.terminate()
            process.wait(timeout=5)
            print("OK: Servidor parado")
            
            return True
        else:
            # Processo terminou, verificar output
            stdout, stderr = process.communicate()
            print("Processo terminou. Output:")
            print(stdout)
            if stderr:
                print("Erros:")
                print(stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == '__main__':
    success = test_main_server()
    if success:
        print("\nSUCCESS: Sistema principal funcionando!")
    else:
        print("\nERROR: Problemas no sistema principal")
