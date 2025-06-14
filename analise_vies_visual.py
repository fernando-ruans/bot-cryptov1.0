#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ANÁLISE VISUAL DE VIÉS - GRÁFICOS E RELATÓRIOS
Gera visualizações dos testes de viés para análise detalhada
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import glob
import numpy as np
from datetime import datetime
import os

class AnalisadorViesVisual:
    def __init__(self):
        self.dados = None
        plt.style.use('dark_background')
        sns.set_palette("husl")
        
    def carregar_dados(self, arquivo_json=None):
        """Carrega dados do teste de viés"""
        if arquivo_json is None:
            # Buscar o arquivo mais recente
            arquivos = glob.glob("teste_vies_*.json")
            if not arquivos:
                print("❌ Nenhum arquivo de teste encontrado.")
                return False
            
            arquivo_json = max(arquivos, key=os.path.getctime)
            print(f"📂 Carregando arquivo mais recente: {arquivo_json}")
        
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                dados_brutos = json.load(f)
            
            self.dados = pd.DataFrame(dados_brutos)
            print(f"✅ Dados carregados: {len(self.dados)} registros")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def gerar_grafico_distribuicao_acoes(self):
        """Gráfico de distribuição de ações (BUY/SELL/HOLD)"""
        sucessos = self.dados[self.dados['sucesso'] == True]
        
        if sucessos.empty:
            print("❌ Nenhum dado válido para gráfico de ações.")
            return
        
        plt.figure(figsize=(10, 6))
        
        # Contar ações
        acoes = sucessos['acao'].value_counts()
        
        # Gráfico de pizza
        plt.subplot(1, 2, 1)
        colors = ['#00ff88', '#ff4444', '#ffaa00']
        plt.pie(acoes.values, labels=acoes.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        plt.title('Distribuição de Ações', fontsize=14, fontweight='bold')
        
        # Gráfico de barras
        plt.subplot(1, 2, 2)
        bars = plt.bar(acoes.index, acoes.values, color=colors)
        plt.title('Contagem de Ações', fontsize=14, fontweight='bold')
        plt.ylabel('Quantidade')
        
        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('vies_distribuicao_acoes.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("💾 Gráfico salvo: vies_distribuicao_acoes.png")
    
    def gerar_heatmap_ativo_timeframe(self):
        """Heatmap de ações por ativo e timeframe"""
        sucessos = self.dados[self.dados['sucesso'] == True]
        
        if sucessos.empty:
            print("❌ Nenhum dado válido para heatmap.")
            return
        
        # Criar tabela cruzada
        crosstab = pd.crosstab(sucessos['ativo'], sucessos['timeframe'], 
                              sucessos['acao'], aggfunc='count', fill_value=0)
        
        # Criar subplots para cada ação
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for i, acao in enumerate(['BUY', 'SELL', 'HOLD']):
            if acao in crosstab.columns:
                data = crosstab[acao]
            else:
                data = pd.DataFrame(0, index=crosstab.index, columns=crosstab.index.names)
            
            sns.heatmap(data, annot=True, fmt='d', cmap='RdYlGn', 
                       ax=axes[i], cbar_kws={'label': 'Quantidade'})
            axes[i].set_title(f'Sinais {acao}', fontsize=14, fontweight='bold')
            axes[i].set_xlabel('Timeframe')
            axes[i].set_ylabel('Ativo')
        
        plt.tight_layout()
        plt.savefig('vies_heatmap_ativo_timeframe.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("💾 Gráfico salvo: vies_heatmap_ativo_timeframe.png")
    
    def gerar_grafico_confianca(self):
        """Gráfico de distribuição de confiança"""
        sucessos = self.dados[self.dados['sucesso'] == True]
        sucessos = sucessos.dropna(subset=['confianca'])
        
        if sucessos.empty:
            print("❌ Nenhum dado de confiança válido.")
            return
        
        plt.figure(figsize=(12, 8))
        
        # Histograma de confiança
        plt.subplot(2, 2, 1)
        plt.hist(sucessos['confianca'], bins=20, color='skyblue', alpha=0.7, edgecolor='black')
        plt.title('Distribuição de Confiança', fontweight='bold')
        plt.xlabel('Confiança (%)')
        plt.ylabel('Frequência')
        
        # Box plot por ação
        plt.subplot(2, 2, 2)
        sucessos.boxplot(column='confianca', by='acao', ax=plt.gca())
        plt.title('Confiança por Ação', fontweight='bold')
        plt.suptitle('')  # Remove título automático
        
        # Scatter plot: confiança vs ativo
        plt.subplot(2, 2, 3)
        for i, ativo in enumerate(sucessos['ativo'].unique()):
            dados_ativo = sucessos[sucessos['ativo'] == ativo]
            plt.scatter([i] * len(dados_ativo), dados_ativo['confianca'], 
                       alpha=0.6, s=50)
        
        plt.xticks(range(len(sucessos['ativo'].unique())), 
                  sucessos['ativo'].unique(), rotation=45)
        plt.title('Confiança por Ativo', fontweight='bold')
        plt.ylabel('Confiança (%)')
        
        # Média de confiança por timeframe
        plt.subplot(2, 2, 4)
        confianca_tf = sucessos.groupby('timeframe')['confianca'].mean().sort_values()
        bars = plt.bar(confianca_tf.index, confianca_tf.values, color='lightgreen')
        plt.title('Confiança Média por Timeframe', fontweight='bold')
        plt.ylabel('Confiança Média (%)')
        plt.xticks(rotation=45)
        
        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('vies_analise_confianca.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("💾 Gráfico salvo: vies_analise_confianca.png")
    
    def gerar_relatorio_detalhado(self):
        """Gera relatório detalhado em texto"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_vies_detalhado_{timestamp}.txt"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("🔥 RELATÓRIO DETALHADO - TESTE DE VIÉS\n")
            f.write("=" * 50 + "\n\n")
            
            # Estatísticas gerais
            total = len(self.dados)
            sucessos = len(self.dados[self.dados['sucesso'] == True])
            taxa_sucesso = sucessos / total * 100 if total > 0 else 0
            
            f.write("📊 ESTATÍSTICAS GERAIS:\n")
            f.write(f"Total de testes: {total}\n")
            f.write(f"Sucessos: {sucessos}\n")
            f.write(f"Falhas: {total - sucessos}\n")
            f.write(f"Taxa de sucesso: {taxa_sucesso:.1f}%\n\n")
            
            # Análise por ativo
            dados_validos = self.dados[self.dados['sucesso'] == True]
            
            if not dados_validos.empty:
                f.write("📈 ANÁLISE POR ATIVO:\n")
                for ativo in dados_validos['ativo'].unique():
                    dados_ativo = dados_validos[dados_validos['ativo'] == ativo]
                    acoes = dados_ativo['acao'].value_counts()
                    confianca_media = dados_ativo['confianca'].mean()
                    
                    f.write(f"\n{ativo}:\n")
                    f.write(f"  Total de sinais: {len(dados_ativo)}\n")
                    for acao, count in acoes.items():
                        pct = count / len(dados_ativo) * 100
                        f.write(f"  {acao}: {count} ({pct:.1f}%)\n")
                    f.write(f"  Confiança média: {confianca_media:.1f}%\n")
                
                f.write("\n⏰ ANÁLISE POR TIMEFRAME:\n")
                for tf in dados_validos['timeframe'].unique():
                    dados_tf = dados_validos[dados_validos['timeframe'] == tf]
                    acoes = dados_tf['acao'].value_counts()
                    confianca_media = dados_tf['confianca'].mean()
                    
                    f.write(f"\n{tf}:\n")
                    f.write(f"  Total de sinais: {len(dados_tf)}\n")
                    for acao, count in acoes.items():
                        pct = count / len(dados_tf) * 100
                        f.write(f"  {acao}: {count} ({pct:.1f}%)\n")
                    f.write(f"  Confiança média: {confianca_media:.1f}%\n")
        
        print(f"📄 Relatório salvo: {nome_arquivo}")
    
    def executar_analise_completa(self):
        """Executa análise visual completa"""
        if not self.carregar_dados():
            return
        
        print("\n🎨 Gerando visualizações...")
        
        try:
            self.gerar_grafico_distribuicao_acoes()
            self.gerar_heatmap_ativo_timeframe()
            self.gerar_grafico_confianca()
            self.gerar_relatorio_detalhado()
            
            print("\n✅ Análise visual completa!")
            print("📊 Todos os gráficos e relatórios foram gerados.")
            
        except Exception as e:
            print(f"❌ Erro durante análise: {e}")

def main():
    analisador = AnalisadorViesVisual()
    
    print("📊 ANALISADOR VISUAL DE VIÉS")
    print("=" * 30)
    
    # Verificar se existe arquivo de teste
    arquivos = glob.glob("teste_vies_*.json")
    if not arquivos:
        print("❌ Nenhum arquivo de teste encontrado.")
        print("💡 Execute primeiro o test_vies_multiplos_ativos.py")
        return
    
    analisador.executar_analise_completa()

if __name__ == "__main__":
    main()
