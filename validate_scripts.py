#!/usr/bin/env python3
"""
CryptoNinja 🥷 - Validador de Scripts de Banco
Testa se os scripts SQL estão corretos
"""

import os
import re
import sys

def validate_sql_script(file_path):
    """Validar script SQL"""
    print(f"\n🔍 Validando: {os.path.basename(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Verificar criação de tabelas essenciais
    essential_tables = ['users', 'trades', 'signals', 'market_data', 'notifications']
    for table in essential_tables:
        if f"CREATE TABLE {table}" in content:
            checks.append(f"✅ Tabela {table}")
        else:
            checks.append(f"❌ Tabela {table} não encontrada")
    
    # Verificar usuários de teste
    if 'admin@cryptoninja.com' in content:
        checks.append("✅ Usuário admin")
    else:
        checks.append("❌ Usuário admin não encontrado")
        
    if 'demo@cryptoninja.com' in content:
        checks.append("✅ Usuário demo")
    else:
        checks.append("❌ Usuário demo não encontrado")
    
    # Verificar hashes bcrypt válidos
    bcrypt_pattern = r'\$2b\$\d+\$[A-Za-z0-9./]{53}'
    bcrypt_matches = re.findall(bcrypt_pattern, content)
    if len(bcrypt_matches) >= 2:
        checks.append(f"✅ {len(bcrypt_matches)} hashes bcrypt válidos")
    else:
        checks.append("❌ Hashes bcrypt inválidos ou insuficientes")
    
    # Verificar índices
    if 'CREATE INDEX' in content:
        index_count = content.count('CREATE INDEX')
        checks.append(f"✅ {index_count} índices criados")
    else:
        checks.append("❌ Nenhum índice encontrado")
    
    # Verificar constraints
    if 'CHECK (' in content:
        constraint_count = content.count('CHECK (')
        checks.append(f"✅ {constraint_count} constraints")
    else:
        checks.append("❌ Nenhuma constraint encontrada")
    
    # Mostrar resultados
    for check in checks:
        print(f"  {check}")
    
    # Contar sucessos
    success_count = sum(1 for check in checks if check.startswith('✅'))
    total_checks = len(checks)
    
    print(f"\n📊 Resultado: {success_count}/{total_checks} verificações passaram")
    
    return success_count == total_checks

def validate_script_syntax(file_path):
    """Verificar sintaxe SQL básica"""
    print(f"\n🔧 Verificando sintaxe: {os.path.basename(file_path)}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Verificar parênteses balanceados
    open_parens = content.count('(')
    close_parens = content.count(')')
    if open_parens != close_parens:
        issues.append(f"❌ Parênteses desbalanceados: {open_parens} abertos, {close_parens} fechados")
    else:
        issues.append("✅ Parênteses balanceados")
    
    # Verificar ponto e vírgula
    statements = content.split(';')
    non_empty_statements = [s.strip() for s in statements if s.strip() and not s.strip().startswith('--')]
    if len(non_empty_statements) > 0:
        issues.append(f"✅ {len(non_empty_statements)} statements SQL encontrados")
    else:
        issues.append("❌ Nenhum statement SQL válido encontrado")
    
    # Verificar palavras-chave essenciais
    keywords = ['CREATE TABLE', 'INSERT INTO', 'CREATE INDEX']
    for keyword in keywords:
        if keyword in content:
            count = content.count(keyword)
            issues.append(f"✅ {keyword}: {count} ocorrências")
        else:
            issues.append(f"❌ {keyword} não encontrado")
    
    for issue in issues:
        print(f"  {issue}")
    
    return len([i for i in issues if i.startswith('❌')]) == 0

def main():
    """Função principal"""
    print("🥷 CryptoNinja - Validador de Scripts de Banco")
    print("=" * 50)
    
    # Scripts para validar
    scripts = [
        'create_database.sql',
        'schema_cloud.sql', 
        'schema_supabase.sql'
    ]
    
    all_valid = True
    
    for script in scripts:
        if os.path.exists(script):
            # Validar conteúdo
            content_valid = validate_sql_script(script)
            
            # Validar sintaxe
            syntax_valid = validate_script_syntax(script)
            
            script_valid = content_valid and syntax_valid
            
            if script_valid:
                print(f"\n🎉 {script}: VÁLIDO")
            else:
                print(f"\n❌ {script}: FALHOU")
                all_valid = False
                
            print("-" * 50)
        else:
            print(f"\n⚠️  Script não encontrado: {script}")
            all_valid = False
    
    # Resultado final
    print(f"\n{'='*50}")
    if all_valid:
        print("🎊 TODOS OS SCRIPTS ESTÃO VÁLIDOS!")
        print("\n📋 Scripts prontos para deploy:")
        for script in scripts:
            if os.path.exists(script):
                print(f"  ✅ {script}")
        
        print(f"\n🚀 Próximos passos:")
        print("  1. Escolha o script apropriado para seu ambiente")
        print("  2. Execute conforme GUIA_BANCO.md")
        print("  3. Configure variáveis de ambiente")
        print("  4. Deploy!")
        
    else:
        print("❌ ALGUNS SCRIPTS FALHARAM!")
        print("Verifique os erros acima e corrija antes de usar.")
        
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())
