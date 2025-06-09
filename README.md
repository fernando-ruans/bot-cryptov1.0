# Trading Bot AI - Crypto & Forex

🤖 **Bot de Trading Inteligente para Criptomoedas e Forex**

Um sistema avançado de trading automatizado que utiliza Inteligência Artificial e Machine Learning para gerar sinais de compra e venda precisos para criptomoedas e pares de forex.

## 🚀 Características Principais

### 🧠 Inteligência Artificial
- **Machine Learning Avançado**: Utiliza XGBoost, LightGBM, Random Forest e Redes Neurais
- **Ensemble Learning**: Combina múltiplos modelos para maior precisão
- **Análise Preditiva**: Previsão de movimentos de preço baseada em padrões históricos
- **Auto-aprendizado**: Modelos se adaptam continuamente aos dados de mercado

### 📊 Análise Técnica Completa
- **40+ Indicadores Técnicos**: RSI, MACD, Bollinger Bands, ATR, ADX, etc.
- **Análise de Volume**: VWAP, OBV, MFI, Volume Profile
- **Padrões de Candlestick**: Detecção automática de padrões de reversão
- **Análise Multi-timeframe**: Confirmação de sinais em diferentes períodos

### 🎯 Geração de Sinais Inteligente
- **Sinais de Alta Precisão**: Combinação de IA e análise técnica
- **Níveis de Confiança**: Cada sinal possui score de confiabilidade
- **Stop Loss e Take Profit**: Cálculo automático baseado em volatilidade
- **Contexto de Mercado**: Considera tendência, volatilidade e sessões

### 🛡️ Gestão de Risco Avançada
- **Position Sizing**: Cálculo automático baseado no risco por trade
- **Controle de Drawdown**: Proteção contra perdas excessivas
- **Correlação de Ativos**: Evita exposição excessiva a ativos correlacionados
- **Limites Dinâmicos**: Ajuste automático baseado na performance

### 📈 Dashboard Interativo
- **Interface Web Moderna**: Dashboard responsivo e intuitivo
- **Gráficos em Tempo Real**: Visualização de performance e sinais
- **Monitoramento Live**: Acompanhamento de posições e PnL
- **Notificações**: Alertas em tempo real via WebSocket

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.8+**: Linguagem principal
- **Flask**: Framework web
- **Socket.IO**: Comunicação em tempo real
- **SQLite**: Banco de dados
- **Pandas/NumPy**: Análise de dados
- **Scikit-learn**: Machine Learning
- **XGBoost/LightGBM**: Gradient Boosting
- **TensorFlow**: Deep Learning (opcional)

### Frontend
- **HTML5/CSS3**: Interface moderna
- **JavaScript ES6+**: Funcionalidades interativas
- **Bootstrap 5**: Framework CSS
- **Chart.js**: Gráficos interativos
- **Font Awesome**: Ícones

### APIs e Dados
- **Binance API**: Dados de criptomoedas
- **Alpha Vantage**: Dados de forex
- **CCXT**: Biblioteca unificada de exchanges

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta na Binance (para criptomoedas)
- Chave API da Alpha Vantage (para forex)
- 4GB RAM mínimo
- Conexão estável com a internet

## 🔧 Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/bot-cryptov1.0.git
cd bot-cryptov1.0
```

### 2. Crie um Ambiente Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
# Binance API (para criptomoedas)
BINANCE_API_KEY=sua_api_key_aqui
BINANCE_SECRET_KEY=sua_secret_key_aqui

# Alpha Vantage API (para forex)
ALPHA_VANTAGE_API_KEY=sua_api_key_aqui

# Configurações do Bot
RISK_PER_TRADE=2.0
MAX_POSITIONS=5
MIN_CONFIDENCE=70

# Notificações (opcional)
WEBHOOK_URL=sua_webhook_url_aqui
```

### 5. Inicialize o Banco de Dados
```bash
python -c "from src.database import DatabaseManager; db = DatabaseManager(); db.initialize()"
```

## 🚀 Como Usar

### 1. Inicie o Bot
```bash
python main.py
```

### 2. Acesse o Dashboard
Abra seu navegador e vá para: `http://localhost:5000`

### 3. Configure o Bot
1. Acesse a seção "Configurações" no dashboard
2. Ajuste os parâmetros de risco conforme sua estratégia
3. Selecione os pares de trading desejados
4. Salve as configurações

### 4. Inicie o Trading
1. Clique em "Iniciar Bot" no dashboard
2. Monitore os sinais gerados em tempo real
3. Acompanhe a performance na seção "Performance"

## 📊 Estrutura do Projeto

