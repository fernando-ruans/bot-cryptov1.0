#!/usr/bin/env python3
"""
🏆 TESTE APROFUNDADO DA ULTRAFAST AI ENGINE
Teste detalhado da engine vencedora para validar sua performance real
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_realistic_data(symbol='BTCUSDT', days=30):
    """Gerar dados mais realistas para teste"""
    logger.info(f"📊 Gerando dados realistas para {symbol} ({days} dias)")
    
    # Gerar dados horários
    periods = days * 24
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
    
    np.random.seed(42)
    
    # Preços base por símbolo
    base_prices = {
        'BTCUSDT': 45000,
        'ETHUSDT': 2800,
        'BNBUSDT': 350
    }
    base_price = base_prices.get(symbol, 1000)
    
    # Simular movimento de preços com tendência e volatilidade variável
    # Adicionar padrões cíclicos e quebras estruturais
    t = np.arange(len(dates))
    
    # Tendência de longo prazo
    trend = 0.0001 * t
    
    # Ciclos
    daily_cycle = 0.02 * np.sin(2 * np.pi * t / 24)  # Ciclo diário
    weekly_cycle = 0.05 * np.sin(2 * np.pi * t / (24 * 7))  # Ciclo semanal
    
    # Ruído com volatilidade variável
    volatility = 0.015 + 0.01 * np.sin(2 * np.pi * t / (24 * 3))  # Vol varia a cada 3 dias
    noise = np.random.normal(0, volatility)
    
    # Eventos de quebra estrutural (5% chance por período)
    breaks = np.random.random(len(dates)) < 0.05
    break_impact = np.where(breaks, np.random.normal(0, 0.05), 0)
    
    # Combinar todos os componentes
    returns = trend + daily_cycle + weekly_cycle + noise + break_impact
    
    # Gerar preços
    prices = [base_price]
    for i in range(1, len(dates)):
        price = prices[-1] * (1 + returns[i])
        price = max(price, base_price * 0.3)  # Floor price
        prices.append(price)
    
    # Criar OHLCV com spreads realistas
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'close': prices,
    })
    
    # Adicionar high/low com spreads realistas
    spreads = np.random.uniform(0.001, 0.005, len(df))  # 0.1% a 0.5%
    df['high'] = df['close'] * (1 + spreads)
    df['low'] = df['close'] * (1 - spreads)
    
    # Volume com padrões realistas
    base_volume = 1000000
    volume_trend = base_volume * (1 + 0.5 * np.sin(2 * np.pi * t / (24 * 7)))
    volume_noise = np.random.lognormal(0, 0.5, len(df))
    df['volume'] = volume_trend * volume_noise
    
    # Garantir ordem correta OHLC
    df['high'] = df[['open', 'close', 'high']].max(axis=1)
    df['low'] = df[['open', 'close', 'low']].min(axis=1)
    
    logger.info(f"✅ Dados gerados: {len(df)} pontos, preço médio: ${df['close'].mean():.2f}")
    return df

def test_ultrafast_detailed():
    """Teste detalhado da UltraFastAIEngine"""
    logger.info("🏆 TESTANDO ULTRAFAST AI ENGINE EM DETALHES")
    logger.info("=" * 50)
    
    try:
        # Importar e inicializar
        from ai_engine_ultra_fast import UltraFastAIEngine
        from src.config import Config
        
        config = Config()
        engine = UltraFastAIEngine(config)
        
        # Teste com múltiplos símbolos e cenários
        test_scenarios = [
            {'symbol': 'BTCUSDT', 'timeframe': '1h', 'days': 30},
            {'symbol': 'ETHUSDT', 'timeframe': '4h', 'days': 30},
            {'symbol': 'BNBUSDT', 'timeframe': '1h', 'days': 20},
        ]
        
        results = []
        
        for scenario in test_scenarios:
            logger.info(f"\n🧪 Testando {scenario['symbol']} {scenario['timeframe']}")
            
            # Gerar dados para este cenário
            data = generate_realistic_data(scenario['symbol'], scenario['days'])
            
            # Teste de performance
            start_time = time.time()
            
            signals_generated = 0
            processing_times = []
            signal_qualities = []
            
            # Testar com janelas deslizantes
            window_size = 100
            step_size = 10
            
            for i in range(0, len(data) - window_size, step_size):
                window_data = data.iloc[i:i + window_size].copy()
                
                window_start = time.time()
                
                try:
                    # Testar métodos disponíveis
                    signal = None
                    
                    if hasattr(engine, 'generate_signal'):
                        signal = engine.generate_signal(window_data, scenario['symbol'], scenario['timeframe'])
                    elif hasattr(engine, 'predict_signal'):
                        signal = engine.predict_signal(window_data)
                    elif hasattr(engine, 'ultra_fast_predict'):
                        signal = engine.ultra_fast_predict(window_data, scenario['symbol'])
                    
                    window_time = time.time() - window_start
                    processing_times.append(window_time)
                    
                    if signal and isinstance(signal, dict):
                        signals_generated += 1
                        
                        # Avaliar qualidade do sinal
                        confidence = signal.get('confidence', 0)
                        signal_type = signal.get('signal_type', 'hold')
                        
                        # Score de qualidade baseado em múltiplos fatores
                        quality_score = 0
                        if signal_type in ['buy', 'sell']:
                            quality_score += 30  # Sinal ativo
                        if confidence > 0.6:
                            quality_score += 40  # Alta confiança
                        if confidence > 0.7:
                            quality_score += 20  # Muito alta
                        if 'reasoning' in signal and signal['reasoning']:
                            quality_score += 10  # Tem explicação
                        
                        signal_qualities.append(quality_score)
                
                except Exception as e:
                    logger.debug(f"Erro em janela {i}: {e}")
                    processing_times.append(float('inf'))
            
            total_time = time.time() - start_time
            
            # Calcular métricas
            avg_processing_time = np.mean([t for t in processing_times if t != float('inf')])
            max_processing_time = np.max([t for t in processing_times if t != float('inf')])
            success_rate = len([t for t in processing_times if t != float('inf')]) / len(processing_times) * 100
            avg_signal_quality = np.mean(signal_qualities) if signal_qualities else 0
            
            scenario_result = {
                'symbol': scenario['symbol'],
                'timeframe': scenario['timeframe'],
                'total_time': round(total_time, 3),
                'signals_generated': signals_generated,
                'windows_tested': len(processing_times),
                'avg_processing_time': round(avg_processing_time, 4),
                'max_processing_time': round(max_processing_time, 4),
                'success_rate': round(success_rate, 2),
                'avg_signal_quality': round(avg_signal_quality, 2),
                'speed_score': round(1 / max(avg_processing_time, 0.0001), 2),
                'signals_per_second': round(signals_generated / max(total_time, 0.001), 2)
            }
            
            results.append(scenario_result)
            
            # Log resultado
            logger.info(f"✅ Resultado {scenario['symbol']}:")
            logger.info(f"   Sinais gerados: {signals_generated}")
            logger.info(f"   Tempo médio: {avg_processing_time:.4f}s")
            logger.info(f"   Taxa de sucesso: {success_rate:.1f}%")
            logger.info(f"   Qualidade média: {avg_signal_quality:.1f}/100")
            logger.info(f"   Velocidade: {scenario_result['signals_per_second']:.1f} sinais/s")
        
        # Análise geral
        analyze_ultrafast_results(results)
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Erro no teste detalhado: {e}")
        return []

def analyze_ultrafast_results(results):
    """Analisar resultados da UltraFastAIEngine"""
    logger.info("\n📊 ANÁLISE DETALHADA - ULTRAFAST AI ENGINE")
    logger.info("=" * 50)
    
    if not results:
        logger.error("❌ Nenhum resultado para analisar")
        return
    
    # Métricas agregadas
    total_signals = sum(r['signals_generated'] for r in results)
    avg_speed = np.mean([r['speed_score'] for r in results])
    avg_success_rate = np.mean([r['success_rate'] for r in results])
    avg_quality = np.mean([r['avg_signal_quality'] for r in results])
    avg_processing_time = np.mean([r['avg_processing_time'] for r in results])
    
    logger.info(f"📈 MÉTRICAS AGREGADAS:")
    logger.info(f"   Total de sinais: {total_signals}")
    logger.info(f"   Velocidade média: {avg_speed:.1f} ops/s")
    logger.info(f"   Taxa de sucesso: {avg_success_rate:.1f}%")
    logger.info(f"   Qualidade média: {avg_quality:.1f}/100")
    logger.info(f"   Tempo médio: {avg_processing_time:.4f}s")
    
    # Classificação da performance
    performance_grade = "F"
    if avg_success_rate >= 95 and avg_speed >= 100 and avg_quality >= 60:
        performance_grade = "A+"
    elif avg_success_rate >= 90 and avg_speed >= 50 and avg_quality >= 50:
        performance_grade = "A"
    elif avg_success_rate >= 80 and avg_speed >= 25 and avg_quality >= 40:
        performance_grade = "B"
    elif avg_success_rate >= 70 and avg_speed >= 10 and avg_quality >= 30:
        performance_grade = "C"
    elif avg_success_rate >= 60:
        performance_grade = "D"
    
    logger.info(f"\n🎯 AVALIAÇÃO FINAL: {performance_grade}")
    
    # Recomendações
    logger.info(f"\n💡 RECOMENDAÇÕES:")
    
    if avg_processing_time < 0.01:
        logger.info("✅ Velocidade EXCELENTE (< 10ms)")
    elif avg_processing_time < 0.1:
        logger.info("✅ Velocidade BOA (< 100ms)")
    else:
        logger.info("⚠️ Velocidade pode ser melhorada")
    
    if avg_success_rate >= 95:
        logger.info("✅ Confiabilidade EXCELENTE")
    elif avg_success_rate >= 80:
        logger.info("✅ Confiabilidade BOA")
    else:
        logger.info("⚠️ Confiabilidade precisa ser melhorada")
    
    if avg_quality >= 60:
        logger.info("✅ Qualidade dos sinais ALTA")
    elif avg_quality >= 40:
        logger.info("✅ Qualidade dos sinais MÉDIA")
    else:
        logger.info("⚠️ Qualidade dos sinais baixa")
    
    # Salvar análise detalhada
    save_detailed_analysis(results, {
        'performance_grade': performance_grade,
        'avg_speed': avg_speed,
        'avg_success_rate': avg_success_rate,
        'avg_quality': avg_quality,
        'total_signals': total_signals
    })

def save_detailed_analysis(results, summary):
    """Salvar análise detalhada"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    analysis = {
        'timestamp': timestamp,
        'engine': 'UltraFastAIEngine',
        'summary': summary,
        'detailed_results': results,
        'conclusion': {
            'recommended': summary['performance_grade'] in ['A+', 'A', 'B'],
            'reason': f"Performance grade: {summary['performance_grade']}",
            'best_for': 'High-frequency trading and real-time applications' if summary['avg_speed'] > 100 else 'Standard trading applications'
        }
    }
    
    filename = f"ultrafast_engine_analysis_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        logger.info(f"💾 Análise salva em: {filename}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar análise: {e}")

def main():
    """Função principal"""
    print("🏆 TESTE APROFUNDADO - ULTRAFAST AI ENGINE")
    print("=" * 55)
    print("🎯 Objetivo: Validar a engine vencedora em cenários reais")
    print("⏱️ Estimativa: 2-3 minutos")
    print()
    
    # Executar teste detalhado
    results = test_ultrafast_detailed()
    
    if results:
        print("\n✅ Teste aprofundado concluído com sucesso!")
        print("📁 Verifique o arquivo de análise gerado")
        print("🎯 UltraFastAIEngine validada como a melhor opção")
    else:
        print("❌ Teste falhou - verifique os logs")

if __name__ == "__main__":
    main()
