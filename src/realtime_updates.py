#!/usr/bin/env python3
"""
Sistema de WebSocket para atualizações em tempo real
Implementa notificações push para trades, preços e sinais
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask_socketio import SocketIO, emit, join_room, leave_room

logger = logging.getLogger(__name__)

class RealTimeUpdates:
    """Sistema de atualizações em tempo real via WebSocket"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.connected_clients = set()
        self.subscribed_symbols = {}  # client_id -> [symbols]
        self.price_cache = {}  # symbol -> price data
        self.last_updates = {}  # symbol -> timestamp
        
        logger.info("🔗 Sistema de WebSocket inicializado")
        
    def setup_events(self):
        """Configurar eventos de WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Cliente conectado"""
            client_id = self.socketio.request.sid
            self.connected_clients.add(client_id)
            logger.info(f"🔌 Cliente conectado: {client_id}")
            
            # Enviar status inicial
            emit('connection_status', {
                'connected': True,
                'timestamp': datetime.now().isoformat(),
                'client_id': client_id
            })
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Cliente desconectado"""
            client_id = self.socketio.request.sid
            self.connected_clients.discard(client_id)
            
            # Limpar subscrições
            if client_id in self.subscribed_symbols:
                del self.subscribed_symbols[client_id]
                
            logger.info(f"🔌 Cliente desconectado: {client_id}")
            
        @self.socketio.on('subscribe_symbol')
        def handle_subscribe_symbol(data):
            """Subscrever atualizações de um símbolo"""
            client_id = self.socketio.request.sid
            symbol = data.get('symbol', 'BTCUSDT')
            
            if client_id not in self.subscribed_symbols:
                self.subscribed_symbols[client_id] = []
                
            if symbol not in self.subscribed_symbols[client_id]:
                self.subscribed_symbols[client_id].append(symbol)
                join_room(f"symbol_{symbol}")
                
                logger.info(f"📊 Cliente {client_id} subscrito em {symbol}")
                
                # Enviar último preço se disponível
                if symbol in self.price_cache:
                    emit('price_update', {
                        'symbol': symbol,
                        'data': self.price_cache[symbol]
                    })
                    
        @self.socketio.on('unsubscribe_symbol')
        def handle_unsubscribe_symbol(data):
            """Cancelar subscrição de um símbolo"""
            client_id = self.socketio.request.sid
            symbol = data.get('symbol')
            
            if client_id in self.subscribed_symbols:
                if symbol in self.subscribed_symbols[client_id]:
                    self.subscribed_symbols[client_id].remove(symbol)
                    leave_room(f"symbol_{symbol}")
                    logger.info(f"📊 Cliente {client_id} cancelou subscrição de {symbol}")
    
    def broadcast_price_update(self, symbol: str, price_data: Dict[str, Any]):
        """Transmitir atualização de preço para clientes subscritos"""
        try:
            # Atualizar cache
            self.price_cache[symbol] = {
                'price': price_data.get('price', 0),
                'change_24h': price_data.get('change_24h', 0),
                'change_percent': price_data.get('change_percent', 0),
                'volume': price_data.get('volume', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Transmitir para clientes subscritos
            self.socketio.emit('price_update', {
                'symbol': symbol,
                'data': self.price_cache[symbol]
            }, room=f"symbol_{symbol}")
            
            # Log apenas a cada 30 segundos para evitar spam
            now = datetime.now()
            last_log = self.last_updates.get(f"price_{symbol}")
            
            if not last_log or (now - last_log).total_seconds() > 30:
                logger.debug(f"📈 Preço atualizado: {symbol} = ${price_data.get('price', 0):.6f}")
                self.last_updates[f"price_{symbol}"] = now
                
        except Exception as e:
            logger.error(f"❌ Erro ao transmitir preço: {e}")
    
    def broadcast_new_signal(self, signal_data: Dict[str, Any]):
        """Transmitir novo sinal para todos os clientes"""
        try:
            signal_info = {
                'symbol': signal_data.get('symbol'),
                'signal_type': signal_data.get('signal_type'),
                'entry_price': signal_data.get('entry_price'),
                'stop_loss': signal_data.get('stop_loss'),
                'take_profit': signal_data.get('take_profit'),
                'confidence': signal_data.get('confidence'),
                'timestamp': datetime.now().isoformat()
            }
            
            self.socketio.emit('new_signal', signal_info)
            logger.info(f"📡 Sinal transmitido: {signal_data.get('signal_type')} {signal_data.get('symbol')}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao transmitir sinal: {e}")
    
    def broadcast_trade_update(self, trade_data: Dict[str, Any]):
        """Transmitir atualização de trade"""
        try:
            trade_info = {
                'id': trade_data.get('id'),
                'symbol': trade_data.get('symbol'),
                'trade_type': trade_data.get('trade_type'),
                'entry_price': trade_data.get('entry_price'),
                'current_price': trade_data.get('current_price'),
                'pnl': trade_data.get('pnl', 0),
                'pnl_percent': trade_data.get('pnl_percent', 0),
                'status': trade_data.get('status'),
                'timestamp': datetime.now().isoformat()
            }
            
            self.socketio.emit('trade_update', trade_info)
            
            # Log apenas mudanças significativas
            if trade_data.get('status') in ['closed', 'profit', 'loss']:
                logger.info(f"💰 Trade atualizado: {trade_data.get('symbol')} - {trade_data.get('status')}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao transmitir trade: {e}")
    
    def broadcast_portfolio_update(self, portfolio_data: Dict[str, Any]):
        """Transmitir atualização do portfolio"""
        try:
            portfolio_info = {
                'total_pnl': portfolio_data.get('total_pnl', 0),
                'total_trades': portfolio_data.get('total_trades', 0),
                'win_rate': portfolio_data.get('win_rate', 0),
                'active_trades': portfolio_data.get('active_trades', 0),
                'balance': portfolio_data.get('balance', 10000),
                'timestamp': datetime.now().isoformat()
            }
            
            self.socketio.emit('portfolio_update', portfolio_info)
            logger.debug(f"📊 Portfolio atualizado: {portfolio_data.get('total_trades')} trades")
            
        except Exception as e:
            logger.error(f"❌ Erro ao transmitir portfolio: {e}")
    
    def broadcast_trade_closed(self, trade_data: Dict[str, Any]):
        """Transmitir fechamento de trade"""
        try:
            close_info = {
                'id': trade_data.get('id'),
                'symbol': trade_data.get('symbol'),
                'exit_reason': trade_data.get('exit_reason'),
                'pnl': trade_data.get('pnl', 0),
                'pnl_percent': trade_data.get('pnl_percent', 0),
                'exit_price': trade_data.get('exit_price'),
                'duration': trade_data.get('duration_minutes', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            self.socketio.emit('trade_closed', close_info)
            
            # Determinar ícone baseado no resultado
            icon = "🟢" if trade_data.get('pnl', 0) >= 0 else "🔴"
            result = "LUCRO" if trade_data.get('pnl', 0) >= 0 else "PERDA"
            
            logger.info(f"{icon} Trade fechado: {trade_data.get('symbol')} - {result} ({trade_data.get('pnl_percent', 0):.2f}%)")
            
        except Exception as e:
            logger.error(f"❌ Erro ao transmitir fechamento: {e}")
    
    def get_client_count(self) -> int:
        """Número de clientes conectados"""
        return len(self.connected_clients)
    
    def get_subscriptions(self) -> Dict[str, list]:
        """Subscrições ativas por cliente"""
        return dict(self.subscribed_symbols)
    
    # Métodos de compatibilidade
    def notify_new_signal(self, signal_data: Dict[str, Any]):
        """Alias para broadcast_new_signal"""
        self.broadcast_new_signal(signal_data)
    
    def notify_trade_opened(self, trade_data: Dict[str, Any]):
        """Notificar trade aberto"""
        self.broadcast_trade_update(trade_data)
    
    def notify_trade_closed(self, trade_data: Dict[str, Any]):
        """Notificar trade fechado"""
        self.broadcast_trade_closed(trade_data)
    
    def notify_portfolio_update(self, portfolio_data: Dict[str, Any]):
        """Alias para broadcast_portfolio_update"""
        self.broadcast_portfolio_update(portfolio_data)
    
    def start_price_updates(self, symbols: list):
        """Iniciar atualizações de preços para símbolos"""
        self.is_active = True
        self.subscribed_symbols = {symbol: True for symbol in symbols}
        logger.info(f"🔄 Atualizações de preços iniciadas para: {symbols}")
    
    def stop_price_updates(self):
        """Parar atualizações de preços"""
        self.is_active = False
        self.subscribed_symbols = {}
        logger.info("⏹️ Atualizações de preços paradas")
    
    @property
    def is_active(self):
        """Status se está ativo"""
        return getattr(self, '_is_active', False)
    
    @is_active.setter
    def is_active(self, value):
        """Definir status ativo"""
        self._is_active = value

# Instância global
realtime_updates = None

def initialize_realtime_updates(socketio: SocketIO) -> RealTimeUpdates:
    """Inicializar sistema de atualizações em tempo real"""
    global realtime_updates
    realtime_updates = RealTimeUpdates(socketio)
    realtime_updates.setup_events()
    return realtime_updates

def get_realtime_updates() -> Optional[RealTimeUpdates]:
    """Obter instância do sistema de atualizações"""
    return realtime_updates
