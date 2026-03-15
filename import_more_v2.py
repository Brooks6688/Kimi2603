#!/usr/bin/env python3
"""
继续从 PDF 提取更多雪茄数据并导入 v2
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')
from database_v2 import CigarDatabaseV2, CigarV2

# 风味关键词映射
FLAVOR_MAPPING = {
    '雪松': 'cedar', '木质': 'wood', '橡木': 'oak',
    '焦糖': 'caramel', '蜂蜜': 'honey', '红糖': 'brown_sugar', 
    '香草': 'vanilla', '奶油': 'cream', '甜味': 'sweet',
    '杏仁': 'almond', '核桃': 'walnut', '坚果': 'nuts', '山核桃': 'pecan',
    '开心果': 'pistachio',
    '咖啡': 'coffee', '可可': 'cocoa', '巧克力': 'chocolate', '浓缩咖啡': 'espresso',
    '胡椒': 'pepper', '香料': 'spice', '肉桂': 'cinnamon', '茴香': 'anise',
    '泥土': 'earth', '矿物质': 'mineral', '皮革': 'leather',
    '水果': 'fruit', '苹果': 'apple', '樱桃': 'cherry', '柑橘': 'citrus', 
    '葡萄干': 'raisin', '枣': 'dates', '热带水果': 'tropical_fruit',
    '花香': 'floral', '烤面包': 'toast', '烧烤': 'bbq', '烟熏': 'smoky',
    '糖蜜': 'molasses', '牛轧糖': 'nougat'
}

STRENGTH_MAP = {
    'Mild': ('Mild', 3),
    'Mild-Medium': ('Mild-Medium', 4),
    'Medium': ('Medium', 5),
    'Medium-Full': ('Medium-Full', 7),
    'Full': ('Full', 9)
}

def parse_flavors(flavor_text):
    """解析风味文本"""
    if not flavor_text:
        return '', ''
    flavors = []
    for cn, en in FLAVOR_MAPPING.items():
        if cn in flavor_text:
            flavors.append(en)
    primary = ', '.join(flavors[:3])
    secondary = ', '.join(flavors[3:6])
    return primary, secondary

# 从 PDF 第 9 页开始提取的雪茄数据
cigars_from_pdf = [
    # Page 9
    {
        'brand': 'Drew Estate',
        'name': 'Liga Privada T52 Toro',
        'origin': '尼加拉瓜',
        'length': '152mm (6")',
        'ring_gauge': 52,
        'wrapper': '美国康涅狄格',
        'binder': '巴西',
        'filler': '洪都拉斯、尼加拉瓜',
        'strength': 'Medium-Full',
        'body': 7,
        'flavor_profile': '黑胡椒、皮革、浓缩咖啡、可可、泥土',
        'expert_rating': 92,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 15.50,
        'vitola': 'Toro'
    },
    {
        'brand': 'My Father',
        'name': 'Le Bijou 1922 Torpedo Box Pressed',
        'origin': '尼加拉瓜',
        'length': '159mm (6 1/4")',
        'ring_gauge': 52,
        'wrapper': '厄瓜多尔',
        'binder': '尼加拉瓜',
        'filler': '尼加拉瓜',
        'strength': 'Full',
        'body': 9,
        'flavor_profile': '浓郁的可可、皮革、浓缩咖啡、黑胡椒、甜味',
        'expert_rating': 94,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 18.00,
        'vitola': 'Torpedo'
    },
    {
        'brand': 'Tatuaje',
        'name': 'Fausto FT127',
        'origin': '尼加拉瓜',
        'length': '127mm (5")',
        'ring_gauge': 54,
        'wrapper': '厄瓜多尔',
        'binder': '尼加拉瓜',
        'filler': '尼加拉瓜',
        'strength': 'Full',
        'body': 9,
        'flavor_profile': '胡椒、皮革、可可、泥土、浓缩咖啡',
        'expert_rating': 91,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 12.00,
        'vitola': 'Robusto'
    },
    {
        'brand': 'Fuente Fuente',
        'name': 'OpusX Perfecxion X',
        'origin': '多米尼加',
        'length': '165mm (6 1/2")',
        'ring_gauge': 48,
        'wrapper': '多米尼加',
        'binder': '多米尼加',
        'filler': '多米尼加',
        'strength': 'Full',
        'body': 9,
        'flavor_profile': '甜味、雪松、香料、皮革、可可',
        'expert_rating': 95,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 35.00,
        'vitola': 'Toro',
        'limited_edition': True
    },
    {
        'brand': 'Romeo y Julieta',
        'name': 'Churchill Tubo',
        'origin': '古巴',
        'length': '178mm (7")',
        'ring_gauge': 47,
        'wrapper': '古巴',
        'binder': '古巴',
        'filler': '古巴',
        'strength': 'Medium',
        'body': 5,
        'flavor_profile': '花香、雪松、坚果、蜂蜜',
        'expert_rating': 90,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 25.00,
        'vitola': 'Churchill'
    },
    # Page 10
    {
        'brand': 'San Cristobal',
        'name': 'Quintessence Robusto',
        'origin': '尼加拉瓜',
        'length': '127mm (5")',
        'ring_gauge': 50,
        'wrapper': '厄瓜多尔',
        'binder': '尼加拉瓜',
        'filler': '尼加拉瓜',
        'strength': 'Medium-Full',
        'body': 7,
        'flavor_profile': '可可、皮革、浓缩咖啡、香料、奶油',
        'expert_rating': 91,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 14.00,
        'vitola': 'Robusto'
    },
    {
        'brand': 'E.P. Carrillo',
        'name': 'Encore Majestic',
        'origin': '多米尼加',
        'length': '146mm (5 3/4")',
        'ring_gauge': 52,
        'wrapper': '尼加拉瓜',
        'binder': '尼加拉瓜',
        'filler': '尼加拉瓜',
        'strength': 'Medium-Full',
        'body': 7,
        'flavor_profile': '雪松、可可、香料、皮革、坚果',
        'expert_rating': 93,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 16.50,
        'vitola': 'Robusto'
    },
    {
        'brand': 'Undercrown',
        'name': 'Maduro Gran Toro',
        'origin': '尼加拉瓜',
        'length': '152mm (6")',
        'ring_gauge': 52,
        'wrapper': '墨西哥',
        'binder': '尼加拉瓜',
        'filler': '尼加拉瓜',
        'strength': 'Medium-Full',
        'body': 7,
        'flavor_profile': '可可、浓缩咖啡、皮革、泥土、香料',
        'expert_rating': 90,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 11.00,
        'vitola': 'Toro'
    },
    {
        'brand': 'Aging Room',
        'name': 'Quattro Nicaragua Maestro',
        'origin': '尼加拉瓜',
        'length': '152mm (6")',
        'ring_gauge': 52,
        'wrapper': '尼加拉瓜',
        'binder': '尼加拉瓜',
        'filler': '尼加拉瓜',
        'strength': 'Medium-Full',
        'body': 7,
        'flavor_profile': '雪松、可可、香料、坚果、皮革',
        'expert_rating': 92,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 17.00,
        'vitola': 'Toro'
    },
    {
        'brand': 'La Flor Dominicana',
        'name': 'Double Ligero Chisel',
        'origin': '多米尼加',
        'length': '152mm (6")',
        'ring_gauge': 54,
        'wrapper': '厄瓜多尔',
        'binder': '多米尼加',
        'filler': '多米尼加',
        'strength': 'Full',
        'body': 10,
        'flavor_profile': '胡椒、皮革、浓缩咖啡、可可、泥土',
        'expert_rating': 91,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 16.00,
        'vitola': 'Toro'
    },
    # 更多高端雪茄
    {
        'brand': 'Cohiba',
        'name': 'Siglo VI',
        'origin': '古巴',
        'length': '150mm (5 7/8")',
        'ring_gauge': 52,
        'wrapper': '古巴',
        'binder': '古巴',
        'filler': '古巴',
        'strength': 'Medium',
        'body': 6,
        'flavor_profile': '雪松、蜂蜜、可可、香料、奶油',
        'expert_rating': 93,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 45.00,
        'vitola': 'Toro'
    },
    {
        'brand': 'Trinidad',
        'name': 'Fundadores',
        'origin': '古巴',
        'length': '192mm (7 1/2")',
        'ring_gauge': 40,
        'wrapper': '古巴',
        'binder': '古巴',
        'filler': '古巴',
        'strength': 'Medium',
        'body': 5,
        'flavor_profile': '花香、雪松、蜂蜜、可可、坚果',
        'expert_rating': 92,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 35.00,
        'vitola': 'Lonsdale'
    },
    {
        'brand': 'Bolivar',
        'name': 'Royal Corona',
        'origin': '古巴',
        'length': '124mm (4 7/8")',
        'ring_gauge': 50,
        'wrapper': '古巴',
        'binder': '古巴',
        'filler': '古巴',
        'strength': 'Full',
        'body': 8,
        'flavor_profile': '泥土、皮革、可可、胡椒、浓缩咖啡',
        'expert_rating': 91,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 22.00,
        'vitola': 'Robusto'
    },
    {
        'brand': 'Hoyo de Monterrey',
        'name': 'Double Corona',
        'origin': '古巴',
        'length': '194mm (7 5/8")',
        'ring_gauge': 49,
        'wrapper': '古巴',
        'binder': '古巴',
        'filler': '古巴',
        'strength': 'Medium',
        'body': 5,
        'flavor_profile': '雪松、奶油、蜂蜜、花香、可可',
        'expert_rating': 90,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 28.00,
        'vitola': 'Double Corona'
    },
    {
        'brand': 'Joya de Nicaragua',
        'name': 'Antano 1970 Gran Consul',
        'origin': '尼加拉瓜',
        'length': '120mm (4 3/4")',
        'ring_gauge': 60,
        'wrapper': '尼加拉瓜',
        'binder': '尼加拉瓜',
        'filler': '尼加拉瓜',
        'strength': 'Full',
        'body': 10,
        'flavor_profile': '胡椒、皮革、泥土、可可、浓缩咖啡',
        'expert_rating': 90,
        'expert_source': 'Cigar Aficionado',
        'price_per_stick': 10.00,
        'vitola': 'Gordo'
    }
]

def import_cigars():
    with CigarDatabaseV2() as db:
        count = 0
        for data in cigars_from_pdf:
            # 解析风味
            primary, secondary = parse_flavors(data.get('flavor_profile', ''))
            data['primary_flavors'] = primary
            data['secondary_flavors'] = secondary
            
            # 解析强度
            strength = data.get('strength', 'Medium')
            data['strength'] = strength
            
            cigar = CigarV2(**data)
            cid = db.add_cigar(cigar)
            count += 1
            print(f"✅ 已添加: {data['brand']} {data['name']} (评分: {data.get('expert_rating', 'N/A')}) - ID: {cid}")
        
        print(f"\n📊 成功导入 {count} 款雪茄")
        
        stats = db.get_stats()
        print(f"数据库现有 {stats['total_cigars']} 款雪茄")

if __name__ == "__main__":
    import_cigars()
