"""
简单快速入门脚本：最小化示例展示如何使用数据定期下载功能
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.qlib_backtest.data.downloader import DataDownloader, DataUpdateManager
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ============================================================================
# 方法1: 最简单 - 单次下载
# ============================================================================
def demo_simple_download():
    """最简单的使用方式"""
    print("\n[示例1] 最简单的单次下载")
    print("-" * 50)
    
    downloader = DataDownloader()
    
    # 一行代码下载数据
    results = downloader.download_data(
        stock_codes="000858.SZ",  # 五粮液
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    
    for code, df in results.items():
        print(f"✓ 成功下载 {code}: {len(df)} 条记录")
        print(f"  最后一条: {df.iloc[-1][['date', 'close']]}")


# ============================================================================
# 方法2: 智能增量更新
# ============================================================================
def demo_incremental_update():
    """自动从上次下载日期继续更新"""
    print("\n[示例2] 智能增量更新（自动检测上次日期）")
    print("-" * 50)
    
    downloader = DataDownloader()
    stocks = ["000858.SZ", "000651.SZ"]
    
    # 无需指定开始日期，自动从上次日期继续
    results = downloader.download_data(
        stock_codes=stocks,
        incremental=True  # 关键：启用增量更新
    )
    
    for code, df in results.items():
        print(f"✓ {code}: {len(df)} 条记录")


# ============================================================================
# 方法3: 定时自动下载 (后台运行)
# ============================================================================
def demo_scheduled_download():
    """最实用的方式：定时自动下载"""
    print("\n[示例3] 定时自动下载（后台运行）")
    print("-" * 50)
    
    downloader = DataDownloader()
    
    # 配置要监控的股票
    stocks = ["000858.SZ", "000651.SZ", "600519.SH"]
    
    # 启动定时任务（每个工作日下午4点更新）
    downloader.start_scheduler(
        stock_codes=stocks,
        cron_expression="0 16 * * 1-5",  # 工作日下午4点
        incremental=True  # 启用增量更新
    )
    
    print(f"✓ 定时下载已启动")
    print(f"  监控 {len(stocks)} 只股票")
    print(f"  执行时间: 每个工作日下午4点")
    print(f"  更新方式: 增量更新（自动检测新数据）")
    
    # 检查运行状态
    import time
    time.sleep(2)
    
    status = downloader.get_download_status()
    stats = downloader.get_download_statistics()
    
    print(f"\n运行状态:")
    print(f"  活跃: {status['running']}")
    print(f"  监控股票: {len(status.get('recent_downloads', []))}")
    if stats:
        print(f"  历史下载: {stats.get('total_downloads', 0)} 次")
        print(f"  成功率: {stats.get('successful', 0)}/{stats.get('total_downloads', 0)}")
    
    # 手动停止
    # downloader.stop_scheduler()
    # print("✓ 已停止")


# ============================================================================
# 方法4: 使用更新管理器（推荐用于管理多个股票）
# ============================================================================
def demo_update_manager():
    """推荐：使用管理器管理多个股票"""
    print("\n[示例4] 使用管理器（推荐）")
    print("-" * 50)
    
    downloader = DataDownloader()
    manager = DataUpdateManager(downloader)
    
    # 配置监控列表
    manager.add_stocks(["000858.SZ", "000651.SZ"])
    manager.add_stocks("600519.SH")
    
    print(f"监控列表: {manager.get_watch_list()}")
    
    # 启动监控
    manager.start_monitoring(cron_expression="0 16 * * 1-5")
    
    print("✓ 监控已启动")
    
    # 手动触发更新
    print("\n执行手动更新...")
    results = manager.manual_update()
    
    for code, df in results.items():
        if df is not None:
            print(f"  ✓ {code}: {len(df)} 条记录")
    
    # 停止监控
    # manager.stop_monitoring()


# ============================================================================
# 方法5: 查看下载统计
# ============================================================================
def demo_check_statistics():
    """查看下载统计和历史"""
    print("\n[示例5] 查看下载统计")
    print("-" * 50)
    
    downloader = DataDownloader()
    
    # 获取统计信息
    stats = downloader.get_download_statistics()
    
    if stats:
        print("下载统计:")
        print(f"  监控的股票数: {stats.get('unique_stocks', 0)}")
        print(f"  总下载次数: {stats.get('total_downloads', 0)}")
        print(f"  成功次数: {stats.get('successful', 0)}")
        print(f"  失败次数: {stats.get('failed', 0)}")
        print(f"  平均下载时间: {stats.get('avg_duration_seconds', 0):.1f} 秒")
        print(f"  最后下载: {stats.get('last_download', 'N/A')}")
    else:
        print("暂无下载记录")


# ============================================================================
# 实用建议
# ============================================================================
def print_tips():
    """打印实用建议"""
    print("\n" + "="*60)
    print("💡 实用建议")
    print("="*60)
    
    print("""
1. 首次使用 - 选择方法3或方法4（定时自动下载）
   - 这样可以让数据在后台自动更新
   - 无需人工干预

2. Cron表达式选择
   - 工作日4点: "0 16 * * 1-5"   (股市收盘后)
   - 每天9点: "0 9 * * *"        (市场开盘前)
   - 每时一次: "0 * * * *"       (全天每小时)

3. 增量更新 (incremental=True)
   - 大大加速更新速度
   - 推荐始终启用

4. 监控哪些股票
   - 优先选择跟踪的策略股票
   - 不需要监控所有股票

5. 错误处理
   - 所有操作都有日志记录
   - 查看 ~/.cache/qlib_backtest/download_history.db
   - 出错会自动重试
    """)


# ============================================================================
# 主程序
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("QLib 数据定期下载 - 快速入门")
    print("="*60)
    
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        if example == "1":
            demo_simple_download()
        elif example == "2":
            demo_incremental_update()
        elif example == "3":
            demo_scheduled_download()
        elif example == "4":
            demo_update_manager()
        elif example == "5":
            demo_check_statistics()
        else:
            print(f"未知的示例: {example}")
    else:
        print("\n请选择要运行的示例:")
        print("\n  python quick_data_download.py 1  - 单次下载")
        print("  python quick_data_download.py 2  - 增量更新")
        print("  python quick_data_download.py 3  - 定时下载 (推荐)")
        print("  python quick_data_download.py 4  - 使用管理器")
        print("  python quick_data_download.py 5  - 查看统计")
        
        print("\n或者运行所有示例:")
        
        try:
            demo_simple_download()
            demo_incremental_update()
            # demo_scheduled_download()  # 注释掉以免后台运行
            # demo_update_manager()
            demo_check_statistics()
            print_tips()
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            print("\n可能需要:")
            print("  - pip install apscheduler")
            print("  - pip install qlib")
