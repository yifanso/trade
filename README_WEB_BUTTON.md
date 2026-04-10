# 🚀 前端下载按钮 - 五分钟快速启动

## ⚡ 快速开始（仅需3步）

### 步骤1️⃣：启动Web前端

```bash
cd /workspaces/trade
source .venv/bin/activate
python examples/web_frontend.py
```

**预期输出**：
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 步骤2️⃣：打开浏览器

访问：**http://localhost:5000/download-manager**

### 步骤3️⃣：触发下载

1. 在输入框输入股票代码（如 `000858.SZ, 000651.SZ`）
2. 点击 **"立即触发下载"** 按钮
3. 等待完成，查看结果

✅ **完成！** 

---

## 📍 导航地址

| 页面 | URL | 功能 |
|------|-----|------|
| 首页 | `http://localhost:5000/` | 回测仪表盘 |
| **📥 下载管理** ⭐ | `http://localhost:5000/download-manager` | **新增下载按钮** |
| 下载数据 | `http://localhost:5000/download` | 手动下载 |
| 回测页面 | `http://localhost:5000/backtest` | 执行回测 |

---

## 🎯 使用示例

### 示例1：下载单只股票

```
1. 输入：000858.SZ
2. 点击：立即触发下载
3. 等待完成（通常1-2秒）
4. 查看结果
```

### 示例2：批量下载多只股票

```
1. 输入：000858.SZ, 000651.SZ, 600519.SH
2. 点击：立即触发下载
3. 等待完成（通常10-20秒）
4. 查看详细结果表格
```

---

## 📄 完整文档

| 文档 | 说明 |
|------|------|
| [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md) | 改动总结 - 看这了解改了什么 ⭐ |
| [FRONTEND_QUICK_GUIDE.md](FRONTEND_QUICK_GUIDE.md) | 快速指南 - 新手必读 ⭐ |
| [FRONTEND_DOWNLOAD_BUTTON.md](FRONTEND_DOWNLOAD_BUTTON.md) | 完整说明 - 深入了解 |

---

## 💻 主要功能

### 🚀 立即触发下载
- 输入股票代码
- 一键下载数据
- 支持增量更新（只下载新数据）

### 📊 查看下载状态
- 定时下载器状态
- 调度器运行状态
- 最近下载记录

### 📈 查看统计信息
- 监控的股票数
- 总下载次数
- 成功/失败统计
- 平均下载耗时

### 📋 下载历史
- 显示最近的下载
- 每条记录包含日期和状态

---

## 🎨 界面预览

### 布局结构

```
┌─────────────────────────────────────────┐
│  📥 数据下载管理                        │
├─────────────────────────────────────────┤
│                                         │
│  🚀 立即触发下载                        │
│  ┌─────────────────────────────────┐   │
│  │ 股票代码：[输入框]              │   │
│  │ [立即触发下载] [清除消息]       │   │
│  │ ✓/✗ 结果提示                    │   │
│  │ 详细结果表格                    │   │
│  └─────────────────────────────────┘   │
│                                         │
│  📊 下载状态                            │
│  ├─ 定时下载器: ✓ 活跃                 │
│  ├─ 调度器: ✓ 启动                     │
│  └─ 最近下载: [表格]                   │
│                                         │
│  📈 下载统计                            │
│  ├─ 监控股票数: 10                     │
│  ├─ 总下载次数: 100                    │
│  └─ 成功率: 98/100                     │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔧 API 快速参考

### 触发下载

```bash
curl -X POST http://localhost:5000/api/trigger-download \
  -H "Content-Type: application/json" \
  -d '{"stock_codes": "000858.SZ, 000651.SZ"}'
