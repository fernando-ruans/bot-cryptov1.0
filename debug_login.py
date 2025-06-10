#!/usr/bin/env python3
"""
Debug do sistema de login - verificar onde está o problema
"""

import os
import sys
from flask import Flask
from src.auth.models import db, User

# Configurar Flask temporário para testes
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/cryptoninja_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar db
db.init_app(app)

def test_user_lookup():
    """Testar busca de usuário"""
    with app.app_context():
        print("🔍 Testando busca de usuário...")
        
        # Buscar usuário admin
        user = User.query.filter_by(username='admin').first()
        
        if user:
            print(f"✅ Usuário encontrado:")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Is Admin: {user.is_admin}")
            print(f"   Is Active: {user.is_active}")
            print(f"   Password Hash: {user.password_hash[:50]}...")
            
            # Testar verificação de senha
            password_ok = user.check_password('ninja123')
            print(f"   Senha 'ninja123': {'✅' if password_ok else '❌'}")
            
            return user
        else:
            print("❌ Usuário 'admin' não encontrado!")
            return None

def test_all_users():
    """Listar todos os usuários"""
    with app.app_context():
        print("\n👥 Todos os usuários no banco:")
        users = User.query.all()
        
        for user in users:
            print(f"   • ID: {user.id}, Username: '{user.username}', Active: {user.is_active}")

def test_direct_query():
    """Teste direto no banco"""
    with app.app_context():
        print("\n📊 Query direta SQL:")
        result = db.session.execute("SELECT id, username, is_active FROM users WHERE username = 'admin'")
        rows = result.fetchall()
        
        if rows:
            for row in rows:
                print(f"   ID: {row[0]}, Username: '{row[1]}', Active: {row[2]}")
        else:
            print("   Nenhum resultado encontrado")

if __name__ == "__main__":
    print("🥷 CryptoNinja - Debug do Sistema de Login")
    print("=" * 50)
    
    try:
        test_all_users()
        test_user_lookup()
        test_direct_query()
        
        print("\n✅ Debug concluído!")
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        import traceback
        traceback.print_exc()
