#!/usr/bin/env python3
"""
Crypto & Forex AI Trading Signal Generator
Aplicativo para gerar sinais de compra e venda usando IA
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Importar módulos do sistema
from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.risk_manager import RiskManager
from src.database import DatabaseManager
from src.config import Config

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
app.config['SECRET_KEY'] = 'crypto_trading_ai_2024'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar componentes do sistema
config = Config()
db_manager = DatabaseManager()
market_data = MarketDataManager(config)
ai_engine = AITradingEngine(config)
signal_generator = SignalGenerator(ai_engine, market_data)
risk_manager = RiskManager(config)

# Configure socketio for signal notifications
from src.signal_generator import set_socketio_instance
set_socketio_instance(socketio)

class TradingBot:
    def __init__(self):
        self.is_running = False
        self.active_signals = []
        
    def start(self):
        """Iniciar o bot de trading"""
        logger.info("Iniciando Trading Bot AI...")
        self.is_running = True
        
        # Inicializar componentes
        db_manager.initialize()
        market_data.start_data_feed()
        ai_engine.load_models()
        
        logger.info("Trading Bot AI iniciado com sucesso!")
        
    def stop(self):
        """Parar o bot de trading"""
        logger.info("Parando Trading Bot AI...")
        self.is_running = False
        market_data.stop_data_feed()
        
    def get_status(self):
        """Obter status do bot"""
        return {
            'running': self.is_running,
            'active_signals': len(self.active_signals),
            'timestamp': datetime.now().isoformat()
        }

# Instância global do bot
trading_bot = TradingBot()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API para obter status do bot"""
    return jsonify(trading_bot.get_status())

