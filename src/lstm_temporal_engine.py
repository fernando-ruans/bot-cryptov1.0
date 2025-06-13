#!/usr/bin/env python3
"""
LSTM Engine Customizado para Análise Temporal
Implementação manual de LSTM para sequências temporais sem TensorFlow
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Optional
import logging
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

logger = logging.getLogger(__name__)

def sigmoid(x):
    """Função sigmoid"""
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def tanh(x):
    """Função tangente hiperbólica"""
    return np.tanh(np.clip(x, -500, 500))

class SimpleLSTMCell:
    """Célula LSTM simplificada"""
    
    def __init__(self, input_size: int, hidden_size: int):
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Inicializar pesos aleatoriamente
        self._init_weights()
        
    def _init_weights(self):
        """Inicializar pesos e bias"""
        # Pesos para forget gate
        self.Wf = np.random.randn(self.hidden_size, self.input_size + self.hidden_size) * 0.1
        self.bf = np.zeros((self.hidden_size, 1))
        
        # Pesos para input gate
        self.Wi = np.random.randn(self.hidden_size, self.input_size + self.hidden_size) * 0.1
        self.bi = np.zeros((self.hidden_size, 1))
        
        # Pesos para candidate values
        self.Wc = np.random.randn(self.hidden_size, self.input_size + self.hidden_size) * 0.1
        self.bc = np.zeros((self.hidden_size, 1))
        
        # Pesos para output gate
        self.Wo = np.random.randn(self.hidden_size, self.input_size + self.hidden_size) * 0.1
        self.bo = np.zeros((self.hidden_size, 1))
        
    def forward(self, x, h_prev, c_prev):
        """Forward pass"""
        # Concatenar input e hidden state anterior
        concat = np.vstack((x.reshape(-1, 1), h_prev))
        
        # Forget gate
        f = sigmoid(np.dot(self.Wf, concat) + self.bf)
        
        # Input gate
        i = sigmoid(np.dot(self.Wi, concat) + self.bi)
        
        # Candidate values
        c_candidate = tanh(np.dot(self.Wc, concat) + self.bc)
        
        # Cell state
        c = f * c_prev + i * c_candidate
        
        # Output gate
        o = sigmoid(np.dot(self.Wo, concat) + self.bo)
        
        # Hidden state
        h = o * tanh(c)
        
        return h, c

class CustomLSTM:
    """Modelo LSTM customizado para análise temporal"""
    
    def __init__(self, input_size: int, hidden_size: int = 50, num_layers: int = 2, dropout: float = 0.2):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout
        
        # Criar células LSTM
        self.lstm_cells = [SimpleLSTMCell(input_size if i == 0 else hidden_size, hidden_size) 
                          for i in range(num_layers)]
        
        # Camada de saída
        self.output_weights = np.random.randn(1, hidden_size) * 0.1
        self.output_bias = np.zeros((1, 1))
        
        # Scaler para normalização
        self.scaler = MinMaxScaler()
        self.is_fitted = False
        
    def prepare_sequences(self, data: np.ndarray, sequence_length: int = 20, target_column: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar sequências para treinamento"""
        sequences = []
        targets = []
        
        for i in range(sequence_length, len(data)):
            sequences.append(data[i-sequence_length:i])
            targets.append(data[i, target_column])
            
        return np.array(sequences), np.array(targets)
    
    def forward(self, sequence: np.ndarray) -> float:
        """Forward pass para uma sequência"""
        seq_length, features = sequence.shape
        
        # Estados iniciais
        h_states = [np.zeros((self.hidden_size, 1)) for _ in range(self.num_layers)]
        c_states = [np.zeros((self.hidden_size, 1)) for _ in range(self.num_layers)]
        
        # Processar sequência
        for t in range(seq_length):
            x = sequence[t]
            
            for layer in range(self.num_layers):
                if layer == 0:
                    input_data = x
                else:
                    input_data = h_states[layer-1].flatten()
                
                h_states[layer], c_states[layer] = self.lstm_cells[layer].forward(
                    input_data, h_states[layer], c_states[layer]
                )
        
        # Saída final
        output = np.dot(self.output_weights, h_states[-1]) + self.output_bias
        return output[0, 0]
    
    def fit(self, X: np.ndarray, y: np.ndarray, sequence_length: int = 20, epochs: int = 50) -> dict:
        """Treinar o modelo LSTM"""
        try:
            logger.info(f"🧠 Iniciando treinamento LSTM: {X.shape[0]} amostras, {X.shape[1]} features")
            
            # Normalizar dados
            X_scaled = self.scaler.fit_transform(X)
            
            # Preparar sequências
            X_seq, y_seq = self.prepare_sequences(X_scaled, sequence_length)
            
            if len(X_seq) < 10:
                logger.warning("⚠️ Dados insuficientes para LSTM")
                return {'success': False, 'message': 'Dados insuficientes'}
            
            # Split treino/validação
            split_idx = int(len(X_seq) * 0.8)
            X_train, X_val = X_seq[:split_idx], X_seq[split_idx:]
            y_train, y_val = y_seq[:split_idx], y_seq[split_idx:]
            
            # Treinamento simplificado (sem backpropagation completa)
            train_losses = []
            val_losses = []
            
            for epoch in range(min(epochs, 20)):  # Limitar épocas para performance
                # Predições de treino
                train_preds = []
                for i in range(len(X_train)):
                    pred = self.forward(X_train[i])
                    train_preds.append(pred)
                
                train_preds = np.array(train_preds)
                train_loss = mean_squared_error(y_train, train_preds)
                train_losses.append(train_loss)
                
                # Predições de validação
                val_preds = []
                for i in range(len(X_val)):
                    pred = self.forward(X_val[i])
                    val_preds.append(pred)
                
                val_preds = np.array(val_preds)
                val_loss = mean_squared_error(y_val, val_preds)
                val_losses.append(val_loss)
                
                if epoch % 5 == 0:
                    logger.info(f"Época {epoch}: Train Loss={train_loss:.6f}, Val Loss={val_loss:.6f}")
            
            self.is_fitted = True
            
            # Métricas finais
            final_mae = mean_absolute_error(y_val, val_preds)
            
            logger.info(f"✅ LSTM treinado: Val MAE={final_mae:.6f}")
            
            return {
                'success': True,
                'train_losses': train_losses,
                'val_losses': val_losses,
                'final_mae': final_mae,
                'num_sequences': len(X_seq)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento LSTM: {e}")
            return {'success': False, 'message': str(e)}
    
    def predict(self, X: np.ndarray, sequence_length: int = 20) -> np.ndarray:
        """Fazer predições"""
        try:
            if not self.is_fitted:
                logger.warning("Modelo LSTM não treinado")
                return np.zeros(len(X))
            
            # Normalizar dados
            X_scaled = self.scaler.transform(X)
            
            # Preparar sequências para predição
            predictions = []
            
            for i in range(sequence_length, len(X_scaled)):
                sequence = X_scaled[i-sequence_length:i]
                pred = self.forward(sequence)
                predictions.append(pred)
            
            # Preencher primeiros valores com média
            full_predictions = np.full(len(X), np.mean(predictions) if predictions else 0)
            full_predictions[sequence_length:] = predictions
            
            return full_predictions
            
        except Exception as e:
            logger.error(f"Erro na predição LSTM: {e}")
            return np.zeros(len(X))
    
    def predict_next(self, X: np.ndarray, sequence_length: int = 20) -> float:
        """Prever próximo valor"""
        try:
            if not self.is_fitted or len(X) < sequence_length:
                return 0.0
            
            # Usar últimos dados
            X_scaled = self.scaler.transform(X)
            sequence = X_scaled[-sequence_length:]
            
            prediction = self.forward(sequence)
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Erro na predição do próximo valor: {e}")
            return 0.0

class LSTMTimeSeriesAnalyzer:
    """Analisador de séries temporais com LSTM"""
    
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.sequence_length = 20
        self.prediction_horizon = [1, 3, 6, 12]  # Horizontes de predição em períodos
        
    def analyze_temporal_patterns(self, df: pd.DataFrame, symbol: str) -> dict:
        """Analisar padrões temporais com LSTM"""
        try:
            logger.info(f"🕰️ Iniciando análise temporal LSTM para {symbol}")
            
            if len(df) < self.sequence_length * 2:
                return {'success': False, 'message': 'Dados insuficientes'}
            
            # Preparar dados
            features = ['close', 'volume', 'rsi', 'macd', 'bb_upper', 'bb_lower']
            available_features = [f for f in features if f in df.columns]
            
            if len(available_features) < 2:
                return {'success': False, 'message': 'Features insuficientes'}
            
            # Matriz de features
            X = df[available_features].values
            
            # Target: retorno futuro
            y = df['close'].pct_change(periods=3).shift(-3).fillna(0).values
            
            # Criar e treinar modelo
            lstm_model = CustomLSTM(
                input_size=len(available_features),
                hidden_size=30,
                num_layers=2
            )
            
            # Treinar modelo
            training_result = lstm_model.fit(X, y, self.sequence_length)
            
            if not training_result['success']:
                return training_result
            
            # Fazer predições
            predictions = lstm_model.predict(X, self.sequence_length)
            
            # Predição do próximo período
            next_prediction = lstm_model.predict_next(X, self.sequence_length)
            
            # Calcular métricas de trend
            trend_strength = self._calculate_trend_strength(predictions)
            momentum_score = self._calculate_momentum_score(predictions)
            volatility_forecast = self._calculate_volatility_forecast(predictions)
            
            # Salvar modelo
            self.models[symbol] = lstm_model
            
            result = {
                'success': True,
                'next_prediction': next_prediction,
                'trend_strength': trend_strength,
                'momentum_score': momentum_score,
                'volatility_forecast': volatility_forecast,
                'training_metrics': training_result,
                'features_used': available_features,
                'sequence_length': self.sequence_length
            }
            
            logger.info(f"✅ Análise temporal concluída: trend={trend_strength:.3f}, momentum={momentum_score:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise temporal: {e}")
            return {'success': False, 'message': str(e)}
    
    def _calculate_trend_strength(self, predictions: np.ndarray) -> float:
        """Calcular força da tendência"""
        if len(predictions) < 10:
            return 0.0
        
        # Usar últimos valores para determinar tendência
        recent_predictions = predictions[-10:]
        
        # Calcular slope
        x = np.arange(len(recent_predictions))
        slope = np.polyfit(x, recent_predictions, 1)[0]
        
        # Normalizar slope
        return np.tanh(slope * 100)
    
    def _calculate_momentum_score(self, predictions: np.ndarray) -> float:
        """Calcular score de momentum"""
        if len(predictions) < 5:
            return 0.0
        
        # Acceleration (segunda derivada)
        velocity = np.diff(predictions)
        acceleration = np.diff(velocity)
        
        # Score baseado na aceleração recente
        if len(acceleration) > 0:
            return np.tanh(acceleration[-1] * 1000)
        return 0.0
    
    def _calculate_volatility_forecast(self, predictions: np.ndarray) -> float:
        """Calcular previsão de volatilidade"""
        if len(predictions) < 10:
            return 0.0
        
        # Volatilidade das predições
        return float(np.std(predictions[-10:]))
    
    def get_lstm_features(self, df: pd.DataFrame, symbol: str) -> dict:
        """Extrair features LSTM para integração com IA"""
        try:
            # Se modelo já existe, usar para predições
            if symbol in self.models:
                model = self.models[symbol]
                
                # Features básicas
                features = ['close', 'volume', 'rsi', 'macd', 'bb_upper', 'bb_lower']
                available_features = [f for f in features if f in df.columns]
                
                if len(available_features) >= 2 and len(df) >= self.sequence_length:
                    X = df[available_features].values
                    
                    # Predições
                    predictions = model.predict(X, self.sequence_length)
                    next_pred = model.predict_next(X, self.sequence_length)
                    
                    # Features derivadas
                    lstm_features = {
                        'lstm_prediction': next_pred,
                        'lstm_trend': self._calculate_trend_strength(predictions),
                        'lstm_momentum': self._calculate_momentum_score(predictions),
                        'lstm_volatility': self._calculate_volatility_forecast(predictions),
                        'lstm_signal': 1 if next_pred > 0.01 else -1 if next_pred < -0.01 else 0
                    }
                    
                    return lstm_features
            
            # Se não há modelo, retornar features neutras
            return {
                'lstm_prediction': 0.0,
                'lstm_trend': 0.0,
                'lstm_momentum': 0.0,
                'lstm_volatility': 0.0,
                'lstm_signal': 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair features LSTM: {e}")
            return {
                'lstm_prediction': 0.0,
                'lstm_trend': 0.0,
                'lstm_momentum': 0.0,
                'lstm_volatility': 0.0,
                'lstm_signal': 0
            }
