"""
Paper Trading Manager - Sistema de Trading Virtual
Gerencia trades virtuais com P&L automático, stop loss e take profit
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class PaperTrade:
    """Representa um trade de paper trading"""
    id: str
    symbol: str
    trade_type: str  # 'buy' ou 'sell'
    entry_price: float
    quantity: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    current_price: Optional[float] = None
    status: str = 'open'  # 'open', 'closed'
    timestamp: datetime = None
    exit_timestamp: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None  # 'manual', 'stop_loss', 'take_profit'
    signal_confidence: Optional[float] = None
    timeframe: Optional[str] = None
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    pnl_percent: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.current_price is None:
            self.current_price = self.entry_price
    
    def update_current_price(self, new_price: float) -> bool:
        """
        Atualiza o preço atual e calcula P&L
        Retorna True se SL/TP foi atingido
        """
        self.current_price = new_price
        
        if self.status != 'open':
            return False
        
        # Calcular P&L não realizado
        if self.trade_type.lower() == 'buy':
            self.unrealized_pnl = (new_price - self.entry_price) * self.quantity
            price_change_pct = (new_price - self.entry_price) / self.entry_price
        else:  # sell
            self.unrealized_pnl = (self.entry_price - new_price) * self.quantity
            price_change_pct = (self.entry_price - new_price) / self.entry_price
        
        self.pnl_percent = price_change_pct * 100
        
        # Verificar Stop Loss
        if self.stop_loss and self._check_stop_loss(new_price):
            self._close_trade(new_price, 'stop_loss')
            return True
        
        # Verificar Take Profit
        if self.take_profit and self._check_take_profit(new_price):
            self._close_trade(new_price, 'take_profit')
            return True
        
        return False
    
    def _check_stop_loss(self, current_price: float) -> bool:
        """Verifica se stop loss foi atingido"""
        if self.trade_type.lower() == 'buy':
            return current_price <= self.stop_loss
        else:  # sell
            return current_price >= self.stop_loss
    
    def _check_take_profit(self, current_price: float) -> bool:
        """Verifica se take profit foi atingido"""
        if self.trade_type.lower() == 'buy':
            return current_price >= self.take_profit
        else:  # sell
            return current_price <= self.take_profit
    
    def _close_trade(self, exit_price: float, reason: str):
        """Fecha o trade com motivo específico"""
        self.status = 'closed'
        self.exit_price = exit_price
        self.exit_timestamp = datetime.now()
        self.exit_reason = reason
        self.realized_pnl = self.unrealized_pnl
        
        logger.info(f"🔒 Trade {self.id[:8]} fechado: {reason} @ {exit_price:.2f} (P&L: ${self.realized_pnl:.2f})")
    
    def close_manually(self, exit_price: float = None):
        """Fecha o trade manualmente"""
        exit_price = exit_price or self.current_price
        self._close_trade(exit_price, 'manual')
    
    def to_dict(self) -> Dict:
        """Converte para dicionário com métricas detalhadas"""
        duration = None
        duration_minutes = 0
        
        if self.exit_timestamp and self.timestamp:
            duration_delta = self.exit_timestamp - self.timestamp
            duration = str(duration_delta)
            duration_minutes = int(duration_delta.total_seconds() / 60)
        
        # Calcular distâncias de SL e TP
        sl_distance_pct = None
        tp_distance_pct = None
        risk_reward_ratio = None
        
        if self.stop_loss:
            sl_distance_pct = abs(self.stop_loss - self.entry_price) / self.entry_price * 100
        
        if self.take_profit:
            tp_distance_pct = abs(self.take_profit - self.entry_price) / self.entry_price * 100
        
        if sl_distance_pct and tp_distance_pct:
            risk_reward_ratio = tp_distance_pct / sl_distance_pct
        
        # Calcular excursões máximas (simulado)
        max_favorable_excursion = self.realized_pnl if self.realized_pnl > 0 else 0
        max_adverse_excursion = abs(self.realized_pnl) if self.realized_pnl < 0 else 0
        
        return {
            'id': self.id,
            'symbol': self.symbol,
            'trade_type': self.trade_type,
            'side': self.trade_type.upper(),  # Compatibilidade
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'entry_time': self.timestamp.isoformat() if self.timestamp else None,
            'entry_timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'exit_timestamp': self.exit_timestamp.isoformat() if self.exit_timestamp else None,
            'exit_time': self.exit_timestamp.isoformat() if self.exit_timestamp else None,
            'exit_reason': self.exit_reason,
            'signal_confidence': self.signal_confidence,
            'timeframe': self.timeframe,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'pnl': self.realized_pnl if self.status == 'closed' else self.unrealized_pnl,            'pnl_percent': self.pnl_percent,
            'pnl_percentage': self.pnl_percent,  # Compatibilidade
            'duration': duration,
            'duration_minutes': duration_minutes,  # Campo necessário para WebSocket
            'sl_distance_pct': sl_distance_pct,
            'tp_distance_pct': tp_distance_pct,
            'risk_reward_ratio': risk_reward_ratio,
            'max_favorable_excursion': max_favorable_excursion,
            'max_adverse_excursion': max_adverse_excursion
        }


class PaperTradingManager:
    """Gerenciador de Paper Trading"""
    
    def __init__(self, market_data_manager, realtime_updates=None, initial_balance: float = 10000.0):
        self.market_data = market_data_manager
        self.realtime_updates = realtime_updates
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        # Armazenamento de trades
        self.active_trades: Dict[str, PaperTrade] = {}
        self.trade_history: List[PaperTrade] = []
        
        # Thread de monitoramento        self._monitor_thread = None        self._monitor_running = False
        
        logger.info(f"📊 Paper Trading Manager inicializado com ${initial_balance:.2f}")
    
    def confirm_signal(self, signal_data: Dict, amount: float = 1000.0) -> Optional[PaperTrade]:
        """Confirma um sinal e cria um trade"""
        try:
            # Extrair dados do sinal
            symbol = signal_data.get('symbol', 'BTCUSDT')
            signal_type = signal_data.get('signal_type', 'buy')
            entry_price = float(signal_data.get('entry_price', 0))
            stop_loss = signal_data.get('stop_loss')
            take_profit = signal_data.get('take_profit')
            confidence = signal_data.get('confidence')
            timeframe = signal_data.get('timeframe', '1h')
            
            if entry_price <= 0:
                logger.error("❌ Preço de entrada inválido")
                return None
            
            # Calcular quantidade baseada no valor
            # ⭐ GARANTIR QUE AMOUNT E ENTRY_PRICE SEJAM VÁLIDOS
            if amount <= 0:
                logger.error(f"❌ Amount inválido: {amount}")
                return None
                
            quantity = amount / entry_price
              # ⭐ VALIDAÇÃO ADICIONAL DA QUANTIDADE
            if quantity <= 0:
                logger.error(f"❌ Quantidade calculada inválida: {quantity} (amount: {amount}, entry_price: {entry_price})")
                return None
            
            logger.info(f"💰 Quantidade calculada: {quantity:.8f} (${amount} / ${entry_price})")
            
            # Criar trade
            trade = PaperTrade(
                id=str(uuid.uuid4()),
                symbol=symbol,
                trade_type=signal_type.lower(),
                entry_price=entry_price,
                quantity=quantity,
                stop_loss=float(stop_loss) if stop_loss else None,
                take_profit=float(take_profit) if take_profit else None,
                signal_confidence=float(confidence) if confidence else None,
                timeframe=timeframe
            )
            
            # Adicionar aos trades ativos
            self.active_trades[trade.id] = trade
            
            # Log detalhado
            logger.info(f"OK Trade criado: {trade.id[:8]}")
            logger.info(f"   📊 {symbol} {signal_type.upper()} @ ${entry_price:.2f}")
            logger.info(f"   💰 Quantidade: {quantity:.6f}")
            logger.info(f"   🛑 Stop Loss: ${stop_loss:.2f}" if stop_loss else "   🛑 Stop Loss: N/A")
            logger.info(f"   🎯 Take Profit: ${take_profit:.2f}" if take_profit else "   🎯 Take Profit: N/A")
            logger.info(f"   📈 Confiança: {confidence:.2%}" if confidence else "   📈 Confiança: N/A")
            
            # Notificação em tempo real
            if self.realtime_updates:
                self.realtime_updates.notify_trade_opened(trade.to_dict())
            
            return trade
            
        except Exception as e:
            logger.error(f"❌ Erro ao confirmar sinal: {e}")
            return None
    
    def update_prices(self):
        """Atualiza preços de todos os trades ativos usando API de tempo real"""
        if not self.active_trades:
            return
        
        # Importar API de tempo real
        from .realtime_price_api import realtime_price_api
        
        trades_to_close = []
        
        for trade_id, trade in self.active_trades.items():
            try:
                # Usar API de tempo real primeiro (muito mais rápido)
                current_price = realtime_price_api.get_current_price(trade.symbol)
                
                # Se falhou, usar fallback tradicional
                if current_price is None:
                    current_price = self.market_data.get_current_price(trade.symbol)
                
                if current_price:
                    # Atualizar preço e verificar SL/TP
                    should_close = trade.update_current_price(current_price)
                    if should_close:
                        trades_to_close.append(trade_id)
                        
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar preço do trade {trade_id[:8]}: {e}")
        
        # Processar trades fechados
        for trade_id in trades_to_close:
            self._process_closed_trade(self.active_trades[trade_id])
            del self.active_trades[trade_id]
    
    def _process_closed_trade(self, trade: PaperTrade):
        """Processa um trade fechado com notificações aprimoradas"""
        # Atualizar balanço
        self.current_balance += trade.realized_pnl
        
        # Mover para histórico
        self.trade_history.append(trade)
        
        # Emojis e mensagens baseadas no resultado
        result_emoji = "🎯" if trade.exit_reason == 'take_profit' else "🛑" if trade.exit_reason == 'stop_loss' else "🔒"
        pnl_emoji = "📈" if trade.realized_pnl >= 0 else "📉"
        
        # Calcular métricas adicionais
        duration = trade.exit_timestamp - trade.timestamp
        duration_str = self._format_duration(duration)
        price_change = ((trade.exit_price - trade.entry_price) / trade.entry_price) * 100
        
        # Log detalhado com mais informações
        logger.info(f"\n{result_emoji} ═══ TRADE FECHADO ═══")
        logger.info(f"   🆔 ID: {trade.id[:8]}")
        logger.info(f"   📊 Par: {trade.symbol} | Tipo: {trade.trade_type.upper()}")
        logger.info(f"   💵 Preços: ${trade.entry_price:.2f} → ${trade.exit_price:.2f} ({price_change:+.2f}%)")
        logger.info(f"   {pnl_emoji} P&L: ${trade.realized_pnl:.2f} ({trade.pnl_percent:.2f}%)")
        logger.info(f"   ⚡ Motivo: {self._get_exit_reason_description(trade.exit_reason)}")
        logger.info(f"   🕐 Duração: {duration_str}")
        logger.info(f"   📈 Timeframe: {trade.timeframe or 'N/A'}")
        logger.info(f"   💰 Balanço: ${self.current_balance - trade.realized_pnl:.2f} → ${self.current_balance:.2f}")
        
        # Notificação detalhada
        notification = self._create_trade_notification(trade, duration_str, price_change)
        
        # Enviar notificação em tempo real
        if self.realtime_updates:
            self.realtime_updates.notify_trade_closed(trade.to_dict())
            
        # Salvar no histórico detalhado
        self._save_to_detailed_history(trade, notification)
        
        # Exibir notificação no console
        self._display_trade_notification(notification)
        
        logger.info(f"═══════════════════════════\n")
    
    def _format_duration(self, duration) -> str:
        """Formata duração de forma legível"""
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _get_exit_reason_description(self, reason: str) -> str:
        """Retorna descrição detalhada do motivo de saída"""
        descriptions = {
            'take_profit': '🎯 Take Profit Atingido',
            'stop_loss': '🛑 Stop Loss Ativado',
            'manual': '🔒 Fechamento Manual'
        }
        return descriptions.get(reason, reason)
    
    def _create_trade_notification(self, trade: PaperTrade, duration_str: str, price_change: float) -> Dict:
        """Cria notificação estruturada do trade"""
        return {
            'type': 'trade_closed',
            'timestamp': datetime.now().isoformat(),
            'trade_id': trade.id,
            'symbol': trade.symbol,
            'trade_type': trade.trade_type,
            'entry_price': trade.entry_price,
            'exit_price': trade.exit_price,
            'price_change_percent': price_change,
            'realized_pnl': trade.realized_pnl,
            'pnl_percent': trade.pnl_percent,
            'exit_reason': trade.exit_reason,
            'exit_reason_description': self._get_exit_reason_description(trade.exit_reason),
            'duration': duration_str,
            'timeframe': trade.timeframe,
            'new_balance': self.current_balance,
            'success': trade.realized_pnl > 0,
            'emoji': '🎯' if trade.exit_reason == 'take_profit' else '🛑' if trade.exit_reason == 'stop_loss' else '🔒'
        }
    
    def _save_to_detailed_history(self, trade: PaperTrade, notification: Dict):
        """Salva trade no histórico detalhado"""
        try:
            # Adicionar à lista de notificações (pode ser salvo em arquivo ou banco)
            if not hasattr(self, 'trade_notifications'):
                self.trade_notifications = []
            
            self.trade_notifications.append(notification)
            
            # Manter apenas as últimas 100 notificações
            if len(self.trade_notifications) > 100:
                self.trade_notifications = self.trade_notifications[-100:]
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar no histórico detalhado: {e}")
    
    def _display_trade_notification(self, notification: Dict):
        """Exibe notificação formatada no console"""
        emoji = notification['emoji']
        symbol = notification['symbol']
        pnl = notification['realized_pnl']
        pnl_pct = notification['pnl_percent']
        reason = notification['exit_reason_description']
        duration = notification['duration']
        
        print(f"\n{emoji} ═══ NOTIFICAÇÃO DE TRADE ═══")
        print(f"   {symbol} | P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
        print(f"   {reason} | Duração: {duration}")
        print(f"   Novo Saldo: ${notification['new_balance']:.2f}")
        print(f"═══════════════════════════════\n")
    
    def close_trade_manually(self, trade_id: str) -> bool:
        """Fecha um trade manualmente"""
        if trade_id not in self.active_trades:
            logger.warning(f"⚠️ Trade {trade_id[:8]} não encontrado")
            return False
        
        trade = self.active_trades[trade_id]
        
        # Obter preço atual para fechamento usando API de tempo real
        from .realtime_price_api import realtime_price_api
        
        current_price = realtime_price_api.get_current_price(trade.symbol)
        if current_price is None:
            current_price = self.market_data.get_current_price(trade.symbol)
            
        if current_price:
            trade.update_current_price(current_price)
        
        # Fechar manualmente
        trade.close_manually()
        
        # Processar fechamento
        self._process_closed_trade(trade)
        del self.active_trades[trade_id]
        
        logger.info(f"🔒 Trade {trade_id[:8]} fechado manualmente")
        return True
    
    def get_portfolio_stats(self) -> Dict:
        """Obtém estatísticas do portfolio"""
        total_trades = len(self.trade_history)
        profitable_trades = len([t for t in self.trade_history if t.realized_pnl > 0])
        losing_trades = total_trades - profitable_trades
        
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(t.realized_pnl for t in self.trade_history)
        total_return = (total_pnl / self.initial_balance * 100) if self.initial_balance > 0 else 0
        
        # P&L não realizado dos trades ativos
        unrealized_pnl = sum(t.unrealized_pnl for t in self.active_trades.values())
        
        return {
            'current_balance': self.current_balance,
            'initial_balance': self.initial_balance,
            'total_pnl': total_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_trades': total_trades,
            'active_trades': len(self.active_trades),
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_return': total_return
        }
    
    def get_active_trades(self) -> List[Dict]:
        """Obtém lista de trades ativos"""
        return [trade.to_dict() for trade in self.active_trades.values()]
    
    def get_trade_notifications(self, limit: int = 20) -> List[Dict]:
        """Obtém histórico de notificações de trades"""
        if not hasattr(self, 'trade_notifications'):
            return []
        
        # Retornar as mais recentes primeiro
        notifications = self.trade_notifications[-limit:] if limit else self.trade_notifications
        return list(reversed(notifications))
    
    def get_detailed_stats(self) -> Dict:
        """Obtém estatísticas detalhadas do portfolio"""
        basic_stats = self.get_portfolio_stats()
        
        if not self.trade_history:
            return basic_stats
        
        # Estatísticas avançadas
        profits = [t.realized_pnl for t in self.trade_history if t.realized_pnl > 0]
        losses = [t.realized_pnl for t in self.trade_history if t.realized_pnl < 0]
        
        # Métricas de performance
        avg_profit = sum(profits) / len(profits) if profits else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        profit_factor = abs(sum(profits) / sum(losses)) if losses else float('inf')
        
        # Análise por motivo de saída
        exit_reasons = {}
        for trade in self.trade_history:
            reason = trade.exit_reason
            if reason not in exit_reasons:
                exit_reasons[reason] = {'count': 0, 'total_pnl': 0}
            exit_reasons[reason]['count'] += 1
            exit_reasons[reason]['total_pnl'] += trade.realized_pnl
        
        # Análise por timeframe
        timeframe_stats = {}
        for trade in self.trade_history:
            tf = trade.timeframe or 'unknown'
            if tf not in timeframe_stats:
                timeframe_stats[tf] = {'count': 0, 'total_pnl': 0, 'wins': 0}
            timeframe_stats[tf]['count'] += 1
            timeframe_stats[tf]['total_pnl'] += trade.realized_pnl
            if trade.realized_pnl > 0:
                timeframe_stats[tf]['wins'] += 1
        
        # Calcular win rate por timeframe
        for tf_data in timeframe_stats.values():
            tf_data['win_rate'] = (tf_data['wins'] / tf_data['count']) * 100 if tf_data['count'] > 0 else 0
        
        basic_stats.update({
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'largest_profit': max(profits) if profits else 0,
            'largest_loss': min(losses) if losses else 0,
            'exit_reasons': exit_reasons,
            'timeframe_stats': timeframe_stats,
            'total_notifications': len(getattr(self, 'trade_notifications', []))
        })
        
        return basic_stats
    
    def get_trade_history(self, limit: int = 50) -> List[PaperTrade]:
        """Obtém histórico de trades"""
        return sorted(self.trade_history, key=lambda t: t.timestamp, reverse=True)[:limit]


class AutoTradeMonitor:
    """Sistema de monitoramento automático de trades"""
    
    def __init__(self, paper_trading_manager, realtime_updates_manager, interval=30):
        self.paper_trading = paper_trading_manager
        self.realtime_updates = realtime_updates_manager
        self.interval = interval  # segundos
        self.running = False
        self.thread = None
        
    def start(self):
        """Iniciar monitoramento automático"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            logger.info(f"🔄 Monitor automático de trades iniciado (intervalo: {self.interval}s)")
    
    def stop(self):
        """Parar monitoramento automático"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("STOP Monitor automatico de trades parado")
    
    def get_status(self) -> Dict:
        """Status do monitor"""
        return {
            'running': self.running,
            'interval': self.interval,
            'active_trades_count': len(self.paper_trading.active_trades)
        }
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                # Atualizar preços de todos os trades ativos
                if self.paper_trading.active_trades:
                    old_count = len(self.paper_trading.active_trades)
                    self.paper_trading.update_prices()
                    new_count = len(self.paper_trading.active_trades)
                    
                    # Se algum trade foi fechado, notificar
                    if new_count < old_count:
                        portfolio_stats = self.paper_trading.get_portfolio_stats()
                        if self.realtime_updates:
                            self.realtime_updates.notify_portfolio_update(portfolio_stats)
                
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no monitor automático: {e}")
                time.sleep(self.interval)
