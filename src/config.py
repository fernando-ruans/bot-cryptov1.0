#!/usr/bin/env python3
"""
Arquivo de configuração para o Trading Bot AI
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Config:
    """Configurações do sistema de trading"""
    
    # Configurações de API
    BINANCE_API_KEY: str = field(default_factory=lambda: os.getenv('BINANCE_API_KEY', ''))
    BINANCE_SECRET_KEY: str = field(default_factory=lambda: os.getenv('BINANCE_SECRET_KEY', ''))
    
    # Configurações de timeframes
    TIMEFRAMES: List[str] = field(default_factory=lambda: ['1m', '5m', '15m', '30m', '1h', '4h', '1d'])
    DEFAULT_TIMEFRAME: str = '1h'
    
    # Pares de trading - EXPANDIDOS para múltiplos ativos
    CRYPTO_PAIRS: List[str] = field(default_factory=lambda: [
        # Crypto Major (alta liquidez)
        'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT',
        'BNBUSDT', 'XRPUSDT', 'LTCUSDT', 'BCHUSDT', 'EOSUSDT',
        # Crypto Alt (média liquidez)  
        'SOLUSDT', 'MATICUSDT', 'AVAXUSDT', 'UNIUSDT', 'ATOMUSDT',
        'ALGOUSDT', 'FILUSDT', 'AAVEUSDT', 'SUSHIUSDT', 'COMPUSDT'
    ])
    
    FOREX_PAIRS: List[str] = field(default_factory=lambda: [
        # Forex Major (alta liquidez)
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD',
        'USDCAD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'EURGBP',
        # Forex Minor (média liquidez)
        'EURCHF', 'GBPCHF', 'AUDCAD', 'AUDJPY', 'NZDJPY'
    ])
    
    # NOVOS: Índices de ações
    INDEX_PAIRS: List[str] = field(default_factory=lambda: [
        'SPX500', 'NAS100', 'DJI30', 'UK100', 'GER30',
        'FRA40', 'JPN225', 'AUS200', 'HK50', 'CHINA50'
    ])
    
    # Configurações de IA
    AI_MODEL_PATH: str = 'models/'
    RETRAIN_INTERVAL_HOURS: int = 24
    MIN_TRAINING_SAMPLES: int = 100  # Reduzido para permitir treinamento com menos dados
    
    # Indicadores técnicos
    TECHNICAL_INDICATORS: Dict = field(default_factory=lambda: {
        'sma_periods': [10, 20, 50, 100, 200],
        'ema_periods': [12, 26, 50],
        'rsi_period': 14,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'bb_period': 20,
        'bb_std': 2,
        'stoch_k': 14,
        'stoch_d': 3,
        'atr_period': 14,
        'adx_period': 14
    })
    
    # Configurações de volume
    VOLUME_INDICATORS: Dict = field(default_factory=lambda: {
        'volume_sma_period': 20,
        'volume_threshold_multiplier': 1.5,
        'obv_enabled': True,
        'vwap_enabled': True
    })
    
    # Configurações de risco - Nova estratégia IA 1:1 com alta assertividade
    RISK_MANAGEMENT: Dict = field(default_factory=lambda: {
        'max_risk_per_trade': 0.03,   # 3% por trade (maior exposição para 1:1)
        'max_daily_loss': 0.08,       # 8% perda diária máxima
        'max_open_positions': 2,      # Máximo 2 posições (foco em qualidade)
        'stop_loss_pct': 0.025,       # 2.5% stop loss (1:1 ratio)
        'take_profit_pct': 0.025,     # 2.5% take profit (1:1 ratio)
        'trailing_stop_pct': 0.008,   # 0.8% trailing stop
        'risk_reward_ratio': 1.0,     # Ratio 1:1 (risco:recompensa)
        'min_ai_confidence': 0.30     # Mínimo 30% confiança IA para executar (muito permissivo)
    })
    
    # Configurações de sinal - Nova estratégia IA com análise de mercado
    SIGNAL_CONFIG: Dict = field(default_factory=lambda: {
        'min_confidence': 0.01,      # 🎯 Confiança mínima 1% (extremamente permissivo)
        'min_ai_confidence': 0.01,   # 🤖 Confiança mínima da IA 1% (extremamente permissivo)
        'max_confidence': 0.98,      # 📊 Confiança máxima 98% (quase certeza)
        'signal_cooldown_minutes': 0, # ⏱️ Cooldown DESABILITADO para desenvolvimento
        'max_signals_per_hour': 20,    # 📈 Máximo 20 sinais por hora
        'enable_ai_analysis': True,   # ✅ Análise IA obrigatória
        'enable_market_context': True, # ✅ Contexto de mercado obrigatório
        'enable_confluence': False,   # ❌ Confluência desabilitada (nova estratégia IA)
        'min_confluence_count': 1,    # Mínimo de 1 indicador em confluência
        'min_market_score': 0.01,    # Mínimo 1% score de mercado (extremamente permissivo)
        'quality_over_quantity': True,  # Priorizar qualidade
        'min_score_difference': 0.05,  # Diferença mínima entre buy/sell scores
        'strong_signal_threshold': 0.25,  # Threshold para sinais fortes
        'medium_signal_threshold': 0.15,  # Threshold para sinais médios
        'weak_signal_threshold': 0.08     # Threshold para sinais fracos
    })
    
    # Configurações de contexto de mercado
    MARKET_CONTEXT: Dict = field(default_factory=lambda: {
        'fear_greed_weight': 0.2,
        'news_sentiment_weight': 0.15,
        'market_structure_weight': 0.3,
        'volume_profile_weight': 0.25,
        'correlation_weight': 0.1
    })
    
    # Configurações de machine learning
    ML_CONFIG: Dict = field(default_factory=lambda: {
        'models': ['xgboost', 'lightgbm', 'neural_network'],
        'ensemble_method': 'voting',
        'feature_selection': True,
        'cross_validation_folds': 5,
        'hyperparameter_tuning': True,
        'lookback_periods': [50, 100, 200],
        'prediction_horizon': 24  # horas
    })
    
    # Configurações de database
    DATABASE_CONFIG: Dict = field(default_factory=lambda: {
        'type': 'sqlite',
        'path': 'data/trading_bot.db',
        'backup_interval_hours': 6
    })
    
    # Configurações de logging
    LOGGING_CONFIG: Dict = field(default_factory=lambda: {
        'level': 'INFO',
        'max_file_size_mb': 100,
        'backup_count': 5,
        'log_trades': True,
        'log_signals': True,
        'log_market_data': False
    })
    
    # Configurações de análise de mercado com IA
    AI_MARKET_ANALYSIS: Dict = field(default_factory=lambda: {
        'sentiment_analysis': True,     # Análise de sentimento
        'volume_analysis': True,        # Análise de volume
        'volatility_analysis': True,    # Análise de volatilidade
        'correlation_analysis': True,   # Análise de correlação
        'momentum_analysis': True,      # Análise de momentum
        'pattern_recognition': True,    # Reconhecimento de padrões
        'market_regime_detection': True, # Detecção de regime de mercado
        'liquidity_analysis': True,     # Análise de liquidez
        'orderbook_analysis': False,    # Análise de order book (premium)
        'news_sentiment': False,        # Sentimento de notícias (premium)
        'social_sentiment': False,      # Sentimento social (premium)
        'macro_indicators': True,       # Indicadores macroeconômicos
        'fear_greed_index': True,       # Índice de medo e ganância
        'funding_rates': True,          # Taxas de funding
        'open_interest': True,          # Open interest
        'whale_movements': False,       # Movimentos de baleias (premium)
        'market_cap_analysis': True,    # Análise de market cap
        'dominance_analysis': True,     # Análise de dominância
        'cross_asset_correlation': True # Correlação entre ativos
    })
    
    # Configurações de modelos de IA
    AI_MODELS_CONFIG: Dict = field(default_factory=lambda: {
        'ensemble_models': True,        # Usar ensemble de modelos
        'deep_learning': True,          # Usar deep learning
        'reinforcement_learning': False, # RL (experimental)
        'transformer_models': False,    # Transformers (premium)
        'lstm_enabled': True,           # LSTM para séries temporais
        'cnn_enabled': True,            # CNN para padrões
        'attention_mechanism': False,   # Mecanismo de atenção (premium)
        'feature_importance': True,     # Importância de features
        'model_explainability': True,   # Explicabilidade do modelo
        'auto_hyperparameter': True,    # Auto-tuning de hiperparâmetros
        'online_learning': False,       # Aprendizado online (experimental)
        'federated_learning': False,    # Aprendizado federado (premium)
        'quantum_ml': False,            # ML quântico (experimental)
        'neuromorphic_computing': False # Computação neuromórfica (experimental)
    })
    
    # Configurações de notificação
    NOTIFICATION_CONFIG: Dict = field(default_factory=lambda: {
        'telegram_enabled': False,
        'telegram_token': os.getenv('TELEGRAM_TOKEN', ''),
        'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
        'email_enabled': False,
        'webhook_enabled': True,
        'webhook_url': os.getenv('WEBHOOK_URL', '')
    })
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        # Criar diretórios necessários
        os.makedirs(self.AI_MODEL_PATH, exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
    def get_all_pairs(self) -> List[str]:
        """Retorna todos os pares de trading"""
        return self.CRYPTO_PAIRS + self.FOREX_PAIRS + self.INDEX_PAIRS
    
    def is_crypto_pair(self, symbol: str) -> bool:
        """Verifica se é um par de criptomoeda"""
        return symbol in self.CRYPTO_PAIRS
    
    def is_forex_pair(self, symbol: str) -> bool:
        """Verifica se é um par de forex"""
        return symbol in self.FOREX_PAIRS
        
    def is_index_pair(self, symbol: str) -> bool:
        """Verifica se é um índice"""
        return symbol in self.INDEX_PAIRS
    
    def get_asset_type(self, symbol: str) -> str:
        """Retorna o tipo de ativo (crypto, forex, index)"""
        if self.is_crypto_pair(symbol):
            return 'crypto'
        elif self.is_forex_pair(symbol):
            return 'forex'
        elif self.is_index_pair(symbol):
            return 'index'
        else:
            return 'unknown'
    
    def get_model_path(self, model_name: str) -> str:
        """Retorna o caminho completo do modelo"""
        return os.path.join(self.AI_MODEL_PATH, f"{model_name}.pkl")