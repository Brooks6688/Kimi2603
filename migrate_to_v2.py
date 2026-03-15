#!/usr/bin/env python3
"""
迁移旧数据库数据到 v2，并继续完善
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')
from database import CigarDatabase, Cigar
from database_v2 import CigarDatabaseV2, CigarV2

# 风味关键词映射表
FLAVOR_MAPPING = {
    # 木质/雪松
    '雪松': 'cedar', '木质': 'wood', '橡木': 'oak',
    # 甜味
    '焦糖': 'caramel', '蜂蜜': 'honey', '红糖': 'brown_sugar', 
    '香草': 'vanilla', '奶油': 'cream', '甜味': 'sweet',
    # 坚果
    '杏仁': 'almond', '核桃': 'walnut', '坚果': 'nuts', '山核桃': 'pecan',
    # 咖啡/可可
    '咖啡': 'coffee', '可可': 'cocoa', '巧克力': 'chocolate', '浓缩咖啡': 'espresso',
    # 香料
    '胡椒': 'pepper', '香料': 'spice', '肉桂': 'cinnamon', '茴香': 'anise',
    # 泥土/矿物
    '泥土': 'earth', '矿物质': 'mineral', '皮革': 'leather',
    # 水果
    '水果': 'fruit', '苹果': 'apple', '樱桃': 'cherry', '柑橘': 'citrus', '葡萄干': 'raisin',
    # 其他
    '花香': 'floral', '烤面包': 'toast', '烧烤': 'bbq', '烟熏': 'smoky'
}

# 强度映射
STRENGTH_MAP = {
    '轻度': ('Mild', 3),
    '轻度-中等': ('Mild-Medium', 4),
    '中等': ('Medium', 5),
    '中等偏浓': ('Medium-Full', 7),
    '浓郁': ('Full', 9)
}

def parse_flavors(flavor_text: str) -> tuple:
    """解析风味文本，提取主要和次要风味"""
    if not flavor_text:
        return '', ''
    
    flavors = []
    for cn, en in FLAVOR_MAPPING.items():
        if cn in flavor_text:
            flavors.append(en)
    
    # 前3个为主要风味，其余为次要
    primary = ', '.join(flavors[:3])
    secondary = ', '.join(flavors[3:])
    return primary, secondary

def migrate_data():
    """从 v1 迁移数据到 v2"""
    print("🔄 开始数据迁移...")
    
    with CigarDatabase() as old_db:
        old_cigars = old_db.list_cigars()
        print(f"找到 {len(old_cigars)} 款旧数据雪茄")
    
    migrated = 0
    with CigarDatabaseV2() as new_db:
        for old in old_cigars:
            # 解析风味
            primary, secondary = parse_flavors(old.get('flavor_profile', ''))
            
            # 解析强度
            strength_cn = old.get('strength', '')
            strength_en, body = STRENGTH_MAP.get(strength_cn, ('Medium', 5))
            
            # 提取价格数字
            price_str = old.get('price_range', '')
            price_num = None
            if '$' in price_str:
                try:
                    price_num = float(price_str.replace('$', '').replace('£', '').split()[0])
                except:
                    pass
            
            # 转换专家评分
            expert_rating = old.get('rating')
            if expert_rating:
                expert_rating = expert_rating * 10  # 1-10 -> 90-100
            
            # 创建 v2 雪茄对象
            cigar = CigarV2(
                brand=old.get('brand', ''),
                name=old.get('name', ''),
                origin=old.get('origin', ''),
                length=old.get('length', ''),
                ring_gauge=old.get('ring_gauge', 0),
                wrapper=old.get('wrapper', ''),
                binder=old.get('binder', ''),
                filler=old.get('filler', ''),
                strength=strength_en,
                body=body,
                flavor_profile=old.get('flavor_profile', ''),
                primary_flavors=primary,
                secondary_flavors=secondary,
                expert_rating=expert_rating,
                user_rating=old.get('rating'),
                price_per_stick=price_num,
                msrp=old.get('price_range', ''),
                smoked_count=old.get('smoked_count', 0),
                personal_notes=old.get('notes', '')
            )
            
            new_db.add_cigar(cigar)
            migrated += 1
            print(f"✅ 已迁移: {cigar.brand} {cigar.name}")
        
        print(f"\n📊 成功迁移 {migrated} 款雪茄到 v2 数据库")
        
        stats = new_db.get_stats()
        print(f"v2 数据库现有 {stats['total_cigars']} 款雪茄")

if __name__ == "__main__":
    migrate_data()
