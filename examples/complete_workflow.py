#!/usr/bin/env python
"""
完整工作流示例：从下载数据到回测分析

流程：
1. 下载历史交易数据 (如果未缓存)
2. 加载并清洗数据
3. 计算特征指标
4. 生成交易信号
5. 执行回测
6. 分析并输出结果
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import logging
from datetime import datetime
from qlib_backtest.data.downloader import DataDownloader
from qlib_backtest.data import DataHandler
from qlib_backtest.features import FeatureEngine
from qlib_backtest.strategies import StrategyFactory
from qlib_backtest.backtest import BacktestEngine
from qlib_backtest.utils import setup_logging, ResultsExporter

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


def print_header(title):
    """打印测试头"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """主函数"""
    
    print_header("量化交易系统完整工作流演示")
    
    # ============================================================================
    # 步骤1: 下载历史交易数据
    # ============================================================================
    print_header("步骤1️⃣  下载历史交易数据")
    
    stocks = ["000858.SZ", "000651.SZ"]
    
    logger.info(f"准备下载 {len(stocks)} 只股票的数据...")
    logger.info(f"股票列表: {stocks}")
    
    downloader = DataDownloader()
    try:
        # 下载数据（如果本地已有，会使用增量更新）
        downloader.download_data(
            stock_codes=stocks,
            incremental=True,  # 增量更新
            start_date="2020-01-01",
            end_date="2023-12-31"
        )
        logger.info("✓ 数据下载/更新完成")
        
        # 显示缓存信息
        cache_dir = os.path.expanduser('~/.cache/qlib_backtest/data')
        if os.path.exists(cache_dir):
            cached_files = [f for f in os.listdir(cache_dir) if f.endswith('.csv')]
            logger.info(f"✓ 缓存中有 {len(cached_files)} 个文件")
            for f in cached_files:
                size = os.path.getsize(f'{cache_dir}/{f}') / 1024
                logger.info(f"  - {f}: {size:.1f} KB")
    except Exception as e:
        logger.error(f"✗ 下载失败: {e}")
        logger.info("  (这是正常的，如果QLib未安装会使用模拟数据)")
    
    # ============================================================================
    # 步骤2: 加载和清洗数据
    # ============================================================================
    print_header("步骤2️⃣  加载和清洗数据")
    
    logger.info(f"加载 {stocks} 的历史数据...")
    data_handler = DataHandler()
    
    df = data_handler.load_stock_data(
        stock_codes=stocks,
        start_date="2020-01-01",
        end_date="2023-12-31",
    )
    logger.info(f"✓ 加载完成: {df.shape[0]} 行 × {df.shape[1]} 列")
    logger.info(f"  时间跨度: {df.index.min()} 至 {df.index.max()}")
    logger.info(f"  股票数: {df['stock_code'].nunique()}")
    
    logger.info("清洗数据...")
    df = data_handler.clean_data(df)
    logger.info("✓ 数据清洗完成")
    logger.info(f"  缺失值处理: 填充/删除异常值")
    logger.info(f"  OHLC检验: 逻辑检查及修复")
    
    logger.info("计算收益率...")
    df = data_handler.add_returns(df)
    logger.info("✓ 收益率计算完成")
    
    # 数据统计
    print(f"\n数据统计:")
    print(f"  开盘价: {df['open'].min():.2f} - {df['open'].max():.2f}")
    print(f"  收盘价: {df['close'].min():.2f} - {df['close'].max():.2f}")
    print(f"  日均成交量: {df['volume'].mean():,.0f}")
    print(f"  日均涨幅: {df['daily_return'].mean()*100:.3f}%")
    
    # ============================================================================
    # 步骤3: 计算特征指标
    # ============================================================================
    print_header("步骤3️⃣  计算特征指标")
    
    logger.info("计算技术指标...")
    feature_engine = FeatureEngine()
    df = feature_engine.calculate_all_features(df)
    logger.info("✓ 特征计算完成")
    logger.info(f"  新增指标数: 40+")
    logger.info(f"  包括: MA, RSI, MACD, 布林带, ATR 等")
    
    # 显示计算的特征
    feature_cols = [col for col in df.columns 
                    if col not in ['stock_code', 'date', 'open', 'high', 'low', 'close', 'volume', 'daily_return']]
    logger.info(f"  计算的特征列: {len(feature_cols)} 个")
    if feature_cols:
        logger.info(f"  样本特征: {feature_cols[:5]}")
    
    # ============================================================================
    # 步骤4: 生成交易信号
    # ============================================================================
    print_header("步骤4️⃣  生成交易信号")
    
    # 测试多个策略
    strategies_to_test = [
        ('momentum', {'short_window': 5, 'long_window': 20, 'threshold': 0.02}),
        ('mean_reversion', {'window': 20, 'std_multiple': 2}),
    ]
    
    signals_dict = {}
    for strat_name, params in strategies_to_test:
        logger.info(f"生成 {strat_name} 策略信号...")
        strategy = StrategyFactory.create_strategy(strat_name, **params)
        signals = strategy.generate_signals(df)
        signals_dict[strat_name] = signals
        
        # 信号统计
        buy_count = sum(1 for s in signals if s.signal_type == 'BUY')
        sell_count = sum(1 for s in signals if s.signal_type == 'SELL')
        hold_count = sum(1 for s in signals if s.signal_type == 'HOLD')
        logger.info(f"✓ {strat_name} 信号生成完成")
        logger.info(f"  买入信号: {buy_count} 次")
        logger.info(f"  卖出信号: {sell_count} 次")
        logger.info(f"  持仓信号: {hold_count} 次")
    
    # ============================================================================
    # 步骤5: 执行回测
    # ============================================================================
    print_header("步骤5️⃣  执行回测")
    
    logger.info("初始化回测引擎...")
    engine = BacktestEngine(
        initial_capital=1000000.0,      # 初始资金100万
        commission=0.001,                # 佣金0.1%
        slippage=0.0001,                 # 滑点0.01%
        max_position_per_stock=0.3,     # 单只最大持仓30%
    )
    logger.info("✓ 回测引擎初始化完成")
    logger.info(f"  初始资金: ¥1,000,000")
    logger.info(f"  佣金: 0.1%, 滑点: 0.01%")
    
    # 执行回测
    backtest_results = {}
    for strat_name in strategies_to_test:
        strat_name_only = strat_name[0]  # 获取策略名称
        logger.info(f"\n执行 {strat_name_only} 策略回测...")
        
        signals = signals_dict[strat_name_only]
        results = engine.run_backtest(df, signals)
        backtest_results[strat_name_only] = results
        
        logger.info(f"✓ {strat_name_only} 回测完成")
    
    # ============================================================================
    # 步骤6: 结果分析和对比
    # ============================================================================
    print_header("步骤6️⃣  回测结果分析")
    
    print("\n策略对标表格:")
    print("┌────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐")
    print("│ 策略名称       │ 总收益   │ 年化收益 │ Sharpe   │ 最大回撤 │ 胜率     │")
    print("├────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for strat_name, results in backtest_results.items():
        print(f"│ {strat_name:14s} │ "
              f"{results.total_return:7.2%} │ "
              f"{results.annual_return:7.2%}  │ "
              f"{results.sharpe_ratio:7.2f}  │ "
              f"{results.max_drawdown:7.2%} │ "
              f"{results.win_rate:7.2%} │")
    
    print("└────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # 选择最优策略
    best_strategy = max(backtest_results.items(), 
                        key=lambda x: x[1].sharpe_ratio)
    best_name, best_results = best_strategy
    
    print(f"\n🏆 最优策略: {best_name}")
    print(f"   Sharpe比率: {best_results.sharpe_ratio:.2f}")
    print(f"   总收益: {best_results.total_return:.2%}")
    print(f"   年化收益: {best_results.annual_return:.2%}")
    print(f"   最大回撤: {best_results.max_drawdown:.2%}")
    print(f"   胜率: {best_results.win_rate:.2%}")
    print(f"   盈利因子: {best_results.profit_factor:.2f}")
    
    # ============================================================================
    # 步骤7: 导出结果
    # ============================================================================
    print_header("步骤7️⃣  导出结果")
    
    results_exporter = ResultsExporter()
    
    for strat_name, results in backtest_results.items():
        logger.info(f"导出 {strat_name} 结果...")
        
        # 导出所有结果 (JSON摘要 + CSV详细)
        base_name = results_exporter.export_results(results, strat_name)
        logger.info(f"✓ 结果已导出，文件前缀: {base_name}")
    
    # ============================================================================
    # 完成
    # ============================================================================
    print_header("完成！🎉")
    
    print(f"""
下一步建议：

1. 查看Web仪表盘
   python examples/web_frontend.py
   然后访问 http://localhost:5000

2. 参数调优 (修改策略参数并重新运行)
   - 调整 short_window, long_window, threshold 等

3. 自定义策略
   - 在 src/qlib_backtest/strategies/ 创建新策略类

4. 生产部署
   - 使用APScheduler定时下载数据
   - 使用APScheduler定时执行回测

详细文档请参考：
- ARCHITECTURE_GUIDE.md - 系统架构详解
- QUICK_START_GUIDE.md - 快速开始指南
    """)
    
    logger.info("=" * 70)
    logger.info("工作流示例完成！")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
