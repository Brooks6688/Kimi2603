# 🚬 雪茄数据库 (Cigar Database)

个人雪茄管理与品鉴记录工具。

## 功能

- 📦 雪茄信息管理（品牌、产地、尺寸、风味等）
- 📝 品鉴记录（抽吸体验、评分、备注）
- 🔍 多维度搜索（品牌、产地、浓度、关键词）
- 📊 统计报表（最常抽的雪茄、产地分布等）

## 快速开始

### 1. 初始化数据库（已预置8款经典雪茄）

```bash
cd /root/.openclaw/workspace/cigar-db
python3 database.py
```

### 2. 使用命令行工具

```bash
# 列出所有雪茄
python3 cigar.py list

# 按品牌筛选
python3 cigar.py list --brand Cohiba

# 查看详情
python3 cigar.py show 1

# 搜索关键词
python3 cigar.py search "浓郁"

# 添加品鉴记录
python3 cigar.py taste 1 --rating 9 --notes "非常顺滑，可可味明显"

# 查看统计
python3 cigar.py stats

# 交互模式
python3 cigar.py interactive
```

### 3. 添加新雪茄

```bash
python3 cigar.py add \
  --brand "Cohiba" \
  --name "Siglo VI" \
  --origin "古巴" \
  --length "150mm" \
  --ring-gauge 52 \
  --strength "中等偏浓" \
  --flavor "雪松、可可、香料" \
  --price "中高端"
```

## 数据结构

### 雪茄信息
| 字段 | 说明 |
|-----|------|
| brand | 品牌 |
| name | 型号/名称 |
| origin | 产地 |
| length | 长度 |
| ring_gauge | 环径 |
| strength | 浓度（轻度/中等/中等偏浓/浓郁）|
| flavor_profile | 风味描述 |
| wrapper | 茄衣 |
| binder | 茄套 |
| filler | 茄芯 |
| price_range | 价格区间 |
| rating | 个人评分(1-10) |
| smoked_count | 已抽数量 |

### 品鉴记录
| 字段 | 说明 |
|-----|------|
| smoke_date | 日期 |
| duration_minutes | 抽吸时长 |
| draw | 吸阻（松/适中/紧）|
| burn | 燃烧（不均匀/一般/均匀）|
| ash | 烟灰（松散/一般/紧实）|
| overall_rating | 整体评分 |
| notes | 备注 |

## 预置雪茄

数据库已包含以下经典雪茄：

1. **Cohiba Behike 52** - 古巴，浓郁
2. **Montecristo No. 2** - 古巴，中等偏浓
3. **Romeo y Julieta Wide Churchill** - 古巴，中等
4. **Partagas Serie D No. 4** - 古巴，浓郁
5. **Hoyo de Monterrey Epicure No. 2** - 古巴，轻度
6. **Davidoff Winston Churchill** - 多米尼加，中等
7. **Arturo Fuente Opus X** - 多米尼加，浓郁
8. **Padron 1964 Anniversary** - 尼加拉瓜，浓郁

## 文件说明

- `database.py` - 数据库模型和管理类
- `cigar.py` - 命令行界面
- `cigars.db` - SQLite 数据库文件
- `README.md` - 本说明文件

## 扩展计划

- [ ] Web 界面（Flask/FastAPI）
- [ ] 图片上传（雪茄照片）
- [ ] 湿度/温度记录（养护管理）
- [ ] 导入/导出功能（CSV/JSON）
