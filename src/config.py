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
    
    # Pares de trading
    CRYPTO_PAIRS: List[str] = field(default_factory=lambda: [
        'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT',
        'BNBUSDT', 'XRPUSDT', 'LTCUSDT', 'BCHUSDT', 'EOSUSDT'
    ])
    
    FOREX_PAIRS: List[str] = field(default_factory=lambda: [
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD',
        'USDCAD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'EURGBP'
    ])
    
    # Configurações de IA
    AI_MODEL_PATH: str = 'models/'
    RETRAIN_INTERVAL_HOURS: int = 24
    MIN_TRAINING_SAMPLES: int = 1000
    
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
    
    # Configurações de risco
    RISK_MANAGEMENT: Dict = field(default_factory=lambda: {
        'max_risk_per_trade': 0.02,  # 2% por trade
        'max_daily_loss': 0.05,      # 5% perda diária máxima
        'max_open_positions': 5,
        'stop_loss_pct': 0.02,       # 2% stop loss
        'take_profit_pct': 0.04,     # 4% take profit
        'trailing_stop_pct': 0.01    # 1% trailing stop
    })
    
    # Configurações de sinal
    SIGNAL_CONFIG: Dict = field(default_factory=lambda: {
        'min_confidence': 0.05,      # 🎯 Confiança mínima 5% (padrão inicial)
        'max_confidence': 0.90,      # 📊 Confiança máxima 90% para controle do slider
        'signal_cooldown_minutes': 1,  # ⏱️ Cooldown de 1 minuto entre sinais
        'max_signals_per_hour': 50,   # 📈 Máximo 50 sinais por hora
        'enable_confluence': True,   # ✅ Confluência habilitada para melhor qualidade
        'min_confluence_count': 2     # Mínimo 2 confirmações para sinal
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
        return self.CRYPTO_PAIRS + self.FOREX_PAIRS
    
    def is_crypto_pair(self, symbol: str) -> bool:
        """Verifica se é um par de criptomoeda"""
        return symbol in self.CRYPTO_PAIRS
    
    def is_forex_pair(self, symbol: str) -> bool:
        """Verifica se é um par de forex"""
        return symbol in self.FOREX_PAIRS
    
    def get_model_path(self, model_name: str) -> str:
        """Retorna o caminho completo do modelo"""
        return os.path.join(self.AI_MODEL_PATH, f"{model_name}.pkl")