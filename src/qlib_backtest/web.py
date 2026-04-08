import json
from io import BytesIO
from pathlib import Path
from flask import Flask, render_template, abort, request, send_file

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
