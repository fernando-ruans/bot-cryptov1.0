#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 TESTE DE VIÉS DIRECIONAL - ANÁLISE BUY vs SELL
Foca especificamente em detectar se a IA tem viés para compra ou venda
"""

import requests
import json
import time
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class TestadorViesDirecional:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.resultados = []
        
        # Ativos principais para teste
        self.ativos = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'MATICUSDT', 'AVAXUSDT'
        ]
        
        # Timeframes variados
        self.timeframes = ['5m', '15m', '1h', '4h']
        
        print("🎯 TESTE DE VIÉS DIRECIONAL - BUY vs SELL")
        print("=" * 50)
        print(f"🔍 Objetivo: Detectar se a IA favorece BUY ou SELL")
        print(f"📊 Ativos: {len(self.ativos)}")
        print(f"⏰ Timeframes: {len(self.timeframes)}")
        print(f"🎲 Total de testes: {len(self.ativos) * len(self.timeframes)}")

    def gerar_sinal_e_extrair_acao(self, ativo, timeframe):
        """Gera sinal e extrai especificamente a ação (BUY/SELL)"""
        try:
            url = f"{self.base_url}/api/generate_signal"
            payload = {
                'symbol': ativo,
                'timeframe': timeframe
            }
            
            print(f"🔍 {ativo} {timeframe}...", end=' ')
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    signal = data.get('signal', {})
                    
                    # Extrair ação corretamente
                    acao = signal.get('action')  # Primeiro tenta 'action'
                    if not acao:
                        acao = signal.get('signal_type')  # Depois 'signal_type'
                    if not acao:
                        acao = signal.get('recommendation')  # Depois 'recommendation'
                    
                    # Debug - mostrar a estrutura do signal
                    print(f"📋 Signal keys: {list(signal.keys())}")
                    
                    # Converter para formato padrão
                    if acao:
                        acao = acao.upper()
                        if acao in ['BUY', 'SELL', 'HOLD']:
                            print(f"✅ {acao} ({signal.get('confidence', 0)*100:.1f}%)")
                        else:
                            print(f"❓ Ação desconhecida: {acao}")
                            acao = None
                    else:
                        print("❌ Ação NULL")
                    
                    return {
                        'ativo': ativo,
                        'timeframe': timeframe,
                        'acao': acao,
                        'confianca': signal.get('confidence', 0) * 100,
                        'preco_entrada': signal.get('entry_price'),
                        'stop_loss': signal.get('stop_loss'),
                        'take_profit': signal.get('take_profit'),
                        'timestamp': datetime.now().isoformat(),
                        'sucesso': True,
                        'signal_raw': signal  # Para debug
                    }
                else:
                    print(f"❌ API Error: {data.get('error', 'Desconhecido')}")
                    return {
                        'ativo': ativo,
                        'timeframe': timeframe,
                        'erro': data.get('error', 'Erro na API'),
                        'timestamp': datetime.now().isoformat(),
                        'sucesso': False
                    }
            else:
                print(f"❌ HTTP {response.status_code}")
                return {
                    'ativo': ativo,
                    'timeframe': timeframe,
                    'erro': f'HTTP {response.status_code}',
                    'timestamp': datetime.now().isoformat(),
                    'sucesso': False
                }
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return {
                'ativo': ativo,
                'timeframe': timeframe,
                'erro': str(e),
                'timestamp': datetime.now().isoformat(),
                'sucesso': False
            }

    def executar_teste_vies_direcional(self):
        """Executa teste focado em viés direcional"""
        print(f"\n🎯 INICIANDO TESTE DE VIÉS DIRECIONAL")
        print("=" * 50)
        
        total = len(self.ativos) * len(self.timeframes)
        contador = 0
        
        for ativo in self.ativos:
            print(f"\n📈 TESTANDO: {ativo}")
            print("-" * 30)
            
            for timeframe in self.timeframes:
                contador += 1
                print(f"[{contador}/{total}] ", end='')
                
                resultado = self.gerar_sinal_e_extrair_acao(ativo, timeframe)
                self.resultados.append(resultado)
                
                # Pausa para não sobrecarregar
                time.sleep(2)
        
        print(f"\n✅ Teste concluído! {len(self.resultados)} resultados coletados.")

    def analisar_vies_direcional(self):
        """Analisa especificamente o viés direcional BUY vs SELL"""
        print(f"\n🎯 ANÁLISE DE VIÉS DIRECIONAL")
        print("=" * 50)
        
        # Filtrar sucessos
        sucessos = [r for r in self.resultados if r.get('sucesso') and r.get('acao')]
        falhas = [r for r in self.resultados if not r.get('sucesso') or not r.get('acao')]
        
        print(f"✅ Sinais válidos: {len(sucessos)}")
        print(f"❌ Falhas/Nulos: {len(falhas)}")
        
        if not sucessos:
            print("❌ Nenhum sinal válido para análise de viés!")
            return
        
        # Contar ações
        acoes = {}
        for resultado in sucessos:
            acao = resultado.get('acao', 'UNKNOWN')
            acoes[acao] = acoes.get(acao, 0) + 1
        
        total_validos = len(sucessos)
        
        print(f"\n📊 DISTRIBUIÇÃO DE AÇÕES:")
        for acao, count in acoes.items():
            pct = count / total_validos * 100
            print(f"  {acao}: {count} sinais ({pct:.1f}%)")
        
        # Detectar viés significativo
        buy_count = acoes.get('BUY', 0)
        sell_count = acoes.get('SELL', 0)
        hold_count = acoes.get('HOLD', 0)
        
        if buy_count + sell_count > 0:
            buy_pct = buy_count / (buy_count + sell_count) * 100
            sell_pct = sell_count / (buy_count + sell_count) * 100
            
            print(f"\n🎯 ANÁLISE DE VIÉS BUY vs SELL:")
            print(f"  BUY: {buy_count} ({buy_pct:.1f}%)")
            print(f"  SELL: {sell_count} ({sell_pct:.1f}%)")
            
            # Detectar viés significativo (>70% em uma direção)
            if buy_pct > 70:
                print(f"⚠️  VIÉS DETECTADO: Forte tendência para BUY ({buy_pct:.1f}%)")
            elif sell_pct > 70:
                print(f"⚠️  VIÉS DETECTADO: Forte tendência para SELL ({sell_pct:.1f}%)")
            elif abs(buy_pct - 50) < 15:
                print(f"✅ EQUILIBRADO: Distribuição balanceada BUY/SELL")
            else:
                print(f"🔍 LEVE VIÉS: Tendência moderada para {'BUY' if buy_pct > sell_pct else 'SELL'}")
        
        # Análise por ativo
        print(f"\n📈 VIÉS POR ATIVO:")
        df = pd.DataFrame(sucessos)
        vies_por_ativo = df.groupby('ativo')['acao'].value_counts().unstack(fill_value=0)
        
        for ativo in vies_por_ativo.index:
            buy_count = vies_por_ativo.loc[ativo].get('BUY', 0)
            sell_count = vies_por_ativo.loc[ativo].get('SELL', 0)
            total_ativo = buy_count + sell_count
            
            if total_ativo > 0:
                buy_pct = buy_count / total_ativo * 100
                print(f"  {ativo}: {buy_count}B/{sell_count}S ({buy_pct:.0f}% BUY)")
        
        # Análise por timeframe
        print(f"\n⏰ VIÉS POR TIMEFRAME:")
        vies_por_tf = df.groupby('timeframe')['acao'].value_counts().unstack(fill_value=0)
        
        for tf in vies_por_tf.index:
            buy_count = vies_por_tf.loc[tf].get('BUY', 0)
            sell_count = vies_por_tf.loc[tf].get('SELL', 0)
            total_tf = buy_count + sell_count
            
            if total_tf > 0:
                buy_pct = buy_count / total_tf * 100
                print(f"  {tf}: {buy_count}B/{sell_count}S ({buy_pct:.0f}% BUY)")

    def gerar_grafico_vies(self):
        """Gera gráfico visual do viés direcional"""
        sucessos = [r for r in self.resultados if r.get('sucesso') and r.get('acao')]
        
        if not sucessos:
            print("❌ Nenhum dado para gráfico")
            return
        
        df = pd.DataFrame(sucessos)
        
        # Configurar estilo
        plt.style.use('dark_background')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Pizza geral BUY vs SELL
        acoes = df['acao'].value_counts()
        colors = {'BUY': '#00ff88', 'SELL': '#ff4444', 'HOLD': '#ffaa00'}
        plot_colors = [colors.get(acao, '#cccccc') for acao in acoes.index]
        
        axes[0,0].pie(acoes.values, labels=acoes.index, autopct='%1.1f%%', 
                      colors=plot_colors, startangle=90)
        axes[0,0].set_title('Distribuição Geral BUY vs SELL', fontweight='bold', color='white')
        
        # 2. Viés por ativo
        vies_ativo = df.groupby('ativo')['acao'].value_counts().unstack(fill_value=0)
        vies_ativo[['BUY', 'SELL']].plot(kind='bar', ax=axes[0,1], 
                                        color=['#00ff88', '#ff4444'], alpha=0.8)
        axes[0,1].set_title('BUY vs SELL por Ativo', fontweight='bold', color='white')
        axes[0,1].set_xlabel('Ativo', color='white')
        axes[0,1].set_ylabel('Quantidade', color='white')
        axes[0,1].legend()
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. Viés por timeframe
        vies_tf = df.groupby('timeframe')['acao'].value_counts().unstack(fill_value=0)
        vies_tf[['BUY', 'SELL']].plot(kind='bar', ax=axes[1,0], 
                                     color=['#00ff88', '#ff4444'], alpha=0.8)
        axes[1,0].set_title('BUY vs SELL por Timeframe', fontweight='bold', color='white')
        axes[1,0].set_xlabel('Timeframe', color='white')
        axes[1,0].set_ylabel('Quantidade', color='white')
        axes[1,0].legend()
        
        # 4. Heatmap de viés
        pivot = df.pivot_table(values='confianca', index='ativo', 
                              columns='acao', aggfunc='mean', fill_value=0)
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', 
                   ax=axes[1,1], cbar_kws={'label': 'Confiança Média (%)'})
        axes[1,1].set_title('Confiança por Ativo × Ação', fontweight='bold', color='white')
        
        plt.tight_layout()
        plt.savefig('vies_direcional_buy_sell.png', dpi=300, bbox_inches='tight', facecolor='black')
        plt.show()
        
        print(f"💾 Gráfico salvo: vies_direcional_buy_sell.png")

    def salvar_resultados(self):
        """Salva resultados do teste de viés direcional"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON
        json_file = f"teste_vies_direcional_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, ensure_ascii=False, indent=2)
        
        # CSV
        csv_file = f"teste_vies_direcional_{timestamp}.csv"
        df = pd.DataFrame(self.resultados)
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n💾 Resultados salvos:")
        print(f"  📄 {json_file}")
        print(f"  📊 {csv_file}")

def main():
    testador = TestadorViesDirecional()
    
    try:
        # Executar teste
        testador.executar_teste_vies_direcional()
        
        # Analisar viés
        testador.analisar_vies_direcional()
        
        # Gerar gráfico
        testador.gerar_grafico_vies()
        
        # Salvar resultados
        testador.salvar_resultados()
        
        print(f"\n🎉 TESTE DE VIÉS DIRECIONAL CONCLUÍDO!")
        print(f"🔍 Verifique se há viés excessivo para BUY ou SELL")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Teste interrompido.")
        if testador.resultados:
            testador.analisar_vies_direcional()
            testador.salvar_resultados()

if __name__ == "__main__":
    main()