```

**响应示例**：
```json
{
  "status": "success",
  "message": "成功下载 2/2 只股票",
  "successful": 2,
  "details": {
    "000858.SZ": {"records": 2500, "success": true},
    "000651.SZ": {"records": 2300, "success": true}
  }
}
```

### 查询状态

```bash
curl http://localhost:5000/api/download-status
```

---

## 📊 功能特性

✅ **一键触发** - 输入股票代码自动下载  
✅ **增量更新** - 智能检测，只下载新数据  
✅ **批量处理** - 支持同时下载多只股票  
✅ **实时反馈** - 加载动画和结果提示  
✅ **监控追踪** - 查看下载状态和统计  
✅ **无需命令行** - 完全通过Web界面操作  

---

## ❓ 常见问题

### Q: 下载速度慢吗？
**A**: 
- 第一次：下载全部历史数据（较慢）
- 后续：只下载新数据（很快，启用增量更新后）

### Q: 支持哪些股票代码格式？
**A**: 
- 深圳：`000858.SZ`（格式：代码.SZ）
- 上海：`600519.SH`（格式：代码.SH）

### Q: 如何输入多只股票？
**A**: 
使用逗号或中文分号分隔
- 英文逗号：`000858.SZ, 000651.SZ`
- 中文分号：`000858.SZ；000651.SZ`

### Q: 数据保存在哪里？
**A**: 
本地缓存目录：`~/.cache/qlib_backtest/data/`

### Q: 按钮无反应怎么办？
**A**: 
1. 按F12打开浏览器控制台
2. 查看是否有JavaScript错误
3. 检查Flask服务器是否正常运行

---

## 🚨 故障排查

| 问题 | 解决方案 |
|------|--------|
| 页面无法打开 | 检查Flask是否运行：`python examples/web_frontend.py` |
| 下载失败 | 检查股票代码格式是否正确 |
| 显示"缺失依赖" | 运行 `pip install -r requirements.txt` |
| 结果为空 | 尝试刷新页面或重启Flask |

---

## 📚 详细文档

需要更详细的说明？查看这些文档：

- **快速上手** → [FRONTEND_QUICK_GUIDE.md](FRONTEND_QUICK_GUIDE.md)
- **完整功能** → [FRONTEND_DOWNLOAD_BUTTON.md](FRONTEND_DOWNLOAD_BUTTON.md)
- **改动详情** → [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)
- **后端功能** → [DATA_DOWNLOAD_GUIDE.md](DATA_DOWNLOAD_GUIDE.md)

---

## 🎓 学习路径

```
第一步：快速体验
  └─ 按上面的3步操作，体验下载功能

第二步：了解工作原理
  └─ 阅读 FRONTEND_QUICK_GUIDE.md

第三步：深入学习
  └─ 阅读 FRONTEND_DOWNLOAD_BUTTON.md
  └─ 查看源代码

第四步：自定义扩展
  └─ 基于现有代码修改和扩展
```

---

## 💾 关键文件

### 新增文件

```
✨ src/qlib_backtest/templates/download_manager.html  - 下载管理页面
📖 FRONTEND_*.md                                      - 文档
🔧 verify_frontend.py                                - 验证脚本
```

### 修改文件

```
🔧 src/qlib_backtest/web.py         - 添加3个API路由
🔧 src/qlib_backtest/templates/     - 更新导航菜单
```

---

## 🎯 典型应用场景

### 场景1：研究特定股票
1. 打开下载管理器
2. 输入股票代码
3. 点击下载
4. 在回测页面使用数据

### 场景2：定期维护数据
1. 设置后台定时更新
2. 通过Web界面监控状态
3. 查看下载统计

### 场景3：批量初始化
1. 输入多只股票代码
2. 一次性批量下载
3. 数据自动缓存

---

## 📞 获取帮助

1. **查看文档** - 完整的使用说明在各markdown文件中
2. **查看源代码** - 注释详尽的代码实现
3. **运行验证脚本** - `python verify_frontend.py` 检查状态
4. **查看日志** - Flask输出会显示详细日志

---

## ✨ 下一步

现在您可以：

✅ 一键下载股票数据  
✅ 在Web界面监控下载状态  
✅ 查看完整的下载统计信息  
✅ 与回测系统无缝集成  

**立即开始**：
```bash
python examples/web_frontend.py
```

然后访问：http://localhost:5000/download-manager

---

**祝您使用愉快！** 🎉

---

*版本：1.0.0 | 实现日期：2026年4月10日 | 状态：✅ 完成*
