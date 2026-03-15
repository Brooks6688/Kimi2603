# 🌐 雪茄数据库 Web 界面

基于 Flask 的 Web 界面，提供直观的雪茄浏览、搜索和推荐功能。

## 🚀 启动方式

```bash
cd /root/.openclaw/workspace/cigar-db
python3 web_app.py
```

访问地址: http://localhost:5000

## 📱 功能截图

### 首页
- 数据库概览统计
- 产地分布可视化
- 顶级评分 TOP 10
- 性价比之选 TOP 10
- 快速导航入口

### 雪茄库 (/cigars)
- 网格展示所有雪茄
- 多维度筛选 (产地/浓度/搜索)
- 多种排序方式 (评分/价格/名称)
- 响应式卡片设计

### 雪茄详情 (/cigar/{id})
- 完整规格参数
- 烟叶成分详情
- 风味档案分析
- 相似雪茄推荐
- 同品牌其他雪茄

### 搜索 (/search)
- 全文搜索功能
- 支持品牌/型号/风味/产地
- 热门搜索快捷入口

### 推荐 (/recommend)
- 💰 性价比推荐
- 🏆 顶级评分
- 👶 新手入门
- 💪 浓郁型
- 🇨🇺 古巴雪茄
- 按饮品搭配推荐
- 按时段选择

### 统计 (/stats)
- 品牌统计
- 价格分布
- 数据来源说明
- API 接口文档

## 🎨 界面特色

- **响应式设计**: 支持桌面和移动设备
- **雪茄主题配色**: 棕色系专业风格
- **卡片式布局**: 清晰的信息层级
- **交互式筛选**: 实时筛选和排序
- **风味标签**: 可视化风味特征

## 🔌 API 接口

```
GET /api/cigars?limit=50&offset=0    # 获取雪茄列表
GET /api/cigar/{id}                 # 获取单支雪茄详情
```

## 🛠️ 技术栈

- **后端**: Flask + SQLite
- **前端**: 原生 HTML + CSS (无框架依赖)
- **样式**: 自定义 CSS，雪茄主题配色
- **数据**: cigars_v2.db (79款雪茄)

## 📁 文件结构

```
cigar-db/
├── web_app.py              # Flask 主应用
├── templates/
│   ├── base.html          # 基础模板
│   ├── index.html         # 首页
│   ├── cigars.html        # 雪茄列表
│   ├── cigar_detail.html  # 雪茄详情
│   ├── search.html        # 搜索页面
│   ├── recommend.html     # 推荐页面
│   ├── stats.html         # 统计页面
│   └── 404.html           # 错误页面
└── cigars_v2.db           # SQLite 数据库
```

## 🔄 与 CLI 工具的关系

Web 界面与 CLI 工具共享同一个数据库:
- CLI: `python3 cigar_v2.py list`
- Web: http://localhost:5000/cigars

两者数据完全同步。

## 📝 使用示例

### 查看古巴雪茄
1. 首页点击 "🇨🇺 古巴雪茄"
2. 或访问: /cigars?origin=古巴

### 搜索咖啡风味
1. 搜索框输入 "咖啡"
2. 或访问: /search?q=咖啡

### 找性价比高的雪茄
1. 导航栏点击 "推荐"
2. 选择 "💰 性价比"
3. 或访问: /recommend?type=value

## 🎯 即将推出

- [ ] 用户登录系统
- [ ] 个人品鉴记录
- [ ] 收藏夹功能
- [ ] 价格监控提醒
- [ ] 数据导出 (CSV/Excel)
