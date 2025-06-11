#!/usr/bin/env python3
"""
Trading Bot AI - Sistema Simplificado de Paper Trading
Sistema focado apenas no fluxo: Gerar Sinal → Aprovar → Contabilizar → Win Rate
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_login import login_required, current_user

# Importar módulos essenciais
from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.database import DatabaseManager
from src.config import Config
from src.paper_trading import PaperTradingManager, AutoTradeMonitor
from src.realtime_price_api import realtime_price_api

# Importar sistema de autenticação
from src.auth.models import db, bcrypt
from src.auth.routes import init_auth

# Configurar logging com UTF-8 para suportar emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'trading_bot_ai_simple_2024'

# Configurar PostgreSQL
try:
    # Tentar PostgreSQL primeiro
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:admin@localhost:5432/cryptoninja_db'
    )
except:
    # Fallback para SQLite se PostgreSQL não estiver disponível
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cryptoninja.db'
    logger.warning("⚠️ PostgreSQL não disponível, usando SQLite como fallback")
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db.init_app(app)
bcrypt.init_app(app)
init_auth(app)  # Configurar sistema de autenticação

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar banco de dados
def init_database():
    """Inicializar banco de dados PostgreSQL ou SQLite"""
    try:
        with app.app_context():
            # Tentar conectar e criar tabelas
            db.create_all()
            
            # Verificar qual banco está sendo usado
            if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
                logger.info("🗄️ Banco SQLite inicializado com sucesso")
            else:
                logger.info("🗄️ Banco PostgreSQL inicializado com sucesso")
            
            # Verificar se existe usuário admin
            from src.auth.models import User
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                # Criar usuário admin padrão
                admin_user = User(
                    username='admin',
                    email='admin@cryptoninja.com',
                    password='ninja123',  # Senha padrão - deve ser alterada
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                logger.info("🥷 Usuário admin criado com sucesso (senha: ninja123)")
            else:
                logger.info("🥷 Usuário admin já existe")
                
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
        # Tentar SQLite como fallback
        try:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cryptoninja.db'
            with app.app_context():
                db.create_all()
                logger.info("🗄️ Usando SQLite como fallback")
                
                # Criar admin no SQLite
                from src.auth.models import User
                admin_user = User.query.filter_by(username='admin').first()
                if not admin_user:
                    admin_user = User(
                        username='admin',
                        email='admin@cryptoninja.com',
                        password='ninja123',
                        is_admin=True
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    logger.info("🥷 Usuário admin criado no SQLite")
                    
        except Exception as e2:
            logger.error(f"❌ Erro crítico na inicialização do banco: {e2}")

# Inicializar componentes essenciais
logger.info("🚀 Inicializando Trading Bot AI - Modo Startup Rápido para Heroku")

# Inicializar banco de dados primeiro
init_database()

config = Config()
db_manager = DatabaseManager()

# OTIMIZAÇÃO HEROKU: Inicialização mínima para startup rápido
logger.info("⚡ Inicialização mínima para startup rápido...")
market_data = MarketDataManager(config)
ai_engine = AITradingEngine(config)

# Inicializar sistema de notificações em tempo real
from src.realtime_updates import RealTimeUpdates
realtime_updates = RealTimeUpdates(socketio)

signal_generator = SignalGenerator(ai_engine, market_data)
paper_trading = PaperTradingManager(market_data, realtime_updates)

# Configure socketio para notificações
from src.signal_generator import set_socketio_instance
set_socketio_instance(socketio)

# DEFER: Não iniciar data feed automaticamente - apenas quando necessário
logger.info("✅ Componentes essenciais inicializados - sem data feed automático")

# Conectar RealTimePriceAPI ao sistema WebSocket
def price_update_callback(symbol: str, price: float):
    """Callback para conectar preços em tempo real ao WebSocket"""
    try:
        # Preparar dados de preço para broadcast
        price_data = {
            'price': price,
            'change_24h': 0,  # Pode ser expandido futuramente
            'change_percent': 0,
            'volume': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Transmitir via WebSocket para todos os clientes conectados
        realtime_updates.broadcast_price_update(symbol, price_data)
        
    except Exception as e:
        logger.error(f"❌ Erro no callback de preços: {e}")

# Adicionar callback ao sistema de preços em tempo real
realtime_price_api.add_callback(price_update_callback)

# Iniciar sistema de preços em tempo real
realtime_price_api.start()

logger.info("🔗 Sistema de preços conectado ao WebSocket")

class SimpleTradingBot:
    """Bot de Trading Simplificado"""
    def __init__(self):
        self.is_running = False
        
    def start(self):
        """Iniciar o bot"""
        logger.info("▶️ Iniciando Trading Bot AI...")
        self.is_running = True
        
        # Inicializar componentes essenciais
        db_manager.initialize()
        market_data.start_data_feed()
        ai_engine.load_models()
        
        # Configurar eventos do WebSocket        realtime_updates.setup_events()
        
        # Garantir que o sistema de preços em tempo real esteja ativo
        if not realtime_price_api.running:
            realtime_price_api.start()
            logger.info("OK Sistema de precos em tempo real iniciado")
        
        logger.info("OK Trading Bot AI iniciado com sucesso!")
        
    def stop(self):
        """Parar o bot"""
        logger.info("STOP Parando Trading Bot AI...")
        self.is_running = False
        market_data.stop_data_feed()
        
        # Parar sistema de preços em tempo real
        realtime_price_api.stop()
        logger.info("STOP Sistema de precos em tempo real parado")
        
    def get_status(self):
        """Status do bot"""
        return {
            'running': self.is_running,
            'timestamp': datetime.now().isoformat()
        }

# Instância global do bot
trading_bot = SimpleTradingBot()

def sync_active_trade_symbols():
    """Sincronizar símbolos de trades ativos com sistema de preços em tempo real"""
    try:
        # Obter trades ativos do paper trading
        active_trades = paper_trading.get_active_trades()
        
        if active_trades:
            # Extrair símbolos únicos dos trades ativos
            active_symbols = list(set([trade.get('symbol', 'BTCUSDT') for trade in active_trades]))
            
            # Garantir que pelo menos um símbolo padrão esteja incluído
            if 'BTCUSDT' not in active_symbols:
                active_symbols.append('BTCUSDT')
            
            # Iniciar monitoramento dos símbolos ativos
            realtime_updates.start_price_updates(active_symbols)
            
            logger.info(f"🔄 Monitoramento de preços sincronizado para {len(active_symbols)} símbolos: {active_symbols}")
            
            return active_symbols
        else:
            # Se não há trades ativos, monitorar símbolos padrão
            default_symbols = ['BTCUSDT', 'ETHUSDT']
            realtime_updates.start_price_updates(default_symbols)
            
            logger.info(f"🔄 Nenhum trade ativo, monitorando símbolos padrão: {default_symbols}")
            
            return default_symbols
            
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar símbolos de trades ativos: {e}")
        return ['BTCUSDT']  # Fallback para símbolo padrão

def convert_hold_to_signal(signal, symbol, timeframe):
    """Converter sinal HOLD em BUY ou SELL baseado em análise simples"""
    if signal is None or signal.signal_type != 'hold':
        return signal
    
    try:
        # Obter dados de mercado atuais para análise
        current_market_data = market_data.get_market_data(symbol, timeframe)
        
        if current_market_data is not None and len(current_market_data) >= 5:
            # Análise simples de momentum para decidir BUY/SELL
            recent_prices = current_market_data['close'].tail(5).values
            
            # Calcular variação percentual recente
            price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
            
            # Determinar sinal baseado no momentum
            if price_change > 0.001:  # Alta de mais de 0.1%
                new_signal_type = 'buy'
                reason = 'converted_from_hold_momentum_up'
            else:
                new_signal_type = 'sell'
                reason = 'converted_from_hold_momentum_down'
            
            # Criar novo sinal mantendo estrutura original
            from src.signal_generator import Signal
            
            new_signal = Signal(
                symbol=signal.symbol,
                signal_type=new_signal_type,
                confidence=0.15,  # Confiança baixa para sinais convertidos
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                timeframe=signal.timeframe,
                reasons=[reason, 'original_was_hold'] + (signal.reasons or [])
            )
            
            logger.info(f"🔄 Convertido HOLD → {new_signal_type.upper()} para {symbol} (momentum: {price_change:.4f})")
            return new_signal
        
        # Fallback: usar timestamp para decisão pseudo-aleatória consistente
        import hashlib
        hash_input = f"{symbol}{timeframe}{datetime.now().strftime('%Y%m%d%H')}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        
        new_signal_type = 'buy' if hash_value % 2 == 0 else 'sell'
        
        from src.signal_generator import Signal
        new_signal = Signal(
            symbol=signal.symbol,
            signal_type=new_signal_type,
            confidence=0.10,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            timeframe=signal.timeframe,
            reasons=['converted_from_hold_fallback', 'original_was_hold'] + (signal.reasons or [])
        )
        
        logger.info(f"🔄 Convertido HOLD → {new_signal_type.upper()} para {symbol} (fallback)")
        return new_signal
        
    except Exception as e:
        logger.error(f"❌ Erro ao converter HOLD: {e}")
        # Em caso de erro, retornar sinal SELL conservador
        from src.signal_generator import Signal
        new_signal = Signal(
            symbol=signal.symbol,
            signal_type='sell',
            confidence=0.05,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            timeframe=signal.timeframe,
            reasons=['converted_from_hold_error', 'original_was_hold'] + (signal.reasons or [])
        )
        
        logger.info(f"🔄 Convertido HOLD → SELL para {symbol} (erro - conservador)")
        return new_signal

# =============================================================================
# ROTAS DA API
# =============================================================================

# ==================== ROTAS WEB ====================

@app.route('/')
@login_required
def index():
    """Dashboard Principal"""
    return render_template('index_enhanced.html')

@app.route('/main')
@login_required
def main():
    """Rota alternativa para o dashboard principal"""
    return redirect(url_for('index'))

# ==================== APIS ESSENCIAIS ====================

@app.route('/api/status')
def api_status():
    """Status do sistema"""
    return jsonify(trading_bot.get_status())

@app.route('/api/start', methods=['POST'])
def api_start():
    """Iniciar o bot"""
    try:
        trading_bot.start()
        return jsonify({'success': True, 'message': 'Bot iniciado'})
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar bot: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Parar o bot"""
    try:
        trading_bot.stop()
        return jsonify({'success': True, 'message': 'Bot parado'})
    except Exception as e:
        logger.error(f"❌ Erro ao parar bot: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate_signal', methods=['POST'])
def api_generate_signal():
    """Gerar novo sinal (sem restrições de confiança)"""
    try:        # Parâmetros da requisição
        data = request.get_json() if request.is_json else {}
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        
        logger.info(f"🎰 Gerando sinal para {symbol} {timeframe}")
        logger.info(f"📊 DEBUG: Dados da requisição: {data}")
        logger.info(f"📊 DEBUG: Signal generator instance: {signal_generator}")
        logger.info(f"📊 DEBUG: Signal generator config: {signal_generator.config.SIGNAL_CONFIG}")        # Gerar sinal
        logger.info(f"📊 DEBUG: Chamando signal_generator.generate_signal('{symbol}', '{timeframe}')")
        signal = signal_generator.generate_signal(symbol, timeframe)
        logger.info(f"📊 DEBUG: Resultado do generate_signal: {signal}")
        
        # Converter HOLD em BUY/SELL se necessário
        if signal and signal.signal_type == 'hold':
            logger.info(f"🔄 Sinal HOLD detectado para {symbol} - convertendo...")
            signal = convert_hold_to_signal(signal, symbol, timeframe)
        
        if signal is None:
            logger.warning(f"⚠️ Nenhum sinal gerado para {symbol}")
            logger.warning(f"📊 DEBUG: Signal é None - verificar causa")
            return jsonify({
                'success': False,
                'message': f'Nenhum sinal gerado para {symbol}',
                'signal': None
            })
        
        logger.info(f"✅ Sinal gerado: {signal.signal_type} para {symbol} @ ${signal.entry_price}")
        
        # Notificar em tempo real sobre novo sinal
        if realtime_updates:
            realtime_updates.notify_new_signal(signal.to_dict())
        
        return jsonify({
            'success': True,
            'message': f'Sinal {signal.signal_type} gerado',
            'signal': signal.to_dict()
        })
        
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"❌ Erro específico ao gerar sinal: {error_msg}")
        
        # Interpretar códigos de erro específicos
        if error_msg.startswith('COOLDOWN:'):
            return jsonify({
                'success': False, 
                'error': f'Aguarde alguns minutos antes de gerar outro sinal para {symbol}',
                'error_type': 'cooldown'
            }), 429
        elif error_msg.startswith('NO_DATA:') or error_msg.startswith('EMPTY_DATA:'):
            return jsonify({
                'success': False, 
                'error': f'Dados de mercado indisponíveis para {symbol}. Tente novamente em alguns instantes.',
                'error_type': 'no_data'
            }), 503
        elif error_msg.startswith('INSUFFICIENT_DATA:'):
            parts = error_msg.split(':')
            count = parts[2] if len(parts) > 2 else 'poucos'
            return jsonify({
                'success': False, 
                'error': f'Dados históricos insuficientes para {symbol} ({count} registros). Timeframes menores requerem mais dados.',
                'error_type': 'insufficient_data'
            }), 503
        elif error_msg.startswith('MISSING_COLUMNS:'):
            return jsonify({
                'success': False, 
                'error': f'Dados de mercado incompletos para {symbol}. Verifique a conexão com a exchange.',
                'error_type': 'invalid_data'
            }), 503
        elif error_msg.startswith('INVALID_DATA:'):
            return jsonify({
                'success': False, 
                'error': f'Dados de mercado inválidos para {symbol}. Tente outro símbolo ou timeframe.',
                'error_type': 'invalid_data'
            }), 503
        elif error_msg.startswith('INDICATORS_FAILED:'):
            return jsonify({
                'success': False, 
                'error': f'Falha no cálculo de indicadores técnicos para {symbol}. Dados podem estar corrompidos.',
                'error_type': 'indicators_error'
            }), 500
        elif error_msg.startswith('LOW_CONFLUENCE:'):
            return jsonify({
                'success': False, 
                'error': f'Condições de mercado não favoráveis para {symbol}. Indicadores não convergem para um sinal claro.',
                'error_type': 'low_confluence'
            }), 200
        elif error_msg.startswith('PRICE_ERROR:'):
            return jsonify({
                'success': False, 
                'error': f'Erro ao obter preço atual de {symbol}. Verifique se o símbolo está correto.',
                'error_type': 'price_error'
            }), 503
        else:
            return jsonify({
                'success': False, 
                'error': f'Erro técnico: {error_msg}',
                'error_type': 'technical_error'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao gerar sinal: {e}")
        return jsonify({
            'success': False, 
            'error': f'Erro interno do sistema. Tente novamente em alguns instantes.',
            'error_type': 'system_error'
        }), 500

@app.route('/api/generate_signals_all_pairs', methods=['POST'])
def api_generate_signals_all_pairs():
    """API para gerar sinais para todos os pares configurados"""
    try:
        data = request.get_json() or {}
        timeframe = data.get('timeframe', '1h')
        
        logger.info(f"🔄 Gerando sinais para todos os pares (timeframe: {timeframe})")
          # Gerar sinais para todos os pares
        signals = signal_generator.generate_signals_for_all_pairs()
        
        # Converter sinais HOLD em BUY/SELL
        converted_signals = []
        for signal in signals:
            if signal.signal_type == 'hold':
                logger.info(f"🔄 Convertendo HOLD para {signal.symbol}")
                signal = convert_hold_to_signal(signal, signal.symbol, timeframe)
            converted_signals.append(signal)
        
        signals = converted_signals
        
        # Converter sinais para formato de resposta
        signals_data = []
        for signal in signals:signals_data.append({
                'symbol': signal.symbol,
                'signal_type': signal.signal_type,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'confidence': signal.confidence,
                'timeframe': signal.timeframe,
                'timestamp': signal.timestamp.isoformat() if signal.timestamp else None,
                'asset_type': config.get_asset_type(signal.symbol)
            })
        
        logger.info(f"✅ Gerados {len(signals_data)} sinais para múltiplos ativos")
        
        # Notificar em tempo real sobre novos sinais
        if realtime_updates and signals_data:
            for signal_data in signals_data:
                realtime_updates.notify_new_signal(signal_data)
        
        return jsonify({
            'success': True,
            'message': f'{len(signals_data)} sinais gerados para múltiplos ativos',
            'signals': signals_data,
            'total_pairs_analyzed': len(config.get_all_pairs()),
            'signals_generated': len(signals_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar sinais para todos os pares: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== APIS PAPER TRADING ====================

@app.route('/api/signals/active')
def api_active_signals():
    """Buscar sinais ativos"""
    try:
        active_signals = signal_generator.get_active_signals()
        
        # Verificar se já são dicionários ou precisam ser convertidos
        signals_data = []
        for signal in active_signals:
            if hasattr(signal, 'to_dict'):
                signals_data.append(signal.to_dict())
            elif isinstance(signal, dict):
                signals_data.append(signal)
            else:
                # Fallback para conversão manual
                signals_data.append({
                    'id': getattr(signal, 'id', 'unknown'),
                    'symbol': getattr(signal, 'symbol', 'unknown'),
                    'signal_type': getattr(signal, 'signal_type', 'unknown'),
                    'confidence': getattr(signal, 'confidence', 0),
                    'entry_price': getattr(signal, 'entry_price', 0),
                    'stop_loss': getattr(signal, 'stop_loss', 0),
                    'take_profit': getattr(signal, 'take_profit', 0),
                    'timestamp': getattr(signal, 'timestamp', '').isoformat() if hasattr(getattr(signal, 'timestamp', ''), 'isoformat') else str(getattr(signal, 'timestamp', '')),
                    'status': getattr(signal, 'status', 'unknown')
                })
        
        logger.info(f"📊 Retornando {len(signals_data)} sinais ativos")
        return jsonify({
            'success': True,
            'signals': signals_data,
            'count': len(signals_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar sinais ativos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paper_trading/confirm_signal', methods=['POST'])
def api_confirm_signal():
    """Confirmar sinal e abrir trade fictício"""
    try:
        data = request.get_json()
        signal = data.get('signal')
        amount = data.get('amount', 1000)  # Valor padrão
        
        if not signal:
            return jsonify({'success': False, 'error': 'Sinal não fornecido'}), 400
        
        logger.info(f"✅ Confirmando sinal: {signal['signal_type']} {signal['symbol']}")
          # Confirmar sinal no paper trading
        trade = paper_trading.confirm_signal(signal, amount)
        
        if trade:
            logger.info(f"📈 Trade aberto: {trade.id}")
            
            # Sincronizar símbolos de trades ativos com sistema de preços
            try:
                sync_active_trade_symbols()
            except Exception as sync_error:
                logger.warning(f"⚠️ Erro ao sincronizar símbolos: {sync_error}")
            
            return jsonify({
                'success': True,
                'message': 'Trade confirmado',
                'trade_id': trade.id
            })
        else:
            return jsonify({'success': False, 'error': 'Erro ao abrir trade'}), 500
            
    except Exception as e:
        logger.error(f"❌ Erro ao confirmar sinal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paper_trading/portfolio')
def api_portfolio():
    """Obter estatísticas do portfolio"""
    try:
        portfolio = paper_trading.get_portfolio_stats()
        active_trades = paper_trading.get_active_trades()
          # Usar dados completos dos trades e apenas atualizar preços atuais
        active_trades_data = []
        for trade in active_trades:
            # Usar o dicionário completo do trade
            trade_data = trade.copy()
            
            # Atualizar preço atual se disponível
            current_price = market_data.get_current_price(trade['symbol'])
            if current_price:
                trade_data['current_price'] = current_price
            
            active_trades_data.append(trade_data)
        
        logger.info(f"📊 Portfolio: {portfolio['total_trades']} trades, {portfolio['win_rate']:.1f}% win rate")
        
        return jsonify({
            'success': True,
            'portfolio': portfolio,
            'active_trades': active_trades_data
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter portfolio: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paper_trading/close_trade', methods=['POST'])
def api_close_trade():
    """Fechar trade específico"""
    try:
        data = request.get_json()
        trade_id = data.get('trade_id')
        
        if not trade_id:
            return jsonify({'success': False, 'error': 'ID do trade não fornecido'}), 400
        
        logger.info(f"🔒 Fechando trade: {trade_id}")
          # Fechar trade
        success = paper_trading.close_trade_manually(trade_id)
        
        if success:
            logger.info(f"✅ Trade {trade_id} fechado com sucesso")
            
            # Sincronizar símbolos de trades ativos com sistema de preços
            try:
                sync_active_trade_symbols()
            except Exception as sync_error:
                logger.warning(f"⚠️ Erro ao sincronizar símbolos: {sync_error}")
            
            return jsonify({'success': True, 'message': 'Trade fechado'})
        else:
            return jsonify({'success': False, 'error': 'Trade não encontrado'}), 404
            
    except Exception as e:
        logger.error(f"❌ Erro ao fechar trade: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paper_trading/history')
def api_trading_history():
    """Histórico de trades"""
    try:
        limit = request.args.get('limit', 50, type=int)
        trades = paper_trading.get_trade_history(limit)
        
        # Converter trades para dicionários
        trades_data = []
        for trade in trades:
            trade_dict = trade.to_dict() if hasattr(trade, 'to_dict') else {
                'id': trade.id,
                'symbol': trade.symbol,
                'trade_type': trade.trade_type,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'pnl': trade.pnl or 0,
                'pnl_percent': getattr(trade, 'pnl_percent', 0),
                'status': trade.status,
                'timestamp': trade.timestamp.isoformat()
            }
            trades_data.append(trade_dict)

        return jsonify({
            'success': True,
            'trades': trades_data,
            'total': len(trades_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter histórico: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paper_trading/update_prices', methods=['POST'])
def api_update_prices():
    """Forçar atualização manual de preços dos trades ativos"""
    try:
        logger.info("🔄 Forçando atualização manual de preços...")
        
        # Contar trades antes da atualização
        trades_before = len(paper_trading.active_trades)
        
        # Executar atualização de preços
        paper_trading.update_prices()
        
        # Contar trades após a atualização
        trades_after = len(paper_trading.active_trades)
        
        # Verificar se algum trade foi fechado
        trades_closed = trades_before - trades_after
        
        logger.info(f"✅ Atualização concluída: {trades_before} → {trades_after} trades ativos")
        
        return jsonify({
            'success': True,
            'message': f'Preços atualizados. {trades_closed} trades finalizados.',
            'trades_before': trades_before,
            'trades_after': trades_after,
            'trades_closed': trades_closed
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na atualização de preços: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/price/<symbol>')
def get_current_price_endpoint(symbol):
    """Obter preço atual de um ativo"""
    try:
        logger.info(f"📊 Obtendo preço para {symbol}")
        
        # Normalizar símbolo (sempre maiúsculo)
        symbol = symbol.upper()
        
        # Obter preço atual
        current_price = market_data.get_current_price(symbol)
        
        if current_price is None:
            return jsonify({
                'success': False,
                'error': f'Não foi possível obter preço para {symbol}'
            }), 404
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'price': current_price,
            'timestamp': datetime.now().isoformat()        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter preço: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/price/realtime/<symbol>')
def get_realtime_price_endpoint(symbol):
    """Obter preço em tempo real ultra-rápido"""
    try:
        # Normalizar símbolo
        symbol = symbol.upper()
        
        # Usar API otimizada diretamente
        price_info = realtime_price_api.get_price_info(symbol)
        
        if price_info:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'price': price_info['price'],
                'timestamp': price_info['timestamp'],
                'source': price_info['source'],
                'age_seconds': price_info['age_seconds']
            })
        
        # Fallback para API tradicional
        current_price = realtime_price_api.get_current_price(symbol)
        if current_price:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'price': current_price,
                'timestamp': datetime.now().isoformat(),
                'source': 'fallback'
            })
        
        return jsonify({
            'success': False,
            'error': f'Preço não disponível para {symbol}'
        }), 404
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter preço tempo real: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ROTAS DEBUG ====================

@app.route('/api/debug/force_signal', methods=['POST'])
def api_debug_force_signal():
    """Forçar geração de sinal para debug - bypassa todas as validações"""
    try:
        data = request.get_json() if request.is_json else {}
        symbol = data.get('symbol', 'BTCUSDT')
        signal_type = data.get('signal_type', 'buy')
        
        logger.info(f"🔧 DEBUG: Forçando sinal {signal_type} para {symbol}")
        
        # Obter preço atual
        current_price = market_data.get_current_price(symbol)
        if current_price is None:
            current_price = 105000  # Fallback para BTCUSDT
        
        # Importar classe Signal
        from src.signal_generator import Signal
        from datetime import datetime
        
        # Criar sinal forçado
        forced_signal = Signal(
            symbol=symbol,
            signal_type=signal_type,
            confidence=0.75,  # 75% de confiança forçada
            entry_price=current_price,
            stop_loss=current_price * (0.98 if signal_type == 'buy' else 1.02),
            take_profit=current_price * (1.04 if signal_type == 'buy' else 0.96),
            timeframe='1h',
            timestamp=datetime.now(),
            reasons=['Sinal forçado via debug', 'Bypass de validações', 'Teste de funcionamento']
        )
        
        # Registrar o sinal
        signal_generator._register_signal(forced_signal)
        
        logger.info(f"✅ DEBUG: Sinal forçado criado: {forced_signal.id}")
        
        return jsonify({
            'success': True,
            'message': f'Sinal {signal_type} forçado para debug',
            'signal': forced_signal.to_dict()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao forçar sinal debug: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Cliente conectou"""
    logger.info("🔗 Cliente WebSocket conectado")
    emit('status', {'message': 'Conectado ao Trading Bot AI'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectou"""
    logger.info("🔌 Cliente WebSocket desconectado")

@socketio.on('request_status')
def handle_status_request():
    """Cliente solicitou status"""
    emit('status_update', trading_bot.get_status())

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno do servidor: {error}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

# ==================== MAIN ====================

def initialize_system():
    """Inicializar sistema na inicialização"""
    try:
        logger.info("🔄 Inicializando sistema...")
        
        # Verificar diretórios
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        
        # Inicializar componentes
        db_manager.initialize()
        
        logger.info("✅ Sistema inicializado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise

# Sistema de monitoramento automático
import threading
import time

# Inicializar monitor automático
auto_monitor = AutoTradeMonitor(paper_trading, realtime_updates, interval=30)

@app.route('/api/monitor/start', methods=['POST'])
def api_start_monitor():
    """API para iniciar monitor automático"""
    try:
        auto_monitor.start()
        
        return jsonify({
            'success': True,
            'message': 'Monitor automático iniciado',
            'interval': auto_monitor.interval
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar monitor: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitor/stop', methods=['POST'])
def api_stop_monitor():
    """API para parar monitor automático"""
    try:
        auto_monitor.stop()
        
        return jsonify({
            'success': True,
            'message': 'Monitor automático parado'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao parar monitor: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitor/status')
def api_monitor_status():
    """API para verificar status do monitor"""
    try:
        status = {
            'running': auto_monitor.running,
            'interval': auto_monitor.interval,
            'active_trades': len(paper_trading.active_trades)
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status do monitor: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/realtime/start', methods=['POST'])
def api_start_realtime():
    """API para iniciar atualizações em tempo real"""
    try:
        data = request.get_json() or {}
        symbols = data.get('symbols', ['BTCUSDT'])
        realtime_updates.start_price_updates(symbols)
        
        logger.info(f"🔄 Atualizações em tempo real iniciadas para: {symbols}")
        
        return jsonify({
            'success': True,
            'message': f'Atualizações em tempo real iniciadas para {len(symbols)} símbolos',
            'symbols': symbols
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar atualizações em tempo real: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/realtime/stop', methods=['POST'])
def api_stop_realtime():
    """API para parar atualizações em tempo real"""
    try:
        realtime_updates.stop_price_updates()
        
        return jsonify({
            'success': True,
            'message': 'Atualizações em tempo real paradas'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao parar atualizações em tempo real: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/realtime/sync-symbols', methods=['POST'])
def api_sync_realtime_symbols():
    """API para sincronizar símbolos de trades ativos com sistema de preços"""
    try:
        # Sincronizar símbolos automaticamente
        active_symbols = sync_active_trade_symbols()
        
        return jsonify({
            'success': True,
            'message': 'Símbolos sincronizados com trades ativos',
            'symbols': active_symbols,
            'count': len(active_symbols)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar símbolos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/update_trades', methods=['POST'])
def api_update_trades():
    """API para atualizar trades ativos manualmente"""
    try:
        paper_trading.update_prices()
        
        # Notificar portfolio atualizado
        if realtime_updates:
            portfolio_stats = paper_trading.get_portfolio_stats()
            active_trades = paper_trading.get_active_trades()
            realtime_updates.notify_portfolio_update(portfolio_stats)
        
        return jsonify({
            'success': True,
            'message': 'Trades atualizados com sucesso',
            'active_trades': len(paper_trading.active_trades)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar trades: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/expand_data', methods=['POST'])
def api_expand_data():
    """API para expandir cobertura de dados após startup"""
    try:
        # Executar em thread separada para não bloquear
        def expand_in_background():
            market_data.expand_data_coverage()
        
        thread = threading.Thread(target=expand_in_background, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Expansão de dados iniciada em background',
            'status': 'expanding'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao expandir dados: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/load_symbol_data', methods=['POST'])
def api_load_symbol_data():
    """API para carregar dados de símbolo específico sob demanda"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        
        market_data.load_symbol_data_on_demand(symbol, timeframe)
        
        return jsonify({
            'success': True,
            'message': f'Dados carregados para {symbol} {timeframe}',
            'symbol': symbol,
            'timeframe': timeframe
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dados do símbolo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    try:
        # Inicializar sistema
        initialize_system()
        
        # Iniciar bot automaticamente
        trading_bot.start()
        
        # Inicializar monitor automático
        auto_monitor.start()
        
        # Inicializar sistema de notificações em tempo real para símbolos principais
        principal_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        realtime_updates.start_price_updates(principal_symbols)
        
        logger.info("🚀 Iniciando servidor Flask...")
        logger.info("📊 Dashboard disponível em: http://localhost:5000")
        logger.info("🔄 Monitor automático ativo")
        logger.info("📡 Notificações em tempo real ativas")
        
        # Iniciar servidor
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("STOP Interrompido pelo usuario")
        auto_monitor.stop()
        realtime_updates.stop_price_updates()
        trading_bot.stop()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        auto_monitor.stop()
        realtime_updates.stop_price_updates()
        sys.exit(1)
