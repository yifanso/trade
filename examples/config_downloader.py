"""
生产环境下载器配置脚本

这个脚本展示如何在生产环境中配置和运行数据下载器
"""

import os
import logging
from datetime import datetime
from pathlib import Path

from src.qlib_backtest.data.downloader import DataDownloader, DataUpdateManager
from src.qlib_backtest.utils import setup_logging

# 设置日志
logger = setup_logging("data_downloader_config")


class DataDownloaderConfig:
    """数据下载器配置类"""
    
    # QLib配置
    QLIB_DATA_PATH = os.path.expanduser("~/.qlib/qlib_data")
    
    # 缓存配置
    DATA_CACHE_DIR = os.path.expanduser("~/.cache/qlib_backtest/data")
    DB_PATH = os.path.expanduser("~/.cache/qlib_backtest/download_history.db")
    
    # 监控的股票列表
    # 可根据实际需求修改
    WATCH_STOCKS = [
        # 白酒行业
        "000858.SZ",  # 五粮液
        "000651.SZ",  # 格力电器
        
        # 食品饮料
        "600519.SH",  # 贵州茅台
        
        # 消费
        "000333.SZ",  # 美的集团
        "600000.SH",  # 浦发银行
        
        # 添加更多股票...
    ]
    
    # 调度配置
    SCHEDULE_CONFIGS = {
        # 默认配置：工作日下午4点（股市收盘后）
        "default": {
            "cron_expression": "0 16 * * 1-5",
            "incremental": True,
            "description": "每个工作日下午4点更新"
        },
        
        # 高频更新配置
        "high_frequency": {
            "cron_expression": "0 * * * *",  # 每小时
            "incremental": True,
            "description": "每小时更新一次"
        },
        
        # 日间更新配置
        "intraday": {
            "cron_expression": "0 9,11,14,16 * * 1-5",  # 工作日4个时间点
            "incremental": True,
            "description": "工作日9点、11点、14点、16点更新"
        },
        
        # 每日一次配置
        "daily": {
            "cron_expression": "0 16 * * *",  # 每天下午4点
            "incremental": True,
            "description": "每天下午4点更新"
        },
    }


def create_downloader(config_name: str = "default") -> DataDownloader:
    """创建配置好的下载器"""
    downloader = DataDownloader(
        qlib_data_path=DataDownloaderConfig.QLIB_DATA_PATH,
        data_cache_dir=DataDownloaderConfig.DATA_CACHE_DIR,
        db_path=DataDownloaderConfig.DB_PATH,
    )
    return downloader


def setup_monitor(downloader: DataDownloader, config_name: str = "default") -> bool:
    """设置监控任务"""
    config = DataDownloaderConfig.SCHEDULE_CONFIGS.get(config_name, 
                                                        DataDownloaderConfig.SCHEDULE_CONFIGS["default"])
    
    logger.info(f"配置监控任务: {config_name}")
    logger.info(f"  描述: {config['description']}")
    logger.info(f"  Cron: {config['cron_expression']}")
    logger.info(f"  增量更新: {config['incremental']}")
    logger.info(f"  监控股票数: {len(DataDownloaderConfig.WATCH_STOCKS)}")
    
    return downloader.start_scheduler(
        stock_codes=DataDownloaderConfig.WATCH_STOCKS,
        cron_expression=config['cron_expression'],
        incremental=config['incremental'],
    )


def print_status(downloader: DataDownloader):
    """打印下载器状态"""
    print("\n" + "="*60)
    print("下载器当前状态")
    print("="*60)
    
    status = downloader.get_download_status()
    stats = downloader.get_download_statistics()
    
    print(f"\n运行状态: {'活跃' if status['running'] else '未运行'}")
    print(f"调度器: {'活跃' if status['scheduler_active'] else '未运行'}")
    
    print(f"\n最近下载:")
    for item in status.get('recent_downloads', [])[:5]:
        print(f"  {item['stock_code']:15} - {item['last_date']} ({item['status']})")
    
    if stats:
        print(f"\n统计信息:")
        print(f"  监控的股票: {stats.get('unique_stocks', 0)}")
        print(f"  总下载次数: {stats.get('total_downloads', 0)}")
        print(f"  成功: {stats.get('successful', 0)}")
        print(f"  失败: {stats.get('failed', 0)}")
        print(f"  平均耗时: {stats.get('avg_duration_seconds', 0):.1f}秒")
        print(f"  最后下载: {stats.get('last_download', 'N/A')}")


