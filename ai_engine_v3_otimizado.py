#!/usr/bin/env python3
"""
🚀 AI ENGINE V3 OTIMIZADO - Foco em ALTA TAXA DE ACERTO
Sistema reformulado para superar 70% de acurácia
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
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, AdaBoostClassifier
    from sklearn.model_selection import cross_val_score, GridSearchCV, TimeSeriesSplit
    from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
    from sklearn.feature_selection import SelectKBest, f_classif, RFECV
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Importar classe original
from src.ai_engine import AITradingEngine

logger = logging.getLogger(__name__)

class OptimizedAIEngineV3(AITradingEngine):
    """AI Engine V3 - Otimizado para alta performance"""
    
    def __init__(self, config):
        super().__init__(config)
        self.optimized_features_enabled = True
        self.min_confidence_threshold = 0.40  # Threshold inicial mais agressivo
        self.ensemble_models = {}
        self.feature_scalers = {}
        self.feature_selectors = {}
        self.model_performance = {}
        
        # Configurações otimizadas
        self.lookback_periods = [5, 10, 20]  # Menos features, mais qualidade
        self.volume_periods = [10, 20]
        self.volatility_periods = [14, 21]
        
    def create_optimized_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Criar conjunto otimizado de features de alta qualidade"""
        
        try:
            logger.info("🚀 Criando features otimizadas V3...")
            
            if len(df) < 50:  # Mínimo de dados necessário
                logger.warning("⚠️ Dados insuficientes para features")
                return df
            
            # =================================================================
            # 📊 1. FEATURES BÁSICAS ESSENCIAIS (MENOS É MAIS)
            # =================================================================
            
            # Médias móveis fundamentais
            periods = [9, 21, 50]
            for period in periods:
                if len(df) >= period:
                    df[f'sma_{period}'] = df['close'].rolling(period).mean()
                    df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
                    
                    # Força da tendência
                    df[f'trend_strength_{period}'] = (df['close'] - df[f'sma_{period}']) / df[f'sma_{period}']
                    df[f'ema_slope_{period}'] = df[f'ema_{period}'].diff() / df[f'ema_{period}']
            
            # Momentum otimizado
            for period in [5, 10, 20]:
                if len(df) >= period:
                    df[f'momentum_{period}'] = (df['close'] / df['close'].shift(period) - 1) * 100
            
            # Price position in recent range
            df['price_position_20'] = (df['close'] - df['low'].rolling(20).min()) / \
                                    (df['high'].rolling(20).max() - df['low'].rolling(20).min() + 1e-8)
            
            # =================================================================
            # 📈 2. INDICADORES TÉCNICOS OTIMIZADOS
            # =================================================================
            
            # RSI melhorado com múltiplos períodos
            for rsi_period in [14, 21]:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
                rs = gain / (loss + 1e-8)
                df[f'rsi_{rsi_period}'] = 100 - (100 / (1 + rs))
                
                # RSI momentum
                df[f'rsi_momentum_{rsi_period}'] = df[f'rsi_{rsi_period}'].diff()
            
            # MACD com sinais claros
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            df['macd'] = ema12 - ema26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            df['macd_momentum'] = df['macd_histogram'].diff()
            
            # Bollinger Bands otimizado
            bb_period = 20
            bb_middle = df['close'].rolling(bb_period).mean()
            bb_std = df['close'].rolling(bb_period).std()
            df['bb_upper'] = bb_middle + (bb_std * 2)
            df['bb_lower'] = bb_middle - (bb_std * 2)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'] + 1e-8)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / bb_middle
            
            # Stochastic %K e %D
            low_14 = df['low'].rolling(14).min()
            high_14 = df['high'].rolling(14).max()
            df['stoch_k'] = 100 * (df['close'] - low_14) / (high_14 - low_14 + 1e-8)
            df['stoch_d'] = df['stoch_k'].rolling(3).mean()
            df['stoch_momentum'] = df['stoch_k'].diff()
            
            # =================================================================
            # 🔊 3. ANÁLISE DE VOLUME OTIMIZADA
            # =================================================================
            
            # Volume basics
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / (df['volume_sma'] + 1e-8)
            
            # VWAP
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
            df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / df['volume'].cumsum()
            df['vwap_deviation'] = (df['close'] - df['vwap']) / df['vwap']
            
            # On-Balance Volume simplificado
            price_change = df['close'].diff()
            df['obv_signal'] = np.where(price_change > 0, 1, np.where(price_change < 0, -1, 0))
            df['obv_volume'] = (df['obv_signal'] * df['volume']).cumsum()
            df['obv_trend'] = df['obv_volume'].rolling(10).apply(lambda x: 1 if x.iloc[-1] > x.iloc[0] else -1)
            
            # =================================================================
            # 🕯️ 4. PADRÕES DE CANDLESTICK SIMPLIFICADOS
            # =================================================================
            
            # Propriedades básicas
            df['body_size'] = abs(df['close'] - df['open'])
            df['range_size'] = df['high'] - df['low']
            df['body_ratio'] = df['body_size'] / (df['range_size'] + 1e-8)
            
            # Direção da vela
            df['candle_direction'] = np.where(df['close'] > df['open'], 1, -1)
            df['candle_momentum'] = df['candle_direction'] * df['body_ratio']
            
            # Sombras
            df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
            df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
            df['shadow_balance'] = (df['upper_shadow'] - df['lower_shadow']) / (df['range_size'] + 1e-8)
            
            # =================================================================
            # 📊 5. VOLATILIDADE E ATR
            # =================================================================
            
            # True Range
            df['tr'] = np.maximum(
                df['high'] - df['low'],
                np.maximum(
                    abs(df['high'] - df['close'].shift(1)),
                    abs(df['low'] - df['close'].shift(1))
                )
            )
            
            df['atr_14'] = df['tr'].rolling(14).mean()
            df['atr_ratio'] = df['atr_14'] / df['close']
            df['volatility_regime'] = pd.cut(df['atr_ratio'], bins=3, labels=[0, 1, 2])
            
            # =================================================================
            # 🎯 6. CONFLUENCE SCORE OTIMIZADO
            # =================================================================
            
            # Sinais bullish essenciais
            bullish_conditions = []
            
            # Tendência de alta
            if 'trend_strength_21' in df.columns:
                bullish_conditions.append(df['trend_strength_21'] > 0.02)
            
            # RSI favorável
            if 'rsi_14' in df.columns:
                bullish_conditions.append((df['rsi_14'] > 40) & (df['rsi_14'] < 80) & (df['rsi_momentum_14'] > 0))
            
            # MACD bullish
            if 'macd_histogram' in df.columns:
                bullish_conditions.append((df['macd_histogram'] > 0) & (df['macd_momentum'] > 0))
            
            # Price above key levels
            if 'ema_21' in df.columns:
                bullish_conditions.append(df['close'] > df['ema_21'])
            
            # Volume confirmation
            if 'volume_ratio' in df.columns:
                bullish_conditions.append(df['volume_ratio'] > 1.1)
            
            # VWAP bullish
            if 'vwap_deviation' in df.columns:
                bullish_conditions.append(df['vwap_deviation'] > 0)
            
            # Calcular confluence bullish
            if bullish_conditions:
                df['bullish_confluence'] = sum(bullish_conditions).astype(float) / len(bullish_conditions)
            else:
                df['bullish_confluence'] = 0.0
            
            # Sinais bearish essenciais
            bearish_conditions = []
            
            # Tendência de baixa
            if 'trend_strength_21' in df.columns:
                bearish_conditions.append(df['trend_strength_21'] < -0.02)
            
            # RSI bearish
            if 'rsi_14' in df.columns:
                bearish_conditions.append((df['rsi_14'] > 20) & (df['rsi_14'] < 60) & (df['rsi_momentum_14'] < 0))
            
            # MACD bearish
            if 'macd_histogram' in df.columns:
                bearish_conditions.append((df['macd_histogram'] < 0) & (df['macd_momentum'] < 0))
            
            # Price below key levels
            if 'ema_21' in df.columns:
                bearish_conditions.append(df['close'] < df['ema_21'])
            
            # VWAP bearish
            if 'vwap_deviation' in df.columns:
                bearish_conditions.append(df['vwap_deviation'] < 0)
              # Calcular confluence bearish
            if bearish_conditions:
                df['bearish_confluence'] = sum(bearish_conditions).astype(float) / len(bearish_conditions)
            else:
                df['bearish_confluence'] = 0.0
            
            # Confluence final
            df['net_confluence'] = df['bullish_confluence'] - df['bearish_confluence']
            df['confluence_strength'] = np.maximum(df['bullish_confluence'], df['bearish_confluence'])
            
            # =================================================================
            # 🎯 7. TARGET OTIMIZADO
            # =================================================================
            # 🎯 7. TARGET OTIMIZADO
            # =================================================================
            
            # Target mais responsivo para capturar movimentos menores
            future_periods = 3  # Próximos 3 períodos
            
            # Retorno futuro
            future_returns = (df['close'].shift(-future_periods) / df['close'] - 1) * 100
            
            # Threshold dinâmico baseado na volatilidade
            rolling_volatility = df['close'].pct_change().rolling(20).std() * 100
            dynamic_threshold = rolling_volatility * 0.5  # 50% da volatilidade
            
            # Classificação mais sensível
            df['target'] = np.where(
                future_returns > dynamic_threshold, 1,  # BUY
                np.where(future_returns < -dynamic_threshold, 0, 2)  # SELL vs HOLD
            )
            
            logger.info(f"✅ Features otimizadas V3 criadas: {len(df.columns)} colunas")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro criando features otimizadas: {e}")
            return df
    
    def train_optimized_model(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Treinar modelo otimizado com foco em performance"""
        
        try:
            if not ML_AVAILABLE:
                logger.warning("⚠️ Bibliotecas ML não disponíveis")
                return {'success': False}
            
            logger.info(f"🚀 Treinamento otimizado V3 para {symbol}")
            
            # Preparar dados
            df_clean = df.dropna()
            if len(df_clean) < 100:
                return {'success': False, 'reason': 'Dados insuficientes'}
            
            # Selecionar features (excluir colunas não-features)
            exclude_cols = [
                'open', 'high', 'low', 'close', 'volume', 'timestamp', 
                'target', 'typical_price', 'Unnamed'
            ]
            feature_cols = [
                col for col in df_clean.columns 
                if not any(exc in str(col) for exc in exclude_cols) and 
                df_clean[col].dtype in ['float64', 'int64', 'float32', 'int32']
            ]
            
            if len(feature_cols) < 5:
                return {'success': False, 'reason': 'Features insuficientes'}
            
            # Preparar X e y
            X = df_clean[feature_cols].iloc[:-5]  # Deixar espaço para target
            y = df_clean['target'].iloc[:-5]
            
            # Remover samples com target inválido
            valid_mask = ~np.isnan(y) & np.isfinite(y)
            X = X[valid_mask]
            y = y[valid_mask]
            
            if len(X) < 50:
                return {'success': False, 'reason': 'Dados válidos insuficientes'}
            
            # Preencher NaN e valores infinitos
            X = X.replace([np.inf, -np.inf], np.nan)
            X = X.fillna(X.median()).fillna(0)
            
            # Feature Selection mais rigorosa
            k_features = min(15, len(feature_cols), len(X) // 4)  # Menos features
            selector = SelectKBest(f_classif, k=k_features)
            X_selected = selector.fit_transform(X, y)
            
            # Feature Scaling
            scaler = RobustScaler()
            X_scaled = scaler.fit_transform(X_selected)
            
            # Modelo ensemble otimizado
            models = []
            
            # Random Forest otimizado
            rf_model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=3,
                max_features='sqrt',
                random_state=42,
                class_weight='balanced',
                bootstrap=True,
                oob_score=True
            )
            models.append(('rf', rf_model))
            
            # Gradient Boosting
            gb_model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=8,
                learning_rate=0.1,
                random_state=42
            )
            models.append(('gb', gb_model))
              # XGBoost se disponível
            try:
                xgb_model = xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    eval_metric='logloss'
                )
                models.append(('xgb', xgb_model))
            except:
                pass
            
            # Voting Classifier
            ensemble = VotingClassifier(
                estimators=models,
                voting='soft'
            )
            
            # Treinar modelo
            ensemble.fit(X_scaled, y)
            
            # Validação com Time Series Split (mais apropriado para dados temporais)
            tscv = TimeSeriesSplit(n_splits=5)
            cv_scores = cross_val_score(ensemble, X_scaled, y, cv=tscv, scoring='accuracy')
            accuracy = cv_scores.mean()
            
            logger.info(f"📊 Acurácia CV: {accuracy:.3f} ± {cv_scores.std():.3f}")
            
            # Salvar componentes
            self.ensemble_models[symbol] = ensemble
            self.feature_selectors[symbol] = selector
            self.feature_scalers[symbol] = scaler
            self.model_performance[symbol] = {
                'accuracy': accuracy,
                'std': cv_scores.std(),
                'features': k_features,
                'samples': len(X)
            }
            
            return {
                'success': True,
                'accuracy': accuracy,
                'std': cv_scores.std(),
                'n_features': X_scaled.shape[1],
                'n_samples': len(X),
                'feature_names': [feature_cols[i] for i in selector.get_support(indices=True)]
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento otimizado: {e}")
            return {'success': False, 'error': str(e)}
    
    def optimized_predict_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Predição otimizada V3"""
        
        try:
            # Criar features otimizadas
            df_enhanced = self.create_optimized_features(df)
            
            # Treinar modelo se necessário
            if symbol not in self.ensemble_models:
                logger.info(f"🧠 Treinando modelo otimizado para {symbol}...")
                training_result = self.train_optimized_model(df_enhanced, symbol)
                
                if not training_result.get('success', False):
                    logger.warning(f"⚠️ Fallback para predição normal")
                    return self.predict_signal(df, symbol)
              # Preparar dados para predição
            exclude_cols = [
                'open', 'high', 'low', 'close', 'volume', 'timestamp', 
                'target', 'typical_price', 'Unnamed'
            ]
            feature_cols = [
                col for col in df_enhanced.columns 
                if not any(exc in str(col) for exc in exclude_cols) and 
                df_enhanced[col].dtype in ['float64', 'int64', 'float32', 'int32']
            ]
            
            # IMPORTANTE: Garantir que temos as mesmas features do treinamento
            if symbol in self.feature_selectors:
                # Obter as features selecionadas no treinamento
                selector = self.feature_selectors[symbol]
                training_features = selector.get_feature_names_out() if hasattr(selector, 'get_feature_names_out') else None
                
                if training_features is not None:
                    # Usar apenas as features que foram usadas no treinamento
                    available_features = [col for col in feature_cols if col in training_features]
                    if len(available_features) != len(training_features):
                        logger.warning(f"⚠️ Features inconsistentes para {symbol}: {len(available_features)} vs {len(training_features)}")
                        # Re-treinar o modelo se necessário
                        logger.info(f"🔄 Re-treinando modelo para {symbol} devido a inconsistência de features")
                        training_result = self.train_optimized_model(df_enhanced, symbol)
                        if not training_result.get('success', False):
                            logger.warning(f"⚠️ Re-treinamento falhou, usando predição padrão")
                            return self.predict_signal(df, symbol)
            
            X_latest = df_enhanced[feature_cols].iloc[-1:].replace([np.inf, -np.inf], np.nan).fillna(0)
            
            # Aplicar transformações
            selector = self.feature_selectors[symbol]
            scaler = self.feature_scalers[symbol]
            
            X_selected = selector.transform(X_latest)
            X_scaled = scaler.transform(X_selected)
            
            # Predição
            model = self.ensemble_models[symbol]
            prediction = model.predict(X_scaled)[0]
            probabilities = model.predict_proba(X_scaled)[0]
            
            # Calcular confiança base
            base_confidence = max(probabilities)
            
            # Ajustes de confiança baseados em confluence
            confluence_boost = 1.0
            if 'confluence_strength' in df_enhanced.columns:
                confluence = df_enhanced['confluence_strength'].iloc[-1]
                if not np.isnan(confluence):
                    confluence_boost = 0.9 + (0.2 * confluence)  # 0.9 a 1.1
            
            # Ajuste baseado na performance do modelo
            performance_boost = 1.0
            if symbol in self.model_performance:
                model_acc = self.model_performance[symbol]['accuracy']
                if model_acc > 0.6:  # Se modelo tem boa acurácia
                    performance_boost = 1.1
                elif model_acc < 0.4:  # Se modelo tem baixa acurácia
                    performance_boost = 0.8
            
            # Confiança final
            final_confidence = base_confidence * confluence_boost * performance_boost
            final_confidence = min(final_confidence, 0.95)  # Cap máximo
            
            # Threshold adaptativo baseado na performance
            adaptive_threshold = self.min_confidence_threshold
            if symbol in self.model_performance:
                model_acc = self.model_performance[symbol]['accuracy']
                if model_acc > 0.55:  # Modelo bom - pode ser mais agressivo
                    adaptive_threshold -= 0.05
                elif model_acc < 0.4:  # Modelo ruim - ser mais conservador
                    adaptive_threshold += 0.1
            
            # Decisão de sinal
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
            atr = df_enhanced.get('atr_14', pd.Series([current_price * 0.02])).iloc[-1]
            
            if np.isnan(atr) or atr == 0:
                atr = current_price * 0.02
            
            # SL/TP baseado na volatilidade
            if 'volatility_regime' in df_enhanced.columns:
                vol_regime = df_enhanced['volatility_regime'].iloc[-1]
                if vol_regime == 2:  # Alta volatilidade
                    atr_multiplier = 2.5
                elif vol_regime == 0:  # Baixa volatilidade
                    atr_multiplier = 1.5
                else:  # Volatilidade média
                    atr_multiplier = 2.0
            else:
                atr_multiplier = 2.0
            
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
                'model_used': 'OptimizedV3',
                'optimized_v3': True,
                'probabilities': probabilities.tolist(),
                'confluence': df_enhanced.get('confluence_strength', pd.Series([0])).iloc[-1],
                'base_confidence': base_confidence,
                'confluence_boost': confluence_boost,
                'performance_boost': performance_boost,
                'adaptive_threshold': adaptive_threshold,
                'model_accuracy': self.model_performance.get(symbol, {}).get('accuracy', 0)
            }
            
            logger.info(f"🎯 {symbol}: {signal_type} (conf: {final_confidence:.3f}, acc: {result['model_accuracy']:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na predição otimizada: {e}")
            return self.predict_signal(df, symbol)

