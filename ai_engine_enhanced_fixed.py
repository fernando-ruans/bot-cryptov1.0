#!/usr/bin/env python3
"""
🚀 AI ENGINE MELHORADO - Versão com Features Avançadas CORRIGIDA
Implementação das principais melhorias para aumentar acertividade
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
import warnings
from datetime import datetime

# Suprimir warnings da biblioteca TA-Lib para melhor experiência do usuário
warnings.filterwarnings('ignore', category=RuntimeWarning, module='ta')
warnings.filterwarnings('ignore', category=FutureWarning, module='ta')

# Importar classes originais
from src.ai_engine import AITradingEngine

logger = logging.getLogger(__name__)

# Importar o enhancer de confiança
try:
    from melhorias_confianca_sinais import SignalConfidenceEnhancer
    CONFIDENCE_ENHANCER_AVAILABLE = True
except ImportError:
    CONFIDENCE_ENHANCER_AVAILABLE = False
    logger.warning("⚠️ SignalConfidenceEnhancer não disponível")

class EnhancedAIEngine(AITradingEngine):
    """AI Engine melhorado com features avançadas"""
    
    def __init__(self, config):
        super().__init__(config)
        self.enhanced_features_enabled = True
        
        # Inicializar enhancer de confiança se disponível
        if CONFIDENCE_ENHANCER_AVAILABLE:
            self.confidence_enhancer = SignalConfidenceEnhancer(config)
            logger.info("✅ SignalConfidenceEnhancer inicializado")
        else:
            self.confidence_enhancer = None
            logger.warning("⚠️ SignalConfidenceEnhancer não disponível - usando confiança padrão")
        
        # Timeframe atual (usado para melhorias de confiança)
        self.current_timeframe = '1h'
    
    def set_timeframe(self, timeframe: str):
        """Definir o timeframe atual para análise"""
        self.current_timeframe = timeframe
        logger.info(f"🕒 Timeframe definido: {timeframe}")
        
    def create_enhanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Criar features avançadas para melhorar predições"""
        
        try:
            # Features básicas primeiro - usar método da classe pai
            df = super().create_features(df)
            
            if not self.enhanced_features_enabled:
                return df
            
            logger.info("🚀 Criando features avançadas...")
            
            # =================================================================
            # 📊 1. MULTI-TIMEFRAME FEATURES
            # =================================================================
            
            # Tendência de diferentes períodos
            for period in [5, 10, 20, 50]:
                if len(df) >= period:
                    df[f'trend_{period}'] = (df['close'] > df['close'].shift(period)).astype(int)
                    df[f'trend_strength_{period}'] = (df['close'] / df['close'].shift(period) - 1) * 100
            
            # =================================================================
            # 🔊 2. VOLUME FEATURES AVANÇADAS
            # =================================================================
            
            # On-Balance Volume (OBV)
            df['obv'] = 0.0
            for i in range(1, len(df)):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    df['obv'].iloc[i] = df['obv'].iloc[i-1] + df['volume'].iloc[i]
                elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                    df['obv'].iloc[i] = df['obv'].iloc[i-1] - df['volume'].iloc[i]
                else:
                    df['obv'].iloc[i] = df['obv'].iloc[i-1]
            
            # Volume-Price Trend (VPT)
            df['vpt'] = (df['volume'] * df['close'].pct_change()).cumsum()
            
            # Volume Rate of Change
            df['volume_roc'] = df['volume'].pct_change(periods=10) * 100
            
            # Volume vs Moving Average
            df['volume_ma_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
            
            # Price-Volume Divergence
            df['pv_divergence'] = (df['close'].pct_change() * df['volume'].pct_change())
            
            # =================================================================
            # 🕯️ 3. CANDLESTICK PATTERNS
            # =================================================================
            
            # Tamanho do corpo da vela
            df['body_size'] = abs(df['close'] - df['open'])
            df['total_size'] = df['high'] - df['low']
            df['body_ratio'] = df['body_size'] / df['total_size']
            
            # Sombras
            df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
            df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
            
            # Padrões simples
            df['is_hammer'] = (
                (df['lower_shadow'] > 2 * df['body_size']) & 
                (df['upper_shadow'] < 0.1 * df['body_size']) &
                (df['body_size'] > 0)
            ).astype(int)
            
            df['is_doji'] = (df['body_size'] < 0.1 * df['total_size']).astype(int)
            
            df['is_shooting_star'] = (
                (df['upper_shadow'] > 2 * df['body_size']) & 
                (df['lower_shadow'] < 0.1 * df['body_size']) &
                (df['body_size'] > 0)
            ).astype(int)
            
            # =================================================================
            # 🧠 4. MOMENTUM AVANÇADO
            # =================================================================
            
            # Rate of Change em múltiplos períodos
            for period in [3, 7, 14, 21]:
                if len(df) >= period:
                    df[f'roc_{period}'] = ((df['close'] - df['close'].shift(period)) / 
                                         df['close'].shift(period)) * 100
            
            # Acceleration (segunda derivada do preço)
            df['acceleration'] = df['close'].diff().diff()
            
            # Momentum Score (combinação de múltiplos momentums)
            momentum_cols = [col for col in df.columns if 'roc_' in col]
            if momentum_cols:
                df['momentum_score'] = df[momentum_cols].mean(axis=1)
            
            # =================================================================
            # 📈 5. VOLATILITY FEATURES
            # =================================================================
            
            # True Range
            df['tr'] = np.maximum(
                df['high'] - df['low'],
                np.maximum(
                    abs(df['high'] - df['close'].shift(1)),
                    abs(df['low'] - df['close'].shift(1))
                )
            )
            
            # Average True Range
            df['atr'] = df['tr'].rolling(14).mean()
            df['atr_percent'] = (df['atr'] / df['close']) * 100
            
            # Volatility Ratio
            df['volatility_ratio'] = df['atr'] / df['atr'].rolling(50).mean()
            
            # =================================================================
            # 🎯 6. REGIME DETECTION
            # =================================================================
            
            # Bull/Bear Market Detection
            ma200 = df['close'].rolling(200).mean()
            df['above_ma200'] = (df['close'] > ma200).astype(int)
            df['bull_bear_regime'] = df['above_ma200'].rolling(20).mean()  # 0-1 score
            
            # Trend Strength
            df['trend_strength'] = abs(df['close'] / ma200 - 1) * 100
            
            # Market Regime Score
            df['market_regime'] = np.where(
                df['bull_bear_regime'] > 0.7, 1,      # Bull
                np.where(df['bull_bear_regime'] < 0.3, -1, 0)  # Bear, Sideways
            )
            
            # =================================================================
            # ⏰ 7. TEMPORAL FEATURES
            # =================================================================
            
            # Time-based features
            df['hour'] = pd.to_datetime(df.index).hour
            df['day_of_week'] = pd.to_datetime(df.index).dayofweek
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            
            # Session-based (simplificado)
            df['asian_session'] = ((df['hour'] >= 0) & (df['hour'] < 8)).astype(int)
            df['london_session'] = ((df['hour'] >= 8) & (df['hour'] < 16)).astype(int)
            df['ny_session'] = ((df['hour'] >= 16) & (df['hour'] < 24)).astype(int)
            
            # =================================================================
            # 📊 8. ENSEMBLE FEATURES
            # =================================================================
            
            # Combinar sinais de diferentes indicadores
            technical_signals = []
            
            # RSI signal
            if 'rsi_14' in df.columns:
                df['rsi_signal'] = np.where(df['rsi_14'] > 70, -1, 
                                  np.where(df['rsi_14'] < 30, 1, 0))
                technical_signals.append('rsi_signal')
            
            # MACD signal
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                df['macd_signal_cross'] = np.where(
                    df['macd'] > df['macd_signal'], 1, -1
                )
                technical_signals.append('macd_signal_cross')
            
            # MA Cross signal
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                df['ma_cross_signal'] = np.where(
                    df['sma_20'] > df['sma_50'], 1, -1
                )
                technical_signals.append('ma_cross_signal')
            
            # Ensemble Technical Score
            if technical_signals:
                df['technical_ensemble'] = df[technical_signals].mean(axis=1)
            
            # =================================================================
            # 🔄 9. FEATURE INTERACTIONS
            # =================================================================
            
            # Volume-Price Interaction
            df['volume_price_momentum'] = df['volume_roc'] * df['roc_7']
            
            # Volatility-Momentum Interaction  
            if 'momentum_score' in df.columns:
                df['vol_momentum_interaction'] = df['volatility_ratio'] * df['momentum_score']
            
            # Regime-Technical Interaction
            if 'technical_ensemble' in df.columns:
                df['regime_technical'] = df['market_regime'] * df['technical_ensemble']
            
            logger.info(f"✅ Features avançadas criadas: {len(df.columns)} colunas totais")
            
            # Limpar NaN e infinitos
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao criar features avançadas: {e}")
            return df
    
    def enhanced_predict_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Predição melhorada usando features avançadas"""
        
        try:
            # Usar features avançadas
            df_enhanced = self.create_enhanced_features(df)
            
            # Se não há modelo treinado, treinar com features avançadas
            if symbol not in self.models:
                logger.info(f"🧠 Treinando modelo avançado para {symbol}...")
                training_result = self.train_enhanced_model(df_enhanced, symbol)
                if not training_result.get('success', False):
                    logger.warning(f"⚠️ Fallback para predição normal")
                    return super().predict_signal(df, symbol)
            
            # Predição normal com features avançadas
            result = super().predict_signal(df_enhanced, symbol)
            
            # Adicionar análise de regime para ajustar confiança
            if 'market_regime' in df_enhanced.columns:
                regime = df_enhanced['market_regime'].iloc[-1]
                signal_value = result.get('signal', 0)
                
                # Ajustar confiança baseado no regime
                confidence_adjustment = 1.0
                if regime == 1 and signal_value == 1:  # Bull market + Buy signal
                    confidence_adjustment = 1.2
                elif regime == -1 and signal_value == 0:  # Bear market + Sell signal
                    confidence_adjustment = 1.2
                elif regime == 0:  # Sideways market
                    confidence_adjustment = 0.8
                
                # Aplicar ajuste
                original_confidence = result.get('confidence', 0.5)
                adjusted_confidence = min(original_confidence * confidence_adjustment, 0.95)
                result['confidence'] = adjusted_confidence
                result['regime_adjusted'] = True
                result['market_regime'] = 'bull' if regime == 1 else 'bear' if regime == -1 else 'sideways'
            
            # === APLICAR MELHORIAS DE CONFIANÇA ===
            if self.confidence_enhancer is not None:
                try:
                    logger.info(f"🎯 Aplicando melhorias de confiança para {symbol}")
                    # Usar timeframe atual
                    timeframe = self.current_timeframe
                    result = self.confidence_enhancer.enhance_signal_confidence(
                        result, df_enhanced, symbol, timeframe
                    )
                    logger.info(f"✅ Confiança melhorada aplicada")
                except Exception as e:
                    logger.error(f"❌ Erro ao aplicar melhorias de confiança: {e}")
                    # Continuar com resultado original se houver erro
            
            result['enhanced'] = True
            return result
            
        except Exception as e:
            logger.error(f"Erro na predição avançada: {e}")
            return super().predict_signal(df, symbol)
    
    def train_enhanced_model(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Treinar modelo com features avançadas"""
        
        try:
            logger.info(f"🚀 Treinamento avançado para {symbol}")
            
            # Usar o método de treinamento original mas com mais features
            result = super().train_model(df, symbol)
            
            if result.get('success', False):
                logger.info(f"✅ Modelo avançado treinado para {symbol}")
                logger.info(f"📊 Features utilizadas: {len(df.select_dtypes(include=[np.number]).columns)}")
                
            return result
            
        except Exception as e:
            logger.error(f"Erro no treinamento avançado: {e}")
            return {'success': False, 'error': str(e)}

# =================================================================
# 🧪 TESTE DO ENGINE MELHORADO
# =================================================================

def test_enhanced_engine():
    """Testar o engine melhorado"""
    
    print("🚀 TESTANDO AI ENGINE MELHORADO")
    print("=" * 50)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        
        config = Config()
        market_data = MarketDataManager(config)
        enhanced_ai = EnhancedAIEngine(config)
        
        # Testar com BTCUSDT
        symbol = 'BTCUSDT'
        print(f"\n🔍 Testando {symbol}...")
        
        df = market_data.get_historical_data(symbol, '1h', 200)
        if df is not None and len(df) >= 100:
            
            # Criar features avançadas
            df_enhanced = enhanced_ai.create_enhanced_features(df)
            print(f"📊 Features criadas: {len(df_enhanced.columns)} (vs {len(df.columns)} original)")
            
            # Features avançadas detectadas
            advanced_features = [col for col in df_enhanced.columns if col not in df.columns]
            print(f"🆕 Novas features: {len(advanced_features)}")
            
            # Fazer predição melhorada
            result = enhanced_ai.enhanced_predict_signal(df, symbol)
            print(f"🎯 Predição: {result.get('signal_type', 'N/A')}")
            print(f"📈 Confiança: {result.get('confidence', 0):.3f}")
            print(f"🏷️ Modelo: {result.get('model_used', 'N/A')}")
            print(f"🔄 Melhorado: {result.get('enhanced', False)}")
            print(f"📊 Regime: {result.get('market_regime', 'N/A')}")
            
        else:
            print("❌ Dados insuficientes para teste")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    print("\n" + "=" * 50)
    print("📋 MELHORIAS IMPLEMENTADAS:")
    print("✅ Multi-timeframe trend analysis")  
    print("✅ Advanced volume indicators (OBV, VPT)")
    print("✅ Candlestick pattern detection")
    print("✅ Enhanced momentum features")
    print("✅ Volatility analysis (ATR)")
    print("✅ Market regime detection")
    print("✅ Temporal features")
    print("✅ Feature interactions")
    print("✅ Regime-based confidence adjustment")
    print("✅ SignalConfidenceEnhancer integration")

if __name__ == "__main__":
    test_enhanced_engine()
