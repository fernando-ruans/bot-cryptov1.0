#!/usr/bin/env python3
"""
API de preços em tempo real otimizada para alta velocidade
Usa WebSockets e APIs públicas mais rápidas - APENAS CRYPTO
"""

import asyncio
import websockets
import json
import requests
import logging
import threading
import time
from typing import Dict, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class RealTimePriceAPI:
    """API de preços em tempo real usando WebSockets e REST APIs rápidas"""
    
    def __init__(self):
        self.prices = {}
        self.callbacks = []
        self.running = False
        self.websocket_thread = None
        self.rest_thread = None
        
        # Cache de preços com timestamp
        self.price_cache = {}
        
        # URLs das APIs mais rápidas
        self.binance_ws_url = "wss://stream.binance.com:9443/ws/"
        self.binance_rest_url = "https://api.binance.com/api/v3/ticker/price"
        
    def start(self):
        """Iniciar feeds de preços em tempo real"""
        if self.running:
            return
            
        self.running = True
        
        # Iniciar WebSocket em thread separada
        self.websocket_thread = threading.Thread(target=self._start_websocket_feed, daemon=True)
        self.websocket_thread.start()
        
        # Iniciar backup REST API em thread separada
        self.rest_thread = threading.Thread(target=self._start_rest_feed, daemon=True)
        self.rest_thread.start()
        
        logger.info("🚀 Feed de preços em tempo real iniciado")
    
    def stop(self):
        """Parar feeds de preços"""
        self.running = False
        logger.info("⏹️ Feed de preços parado")
    
    def _start_websocket_feed(self):
        """Iniciar feed WebSocket da Binance"""
        try:
            asyncio.run(self._websocket_handler())
        except Exception as e:
            logger.error(f"❌ Erro no WebSocket: {e}")
    
    async def _websocket_handler(self):
        """Handler principal do WebSocket"""
        symbols = ['btcusdt', 'ethusdt', 'adausdt', 'bnbusdt', 'solusdt', 
                  'xrpusdt', 'dotusdt', 'linkusdt', 'maticusdt', 'avaxusdt']
        
        # Criar stream para múltiplos símbolos
        streams = [f"{symbol}@ticker" for symbol in symbols]
        stream_names = '/'.join(streams)
        url = f"wss://stream.binance.com:9443/stream?streams={stream_names}"
        
        while self.running:
            try:
                async with websockets.connect(url) as websocket:
                    logger.info("✅ WebSocket conectado à Binance")
                    
                    while self.running:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            response = json.loads(message)
                            
                            # Processar dados do ticker (formato combined stream)
                            if 'data' in response:
                                data = response['data']
                                if 's' in data and 'c' in data:  # symbol e close price
                                    symbol = data['s'].upper()
                                    price = float(data['c'])
                                    
                                    # Atualizar cache
                                    self.price_cache[symbol] = {
                                        'price': price,
                                        'timestamp': datetime.now(),
                                        'source': 'websocket'
                                    }
                                    
                                    # Notificar callbacks
                                    self._notify_price_update(symbol, price)
                                    
                        except asyncio.TimeoutError:
                            # Ping para manter conexão viva
                            await websocket.ping()
                            
                        except Exception as e:
                            logger.warning(f"Erro ao processar mensagem WS: {e}")
                            break
                            
            except Exception as e:
                logger.error(f"❌ Erro na conexão WebSocket: {e}")
                if self.running:
                    await asyncio.sleep(5)  # Aguardar antes de reconectar
    
    def _start_rest_feed(self):
        """Feed REST como backup - apenas crypto"""
        while self.running:
            try:
                # Atualizar preços crypto via REST (backup)
                self._update_crypto_prices_rest()
                
                # Aguardar antes da próxima atualização
                time.sleep(1)  # 1 segundo - muito mais rápido que before
                
            except Exception as e:
                logger.error(f"❌ Erro no feed REST: {e}")
                time.sleep(5)
    
    def _update_crypto_prices_rest(self):
        """Atualizar preços crypto via REST API rápida"""
        try:
            # API da Binance - extremamente rápida
            response = requests.get(self.binance_rest_url, timeout=2)
            data = response.json()
            
            for item in data:
                symbol = item['symbol']
                price = float(item['price'])
                
                # Só atualizar se não temos preço recente do WebSocket
                if symbol not in self.price_cache or \
                   (datetime.now() - self.price_cache[symbol]['timestamp']).total_seconds() > 2:
                    
                    self.price_cache[symbol] = {
                        'price': price,
                        'timestamp': datetime.now(),
                        'source': 'rest_binance'
                    }
                    
                    self._notify_price_update(symbol, price)
                    
        except Exception as e:
            logger.debug(f"Erro REST crypto: {e}")
    
    def _notify_price_update(self, symbol: str, price: float):
        """Notificar callbacks sobre atualização de preço"""
        for callback in self.callbacks:
            try:
                callback(symbol, price)
            except Exception as e:
                logger.error(f"Erro no callback: {e}")
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obter preço atual mais recente"""
        symbol = symbol.upper()
        
        if symbol in self.price_cache:
            cache_entry = self.price_cache[symbol]
            
            # Verificar se o preço não é muito antigo (máximo 10 segundos)
            age = (datetime.now() - cache_entry['timestamp']).total_seconds()
            if age < 10:
                return cache_entry['price']
        
        # Se não temos preço recente, tentar buscar via REST imediatamente
        return self._fetch_price_immediate(symbol)
    
    def _fetch_price_immediate(self, symbol: str) -> Optional[float]:
        """Buscar preço imediatamente via REST"""
        try:
            # Para crypto
            if symbol.endswith('USDT'):
                url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                response = requests.get(url, timeout=1)
                data = response.json()
                
                if 'price' in data:
                    price = float(data['price'])
                    
                    # Atualizar cache
                    self.price_cache[symbol] = {
                        'price': price,
                        'timestamp': datetime.now(),
                        'source': 'immediate_rest'
                    }
                    
                    return price
            
            # Apenas crypto suportado
            else:
                logger.warning(f"Tipo de ativo não suportado: {symbol}")
                return None
                
        except Exception as e:
            logger.debug(f"Erro ao buscar preço imediato para {symbol}: {e}")
        
        return None
    
    def add_callback(self, callback: Callable[[str, float], None]):
        """Adicionar callback para receber atualizações de preço"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str, float], None]):
        """Remover callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_price_info(self, symbol: str) -> Optional[Dict]:
        """Obter informações detalhadas do preço"""
        symbol = symbol.upper()
        
        if symbol in self.price_cache:
            return {
                'symbol': symbol,
                'price': self.price_cache[symbol]['price'],
                'timestamp': self.price_cache[symbol]['timestamp'].isoformat(),
                'source': self.price_cache[symbol]['source'],
                'age_seconds': (datetime.now() - self.price_cache[symbol]['timestamp']).total_seconds()
            }
        
        return None

# Instância global
realtime_price_api = RealTimePriceAPI()
