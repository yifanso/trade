#!/usr/bin/env python
"""
基础回测示例：使用MomentumStrategy进行回测
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import logging
from qlib_backtest.data import DataHandler
from qlib_backtest.features import FeatureEngine
from qlib_backtest.strategies import StrategyFactory
from qlib_backtest.backtest import BacktestEngine
from qlib_backtest.utils import setup_logging, ResultsExporter

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    
    logger.info("=" * 60)
    logger.info("开始执行Momentum策略回测")
    logger.info("=" * 60)
    
    # 1. 加载数据
    logger.info("\n[第1步] 加载数据")
    data_handler = DataHandler()
    
    stocks = ["000001.SZ", "000858.SZ", "600000.SH"]
    df = data_handler.load_stock_data(
        stock_codes=stocks,
        start_date="2020-01-01",
        end_date="2023-12-31",
    )
    
    # 2. 清洗数据
    logger.info("\n[第2步] 清洗数据")
    df = data_handler.clean_data(df)
    df = data_handler.add_returns(df)
    
    # 3. 特征工程
    logger.info("\n[第3步] 生成特征")
    feature_engine = FeatureEngine()
    df = feature_engine.calculate_all_features(df)
    
    # 4. 生成交易信号
    logger.info("\n[第4步] 生成交易信号")
    strategy = StrategyFactory.create_strategy(
        'momentum',
        short_window=5,
        long_window=20,
        threshold=0.02,
    )
    signals = strategy.generate_signals(df)
    
    # 5. 执行回测
    logger.info("\n[第5步] 执行回测")
    backtest_engine = BacktestEngine(
        initial_capital=1000000.0,
        commission=0.001,
        slippage=0.0001,
    )
    results = backtest_engine.run_backtest(df, signals)
    
    # 6. 输出结果
    logger.info("\n[第6步] 输出结果")
    logger.info("\n" + "=" * 60)
    logger.info("回测结果汇总")
    logger.info("=" * 60)
    for key, value in results.to_dict().items():
        logger.info(f"{key:20s}: {value}")
    
    # 输出交易记录
    logger.info(f"\n交易记录数: {len(results.trades)}")
    if results.trades:
        logger.info("前5条交易:")
        for trade in results.trades[:5]:
            logger.info(f"  {trade}")
    
    # 导出结果
    logger.info("\n[第7步] 导出结果")
    exporter = ResultsExporter("./results")
    exporter.export_results(results, "momentum_strategy")
    
    logger.info("\n回测完成！")


if __name__ == "__main__":
    main()
