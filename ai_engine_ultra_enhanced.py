#!/usr/bin/env python3
"""
🚀 AI ENGINE ULTRA MELHORADO - Foco em Alta Precisão (70%+)
Sistema de IA reformulado para atingir alta taxa de acerto
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importar bibliotecas de ML avançadas
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
    from sklearn.model_selection import cross_val_score, GridSearchCV
    from sklearn.preprocessing import StandardScaler, RobustScaler
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn.metrics import accuracy_score, classification_report
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Importar classe original
from src.ai_engine import AITradingEngine

logger = logging.getLogger(__name__)

class UltraEnhancedAIEngine(AITradingEngine):
    """AI Engine ultra melhorado focado em alta precisão"""
    
    def __init__(self, config):
        super().__init__(config)
        self.ultra_features_enabled = True
        self.min_confidence_threshold = 0.55  # Threshold mais baixo para ser menos conservador
        self.ensemble_models = {}
        self.feature_scalers = {}
        self.feature_selectors = {}
        
        # Configurações avançadas
        self.lookback_periods = [3, 5, 8, 13, 21]  # Fibonacci
        self.volume_periods = [5, 10, 20]
        self.volatility_periods = [7, 14, 21]
        
    def create_ultra_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Criar conjunto ultra avançado de features"""
        
        try:
            logger.info("🚀 Criando features ultra avançadas...")
            
            if len(df) < 50:  # Mínimo de dados necessário
                logger.warning("⚠️ Dados insuficientes para features avançadas")
                return df
            
            # =================================================================
            # 📊 1. FEATURES BÁSICAS DE PREÇO
            # =================================================================
            
            # Médias móveis essenciais
            for period in [5, 10, 20, 50]:
                if len(df) >= period:
                    df[f'sma_{period}'] = df['close'].rolling(period).mean()
                    df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
                    
                    # Posição relativa às médias
                    df[f'above_sma_{period}'] = (df['close'] > df[f'sma_{period}']).astype(int)
                    df[f'above_ema_{period}'] = (df['close'] > df[f'ema_{period}']).astype(int)
                    
                    # Distância percentual das médias
                    df[f'dist_sma_{period}'] = ((df['close'] - df[f'sma_{period}']) / df['close']) * 100
            
            # Rate of Change multi-período
            for period in [3, 5, 10, 20]:
                if len(df) >= period:
                    df[f'roc_{period}'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
            
            # Momentum Score
            roc_cols = [col for col in df.columns if 'roc_' in col]
            if len(roc_cols) >= 2:
                df['momentum_score'] = df[roc_cols].mean(axis=1)
                df['momentum_strength'] = df[roc_cols].std(axis=1)
            
            # =================================================================
            # 📈 2. INDICADORES TÉCNICOS OTIMIZADOS
            # =================================================================
            
            # RSI melhorado
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss + 1e-8)
            df['rsi'] = 100 - (100 / (1 + rs))
            df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
            df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
            df['rsi_neutral'] = ((df['rsi'] >= 40) & (df['rsi'] <= 60)).astype(int)
            
            # MACD avançado
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            df['macd'] = ema12 - ema26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            df['macd_bullish'] = (df['macd'] > df['macd_signal']).astype(int)
            df['macd_crossover'] = ((df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int)
            
            # Bollinger Bands com squeeze detection
            bb_period = 20
            bb_std = 2
            bb_middle = df['close'].rolling(bb_period).mean()
            bb_std_dev = df['close'].rolling(bb_period).std()
            df['bb_upper'] = bb_middle + (bb_std_dev * bb_std)
            df['bb_lower'] = bb_middle - (bb_std_dev * bb_std)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'] + 1e-8)
            df['bb_squeeze'] = (bb_std_dev < bb_std_dev.rolling(20).mean()).astype(int)
            df['bb_breakout_up'] = (df['close'] > df['bb_upper']).astype(int)
            df['bb_breakout_down'] = (df['close'] < df['bb_lower']).astype(int)
            
            # Stochastic Oscillator
            lowest_low = df['low'].rolling(14).min()
            highest_high = df['high'].rolling(14).max()
            df['stoch_k'] = 100 * (df['close'] - lowest_low) / (highest_high - lowest_low + 1e-8)
            df['stoch_d'] = df['stoch_k'].rolling(3).mean()
            df['stoch_oversold'] = (df['stoch_k'] < 20).astype(int)
            df['stoch_overbought'] = (df['stoch_k'] > 80).astype(int)
            
            # Williams %R
            df['williams_r'] = (df['close'] - highest_high) / (highest_high - lowest_low + 1e-8) * -100
            
            # =================================================================
            # 🔊 3. ANÁLISE DE VOLUME SOFISTICADA
            # =================================================================
            
            # Volume básico
            df['volume_ma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / (df['volume_ma'] + 1e-8)
            df['volume_spike'] = (df['volume_ratio'] > 2.0).astype(int)
            df['volume_dry'] = (df['volume_ratio'] < 0.5).astype(int)
            
            # On-Balance Volume (OBV)
            df['obv'] = 0.0
            for i in range(1, len(df)):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    df['obv'].iloc[i] = df['obv'].iloc[i-1] + df['volume'].iloc[i]
                elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                    df['obv'].iloc[i] = df['obv'].iloc[i-1] - df['volume'].iloc[i]
                else:
                    df['obv'].iloc[i] = df['obv'].iloc[i-1]
            
            # OBV trend
            df['obv_ma'] = df['obv'].rolling(20).mean()
            df['obv_rising'] = (df['obv'] > df['obv_ma']).astype(int)
            
            # Volume-Price Trend (VPT)
            df['vpt'] = (df['volume'] * df['close'].pct_change()).cumsum()
            
            # VWAP (Volume Weighted Average Price)
            df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
            df['above_vwap'] = (df['close'] > df['vwap']).astype(int)
            df['vwap_distance'] = ((df['close'] - df['vwap']) / df['close']) * 100
            
            # =================================================================
            # 🕯️ 4. PADRÕES DE CANDLESTICK AVANÇADOS
            # =================================================================
            
            # Propriedades básicas
            df['body_size'] = abs(df['close'] - df['open'])
            df['total_size'] = df['high'] - df['low']
            df['body_ratio'] = df['body_size'] / (df['total_size'] + 1e-8)
            
            # Sombras
            df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
            df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
            df['shadow_ratio'] = (df['upper_shadow'] + df['lower_shadow']) / (df['total_size'] + 1e-8)
            
            # Tipos de vela
            df['bullish_candle'] = (df['close'] > df['open']).astype(int)
            df['bearish_candle'] = (df['close'] < df['open']).astype(int)
            df['doji'] = (df['body_size'] < 0.1 * df['total_size']).astype(int)
            
            # Padrões específicos
            df['hammer'] = (
                (df['lower_shadow'] > 2 * df['body_size']) & 
                (df['upper_shadow'] < 0.3 * df['body_size']) &
                (df['body_size'] > 0.1 * df['total_size'])
            ).astype(int)
            
            df['shooting_star'] = (
                (df['upper_shadow'] > 2 * df['body_size']) & 
                (df['lower_shadow'] < 0.3 * df['body_size']) &
                (df['body_size'] > 0.1 * df['total_size'])
            ).astype(int)
            
            # Engulfing patterns
            df['bullish_engulfing'] = (
                (df['bullish_candle'] == 1) &
                (df['bearish_candle'].shift(1) == 1) &
                (df['open'] < df['close'].shift(1)) &
                (df['close'] > df['open'].shift(1))
            ).astype(int)
            
            df['bearish_engulfing'] = (
                (df['bearish_candle'] == 1) &
                (df['bullish_candle'].shift(1) == 1) &
                (df['open'] > df['close'].shift(1)) &
                (df['close'] < df['open'].shift(1))
            ).astype(int)
            
            # =================================================================
            # 📊 5. VOLATILIDADE E RISK MANAGEMENT
            # =================================================================
            
            # True Range e ATR
            df['tr'] = np.maximum(
                df['high'] - df['low'],
                np.maximum(
                    abs(df['high'] - df['close'].shift(1)),
                    abs(df['low'] - df['close'].shift(1))
                )
            )
            
            df['atr'] = df['tr'].rolling(14).mean()
            df['atr_percent'] = (df['atr'] / df['close']) * 100
            df['atr_normalized'] = df['atr'] / df['atr'].rolling(50).mean()
            
            # Volatility regimes
            df['low_volatility'] = (df['atr_normalized'] < 0.8).astype(int)
            df['high_volatility'] = (df['atr_normalized'] > 1.2).astype(int)
            
            # Price channels
            df['high_channel'] = df['high'].rolling(20).max()
            df['low_channel'] = df['low'].rolling(20).min()
            df['channel_position'] = (df['close'] - df['low_channel']) / (df['high_channel'] - df['low_channel'] + 1e-8)
            
            # =================================================================
            # 🎯 6. CONFLUENCE E FORÇA DE SINAL
            # =================================================================
            
            # Sinais bullish
            bullish_signals = []
            if 'rsi' in df.columns:
                bullish_signals.append((df['rsi'] > 30) & (df['rsi'] < 70) & (df['rsi'] > df['rsi'].shift(1)))
            if 'macd_bullish' in df.columns:
                bullish_signals.append(df['macd_bullish'] == 1)
            if 'above_sma_20' in df.columns:
                bullish_signals.append(df['above_sma_20'] == 1)
            if 'above_vwap' in df.columns:
                bullish_signals.append(df['above_vwap'] == 1)
            if 'volume_spike' in df.columns:
                bullish_signals.append(df['volume_spike'] == 1)
            if 'hammer' in df.columns:
                bullish_signals.append(df['hammer'] == 1)
            if 'bullish_engulfing' in df.columns:
                bullish_signals.append(df['bullish_engulfing'] == 1)
            
            # Sinais bearish
            bearish_signals = []
            if 'rsi' in df.columns:
                bearish_signals.append((df['rsi'] > 70) | ((df['rsi'] < 30) & (df['rsi'] < df['rsi'].shift(1))))
            if 'macd_bullish' in df.columns:
                bearish_signals.append(df['macd_bullish'] == 0)
            if 'above_sma_20' in df.columns:
                bearish_signals.append(df['above_sma_20'] == 0)
            if 'above_vwap' in df.columns:
                bearish_signals.append(df['above_vwap'] == 0)
            if 'shooting_star' in df.columns:
                bearish_signals.append(df['shooting_star'] == 1)
            if 'bearish_engulfing' in df.columns:
                bearish_signals.append(df['bearish_engulfing'] == 1)
            
            # Calcular confluence
            if bullish_signals:
                df['bullish_confluence'] = sum(bullish_signals).astype(int)
                df['bullish_strength'] = df['bullish_confluence'] / len(bullish_signals)
            else:
                df['bullish_strength'] = 0.0
            
            if bearish_signals:
                df['bearish_confluence'] = sum(bearish_signals).astype(int)
                df['bearish_strength'] = df['bearish_confluence'] / len(bearish_signals)
            else:
                df['bearish_strength'] = 0.0
            
            # Confluence score final
            df['confluence_score'] = df['bullish_strength'] - df['bearish_strength']
            df['confluence_strength'] = abs(df['confluence_score'])
            
            # =================================================================
            # 🎯 7. REGIME DE MERCADO
            # =================================================================
            
            # Trend regime usando múltiplas MAs
            trend_signals = []
            for period in [20, 50]:
                if f'above_sma_{period}' in df.columns:
                    trend_signals.append(df[f'above_sma_{period}'])
            
            if trend_signals:
                df['trend_strength'] = sum(trend_signals) / len(trend_signals)
                df['bull_regime'] = (df['trend_strength'] > 0.7).astype(int)
                df['bear_regime'] = (df['trend_strength'] < 0.3).astype(int)
                df['sideways_regime'] = ((df['trend_strength'] >= 0.3) & (df['trend_strength'] <= 0.7)).astype(int)
              # =================================================================
            # 🎯 8. TARGET ENGINEERING OTIMIZADO
            # =================================================================
            
            # Criar target baseado em retorno futuro
            future_periods = 2  # Mais responsivo - próximos 2 períodos
            future_returns = (df['close'].shift(-future_periods) / df['close'] - 1) * 100
            
            # Threshold mais sensível baseado na volatilidade
            volatility_threshold = df['atr_percent'].rolling(5).mean()  # Janela menor
            
            # Classificação mais sensível
            df['future_direction'] = np.where(
                future_returns > volatility_threshold * 0.3, 1,  # BUY (mais sensível)
                np.where(future_returns < -volatility_threshold * 0.3, 0, 2)  # SELL vs HOLD
            )
            
            logger.info(f"✅ Features ultra avançadas criadas: {len(df.columns)} colunas")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro criando features ultra avançadas: {e}")
            return df
    
    def train_ultra_model(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Treinar modelo ultra avançado com otimizações"""
        
        try:
            if not ML_AVAILABLE:
                logger.warning("⚠️ Bibliotecas ML não disponíveis")
                return {'success': False}
            
            logger.info(f"🚀 Treinamento ultra avançado para {symbol}")
            
            # Preparar dados
            df_clean = df.dropna()
            if len(df_clean) < 100:
                return {'success': False, 'reason': 'Dados insuficientes'}
            
            # Selecionar features (excluir colunas não-features)
            exclude_cols = [
                'open', 'high', 'low', 'close', 'volume', 'timestamp', 
                'future_direction', 'Unnamed'
            ]
            feature_cols = [
                col for col in df_clean.columns 
                if not any(exc in col for exc in exclude_cols)
            ]
            
            if len(feature_cols) < 10:
                return {'success': False, 'reason': 'Features insuficientes'}
            
            # Preparar X e y
            X = df_clean[feature_cols].iloc[:-5]  # Deixar espaço para target
            y = df_clean['future_direction'].iloc[:-5]
            
            # Remover samples com target inválido
            valid_mask = ~np.isnan(y)
            X = X[valid_mask]
            y = y[valid_mask]
            
            if len(X) < 50:
                return {'success': False, 'reason': 'Dados válidos insuficientes'}
            
            # Preencher NaN
            X = X.fillna(X.mean()).fillna(0)
            
            # Feature Selection otimizada
            k_features = min(30, len(feature_cols), len(X) // 3)
            selector = SelectKBest(f_classif, k=k_features)
            X_selected = selector.fit_transform(X, y)
            
            # Feature Scaling
            scaler = RobustScaler()
            X_scaled = scaler.fit_transform(X_selected)
              # Modelo ensemble otimizado com XGBoost se disponível
            if ML_AVAILABLE and 'xgboost' in str(type(xgb)):
                # Ensemble com Random Forest e XGBoost
                rf_model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=8,
                    min_samples_split=3,
                    min_samples_leaf=2,
                    max_features='sqrt',
                    random_state=42,
                    class_weight='balanced'
                )
                
                xgb_model = xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    eval_metric='logloss'
                )
                
                # Voting Classifier
                ensemble = VotingClassifier(
                    estimators=[('rf', rf_model), ('xgb', xgb_model)],
                    voting='soft'
                )
            else:
                # Apenas Random Forest otimizado
                ensemble = RandomForestClassifier(
                    n_estimators=150,
                    max_depth=10,
                    min_samples_split=3,
                    min_samples_leaf=2,
                    max_features='sqrt',
                    random_state=42,
                    class_weight='balanced'
                )
              # Treinar modelo
            ensemble.fit(X_scaled, y)
            
            # Validação cruzada
            cv_scores = cross_val_score(ensemble, X_scaled, y, cv=5, scoring='accuracy')
            accuracy = cv_scores.mean()
            
            logger.info(f"📊 Acurácia CV: {accuracy:.3f} ± {cv_scores.std():.3f}")
            
            # Salvar componentes
            self.ensemble_models[symbol] = ensemble
            self.feature_selectors[symbol] = selector
            self.feature_scalers[symbol] = scaler
            
            return {
                'success': True,
                'accuracy': accuracy,
                'std': cv_scores.std(),
                'n_features': X_scaled.shape[1],
                'n_samples': len(X),
                'feature_importance': getattr(ensemble, 'feature_importances_', [])
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento ultra: {e}")
            return {'success': False, 'error': str(e)}
    
    def ultra_predict_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Predição ultra avançada otimizada"""
        
        try:
            # Criar features ultra avançadas
            df_enhanced = self.create_ultra_features(df)
            
            # Treinar modelo se necessário
            if symbol not in self.ensemble_models:
                logger.info(f"🧠 Treinando modelo ultra para {symbol}...")
                training_result = self.train_ultra_model(df_enhanced, symbol)
                
                if not training_result.get('success', False):
                    logger.warning(f"⚠️ Fallback para predição normal")
                    return self.predict_signal(df, symbol)
            
            # Preparar dados para predição
            exclude_cols = [
                'open', 'high', 'low', 'close', 'volume', 'timestamp', 
                'future_direction', 'Unnamed'
            ]
            feature_cols = [
                col for col in df_enhanced.columns 
                if not any(exc in col for exc in exclude_cols)
            ]
            
            X_latest = df_enhanced[feature_cols].iloc[-1:].fillna(0)
            
            # Aplicar transformações
            selector = self.feature_selectors[symbol]
            scaler = self.feature_scalers[symbol]
            
            X_selected = selector.transform(X_latest)
            X_scaled = scaler.transform(X_selected)
            
            # Predição
            model = self.ensemble_models[symbol]
            prediction = model.predict(X_scaled)[0]
            probabilities = model.predict_proba(X_scaled)[0]
            
            # Calcular confiança
            base_confidence = max(probabilities)
            
            # Ajustes de confiança baseados em confluence
            confluence_boost = 1.0
            if 'confluence_strength' in df_enhanced.columns:
                confluence = df_enhanced['confluence_strength'].iloc[-1]
                if not np.isnan(confluence):
                    confluence_boost = 0.85 + (0.3 * confluence)  # 0.85 a 1.15
            
            # Ajuste por volatilidade
            volatility_adjustment = 1.0
            if 'atr_normalized' in df_enhanced.columns:
                atr_norm = df_enhanced['atr_normalized'].iloc[-1]
                if not np.isnan(atr_norm):
                    if atr_norm > 1.5:  # Alta volatilidade
                        volatility_adjustment = 0.9
                    elif atr_norm < 0.7:  # Baixa volatilidade
                        volatility_adjustment = 1.1
            
            # Confiança final
            final_confidence = base_confidence * confluence_boost * volatility_adjustment
            final_confidence = min(final_confidence, 0.95)  # Cap máximo
              # Decisão de sinal com threshold adaptativo
            adaptive_threshold = self.min_confidence_threshold
            
            # Ajustar threshold baseado no regime de mercado (menos conservador)
            if 'sideways_regime' in df_enhanced.columns:
                if df_enhanced['sideways_regime'].iloc[-1] == 1:
                    adaptive_threshold += 0.05  # Apenas +5% em mercado lateral
            
            # Reduzir threshold se confluence for alta
            if 'confluence_strength' in df_enhanced.columns:
                confluence = df_enhanced['confluence_strength'].iloc[-1]
                if not np.isnan(confluence) and confluence > 0.7:
                    adaptive_threshold -= 0.1  # Reduzir threshold com alta confluence
            
            if final_confidence < adaptive_threshold:
                signal_type = 'HOLD'
                signal_value = 2
            else:
                if prediction == 1:
                    signal_type = 'BUY'
                    signal_value = 1
                elif prediction == 0:
                    signal_type = 'SELL'
                    signal_value = 0
                else:
                    signal_type = 'HOLD'
                    signal_value = 2
            
            # Stop loss e take profit dinâmicos
            current_price = df_enhanced['close'].iloc[-1]
            atr = df_enhanced.get('atr', pd.Series([current_price * 0.02])).iloc[-1]
            
            if np.isnan(atr):
                atr = current_price * 0.02
            
            # Ajustar SL/TP baseado na volatilidade
            atr_multiplier = 1.5
            if 'high_volatility' in df_enhanced.columns and df_enhanced['high_volatility'].iloc[-1] == 1:
                atr_multiplier = 2.0  # SL/TP mais amplos em alta volatilidade
            elif 'low_volatility' in df_enhanced.columns and df_enhanced['low_volatility'].iloc[-1] == 1:
                atr_multiplier = 1.0  # SL/TP mais apertados em baixa volatilidade
            
            if signal_type == 'BUY':
                stop_loss = current_price - (atr * atr_multiplier)
                take_profit = current_price + (atr * atr_multiplier * 2)
            elif signal_type == 'SELL':
                stop_loss = current_price + (atr * atr_multiplier)
                take_profit = current_price - (atr * atr_multiplier * 2)
            else:
                stop_loss = 0
                take_profit = 0
            
            result = {
                'signal': signal_value,
                'signal_type': signal_type,
                'confidence': final_confidence,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'model_used': 'UltraEnhancedV2',
                'ultra_enhanced': True,
                'probabilities': probabilities.tolist(),
                'confluence': df_enhanced.get('confluence_strength', pd.Series([0])).iloc[-1],
                'base_confidence': base_confidence,
                'confluence_boost': confluence_boost,
                'volatility_adjustment': volatility_adjustment,
                'adaptive_threshold': adaptive_threshold
            }
            
            logger.info(f"🎯 {symbol}: {signal_type} (conf: {final_confidence:.3f}, base: {base_confidence:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na predição ultra: {e}")
            return self.predict_signal(df, symbol)

def test_ultra_engine():
    """Teste do engine ultra melhorado"""
    
    print("🚀 TESTANDO AI ENGINE ULTRA MELHORADO V2")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        
        config = Config()
        market_data = MarketDataManager(config)
        ultra_ai = UltraEnhancedAIEngine(config)
        
        # Testar com BTCUSDT
        symbol = 'BTCUSDT'
        print(f"\n🔍 Testando {symbol}...")
        
        df = market_data.get_historical_data(symbol, '5m', 500)
        if df is not None and len(df) >= 200:
            
            print(f"📊 Dados obtidos: {len(df)} registros")
            
            # Criar features ultra avançadas
            df_ultra = ultra_ai.create_ultra_features(df)
            print(f"✅ Features criadas: {len(df_ultra.columns)} colunas")
            
            # Fazer predição ultra
            result = ultra_ai.ultra_predict_signal(df, symbol)
            
            print(f"\n🎯 RESULTADO:")
            print(f"   Sinal: {result.get('signal_type', 'N/A')}")
            print(f"   Confiança: {result.get('confidence', 0):.3f}")
            print(f"   Confiança base: {result.get('base_confidence', 0):.3f}")
            print(f"   Modelo: {result.get('model_used', 'N/A')}")
            print(f"   Ultra Enhanced: {result.get('ultra_enhanced', False)}")
            print(f"   Confluence: {result.get('confluence', 0):.3f}")
            print(f"   Threshold adaptativo: {result.get('adaptive_threshold', 0):.3f}")
            
            if result.get('signal_type') != 'HOLD':
                print(f"   Entry: ${result.get('entry_price', 0):.2f}")
                print(f"   Stop Loss: ${result.get('stop_loss', 0):.2f}")
                print(f"   Take Profit: ${result.get('take_profit', 0):.2f}")
            
        else:
            print("❌ Dados insuficientes")
                
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("📋 MELHORIAS ULTRA V2 IMPLEMENTADAS:")
    print("✅ 80+ features técnicas avançadas")
    print("✅ Random Forest otimizado com class_weight")  
    print("✅ Confluence analysis sofisticado")
    print("✅ Threshold adaptativo por regime")
    print("✅ SL/TP dinâmicos por volatilidade")
    print("✅ Error handling completo")
    print("✅ Regime detection avançado")
    print("✅ Multi-layer confidence boosting")

if __name__ == "__main__":
    test_ultra_engine()