```
bot-cryptov1.0/
├── src/
│   ├── ai_engine.py          # Motor de IA e ML
│   ├── config.py             # Configurações
│   ├── database.py           # Gerenciamento do banco
│   ├── market_data.py        # Dados de mercado
│   ├── risk_manager.py       # Gestão de risco
│   ├── signal_generator.py   # Geração de sinais
│   ├── technical_indicators.py # Indicadores técnicos
│   └── utils.py              # Utilitários
├── templates/
│   └── index.html            # Interface web
├── static/
│   └── js/
│       └── dashboard.js      # JavaScript do dashboard
├── data/                     # Dados e modelos
├── models/                   # Modelos treinados
├── logs/                     # Logs do sistema
├── main.py                   # Arquivo principal
├── requirements.txt          # Dependências
└── README.md                 # Este arquivo
```

## ⚙️ Configurações Avançadas

### Parâmetros de Risco
- **RISK_PER_TRADE**: Percentual do capital por trade (1-10%)
- **MAX_DAILY_LOSS**: Perda máxima diária (5-20%)
- **MAX_DRAWDOWN**: Drawdown máximo permitido (10-30%)
- **MAX_POSITIONS**: Número máximo de posições simultâneas

### Configurações de IA
- **AI_RETRAIN_INTERVAL**: Intervalo de retreinamento (horas)
- **MIN_CONFIDENCE**: Confiança mínima para sinais (50-95%)
- **ENSEMBLE_WEIGHTS**: Pesos dos modelos no ensemble

### Indicadores Técnicos
- **RSI_PERIOD**: Período do RSI (14)
- **MACD_FAST**: Período rápido do MACD (12)
- **MACD_SLOW**: Período lento do MACD (26)
- **BB_PERIOD**: Período das Bollinger Bands (20)

## 📈 Estratégias de Trading

### 1. Scalping (1-5 minutos)
- Foco em movimentos rápidos
- Alta frequência de trades
- Stop loss apertado

### 2. Day Trading (15 minutos - 1 hora)
- Trades intraday
- Análise de tendências de curto prazo
- Gestão ativa de posições

### 3. Swing Trading (4 horas - 1 dia)
- Trades de médio prazo
- Aproveitamento de correções
- Maior tolerância a volatilidade

## 🔍 Monitoramento e Logs

### Logs do Sistema
- **INFO**: Operações normais
- **WARNING**: Situações de atenção
- **ERROR**: Erros que precisam correção
- **DEBUG**: Informações detalhadas

### Métricas de Performance
- **Sharpe Ratio**: Retorno ajustado ao risco
- **Sortino Ratio**: Retorno ajustado ao downside
- **Max Drawdown**: Maior perda consecutiva
- **Win Rate**: Taxa de acerto
- **Profit Factor**: Relação lucro/prejuízo

## 🚨 Avisos Importantes

⚠️ **AVISO DE RISCO**: Trading envolve risco significativo de perda. Nunca invista mais do que pode perder.

⚠️ **TESTE PRIMEIRO**: Sempre teste em conta demo antes de usar capital real.

⚠️ **MONITORAMENTO**: Mantenha supervisão constante do bot, especialmente no início.

⚠️ **BACKUP**: Faça backup regular das configurações e dados.

## 🛠️ Solução de Problemas

### Problemas Comuns

**1. Erro de Conexão com API**
- Verifique suas chaves de API
- Confirme se as permissões estão corretas
- Teste a conectividade de rede

**2. Bot Não Gera Sinais**
- Verifique se há dados suficientes
- Confirme as configurações de confiança mínima
- Verifique os logs para erros

**3. Performance Baixa**
- Ajuste os parâmetros de IA
- Considere retreinar os modelos
- Revise a estratégia de risco

### Logs e Debug
```bash
# Visualizar logs em tempo real
tail -f logs/trading_bot.log

# Verificar status do banco
python -c "from src.database import DatabaseManager; db = DatabaseManager(); print(db.get_database_stats())"
```

## 🔄 Atualizações e Manutenção

### Backup Regular
```bash
# Backup do banco de dados
cp data/trading_bot.db backups/trading_bot_$(date +%Y%m%d).db

# Backup dos modelos
cp -r models/ backups/models_$(date +%Y%m%d)/
```

### Limpeza de Dados
```bash
# Limpar dados antigos (90+ dias)
python -c "from src.database import DatabaseManager; db = DatabaseManager(); db.cleanup_old_data(90)"
```

## 📞 Suporte

Para suporte técnico:
- 📧 Email: suporte@tradingbot.com
- 💬 Discord: [Link do servidor]
- 📖 Documentação: [Link da wiki]
- 🐛 Issues: [Link do GitHub Issues]

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📊 Roadmap

### Versão 2.0
- [ ] Suporte a mais exchanges
- [ ] Trading de opções
- [ ] Análise de sentimento
- [ ] Mobile app

### Versão 2.1
- [ ] Copy trading
- [ ] Estratégias customizáveis
- [ ] Backtesting avançado
- [ ] API pública

---

**Desenvolvido com ❤️ para a comunidade de traders**

*Lembre-se: O sucesso no trading requer disciplina, gestão de risco e aprendizado contínuo. Este bot é uma ferramenta para auxiliar suas decisões, não uma garantia de lucro.*