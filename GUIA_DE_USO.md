# 🚀 Guia de Uso - Trading Bot AI

## 📋 Visão Geral

Este Trading Bot AI é uma aplicação completa para análise de mercado e geração de sinais de trading. **IMPORTANTE: Esta aplicação NÃO executa trades automaticamente, apenas gera sinais com pontos de entrada, stop loss e take profit.**

## 🎯 Funcionalidades Principais

### ✅ Geração de Sinais
- **Sinais BUY/SELL** com base em análise técnica e IA
- **Pontos de entrada** precisos
- **Stop Loss** calculado automaticamente
- **Take Profit** otimizado
- **Nível de confiança** para cada sinal

### 📊 Análise Técnica
- **Indicadores de Momentum**: RSI, MACD, Stochastic
- **Indicadores de Tendência**: Médias Móveis, ADX
- **Indicadores de Volatilidade**: Bollinger Bands, ATR
- **Indicadores de Volume**: OBV, MFI, VWAP

### 🧠 Inteligência Artificial
- **Machine Learning** para previsão de movimentos
- **Análise de padrões** históricos
- **Otimização automática** de parâmetros

## 🔧 Configuração Inicial

### 1. Configurar APIs (Opcional)

Copie o arquivo `.env.example` para `.env` e configure suas chaves de API:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas chaves:

```env
# Binance API (para dados de criptomoedas)
BINANCE_API_KEY=sua_chave_aqui
BINANCE_SECRET_KEY=sua_chave_secreta_aqui

# Alpha Vantage API (para dados de forex)
ALPHA_VANTAGE_API_KEY=sua_chave_aqui
```

**Nota**: As APIs são opcionais. O bot pode funcionar com dados simulados para demonstração.

### 2. Iniciar a Aplicação

```bash
python main.py
```

A aplicação estará disponível em: **http://localhost:5000**

## 🖥️ Interface Web

### Dashboard Principal
- **Visão geral** dos sinais ativos
- **Estatísticas** de performance
- **Gráficos** em tempo real
- **Alertas** e notificações

### Seções Disponíveis

#### 📈 Sinais
- Lista de sinais gerados
- Filtros por símbolo, tipo e confiança
- Detalhes completos de cada sinal

#### 📊 Análise
- Gráficos interativos
- Indicadores técnicos sobrepostos
- Análise de múltiplos timeframes

#### ⚙️ Configurações
- Parâmetros de risco
- Configuração de indicadores
- Preferências de notificação

## 📋 Como Interpretar os Sinais

### Estrutura de um Sinal

```json
{
  "symbol": "BTCUSDT",
  "signal_type": "BUY",
  "confidence": 85,
  "entry_price": 50000.00,
  "stop_loss": 48000.00,
  "take_profit": 54000.00,
  "timeframe": "1h",
  "reasons": [
    "RSI oversold",
    "MACD bullish crossover",
    "Price above MA20"
  ]
}
```

### Níveis de Confiança
- **90-100%**: Sinal muito forte
- **80-89%**: Sinal forte
- **70-79%**: Sinal moderado
- **60-69%**: Sinal fraco
- **<60%**: Não recomendado

### Gestão de Risco
- **Risk/Reward**: Sempre calculado automaticamente
- **Position Size**: Baseado no risco configurado
- **Stop Loss**: Nunca deve ser ignorado
- **Take Profit**: Pode ser ajustado conforme estratégia

## 🔍 Monitoramento

### Logs do Sistema
Os logs são salvos em `logs/trading_bot.log` e incluem:
- Sinais gerados
- Erros e avisos
- Performance do sistema
- Conexões de API

### Base de Dados
Todos os dados são armazenados em `data/trading_bot.db`:
- Histórico de sinais
- Dados de mercado
- Estatísticas de performance
- Configurações do usuário

## ⚠️ Avisos Importantes

### 🚫 NÃO É UM ROBÔ DE TRADING AUTOMÁTICO
- Esta aplicação **NÃO executa trades**
- Você deve **analisar cada sinal** antes de agir
- **Sempre faça sua própria pesquisa**
- **Nunca invista mais do que pode perder**

### 📊 Dados de Mercado
- Dados podem ter atraso
- Verifique sempre em múltiplas fontes
- Considere condições de mercado atuais

### 🔒 Segurança
- **NUNCA compartilhe** suas chaves de API
- Use apenas em redes seguras
- Mantenha o software atualizado

## 🛠️ Solução de Problemas

### Aplicação não inicia
```bash
# Verificar dependências
python test_components.py

# Reinstalar dependências
pip install -r requirements.txt
```

### Sem dados de mercado
- Verificar conexão com internet
- Verificar chaves de API
- Verificar logs em `logs/trading_bot.log`

### Performance lenta
- Reduzir número de símbolos monitorados
- Aumentar intervalo de atualização
- Verificar recursos do sistema

## 📞 Suporte

Para problemas técnicos:
1. Verificar logs em `logs/trading_bot.log`
2. Executar `python test_components.py`
3. Verificar configurações em `.env`

## 📈 Próximos Passos

1. **Configure suas APIs** para dados reais
2. **Ajuste os parâmetros** conforme sua estratégia
3. **Monitore os sinais** gerados
4. **Analise a performance** regularmente
5. **Refine sua estratégia** com base nos resultados

---

**Lembre-se**: Este é um sistema de apoio à decisão. A responsabilidade final pelas decisões de trading é sempre sua!