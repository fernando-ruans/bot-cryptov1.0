# ANÁLISE DE VIÉS - 14 DE JUNHO DE 2025

## Resumo Executivo
Teste realizado às 13:04 com 60 sinais (10 ativos × 6 timeframes) usando EnhancedAIEngine com SignalConfidenceEnhancer ativo.

## Resultados Principais

### Distribuição Geral
- **BUY**: 25 sinais (41.7%)
- **SELL**: 34 sinais (56.7%)
- **HOLD**: 1 sinal (1.7%)

### Análise por Timeframe

| Timeframe | Total | BUY | SELL | HOLD | BUY% | SELL% | HOLD% |
|-----------|-------|-----|------|------|------|-------|-------|
| 1m        | 10    | 6   | 4    | 0    | 60%  | 40%   | 0%    |
| 5m        | 10    | 9   | 1    | 0    | 90%  | 10%   | 0%    |
| 15m       | 10    | 3   | 7    | 0    | 30%  | 70%   | 0%    |
| 1h        | 10    | 1   | 8    | 1    | 10%  | 80%   | 10%   |
| 4h        | 10    | 5   | 5    | 0    | 50%  | 50%   | 0%    |
| 1d        | 10    | 1   | 9    | 0    | 10%  | 90%   | 0%    |

## Problemas Identificados

### 1. Viés Extremo por Timeframe
- **5m**: 90% BUY (viés altista severo)
- **1d**: 90% SELL (viés baixista severo)
- **1h**: 80% SELL (viés baixista alto)
- **15m**: 70% SELL (viés baixista moderado)

### 2. Insuficiência de Sinais HOLD
- Apenas 1.7% dos sinais são HOLD
- Meta: 20-30% para mercados incertos
- Problema: threshold de confiança ainda muito baixo

### 3. Desequilíbrio Geral
- SELL predomina (56.7% vs 41.7% BUY)
- Mercado atual pode estar em tendência baixista, mas o viés por timeframe indica problema algorítmico

## Análise de Confiança por Ativo

### Casos de Baixa Confiança (< 0.4)
- ETHUSDT 4h: 0.311
- BNBUSDT 15m: 0.327
- BNBUSDT 1h: 0.354
- XRPUSDT 5m: 0.351
- XRPUSDT 1d: 0.369
- ADAUSDT 1h: 0.346
- ADAUSDT 4h: 0.333
- ADAUSDT 1d: 0.334
- DOTUSDT 5m: 0.309
- DOTUSDT 1h: 0.341
- DOTUSDT 4h: 0.280
- LINKUSDT 1m: 0.374
- LINKUSDT 1h: 0.351
- LINKUSDT 4h: 0.299
- LTCUSDT 5m: 0.373
- LTCUSDT 4h: 0.294
- MATICUSDT 15m: 0.318
- MATICUSDT 1d: 0.321

### Observações
- 18 de 60 sinais (30%) têm confiança < 0.4
- Destes, apenas 1 foi convertido para HOLD (MATICUSDT 1h)
- **Problema**: threshold de 0.55 ainda muito baixo

## Recomendações de Correção

### 1. Ajuste de Threshold (CRÍTICO)
- Aumentar threshold de confiança para 0.65-0.70
- Forçar HOLD para confiança < 0.65

### 2. Correção de Viés por Timeframe (URGENTE)
- 5m: penalidade -0.3 para sinais BUY
- 1d: penalidade -0.3 para sinais SELL
- 1h: penalidade -0.2 para sinais SELL
- 15m: penalidade -0.15 para sinais SELL

### 3. Reforço da Lógica HOLD
- Consenso técnico < 0.6 → HOLD automático
- Volatilidade > limite → HOLD automático
- Sinais contraditórios entre timeframes → HOLD

### 4. Implementação de Ensemble Temporal
- Considerar consenso entre timeframes adjacentes
- Peso maior para timeframes intermediários (15m, 1h)

## Próximos Passos

1. **Implementar correções agressivas** (threshold 0.65, penalidades maiores)
2. **Teste rápido** com 30 sinais para validação
3. **Teste completo** com 60 sinais após ajustes
4. **Monitoramento** de distribuição em tempo real
5. **Calibração fina** baseada em resultados

## Status
❌ **VIÉS NÃO CORRIGIDO** - Requer intervenção imediata
🔧 **CORREÇÕES NECESSÁRIAS** - Threshold e penalidades insuficientes
📊 **PRÓXIMO TESTE** - Aguardando implementação de ajustes mais agressivos

---
*Relatório gerado em: 14/06/2025 13:20*
*Arquivo: ANALISE_VIES_14_JUNHO_2025.md*
