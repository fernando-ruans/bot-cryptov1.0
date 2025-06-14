#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ANÁLISE DOS RESULTADOS DE VIÉS - Adaptado para dados com ação null
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Carregar dados
with open('teste_vies_20250613_232926.json', 'r') as f:
    dados_brutos = json.load(f)

df = pd.DataFrame(dados_brutos)

print("🔍 ANÁLISE DOS RESULTADOS DE TESTE DE VIÉS")
print("=" * 50)

# Estatísticas gerais
total_testes = len(df)
sucessos = len(df[df['sucesso'] == True])
taxa_sucesso = sucessos / total_testes * 100

print(f"📊 ESTATÍSTICAS GERAIS:")
print(f"  Total de testes: {total_testes}")
print(f"  Sucessos: {sucessos}")
print(f"  Falhas: {total_testes - sucessos}")
print(f"  Taxa de sucesso: {taxa_sucesso:.1f}%")

# Verificar problema com ações
dados_validos = df[df['sucesso'] == True]
acoes_null = dados_validos['acao'].isnull().sum()
print(f"\n⚠️  PROBLEMA IDENTIFICADO:")
print(f"  Sinais com ação NULL: {acoes_null}/{len(dados_validos)}")
print(f"  Isso indica um bug na API de geração de sinais!")

# Análise de confiança
print(f"\n🎯 ANÁLISE DE CONFIANÇA:")
confianca_stats = dados_validos['confianca'].describe()
print(f"  Mínima: {confianca_stats['min']:.1f}%")
print(f"  Máxima: {confianca_stats['max']:.1f}%")
print(f"  Média: {confianca_stats['mean']:.1f}%")
print(f"  Mediana: {confianca_stats['50%']:.1f}%")

# Análise por ativo
print(f"\n📈 CONFIANÇA MÉDIA POR ATIVO:")
confianca_por_ativo = dados_validos.groupby('ativo')['confianca'].agg(['mean', 'std', 'count']).round(1)
for ativo, stats in confianca_por_ativo.iterrows():
    print(f"  {ativo}: {stats['mean']:.1f}% ±{stats['std']:.1f}% ({stats['count']} sinais)")

# Análise por timeframe
print(f"\n⏰ CONFIANÇA MÉDIA POR TIMEFRAME:")
confianca_por_tf = dados_validos.groupby('timeframe')['confianca'].agg(['mean', 'std', 'count']).round(1)
for tf, stats in confianca_por_tf.iterrows():
    print(f"  {tf}: {stats['mean']:.1f}% ±{stats['std']:.1f}% ({stats['count']} sinais)")

# Gerar gráficos
plt.style.use('dark_background')
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 1. Distribuição de confiança
axes[0,0].hist(dados_validos['confianca'], bins=20, color='skyblue', alpha=0.7, edgecolor='white')
axes[0,0].set_title('Distribuição de Confiança', fontweight='bold', color='white')
axes[0,0].set_xlabel('Confiança (%)', color='white')
axes[0,0].set_ylabel('Frequência', color='white')
axes[0,0].axvline(dados_validos['confianca'].mean(), color='red', linestyle='--', 
                  label=f'Média: {dados_validos["confianca"].mean():.1f}%')
axes[0,0].legend()

# 2. Confiança por ativo
confianca_por_ativo_sorted = dados_validos.groupby('ativo')['confianca'].mean().sort_values()
bars = axes[0,1].bar(range(len(confianca_por_ativo_sorted)), confianca_por_ativo_sorted.values, 
                     color='lightgreen', alpha=0.8)
axes[0,1].set_title('Confiança Média por Ativo', fontweight='bold', color='white')
axes[0,1].set_ylabel('Confiança (%)', color='white')
axes[0,1].set_xticks(range(len(confianca_por_ativo_sorted)))
axes[0,1].set_xticklabels(confianca_por_ativo_sorted.index, rotation=45, ha='right')

# Adicionar valores nas barras
for i, bar in enumerate(bars):
    height = bar.get_height()
    axes[0,1].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', color='white')

# 3. Confiança por timeframe
confianca_por_tf_sorted = dados_validos.groupby('timeframe')['confianca'].mean().sort_values()
bars = axes[1,0].bar(confianca_por_tf_sorted.index, confianca_por_tf_sorted.values, 
                     color='orange', alpha=0.8)
axes[1,0].set_title('Confiança Média por Timeframe', fontweight='bold', color='white')
axes[1,0].set_ylabel('Confiança (%)', color='white')
axes[1,0].set_xlabel('Timeframe', color='white')

# Adicionar valores nas barras
for bar in bars:
    height = bar.get_height()
    axes[1,0].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', color='white')

# 4. Heatmap de confiança (ativo vs timeframe)
pivot_confianca = dados_validos.pivot_table(values='confianca', index='ativo', 
                                           columns='timeframe', aggfunc='mean')
sns.heatmap(pivot_confianca, annot=True, fmt='.1f', cmap='RdYlGn', 
            ax=axes[1,1], cbar_kws={'label': 'Confiança (%)'})
axes[1,1].set_title('Confiança por Ativo × Timeframe', fontweight='bold', color='white')

plt.tight_layout()
plt.savefig('analise_vies_confianca.png', dpi=300, bbox_inches='tight', facecolor='black')
plt.show()

print(f"\n💾 Gráfico salvo: analise_vies_confianca.png")

# Identificar padrões interessantes
print(f"\n🔍 PADRÕES IDENTIFICADOS:")

# Ativo com maior/menor confiança média
ativo_max_conf = confianca_por_ativo_sorted.idxmax()
ativo_min_conf = confianca_por_ativo_sorted.idxmin()
print(f"  Ativo com MAIOR confiança: {ativo_max_conf} ({confianca_por_ativo_sorted[ativo_max_conf]:.1f}%)")
print(f"  Ativo com MENOR confiança: {ativo_min_conf} ({confianca_por_ativo_sorted[ativo_min_conf]:.1f}%)")

# Timeframe com maior/menor confiança média
tf_max_conf = confianca_por_tf_sorted.idxmax()
tf_min_conf = confianca_por_tf_sorted.idxmin()
print(f"  Timeframe com MAIOR confiança: {tf_max_conf} ({confianca_por_tf_sorted[tf_max_conf]:.1f}%)")
print(f"  Timeframe com MENOR confiança: {tf_min_conf} ({confianca_por_tf_sorted[tf_min_conf]:.1f}%)")

# Análise de spread stop/take
dados_validos['spread_stop'] = abs(dados_validos['preco_entrada'] - dados_validos['stop_loss']) / dados_validos['preco_entrada'] * 100
dados_validos['spread_take'] = abs(dados_validos['take_profit'] - dados_validos['preco_entrada']) / dados_validos['preco_entrada'] * 100
dados_validos['risk_reward'] = dados_validos['spread_take'] / dados_validos['spread_stop']

print(f"\n📊 ANÁLISE RISK/REWARD:")
print(f"  Risk/Reward médio: {dados_validos['risk_reward'].mean():.2f}")
print(f"  Stop Loss médio: {dados_validos['spread_stop'].mean():.2f}%")
print(f"  Take Profit médio: {dados_validos['spread_take'].mean():.2f}%")

print(f"\n⚠️  RECOMENDAÇÕES:")
print(f"  1. Corrigir o bug na API que está retornando ação = null")
print(f"  2. Investigar por que alguns ativos têm confiança consistentemente baixa")
print(f"  3. Analisar se timeframes longos devem ter confiança diferente dos curtos")
print(f"  4. Após correção, repetir teste para análise completa de viés")

print(f"\n✅ Análise concluída!")
