# 🚬 雪茄数据库 v2 - 专业版

基于多个权威数据源构建的专业雪茄管理与推荐系统。

## 📊 数据规模

- **79 款精选雪茄**
- **49 个品牌**
- **4 大产地**：尼加拉瓜(53%)、多米尼加(22%)、古巴(19%)、洪都拉斯(6%)

## 📚 数据来源

| 数据源 | 数量 | 特点 |
|-------|-----|------|
| **Cigar Scanner** | 20 款 | 用户众包数据，真实口碑 |
| **Cigar Aficionado** | 15 款 | 行业标杆，专业评审 |
| **Halfwheel** | 10 款 | 深度背景调查，限量款详情 |
| **Cigar Sense** | 9 款 | ISO 标准化感官分析 |

## 🏆 顶级雪茄

### 专家评分 TOP 5
| 排名 | 雪茄 | 评分 | 来源 |
|-----|------|-----|------|
| 🥇 | Fuente Fuente OpusX Perfecxion X | 95分 | Cigar Aficionado |
| 🥈 | My Father Le Bijou 1922 | 94分 | Cigar Aficionado |
| 🥈 | Drew Estate Liga Privada No. 9 | 94分 | Halfwheel |
| 🥈 | Cohiba Behike 52 | 94分 | Cigar Sense |
| 🥉 | Padron 1926 Serie No. 90 | 93.8分 | Cigar Scanner |

### 性价比 TOP 5
| 排名 | 雪茄 | 评分 | 价格 | 性价比 |
|-----|------|-----|------|-------|
| 🥇 | Nub Maduro 460 | 90分 | $8 | 11.25 |
| 🥈 | Perdomo Habano Bourbon | 92分 | $9 | 10.21 |
| 🥉 | Brick House Churchill | 90分 | $9 | 10.17 |
| 4 | Undercrown Sun Grown | 91分 | $9 | 10.07 |
| 5 | Sancho Panza Double Maduro | 90分 | $9 | 10.00 |

## 🎯 推荐算法

### 1. 风味相似度推荐
```bash
python3 cigar_v2.py recommend --type flavor --id 1
```

### 2. 性价比推荐
```bash
python3 cigar_v2.py recommend --type value
```

### 3. 饮品搭配推荐
```bash
python3 cigar_v2.py recommend --type pairing --drink 威士忌
```

## 📋 数据字段

### 基础信息
- 品牌、型号、系列、产地、工厂

### 物理参数
- 长度、环径、形状(Vitola)

### 烟叶成分
- 茄衣/茄套/茄芯及其产地

### 风味档案
- 浓度、醇厚度、主要/次要风味
- **Cigar Sense 风格**: 16个风味轮参数 (泥土/木质/雪松/胡椒等)

### 评分系统
- 专家评分 (90-100)
- 个人评分 (1-10)
- 用户评分 (Cigar Scanner 1-5)

### 品鉴建议
- 推荐搭配饮品
- 最佳吸食时段
- 预计抽吸时长

## 🚀 快速开始

### 查看统计
```bash
python3 cigar_v2.py stats
python3 full_report.py
```

### 列出雪茄
```bash
python3 cigar_v2.py list
python3 cigar_v2.py list --origin 古巴
python3 cigar_v2.py list --strength Full
```

### 搜索
```bash
python3 cigar_v2.py search "可可"
```

### 查看详情
```bash
python3 cigar_v2.py show 1
```

## 📁 文件结构

```
cigar-db/
├── database_v2.py              # v2 数据库核心
├── cigar_v2.py                 # v2 CLI 工具
├── full_report.py              # 完整报告生成
│
├── import_halfwheel.py         # Halfwheel 数据导入
├── import_cigar_scanner.py     # Cigar Scanner 数据导入
├── import_cigar_sense.py       # Cigar Sense 数据导入
├── halfwheel_playwright.py     # Halfwheel 爬虫框架
│
├── migrate_to_v2.py            # 数据迁移脚本
├── import_more_v2.py           # 批量导入工具
│
├── cigars_v2.db                # SQLite 数据库
└── README_v2.md                # 本文档
```

## 🔮 未来扩展

- [ ] **Bond Roberts** - 古巴雪茄拍卖价格追踪
- [ ] **价格监控** - 自动抓取零售商价格
- [ ] **品鉴记录** - 个人抽吸体验记录
- [ ] **Web 界面** - Flask/FastAPI 浏览器界面
- [ ] **AI 推荐** - 基于历史品鉴的个性化推荐

## 📝 数据来源说明

### Cigar Aficionado
- 行业最权威的雪茄评分机构
- 年度 Top 25 榜单
- 评分范围: 90-100

### Halfwheel
- 详细的背景调查和工厂信息
- 限量版、新款发布详情
- 三段式风味描述

### Cigar Scanner
- 用户众包数据库 (13,000+ 款)
- 用户评分 1-5 分
- 风味标签系统

### Cigar Sense
- ISO 标准化感官分析
- 100+ 感官参数
- 推荐搭配和场景

---

Made with ❤️ for cigar aficionados

Database Version: 2.0 | Total Cigars: 79 | Last Updated: 2026-03-15
