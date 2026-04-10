"""
数据定期下载示例

演示如何使用DataDownloader实现从QLib定期自动下载更新交易数据

功能演示：
1. 单次下载特定股票数据
2. 启动定时监控任务
3. 查看下载状态和统计信息
4. 手动触发更新
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qlib_backtest.data.downloader import DataDownloader, DataUpdateManager
from qlib_backtest.utils import setup_logging

# 设置日志
logger = setup_logging(log_name="data_download_example")


def example_1_single_download():
    """示例1: 单次下载股票数据"""
    print("\n" + "="*60)
    print("示例1: 单次下载股票数据")
    print("="*60)
    
    downloader = DataDownloader()
    
    # 下载单个股票
    results = downloader.download_data(
        stock_codes="000858.SZ",  # 五粮液
        start_date="2024-01-01",
        end_date="2024-12-31",
        incremental=False,
    )
    
    for code, df in results.items():
        if df is not None:
            print(f"\n股票: {code}")
            print(f"记录数: {len(df)}")
            print(f"日期范围: {df['date'].min()} ~ {df['date'].max()}")
            print(f"\n数据样本（前5行）:")
            print(df.head())


def example_2_incremental_download():
    """示例2: 增量下载数据"""
    print("\n" + "="*60)
    print("示例2: 增量下载数据（智能更新）")
    print("="*60)
    
    downloader = DataDownloader()
    
    # 第一次下载
    print("\n第一次下载...")
    results1 = downloader.download_data(
        stock_codes=["000858.SZ", "000651.SZ"],  # 五粮液、格力电器
        start_date="2024-01-01",
        incremental=False,
    )
    
    for code, df in results1.items():
        print(f"{code}: 下载 {len(df)} 条记录")
    
    # 第二次增量下载（会自动从上次日期继续）
    print("\n增量更新（自动从上次日期继续下载）...")
    results2 = downloader.download_data(
        stock_codes=["000858.SZ", "000651.SZ"],
        incremental=True,  # 启用增量更新
    )
    
    for code, df in results2.items():
        print(f"{code}: 合并后 {len(df)} 条记录")


def example_3_batch_download():
    """示例3: 批量下载多个股票"""
    print("\n" + "="*60)
    print("示例3: 批量下载多个股票")
    print("="*60)
    
    downloader = DataDownloader()
    
    # 热门股票列表
    top_stocks = [
        "000858.SZ",  # 五粮液
        "000651.SZ",  # 格力电器
        "000333.SZ",  # 美的集团
        "600519.SH",  # 贵州茅台
        "600000.SH",  # 浦发银行
    ]
    
    print(f"下载 {len(top_stocks)} 只股票的数据...")
    
    results = downloader.download_data(
        stock_codes=top_stocks,
        start_date="2024-06-01",
        end_date="2024-12-31",
    )
    
    print("\n下载统计:")
    for code, df in results.items():
        if df is not None:
            print(f"  {code}: ✓ {len(df)} 条记录")
        else:
            print(f"  {code}: ✗ 失败")


def example_4_scheduled_download():
    """示例4: 启动定时自动下载"""
    print("\n" + "="*60)
    print("示例4: 启动定时自动下载任务")
    print("="*60)
    
    downloader = DataDownloader()
    
    # 监控的股票列表
    watch_stocks = [
        "000858.SZ",  # 五粮液
        "000651.SZ",  # 格力电器
        "600519.SH",  # 贵州茅台
    ]
    
    print(f"监控股票: {watch_stocks}")
    
    # Cron表达式说明:
    # "0 16 * * 1-5"  - 每个工作日下午4点
    # "0 9 * * *"     - 每天上午9点
    # "*/30 * * * *"  - 每30分钟
    # "0 0 * * *"     - 每天午夜
    
    cron_expr = "0 16 * * 1-5"  # 每个工作日下午4点（股市收盘后）
    
    success = downloader.start_scheduler(
        stock_codes=watch_stocks,
        cron_expression=cron_expr,
        incremental=True,  # 启用增量更新
    )
    
    if success:
        print(f"✓ 定时任务已启动")
        print(f"  Cron表达式: {cron_expr}")
        print(f"  含义: 每个工作日下午4点自动更新数据")
        print(f"\n下载器将在后台运行，按下 Ctrl+C 退出...")
        
        try:
            # 保持程序运行
            import time
            while True:
                # 还可以在这里定期检查状态
                status = downloader.get_download_status()
                stats = downloader.get_download_statistics()
                
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 运行中...")
                print(f"  运行状态: {'活跃' if status['running'] else '已停止'}")
                print(f"  近期成功下载: {len(status.get('recent_downloads', []))}")
                
                if stats:
                    print(f"  总下载次数: {stats.get('total_downloads', 0)}")
                    print(f"  成功: {stats.get('successful', 0)}, 失败: {stats.get('failed', 0)}")
                
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            print("\n\n正在停止下载器...")
            downloader.stop_scheduler()
            print("✓ 下载器已停止")
    else:
        print("✗ 启动定时任务失败")


def example_5_update_manager():
    """示例5: 使用更新管理器"""
    print("\n" + "="*60)
    print("示例5: 使用DataUpdateManager管理多个股票监控")
    print("="*60)
    
    downloader = DataDownloader()
    manager = DataUpdateManager(downloader)
    
    # 添加监控股票
    print("添加监控股票...")
    manager.add_stocks(["000858.SZ", "000651.SZ"])
    print(f"监控列表: {manager.get_watch_list()}")
    
    # 添加更多
    manager.add_stocks("600519.SH")
    print(f"添加后: {manager.get_watch_list()}")
    
    # 启动监控
    print("\n启动监控...")
    manager.start_monitoring(cron_expression="0 16 * * 1-5")
    
    # 手动更新
    print("\n执行手动更新...")
    results = manager.manual_update()
    
    for code, df in results.items():
        if df is not None:
            print(f"  {code}: {len(df)} 条记录")
    
    # 获取统计信息
    print("\n下载统计:")
    stats = downloader.get_download_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 停止监控
    print("\n停止监控...")
    manager.stop_monitoring()


def example_6_custom_schedule():
    """示例6: 自定义调度策略"""
    print("\n" + "="*60)
    print("示例6: 自定义调度策略")
    print("="*60)
    
    downloader = DataDownloader()
    
    print("不同的Cron调度策略:")
    print("\n1. 每个工作日下午4点（股市收盘后）")
    print("   cron: '0 16 * * 1-5'")
    
    print("\n2. 每天上午9点和下午2点")
    print("   cron: '0 9,14 * * *'")
    
    print("\n3. 每周一到周五，每小时执行一次")
    print("   cron: '0 * * * 1-5'")
    
    print("\n4. 每30分钟执行一次（全天）")
    print("   cron: '*/30 * * * *'")
    
    print("\n5. 每月第一个工作日晚上8点")
    print("   cron: '0 20 1-7 * 1'")
    
    example_cron = "0 16 * * 1-5"
    
    success = downloader.start_scheduler(
        stock_codes=["000858.SZ"],
        cron_expression=example_cron,
        incremental=True,
    )
    
    if success:
        print(f"\n✓ 已启动 Cron: {example_cron}")
        import time
        time.sleep(5)
        downloader.stop_scheduler()
        print("✓ 已停止")
    else:
        print("✗ 启动失败")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("QLib 数据定期下载功能示例")
    print("="*60)
    
    print("\n请选择要运行的示例:")
    print("\n1. 单次下载股票数据")
    print("2. 增量下载数据（智能更新）")
    print("3. 批量下载多个股票")
    print("4. 启动定时自动下载 (后台运行)")
    print("5. 使用数据更新管理器")
    print("6. 自定义调度策略演示")
    print("0. 退出")
    
    try:
        choice = input("\n请输入选择 (0-6): ").strip()
        
        if choice == "1":
            example_1_single_download()
        elif choice == "2":
            example_2_incremental_download()
        elif choice == "3":
            example_3_batch_download()
        elif choice == "4":
            example_4_scheduled_download()
        elif choice == "5":
            example_5_update_manager()
        elif choice == "6":
            example_6_custom_schedule()
        elif choice == "0":
            print("退出程序")
            return
        else:
            print("无效的选择")
            
    except KeyboardInterrupt:
        print("\n\n程序已中止")
    except Exception as e:
        logger.error(f"运行示例时出错: {str(e)}")
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()
