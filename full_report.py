#!/usr/bin/env python3
"""生成完整的数据库报告"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')
from database_v2 import CigarDatabaseV2

with CigarDatabaseV2() as db:
    print('='*90)
    print('🚬 雪茄数据库 v2 - 完整数据报告')
    print('='*90)
    
    stats = db.get_stats()
    
    # 数据规模
    print(f'''
📊 数据规模:
   • 雪茄总数: {stats['total_cigars']} 款
   • 品牌数量: {len(stats['brands'])} 个
   • 产地数量: {len(stats['origins'])} 个
''')
    
    # 产地分布
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT origin, COUNT(*) as count 
        FROM cigars_v2 
        WHERE origin IS NOT NULL AND origin != ''
        GROUP BY origin 
        ORDER BY count DESC
    ''')
    print('📍 产地分布:')
    total = stats['total_cigars']
    for row in cursor.fetchall():
        pct = row['count'] / total * 100
        bar = '█' * int(pct / 5)
        print(f"   • {row['origin']:<12} {row['count']:2d} 款 ({pct:4.1f}%) {bar}")
    
    # 浓度分布
    print()
    cursor.execute('''
        SELECT strength, COUNT(*) as count 
        FROM cigars_v2 
        WHERE strength IS NOT NULL AND strength != ''
        GROUP BY strength 
        ORDER BY count DESC
    ''')
    print('💨 浓度分布:')
    for row in cursor.fetchall():
        print(f"   • {row['strength']:<15} {row['count']:2d} 款")
    
    # 数据来源
    print()
    cursor.execute('''
        SELECT 
            CASE 
                WHEN expert_source LIKE '%Cigar Aficionado%' THEN 'Cigar Aficionado'
                WHEN expert_source LIKE '%Halfwheel%' THEN 'Halfwheel'
                WHEN expert_source LIKE '%Cigar Scanner%' THEN 'Cigar Scanner'
                WHEN expert_source LIKE '%Cigar Sense%' THEN 'Cigar Sense'
                ELSE expert_source
            END as source,
            COUNT(*) as count
        FROM cigars_v2
        WHERE expert_source IS NOT NULL AND expert_source != ''
        GROUP BY source
        ORDER BY count DESC
    ''')
    print('📚 数据来源分布:')
    for row in cursor.fetchall():
        print(f"   • {row['source']:<25} {row['count']:2d} 款")
    
    # TOP 15 评分雪茄
    print()
    print('🏆 专家评分 TOP 15:')
    print('-'*90)
    cursor.execute('''
        SELECT brand, name, origin, expert_rating, expert_source, price_per_stick
        FROM cigars_v2 
        WHERE expert_rating IS NOT NULL
        ORDER BY expert_rating DESC
        LIMIT 15
    ''')
    for i, row in enumerate(cursor.fetchall(), 1):
        price = f"${row['price_per_stick']:.0f}" if row['price_per_stick'] else "N/A"
        source = row['expert_source'][:15] if row['expert_source'] else "Unknown"
        print(f"  {i:2d}. [{row['expert_rating']:>5.1f}分] {row['brand']:<22} {row['name']:<32} {price:>6}  {source}")
    
    # 性价比 TOP 10
    print()
    print('💰 性价比 TOP 10 (评分/价格):')
    print('-'*90)
    cursor.execute('''
        SELECT brand, name, expert_rating, price_per_stick,
               (expert_rating / NULLIF(price_per_stick, 0)) as value_ratio
        FROM cigars_v2
        WHERE expert_rating IS NOT NULL AND price_per_stick IS NOT NULL AND price_per_stick > 0
        ORDER BY value_ratio DESC
        LIMIT 10
    ''')
    for i, row in enumerate(cursor.fetchall(), 1):
        value = row['value_ratio'] if row['value_ratio'] else 0
        print(f"  {i:2d}. {row['brand']:<22} {row['name']:<30} {row['expert_rating']:.0f}分/${row['price_per_stick']:.0f} = {value:.2f}")
    
    # 品牌统计
    print()
    print('🏷️ 品牌分布 (≥2款):')
    cursor.execute('''
        SELECT brand, COUNT(*) as count
        FROM cigars_v2
        GROUP BY brand
        HAVING count >= 2
        ORDER BY count DESC, brand
    ''')
    brands = cursor.fetchall()
    for row in brands:
        print(f"   • {row['brand']:<25} {row['count']} 款")
    
    print()
    print('='*90)
    print('✅ 报告生成完成')
    print('='*90)
