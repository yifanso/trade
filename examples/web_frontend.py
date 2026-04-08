#!/usr/bin/env python
"""
前端示例：运行 Flask 页面，展示导出的回测结果。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from qlib_backtest.web import app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
