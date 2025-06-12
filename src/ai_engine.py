#!/usr/bin/env python3
"""
Engine de IA simplificado para deploy - CryptoNinja
Versão otimizada para produção com fallbacks graceful
"""

import numpy as np
import pandas as pd
import pickle
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

# Machine Learning imports básicos (sempre disponíveis)
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import SelectKBest, f_classif

# Imports avançados com fallback graceful
XGBOOST_AVAILABLE = False
LIGHTGBM_AVAILABLE = False
TENSORFLOW_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    pass

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    pass

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger(__name__)

class AITradingEngine:
    """Engine de IA simplificado para trading - otimizado para deploy"""
    
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.is_trained = False
        
        # Log das bibliotecas disponíveis
        available_libs = []
        if XGBOOST_AVAILABLE:
            available_libs.append("XGBoost")
        if LIGHTGBM_AVAILABLE:
            available_libs.append("LightGBM")
        if TENSORFLOW_AVAILABLE:
            available_libs.append("TensorFlow")
        
        logger.info(f"AI Engine inicializado com: Random Forest + {', '.join(available_libs) if available_libs else 'sem libs extras'}")
    
    def create_simple_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Criar features simples para o modelo"""
        try:
            # Features básicas de preço
            df['price_change'] = df['close'].pct_change()
            df['volume_change'] = df['volume'].pct_change()
            
            # Médias móveis simples
            for period in [5, 10, 20]:
                df[f'sma_{period}'] = df['close'].rolling(period).mean()
                df[f'price_sma_{period}_ratio'] = df['close'] / df[f'sma_{period}']
            
            # Volatilidade
            df['volatility'] = df['close'].pct_change().rolling(10).std()
            
            # Range
            df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
            
            # Momentum
            df['momentum_5'] = df['close'] - df['close'].shift(5)
            df['momentum_10'] = df['close'] - df['close'].shift(10)            # Limpar NaN (usando método atualizado)
            df = df.ffill().bfill().fillna(0)            
            logger.info(f"Features criadas: {len(df.columns)} colunas")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao criar features: {e}")
            return df
    
    def create_simple_labels(self, df: pd.DataFrame) -> pd.Series:
        """Criar labels simples - APENAS BUY/SELL (sem HOLD)"""
        try:
            # Retorno futuro em 12 períodos
            future_return = df['close'].shift(-12) / df['close'] - 1
            
            # Labels binários: BUY (1), SELL (0) - SEM HOLD
            labels = pd.Series(index=df.index, dtype=int)
            
            # Threshold mais agressivo para forçar decisões
            threshold = 0.005  # 0.5% em vez de 1.5%
            
            # BUY se retorno positivo, SELL se negativo
            labels[future_return > threshold] = 1   # BUY
            labels[future_return <= threshold] = 0  # SELL
            
            return labels.fillna(0)
            
        except Exception as e:
            logger.error(f"Erro ao criar labels: {e}")
            return pd.Series(index=df.index, dtype=int).fillna(0)
    
    def train_simple_model(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Treinar modelo simplificado"""
        try:
            logger.info(f"Treinando modelo simples para {symbol}")
            
            # Preparar dados
            df_features = self.create_simple_features(df)
            labels = self.create_simple_labels(df_features)
            
            # Selecionar features numéricas
            numeric_cols = df_features.select_dtypes(include=[np.number]).columns
            X = df_features[numeric_cols]
            y = labels
            
            # Remover NaN
            mask = ~(X.isna().any(axis=1) | y.isna())
            X = X[mask]
            y = y[mask]
            
            if len(X) < 100:
                logger.warning(f"Dados insuficientes: {len(X)} amostras")
                return {'success': False, 'error': 'Dados insuficientes'}
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scaler
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Feature selection
            selector = SelectKBest(f_classif, k=min(20, X_train.shape[1]))
            X_train_selected = selector.fit_transform(X_train_scaled, y_train)
            X_test_selected = selector.transform(X_test_scaled)
            
            # Treinar modelos
            models = {}
            
            # Random Forest (sempre disponível)
            rf_model = RandomForestClassifier(n_estimators=50, random_state=42)
            rf_model.fit(X_train_selected, y_train)
            rf_pred = rf_model.predict(X_test_selected)
            rf_acc = accuracy_score(y_test, rf_pred)
            models['random_forest'] = {'model': rf_model, 'accuracy': rf_acc}            # XGBoost (se disponível) - VERSÃO BINÁRIA
            if XGBOOST_AVAILABLE:
                try:
                    # Agora as labels já são binárias (0, 1), não precisa converter
                    xgb_model = xgb.XGBClassifier(
                        n_estimators=50, 
                        random_state=42,
                        eval_metric='logloss',
                        verbosity=0
                    )
                    xgb_model.fit(X_train_selected, y_train)
                    xgb_pred = xgb_model.predict(X_test_selected)
                    xgb_acc = accuracy_score(y_test, xgb_pred)
                    
                    models['xgboost'] = {'model': xgb_model, 'accuracy': xgb_acc}
                    logger.info(f"XGBoost treinado com accuracy: {xgb_acc:.3f}")
                except Exception as e:
                    logger.warning(f"XGBoost falhou: {str(e)[:50]}...")
              # Salvar
            self.models[symbol] = models
            self.scalers[symbol] = scaler
            self.feature_selectors[symbol] = selector
            self.is_trained = True
            
            best_model = max(models.keys(), key=lambda k: models[k]['accuracy'])
            logger.info(f"Melhor modelo para {symbol}: {best_model} (acc: {models[best_model]['accuracy']:.3f})")
            return {
                'success': True,
                'best_model': best_model,
                'accuracy': models[best_model]['accuracy'],
                'models_count': len(models)
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return {'success': False, 'error': str(e)}
    
    def predict_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Predição de sinal com IA real - MODO PRODUÇÃO ATIVADO"""
        
        # MODO PRODUÇÃO: IA Real ativada!
        try:
            # Se modelo não está treinado, treinar automaticamente
            if symbol not in self.models:
                logger.info(f"🧠 Modelo não encontrado para {symbol}. Treinando automaticamente...")
                training_result = self.train_simple_model(df, symbol)
                if not training_result.get('success', False):
                    logger.warning(f"⚠️ Falha no treinamento para {symbol}. Usando análise técnica.")
                    return self._fallback_technical_prediction(df, symbol)
            
            # Preparar features para predição
            df_features = self.create_simple_features(df)
            
            # Usar última linha para predição
            X = df_features.select_dtypes(include=[np.number]).iloc[-1:].fillna(0)
            
            # Transformar dados
            X_scaled = self.scalers[symbol].transform(X)
            X_selected = self.feature_selectors[symbol].transform(X_scaled)
            
            # Fazer predição com todos os modelos disponíveis
            predictions = {}
            confidences = {}
            
            for model_name, model_data in self.models[symbol].items():
                try:
                    pred = model_data['model'].predict(X_selected)[0]
                    
                    # Calcular confiança baseada na accuracy do modelo
                    if hasattr(model_data['model'], 'predict_proba'):
                        pred_proba = model_data['model'].predict_proba(X_selected)[0]
                        confidence = np.max(pred_proba)
                    else:
                        confidence = model_data.get('accuracy', 0.6)
                    
                    predictions[model_name] = pred
                    confidences[model_name] = confidence
                    
                except Exception as e:
                    logger.warning(f"Erro na predição {model_name}: {e}")
                    continue
            
            if not predictions:
                logger.warning(f"Nenhuma predição válida para {symbol}")
                return self._fallback_technical_prediction(df, symbol)
            
            # Usar melhor modelo ou fazer ensemble
            if len(predictions) == 1:
                model_name = list(predictions.keys())[0]
                final_signal = predictions[model_name]
                final_confidence = confidences[model_name]
                best_model = model_name
            else:
                # Ensemble voting: usar modelo com maior accuracy
                best_model = max(self.models[symbol].keys(), 
                               key=lambda k: self.models[symbol][k].get('accuracy', 0))
                final_signal = predictions[best_model]
                final_confidence = confidences[best_model]
              # Mapear sinais binários
            signal_names = {0: 'SELL', 1: 'BUY'}
            
            logger.info(f"🤖 IA REAL: {signal_names[final_signal]} para {symbol} "
                       f"(confiança: {final_confidence:.3f}, modelo: {best_model})")
            
            return {
                'signal': int(final_signal),
                'confidence': float(final_confidence),
                'signal_type': signal_names[final_signal],
                'model_used': best_model,
                'timestamp': datetime.now().isoformat(),
                'test_mode': False,  # IA REAL ATIVADA!
                'individual_predictions': predictions            }
            
        except Exception as e:
            logger.error(f"Erro na IA real para {symbol}: {e}")
            return self._fallback_technical_prediction(df, symbol)
    
    def get_model_status(self) -> Dict:
        """Status dos modelos"""
        available_models = ["Random Forest"]
        if XGBOOST_AVAILABLE:
            available_models.append("XGBoost")
        if LIGHTGBM_AVAILABLE:
            available_models.append("LightGBM")
        if TENSORFLOW_AVAILABLE:
            available_models.append("Neural Network")
        
        return {
            'is_trained': self.is_trained,
            'available_models': available_models,
            'trained_symbols': list(self.models.keys()),
            'deploy_ready': True        }
    
    def load_models(self):
        """Carregar modelos salvos e treinar automaticamente se necessário"""
        try:
            import os
            
            # Verificar se existem modelos salvos
            startup_symbols = ['BTCUSDT', 'ETHUSDT', 'COMPUSDT']
            models_to_train = []
            
            for symbol in startup_symbols:
                model_files = [
                    f'models/{symbol}_models.pkl',
                    f'models/{symbol}_scaler.pkl', 
                    f'models/{symbol}_selector.pkl'
                ]
                
                models_exist = all(os.path.exists(f) for f in model_files)
                
                if models_exist:
                    try:
                        # Tentar carregar modelo existente
                        with open(f'models/{symbol}_models.pkl', 'rb') as f:
                            self.models[symbol] = pickle.load(f)
                        
                        self.scalers[symbol] = joblib.load(f'models/{symbol}_scaler.pkl')
                        self.feature_selectors[symbol] = joblib.load(f'models/{symbol}_selector.pkl')
                        
                        logger.info(f"✅ Modelo {symbol} carregado com sucesso")
                        self.is_trained = True
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao carregar modelo {symbol}: {e}")
                        models_to_train.append(symbol)
                else:
                    logger.info(f"📝 Modelo {symbol} não encontrado - será treinado")
                    models_to_train.append(symbol)
            
            # Treinar modelos faltantes em background se houver
            if models_to_train:
                logger.info(f"🧠 Iniciando treinamento automático para: {models_to_train}")
                self._train_missing_models_background(models_to_train)
            
            logger.info(f"🤖 IA Engine pronto - {len(self.models)} modelos carregados")
                
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
        
        logger.info("IA load models concluído - sistema pronto")

    def save_models(self, symbol: str):
        """Salvar modelos treinados"""
        try:
            import os
            
            # Criar diretório se não existir
            os.makedirs('models', exist_ok=True)
            
            if symbol in self.models:
                # Salvar modelos
                with open(f'models/{symbol}_models.pkl', 'wb') as f:
                    pickle.dump(self.models[symbol], f)
                    
                # Salvar scaler
                if symbol in self.scalers:
                    joblib.dump(self.scalers[symbol], f'models/{symbol}_scaler.pkl')
                    
                # Salvar feature selector
                if symbol in self.feature_selectors:
                    joblib.dump(self.feature_selectors[symbol], f'models/{symbol}_selector.pkl')
                    
                logger.info(f"Modelos salvos para {symbol}")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao salvar modelos: {e}")
            
        return False
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preparar features para o modelo de IA (versão simplificada)"""
        try:
            # Verificar se tem dados suficientes
            if len(df) < 20:
                logger.warning(f"Dados insuficientes: {len(df)} linhas")
                return df
            
            # Features básicas de preço
            df['price_change'] = df['close'].pct_change()
            df['price_change_abs'] = df['price_change'].abs()
            df['high_low_pct'] = (df['high'] - df['low']) / df['close']
            df['open_close_pct'] = (df['close'] - df['open']) / df['open']
            
            # Médias móveis e ratios
            for period in [5, 10, 20, 50]:
                if len(df) >= period:
                    df[f'sma_{period}'] = df['close'].rolling(period).mean()
                    df[f'price_sma_{period}_ratio'] = df['close'] / df[f'sma_{period}']
                    df[f'volume_sma_{period}'] = df['volume'].rolling(period).mean()
            
            # Features de volatilidade
            df['volatility_5'] = df['close'].pct_change().rolling(5).std()
            df['volatility_10'] = df['close'].pct_change().rolling(10).std()
            df['volatility_20'] = df['close'].pct_change().rolling(20).std()
            
            # Features de volume
            df['volume_change'] = df['volume'].pct_change()
            df['volume_price_trend'] = df['volume'] * df['price_change']
            
            # Features de momentum
            for period in [5, 10, 20]:
                if len(df) >= period:
                    df[f'momentum_{period}'] = df['close'] - df['close'].shift(period)
                    df[f'roc_{period}'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
            
            # RSI simplificado
            def calculate_rsi(prices, period=14):
                if len(prices) < period + 1:
                    return pd.Series([50] * len(prices), index=prices.index)
                
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return rsi.fillna(50)
            
            df['rsi_14'] = calculate_rsi(df['close'], 14)
            
            # MACD simplificado
            if len(df) >= 26:
                ema_12 = df['close'].ewm(span=12).mean()
                ema_26 = df['close'].ewm(span=26).mean()
                df['macd'] = ema_12 - ema_26
                df['macd_signal'] = df['macd'].ewm(span=9).mean()
                df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # Bollinger Bands simplificado
            if len(df) >= 20:
                sma_20 = df['close'].rolling(20).mean()
                std_20 = df['close'].rolling(20).std()
                df['bb_upper'] = sma_20 + (std_20 * 2)
                df['bb_lower'] = sma_20 - (std_20 * 2)
                df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Features temporais
            df['hour'] = pd.to_datetime(df.index).hour
            df['day_of_week'] = pd.to_datetime(df.index).dayofweek
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            
            # Limpar NaN com forward fill, backward fill e depois zero
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                df[col] = df[col].ffill().bfill().fillna(0)
            
            logger.info(f"Features preparadas: {len(df.columns)} colunas, {len(df)} linhas")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao preparar features: {e}")
            return df
    
    def _fallback_technical_prediction(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Fallback usando análise técnica - APENAS BUY/SELL"""
        try:
            logger.info(f"📊 Usando fallback técnico para {symbol}")
            
            # Calcular indicadores simples
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # RSI
            if 'rsi' in df.columns and not pd.isna(latest['rsi']):
                rsi = latest['rsi']
                if rsi < 45:  # Threshold mais agressivo
                    signal = 1  # BUY
                    confidence = 0.7
                    reason = f"RSI baixo: {rsi:.1f}"
                else:
                    signal = 0  # SELL
                    confidence = 0.7
                    reason = f"RSI alto: {rsi:.1f}"
            else:
                # Análise de preço simples
                price_change = (latest['close'] - prev['close']) / prev['close']
                if price_change > 0:  # Qualquer subida = BUY
                    signal = 1
                    confidence = 0.6
                    reason = "Price momentum up"
                else:  # Qualquer descida = SELL
                    signal = 0
                    confidence = 0.6
                    reason = "Price momentum down"
            
            signal_names = {0: 'SELL', 1: 'BUY'}
            
            return {
                'signal': signal,
                'confidence': confidence,
                'signal_type': signal_names[signal],
                'model_used': 'technical_fallback',
                'timestamp': datetime.now().isoformat(),
                'test_mode': False,
                'reason': reason            }
            
        except Exception as e:
            logger.error(f"Erro no fallback técnico: {e}")
            return {
                'signal': 0,
                'confidence': 0.5,
                'signal_type': 'SELL',
                'model_used': 'error_fallback',
                'timestamp': datetime.now().isoformat(),
                'test_mode': False,
                'error': str(e)
            }
    
    def _train_missing_models_background(self, symbols: List[str]):
        """Treinar modelos faltantes em background thread"""
        def train_worker():
            # Importar MarketDataManager dentro da thread
            from .market_data import MarketDataManager
            
            # Criar instância temporária para obter dados
            temp_market_data = MarketDataManager(self.config)
            
            for symbol in symbols:
                try:
                    logger.info(f"🧠 Treinando modelo para {symbol}...")
                    
                    # Obter dados históricos para treinamento
                    df = temp_market_data.get_historical_data(symbol, '1h', 1000)
                    
                    if df is not None and len(df) >= 200:
                        result = self.train_simple_model(df, symbol)
                        if result.get('success'):
                            self.save_models(symbol)
                            logger.info(f"✅ Modelo {symbol} treinado e salvo!")
                        else:
                            logger.warning(f"⚠️ Falha no treinamento de {symbol}")
                    else:
                        logger.warning(f"⚠️ Dados insuficientes para treinar {symbol}")
                        
                except Exception as e:
                    logger.error(f"❌ Erro no treinamento de {symbol}: {e}")
            
            logger.info("🧠 Treinamento em background concluído")
        
        # Executar em thread separada para não bloquear startup
        import threading
        thread = threading.Thread(target=train_worker, daemon=True)
        thread.start()

    def retrain_models_if_needed(self):
        """Retreinar modelos se necessário (chamado periodicamente)"""
        try:
            # Verificar se é hora de retreinar (a cada 24h)
            last_retrain = getattr(self, '_last_retrain', None)
            now = datetime.now()
            
            if last_retrain is None or (now - last_retrain).total_seconds() > 86400:  # 24h
                logger.info("🔄 Iniciando retreinamento periódico...")
                self._last_retrain = now
                
                symbols_to_retrain = list(self.models.keys())
                if symbols_to_retrain:
                    self._train_missing_models_background(symbols_to_retrain)
                    
        except Exception as e:
            logger.error(f"Erro no retreinamento: {e}")
