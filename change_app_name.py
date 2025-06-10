#!/usr/bin/env python3
"""
Script para alterar o nome da aplicação em todos os arquivos
"""

import os
import re

def change_app_name(new_name, new_subtitle, emoji=""):
    """
    Muda o nome da aplicação em todos os arquivos relevantes
    """
    
    # Arquivos para alterar
    files_to_change = [
        'templates/index_enhanced.html',
        'templates/index.html', 
        'templates/dashboard_simple.html',
        'templates/index_clean.html',
        'static/js/dashboard.js',
        'README.md',
        'README_SIMPLIFICADO.md'
    ]
    
    # Padrões para substituir
    patterns = [
        (r'Trading Bot AI.*?Dashboard', f'{new_name} {emoji} - {new_subtitle}'),
        (r'Trading Bot AI.*?Enhanced', f'{new_name} {emoji}'),
        (r'Trading Bot AI.*?Paper Trading', f'{new_name} {emoji} - {new_subtitle}'),
        (r'Trading Bot AI.*?Versão Simplificada', f'{new_name} {emoji} - {new_subtitle}'),
        (r'Trading Bot AI.*?Sistema Simplificado', f'{new_name} {emoji} - {new_subtitle}'),
        (r'Trading Bot AI.*?Smart Trading', f'{new_name} {emoji} - {new_subtitle}'),
        (r'Trading Bot AI', f'{new_name} {emoji}')
    ]
    
    base_path = r'c:\Users\ferna\bot-cryptov1.0'
    
    for file_path in files_to_change:
        full_path = os.path.join(base_path, file_path)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Aplicar substituições
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Atualizado: {file_path}")
                
            except Exception as e:
                print(f"❌ Erro ao atualizar {file_path}: {e}")
        else:
            print(f"⚠️ Arquivo não encontrado: {file_path}")

# Opções de nomes disponíveis
name_options = {
    '1': ('CryptoBolt AI', 'Smart Trading Platform', '⚡'),
    '2': ('BitForge', 'AI Trading Engine', '🔥'),  
    '3': ('CryptoNinja', 'Stealth Trading AI', '🥷'),
    '4': ('DiamondBot', 'Premium Crypto AI', '💎'),
    '5': ('LunarBot', 'To The Moon Trading', '🌙'),
    '6': ('CryptoMind', 'Intelligent Trading Bot', '🧠'),
    '7': ('RocketTrade', 'AI-Powered Crypto Bot', '🚀')
}

def show_options():
    print("🎯 Escolha o novo nome para a aplicação:")
    print("=" * 50)
    
    for key, (name, subtitle, emoji) in name_options.items():
        print(f"{key}. {name} {emoji} - {subtitle}")
    
    print("=" * 50)
    choice = input("Digite o número da sua escolha (1-7): ").strip()
    
    if choice in name_options:
        name, subtitle, emoji = name_options[choice]
        print(f"\n🎉 Você escolheu: {name} {emoji} - {subtitle}")
        
        confirm = input("\nConfirma a mudança? (s/n): ").strip().lower()
        if confirm in ['s', 'sim', 'y', 'yes']:
            change_app_name(name, subtitle, emoji)
            print(f"\n✅ Nome da aplicação alterado para: {name} {emoji}")
            print("🔄 Reinicie o servidor para ver as mudanças!")
        else:
            print("❌ Operação cancelada")
    else:
        print("❌ Escolha inválida!")

if __name__ == "__main__":
    show_options()
