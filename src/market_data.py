#!/usr/bin/env python3
"""
Gerenciador de dados de mercado para criptomoedas e forex
"""

import ccxt
import yfinance as yf
import pandas as pd
import numpy as np
import logging
import threading
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .realtime_price_api import realtime_price_api

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Estrutura de dados de mercado"""
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
class MarketDataManager:
    """Gerenciador de dados de mercado em tempo real"""
    
    def __init__(self, config):
        self.config = config
        self.exchanges = {}
        self.data_cache = {}
        self.is_running = False
        self.update_thread = None
        self.demo_mode = False
        self.use_public_apis = True  # Usar APIs públicas por padrão
        
        # Inicializar exchanges e APIs públicas
        self._initialize_exchanges()
        self._initialize_public_apis()
        
    def _initialize_exchanges(self):
        """Inicializar conexões com exchanges"""
        try:
            # Verificar se temos chaves válidas
            if self.config.BINANCE_API_KEY and self.config.BINANCE_API_KEY != 'demo_key':
                # Binance para criptomoedas
                self.exchanges['binance'] = ccxt.binance({
                    'apiKey': self.config.BINANCE_API_KEY,
                    'secret': self.config.BINANCE_SECRET_KEY,
                    'sandbox': False,
                    'enableRateLimit': True,
                })
                logger.info("Exchanges privadas inicializadas com sucesso")
                self.use_public_apis = False
            else:
                logger.info("Usando APIs públicas para dados de mercado")
                self.use_public_apis = True
        except Exception as e:
            logger.error(f"Erro ao inicializar exchanges: {e}")
            logger.info("Fallback para APIs públicas")
            self.use_public_apis = True
    
    def _initialize_public_apis(self):
        """Inicializar APIs públicas sem autenticação"""
        try:
            # Binance público (sem chaves)
            self.exchanges['binance_public'] = ccxt.binance({
                'enableRateLimit': True,
                'sandbox': False,
            })
              # Kraken público
            self.exchanges['kraken'] = ccxt.kraken({
                'enableRateLimit': True,
                'sandbox': False,
            })
            
            logger.info("APIs públicas inicializadas: Binance, Kraken")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar APIs públicas: {e}")
            logger.warning("Fallback para modo demonstração")
            self.demo_mode = True
    
    def start_data_feed(self):
        """Iniciar feed de dados em tempo real"""
        if self.is_running:
            return
            
        # Iniciar API de preços em tempo real primeiro
        realtime_price_api.start()
        logger.info("🚀 API de preços em tempo real iniciada")
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._data_update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        logger.info("Feed de dados iniciado")
    
    def stop_data_feed(self):
        """Parar feed de dados"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()
        
        # Parar API de preços em tempo real
        realtime_price_api.stop()
        
        logger.info("Feed de dados parado")
    
    def _data_update_loop(self):
        """Loop principal de atualização de dados"""
        while self.is_running:
            try:
                # Atualizar dados de criptomoedas
                for symbol in self.config.CRYPTO_PAIRS:
                    for timeframe in self.config.TIMEFRAMES:
                        self._update_crypto_data(symbol, timeframe)
                  # Atualizar dados de forex
                for symbol in self.config.FOREX_PAIRS:
                    self._update_forex_data(symbol)
                
                time.sleep(60)  # Atualizar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro no loop de atualização: {e}")
                time.sleep(30)
    
    def _update_crypto_data(self, symbol: str, timeframe: str):
        """Atualizar dados de criptomoeda usando APIs públicas"""
        try:
            # Priorizar APIs públicas sobre dados simulados
            if not self.demo_mode and self.use_public_apis:
                # Tentar Binance público primeiro
                df = self._fetch_from_binance_public(symbol, timeframe)
            elif not self.demo_mode and not self.use_public_apis:
                # Usar API privada com chaves
                exchange = self.exchanges['binance']
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=500)
                
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
            else:
                # Fallback para dados simulados
                df = self._generate_demo_data(symbol, timeframe)
            
            # Armazenar no cache
            cache_key = f"{symbol}_{timeframe}"
            self.data_cache[cache_key] = df
            
        except Exception as e:
            logger.error(f"Erro ao atualizar dados crypto {symbol} {timeframe}: {e}")
            # Fallback para dados simulados
            try:
                df = self._generate_demo_data(symbol, timeframe)
                cache_key = f"{symbol}_{timeframe}"
                self.data_cache[cache_key] = df
            except Exception as e2:
                logger.error(f"Erro ao gerar dados simulados: {e2}")
    
    def _fetch_from_binance_public(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Buscar dados da Binance pública (método simplificado)"""
        try:
            if 'binance_public' not in self.exchanges:
                raise ValueError("Binance público não inicializado")
                
            exchange = self.exchanges['binance_public']
            logger.info(f"Buscando {symbol} da Binance pública")
            
            # Buscar dados
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=500)
            
            if not ohlcv or len(ohlcv) == 0:
                raise ValueError("Nenhum dado retornado")
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"✓ Dados reais da Binance obtidos: {len(df)} registros")
            logger.info(f"✓ Último preço: ${df['close'].iloc[-1]:.2f}")
            
            return df
            
        except Exception as e:
            logger.warning(f"Binance pública falhou: {e}")
            # Tentar CoinGecko como backup
            return self._fetch_from_coingecko(symbol, timeframe)
    
    def _fetch_from_public_apis(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Buscar dados de APIs públicas"""
        
        # Lista de exchanges públicas para tentar
        public_exchanges = ['binance_public', 'kraken']
        
        for exchange_name in public_exchanges:
            try:
                if exchange_name not in self.exchanges:
                    continue
                    
                exchange = self.exchanges[exchange_name]
                
                # Ajustar símbolo para cada exchange
                adjusted_symbol = self._adjust_symbol_for_exchange(symbol, exchange_name)
                if not adjusted_symbol:
                    continue
                
                logger.info(f"Buscando {adjusted_symbol} de {exchange_name}")
                
                # Buscar dados
                ohlcv = exchange.fetch_ohlcv(adjusted_symbol, timeframe, limit=500)
                
                if ohlcv and len(ohlcv) > 0:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    
                    logger.info(f"✓ Dados obtidos de {exchange_name}: {len(df)} registros")
                    return df
                    
            except Exception as e:
                logger.warning(f"Falha ao buscar {symbol} de {exchange_name}: {e}")
                continue
        
        # Se todas as APIs falharam, usar CoinGecko como backup
        try:
            return self._fetch_from_coingecko(symbol, timeframe)
        except Exception as e:
            logger.error(f"CoinGecko também falhou: {e}")
            
        # Último recurso: dados simulados
        logger.warning(f"Usando dados simulados para {symbol}")
        return self._generate_demo_data(symbol, timeframe)
    
    def _adjust_symbol_for_exchange(self, symbol: str, exchange_name: str) -> Optional[str]:
        """Ajustar formato do símbolo para cada exchange"""
        
        if exchange_name == 'binance_public':
            return symbol  # BTCUSDT
            
        elif exchange_name == 'kraken':
            # BTCUSDT -> BTC/USD
            if symbol.endswith('USDT'):
                base = symbol[:-4]
                # Kraken usa nomes específicos
                kraken_map = {
                    'BTC': 'XBT',
                    'ETH': 'ETH',
                    'ADA': 'ADA',
                    'DOT': 'DOT',
                    'LINK': 'LINK'
                }
                kraken_base = kraken_map.get(base, base)
                return f"{kraken_base}/USD"
                
        return None
    
    def _fetch_from_coingecko(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Buscar dados da API pública do CoinGecko"""
        
        # Mapear símbolos para IDs do CoinGecko
        coingecko_map = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'ADAUSDT': 'cardano',
            'DOTUSDT': 'polkadot',
            'LINKUSDT': 'chainlink',
            'BNBUSDT': 'binancecoin',
            'XRPUSDT': 'ripple',
            'LTCUSDT': 'litecoin',
            'BCHUSDT': 'bitcoin-cash',
            'EOSUSDT': 'eos'
        }
        
        coin_id = coingecko_map.get(symbol)
        if not coin_id:
            raise ValueError(f"Símbolo {symbol} não suportado pelo CoinGecko")
        
        # Determinar dias baseado no timeframe
        days_map = {
            '1m': 1,
            '5m': 1, 
            '15m': 1,
            '30m': 1,
            '1h': 7,
            '4h': 30,
            '1d': 365
        }
        
        days = days_map.get(timeframe, 7)
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
        params = {
            'vs_currency': 'usd',
            'days': days
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            raise ValueError("Nenhum dado retornado pelo CoinGecko")
        
        # Converter para DataFrame
        df_data = []
        for item in data:
            timestamp = pd.to_datetime(item[0], unit='ms')
            df_data.append({
                'timestamp': timestamp,
                'open': item[1],
                'high': item[2], 
                'low': item[3],
                'close': item[4],
                'volume': 1000000  # CoinGecko OHLC não tem volume, usar placeholder
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('timestamp', inplace=True)
        
        logger.info(f"✓ Dados CoinGecko obtidos: {len(df)} registros")
        return df
    
    def _update_forex_data(self, symbol: str):
        """Atualizar dados de forex"""
        try:
            # Converter formato (EURUSD -> EUR=X)
            yahoo_symbol = f"{symbol[:3]}{symbol[3:]}=X"
            
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period="1d", interval="1h")
            
            if not hist.empty:                # Converter para formato padrão
                df = hist[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                df.columns = ['open', 'high', 'low', 'close', 'volume']
                
                cache_key = f"{symbol}_1h"
                self.data_cache[cache_key] = df
                
        except Exception as e:
            logger.error(f"Erro ao atualizar dados forex {symbol}: {e}")
    
    def _generate_demo_data(self, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        """Gerar dados simulados para demonstração"""
        try:
            # Definir preços base para diferentes símbolos
            base_prices = {
                'BTCUSDT': 45000,
                'ETHUSDT': 3000,
                'ADAUSDT': 0.5,
                'DOTUSDT': 25,
                'LINKUSDT': 15,
                'BNBUSDT': 300,
                'XRPUSDT': 0.6,
                'LTCUSDT': 150,
                'BCHUSDT': 400,
                'EOSUSDT': 4
            }
            
            base_price = base_prices.get(symbol, 100)
            
            # Gerar timestamps
            timeframe_minutes = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '4h': 240, '1d': 1440
            }
            
            minutes = timeframe_minutes.get(timeframe, 60)
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=minutes * limit)
            
            timestamps = pd.date_range(start=start_time, end=end_time, freq=f'{minutes}min')[:limit]
            
            # Gerar dados OHLCV simulados
            np.random.seed(hash(symbol) % 2**32)  # Seed baseado no símbolo para consistência
            
            data = []
            current_price = base_price
            
            for i, timestamp in enumerate(timestamps):
                # Simular movimento de preço com tendência e volatilidade
                volatility = 0.02  # 2% de volatilidade
                trend = np.sin(i / 50) * 0.001  # Tendência suave
                
                price_change = np.random.normal(trend, volatility)
                current_price *= (1 + price_change)
                
                # Gerar OHLC baseado no preço atual
                high_low_range = current_price * 0.01  # 1% de range
                
                open_price = current_price + np.random.uniform(-high_low_range/2, high_low_range/2)
                close_price = current_price + np.random.uniform(-high_low_range/2, high_low_range/2)
                high_price = max(open_price, close_price) + np.random.uniform(0, high_low_range/2)
                low_price = min(open_price, close_price) - np.random.uniform(0, high_low_range/2)
                
                volume = np.random.uniform(1000, 10000)
                
                data.append({
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })
                
                current_price = close_price
            
            df = pd.DataFrame(data, index=timestamps)
            return df
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados demo para {symbol}: {e}")
            return pd.DataFrame()
    
    def get_historical_data(self, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        """Obter dados históricos"""
        cache_key = f"{symbol}_{timeframe}"
        
        if cache_key in self.data_cache:
            df = self.data_cache[cache_key].copy()
            return df.tail(limit) if len(df) > limit else df
        
        # Se não estiver no cache, buscar dados
        if self.config.is_crypto_pair(symbol):
            self._update_crypto_data(symbol, timeframe)
        else:
            self._update_forex_data(symbol)
        
        return self.data_cache.get(cache_key, pd.DataFrame())
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obter preço atual usando API otimizada"""
        try:
            # 1. Tentar API em tempo real primeiro (muito mais rápida)
            realtime_price = realtime_price_api.get_current_price(symbol)
            if realtime_price is not None:
                logger.debug(f"💰 Preço tempo real obtido: {symbol} = ${realtime_price:.6f}")
                return realtime_price
            
            # 2. Fallback para método original se a API rápida falhar
            logger.debug(f"⚠️ Fallback para método tradicional: {symbol}")
            
            if self.demo_mode or 'binance' not in self.exchanges:
                # Usar dados do cache ou gerar novos
                cache_key = f"{symbol}_1h"
                if cache_key not in self.data_cache:
                    self._update_crypto_data(symbol, '1h')
                
                if cache_key in self.data_cache:
                    df = self.data_cache[cache_key]
                    if not df.empty:
                        return df['close'].iloc[-1]
            else:
                if self.config.is_crypto_pair(symbol):
                    exchange = self.exchanges['binance']
                    ticker = exchange.fetch_ticker(symbol)
                    return ticker['last']
                else:
                    # Para forex, usar último preço do cache
                    cache_key = f"{symbol}_1h"
                    if cache_key in self.data_cache:
                        df = self.data_cache[cache_key]
                        if not df.empty:
                            return df['close'].iloc[-1]
        except Exception as e:
            logger.error(f"Erro ao obter preço atual {symbol}: {e}")
            # Fallback para dados simulados
            try:
                cache_key = f"{symbol}_1h"
                if cache_key not in self.data_cache:
                    df = self._generate_demo_data(symbol, '1h', 100)
                    self.data_cache[cache_key] = df
                
                if cache_key in self.data_cache:
                    df = self.data_cache[cache_key]
                    if not df.empty:
                        return df['close'].iloc[-1]
            except Exception as e2:
                logger.error(f"Erro ao obter preço simulado: {e2}")
        
        return None
    
    def get_market_info(self, symbol: str) -> Dict:
        """Obter informações do mercado"""
        try:
            current_price = self.get_current_price(symbol)
            df = self.get_historical_data(symbol, '1h', 24)
            
            if df.empty or current_price is None:
                return {}
            
            # Calcular estatísticas
            price_change_24h = ((current_price - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
            volume_24h = df['volume'].sum()
            high_24h = df['high'].max()
            low_24h = df['low'].min()
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'volume_24h': volume_24h,
                'high_24h': high_24h,
                'low_24h': low_24h,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter info do mercado {symbol}: {e}")
            return {}
    
    def calculate_volatility(self, symbol: str, timeframe: str, periods: int = 20) -> float:
        """Calcular volatilidade"""
        try:
            df = self.get_historical_data(symbol, timeframe, periods + 10)
            if len(df) < periods:
                return 0.0
            
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(periods)
            
            return volatility
            
        except Exception as e:
            logger.error(f"Erro ao calcular volatilidade {symbol}: {e}")
            return 0.0
    
    def get_volume_profile(self, symbol: str, timeframe: str, periods: int = 100) -> Dict:
        """Calcular perfil de volume"""
        try:
            df = self.get_historical_data(symbol, timeframe, periods)
            if df.empty:
                return {}
            
            # Calcular VWAP
            df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
            
            # Volume médio
            avg_volume = df['volume'].mean()
            current_volume = df['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # Identificar níveis de alto volume
            volume_threshold = df['volume'].quantile(0.8)
            high_volume_levels = df[df['volume'] > volume_threshold]['close'].tolist()
            
            return {
                'vwap': df['vwap'].iloc[-1],
                'avg_volume': avg_volume,
                'current_volume': current_volume,
                'volume_ratio': volume_ratio,
                'high_volume_levels': high_volume_levels[-10:]  # Últimos 10 níveis
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular perfil de volume {symbol}: {e}")
            return {}
    
    def detect_market_structure(self, symbol: str, timeframe: str) -> Dict:
        """Detectar estrutura de mercado"""
        try:
            df = self.get_historical_data(symbol, timeframe, 100)
            if len(df) < 50:
                return {}
            
            # Identificar tendência usando médias móveis
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            
            current_price = df['close'].iloc[-1]
            sma_20 = df['sma_20'].iloc[-1]
            sma_50 = df['sma_50'].iloc[-1]
            
            # Determinar tendência
            if current_price > sma_20 > sma_50:
                trend = 'bullish'
            elif current_price < sma_20 < sma_50:
                trend = 'bearish'
            else:
                trend = 'sideways'
            
            # Identificar suporte e resistência
            highs = df['high'].rolling(10, center=True).max()
            lows = df['low'].rolling(10, center=True).min()
            
            resistance_levels = df[df['high'] == highs]['high'].drop_duplicates().tail(5).tolist()
            support_levels = df[df['low'] == lows]['low'].drop_duplicates().tail(5).tolist()
            
            return {
                'trend': trend,
                'current_price': current_price,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'resistance_levels': resistance_levels,
                'support_levels': support_levels
            }
            
        except Exception as e:
            logger.error(f"Erro ao detectar estrutura de mercado {symbol}: {e}")
            return {}
    
    def get_market_correlation(self, symbol1: str, symbol2: str, timeframe: str = '1h', periods: int = 100) -> float:
        """Calcular correlação entre dois ativos"""
        try:
            df1 = self.get_historical_data(symbol1, timeframe, periods)
            df2 = self.get_historical_data(symbol2, timeframe, periods)
            
            if df1.empty or df2.empty:
                return 0.0
            
            # Alinhar timestamps
            df1 = df1.reindex(df2.index, method='nearest')
            
            # Calcular retornos
            returns1 = df1['close'].pct_change().dropna()
            returns2 = df2['close'].pct_change().dropna()
            
            # Calcular correlação
            correlation = returns1.corr(returns2)
            
            return correlation if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            logger.error(f"Erro ao calcular correlação {symbol1}-{symbol2}: {e}")
            return 0.0