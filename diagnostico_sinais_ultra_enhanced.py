#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO DE GERAÇÃO DE SINAIS - UltraEnhancedAIEngine
===========================================================

Script para verificar possíveis erros e inconsistências na geração de sinais:
1. Verificar se métodos existem
2. Testar consistência dos sinais
3. Verificar valores de entrada/saída
4. Identificar possíveis bugs ou problemas

Autor: Sistema de IA  
Data: 17/06/2025
"""

import sys
import os
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
    from src.ai_engine import AITradingEngine
    print("✅ Engines importadas com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar engines: {e}")
    sys.exit(1)

class DiagnosticoSinais:
    def __init__(self):
        """Inicializar diagnóstico"""
        self.problemas_encontrados = []
        self.warnings = []
        self.sucessos = []
        
        # Configuração de teste
        self.config = {
            'ai_engine': {
                'confidence_threshold': 0.65,
                'max_signals_per_hour': 12
            }
        }        
        print("🔍 Iniciando Diagnóstico da UltraEnhancedAIEngine...")

    def gerar_dados_teste(self, periods=150):  # Aumentar para 150 períodos
        """Gerar dados de teste padronizados"""
        np.random.seed(42)  # Para reprodutibilidade
        
        data = []
        base_price = 50000
        
        for i in range(periods):
            change = np.random.normal(0, 0.02)
            base_price *= (1 + change)
            
            spread = base_price * 0.001
            high = base_price * (1 + abs(np.random.normal(0, 0.005)))
            low = base_price * (1 - abs(np.random.normal(0, 0.005)))
            volume = 1000 * np.random.uniform(0.5, 2.0)
            
            data.append({
                'timestamp': int(time.time() * 1000) - (periods - i) * 60000,
                'open': base_price,
                'high': high,
                'low': low,
                'close': base_price,
                'volume': volume
            })
        
        return pd.DataFrame(data)

    def teste_1_verificar_metodos(self):
        """Teste 1: Verificar se todos os métodos necessários existem"""
        print("\n🔧 Teste 1: Verificando Métodos...")
        
        try:
            engine = UltraEnhancedAIEngine(self.config)
            
            # Métodos que devem existir
            metodos_esperados = [
                'ultra_predict_signal',
                'create_ultra_features', 
                'train_ultra_model',
                'predict_signal'  # Método herdado da classe base
            ]
            
            for metodo in metodos_esperados:
                if hasattr(engine, metodo):
                    self.sucessos.append(f"✅ Método {metodo} existe")
                else:
                    self.problemas_encontrados.append(f"❌ Método {metodo} não encontrado")
            
            # Verificar atributos essenciais
            atributos_esperados = [
                'ensemble_models',
                'feature_scalers', 
                'feature_selectors',
                'min_confidence_threshold'
            ]
            
            for attr in atributos_esperados:
                if hasattr(engine, attr):
                    self.sucessos.append(f"✅ Atributo {attr} existe")
                else:
                    self.problemas_encontrados.append(f"❌ Atributo {attr} não encontrado")
                    
        except Exception as e:
            self.problemas_encontrados.append(f"❌ Erro ao inicializar engine: {e}")

    def teste_2_consistencia_sinais(self):
        """Teste 2: Verificar consistência dos sinais gerados"""
        print("\n📊 Teste 2: Testando Consistência dos Sinais...")
        
        try:
            engine = UltraEnhancedAIEngine(self.config)
            df = self.gerar_dados_teste()
            
            sinais_gerados = []
            
            # Gerar múltiplos sinais com os mesmos dados
            for i in range(5):
                resultado = engine.ultra_predict_signal(df, 'BTCUSDT')
                sinais_gerados.append(resultado)
                time.sleep(0.1)
            
            # Verificar consistência
            primeiro_sinal = sinais_gerados[0]
            
            for i, sinal in enumerate(sinais_gerados[1:], 1):
                if sinal.get('signal_type') != primeiro_sinal.get('signal_type'):
                    self.problemas_encontrados.append(
                        f"❌ Inconsistência: Sinal {i+1} difere do primeiro "
                        f"({sinal.get('signal_type')} vs {primeiro_sinal.get('signal_type')})"
                    )
                    
                # Tolerância de 5% na confiança
                conf_diff = abs(sinal.get('confidence', 0) - primeiro_sinal.get('confidence', 0))
                if conf_diff > 0.05:
                    self.warnings.append(
                        f"⚠️ Variação de confiança alta: {conf_diff:.3f}"
                    )
            
            if len(set([s.get('signal_type') for s in sinais_gerados])) == 1:
                self.sucessos.append("✅ Sinais consistentes com mesmos dados")
              # Verificar estrutura dos sinais
            campos_obrigatorios = ['signal_type', 'confidence', 'entry_price']
            for campo in campos_obrigatorios:
                if campo in primeiro_sinal:
                    self.sucessos.append(f"✅ Campo obrigatório {campo} presente")
                else:
                    # Verificar se é um resultado de fallback
                    if 'reason' in primeiro_sinal and 'ai_features' in primeiro_sinal:
                        # É resultado da engine base (fallback)
                        self.warnings.append(f"⚠️ Campo {campo} ausente - Engine usando fallback")
                    else:
                        self.problemas_encontrados.append(f"❌ Campo {campo} ausente")
                    
        except Exception as e:
            self.problemas_encontrados.append(f"❌ Erro no teste de consistência: {e}")

    def teste_3_valores_validos(self):
        """Teste 3: Verificar se valores estão dentro de ranges válidos"""
        print("\n🎯 Teste 3: Verificando Valores Válidos...")
        
        try:
            engine = UltraEnhancedAIEngine(self.config)
            df = self.gerar_dados_teste()
            
            # Testar com diferentes símbolos
            simbolos_teste = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
            
            for simbolo in simbolos_teste:
                resultado = engine.ultra_predict_signal(df, simbolo)
                
                # Verificar confiança (0-1)
                confidence = resultado.get('confidence', 0)
                if 0 <= confidence <= 1:
                    self.sucessos.append(f"✅ {simbolo}: Confiança válida ({confidence:.3f})")
                else:
                    self.problemas_encontrados.append(
                        f"❌ {simbolo}: Confiança inválida ({confidence})"
                    )
                  # Verificar tipo de sinal
                signal_type = resultado.get('signal_type', resultado.get('signal', ''))
                if signal_type in ['BUY', 'SELL', 'HOLD', 'buy', 'sell', 'hold']:
                    self.sucessos.append(f"✅ {simbolo}: Tipo de sinal válido ({signal_type})")
                else:
                    self.problemas_encontrados.append(
                        f"❌ {simbolo}: Tipo de sinal inválido ({signal_type})"
                    )
                
                # Verificar preços
                entry_price = resultado.get('entry_price', 0)
                stop_loss = resultado.get('stop_loss', 0)
                take_profit = resultado.get('take_profit', 0)
                
                if entry_price > 0:
                    self.sucessos.append(f"✅ {simbolo}: Preço de entrada válido")
                      # Verificar lógica de SL/TP para BUY/SELL
                    signal_type_upper = signal_type.upper()
                    if signal_type_upper == 'BUY':
                        if stop_loss > 0 and stop_loss < entry_price:
                            self.sucessos.append(f"✅ {simbolo}: Stop Loss BUY correto")
                        elif stop_loss > 0:
                            self.problemas_encontrados.append(
                                f"❌ {simbolo}: Stop Loss BUY incorreto (SL: {stop_loss}, Entry: {entry_price})"
                            )
                            
                        if take_profit > 0 and take_profit > entry_price:
                            self.sucessos.append(f"✅ {simbolo}: Take Profit BUY correto")
                        elif take_profit > 0:
                            self.problemas_encontrados.append(
                                f"❌ {simbolo}: Take Profit BUY incorreto (TP: {take_profit}, Entry: {entry_price})"
                            )
                    
                    elif signal_type_upper == 'SELL':
                        if stop_loss > 0 and stop_loss > entry_price:
                            self.sucessos.append(f"✅ {simbolo}: Stop Loss SELL correto")
                        elif stop_loss > 0:
                            self.problemas_encontrados.append(
                                f"❌ {simbolo}: Stop Loss SELL incorreto (SL: {stop_loss}, Entry: {entry_price})"
                            )
                            
                        if take_profit > 0 and take_profit < entry_price:
                            self.sucessos.append(f"✅ {simbolo}: Take Profit SELL correto")
                        elif take_profit > 0:
                            self.problemas_encontrados.append(
                                f"❌ {simbolo}: Take Profit SELL incorreto (TP: {take_profit}, Entry: {entry_price})"
                            )
                else:
                    self.problemas_encontrados.append(f"❌ {simbolo}: Preço de entrada inválido")
                    
        except Exception as e:
            self.problemas_encontrados.append(f"❌ Erro no teste de valores: {e}")

    def teste_4_fallback_funcionando(self):
        """Teste 4: Verificar se fallback funciona corretamente"""
        print("\n🔄 Teste 4: Testando Sistema de Fallback...")
        
        try:
            engine = UltraEnhancedAIEngine(self.config)
            
            # Criar dados inválidos para forçar fallback
            df_invalido = pd.DataFrame({
                'timestamp': [1],
                'open': [np.nan],
                'high': [np.nan], 
                'low': [np.nan],
                'close': [np.nan],
                'volume': [np.nan]
            })
            
            resultado = engine.ultra_predict_signal(df_invalido, 'BTCUSDT')
            
            if resultado is not None:
                self.sucessos.append("✅ Sistema de fallback funcionando")
                
                # Verificar se tem estrutura básica
                if 'signal_type' in resultado and 'confidence' in resultado:
                    self.sucessos.append("✅ Fallback retorna estrutura válida")
                else:
                    self.problemas_encontrados.append("❌ Fallback não retorna estrutura válida")
            else:
                self.problemas_encontrados.append("❌ Fallback retorna None")
                
        except Exception as e:
            self.problemas_encontrados.append(f"❌ Erro no teste de fallback: {e}")

    def teste_5_performance_memoria(self):
        """Teste 5: Verificar performance e uso de memória"""
        print("\n⚡ Teste 5: Testando Performance...")
        
        try:
            engine = UltraEnhancedAIEngine(self.config)
            df = self.gerar_dados_teste(100)  # Dados maiores
            
            tempos = []
            
            # Múltiplas execuções para medir performance
            for i in range(10):
                start_time = time.time()
                resultado = engine.ultra_predict_signal(df, 'BTCUSDT')
                end_time = time.time()
                
                tempo_execucao = end_time - start_time
                tempos.append(tempo_execucao)
            
            tempo_medio = sum(tempos) / len(tempos)
            tempo_max = max(tempos)
            tempo_min = min(tempos)
            
            # Verificar performance
            if tempo_medio < 0.5:  # Menos de 500ms
                self.sucessos.append(f"✅ Performance adequada (média: {tempo_medio:.3f}s)")
            else:
                self.warnings.append(f"⚠️ Performance lenta (média: {tempo_medio:.3f}s)")
            
            if tempo_max > 1.0:  # Mais de 1 segundo
                self.warnings.append(f"⚠️ Pico de latência alto ({tempo_max:.3f}s)")
            
            # Verificar variação de performance
            variacao = (tempo_max - tempo_min) / tempo_medio
            if variacao > 0.5:  # 50% de variação
                self.warnings.append(f"⚠️ Performance inconsistente (variação: {variacao:.1%})")
            else:
                self.sucessos.append("✅ Performance consistente")
                
        except Exception as e:
            self.problemas_encontrados.append(f"❌ Erro no teste de performance: {e}")

    def executar_diagnostico_completo(self):
        """Executar todos os testes de diagnóstico"""
        print("🔍 DIAGNÓSTICO COMPLETO DA UltraEnhancedAIEngine")
        print("=" * 60)
        
        # Executar todos os testes
        self.teste_1_verificar_metodos()
        self.teste_2_consistencia_sinais() 
        self.teste_3_valores_validos()
        self.teste_4_fallback_funcionando()
        self.teste_5_performance_memoria()
        
        # Gerar relatório
        self.gerar_relatorio()

    def gerar_relatorio(self):
        """Gerar relatório final do diagnóstico"""
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO DE DIAGNÓSTICO")
        print("=" * 60)
        
        total_problemas = len(self.problemas_encontrados)
        total_warnings = len(self.warnings)
        total_sucessos = len(self.sucessos)
        
        print(f"\n📊 RESUMO:")
        print(f"   ✅ Sucessos: {total_sucessos}")
        print(f"   ⚠️  Warnings: {total_warnings}")
        print(f"   ❌ Problemas: {total_problemas}")
        
        # Mostrar sucessos
        if self.sucessos:
            print(f"\n✅ SUCESSOS ({len(self.sucessos)}):")
            for sucesso in self.sucessos:
                print(f"   {sucesso}")
        
        # Mostrar warnings
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        # Mostrar problemas
        if self.problemas_encontrados:
            print(f"\n❌ PROBLEMAS ENCONTRADOS ({len(self.problemas_encontrados)}):")
            for problema in self.problemas_encontrados:
                print(f"   {problema}")
        
        # Avaliação geral
        print(f"\n🎯 AVALIAÇÃO GERAL:")
        
        if total_problemas == 0:
            if total_warnings == 0:
                print("   🏆 EXCELENTE - Nenhum problema encontrado!")
            elif total_warnings <= 2:
                print("   ✅ MUITO BOM - Apenas warnings menores")
            else:
                print("   ⚠️ BOM - Vários warnings para revisar")
        elif total_problemas <= 2:
            print("   ⚠️ REGULAR - Poucos problemas encontrados")
        else:
            print("   ❌ CRÍTICO - Muitos problemas precisam ser corrigidos")
        
        # Salvar relatório
        self.salvar_relatorio()

    def salvar_relatorio(self):
        """Salvar relatório em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diagnostico_sinais_{timestamp}.json"
        
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'engine': 'UltraEnhancedAIEngine',
            'sucessos': self.sucessos,
            'warnings': self.warnings,
            'problemas': self.problemas_encontrados,
            'resumo': {
                'total_sucessos': len(self.sucessos),
                'total_warnings': len(self.warnings),
                'total_problemas': len(self.problemas_encontrados)
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {filename}")

def main():
    """Função principal"""
    diagnostico = DiagnosticoSinais()
    diagnostico.executar_diagnostico_completo()

if __name__ == "__main__":
    main()