def test_optimized_engine():
    """Teste do engine otimizado V3"""
    
    print("🚀 TESTANDO AI ENGINE OTIMIZADO V3")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        
        config = Config()
        market_data = MarketDataManager(config)
        optimized_ai = OptimizedAIEngineV3(config)
        
        # Testar com múltiplos símbolos
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        timeframes = ['1m', '5m']
        
        for symbol in symbols:
            for timeframe in timeframes:
                print(f"\n🔍 Testando {symbol} {timeframe}...")
                
                df = market_data.get_historical_data(symbol, timeframe, 500)
                if df is not None and len(df) >= 200:
                    
                    result = optimized_ai.optimized_predict_signal(df, f"{symbol}_{timeframe}")
                    
                    print(f"   🎯 Sinal: {result.get('signal_type', 'N/A')}")
                    print(f"   📈 Confiança: {result.get('confidence', 0):.3f}")
                    print(f"   🎯 Acurácia do modelo: {result.get('model_accuracy', 0):.3f}")
                    print(f"   🤝 Confluence: {result.get('confluence', 0):.3f}")
                    
                    if result.get('signal_type') != 'HOLD':
                        print(f"   💰 Entry: ${result.get('entry_price', 0):.2f}")
                        print(f"   🛑 Stop Loss: ${result.get('stop_loss', 0):.2f}")
                        print(f"   🎯 Take Profit: ${result.get('take_profit', 0):.2f}")
                
                else:
                    print(f"   ❌ Dados insuficientes")
                
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("📋 OTIMIZAÇÕES V3 IMPLEMENTADAS:")
    print("✅ Features de alta qualidade (menos ruído)")
    print("✅ Ensemble com múltiplos algoritmos")
    print("✅ Time Series Cross-Validation")
    print("✅ Threshold adaptativo por performance")
    print("✅ Confluence otimizado")
    print("✅ Target dinâmico baseado em volatilidade")
    print("✅ Feature selection rigorosa")
    print("✅ Performance tracking por símbolo")

if __name__ == "__main__":
    test_optimized_engine()
