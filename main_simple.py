#!/usr/bin/env python3
"""
Trading Bot AI - Sistema Simplificado de Paper Trading
Sistema focado apenas no fluxo: Gerar Sinal → Aprovar → Contabilizar → Win Rate
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Importar módulos essenciais
from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.database import DatabaseManager
from src.config import Config
from src.paper_trading import PaperTradingManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'trading_bot_ai_simple_2024'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar componentes essenciais
logger.info("🚀 Inicializando Trading Bot AI - Versão Simplificada")
config = Config()
db_manager = DatabaseManager()
market_data = MarketDataManager(config)
ai_engine = AITradingEngine(config)
signal_generator = SignalGenerator(ai_engine, market_data)
paper_trading = PaperTradingManager(market_data)

# Configure socketio para notificações
from src.signal_generator import set_socketio_instance
set_socketio_instance(socketio)

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
        
        logger.info("✅ Trading Bot AI iniciado com sucesso!")
        
    def stop(self):
        """Parar o bot"""
        logger.info("⏹️ Parando Trading Bot AI...")
        self.is_running = False
        market_data.stop_data_feed()
        
    def get_status(self):
        """Status do bot"""
        return {
            'running': self.is_running,
            'timestamp': datetime.now().isoformat()
        }

# Instância global do bot
trading_bot = SimpleTradingBot()

# ==================== ROTAS WEB ====================

@app.route('/')
def index():
    """Dashboard Principal"""
    return render_template('index.html')

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
    try:
        # Parâmetros da requisição
        data = request.get_json() if request.is_json else {}
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        
        logger.info(f"🎰 Gerando sinal para {symbol} {timeframe}")
        
        # Gerar sinal
        signal = signal_generator.generate_signal(symbol, timeframe)
        
        if signal is None:
            logger.warning(f"⚠️ Nenhum sinal gerado para {symbol}")
            return jsonify({
                'success': False,
                'message': f'Nenhum sinal gerado para {symbol}',
                'signal': None
            })
        
        logger.info(f"✅ Sinal gerado: {signal.signal_type} para {symbol} @ ${signal.price}")
        return jsonify({
            'success': True,
            'message': f'Sinal {signal.signal_type} gerado',
            'signal': signal.to_dict()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar sinal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== APIS PAPER TRADING ====================

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
        
        # Converter trades ativos para dicionários
        active_trades_data = []
        for trade in active_trades:
            current_price = market_data.get_current_price(trade.symbol)
            current_pnl = trade.calculate_pnl(current_price) if current_price else 0
            
            active_trades_data.append({
                'id': trade.id,
                'symbol': trade.symbol,
                'action': trade.action,
                'entry_price': trade.entry_price,
                'amount': trade.amount,
                'current_pnl': current_pnl,
                'timestamp': trade.timestamp.isoformat()
            })
        
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
        success = paper_trading.close_trade(trade_id)
        
        if success:
            logger.info(f"✅ Trade {trade_id} fechado com sucesso")
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
            trades_data.append({
                'id': trade.id,
                'symbol': trade.symbol,
                'action': trade.action,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'amount': trade.amount,
                'pnl': trade.pnl or 0,
                'status': trade.status,
                'timestamp': trade.timestamp.isoformat()
            })
        
        logger.info(f"📜 Histórico: {len(trades_data)} trades")
        
        return jsonify({
            'success': True,
            'trades': trades_data,
            'count': len(trades_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter histórico: {e}")
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

if __name__ == '__main__':
    try:
        # Inicializar sistema
        initialize_system()
        
        # Iniciar bot automaticamente
        trading_bot.start()
        
        logger.info("🚀 Iniciando servidor Flask...")
        logger.info("📊 Dashboard disponível em: http://localhost:5000")
        
        # Iniciar servidor
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido pelo usuário")
        trading_bot.stop()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)
