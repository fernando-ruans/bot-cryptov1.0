from src.config import Config
from src.market_data import MarketDataManager
from src.technical_indicators import TechnicalIndicators

print("Iniciando...")
config = Config()
market_data = MarketDataManager(config)
df = market_data.get_historical_data('BTCUSDT', '1h', 100)
print(f"Dados: {len(df)} registros")

tech = TechnicalIndicators(config)
print("TechnicalIndicators criado com sucesso")

# Calcular indicadores
print("Calculando indicadores...")
df_with_indicators = tech.calculate_all_indicators(df)
print(f"Indicadores calculados. Colunas: {len(df_with_indicators.columns)}")

# Verificar força dos sinais
print("Calculando força dos sinais...")
signal_strength = tech.get_signal_strength(df_with_indicators)
print(f"Força dos sinais: {signal_strength}")

print("Concluído.")
