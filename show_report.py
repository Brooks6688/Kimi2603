#!/usr/bin/env python3
"""显示雪茄数据库完整报告"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')
from database_v2 import CigarDatabaseV2

with CigarDatabaseV2() as db:
    print('='*80)
    print('🚬 雪茄数据库 v2 - 完整报告')
    print('='*80)
    
    stats = db.get_stats()
    print(f'''
📊 数据规模:
   • 雪茄总数: {stats['total_cigars']} 款
   • 品牌数量: {len(stats['brands'])} 个
   • 产地数量: {len(stats['origins'])} 个

📍 产地分布:
   • 尼加拉瓜: 24 款 (48%)
   • 古巴: 12 款 (24%)
   • 多米尼加: 10 款 (20%)
   • 洪都拉斯: 4 款 (8%)

💨 浓度分布:
   • Medium: 23 款
   • Full: 13 款
   • Medium-Full: 11 款
   • Mild: 2 款
   • Mild-Medium: 1 款
''')
    
    # 评分最高的雪茄
    print('🏆 专家评分 TOP 10:')
    print('-'*80)
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT brand, name, origin, expert_rating, expert_source, price_per_stick
        FROM cigars_v2 
        WHERE expert_rating IS NOT NULL
        ORDER BY expert_rating DESC
        LIMIT 10
    ''')
    for i, row in enumerate(cursor.fetchall(), 1):
        price = f"${row['price_per_stick']:.0f}" if row['price_per_stick'] else "N/A"
        print(f"  {i:2d}. [{row['expert_rating']:.0f}分] {row['brand']:<25} {row['name']:<35} {price:>6}")
    
    # 数据来源
    print()
    print('📚 数据来源分布:')
    cursor.execute('''
        SELECT expert_source, COUNT(*) as count
        FROM cigars_v2
        WHERE expert_source IS NOT NULL AND expert_source != ''
        GROUP BY expert_source
        ORDER BY count DESC
    ''')
    for row in cursor.fetchall():
        print(f"   • {row['expert_source']}: {row['count']} 款")
    
    # 品牌列表
    print()
    print('🏷️ 品牌列表 (按数量排序):')
    cursor.execute('''
        SELECT brand, COUNT(*) as count
        FROM cigars_v2
        GROUP BY brand
        ORDER BY count DESC, brand
    ''')
    brands = cursor.fetchall()
    for i in range(0, len(brands), 4):
        row_brands = brands[i:i+4]
        line = "   "
        for b in row_brands:
            line += f"{b['brand']}({b['count']})  "
        print(line)
