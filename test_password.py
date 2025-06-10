#!/usr/bin/env python3
"""
Teste de verificação de senha para debug do login
"""

from flask_bcrypt import Bcrypt

# Inicializar bcrypt
bcrypt = Bcrypt()

# Hash armazenado no banco
stored_hash = "$2b$12$MeKajNh.3cNpEMDbd9.YVesshzrVOSYUx3/GDLge2j.QMfoTYDpQW"

# Senha para testar
password = "ninja123"

# Testar verificação
result = bcrypt.check_password_hash(stored_hash, password)

print(f"Hash armazenado: {stored_hash}")
print(f"Senha testada: {password}")
print(f"Verificação: {'✅ SUCESSO' if result else '❌ FALHA'}")

# Testar também com outras senhas
test_passwords = ["ninja123", "admin", "123", "ninja", "NINJA123"]

print("\n--- Teste com várias senhas ---")
for test_pwd in test_passwords:
    result = bcrypt.check_password_hash(stored_hash, test_pwd)
    print(f"Senha '{test_pwd}': {'✅' if result else '❌'}")
