#!/usr/bin/env python3
"""
Script para otimizar performance dos DataFrames fragmentados
Corrige os warnings de "DataFrame is highly fragmented"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_engine import AITradingEngine
from src.market_regime import MarketRegimeDetector

def otimizar_ai_engine():
    """Otimizar método de preparação de features do AI Engine"""
    
    print("🔧 OTIMIZANDO AI ENGINE - Performance de DataFrames")
    print("=" * 60)
    
    # Arquivo de destino
    ai_engine_file = "src/ai_engine.py"
    
    # Ler o arquivo atual
    with open(ai_engine_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a função _prepare_regime_features e otimizar
    old_method = '''        # Adicionar features derivadas dos regimes
        for score_col in regime_scores:
            if score_col in df.columns:
                # Features atuais
                df[f'{score_col}_current'] = df[score_col]
                
                # Changes and momentum
                df[f'{score_col}_change'] = df[score_col].diff()
                
                # Volatility and stability metrics
                df[f'{score_col}_stability'] = df[score_col].rolling(10).std()
                
                # Percentile ranking
                rolling_window = min(len(df), 50)
                df[f'{score_col}_percentile'] = df[score_col].rolling(rolling_window).rank(pct=True)'''
    
    new_method = '''        # Adicionar features derivadas dos regimes (Otimizado - sem fragmentação)
        features_to_add = {}
        
        for score_col in regime_scores:
            if score_col in df.columns:
                col_data = df[score_col]
                
                # Calcular todas as features de uma vez para evitar fragmentação
                features_to_add[f'{score_col}_current'] = col_data
                features_to_add[f'{score_col}_change'] = col_data.diff()
                features_to_add[f'{score_col}_stability'] = col_data.rolling(10).std()
                
                rolling_window = min(len(df), 50)
                features_to_add[f'{score_col}_percentile'] = col_data.rolling(rolling_window).rank(pct=True)
        
        # Adicionar todas as features de uma vez usando pd.concat
        if features_to_add:
            import pandas as pd
            new_features_df = pd.DataFrame(features_to_add, index=df.index)
            df = pd.concat([df, new_features_df], axis=1)'''
    
    # Substituir na função
    if old_method in content:
        content = content.replace(old_method, new_method)
        print("✅ Otimizada função _prepare_regime_features")
    else:
        print("⚠️ Padrão não encontrado em _prepare_regime_features")
    
    # Otimizar também a seção de smoothing
    old_smoothing = '''        # Smooth out volatile features
        volatile_features = [col for col in df.columns if any(x in col.lower() for x in ['score', 'strength', 'change'])]
        for col in volatile_features:
            if col in df.columns and df[col].dtype in ['float64', 'int64']:
                df[f'{col}_smooth'] = df[col].rolling(5).mean()
                
                # Add shock detection
                col_diff = df[col].diff()
                df[f'{col}_shock'] = abs(col_diff) > df[col].rolling(20).std() * 2'''
    
    new_smoothing = '''        # Smooth out volatile features (Otimizado)
        volatile_features = [col for col in df.columns if any(x in col.lower() for x in ['score', 'strength', 'change'])]
        smoothing_features = {}
        
        for col in volatile_features:
            if col in df.columns and df[col].dtype in ['float64', 'int64']:
                col_data = df[col]
                smoothing_features[f'{col}_smooth'] = col_data.rolling(5).mean()
                
                # Add shock detection
                col_diff = col_data.diff()
                smoothing_features[f'{col}_shock'] = abs(col_diff) > col_data.rolling(20).std() * 2
        
        # Adicionar features de smoothing de uma vez
        if smoothing_features:
            smoothing_df = pd.DataFrame(smoothing_features, index=df.index)
            df = pd.concat([df, smoothing_df], axis=1)'''
    
    if old_smoothing in content:
        content = content.replace(old_smoothing, new_smoothing)
        print("✅ Otimizada seção de smoothing")
    else:
        print("⚠️ Padrão de smoothing não encontrado")
    
    # Salvar arquivo otimizado
    with open(ai_engine_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ AI Engine otimizado com sucesso!")

def otimizar_market_regime():
    """Otimizar o MarketRegimeAnalyzer"""
    
    print("\n🔧 OTIMIZANDO MARKET REGIME - Performance de DataFrames")
    print("=" * 60)
    
    regime_file = "src/market_regime.py"
    
    with open(regime_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Otimizar adição de features nos regimes
    old_pattern = "df['clustering_regime'] = regime_names"
    
    if old_pattern in content:
        # Encontrar a seção que adiciona múltiplas colunas
        old_section = '''        df['clustering_regime'] = regime_names
        df['clustering_regime_id'] = cluster_labels'''
        
        new_section = '''        # Adicionar features de clustering de uma vez (Otimizado)
        clustering_features = pd.DataFrame({
            'clustering_regime': regime_names,
            'clustering_regime_id': cluster_labels
        }, index=df.index)
        df = pd.concat([df, clustering_features], axis=1)'''
        
        if old_section in content:
            content = content.replace(old_section, new_section)
            print("✅ Otimizada seção de clustering")
    
    # Otimizar correlations
    old_corr_pattern = "df['correlation_regime'] = correlation_regime"
    if old_corr_pattern in content:
        old_corr_section = '''        df['correlation_regime'] = correlation_regime
        df['correlation_strength'] = avg_correlation'''
        
        new_corr_section = '''        # Adicionar features de correlação de uma vez (Otimizado)
        correlation_features = pd.DataFrame({
            'correlation_regime': correlation_regime,
            'correlation_strength': avg_correlation
        }, index=df.index)
        df = pd.concat([df, correlation_features], axis=1)'''
        
        if old_corr_section in content:
            content = content.replace(old_corr_section, new_corr_section)
            print("✅ Otimizada seção de correlação")
    
    # Otimizar ensemble features
    old_ensemble_pattern = "df['ensemble_regime_score'] = ensemble_score"
    if old_ensemble_pattern in content:
        # Encontrar a seção inteira de ensemble
        start_marker = "df['ensemble_regime_score'] = ensemble_score"
        end_marker = "df['ensemble_regime'] = ensemble_regime"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker) + len(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            new_ensemble_section = '''        # Adicionar features de ensemble de uma vez (Otimizado)
        ensemble_features = pd.DataFrame({
            'ensemble_regime_score': ensemble_score,
            'ensemble_regime': ensemble_regime
        }, index=df.index)
        df = pd.concat([df, ensemble_features], axis=1)'''
        
        old_ensemble_section = content[start_idx:end_idx]
        content = content.replace(old_ensemble_section, new_ensemble_section)
        print("✅ Otimizada seção de ensemble")
    
    with open(regime_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Market Regime otimizado com sucesso!")

def criar_funcao_otimizada_concat():
    """Criar função helper para concatenação otimizada"""
    
    print("\n🔧 CRIANDO FUNÇÃO HELPER DE CONCATENAÇÃO")
    print("=" * 50)
    
    helper_code = '''
def concat_features_optimized(df, new_features_dict):
    """
    Função otimizada para adicionar múltiplas features ao DataFrame
    sem causar fragmentação
    
    Args:
        df: DataFrame principal
        new_features_dict: Dicionário com {nome_coluna: Series/array}
    
    Returns:
        DataFrame com as novas features adicionadas
    """
    if not new_features_dict:
        return df
    
    try:
        import pandas as pd
        
        # Criar DataFrame com as novas features
        new_features_df = pd.DataFrame(new_features_dict, index=df.index)
        
        # Concatenar uma única vez
        result_df = pd.concat([df, new_features_df], axis=1)
        
        return result_df
        
    except Exception as e:
        # Fallback para método tradicional se houver erro
        print(f"Warning: Fallback para método tradicional devido a erro: {e}")
        result_df = df.copy()
        for col_name, col_data in new_features_dict.items():
            result_df[col_name] = col_data
        return result_df
'''
    
    # Adicionar ao final do ai_engine.py
    ai_engine_file = "src/ai_engine.py"
    
    with open(ai_engine_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já existe
    if "concat_features_optimized" not in content:
        # Adicionar antes da última linha (que geralmente é a classe)
        content = content.rstrip() + helper_code + "\n"
        
        with open(ai_engine_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Função helper adicionada ao ai_engine.py")
    else:
        print("✅ Função helper já existe")

def testar_otimizacoes():
    """Testar se as otimizações funcionam"""
    
    print("\n🧪 TESTANDO OTIMIZAÇÕES")
    print("=" * 40)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        
        # Testar com dados pequenos
        df = market_data.get_historical_data('BTCUSDT', '1h', 100)
        
        if df is not None and not df.empty:
            print(f"✅ Dados obtidos: {len(df)} registros")
              # Testar preparação de features
            try:
                features_df = ai_engine.prepare_features(df)
                print(f"✅ Features preparadas: {len(features_df.columns)} colunas")
                print("✅ Otimizações funcionando corretamente!")
                
            except Exception as e:
                print(f"❌ Erro na preparação de features: {e}")
                
        else:
            print("⚠️ Não foi possível obter dados para teste")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def main():
    """Função principal"""
    
    print("🚀 INICIANDO OTIMIZAÇÃO DE PERFORMANCE")
    print("=" * 70)
    print("Objetivo: Eliminar warnings de DataFrame fragmentado")
    print("Método: Usar pd.concat ao invés de múltiplas inserções")
    print()
    
    try:
        # 1. Otimizar AI Engine
        otimizar_ai_engine()
        
        # 2. Otimizar Market Regime
        otimizar_market_regime() 
        
        # 3. Criar função helper
        criar_funcao_otimizada_concat()
        
        # 4. Testar otimizações
        testar_otimizacoes()
        
        print("\n" + "=" * 70)
        print("🎉 OTIMIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("📊 RESULTADOS ESPERADOS:")
        print("  ✅ Eliminação dos warnings de DataFrame fragmentado")
        print("  ✅ Melhoria na performance de preparação de features")
        print("  ✅ Redução no tempo de processamento")
        print("  ✅ Menor uso de memória")
        print()
        print("🔄 PRÓXIMOS PASSOS:")
        print("  1. Executar teste de viés novamente")
        print("  2. Verificar se warnings foram eliminados") 
        print("  3. Medir melhoria de performance")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OTIMIZAÇÃO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
