// Dashboard JavaScript para Trading Bot AI

class TradingBotDashboard {
    constructor() {
        this.socket = null;
        this.charts = {};
        this.isConnected = false;
        this.currentSection = 'dashboard';
        
        this.init();
    }

    init() {
        this.initializeSocket();
        this.setupEventListeners();
        this.initializeCharts();
        this.loadInitialData();
        this.startPeriodicUpdates();
        this.setupConfidenceSlider();
    }

    // Socket.IO Setup
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Conectado ao servidor');
            this.isConnected = true;
            this.showNotification('Conectado ao servidor', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('Desconectado do servidor');
            this.isConnected = false;
            this.showNotification('Desconectado do servidor', 'warning');
        });

        this.socket.on('bot_status', (data) => {
            this.updateBotStatus(data.status);
        });

        this.socket.on('new_signal', (data) => {
            this.handleNewSignal(data);
        });

        this.socket.on('position_update', (data) => {
            this.handlePositionUpdate(data);
        });

        this.socket.on('performance_update', (data) => {
            this.updatePerformanceData(data);
        });
    }

    // Event Listeners
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.closest('.nav-link').dataset.section;
                this.showSection(section);
            });
        });

        // Asset Selection
        const assetSelect = document.getElementById('assetSelect');
        if (assetSelect) {
            assetSelect.addEventListener('change', (e) => {
                this.updateCurrentAsset(e.target.value);
            });
        }

        // Timeframe Selection
        const timeframeSelect = document.getElementById('timeframeSelect');
        if (timeframeSelect) {
            timeframeSelect.addEventListener('change', (e) => {
                this.updateTimeframe(e.target.value);
            });
        }

        // Confidence Slider
        const confidenceSlider = document.getElementById('confidenceSlider');
        if (confidenceSlider) {
            confidenceSlider.addEventListener('input', (e) => {
                this.updateConfidence(e.target.value);
            });
        }

        // Bot Controls
        document.getElementById('startBot').addEventListener('click', () => {
            this.startBot();
        });

        document.getElementById('stopBot').addEventListener('click', () => {
            this.stopBot();
        });

        document.getElementById('generateSignal').addEventListener('click', () => {
            this.generateSignal();
        });

        // Settings
        const saveSettings = document.getElementById('saveSettings');
        if (saveSettings) {
            saveSettings.addEventListener('click', () => {
                this.saveSettings();
            });
        }

        // Test Signal Generation
        const generateTestSignal = document.getElementById('generateTestSignal');
        if (generateTestSignal) {
            generateTestSignal.addEventListener('click', () => {
                this.generateTestSignal();
            });
        }

        // Real Signal Generation
        const generateRealSignal = document.getElementById('generateRealSignal');
        if (generateRealSignal) {
            generateRealSignal.addEventListener('click', () => {
                this.generateRealSignal();
            });
        }

        // Auto-refresh toggle
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
    }

    // Navigation
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.display = 'none';
        });

        // Show selected section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }

        // Update navigation for both sidebar and mobile nav
        document.querySelectorAll('.nav-link[data-section]').forEach(link => {
            link.classList.remove('active');
        });
        
        // Update all links with the same data-section attribute
        document.querySelectorAll(`[data-section="${sectionName}"]`).forEach(link => {
            link.classList.add('active');
        });

        this.currentSection = sectionName;
        
        // Load section-specific data
        this.loadSectionData(sectionName);
        
        // Scroll to top on mobile
        if (window.innerWidth <= 768) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    loadSectionData(section) {
        switch (section) {
            case 'signals':
                this.loadSignals();
                break;
            case 'positions':
                this.loadPositions();
                break;
            case 'performance':
                this.loadPerformanceData();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }
    }

    // Bot Controls
    async startBot() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/start', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Bot iniciado com sucesso', 'success');
                this.updateBotStatus('running');
            } else {
                this.showNotification(`Erro ao iniciar bot: ${data.message}`, 'error');
            }
        } catch (error) {
            this.showNotification('Erro de conexão ao iniciar bot', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async stopBot() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/stop', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Bot parado com sucesso', 'success');
                this.updateBotStatus('stopped');
            } else {
                this.showNotification(`Erro ao parar bot: ${data.message}`, 'error');
            }
        } catch (error) {
            this.showNotification('Erro de conexão ao parar bot', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async generateSignal() {
        try {
            this.showLoading(true);
            
            const assetSelect = document.getElementById('assetSelect');
            const timeframeSelect = document.getElementById('timeframeSelect');
            const confidenceSlider = document.getElementById('confidenceSlider');
            
            const selectedAsset = assetSelect ? assetSelect.value : 'BTCUSDT';
            const selectedTimeframe = timeframeSelect ? timeframeSelect.value : '1h';
            const minConfidence = confidenceSlider ? confidenceSlider.value : 70;
            
            this.showNotification(`Gerando sinal para ${selectedAsset} (${selectedTimeframe})...`, 'info');
            
            const response = await fetch('/api/generate_signal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: selectedAsset,
                    timeframe: selectedTimeframe,
                    min_confidence: minConfidence / 100
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`Sinal gerado para ${selectedAsset}!`, 'success');
                this.loadSignals();
                this.displayNewSignal(data.signal);
            } else {
                this.showNotification(`Erro ao gerar sinal: ${data.message}`, 'error');
            }
        } catch (error) {
            this.showNotification('Erro de conexão ao gerar sinal', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async generateTestSignal() {
        try {
            this.showNotification('Gerando sinal de teste...', 'info');
            
            const response = await fetch('/api/generate_test_signal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`✅ Sinal de teste gerado: ${data.signal.signal_type.toUpperCase()} ${data.signal.symbol} - Confiança: ${(data.signal.confidence * 100).toFixed(1)}%`, 'success');
                
                // Reload signals if we're on the signals section
                if (this.currentSection === 'signals' || this.currentSection === 'dashboard') {
                    setTimeout(() => {
                        this.loadSectionData(this.currentSection);
                    }, 1000);
                }
            } else {
                this.showNotification(`❌ Erro ao gerar sinal de teste: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Erro de conexão ao gerar sinal de teste', 'error');
        }
    }

    async generateRealSignal() {
        try {
            this.showNotification('Gerando sinal real com dados de mercado...', 'info');
            
            const response = await fetch('/api/generate_signal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: 'BTCUSDT',
                    timeframe: '1h'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`🎯 Sinal real gerado: ${data.signal.signal_type.toUpperCase()} ${data.signal.symbol} - Confiança: ${(data.signal.confidence * 100).toFixed(1)}%`, 'success');
                
                // Reload signals if we're on the signals section
                if (this.currentSection === 'signals' || this.currentSection === 'dashboard') {
                    setTimeout(() => {
                        this.loadSectionData(this.currentSection);
                    }, 1000);
                }
            } else {
                this.showNotification(`⚠️ ${data.message || 'Nenhum sinal gerado no momento'}`, 'warning');
            }
        } catch (error) {
            this.showNotification('Erro de conexão ao gerar sinal real', 'error');
        }
    }

    // Asset Selection Functions
    updateCurrentAsset(asset) {
        const assetDisplay = asset.replace('USDT', '/USDT').replace('USD', '/USD');
        const currentAssetElement = document.getElementById('currentAsset');
        if (currentAssetElement) {
            currentAssetElement.textContent = assetDisplay;
        }
        this.showNotification(`Ativo alterado para ${assetDisplay}`, 'info');
    }

    updateTimeframe(timeframe) {
        this.showNotification(`Timeframe alterado para ${timeframe}`, 'info');
    }

    updateConfidence(confidence) {
        const confidenceValueElement = document.getElementById('confidenceValue');
        if (confidenceValueElement) {
            confidenceValueElement.textContent = `${confidence}%`;
        }
    }

    // Display New Signal with Details
    displayNewSignal(signal) {
        if (!signal) return;
        
        const signalHtml = `
            <div class="alert alert-info alert-dismissible fade show" role="alert">
                <h6><i class="fas fa-bullhorn me-2"></i>Novo Sinal Gerado!</h6>
                <div class="row">
                    <div class="col-md-6">
                        <strong>Ativo:</strong> ${signal.symbol || 'N/A'}<br>
                        <strong>Tipo:</strong> <span class="badge bg-${signal.signal_type === 'BUY' ? 'success' : signal.signal_type === 'SELL' ? 'danger' : 'warning'}">${signal.signal_type || 'HOLD'}</span><br>
                        <strong>Confiança:</strong> ${signal.confidence ? (signal.confidence * 100).toFixed(1) : 'N/A'}%
                    </div>
                    <div class="col-md-6">
                        <strong>Entrada:</strong> $${signal.entry_price || 'N/A'}<br>
                        <strong>Stop Loss:</strong> $${signal.stop_loss || 'N/A'}<br>
                        <strong>Take Profit:</strong> $${signal.take_profit || 'N/A'}
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('#dashboard-section .container-fluid');
        if (container) {
            container.insertAdjacentHTML('afterbegin', signalHtml);
        }
    }

    // Data Loading
    async loadInitialData() {
        await Promise.all([
            this.loadBotStatus(),
            this.loadDashboardStats(),
            this.loadRecentSignals()
        ]);
    }

    async loadBotStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            this.updateBotStatus(data.status);
        } catch (error) {
            console.error('Erro ao carregar status do bot:', error);
        }
    }

    async loadDashboardStats() {
        try {
            const response = await fetch('/api/stats');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.updateDashboardStats(data);
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
            // Use dados simulados se a API falhar
            this.updateDashboardStats({
                total_pnl: 0,
                active_signals: 0,
                open_positions: 0,
                win_rate: 0
            });
        }
    }

    async loadRecentSignals() {
        try {
            const response = await fetch('/api/signals?limit=5');
            const data = await response.json();
            this.displayRecentSignals(data.signals || []);
        } catch (error) {
            console.error('Erro ao carregar sinais recentes:', error);
        }
    }

    async loadSignals() {
        try {
            const response = await fetch('/api/signals');
            const data = await response.json();
            this.displaySignalsTable(data.signals || []);
        } catch (error) {
            console.error('Erro ao carregar sinais:', error);
        }
    }

    async loadPositions() {
        try {
            const response = await fetch('/api/positions');
            const data = await response.json();
            this.displayPositionsTable(data.positions || []);
        } catch (error) {
            console.error('Erro ao carregar posições:', error);
        }
    }

    async loadPerformanceData() {
        try {
            const response = await fetch('/api/performance');
            const data = await response.json();
            this.updatePerformanceCharts(data);
        } catch (error) {
            console.error('Erro ao carregar dados de performance:', error);
        }
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.populateSettings(data.settings || {});
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
            // Carregar configurações padrão
            this.populateSettings({
                risk_per_trade: 2,
                max_drawdown: 20,
                max_daily_loss: 10,
                primary_timeframe: '1h',
                min_confidence: 70,
                max_positions: 5
            });
        }
    }

    async saveSettings() {
        try {
            const settings = {
                risk_per_trade: parseFloat(document.getElementById('riskPerTrade').value),
                max_drawdown: parseFloat(document.getElementById('maxDrawdown').value),
                max_daily_loss: parseFloat(document.getElementById('maxDailyLoss').value),
                primary_timeframe: document.getElementById('primaryTimeframe').value,
                min_confidence: parseFloat(document.getElementById('minConfidence').value),
                max_positions: parseInt(document.getElementById('maxPositions').value)
            };

            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ settings })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                this.showNotification('Configurações salvas com sucesso', 'success');
            } else {
                this.showNotification(`Erro ao salvar: ${data.message}`, 'error');
            }
        } catch (error) {
            console.error('Erro ao salvar configurações:', error);
            this.showNotification('Erro ao salvar configurações', 'error');
        }
    }

    populateSettings(settings) {
        document.getElementById('riskPerTrade').value = settings.risk_per_trade || 2;
        document.getElementById('maxDrawdown').value = settings.max_drawdown || 20;
        document.getElementById('maxDailyLoss').value = settings.max_daily_loss || 10;
        document.getElementById('primaryTimeframe').value = settings.primary_timeframe || '1h';
        document.getElementById('minConfidence').value = settings.min_confidence || 70;
        document.getElementById('maxPositions').value = settings.max_positions || 5;
    }

    // UI Updates
    updateBotStatus(status) {
        const statusIndicator = document.getElementById('botStatus');
        const statusText = document.getElementById('botStatusText');
        
        statusIndicator.className = 'status-indicator';
        
        if (status === 'running') {
            statusIndicator.classList.add('status-running');
            statusText.textContent = 'Executando';
        } else {
            statusIndicator.classList.add('status-stopped');
            statusText.textContent = 'Parado';
        }
    }

    updateDashboardStats(stats) {
        document.getElementById('totalPnl').textContent = this.formatCurrency(stats.total_pnl || 0);
        document.getElementById('activeSignals').textContent = stats.active_signals || 0;
        document.getElementById('openPositions').textContent = stats.open_positions || 0;
        document.getElementById('winRate').textContent = this.formatPercentage(stats.win_rate || 0);
    }

    displayRecentSignals(signals) {
        const container = document.getElementById('recentSignals');
        
        if (signals.length === 0) {
            container.innerHTML = '<div class="text-center text-muted">Nenhum sinal recente</div>';
            return;
        }

        container.innerHTML = signals.map(signal => `
            <div class="signal-card card mb-2 ${signal.signal_type}">
                <div class="card-body py-2">
                    <div class="row align-items-center">
                        <div class="col-md-2">
                            <strong>${signal.symbol}</strong>
                        </div>
                        <div class="col-md-2">
                            <span class="badge badge-custom bg-${this.getSignalColor(signal.signal_type)}">
                                ${signal.signal_type.toUpperCase()}
                            </span>
                        </div>
                        <div class="col-md-2">
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: ${signal.confidence}%"></div>
                            </div>
                            <small>${signal.confidence}%</small>
                        </div>
                        <div class="col-md-2">
                            $${signal.entry_price}
                        </div>
                        <div class="col-md-2">
                            ${signal.timeframe}
                        </div>
                        <div class="col-md-2">
                            <small class="text-muted">${this.formatDate(signal.timestamp)}</small>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    displaySignalsTable(signals) {
        const tbody = document.getElementById('signalsTable');
        
        if (signals.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">Nenhum sinal encontrado</td></tr>';
            return;
        }

        tbody.innerHTML = signals.map(signal => `
            <tr>
                <td><strong>${signal.symbol}</strong></td>
                <td>
                    <span class="badge badge-custom bg-${this.getSignalColor(signal.signal_type)}">
                        ${signal.signal_type.toUpperCase()}
                    </span>
                </td>
                <td>
                    <div class="confidence-bar mb-1">
                        <div class="confidence-fill" style="width: ${signal.confidence}%"></div>
                    </div>
                    ${signal.confidence}%
                </td>
                <td>$${signal.entry_price}</td>
                <td>$${signal.stop_loss}</td>
                <td>$${signal.take_profit}</td>
                <td>${signal.timeframe}</td>
                <td>
                    <span class="badge badge-custom bg-${this.getStatusColor(signal.status)}">
                        ${signal.status}
                    </span>
                </td>
                <td>${this.formatDate(signal.timestamp)}</td>
            </tr>
        `).join('');
    }

    displayPositionsTable(positions) {
        const tbody = document.getElementById('positionsTable');
        
        if (positions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">Nenhuma posição encontrada</td></tr>';
            return;
        }

        tbody.innerHTML = positions.map(position => `
            <tr>
                <td><strong>${position.symbol}</strong></td>
                <td>
                    <span class="badge badge-custom bg-${position.side === 'buy' ? 'success' : 'danger'}">
                        ${position.side.toUpperCase()}
                    </span>
                </td>
                <td>${position.size}</td>
                <td>$${position.entry_price}</td>
                <td>$${position.current_price || 'N/A'}</td>
                <td class="${position.unrealized_pnl >= 0 ? 'text-success' : 'text-danger'}">
                    ${this.formatCurrency(position.unrealized_pnl || 0)}
                </td>
                <td>
                    <span class="badge badge-custom bg-${this.getStatusColor(position.status)}">
                        ${position.status}
                    </span>
                </td>
                <td>${this.formatDate(position.open_time)}</td>
            </tr>
        `).join('');
    }

    // Charts
    initializeCharts() {
        this.initEquityChart();
        this.initSignalsChart();
        this.initPerformanceChart();
    }

    initEquityChart() {
        const ctx = document.getElementById('equityChart').getContext('2d');
        this.charts.equity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Equity',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    initSignalsChart() {
        const ctx = document.getElementById('signalsChart').getContext('2d');
        this.charts.signals = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Buy', 'Sell', 'Hold'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#27ae60', '#e74c3c', '#f39c12']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initPerformanceChart() {
        const ctx = document.getElementById('performanceChart').getContext('2d');
        this.charts.performance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'PnL Diário',
                    data: [],
                    backgroundColor: function(context) {
                        const value = context.parsed && context.parsed.y !== undefined ? context.parsed.y : 0;
                        return value >= 0 ? '#27ae60' : '#e74c3c';
                    }
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    updatePerformanceCharts(data) {
        // Update equity chart
        if (data.equity_curve) {
            this.charts.equity.data.labels = data.equity_curve.dates;
            this.charts.equity.data.datasets[0].data = data.equity_curve.values;
            this.charts.equity.update();
        }

        // Update signals distribution
        if (data.signal_distribution) {
            this.charts.signals.data.datasets[0].data = [
                data.signal_distribution.buy || 0,
                data.signal_distribution.sell || 0,
                data.signal_distribution.hold || 0
            ];
            this.charts.signals.update();
        }

        // Update performance chart
        if (data.daily_pnl) {
            this.charts.performance.data.labels = data.daily_pnl.dates;
            this.charts.performance.data.datasets[0].data = data.daily_pnl.values;
            this.charts.performance.update();
        }

        // Update performance stats
        if (data.stats) {
            this.displayPerformanceStats(data.stats);
        }
    }

    displayPerformanceStats(stats) {
        const container = document.getElementById('performanceStats');
        container.innerHTML = `
            <div class="row">
                <div class="col-6 mb-3">
                    <div class="text-center">
                        <h6 class="text-muted">Sharpe Ratio</h6>
                        <h4>${(stats.sharpe_ratio || 0).toFixed(2)}</h4>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <div class="text-center">
                        <h6 class="text-muted">Sortino Ratio</h6>
                        <h4>${(stats.sortino_ratio || 0).toFixed(2)}</h4>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <div class="text-center">
                        <h6 class="text-muted">Max Drawdown</h6>
                        <h4 class="text-danger">${this.formatPercentage(stats.max_drawdown || 0)}</h4>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <div class="text-center">
                        <h6 class="text-muted">Profit Factor</h6>
                        <h4>${(stats.profit_factor || 0).toFixed(2)}</h4>
                    </div>
                </div>
                <div class="col-12">
                    <div class="text-center">
                        <h6 class="text-muted">Total de Trades</h6>
                        <h4>${stats.total_trades || 0}</h4>
                    </div>
                </div>
            </div>
        `;
    }

    // Settings
    populateSettings(settings) {
        document.getElementById('riskPerTrade').value = settings.risk_per_trade || 2;
        document.getElementById('maxDrawdown').value = settings.max_drawdown || 20;
        document.getElementById('maxDailyLoss').value = settings.max_daily_loss || 10;
        document.getElementById('primaryTimeframe').value = settings.primary_timeframe || '1h';
        
        // Set min confidence slider value and update display
        const minConfidenceValue = (settings.min_confidence || 5);
        const slider = document.getElementById('minConfidence');
        const display = document.getElementById('minConfidenceValue');
        if (slider && display) {
            slider.value = minConfidenceValue;
            display.textContent = minConfidenceValue;
        }
        
        document.getElementById('maxPositions').value = settings.max_positions || 5;
    }

    setupConfidenceSlider() {
        const slider = document.getElementById('minConfidence');
        const display = document.getElementById('minConfidenceValue');
        
        if (slider && display) {
            slider.addEventListener('input', (e) => {
                display.textContent = e.target.value;
            });
        }
    }

    async saveSettings() {
        const settings = {
            risk_per_trade: parseFloat(document.getElementById('riskPerTrade').value),
            max_drawdown: parseFloat(document.getElementById('maxDrawdown').value),
            max_daily_loss: parseFloat(document.getElementById('maxDailyLoss').value),
            primary_timeframe: document.getElementById('primaryTimeframe').value,
            min_confidence: parseFloat(document.getElementById('minConfidence').value),
            max_positions: parseInt(document.getElementById('maxPositions').value)
        };

        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`Configurações salvas! Confiança mínima: ${settings.min_confidence}%`, 'success');
                
                // Reload current section to apply new settings
                if (this.currentSection === 'signals' || this.currentSection === 'dashboard') {
                    setTimeout(() => {
                        this.loadSectionData(this.currentSection);
                    }, 1000);
                }
            } else {
                this.showNotification('Erro ao salvar configurações', 'error');
            }
        } catch (error) {
            this.showNotification('Erro de conexão ao salvar configurações', 'error');
        }
    }

    // Socket Event Handlers
    handleNewSignal(signal) {
        console.log('Novo sinal recebido:', signal);
        
        // Show detailed notification
        const confidence = typeof signal.confidence === 'number' ? 
            (signal.confidence * 100).toFixed(1) : 
            (parseFloat(signal.confidence) * 100).toFixed(1);
            
        const signalType = signal.signal_type.toUpperCase();
        const symbol = signal.symbol;
        
        this.showNotification(
            `🎯 NOVO SINAL: ${signalType} ${symbol} | Confiança: ${confidence}% | Preço: $${signal.entry_price}`, 
            'success'
        );
        
        // Auto-refresh current section
        if (this.currentSection === 'dashboard') {
            this.loadRecentSignals();
            this.loadDashboardStats();
        } else if (this.currentSection === 'signals') {
            this.loadSignals();
        }
    }

    handlePositionUpdate(position) {
        if (this.currentSection === 'positions') {
            this.loadPositions();
        }
        
        this.loadDashboardStats();
    }

    updatePerformanceData(data) {
        this.updateDashboardStats(data);
        
        if (this.currentSection === 'performance') {
            this.updatePerformanceCharts(data);
        }
    }

    // Utility Functions
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'USD'
        }).format(value);
    }

    formatPercentage(value) {
        return `${value.toFixed(2)}%`;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    }

    getSignalColor(signalType) {
        const colors = {
            'buy': 'success',
            'sell': 'danger',
            'hold': 'warning'
        };
        return colors[signalType] || 'secondary';
    }

    getStatusColor(status) {
        const colors = {
            'active': 'primary',
            'executed': 'success',
            'cancelled': 'secondary',
            'open': 'info',
            'closed': 'success'
        };
        return colors[status] || 'secondary';
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        const id = 'notification-' + Date.now();
        
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';

        const notification = document.createElement('div');
        notification.id = id;
        notification.className = `alert ${alertClass} alert-dismissible fade show notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            const element = document.getElementById(id);
            if (element) {
                element.remove();
            }
        }, 5000);
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'block' : 'none';
    }

    // Periodic Updates
    startPeriodicUpdates() {
        this.updateInterval = setInterval(() => {
            if (this.isConnected && !document.hidden) {
                this.loadDashboardStats();
                
                if (this.currentSection === 'dashboard') {
                    this.loadRecentSignals();
                }
            }
        }, 30000); // Update every 30 seconds
    }

    pauseUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }

    resumeUpdates() {
        this.startPeriodicUpdates();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new TradingBotDashboard();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.pauseUpdates();
    }
});