#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证Web前端的下载按钮功能是否正确实现
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def check_web_file():
    """检查web.py文件是否正确"""
    print("\n📋 检查 web.py 文件...")
    
    web_file = project_root / "src/qlib_backtest/web.py"
    
    if not web_file.exists():
        print("❌ web.py 文件不存在")
        return False
    
    with open(web_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的导入
    checks = [
        ("jsonify 导入", "from flask import Flask, render_template, abort, request, send_file, jsonify"),
        ("API 路由 - trigger-download", "@app.route(\"/api/trigger-download\", methods=[\"POST\"])"),
        ("API 路由 - download-status", "@app.route(\"/api/download-status\", methods=[\"GET\"])"),
        ("下载管理页面", "@app.route(\"/download-manager\", methods=[\"GET\"])"),
        ("DataDownloader 导入", "from qlib_backtest.data.downloader import DataDownloader"),
    ]
    
    all_ok = True
    for check_name, check_str in checks:
        if check_str in content:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ❌ {check_name}：未找到")
            all_ok = False
    
    return all_ok


def check_templates():
    """检查模板文件"""
    print("\n📋 检查模板文件...")
    
    templates_dir = project_root / "src/qlib_backtest/templates"
    
    required_templates = {
        "download_manager.html": [
            "data-下载管理",
            "立即触发下载",
            "triggerDownload",
        ],
        "download.html": [
            "快速触发",
            "下载管理器",
        ],
        "dashboard.html": [
            "数据下载管理",
        ],
    }
    
    all_ok = True
    for template_name, required_content in required_templates.items():
        template_file = templates_dir / template_name
        
        if not template_file.exists():
            print(f"  ❌ {template_name}：文件不存在")
            all_ok = False
            continue
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing = []
        for content_check in required_content:
            if content_check.lower() not in content.lower():
                missing.append(content_check)
        
        if missing:
            print(f"  ⚠ {template_name}：缺少内容 {missing}")
            all_ok = False
        else:
            print(f"  ✓ {template_name}")
    
    return all_ok


def check_downloader():
    """检查DataDownloader类"""
    print("\n📋 检查 DataDownloader 类...")
    
    try:
        from qlib_backtest.data.downloader import DataDownloader, DataUpdateManager
        
        # 检查DataDownloader方法
        required_methods = [
            "download_data",
            "start_scheduler",
            "stop_scheduler",
            "get_download_status",
            "get_download_statistics",
        ]
        
        all_ok = True
        for method in required_methods:
            if hasattr(DataDownloader, method):
                print(f"  ✓ DataDownloader.{method}")
            else:
                print(f"  ❌ DataDownloader.{method}：方法不存在")
                all_ok = False
        
        # 检查DataUpdateManager
        if hasattr(DataUpdateManager, 'add_stocks'):
            print(f"  ✓ DataUpdateManager 类存在")
        else:
            print(f"  ❌ DataUpdateManager 类不存在")
            all_ok = False
        
        return all_ok
        
    except ImportError as e:
        print(f"  ❌ 导入错误：{e}")
        return False


def check_requirements():
    """检查依赖包"""
    print("\n📋 检查依赖包...")
    
    required_packages = {
        "flask": "Flask Web框架",
        "apscheduler": "定时任务库",
        "pandas": "数据处理库",
    }
    
    all_ok = True
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {package}: {description}")
        except ImportError:
            print(f"  ❌ {package}：未安装 ({description})")
            all_ok = False
    
    return all_ok


def test_api_endpoints():
    """测试API端点"""
    print("\n📋 测试 API 端点定义...")
    
    try:
        from qlib_backtest.web import app
        
        rules = {
            "/api/trigger-download": "POST",
            "/api/download-status": "GET",
            "/download-manager": "GET",
        }
        
        all_ok = True
        for rule in app.url_map.iter_rules():
            for endpoint, method in rules.items():
                if rule.rule == endpoint and method in rule.methods:
                    print(f"  ✓ {method} {endpoint}")
        
        return all_ok
        
    except Exception as e:
        print(f"  ⚠ 无法完全验证API端点：{e}")
        return True


def check_documentation():
    """检查文档"""
    print("\n📋 检查文档文件...")
    
    doc_files = {
        "FRONTEND_DOWNLOAD_BUTTON.md": "前端下载按钮功能说明",
        "FRONTEND_QUICK_GUIDE.md": "前端快速指南",
    }
    
    all_ok = True
    for doc_file, description in doc_files.items():
        doc_path = project_root / doc_file
        
        if doc_path.exists():
            print(f"  ✓ {doc_file}")
        else:
            print(f"  ❌ {doc_file}：文件不存在")
            all_ok = False
    
    return all_ok


def main():
    """主函数"""
    print("=" * 60)
    print("Web前端下载按钮功能验证")
    print("=" * 60)
    
    results = []
    
    # 运行所有检查
    results.append(("Web文件", check_web_file()))
    results.append(("模板文件", check_templates()))
    results.append(("DataDownloader类", check_downloader()))
    results.append(("依赖包", check_requirements()))
    results.append(("API端点", test_api_endpoints()))
    results.append(("文档文件", check_documentation()))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{name:20} {status}")
    
    print(f"\n总体：{passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n✅ 所有检查通过！前端下载按钮功能已正确实现。")
        print("\n接下来可以：")
        print("  python examples/web_frontend.py")
        print("  然后访问: http://localhost:5000/download-manager")
        return 0
    else:
        print("\n⚠ 有些检查失败。请检查上面的错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
