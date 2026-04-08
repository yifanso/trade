#!/usr/bin/env python
"""
快速验证脚本：测试项目各个模块的基本功能
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """测试模块导入"""
    logger.info("=" * 60)
    logger.info("测试1: 模块导入")
    logger.info("=" * 60)
    
    try:
        from qlib_backtest.data import DataHandler
        logger.info("✓ DataHandler 导入成功")
    except Exception as e:
        logger.error(f"✗ DataHandler 导入失败: {e}")
        return False
    
    try:
        from qlib_backtest.features import FeatureEngine
        logger.info("✓ FeatureEngine 导入成功")
    except Exception as e:
        logger.error(f"✗ FeatureEngine 导入失败: {e}")
        return False
    
    try:
        from qlib_backtest.strategies import StrategyFactory
        logger.info("✓ StrategyFactory 导入成功")
    except Exception as e:
        logger.error(f"✗ StrategyFactory 导入失败: {e}")
        return False
    
    try:
        from qlib_backtest.backtest import BacktestEngine
        logger.info("✓ BacktestEngine 导入成功")
    except Exception as e:
        logger.error(f"✗ BacktestEngine 导入失败: {e}")
        return False
    
    return True


def test_data_handler():
    """测试数据处理"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 数据处理")
    logger.info("=" * 60)
    
    try:
        from qlib_backtest.data import DataHandler
        
        handler = DataHandler()
        df = handler.load_stock_data(
            stock_codes=["000001.SZ"],
            start_date="2023-01-01",
            end_date="2023-12-31",
        )
        
        logger.info(f"✓ 成功加载 {len(df)} 行数据")
        logger.info(f"  列数: {df.shape[1]}")
        logger.info(f"  列名: {list(df.columns)[:5]}...")
        
        # 测试数据清洗
        df = handler.clean_data(df)
        logger.info(f"✓ 数据清洗完成")
        
        # 测试添加收益率
        df = handler.add_returns(df)
        logger.info(f"✓ 添加收益率完成")
        
        return True, df
        
    except Exception as e:
        logger.error(f"✗ 数据处理失败: {e}")
        return False, None


def test_feature_engine(df):
    """测试特征工程"""
    if df is None or df.empty:
        logger.error("✗ 没有有效的数据用于特征工程")
        return False, None
    
    logger.info("\n" + "=" * 60)
    logger.info("测试3: 特征工程")
    logger.info("=" * 60)
    
    try:
        from qlib_backtest.features import FeatureEngine
        
        engine = FeatureEngine()
        
        # 计算特征（使用最小配置以加快速度）
        df = engine.calculate_all_features(
            df,
            feature_config={
                'trend': {'windows': [10, 20]},
            }
        )
        
        logger.info(f"✓ 特征计算完成")
        logger.info(f"  新增列数: {df.shape[1]}")
        
        return True, df
        
    except Exception as e:
        logger.error(f"✗ 特征工程失败: {e}")
        return False, None


def test_strategies(df):
    """测试策略"""
    if df is None or df.empty:
        logger.error("✗ 没有有效的数据用于策略")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("测试4: 策略框架")
    logger.info("=" * 60)
    
    try:
        from qlib_backtest.strategies import StrategyFactory
        
        # 测试工厂创建策略
        strategy = StrategyFactory.create_strategy('momentum')
        logger.info(f"✓ 创建 momentum 策略")
        
        # 生成信号
        signals = strategy.generate_signals(df)
        logger.info(f"✓ 生成 {len(signals)} 条交易信号")
        
        if signals:
            sample = signals[0]
            logger.info(f"  示例信号: {sample.date} {sample.stock_code} {sample.signal_type}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 策略框架失败: {e}")
        return False


def test_backtest(df):
    """测试回测引擎"""
    if df is None or df.empty:
        logger.error("✗ 没有有效的数据用于回测")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("测试5: 回测引擎")
    logger.info("=" * 60)
    
    try:
        from qlib_backtest.strategies import StrategyFactory
        from qlib_backtest.backtest import BacktestEngine
        
        # 创建策略和信号
        strategy = StrategyFactory.create_strategy('momentum')
        signals = strategy.generate_signals(df)
        
        # 创建回测引擎
        engine = BacktestEngine(initial_capital=1000000.0)
        
        # 运行回测
        results = engine.run_backtest(df, signals)
        
        logger.info(f"✓ 回测执行完成")
        logger.info(f"  总收益率: {results.total_return:.2%}")
        logger.info(f"  Sharpe比率: {results.sharpe_ratio:.2f}")
        logger.info(f"  最大回撤: {results.max_drawdown:.2%}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 回测引擎失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    
    logger.info("\n" + "=" * 60)
    logger.info("QLib量化回测框架 - 功能验证")
    logger.info("=" * 60)
    
    # 测试导入
    if not test_imports():
        logger.error("\n模块导入失败，请检查安装")
        return
    
    # 测试数据处理
    success, df = test_data_handler()
    if not success:
        logger.error("\n数据处理失败")
        return
    
    # 测试特征工程
    success, df = test_feature_engine(df)
    if not success:
        logger.error("\n特征工程失败")
        return
    
    # 测试策略
    if not test_strategies(df):
        logger.error("\n策略框架失败")
        return
    
    # 测试回测
    if not test_backtest(df):
        logger.error("\n回测引擎失败")
        return
    
    # 全部通过
    logger.info("\n" + "=" * 60)
    logger.info("✓ 所有测试通过！")
    logger.info("=" * 60)
    logger.info("\n下一步:")
    logger.info("  1. 运行示例: python examples/basic_backtest.py")
    logger.info("  2. 阅读指南: cat GUIDE.md")
    logger.info("  3. 查看文档: cat README.md")


if __name__ == "__main__":
    main()
