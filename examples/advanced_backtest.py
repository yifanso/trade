#!/usr/bin/env python
"""
高级回测示例：使用组合策略和多个指标
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import logging
from qlib_backtest.data import DataHandler
from qlib_backtest.features import FeatureEngine
from qlib_backtest.strategies import (
    StrategyFactory,
    MomentumStrategy,
    MeanReversionStrategy,
    CombinedStrategy,
)
from qlib_backtest.backtest import BacktestEngine
from qlib_backtest.utils import setup_logging, ResultsExporter, PerformanceAnalyzer
import matplotlib.pyplot as plt

setup_logging()
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    
    logger.info("=" * 60)
    logger.info("高级实例：组合策略回测")
    logger.info("=" * 60)
    
    # 1. 加载数据
    logger.info("\n[步骤1] 加载数据")
    data_handler = DataHandler()
    
    df = data_handler.load_stock_data(
        stock_codes=["000001.SZ", "600000.SH"],
        start_date="2021-01-01",
        end_date="2023-12-31",
    )
    logger.info(f"已加载 {len(df)} 条数据记录")
    
    # 2. 数据预处理
    logger.info("\n[步骤2] 数据预处理")
    df = data_handler.clean_data(df)
    df = data_handler.add_returns(df)
    
    # 3. 特征工程
    logger.info("\n[步骤3] 特征工程")
    feature_engine = FeatureEngine()
    df = feature_engine.calculate_all_features(df)
    
    logger.info(f"生成的特征数: {df.shape[1]}")
    
    # 4. 创建和运行多个策略
    logger.info("\n[步骤4] 生成交易信号")
    
    # 4.1 Momentum策略
    momentum_strategy = MomentumStrategy()
    momentum_strategy.set_parameters(short_window=5, long_window=20, threshold=0.02)
    momentum_signals = momentum_strategy.generate_signals(df)
    
    logger.info(f"Momentum策略生成了 {len(momentum_signals)} 条信号")
    
    # 4.2 Mean Reversion策略
    mean_reversion_strategy = MeanReversionStrategy()
    mean_reversion_strategy.set_parameters(window=20, std_multiple=2)
    mr_signals = mean_reversion_strategy.generate_signals(df)
    
    logger.info(f"Mean Reversion策略生成了 {len(mr_signals)} 条信号")
    
    # 4.3 组合策略
    combined_strategy = CombinedStrategy()
    combined_strategy.add_strategy(momentum_strategy)
    combined_strategy.add_strategy(mean_reversion_strategy)
    combined_strategy.set_parameters(voting_threshold=0.5)
    combined_signals = combined_strategy.generate_signals(df)
    
    logger.info(f"组合策略生成了 {len(combined_signals)} 条信号")
    
    # 5. 执行回测
    logger.info("\n[步骤5] 执行回测")
    
    backtest_engine = BacktestEngine(
        initial_capital=1000000.0,
        commission=0.001,
        slippage=0.0001,
    )
    
    # 运行组合策略回测
    results = backtest_engine.run_backtest(df, combined_signals)
    
    # 6. 分析结果
    logger.info("\n[步骤6] 分析结果")
    logger.info("\n" + "=" * 60)
    logger.info("回测结果对比")
    logger.info("=" * 60)
    
    metrics_dict = results.to_dict()
    for metric, value in metrics_dict.items():
        logger.info(f"{metric:20s}: {value}")
    
    # 7. 性能分析
    logger.info("\n[步骤7] 详细性能分析")
    analyzer = PerformanceAnalyzer()
    detailed_metrics = analyzer.analyze_strategy(results.equity_curve)
    
    logger.info("详细指标:")
    for metric, value in detailed_metrics.items():
        if isinstance(value, float):
            logger.info(f"  {metric:20s}: {value:.4f}")
        else:
            logger.info(f"  {metric:20s}: {value}")
    
    # 8. 导出结果
    logger.info("\n[步骤8] 导出结果")
    exporter = ResultsExporter("./results")
    exporter.export_results(results, "combined_strategy")
    
    # 9. 可视化
    logger.info("\n[步骤9] 绘制图表")
    try:
        plot_results(results)
    except Exception as e:
        logger.warning(f"绘图失败: {e}")
    
    logger.info("\n高级示例完成！")


def plot_results(results):
    """绘制结果图表"""
    if results.equity_curve.empty:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 资金曲线
    ax = axes[0, 0]
    ax.plot(results.equity_curve['total_value'])
    ax.set_title("资金曲线")
    ax.set_ylabel("资产价值")
    ax.grid(True)
    
    # 日收益率
    ax = axes[0, 1]
    returns = results.equity_curve['total_value'].pct_change()
    ax.hist(returns.dropna(), bins=50, edgecolor='black')
    ax.set_title("日收益率分布")
    ax.set_xlabel("收益率")
    ax.grid(True)
    
    # 现金和持仓
    ax = axes[1, 0]
    ax.plot(results.equity_curve['cash'], label='现金')
    ax.plot(results.equity_curve['position_value'], label='持仓价值')
    ax.set_title("现金和持仓价值")
    ax.legend()
    ax.grid(True)
    
    # 累计收益率
    ax = axes[1, 1]
    cumulative_return = (results.equity_curve['total_value'] / results.equity_curve['total_value'].iloc[0] - 1) * 100
    ax.plot(cumulative_return)
    ax.set_title("累计收益率")
    ax.set_ylabel("收益率 (%)")
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('./results/backtest_results.png', dpi=150)
    logger.info("图表已保存到: ./results/backtest_results.png")


if __name__ == "__main__":
    main()
