#!/usr/bin/env python3
"""
🔥 TESTE COMPARATIVO - ENGINES ENHANCED DE IA
Compara todas as engines enhanced/v3 para escolher a melhor
"""

import sys
import os
import time
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Importar engines enhanced
engines_to_test = []

try:
    from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
    engines_to_test.append(("UltraEnhancedAIEngine", UltraEnhancedAIEngine))
    print("✅ UltraEnhancedAIEngine importada")
except ImportError as e:
    print(f"❌ Erro ao importar UltraEnhancedAIEngine: {e}")

try:
    from ai_engine_v3_otimizado import OptimizedAIEngineV3
    engines_to_test.append(("OptimizedAIEngineV3", OptimizedAIEngineV3))
    print("✅ OptimizedAIEngineV3 importada")
except ImportError as e:
    print(f"❌ Erro ao importar OptimizedAIEngineV3: {e}")

try:
    from ai_engine_enhanced_fixed import AIEngineEnhancedFixed
    engines_to_test.append(("AIEngineEnhancedFixed", AIEngineEnhancedFixed))
    print("✅ AIEngineEnhancedFixed importada")
except ImportError as e:
    print(f"❌ Erro ao importar AIEngineEnhancedFixed: {e}")

try:
    from ai_engine_enhanced import AIEngineEnhanced
    engines_to_test.append(("AIEngineEnhanced", AIEngineEnhanced))
    print("✅ AIEngineEnhanced importada")
except ImportError as e:
    print(f"❌ Erro ao importar AIEngineEnhanced: {e}")

# Engine base para comparação
try:
    from src.ai_engine import AITradingEngine
    engines_to_test.append(("AITradingEngine_Base", AITradingEngine))
    print("✅ AITradingEngine base importada")
except ImportError as e:
    print(f"❌ Erro ao importar AITradingEngine: {e}")

