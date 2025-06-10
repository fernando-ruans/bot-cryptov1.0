#!/usr/bin/env python3
"""
Script para corrigir as senhas dos usuários no banco
"""

import psycopg2
from flask_bcrypt import Bcrypt

# Configurar bcrypt
bcrypt = Bcrypt()

# Gerar hash correto para 'ninja123'
password = 'ninja123'
new_hash = bcrypt.generate_password_hash(password).decode('utf-8')

print(f"Nova senha hash: {new_hash}")

# Conectar ao banco
try:
    conn = psycopg2.connect(
        host="localhost",
        database="cryptoninja_db",
        user="postgres",
        password="admin"
    )
    
    cur = conn.cursor()
    
    # Atualizar usuário admin
    cur.execute("UPDATE users SET password_hash = %s WHERE username = %s", (new_hash, 'admin'))
    print("✅ Hash do admin atualizado")
    
    # Atualizar usuário demo
    cur.execute("UPDATE users SET password_hash = %s WHERE username = %s", (new_hash, 'demo'))
    print("✅ Hash do demo atualizado")
    
    # Confirmar mudanças
    conn.commit()
    
    # Verificar resultado
    cur.execute("SELECT username, LEFT(password_hash, 10) as hash_start, LENGTH(password_hash) as hash_len FROM users")
    rows = cur.fetchall()
    
    print("\n📊 Resultado:")
    for row in rows:
        print(f"   {row[0]}: {row[1]}... (len: {row[2]})")
    
    cur.close()
    conn.close()
    
    print("\n✅ Senhas corrigidas com sucesso!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
