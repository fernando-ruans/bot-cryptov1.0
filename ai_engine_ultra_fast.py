"""
AI Engine V3 Otimizado - VERSÃO SUPER RÁPIDA
Reduz drasticamente o tempo de processamento e logs
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import logging
import warnings
import time
from pathlib import Path
import pickle
import hashlib

# Suprimir warnings desnecessários
warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None

# Machine Learning
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import accuracy_score, classification_report

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

logger = logging.getLogger(__name__)

class UltraFastAIEngine:
    """AI Engine otimizado para máxima velocidade"""
    
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.model_performance = {}
        self.feature_cache = {}
          # Cache para acelerar processamento
        self.cache_ttl = 120  # 2 minutos (reduzido de 5)
        self.data_cache = {}
        self.feature_cache = {}  # Cache específico para features
        
        # Configurações otimizadas para velocidade
        self.min_confidence_threshold = 0.10  # Mais baixo ainda
        self.max_features = 30  # Reduzido de 50 para 30
        self.quick_mode = True
        self.use_cache = True  # Flag para usar cache
        
        # Modelos leves e rápidos
        if XGB_AVAILABLE:
            self.ensemble_models = {
                'rf': RandomForestClassifier(
                    n_estimators=20,  # Reduzido de 100
                    max_depth=8,      # Reduzido de 15
                    random_state=42,
                    n_jobs=2,         # Reduzido de -1
                    warm_start=True
                ),
                'xgb': xgb.XGBClassifier(
                    n_estimators=20,  # Reduzido de 100
                    max_depth=6,      # Reduzido de 10
                    random_state=42,
                    n_jobs=2,         # Reduzido de -1
                    verbosity=0       # Sem logs
                )
            }
        else:
            self.ensemble_models = {
                'rf': RandomForestClassifier(
                    n_estimators=20,
                    max_depth=8,
                    random_state=42,
                    n_jobs=2
                ),
                'gb': GradientBoostingClassifier(
                    n_estimators=20,  # Reduzido de 100
                    max_depth=6,      # Reduzido de 10
                    random_state=42
                )
            }
    
    def _get_cache_key(self, symbol: str, df_hash: str) -> str:
        """Gerar chave de cache baseada no símbolo e hash dos dados"""
        return f"{symbol}_{df_hash}"
    
    def _get_df_hash(self, df: pd.DataFrame) -> str:
        """Gerar hash dos dados para cache"""
        try:
            # Hash apenas das últimas 10 linhas para velocidade
            last_rows = df.tail(10).to_string()
            return hashlib.md5(last_rows.encode()).hexdigest()[:8]
        except:
            return str(int(time.time()))
    def _create_fast_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Criar apenas features essenciais para máxima velocidade"""
        try:
            # Cache de features baseado no hash dos dados
            df_hash = self._get_df_hash(df)
            if df_hash in self.feature_cache:
                return self.feature_cache[df_hash]
            
            result = df.copy()
            
            # Features mínimas apenas
            if 'close' in df.columns:
                # Médias móveis essenciais
                result['sma_10'] = df['close'].rolling(10).mean()
                result['sma_20'] = df['close'].rolling(20).mean()
                result['sma_ratio'] = result['sma_10'] / result['sma_20']
                
                # RSI simplificado (período menor)
                delta = df['close'].diff()
                gain = delta.where(delta > 0, 0).rolling(7).mean()  # Reduzido de 14 para 7
                loss = (-delta.where(delta < 0, 0)).rolling(7).mean()
                rs = gain / loss
                result['rsi'] = 100 - (100 / (1 + rs))
                
                # Volatilidade simples
                result['volatility'] = df['close'].rolling(10).std()  # Reduzido de 20 para 10
                
                # Volume ratio (se disponível)
                if 'volume' in df.columns:
                    result['volume_sma'] = df['volume'].rolling(10).mean()
                    result['volume_ratio'] = df['volume'] / result['volume_sma']
                
                # Retornos simples
                result['returns_1'] = df['close'].pct_change(1)
                result['returns_3'] = df['close'].pct_change(3)  # Reduzido de 5 para 3
                
                # Momentum simples
                result['momentum'] = df['close'] / df['close'].shift(5) - 1  # Reduzido de 10 para 5
            
            # Remover infinitos e NaN
            result = result.replace([np.inf, -np.inf], np.nan)
            result = result.fillna(method='bfill').fillna(0)
            
            # Cache resultado
            self.feature_cache[df_hash] = result
            
            # Limitar cache
            if len(self.feature_cache) > 20:
                oldest_key = list(self.feature_cache.keys())[0]
                del self.feature_cache[oldest_key]
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao criar features rápidas: {e}")
            return df
    
    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Preparar dados de treino de forma rápida"""
        try:
            # Criar features rápidas
            df_features = self._create_fast_features(df)
            
            # Target simples baseado em retornos futuros
            future_returns = df['close'].shift(-3) / df['close'] - 1  # 3 períodos à frente
            
            # Classificação simples
            target = pd.Series(2, index=df.index)  # Default HOLD
            target[future_returns > 0.01] = 1      # BUY se retorno > 1%
            target[future_returns < -0.01] = 0     # SELL se retorno < -1%
            
            # Selecionar apenas features numéricas
            numeric_features = df_features.select_dtypes(include=[np.number]).columns
            X = df_features[numeric_features]
            
            # Limitar número de features para velocidade
            if len(X.columns) > self.max_features:
                # Usar correlação com target para seleção rápida
                correlations = abs(X.corrwith(target))
                top_features = correlations.nlargest(self.max_features).index
                X = X[top_features]
            
            return X, target
            
        except Exception as e:
            logger.error(f"Erro ao preparar dados de treino: {e}")
            return pd.DataFrame(), pd.Series()
    
    def ultra_fast_predict(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Predição ultra rápida com cache agressivo"""
        try:
            start_time = time.time()
            
            # Verificar cache
            df_hash = self._get_df_hash(df)
            cache_key = self._get_cache_key(symbol, df_hash)
            
            if cache_key in self.data_cache:
                cache_data = self.data_cache[cache_key]
                if time.time() - cache_data['timestamp'] < self.cache_ttl:
                    # logger.info(f"🚀 Cache hit para {symbol} - {time.time() - start_time:.2f}s")
                    return cache_data['result']
            
            # Preparar dados rapidamente
            X, y = self._prepare_training_data(df)
            
            if X.empty or len(X) < 50:
                return self._default_prediction()
              # Treinar modelo leve se necessário
            if symbol not in self.models or len(self.models) == 0:
                self._train_ultra_fast_model(X, y, symbol)
            
            # Predição
            try:
                # Usar apenas último ponto para predição
                X_pred = X.iloc[-1:].fillna(0)
                
                # Ensemble rápido
                predictions = []
                confidences = []
                
                for model_name, model in self.ensemble_models.items():
                    if model:
                        try:
                            pred = model.predict(X_pred)[0]
                            prob = model.predict_proba(X_pred)[0]
                            conf = max(prob)
                            
                            predictions.append(pred)
                            confidences.append(conf)
                        except:
                            continue
                
                if not predictions:
                    return self._default_prediction()
                
                # Decisão final por maioria
                final_prediction = max(set(predictions), key=predictions.count)
                avg_confidence = np.mean(confidences)
                
                # Aplicar threshold
                if avg_confidence < self.min_confidence_threshold:
                    final_prediction = 2  # HOLD
                
                # Mapear para strings
                signal_map = {0: 'sell', 1: 'buy', 2: 'hold'}
                signal_type = signal_map.get(final_prediction, 'hold')
                
                # Calcular preços
                current_price = df['close'].iloc[-1]
                volatility = df['close'].rolling(20).std().iloc[-1] or current_price * 0.02
                
                if signal_type == 'buy':
                    stop_loss = current_price - (volatility * 2)
                    take_profit = current_price + (volatility * 2)
                elif signal_type == 'sell':
                    stop_loss = current_price + (volatility * 2)
                    take_profit = current_price - (volatility * 2)
                else:
                    stop_loss = 0
                    take_profit = 0
                
                result = {
                    'signal': final_prediction,
                    'signal_type': signal_type,
                    'confidence': avg_confidence,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'model_used': 'UltraFast',
                    'processing_time': time.time() - start_time,
                    'optimized_v4': True
                }
                
                # Cache resultado
                self.data_cache[cache_key] = {
                    'result': result,
                    'timestamp': time.time()
                }
                
                # Limpar cache antigo
                if len(self.data_cache) > 100:
                    oldest_key = min(self.data_cache.keys(), 
                                   key=lambda k: self.data_cache[k]['timestamp'])
                    del self.data_cache[oldest_key]
                
                logger.info(f"🎯 {symbol}: {signal_type.upper()} (conf: {avg_confidence:.3f}, time: {time.time() - start_time:.2f}s)")
                return result
                
            except Exception as e:
                logger.error(f"Erro na predição para {symbol}: {e}")
                return self._default_prediction()
                
        except Exception as e:
            logger.error(f"Erro geral na predição ultra rápida: {e}")
            return self._default_prediction()
    def _train_ultra_fast_model(self, X: pd.DataFrame, y: pd.Series, symbol: str):
        """Treinar modelo ultra rápido"""
        try:
            # Remover NaN
            mask = ~(X.isna().any(axis=1) | y.isna())
            X_clean = X[mask]
            y_clean = y[mask]
            
            if len(X_clean) < 30:  # Reduzido de 50
                return
            
            # Usar apenas dados mais recentes para velocidade
            recent_size = min(200, len(X_clean))  # Máximo 200 amostras
            X_recent = X_clean.tail(recent_size)
            y_recent = y_clean.tail(recent_size)
            
            # Modelo super simples e rápido
            model = RandomForestClassifier(
                n_estimators=5,   # Muito reduzido (era 10)
                max_depth=3,      # Muito reduzido (era 5)
                random_state=42,
                n_jobs=1,
                max_features='sqrt'  # Menos features
            )
            
            model.fit(X_recent, y_recent)
            
            # Atualizar ensemble com modelo único para velocidade
            self.ensemble_models = {'rf': model}  # Só um modelo
            self.models[symbol] = model
            
            # Calcular acurácia simples
            if len(X_recent) > 10:
                train_pred = model.predict(X_recent[-10:])
                train_acc = accuracy_score(y_recent[-10:], train_pred)
                self.model_performance[symbol] = {'accuracy': train_acc}
            
            # logger.info(f"🚀 Modelo ultra rápido treinado para {symbol}")
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo ultra rápido para {symbol}: {e}")
    
    def _train_fast_model(self, X: pd.DataFrame, y: pd.Series, symbol: str):
        """Método de compatibilidade"""
        return self._train_ultra_fast_model(X, y, symbol)
    
    def _default_prediction(self) -> Dict:
        """Predição padrão quando há falhas"""
        return {
            'signal': 2,
            'signal_type': 'hold',
            'confidence': 0.3,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'model_used': 'Default',
            'optimized_v4': True
        }
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preparar features de forma super rápida"""
        return self._create_fast_features(df)
    
    def load_models(self):
        """Método de compatibilidade - models são criados on-demand"""
        logger.info("✅ UltraFast AI Engine - modelos serão criados dinamicamente")
        return True
    
    # Métodos de compatibilidade
    def optimized_predict_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Método de compatibilidade"""
        return self.ultra_fast_predict(df, symbol)
    
    def ultra_predict_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Método de compatibilidade"""
        return self.ultra_fast_predict(df, symbol)
    
    def predict_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Método de compatibilidade"""
        return self.ultra_fast_predict(df, symbol)