class EnhancedEngineComparator:
    """Comparador específico para engines enhanced"""
    
    def __init__(self):
        self.config = {
            'ai_confidence_threshold': 0.3,  # Threshold mais baixo
            'use_ai': True,
            'candlestick_strength_threshold': 0.5,
            'model_retrain_interval': 50,
            'feature_selection_threshold': 0.05,
            'max_features': 30
        }
        self.results = []
    
    def generate_realistic_data(self, symbol="BTCUSDT", periods=200):
        """Gera dados mais realistas com padrões claros"""
        print(f"📊 Gerando dados realistas para {symbol}...")
        
        dates = pd.date_range(
            start=datetime.now() - timedelta(hours=periods),
            end=datetime.now(),
            freq='1H'
        )
        
        # Criar diferentes cenários de mercado
        scenario = np.random.choice(['bull', 'bear', 'sideways'], p=[0.4, 0.3, 0.3])
        
        if scenario == 'bull':
            # Mercado em alta com volatilidade
            trend = np.linspace(0, 0.3, len(dates))  # 30% de alta
            volatility = 0.02
        elif scenario == 'bear':
            # Mercado em baixa
            trend = np.linspace(0, -0.25, len(dates))  # 25% de queda
            volatility = 0.025
        else:
            # Mercado lateral com oscilações
            trend = np.sin(np.arange(len(dates)) * 0.1) * 0.05
            volatility = 0.015
        
        # Gerar returns com tendência e volatilidade
        np.random.seed(42)
        base_returns = np.random.normal(0.001, volatility, len(dates))
        returns = base_returns + trend / len(dates)
        
        # Adicionar alguns spikes para criar padrões
        for i in range(0, len(returns), 20):
            if np.random.random() > 0.7:
                spike_size = np.random.uniform(0.02, 0.05)
                spike_direction = 1 if np.random.random() > 0.5 else -1
                returns[i:i+3] += spike_direction * spike_size
        
        # Converter para preços OHLCV
        base_price = 50000  # Preço inicial
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # Variação intraday mais realista
            daily_range = price * 0.015  # 1.5% de range diário
            high = price + np.random.uniform(0, daily_range)
            low = price - np.random.uniform(0, daily_range)
            open_price = prices[i-1] if i > 0 else price
            close = price
            
            # Volume correlacionado com volatilidade
            base_volume = 10000
            vol_multiplier = 1 + abs(returns[i]) * 50
            volume = int(base_volume * vol_multiplier)
            
            data.append({
                'timestamp': date,
                'open': open_price,
                'high': max(high, open_price, close),
                'low': min(low, open_price, close),
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        print(f"✅ Dados gerados: {len(df)} períodos, cenário: {scenario}")
        return df, scenario
    
    def test_engine(self, engine_name, engine_class, test_data, scenario):
        """Testa uma engine específica"""
        print(f"\n🔍 Testando {engine_name}...")
        
        result = {
            'engine_name': engine_name,
            'scenario': scenario,
            'success': False,
            'error': None,
            'init_time': 0,
            'analysis_time': 0,
            'signals_generated': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'hold_signals': 0,
            'avg_confidence': 0,
            'max_confidence': 0,
            'min_confidence': 1,
            'features_available': 0,
            'methods_available': 0,
            'enhanced_features': []
        }
        
        try:
            # Inicialização
            start_time = time.time()
            engine = engine_class(self.config)
            result['init_time'] = time.time() - start_time
            
            # Verificar métodos disponíveis
            methods = []
            if hasattr(engine, 'analyze_signals'):
                methods.append('analyze_signals')
            if hasattr(engine, 'generate_signal'):
                methods.append('generate_signal')
            if hasattr(engine, 'predict_signal'):
                methods.append('predict_signal')
            if hasattr(engine, 'create_ultra_features'):
                methods.append('create_ultra_features')
                result['enhanced_features'].append('ultra_features')
            if hasattr(engine, 'create_optimized_features'):
                methods.append('create_optimized_features')
                result['enhanced_features'].append('optimized_features')
            if hasattr(engine, 'ensemble_prediction'):
                methods.append('ensemble_prediction')
                result['enhanced_features'].append('ensemble')
            
            result['methods_available'] = len(methods)
            
            # Análise de sinais
            start_time = time.time()
            signals = []
            confidences = []
            
            # Testar com janelas menores para mais sinais
            for i in range(0, len(test_data) - 50, 10):
                sample_data = test_data.iloc[i:i+50]
                
                try:
                    signal = None
                    
                    # Tentar diferentes métodos
                    if hasattr(engine, 'analyze_signals'):
                        signal = engine.analyze_signals('BTCUSDT', sample_data, 'test')
                    elif hasattr(engine, 'generate_signal'):
                        signal = engine.generate_signal(sample_data, 'BTCUSDT')
                    elif hasattr(engine, 'predict_signal'):
                        signal = engine.predict_signal(sample_data)
                    
                    if signal and isinstance(signal, dict):
                        signals.append(signal)
                        
                        action = signal.get('action', signal.get('signal', 'hold')).lower()
                        confidence = float(signal.get('confidence', 0.5))
                        
                        if action in ['buy', 'long']:
                            result['buy_signals'] += 1
                        elif action in ['sell', 'short']:
                            result['sell_signals'] += 1
                        else:
                            result['hold_signals'] += 1
                        
                        confidences.append(confidence)
                        result['max_confidence'] = max(result['max_confidence'], confidence)
                        result['min_confidence'] = min(result['min_confidence'], confidence)
                
                except Exception as e:
                    print(f"⚠️ Erro na análise #{i}: {str(e)}")
                    continue
            
            result['analysis_time'] = time.time() - start_time
            result['signals_generated'] = len(signals)
            result['avg_confidence'] = np.mean(confidences) if confidences else 0
            result['success'] = True
            
            # Mostrar resultados
            print(f"✅ {engine_name} - OK")
            print(f"   Tempo init: {result['init_time']:.3f}s")
            print(f"   Tempo análise: {result['analysis_time']:.3f}s")
            print(f"   Sinais: {result['signals_generated']} (Buy: {result['buy_signals']}, Sell: {result['sell_signals']}, Hold: {result['hold_signals']})")
            print(f"   Confiança: avg={result['avg_confidence']:.3f}, max={result['max_confidence']:.3f}")
            print(f"   Features enhanced: {result['enhanced_features']}")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ {engine_name} - ERRO: {str(e)}")
        
        return result
    
    def analyze_results(self, results):
        """Analisa e rankeia os resultados"""
        print("\n" + "="*60)
        print("📊 ANÁLISE COMPARATIVA - ENGINES ENHANCED")
        print("="*60)
        
        successful_results = [r for r in results if r['success']]
        
        if not successful_results:
            print("❌ Nenhuma engine funcionou!")
            return
        
        # Calcular scores
        for result in successful_results:
            # Score de performance (velocidade + sinais gerados)
            speed_score = 1000 / (result['analysis_time'] + 0.001)  # Evitar divisão por zero
            signal_score = result['signals_generated'] * 10
            confidence_score = result['avg_confidence'] * 100
            
            # Score de diversidade (não só hold)
            total_signals = result['signals_generated']
            if total_signals > 0:
                diversity_score = ((result['buy_signals'] + result['sell_signals']) / total_signals) * 100
            else:
                diversity_score = 0
            
            # Score de features enhanced
            feature_score = len(result['enhanced_features']) * 20
            
            # Score composto
            result['performance_score'] = speed_score + signal_score + confidence_score
            result['diversity_score'] = diversity_score
            result['feature_score'] = feature_score
            result['total_score'] = result['performance_score'] + result['diversity_score'] + result['feature_score']
        
        # Ordenar por score total
        successful_results.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Mostrar ranking
        print("\n🏆 RANKING DAS ENGINES ENHANCED:")
        for i, result in enumerate(successful_results, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
            print(f"\n{emoji} {result['engine_name']}")
            print(f"   Score Total: {result['total_score']:.1f}")
            print(f"   Performance: {result['performance_score']:.1f}")
            print(f"   Diversidade: {result['diversity_score']:.1f}%")
            print(f"   Features: {result['feature_score']}")
            print(f"   Sinais: {result['signals_generated']} (B:{result['buy_signals']}, S:{result['sell_signals']}, H:{result['hold_signals']})")
            print(f"   Confiança: {result['avg_confidence']:.3f}")
            print(f"   Enhanced: {result['enhanced_features']}")
        
        # Recomendação
        best_engine = successful_results[0]
        print(f"\n🎯 RECOMENDAÇÃO PARA MOBILE/ANDROID:")
        print(f"🏆 Melhor Engine Enhanced: {best_engine['engine_name']}")
        print(f"📊 Score: {best_engine['total_score']:.1f}")
        print(f"⚡ Performance: {best_engine['performance_score']:.1f}")
        print(f"🎲 Diversidade: {best_engine['diversity_score']:.1f}%")
        
        return successful_results
    
    def save_results(self, results):
        """Salva os resultados"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'enhanced_engines_comparison_{timestamp}.json'
        
        # Preparar dados para JSON
        json_results = []
        for result in results:
            json_result = result.copy()
            for key, value in json_result.items():
                if isinstance(value, np.floating):
                    json_result[key] = float(value)
                elif isinstance(value, np.integer):
                    json_result[key] = int(value)
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'test_type': 'enhanced_engines_comparison',
                'results': json_results
            }, f, indent=2)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
        # Criar recomendação
        if results:
            best = results[0]
            with open(f'ENHANCED_ENGINE_RECOMMENDATION_{timestamp}.txt', 'w') as f:
                f.write("🎯 RECOMENDAÇÃO - MELHOR ENGINE ENHANCED\n")
                f.write("="*50 + "\n\n")
                f.write(f"🏆 ENGINE RECOMENDADA: {best['engine_name']}\n")
                f.write(f"📊 Score Total: {best['total_score']:.1f}\n\n")
                f.write("CARACTERÍSTICAS:\n")
                f.write(f"- Performance Score: {best['performance_score']:.1f}\n")
                f.write(f"- Diversidade: {best['diversity_score']:.1f}%\n")
                f.write(f"- Features Enhanced: {best['feature_score']}\n")
                f.write(f"- Sinais Gerados: {best['signals_generated']}\n")
                f.write(f"- Confiança Média: {best['avg_confidence']:.3f}\n")
                f.write(f"- Enhanced Features: {best['enhanced_features']}\n")
    
    def run_comparison(self):
        """Executa a comparação completa"""
        print("🚀 TESTE COMPARATIVO - ENGINES ENHANCED DE IA")
        print("=" * 60)
        
        if not engines_to_test:
            print("❌ Nenhuma engine enhanced disponível para teste!")
            return
        
        print(f"🎯 Testando {len(engines_to_test)} engines enhanced...")
        
        # Gerar dados de teste
        test_data, scenario = self.generate_realistic_data()
        
        # Executar testes
        all_results = []
        for engine_name, engine_class in engines_to_test:
            result = self.test_engine(engine_name, engine_class, test_data, scenario)
            all_results.append(result)
            time.sleep(0.1)  # Pequena pausa entre testes
        
        # Analisar resultados
        successful_results = self.analyze_results(all_results)
        
        # Salvar resultados
        if successful_results:
            self.save_results(successful_results)
        
        return successful_results

def main():
    """Função principal"""
    comparator = EnhancedEngineComparator()
    results = comparator.run_comparison()
    
    print("\n🎉 Teste comparativo de engines enhanced concluído!")
    print("📋 Verifique os arquivos gerados para detalhes completos.")

if __name__ == "__main__":
    main()
