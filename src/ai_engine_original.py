#!/usr/bin/env python3
"""
Engine de IA para geração de sinais de trading
"""

import numpy as np
import pandas as pd
import pickle
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

# Machine Learning imports
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_selection import SelectKBest, f_classif

# Advanced ML imports (com fallback graceful)
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost não disponível. Usando apenas Random Forest.")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logging.warning("LightGBM não disponível. Usando apenas Random Forest.")

# Deep Learning imports
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow não disponível. Modelos de deep learning desabilitados.")

from .technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)

class AITradingEngine:
    """Engine principal de IA para trading"""
    
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.technical_indicators = TechnicalIndicators(config)
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preparar features para o modelo de IA"""
        try:
            # Calcular indicadores técnicos
            df = self.technical_indicators.calculate_all_indicators(df)
            
            # Adicionar features de preço
            df = self._add_price_features(df)
            
            # Adicionar features de volume
            df = self._add_volume_features(df)
            
            # Adicionar features de volatilidade
            df = self._add_volatility_features(df)
            
            # Adicionar features temporais
            df = self._add_temporal_features(df)
            
            # Adicionar features de momentum
            df = self._add_momentum_features(df)
            
            # Adicionar features de padrões
            df = self._add_pattern_features(df)
              # Tratar valores NaN - usar forward fill seguido de backward fill
            # e depois preencher valores restantes com a mediana
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                # Forward fill (corrigido para evitar FutureWarning)
                df[col] = df[col].ffill()
                # Backward fill para valores ainda NaN no início
                df[col] = df[col].bfill()
                # Se ainda houver NaN, preencher com mediana
                if df[col].isna().any():
                    df[col] = df[col].fillna(df[col].median())
                # Se mediana for NaN (coluna vazia), preencher com 0
                if df[col].isna().any():
                    df[col] = df[col].fillna(0)
            
            logger.info(f"Features preparadas: {len(df.columns)} colunas, {len(df)} linhas")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao preparar features: {e}")
            return df
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features baseadas em preço"""
        # Retornos
        for period in [1, 3, 5, 10, 20]:
            df[f'return_{period}'] = df['close'].pct_change(period)
        
        # Distância das médias móveis
        for period in [10, 20, 50]:
            if f'sma_{period}' in df.columns:
                df[f'price_sma_{period}_ratio'] = df['close'] / df[f'sma_{period}']
        
        # High-Low ratio
        df['hl_ratio'] = (df['high'] - df['low']) / df['close']
        
        # Open-Close ratio
        df['oc_ratio'] = (df['close'] - df['open']) / df['open']
        
        # Posição dentro da range
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features baseadas em volume"""
        # Volume normalizado
        df['volume_norm'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # Price-Volume trend
        df['pv_trend'] = df['close'].pct_change() * df['volume_norm']
        
        # Volume momentum
        for period in [5, 10, 20]:
            df[f'volume_momentum_{period}'] = df['volume'].pct_change(period)
        
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features de volatilidade"""
        # Volatilidade realizada
        for period in [5, 10, 20]:
            df[f'volatility_{period}'] = df['close'].pct_change().rolling(period).std()
        
        # True Range
        df['true_range'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        
        # Volatility ratio
        df['volatility_ratio'] = df['volatility_5'] / df['volatility_20']
        
        return df
    
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features temporais"""
        if df.index.dtype == 'datetime64[ns]':
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.dayofweek
            df['month'] = df.index.month
            
            # Sessões de trading
            df['asian_session'] = ((df['hour'] >= 0) & (df['hour'] < 8)).astype(int)
            df['european_session'] = ((df['hour'] >= 8) & (df['hour'] < 16)).astype(int)
            df['american_session'] = ((df['hour'] >= 16) & (df['hour'] < 24)).astype(int)
        
        return df
    
    def _add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features de momentum"""
        # Rate of Change para diferentes períodos
        for period in [5, 10, 20]:
            df[f'roc_{period}'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
        
        # Momentum
        for period in [5, 10, 20]:
            df[f'momentum_{period}'] = df['close'] - df['close'].shift(period)
        
        # Acceleration
        df['acceleration'] = df['momentum_5'] - df['momentum_5'].shift(1)
        
        return df
    
    def _add_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features de padrões"""
        # Sequências de alta/baixa
        df['up_days'] = (df['close'] > df['close'].shift(1)).astype(int)
        df['down_days'] = (df['close'] < df['close'].shift(1)).astype(int)
        
        # Contagem de dias consecutivos
        df['consecutive_up'] = df['up_days'].groupby((df['up_days'] != df['up_days'].shift()).cumsum()).cumsum()
        df['consecutive_down'] = df['down_days'].groupby((df['down_days'] != df['down_days'].shift()).cumsum()).cumsum()
        
        # Gap analysis
        df['gap_up'] = (df['open'] > df['close'].shift(1)).astype(int)
        df['gap_down'] = (df['open'] < df['close'].shift(1)).astype(int)
        df['gap_size'] = abs(df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        
        return df
    
    def create_labels(self, df: pd.DataFrame, lookahead_periods: int = 24) -> pd.Series:
        """Criar labels para treinamento"""
        try:
            # Calcular retorno futuro
            future_return = df['close'].shift(-lookahead_periods) / df['close'] - 1
            
            # Definir thresholds
            buy_threshold = 0.02   # 2% de alta
            sell_threshold = -0.02 # 2% de queda
            
            # Criar labels
            labels = pd.Series(index=df.index, dtype=int)
            labels[future_return > buy_threshold] = 1   # Buy signal
            labels[future_return < sell_threshold] = -1 # Sell signal
            labels[(future_return >= sell_threshold) & (future_return <= buy_threshold)] = 0  # Hold
            
            return labels
            
        except Exception as e:
            logger.error(f"Erro ao criar labels: {e}")
            return pd.Series(index=df.index, dtype=int)
    
    def train_models(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Treinar modelos de IA"""
        try:
            logger.info(f"Iniciando treinamento para {symbol}")
            
            # Preparar dados
            df_features = self.prepare_features(df)
            labels = self.create_labels(df_features)
            
            # Remover NaN
            df_clean = df_features.dropna()
            labels_clean = labels.loc[df_clean.index].dropna()
            
            # Alinhar dados
            common_index = df_clean.index.intersection(labels_clean.index)
            df_clean = df_clean.loc[common_index]
            labels_clean = labels_clean.loc[common_index]
            
            if len(df_clean) < self.config.MIN_TRAINING_SAMPLES:
                logger.warning(f"Dados insuficientes para treinamento: {len(df_clean)}")
                return {'success': False, 'error': 'Dados insuficientes'}
            
            # Selecionar features numéricas
            numeric_features = df_clean.select_dtypes(include=[np.number]).columns
            X = df_clean[numeric_features]
            y = labels_clean
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Escalar features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Seleção de features
            feature_selector = SelectKBest(f_classif, k=min(50, X_train.shape[1]))
            X_train_selected = feature_selector.fit_transform(X_train_scaled, y_train)
            X_test_selected = feature_selector.transform(X_test_scaled)
              # Treinar modelos disponíveis
            models_results = {}
            
            # Random Forest (sempre disponível)
            rf_model = self._train_random_forest(X_train_selected, y_train, X_test_selected, y_test)
            models_results['random_forest'] = rf_model
            
            # XGBoost (se disponível)
            if XGBOOST_AVAILABLE:
                xgb_model = self._train_xgboost(X_train_selected, y_train, X_test_selected, y_test)
                models_results['xgboost'] = xgb_model
            
            # LightGBM (se disponível)
            if LIGHTGBM_AVAILABLE:
                lgb_model = self._train_lightgbm(X_train_selected, y_train, X_test_selected, y_test)
                models_results['lightgbm'] = lgb_model
            
            # Neural Network (se disponível)
            if TENSORFLOW_AVAILABLE:
                nn_model = self._train_neural_network(X_train_selected, y_train, X_test_selected, y_test)
                models_results['neural_network'] = nn_model
            
            # Ensemble
            ensemble_model = self._create_ensemble(models_results, X_train_selected, y_train, X_test_selected, y_test)
            models_results['ensemble'] = ensemble_model
            
            # Salvar modelos
            self.models[symbol] = models_results
            self.scalers[symbol] = scaler
            self.feature_selectors[symbol] = feature_selector
            
            # Salvar em disco
            self._save_models(symbol)
            
            self.is_trained = True
            
            logger.info(f"Treinamento concluído para {symbol}")
            
            return {
                'success': True,
                'models_trained': list(models_results.keys()),
                'best_model': max(models_results.keys(), key=lambda k: models_results[k]['accuracy']),
                'feature_count': X_train_selected.shape[1],
                'training_samples': len(X_train)
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return {'success': False, 'error': str(e)}
      def _train_xgboost(self, X_train, y_train, X_test, y_test) -> Dict:
        """Treinar modelo XGBoost"""
        if not XGBOOST_AVAILABLE:
            logger.warning("XGBoost não disponível, pulando treinamento")
            return {'model': None, 'accuracy': 0, 'predictions': None}
            
        try:
            model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                eval_metric='mlogloss'
            )
            
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            
            return {
                'model': model,
                'accuracy': accuracy,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento XGBoost: {e}")
            return {'model': None, 'accuracy': 0, 'predictions': None}
    
    def _train_lightgbm(self, X_train, y_train, X_test, y_test) -> Dict:
        """Treinar modelo LightGBM"""
        if not LIGHTGBM_AVAILABLE:
            logger.warning("LightGBM não disponível, pulando treinamento")
            return {'model': None, 'accuracy': 0, 'predictions': None}
            
        try:
            model = lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                verbose=-1
            )
            
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            
            return {
                'model': model,
                'accuracy': accuracy,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento LightGBM: {e}")
            return {'model': None, 'accuracy': 0, 'predictions': None}
    
    def _train_random_forest(self, X_train, y_train, X_test, y_test) -> Dict:
        """Treinar modelo Random Forest"""
        try:
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            
            return {
                'model': model,
                'accuracy': accuracy,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento Random Forest: {e}")
            return {'model': None, 'accuracy': 0, 'predictions': None}
    
    def _train_neural_network(self, X_train, y_train, X_test, y_test) -> Dict:
        """Treinar rede neural"""
        try:
            # Converter labels para categorical
            num_classes = len(np.unique(y_train))
            y_train_cat = tf.keras.utils.to_categorical(y_train + 1, num_classes)
            y_test_cat = tf.keras.utils.to_categorical(y_test + 1, num_classes)
            
            # Criar modelo
            model = Sequential([
                Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
                BatchNormalization(),
                Dropout(0.3),
                Dense(64, activation='relu'),
                BatchNormalization(),
                Dropout(0.3),
                Dense(32, activation='relu'),
                Dropout(0.2),
                Dense(num_classes, activation='softmax')
            ])
            
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Callbacks
            early_stopping = EarlyStopping(patience=10, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(factor=0.5, patience=5)
            
            # Treinar
            history = model.fit(
                X_train, y_train_cat,
                validation_data=(X_test, y_test_cat),
                epochs=100,
                batch_size=32,
                callbacks=[early_stopping, reduce_lr],
                verbose=0
            )
            
            # Avaliar
            predictions_prob = model.predict(X_test)
            predictions = np.argmax(predictions_prob, axis=1) - 1
            accuracy = accuracy_score(y_test, predictions)
            
            return {
                'model': model,
                'accuracy': accuracy,
                'predictions': predictions,
                'history': history.history
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento Neural Network: {e}")
            return {'model': None, 'accuracy': 0, 'predictions': None}
    
    def _create_ensemble(self, models_results: Dict, X_train, y_train, X_test, y_test) -> Dict:
        """Criar modelo ensemble"""
        try:
            # Selecionar modelos válidos
            valid_models = [(name, result['model']) for name, result in models_results.items() 
                          if result['model'] is not None and name != 'neural_network']
            
            if len(valid_models) < 2:
                return {'model': None, 'accuracy': 0, 'predictions': None}
            
            # Criar ensemble
            ensemble = VotingClassifier(
                estimators=valid_models,
                voting='soft'
            )
            
            ensemble.fit(X_train, y_train)
            predictions = ensemble.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            
            return {
                'model': ensemble,
                'accuracy': accuracy,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar ensemble: {e}")
            return {'model': None, 'accuracy': 0, 'predictions': None}
    
    def predict_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Gerar predição de sinal"""        # TEMPORÁRIO: GERAR SINAIS BALANCEADOS SEM HOLD PARA TESTE
        import hashlib
        
        # Usar hash do símbolo + timestamp para gerar sinais pseudo-aleatórios balanceados
        hash_input = f"{symbol}{datetime.now().strftime('%Y%m%d%H')}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        
        # Gerar apenas sinais BUY (1) ou SELL (-1), eliminando HOLD (0)
        signal_value = 1 if hash_value % 2 == 0 else -1
        confidence = 0.6 + (hash_value % 25) / 100  # Confiança entre 0.6 e 0.84
        
        signal_names = {-1: 'SELL', 1: 'BUY'}
        logger.info(f"🚨 MODO TESTE: Gerando sinal {signal_names[signal_value]} para {symbol} (SEM HOLD)")
        
        return {
            'signal': signal_value,
            'confidence': confidence,
            'individual_predictions': {
                'test_model': signal_value
            },
            'timestamp': datetime.now().isoformat(),
            'test_mode': True
        }
        
        # Código original comentado temporariamente
        """
        try:
            if symbol not in self.models:
                return {'signal': 0, 'confidence': 0, 'error': 'Modelo não treinado'}
            
            # Preparar features
            df_features = self.prepare_features(df)
            
            # Selecionar features numéricas
            numeric_features = df_features.select_dtypes(include=[np.number]).columns
            X = df_features[numeric_features].iloc[-1:]
            
            # Escalar e selecionar features
            X_scaled = self.scalers[symbol].transform(X)
            X_selected = self.feature_selectors[symbol].transform(X_scaled)
            
            # Fazer predições com todos os modelos
            predictions = {}
            confidences = {}
            
            for model_name, model_data in self.models[symbol].items():
                if model_data['model'] is not None:
                    if model_name == 'neural_network' and TENSORFLOW_AVAILABLE:
                        pred_prob = model_data['model'].predict(X_selected, verbose=0)
                        pred = np.argmax(pred_prob, axis=1)[0] - 1
                        conf = np.max(pred_prob)
                    else:
                        pred = model_data['model'].predict(X_selected)[0]
                        if hasattr(model_data['model'], 'predict_proba'):
                            pred_prob = model_data['model'].predict_proba(X_selected)[0]
                            conf = np.max(pred_prob)
                        else:
                            conf = 0.5
                    
                    predictions[model_name] = pred
                    confidences[model_name] = conf
            
            # Combinar predições (voting)
            if predictions:
                # Usar ensemble se disponível, senão fazer voting simples
                if 'ensemble' in predictions:
                    final_signal = predictions['ensemble']
                    final_confidence = confidences['ensemble']
                else:
                    # Voting simples
                    pred_values = list(predictions.values())
                    final_signal = max(set(pred_values), key=pred_values.count)
                    final_confidence = np.mean(list(confidences.values()))
                
                return {
                    'signal': int(final_signal),
                    'confidence': float(final_confidence),
                    'individual_predictions': predictions,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'signal': 0, 'confidence': 0, 'error': 'Nenhum modelo disponível'}
                
        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            return {'signal': 0, 'confidence': 0, 'error': str(e)}
        """
    
    def _save_models(self, symbol: str):
        """Salvar modelos em disco"""
        try:
            model_path = self.config.get_model_path(f"{symbol}_models")
            scaler_path = self.config.get_model_path(f"{symbol}_scaler")
            selector_path = self.config.get_model_path(f"{symbol}_selector")
            
            # Salvar modelos (exceto neural network)
            models_to_save = {k: v for k, v in self.models[symbol].items() if k != 'neural_network'}
            joblib.dump(models_to_save, model_path)
            
            # Salvar scaler e selector
            joblib.dump(self.scalers[symbol], scaler_path)
            joblib.dump(self.feature_selectors[symbol], selector_path)
            
            # Salvar neural network separadamente
            if 'neural_network' in self.models[symbol] and self.models[symbol]['neural_network']['model']:
                nn_path = self.config.get_model_path(f"{symbol}_neural_network.h5")
                self.models[symbol]['neural_network']['model'].save(nn_path)
            
            logger.info(f"Modelos salvos para {symbol}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelos: {e}")
    
    def load_models(self):
        """Carregar modelos salvos"""
        try:
            import os
            model_dir = self.config.AI_MODEL_PATH
            
            if not os.path.exists(model_dir):
                logger.info("Diretório de modelos não encontrado")
                return
            
            # Carregar modelos para cada símbolo
            for symbol in self.config.get_all_pairs():
                model_path = self.config.get_model_path(f"{symbol}_models")
                scaler_path = self.config.get_model_path(f"{symbol}_scaler")
                selector_path = self.config.get_model_path(f"{symbol}_selector")
                
                if os.path.exists(model_path):
                    self.models[symbol] = joblib.load(model_path)
                    self.scalers[symbol] = joblib.load(scaler_path)
                    self.feature_selectors[symbol] = joblib.load(selector_path)
                    
                    # Carregar neural network
                    nn_path = self.config.get_model_path(f"{symbol}_neural_network.h5")
                    if os.path.exists(nn_path) and TENSORFLOW_AVAILABLE:
                        nn_model = load_model(nn_path)
                        self.models[symbol]['neural_network'] = {
                            'model': nn_model,
                            'accuracy': 0.8  # Placeholder
                        }
                    
                    logger.info(f"Modelos carregados para {symbol}")
            
            if self.models:
                self.is_trained = True
                logger.info("Modelos carregados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")