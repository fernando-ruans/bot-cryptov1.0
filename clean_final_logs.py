#!/usr/bin/env python3
"""
Script final para remover logs restantes do dashboard.js
"""

import re
import os

def clean_remaining_logs():
    file_path = "static/js/dashboard.js"
    
    # Ler o arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remover logs específicos restantes, mantendo apenas console.error
    replacements = [
        # Remover logs de sinal gerado, display, confirmação
        (r"\s*console\.log\('✅ Sinal gerado:'[^;]*\);\s*", ""),
        (r"\s*console\.log\('📊 Exibindo sinal:'[^;]*\);\s*", ""),
        (r"\s*console\.log\('✅ Confirmando sinal:'[^;]*\);\s*", ""),
        (r"\s*console\.log\('📊 Portfolio atualizado:'[^;]*\);\s*", ""),
        (r"\s*console\.log\('🔒 Fechando trade:'[^;]*\);\s*", ""),
        
        # Remover logs de eventos WebSocket (são muito frequentes)
        (r"\s*console\.log\('💰 Atualização de preço:'[^;]*\);\s*", ""),
        (r"\s*console\.log\('📈 Atualização de trade:'[^;]*\);\s*", ""),
        (r"\s*console\.log\('🎯 Novo sinal recebido:'[^;]*\);\s*", ""),
        (r"\s*console\.log\('📊 Trade aberto:'[^;]*\);\s*", ""),
        (r"\s*console\.log\('🔒 Trade fechado:'[^;]*\);\s*", ""),
        (r"\s*console\.log\('💼 Portfolio atualizado:'[^;]*\);\s*", ""),
        
        # Remover logs de display de mercado (muito frequente)
        (r"\s*console\.log\('📊 Atualizando display de mercado:'[^;]*\);\s*", ""),
        
        # Remover log de expansão de dados
        (r"\s*console\.log\('✅ Expansão de dados iniciada em background'\);\s*", ""),
        
        # Manter apenas o log de inicialização principal, mas torná-lo mais simples
        (r"console\.log\('🎯 DOM carregado, inicializando dashboard\.\.\.'\);", "// Dashboard inicializado"),
    ]
    
    # Aplicar substituições
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Limpar linhas vazias excessivas
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Salvar arquivo limpo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Logs restantes removidos do dashboard.js!")
    print("📊 Console do browser agora estará limpo")
    print("⚠️ Apenas console.error permanecerão para debug de problemas")

if __name__ == "__main__":
    clean_remaining_logs()
