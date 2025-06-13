#!/usr/bin/env python3
"""
Script para remover logs desnecessários do dashboard.js
"""

import re
import os

def clean_dashboard_logs():
    file_path = "static/js/dashboard.js"
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    # Ler o arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup do arquivo original
    with open(file_path + '.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Remover console.log, mantendo apenas os críticos
    patterns_to_remove = [
        # Logs de inicialização
        r"console\.log\('🚀[^']*'\);?\s*\n?",
        r"console\.log\(`📊[^`]*`\);?\s*\n?",
        r"console\.log\(`💰[^`]*`\);?\s*\n?",
        r"console\.log\('✅ CryptoNinja[^']*'\);?\s*\n?",
        r"console\.log\('📈 Inicializando TradingView[^']*'\);?\s*\n?",
        r"console\.log\('🎯 Configurando event listeners[^']*'\);?\s*\n?",
        
        # Logs de timeframe/ativo
        r"console\.log\(`🔄 Timeframe selecionado[^`]*`\);?\s*\n?",
        r"console\.log\(`🔄 Interface atualizada para ativo[^`]*`\);?\s*\n?",
        r"console\.log\(`🔄 Mudando ativo para[^`]*`\);?\s*\n?",
        r"console\.log\('⚠️ Ativo já selecionado[^']*'\);?\s*\n?",
        r"console\.log\(`✅ Ativo alterado com sucesso[^`]*`\);?\s*\n?",
        r"console\.log\(`⏰ Mudando timeframe para[^`]*`\);?\s*\n?",
        
        # Logs de preços/atualizações
        r"console\.log\('🔄 Atualização automática[^']*'\);?\s*\n?",
        r"console\.log\('⏹️ Atualização automática[^']*'\);?\s*\n?",
        r"console\.log\('⏹️ Captura de preços[^']*'\);?\s*\n?",
        r"console\.log\('💰 Atualização de preço[^']*data[^;]*\);?\s*\n?",
        r"console\.log\(`💰 Atualizando preços para[^`]*`\);?\s*\n?",
        r"console\.log\(`💰 Dados de mercado atualizados[^`]*`\);?\s*\n?",
        r"console\.log\(`💰 Preço [^`]*`\);?\s*\n?",
        r"console\.log\(`💰 Display atualizado[^`]*`\);?\s*\n?",
        r"console\.log\(`💰 Preço atualizado[^`]*`\);?\s*\n?",
        r"console\.log\('📊 Atualizando display de mercado[^']*'\);?\s*\n?",
        
        # Logs de WebSocket
        r"console\.log\('🔗 Conectando WebSocket[^']*'\);?\s*\n?",
        r"console\.log\('✅ WebSocket conectado[^']*'\);?\s*\n?",
        r"console\.log\('❌ WebSocket desconectado[^']*'\);?\s*\n?",
        
        # Logs de trades/sinais
        r"console\.log\('🎰 Gerando novo sinal[^']*'\);?\s*\n?",
        r"console\.log\('✅ Sinal gerado[^']*signal[^;]*\);?\s*\n?",
        r"console\.log\('📊 Exibindo sinal[^']*signal[^;]*\);?\s*\n?",
        r"console\.log\('✅ Confirmando sinal[^']*'\);?\s*\n?",
        r"console\.log\('✅ Trade confirmado[^']*'\);?\s*\n?",
        r"console\.log\('❌ Sinal rejeitado[^']*'\);?\s*\n?",
        r"console\.log\('📊 Portfolio atualizado[^']*portfolio[^;]*\);?\s*\n?",
        r"console\.log\('🔒 Fechando trade[^']*'\);?\s*\n?",
        r"console\.log\('✅ Trade fechado[^']*'\);?\s*\n?",
        r"console\.log\('📊 Interface atualizada após[^']*'\);?\s*\n?",
        
        # Logs de monitoramento
        r"console\.log\(`🔍 Iniciando monitoramento[^`]*`\);?\s*\n?",
        r"console\.log\(`⏰ Monitoramento automático[^`]*`\);?\s*\n?",
        r"console\.log\('⏹️ Monitoramento multi-símbolos[^']*'\);?\s*\n?",
        
        # Logs de histórico
        r"console\.log\('📜 Carregando histórico[^']*'\);?\s*\n?",
        r"console\.log\(`📊 Histórico carregado[^`]*`\);?\s*\n?",
        
        # Logs de eventos WebSocket
        r"console\.log\('📈 Atualização de trade[^']*data[^;]*\);?\s*\n?",
        r"console\.log\('🎯 Novo sinal recebido[^']*data[^;]*\);?\s*\n?",
        r"console\.log\(`📊 Sinal recebido para[^`]*`\);?\s*\n?",
        r"console\.log\('📊 Trade aberto[^']*data[^;]*\);?\s*\n?",
        r"console\.log\('🔒 Trade fechado[^']*data[^;]*\);?\s*\n?",
        r"console\.log\('💼 Portfolio atualizado[^']*data[^;]*\);?\s*\n?",
        
        # Logs de TradingView
        r"console\.log\(`📈 Atualizando gráfico[^`]*`\);?\s*\n?",
        r"console\.log\(`📈 TradingView carregado[^`]*`\);?\s*\n?",
        r"console\.log\(`✅ Widget TradingView criado[^`]*`\);?\s*\n?",
        r"console\.log\('✅ Captura de preços do TradingView[^']*'\);?\s*\n?",
    ]
    
    # Aplicar todas as remoções
    original_lines = len(content.split('\n'))
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # Limpar linhas vazias excessivas
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Salvar arquivo limpo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_lines = len(content.split('\n'))
    removed_lines = original_lines - new_lines
    
    print(f"✅ Logs limpos do dashboard.js!")
    print(f"📊 Linhas removidas: {removed_lines}")
    print(f"📄 Backup salvo em: {file_path}.backup")

if __name__ == "__main__":
    clean_dashboard_logs()
