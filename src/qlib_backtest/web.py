import json
import os
import sys
from io import BytesIO
from pathlib import Path
from flask import Flask, render_template, abort, request, send_file, jsonify

# 确保src目录在Python路径中，以便正确导入qlib_backtest模块
_src_path = os.path.join(os.path.dirname(__file__), '..', '..')
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)
    
# 也添加src目录本身
_src_dir = os.path.join(os.path.dirname(__file__), '..')
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

PACKAGE_ROOT = Path(__file__).resolve().parent
TEMPLATE_FOLDER = PACKAGE_ROOT / "templates"
STATIC_FOLDER = PACKAGE_ROOT / "static"
RESULTS_DIR = Path("./results")

app = Flask(
    __name__,
    template_folder=str(TEMPLATE_FOLDER),
    static_folder=str(STATIC_FOLDER),
    static_url_path="/static",
)


def list_summary_files():
    if not RESULTS_DIR.exists():
        return []

    return sorted(
        [p.name for p in RESULTS_DIR.glob("*_summary.json") if p.is_file()],
        reverse=True,
    )


def load_summary(filename: str) -> dict:
    filepath = RESULTS_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        raise FileNotFoundError(f"未找到回测结果文件: {filename}")

    with filepath.open("r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    summaries = list_summary_files()
    active_summary = {}
    active_name = ""

    if summaries:
        active_name = summaries[0]
        active_summary = load_summary(active_name)

    return render_template(
        "dashboard.html",
        summaries=summaries,
        active_summary=active_summary,
        active_name=active_name,
    )


@app.route("/results/<summary_name>")
def result_detail(summary_name: str):
    summaries = list_summary_files()
    if summary_name not in summaries:
        abort(404)

    active_summary = load_summary(summary_name)
    return render_template(
        "dashboard.html",
        summaries=summaries,
        active_summary=active_summary,
        active_name=summary_name,
    )


def parse_stock_codes(codes: str):
    return [
        code.strip()
        for code in codes.replace("；", ",").replace("，", ",").replace(";", ",").split(",")
        if code.strip()
    ]


def parse_int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_float(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@app.route("/download", methods=["GET", "POST"])
def download_page():
    error = None

    if request.method == "POST":
        stock_codes = parse_stock_codes(request.form.get("stock_codes", ""))
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
        freq = request.form.get("freq", "day")

        if not stock_codes or not start_date or not end_date:
            error = "请输入股票代码、开始日期和结束日期。"
        else:
            from qlib_backtest.data import DataHandler

            handler = DataHandler()
            df = handler.load_stock_data(stock_codes, start_date, end_date, freq)

            if df.empty:
                error = "未加载到任何数据，请检查输入参数或确认QLib数据是否可用。"
            else:
                csv_bytes = df.to_csv(index=False, encoding="utf-8")
                buffer = BytesIO(csv_bytes.encode("utf-8"))
                filename = f"stock_data_{start_date}_{end_date}.csv"
                buffer.seek(0)
                return send_file(
                    buffer,
                    mimetype="text/csv",
                    as_attachment=True,
                    download_name=filename,
                )

    return render_template("download.html", error=error)


@app.route("/backtest", methods=["GET", "POST"])
def backtest_page():
    error = None
    result_summary = None
    export_name = None
    metrics = None
    strategy_name = request.form.get("strategy", "momentum")

    if request.method == "POST":
        stock_codes = parse_stock_codes(request.form.get("stock_codes", ""))
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
        freq = request.form.get("freq", "day")
        strategy_name = request.form.get("strategy", "momentum")

        if not stock_codes or not start_date or not end_date:
            error = "请输入股票代码、开始日期和结束日期。"
        else:
            from qlib_backtest.data import DataHandler
            from qlib_backtest.features import FeatureEngine
            from qlib_backtest.strategies import StrategyFactory
            from qlib_backtest.backtest import BacktestEngine
            from qlib_backtest.utils import ResultsExporter

            try:
                handler = DataHandler()
                df = handler.load_stock_data(stock_codes, start_date, end_date, freq)
                if df.empty:
                    error = "未加载到任何数据，请检查输入参数或确认QLib数据是否可用。"
                else:
                    df = handler.clean_data(df)
                    df = handler.add_returns(df)

                    feature_engine = FeatureEngine()
                    df = feature_engine.calculate_all_features(df)

                    strategy_params = {}
                    if strategy_name == "momentum":
                        strategy_params = {
                            "short_window": parse_int(request.form.get("short_window", "5"), 5),
                            "long_window": parse_int(request.form.get("long_window", "20"), 20),
                            "threshold": parse_float(request.form.get("threshold", "0.02"), 0.02),
                        }
                    elif strategy_name == "mean_reversion":
                        strategy_params = {
                            "window": parse_int(request.form.get("window", "20"), 20),
                            "std_multiple": parse_float(request.form.get("std_multiple", "2"), 2.0),
                        }

                    strategy = StrategyFactory.create_strategy(strategy_name, **strategy_params)
                    signals = strategy.generate_signals(df)

                    backtest_engine = BacktestEngine(
                        initial_capital=1000000.0,
                        commission=0.001,
                        slippage=0.0001,
                    )
                    result_summary = backtest_engine.run_backtest(df, signals)
                    exporter = ResultsExporter("./results")
                    export_name = exporter.export_results(result_summary, f"{strategy_name}_web")
                    metrics = result_summary.to_dict()
            except Exception as exc:
                error = f"回测执行失败: {str(exc)}"

    return render_template(
        "backtest.html",
        error=error,
        metrics=metrics,
        export_name=export_name,
        strategy_name=strategy_name,
    )


@app.route("/api/trigger-download", methods=["POST"])
def trigger_download():
    """触发数据下载API"""
    try:
        from qlib_backtest.data.downloader import DataDownloader
        
        stock_codes = request.json.get("stock_codes", [])
        if isinstance(stock_codes, str):
            stock_codes = parse_stock_codes(stock_codes)
        
        if not stock_codes:
            return jsonify({
                "status": "error",
                "message": "请指定要下载的股票代码"
            }), 400
        
        downloader = DataDownloader()
        results = downloader.download_data(
            stock_codes=stock_codes,
            incremental=True,
        )
        
        successful = sum(1 for df in results.values() if df is not None)
        
        return jsonify({
            "status": "success",
            "message": f"成功下载 {successful}/{len(stock_codes)} 只股票",
            "successful": successful,
            "total": len(stock_codes),
            "details": {
                code: {
                    "records": len(df) if df is not None else 0,
                    "success": df is not None
                }
                for code, df in results.items()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"下载失败: {str(e)}"
        }), 500


@app.route("/api/download-status", methods=["GET"])
def download_status():
    """获取下载器状态API"""
    try:
        from qlib_backtest.data.downloader import DataDownloader
        
        downloader = DataDownloader()
        status = downloader.get_download_status()
        stats = downloader.get_download_statistics()
        
        return jsonify({
            "status": "success",
            "running": status.get('running', False),
            "scheduler_active": status.get('scheduler_active', False),
            "recent_downloads": status.get('recent_downloads', []),
            "statistics": stats
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/download-manager", methods=["GET"])
def download_manager_page():
    """下载管理页面"""
    # 默认状态和统计数据
    status = {"scheduler_running": False, "monitored_stocks": [], "last_check": None}
    stats = {"total_downloads": 0, "success_rate": 0, "avg_duration": 0}
    error = None
    
    try:
        from qlib_backtest.data.downloader import DataDownloader
        
        downloader = DataDownloader()
        status = downloader.get_download_status()
        stats = downloader.get_download_statistics()
    except ImportError as e:
        error = f"模块导入失败: {str(e)}. 请检查 DataDownloader 是否正确安装。"
    except Exception as e:
        error = f"获取下载状态失败: {str(e)}"
    
    return render_template(
        "download_manager.html",
        status=status,
        stats=stats,
        error=error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
