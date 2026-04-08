#!/usr/bin/env python
"""
参数优化示例：使用网格搜索优化策略参数
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import logging
from itertools import product
import pandas as pd
from qlib_backtest.data import DataHandler
from qlib_backtest.features import FeatureEngine
from qlib_backtest.strategies import MomentumStrategy
from qlib_backtest.backtest import BacktestEngine
from qlib_backtest.utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def optimize_strategy():
    """
    使用网格搜索优化Momentum策略参数
    """
    
    logger.info("=" * 60)
    logger.info("参数优化：网格搜索")
    logger.info("=" * 60)
    
    # 1. 加载和准备数据
    logger.info("\n[步骤1] 加载数据")
    data_handler = DataHandler()
    df = data_handler.load_stock_data(
        stock_codes=["000001.SZ"],
        start_date="2020-01-01",
        end_date="2023-12-31",
    )
    
    df = data_handler.clean_data(df)
    df = data_handler.add_returns(df)
    
    logger.info("\n[步骤2] 特征工程")
    feature_engine = FeatureEngine()
    df = feature_engine.calculate_all_features(df)
    
    # 2. 定义参数网格
    logger.info("\n[步骤3] 定义参数网格")
    param_grid = {
        'short_window': [5, 10],
        'long_window': [15, 20, 30],
        'threshold': [0.01, 0.02, 0.03],
    }
    
    # 3. 网格搜索
    logger.info("\n[步骤4] 执行网格搜索")
    results_list = []
    
    # 生成所有参数组合
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    
    total_combinations = 1
    for values in param_values:
        total_combinations *= len(values)
    
    logger.info(f"总参数组合数: {total_combinations}")
    
    backtest_engine = BacktestEngine(initial_capital=1000000.0)
    
    for i, params in enumerate(product(*param_values)):
        param_dict = dict(zip(param_names, params))
        
        logger.info(f"\n[{i+1}/{total_combinations}] 测试参数: {param_dict}")
        
        try:
            # 创建策略
            strategy = MomentumStrategy()
            strategy.set_parameters(**param_dict)
            
            # 生成信号
            signals = strategy.generate_signals(df)
            
            # 执行回测
            results = backtest_engine.run_backtest(df, signals)
            
            # 保存结果
            result_row = param_dict.copy()
            result_row.update({
                'total_return': results.total_return,
                'sharpe_ratio': results.sharpe_ratio,
                'max_drawdown': results.max_drawdown,
                'win_rate': results.win_rate,
            })
            results_list.append(result_row)
            
            logger.info(f"  Total Return: {results.total_return:.2%}")
            logger.info(f"  Sharpe Ratio: {results.sharpe_ratio:.2f}")
            
        except Exception as e:
            logger.error(f"  参数优化失败: {str(e)}")
    
    # 4. 分析结果
    logger.info("\n[步骤5] 分析优化结果")
    
    if results_list:
        results_df = pd.DataFrame(results_list)
        
        # 按Sharpe比率排序
        results_df = results_df.sort_values('sharpe_ratio', ascending=False)
        
        logger.info("\n" + "=" * 60)
        logger.info("前5个最佳参数组合")
        logger.info("=" * 60)
        
        for idx, row in results_df.head().iterrows():
            logger.info(f"\n参数:")
            for col in param_names:
                logger.info(f"  {col}: {row[col]}")
            logger.info(f"性能:")
            logger.info(f"  Total Return: {row['total_return']:.2%}")
            logger.info(f"  Sharpe Ratio: {row['sharpe_ratio']:.2f}")
            logger.info(f"  Max Drawdown: {row['max_drawdown']:.2%}")
            logger.info(f"  Win Rate: {row['win_rate']:.2%}")
        
        # 保存结果到CSV
        results_df.to_csv('./results/optimization_results.csv', index=False)
        logger.info(f"\n结果已保存到: ./results/optimization_results.csv")
        
        return results_df
    else:
        logger.error("没有有效的优化结果")
        return None


def compare_strategies():
    """
    对比不同策略在相同数据上的表现
    """
    
    logger.info("\n" + "=" * 60)
    logger.info("策略对比")
    logger.info("=" * 60)
    
    # 加载数据
    data_handler = DataHandler()
    df = data_handler.load_stock_data(
        stock_codes=["000001.SZ"],
        start_date="2021-01-01",
        end_date="2023-12-31",
    )
    
    df = data_handler.clean_data(df)
    df = data_handler.add_returns(df)
    
    feature_engine = FeatureEngine()
    df = feature_engine.calculate_all_features(df)
    
    # 测试参数集合
    test_configs = [
        {
            'name': 'Conservative',
            'short_window': 10,
            'long_window': 30,
            'threshold': 0.01,
        },
        {
            'name': 'Moderate',
            'short_window': 5,
            'long_window': 20,
            'threshold': 0.02,
        },
        {
            'name': 'Aggressive',
            'short_window': 3,
            'long_window': 10,
            'threshold': 0.03,
        },
    ]
    
    comparison_results = []
    backtest_engine = BacktestEngine(initial_capital=1000000.0)
    
    for config in test_configs:
        strategy_name = config.pop('name')
        
        logger.info(f"\n测试策略: {strategy_name}")
        logger.info(f"参数: {config}")
        
        strategy = MomentumStrategy()
        strategy.set_parameters(**config)
        signals = strategy.generate_signals(df)
        results = backtest_engine.run_backtest(df, signals)
        
        comparison_results.append({
            'strategy': strategy_name,
            'total_return': results.total_return,
            'annual_return': results.annual_return,
            'sharpe_ratio': results.sharpe_ratio,
            'max_drawdown': results.max_drawdown,
            'win_rate': results.win_rate,
            'profit_factor': results.profit_factor,
        })
    
    # 结果表格
    comparison_df = pd.DataFrame(comparison_results)
    
    logger.info("\n" + "=" * 60)
    logger.info("策略对比结果")
    logger.info("=" * 60)
    logger.info("\n" + comparison_df.to_string(index=False))
    
    comparison_df.to_csv('./results/strategy_comparison.csv', index=False)
    
    return comparison_df


if __name__ == "__main__":
    # 执行参数优化
    optimization_results = optimize_strategy()
    
    # 执行策略对比
    comparison_results = compare_strategies()
    
    logger.info("\n优化完成！")