@app.route('/api/start', methods=['POST'])
def api_start():
    """API para iniciar o bot"""
    try:
        trading_bot.start()
        return jsonify({'success': True, 'message': 'Bot iniciado com sucesso'})
    except Exception as e:
        logger.error(f"Erro ao iniciar bot: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """API para parar o bot"""
    try:
        trading_bot.stop()
        return jsonify({'success': True, 'message': 'Bot parado com sucesso'})
    except Exception as e:
        logger.error(f"Erro ao parar bot: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signals')
def api_signals():
    """API para obter sinais ativos"""
    try:
        limit = request.args.get('limit', type=int)
        signals = signal_generator.get_active_signals()
        
        # Converter para lista de dicionários se necessário
        if signals and hasattr(signals[0], 'to_dict'):
            signals_data = [signal.to_dict() for signal in signals]
        else:
            signals_data = signals if signals else []
        
        # Aplicar limite se especificado
        if limit and limit > 0:
            signals_data = signals_data[:limit]
        
        logger.info(f"📊 Retornando {len(signals_data)} sinais via API")
        
        return jsonify({
            'success': True,
            'signals': signals_data,
            'count': len(signals_data),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro ao obter sinais: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'signals': [],
            'count': 0
        }), 500

@app.route('/api/generate_signal', methods=['POST'])
def api_generate_signal():
    """API para gerar novo sinal"""
    try:
        # Verificar se há dados JSON
        if request.is_json:
            data = request.get_json()
            symbol = data.get('symbol', 'BTCUSDT')
            timeframe = data.get('timeframe', '1h')
        else:
            # Usar valores padrão se não houver JSON
            symbol = 'BTCUSDT'
            timeframe = '1h'
        
        logger.info(f"Tentando gerar sinal para {symbol} {timeframe}")
        signal = signal_generator.generate_signal(symbol, timeframe)
        
        if signal is None:
            logger.warning(f"Nenhum sinal gerado para {symbol} {timeframe}")
            return jsonify({
                'success': False,
                'message': f'Nenhum sinal gerado para {symbol}. Possíveis causas: dados insuficientes, baixa confiança ou cooldown ativo.',
                'signal': None
            })
        
        logger.info(f"Sinal gerado com sucesso: {signal.signal_type} para {symbol}")
        return jsonify({
            'success': True,
            'message': f'Sinal {signal.signal_type} gerado para {symbol}',
            'signal': signal.to_dict()
        })
    except Exception as e:
        logger.error(f"Erro ao gerar sinal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate_test_signal', methods=['POST'])
def api_generate_test_signal():
    """API para gerar sinal de teste forçado"""
    try:
        from src.signal_generator import Signal
        from datetime import datetime
        
        # Obter preço atual
        current_price = market_data.get_current_price('BTCUSDT')
        if current_price is None:
            current_price = 45000  # Fallback
        
        # Criar sinal forçado
        test_signal = Signal(
            symbol='BTCUSDT',
            signal_type='buy',
            confidence=0.85,
            entry_price=current_price,
            stop_loss=current_price * 0.98,
            take_profit=current_price * 1.04,
            timeframe='1h',
            timestamp=datetime.now(),
            reasons=['Sinal de teste forçado', 'RSI oversold simulado', 'Volume alto simulado']
        )
        
        # Registrar o sinal
        signal_generator._register_signal(test_signal)
        
        logger.info(f"Sinal de teste criado: {test_signal.signal_type} para {test_signal.symbol}")
        
        return jsonify({
            'success': True,
            'message': 'Sinal de teste criado com sucesso',
            'signal': test_signal.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar sinal de teste: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/positions')
def api_positions():
    """API para obter posições abertas"""
    try:
        # Como não executamos trades reais, retornamos lista vazia
        positions = []
        return jsonify(positions)
    except Exception as e:
        logger.error(f"Erro ao obter posições: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def api_performance():
    """API para obter dados de performance"""
    try:
        # Dados simulados de performance
        performance = {
            'total_pnl': 0.0,
            'daily_pnl': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0
        }
        return jsonify(performance)
    except Exception as e:
        logger.error(f"Erro ao obter performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API para obter estatísticas do dashboard"""
    try:
        stats = {
            'total_pnl': 0.0,
            'active_signals': len(trading_bot.active_signals),
            'open_positions': 0,
            'win_rate': 0.0
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings')
def api_settings():
    """API para obter configurações"""
    try:
        settings = {
            'risk_per_trade': config.RISK_MANAGEMENT['max_risk_per_trade'],
            'max_drawdown': 20,
            'max_daily_loss': 10,
            'primary_timeframe': '1h',
            'max_positions': config.RISK_MANAGEMENT['max_open_positions'],
            'min_confidence': int(config.SIGNAL_CONFIG['min_confidence'] * 100),  # Convert to percentage
            'timeframes': config.TIMEFRAMES,
            'crypto_pairs': config.CRYPTO_PAIRS,
            'forex_pairs': config.FOREX_PAIRS
        }
        return jsonify({'success': True, 'settings': settings})
    except Exception as e:
        logger.error(f"Erro ao obter configurações: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def api_update_settings():
    """API para atualizar configurações"""
    try:
        data = request.get_json()
        logger.info(f"Atualizando configurações: {data}")
        
        # Update min_confidence in config
        if 'min_confidence' in data:
            new_confidence = float(data['min_confidence']) / 100.0  # Convert from percentage
            config.SIGNAL_CONFIG['min_confidence'] = new_confidence
            logger.info(f"🎯 Confiança mínima atualizada para: {new_confidence:.2%}")
            
            # Update signal generator config
            if signal_generator:
                signal_generator.config.SIGNAL_CONFIG['min_confidence'] = new_confidence
        
        # Update other risk management settings
        if 'risk_per_trade' in data:
            config.RISK_MANAGEMENT['max_risk_per_trade'] = float(data['risk_per_trade']) / 100.0
            
        if 'max_positions' in data:
            config.RISK_MANAGEMENT['max_open_positions'] = int(data['max_positions'])
        
        logger.info("✅ Configurações atualizadas com sucesso!")
        return jsonify({
            'success': True, 
            'message': f'Configurações atualizadas! Nova confiança mínima: {config.SIGNAL_CONFIG["min_confidence"]:.1%}'
        })
    except Exception as e:
        logger.error(f"Erro ao atualizar configurações: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Lidar com conexão WebSocket"""
    logger.info('Cliente conectado via WebSocket')
    emit('status', trading_bot.get_status())

@socketio.on('disconnect')
def handle_disconnect():
    """Lidar com desconexão WebSocket"""
    logger.info('Cliente desconectado do WebSocket')

def broadcast_signal(signal):
    """Transmitir sinal para todos os clientes conectados"""
    socketio.emit('new_signal', signal)

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    logger.info("Iniciando aplicativo Crypto & Forex AI Trading...")
    
    # Executar aplicativo
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)