def manual_update_now(downloader: DataDownloader):
    """立即执行一次更新"""
    logger.info("执行手动更新...")
    
    results = downloader.download_data(
        stock_codes=DataDownloaderConfig.WATCH_STOCKS,
        incremental=True,
    )
    
    successful = sum(1 for df in results.values() if df is not None)
    print(f"✓ 手动更新完成: {successful}/{len(DataDownloaderConfig.WATCH_STOCKS)} 只股票")


def run_downloader(config_name: str = "default"):
    """运行下载器"""
    print("\n" + "="*60)
    print("QLib 数据定期下载系统 - 配置模式")
    print("="*60)
    
    # 创建下载器
    logger.info("正在初始化下载器...")
    downloader = create_downloader(config_name)
    
    # 设置监控
    logger.info("正在设置监控任务...")
    success = setup_monitor(downloader, config_name)
    
    if success:
        logger.info("✓ 监控任务已启动")
        
        # 打印状态
        import time
        time.sleep(1)
        print_status(downloader)
        
        # 可选：立即执行一次更新
        # manual_update_now(downloader)
        
        return downloader
    else:
        logger.error("✗ 启动监控任务失败")
        return None


# ============================================================================
# 高级配置示例
# ============================================================================

def example_custom_stocks():
    """自定义股票列表example"""
    print("\n" + "="*60)
    print("示例: 自定义股票列表")
    print("="*60)
    
    downloader = DataDownloader()
    
    # 自定义股票列表
    my_stocks = [
        "000858.SZ",  # 五粮液
        "600519.SH",  # 贵州茅台
    ]
    
    downloader.start_scheduler(
        stock_codes=my_stocks,
        cron_expression="0 16 * * 1-5",
        incremental=True,
    )
    
    print(f"✓ 已启动监控 {len(my_stocks)} 只股票")


def example_multiple_schedules():
    """多个调度任务示例"""
    print("\n" + "="*60)
    print("示例: 多个调度任务")
    print("="*60)
    
    downloader = DataDownloader()
    
    # 日间高频更新
    downloader.start_scheduler(
        stock_codes=["000858.SZ", "600519.SH"],
        cron_expression="0 9,11,14,16 * * 1-5",
        incremental=True,
    )
    
    print("✓ 已启动多时段更新")


def example_batch_initialization():
    """批量初始化历史数据示例"""
    print("\n" + "="*60)
    print("示例: 批量初始化历史数据")
    print("="*60)
    
    downloader = DataDownloader()
    
    print("一次性下载所有股票的3年历史数据...")
    
    results = downloader.download_data(
        stock_codes=DataDownloaderConfig.WATCH_STOCKS,
        start_date="2021-01-01",
        incremental=False,
    )
    
    successful = sum(1 for df in results.values() if df is not None)
    print(f"✓ 初始化完成: {successful}/{len(DataDownloaderConfig.WATCH_STOCKS)} 只股票")


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """主函数"""
    import sys
    
    print("\n使用方式:")
    print("  python config_downloader.py run              # 运行默认配置")
    print("  python config_downloader.py run high_freq   # 运行高频配置")
    print("  python config_downloader.py status           # 查看状态")
    print("  python config_downloader.py update           # 手动更新")
    print("  python config_downloader.py init             # 初始化历史数据")
    
    if len(sys.argv) < 2:
        print("\n请指定命令")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        config = sys.argv[2] if len(sys.argv) > 2 else "default"
        downloader = run_downloader(config)
        if downloader:
            print("\n按 Ctrl+C 停止下载器...")
            import time
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n\n正在停止...")
                downloader.stop_scheduler()
                print("✓ 已停止")
                
    elif cmd == "status":
        downloader = create_downloader()
        print_status(downloader)
        
    elif cmd == "update":
        downloader = create_downloader()
        manual_update_now(downloader)
        
    elif cmd == "init":
        print("初始化3年历史数据...")
        example_batch_initialization()
        
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        main()
    else:
        # 默认运行配置说明
        print("\n" + "="*60)
        print("数据下载器配置说明")
        print("="*60)
        
        print("\n1. 编辑此文件修改配置:")
        print("   - WATCH_STOCKS: 要监控的股票列表")
        print("   - SCHEDULE_CONFIGS: 调度策略")
        
        print("\n2. 预设的调度配置:")
        for name, config in DataDownloaderConfig.SCHEDULE_CONFIGS.items():
            print(f"   - {name:15} : {config['description']}")
        
        print("\n3. 运行方式:")
        print("   python config_downloader.py run")
        print("   python config_downloader.py status")
        print("   python config_downloader.py update")
        
        print("\n4. 生产环境部署:")
        print("   - 可以使用 systemd 或其他进程管理工具")
        print("   - 建议配置日志轮转")
        print("   - 定期检查下载状态和统计信息")
