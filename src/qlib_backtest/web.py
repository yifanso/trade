import json
from pathlib import Path
from flask import Flask, render_template, abort

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
