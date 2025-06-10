#!/usr/bin/env python3
"""
Teste específico do sistema de login - debug do redirecionamento
"""

import requests
import json
import time

def test_login_flow():
    """Testar fluxo completo de login"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testando fluxo de login do CryptoNinja")
    print("=" * 50)
    
    # 1. Testar se servidor está rodando
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        print(f"✅ Servidor online: {response.status_code}")
    except Exception as e:
        print(f"❌ Servidor offline: {e}")
        return False
    
    # 2. Testar página de login (GET)
    try:
        response = requests.get(f"{base_url}/auth/login", timeout=5)
        print(f"✅ Página de login acessível: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar login: {e}")
        return False
    
    # 3. Testar login via JSON (POST)
    login_data = {
        "username": "admin",
        "password": "ninja123",
        "remember": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(login_data),
            timeout=10
        )
        
        print(f"📡 Status do login: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"📄 Resposta JSON:")
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Redirect: {result.get('redirect')}")
            print(f"   User: {result.get('user')}")
            
            if result.get('success'):
                print("✅ Login bem-sucedido!")
                
                # 4. Testar acesso à página principal
                redirect_url = result.get('redirect', '/')
                full_redirect_url = f"{base_url}{redirect_url}"
                
                print(f"🔗 Testando redirecionamento para: {full_redirect_url}")
                
                try:
                    # Criar sessão para manter cookies
                    session = requests.Session()
                    
                    # Fazer login novamente para obter cookies
                    session.post(
                        f"{base_url}/auth/login",
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(login_data)
                    )
                    
                    # Tentar acessar página principal
                    dashboard_response = session.get(full_redirect_url, timeout=10)
                    print(f"🏠 Dashboard acessível: {dashboard_response.status_code}")
                    
                    if dashboard_response.status_code == 200:
                        print("✅ Redirecionamento funcionando!")
                        return True
                    else:
                        print(f"❌ Problema no dashboard: {dashboard_response.status_code}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Erro no redirecionamento: {e}")
                    return False
            else:
                print(f"❌ Falha no login: {result.get('error')}")
                return False
        else:
            print(f"❌ Resposta não-JSON: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
        return False

def test_form_login():
    """Testar login via formulário HTML"""
    
    base_url = "http://localhost:5000"
    
    print("\n🧪 Testando login via formulário")
    print("=" * 40)
    
    login_data = {
        "username": "admin",
        "password": "ninja123",
        "remember": False
    }
    
    try:
        session = requests.Session()
        
        # Fazer login via form data
        response = session.post(
            f"{base_url}/auth/login",
            data=login_data,
            allow_redirects=False,  # Não seguir redirecionamentos automaticamente
            timeout=10
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"🔗 Location header: {response.headers.get('Location')}")
        
        if response.status_code == 302:  # Redirecionamento
            redirect_location = response.headers.get('Location')
            print(f"✅ Redirecionamento detectado para: {redirect_location}")
            
            # Seguir redirecionamento manualmente
            if redirect_location:
                final_response = session.get(f"{base_url}{redirect_location}", timeout=10)
                print(f"🏠 Página final: {final_response.status_code}")
                
                if final_response.status_code == 200:
                    print("✅ Login via formulário funcionando!")
                    return True
        
        print("❌ Problema no login via formulário")
        return False
        
    except Exception as e:
        print(f"❌ Erro no teste de formulário: {e}")
        return False

if __name__ == "__main__":
    print("🥷 CryptoNinja - Debug do Sistema de Login")
    print("=" * 60)
    
    # Aguardar servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(3)
    
    success1 = test_login_flow()
    success2 = test_form_login()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TODOS OS TESTES PASSARAM! Login funcionando corretamente.")
    else:
        print("❌ Alguns testes falharam. Verifique os logs acima.")
        
    print("=" * 60)
