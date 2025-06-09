#!/usr/bin/env python3
"""
Script de debug para diagnosticar problemas na geração de sinais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.ai_engine import AITradingEngine
import logging

# Configurar logging detalhado
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def debug_signal_generation():
    """Debug completo da geração de sinais"""
    print("🔍 INICIANDO DEBUG DA GERAÇÃO DE SINAIS")
    print("=" * 50)
    
    try:
        # Inicializar componentes
        print("1. Inicializando componentes...")
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        # Verificar configurações
        print("\n2. Verificando configurações:")
        print(f"   Min Confidence: {config.SIGNAL_CONFIG['min_confidence']:.1%}")
        print(f"   Cooldown: {config.SIGNAL_CONFIG['signal_cooldown_minutes']} min")
        print(f"   Confluence: {config.SIGNAL_CONFIG['enable_confluence']}")
        print(f"   Min Confluence Count: {config.SIGNAL_CONFIG['min_confluence_count']}")
        
        # Verificar dados de mercado
        print("\n3. Testando dados de mercado:")
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        current_price = market_data.get_current_price(symbol)
        print(f"   Preço atual {symbol}: ${current_price}")
        
        if current_price is None:
            print("   ❌ ERRO: Não conseguiu obter preço atual!")
            return
        
        # Obter dados históricos
        print("\n4. Obtendo dados históricos:")
        df = market_data.get_market_data(symbol, timeframe, 100)
        if df is None or df.empty:
            print("   ❌ ERRO: Dados históricos não obtidos!")
            return
        
        print(f"   ✅ Dados obtidos: {len(df)} candles")
        print(f"   Último preço nos dados: ${df['close'].iloc[-1]:.2f}")
        
        # Debug do gerador de sinais linha por linha
        print("\n5. Debug detalhado da geração de sinal:")
        
        # Verificar cooldown
        is_cooldown = signal_generator._is_in_cooldown(symbol)
        print(f"   Cooldown ativo: {is_cooldown}")
        
        if is_cooldown:
            print("   ❌ SINAL BLOQUEADO POR COOLDOWN!")
            # Forçar reset do cooldown para teste
            if symbol in signal_generator.last_signal_time:
                del signal_generator.last_signal_time[symbol]
            print("   ✅ Cooldown resetado para teste")
        
        # Verificar análise técnica
        print("\n6. Testando análise técnica:")
        try:
            technical_result = signal_generator._analyze_technical_indicators(df, symbol)
            print(f"   Resultado técnico: {technical_result}")
            
            if technical_result['signal'] == 'hold':
                print("   ⚠️ Análise técnica resultou em 'hold'")
                
                # Vamos forçar condições mais agressivas temporariamente
                print("\n7. Aplicando configurações ultra-agressivas:")
                
                # Modificar config temporariamente
                config.SIGNAL_CONFIG['min_confidence'] = 0.01  # 1%
                config.SIGNAL_CONFIG['signal_cooldown_minutes'] = 0
                config.SIGNAL_CONFIG['enable_confluence'] = False
                signal_generator.config = config
                
                print("   ✅ Configurações ultra-agressivas aplicadas")
                
                # Tentar novamente
                print("\n8. Tentativa com configurações agressivas:")
                signal = signal_generator.generate_signal(symbol, timeframe)
                
                if signal:
                    print(f"   🎯 SINAL GERADO COM SUCESSO!")
                    print(f"   Tipo: {signal.signal_type}")
                    print(f"   Confiança: {signal.confidence:.1%}")
                    print(f"   Preço entrada: ${signal.entry_price}")
                    print(f"   Stop Loss: ${signal.stop_loss}")
                    print(f"   Take Profit: ${signal.take_profit}")
                    print(f"   Razões: {signal.reasons}")
                else:
                    print("   ❌ AINDA NÃO GEROU SINAL")
                    
                    # Debug ainda mais profundo
                    print("\n9. Debug profundo dos indicadores:")
                    
                    # Verificar RSI
                    from src.technical_indicators import TechnicalIndicators
                    tech_indicators = TechnicalIndicators()
                    
                    rsi = tech_indicators.calculate_rsi(df, 14)
                    current_rsi = rsi.iloc[-1] if not rsi.empty else None
                    print(f"   RSI atual: {current_rsi:.2f}" if current_rsi else "   RSI: N/A")
                    
                    # Verificar MACD
                    macd_line, macd_signal, macd_hist = tech_indicators.calculate_macd(df)
                    if not macd_line.empty:
                        print(f"   MACD: {macd_line.iloc[-1]:.4f}")
                        print(f"   MACD Signal: {macd_signal.iloc[-1]:.4f}")
                        print(f"   MACD Hist: {macd_hist.iloc[-1]:.4f}")
                    
                    # Verificar Bollinger Bands
                    bb_upper, bb_middle, bb_lower = tech_indicators.calculate_bollinger_bands(df)
                    current_price_df = df['close'].iloc[-1]
                    if not bb_upper.empty:
                        print(f"   BB Upper: ${bb_upper.iloc[-1]:.2f}")
                        print(f"   BB Lower: ${bb_lower.iloc[-1]:.2f}")
                        print(f"   Preço atual vs BB: {current_price_df:.2f}")
                        
                        # Forçar sinal baseado em condições extremas
                        print("\n10. FORÇANDO GERAÇÃO DE SINAL:")
                        force_signal_type = 'buy' if current_rsi and current_rsi < 50 else 'sell'
                        
                        from src.signal_generator import Signal
                        from datetime import datetime
                        
                        forced_signal = Signal(
                            symbol=symbol,
                            signal_type=force_signal_type,
                            confidence=0.75,  # 75% de confiança forçada
                            entry_price=current_price,
                            stop_loss=current_price * (0.98 if force_signal_type == 'buy' else 1.02),
                            take_profit=current_price * (1.04 if force_signal_type == 'buy' else 0.96),
                            timeframe=timeframe,
                            timestamp=datetime.now(),
                            reasons=[
                                "Sinal forçado para debug",
                                f"RSI: {current_rsi:.1f}" if current_rsi else "RSI indisponível",
                                f"Preço: ${current_price:.2f}",
                                "Configurações ultra-agressivas aplicadas"
                            ]
                        )
                        
                        # Registrar o sinal forçado
                        signal_generator._register_signal(forced_signal)
                        
                        print(f"   🚀 SINAL FORÇADO CRIADO!")
                        print(f"   Tipo: {forced_signal.signal_type}")
                        print(f"   Confiança: {forced_signal.confidence:.1%}")
                        print(f"   ID: {forced_signal.id}")
            else:
                print(f"   ✅ Análise técnica OK: {technical_result['signal']}")
                
        except Exception as e:
            print(f"   ❌ ERRO na análise técnica: {e}")
            import traceback
            traceback.print_exc()
        
        # Verificar sinais ativos
        print("\n11. Verificando sinais ativos:")
        active_signals = signal_generator.get_active_signals()
        print(f"   Sinais ativos: {len(active_signals)}")
        
        if active_signals:
            for signal in active_signals[-3:]:  # Últimos 3
                print(f"   - {signal['symbol']} {signal['signal_type']} ({signal['confidence']:.1%})")
        
        print("\n🏁 DEBUG CONCLUÍDO!")
        return active_signals
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_signal_generation()
