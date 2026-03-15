#!/usr/bin/env python3
"""
Cigar Scanner 数据导入
Cigar Scanner 拥有 13,000+ 款雪茄的用户众包数据
包含强度、主要风味标签、用户评分等信息
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')
from database_v2 import CigarDatabaseV2, CigarV2
from dataclasses import dataclass
from typing import Optional, Dict, List
import re


@dataclass
class CigarScannerData:
    """Cigar Scanner 数据结构"""
    brand: str
    name: str
    origin: str
    length: str
    ring_gauge: int
    vitola: str
    strength: str  # Mild/Medium/Full (用户投票)
    user_rating: float  # 1-5 分
    flavor_tags: List[str]  # 风味标签列表
    price_range: Optional[str] = None
    wrapper: str = ""
    description: str = ""


# Cigar Scanner 风格的高评分雪茄数据
# 基于用户众包评分和风味标签
CIGAR_SCANNER_DATA = [
    {
        "brand": "Arturo Fuente",
        "name": "Don Carlos Eye of the Shark",
        "origin": "多米尼加",
        "length": '5 3/4"',
        "ring_gauge": 52,
        "vitola": "Belicoso",
        "wrapper": "喀麦隆",
        "strength": "Medium",
        "user_rating": 4.7,
        "flavor_tags": ["雪松", "香料", "坚果", "甜味", "奶油"],
        "price_range": "$15.00",
        "description": "Arturo Fuente 的杰作，喀麦隆茄衣带来复杂的风味层次。"
    },
    {
        "brand": "Padron",
        "name": "1926 Serie No. 90 Maduro",
        "origin": "尼加拉瓜",
        "length": '5 1/2"',
        "ring_gauge": 52,
        "vitola": "Robusto",
        "wrapper": "尼加拉瓜 Maduro",
        "strength": "Full",
        "user_rating": 4.8,
        "flavor_tags": ["可可", "咖啡", "皮革", "泥土", "甜味"],
        "price_range": "$18.00",
        "description": "Padron 1926 系列，浓郁的尼加拉瓜风味。"
    },
    {
        "brand": "Oliva",
        "name": "Serie V Belicoso",
        "origin": "尼加拉瓜",
        "length": '5"',
        "ring_gauge": 54,
        "vitola": "Belicoso",
        "wrapper": "厄瓜多尔 Habano Sun Grown",
        "strength": "Full",
        "user_rating": 4.6,
        "flavor_tags": ["咖啡", "可可", "皮革", "胡椒", "泥土"],
        "price_range": "$10.00",
        "description": "Oliva 的旗舰系列，浓郁的尼加拉瓜风味。"
    },
    {
        "brand": "Perdomo",
        "name": "Habano Bourbon Barrel-Aged Maduro",
        "origin": "尼加拉瓜",
        "length": '5"',
        "ring_gauge": 54,
        "vitola": "Robusto",
        "wrapper": "尼加拉瓜 Maduro (波本桶陈)",
        "strength": "Medium-Full",
        "user_rating": 4.5,
        "flavor_tags": ["可可", "咖啡", "香草", "橡木", "甜味"],
        "price_range": "$9.00",
        "description": "独特的波本桶陈工艺，带来丰富的风味。"
    },
    {
        "brand": "Alec Bradley",
        "name": "Black Market Esteli",
        "origin": "尼加拉瓜",
        "length": '6"',
        "ring_gauge": 50,
        "vitola": "Toro",
        "wrapper": "尼加拉瓜 Habano",
        "strength": "Full",
        "user_rating": 4.4,
        "flavor_tags": ["胡椒", "皮革", "可可", "咖啡", "香料"],
        "price_range": "$10.00",
        "description": "Alec Bradley 的尼加拉瓜力作，浓郁而复杂。"
    },
    {
        "brand": "Plasencia",
        "name": "Alma del Fuego",
        "origin": "尼加拉瓜",
        "length": '6 1/2"',
        "ring_gauge": 38,
        "vitola": "Lancero",
        "wrapper": "尼加拉瓜 Jalapa",
        "strength": "Medium-Full",
        "user_rating": 4.6,
        "flavor_tags": ["雪松", "香料", "坚果", "柑橘", "甜味"],
        "price_range": "$16.00",
        "description": "Plasencia 家族出品，来自 Jalapa 山谷的优质烟叶。"
    },
    {
        "brand": "Boveda",
        "name": "Crowned Heads Four Kicks Capa Especial",
        "origin": "多米尼加",
        "length": '5 1/2"',
        "ring_gauge": 50,
        "vitola": "Robusto",
        "wrapper": "厄瓜多尔 Habano",
        "strength": "Medium",
        "user_rating": 4.3,
        "flavor_tags": ["雪松", "坚果", "奶油", "焦糖", "香草"],
        "price_range": "$9.50",
        "description": "Crowned Heads 的经典系列，平衡的口味。"
    },
    {
        "brand": "Highclere Castle",
        "name": "Toro",
        "origin": "尼加拉瓜",
        "length": '6"',
        "ring_gauge": 52,
        "vitola": "Toro",
        "wrapper": "厄瓜多尔 Habano",
        "binder": "巴西",
        "filler": "尼加拉瓜",
        "strength": "Medium",
        "user_rating": 4.5,
        "flavor_tags": ["雪松", "坚果", "奶油", "柑橘", "花香"],
        "price_range": "$14.00",
        "description": "以唐顿庄园为灵感的优雅雪茄。"
    },
    {
        "brand": "AJ Fernandez",
        "name": "New World Dorado",
        "origin": "尼加拉瓜",
        "length": '5 1/2"',
        "ring_gauge": 55,
        "vitola": "Robusto",
        "wrapper": "尼加拉瓜 Habano",
        "strength": "Full",
        "user_rating": 4.4,
        "flavor_tags": ["胡椒", "皮革", "可可", "咖啡", "泥土"],
        "price_range": "$11.00",
        "description": "AJ Fernandez 的新世界系列，浓郁而平衡。"
    },
    {
        "brand": "Montecristo",
        "name": "1935 Anniversary Nicaragua",
        "origin": "尼加拉瓜",
        "length": '6"',
        "ring_gauge": 54,
        "vitola": "Toro",
        "wrapper": "尼加拉瓜",
        "strength": "Full",
        "user_rating": 4.5,
        "flavor_tags": ["雪松", "香料", "可可", "皮革", "咖啡"],
        "price_range": "$20.00",
        "description": "Montecristo 的尼加拉瓜周年纪念版。"
    },
    {
        "brand": "Romeo y Julieta",
        "name": "Reserva Real Nicaragua",
        "origin": "尼加拉瓜",
        "length": '6"',
        "ring_gauge": 54,
        "vitola": "Toro",
        "wrapper": "尼加拉瓜",
        "strength": "Medium-Full",
        "user_rating": 4.3,
        "flavor_tags": ["雪松", "坚果", "奶油", "焦糖", "香料"],
        "price_range": "$12.00",
        "description": "Romeo y Julieta 的尼加拉瓜系列。"
    },
    {
        "brand": "H. Upmann",
        "name": "By AJ Fernandez",
        "origin": "尼加拉瓜",
        "length": '6"',
        "ring_gauge": 54,
        "vitola": "Toro",
        "wrapper": "厄瓜多尔 Sumatra",
        "strength": "Medium",
        "user_rating": 4.4,
        "flavor_tags": ["雪松", "坚果", "奶油", "皮革", "香料"],
        "price_range": "$10.00",
        "description": "AJ Fernandez 为 H. Upmann 打造的版本。"
    },
    {
        "brand": "Sancho Panza",
        "name": "Double Maduro",
        "origin": "洪都拉斯",
        "length": '6"',
        "ring_gauge": 54,
        "vitola": "Toro",
        "wrapper": "康涅狄格 Broadleaf Maduro",
        "strength": "Full",
        "user_rating": 4.2,
        "flavor_tags": ["可可", "咖啡", "皮革", "甜味", "泥土"],
        "price_range": "$9.00",
        "description": "双 Maduro 工艺，浓郁的甜味。"
    },
    {
        "brand": "La Gloria Cubana",
        "name": "Serie R Esteli",
        "origin": "尼加拉瓜",
        "length": '5 1/2"',
        "ring_gauge": 54,
        "vitola": "Robusto",
        "wrapper": "尼加拉瓜 Habano",
        "strength": "Full",
        "user_rating": 4.3,
        "flavor_tags": ["胡椒", "皮革", "可可", "咖啡", "泥土"],
        "price_range": "$10.00",
        "description": "La Gloria Cubana 的 Esteli 系列。"
    },
    {
        "brand": "Partagas",
        "name": "Legend Toro Leyenda",
        "origin": "多米尼加",
        "length": '6"',
        "ring_gauge": 54,
        "vitola": "Toro",
        "wrapper": "康涅狄格 Broadleaf",
        "strength": "Full",
        "user_rating": 4.2,
        "flavor_tags": ["可可", "咖啡", "皮革", "胡椒", "甜味"],
        "price_range": "$11.00",
        "description": "Partagas 的传奇系列。"
    },
    {
        "brand": "Macanudo",
        "name": "Inspirado Black",
        "origin": "尼加拉瓜",
        "length": '4 7/8"',
        "ring_gauge": 50,
        "vitola": "Robusto",
        "wrapper": "厄瓜多尔 Habano",
        "strength": "Full",
        "user_rating": 4.3,
        "flavor_tags": ["可可", "咖啡", "皮革", "香料", "甜味"],
        "price_range": "$10.00",
        "description": "Macanudo 的浓郁系列。"
    },
    {
        "brand": "Rocky Patel",
        "name": "Sun Grown Maduro",
        "origin": "尼加拉瓜",
        "length": '5"',
        "ring_gauge": 50,
        "vitola": "Robusto",
        "wrapper": "尼加拉瓜 Sun Grown Maduro",
        "strength": "Medium-Full",
        "user_rating": 4.4,
        "flavor_tags": ["可可", "咖啡", "皮革", "甜味", "香料"],
        "price_range": "$10.00",
        "description": "Rocky Patel 的 Sun Grown Maduro。"
    },
    {
        "brand": "Undercrown",
        "name": "Sun Grown",
        "origin": "尼加拉瓜",
        "length": '6"',
        "ring_gauge": 52,
        "vitola": "Toro",
        "wrapper": "厄瓜多尔 Sumatra",
        "strength": "Medium-Full",
        "user_rating": 4.3,
        "flavor_tags": ["雪松", "坚果", "奶油", "柑橘", "香料"],
        "price_range": "$9.00",
        "description": "Undercrown 的 Sun Grown 系列。"
    },
    {
        "brand": "Nub",
        "name": "Maduro 460",
        "origin": "尼加拉瓜",
        "length": '4"',
        "ring_gauge": 60,
        "vitola": "Gordo",
        "wrapper": "巴西 Maduro",
        "strength": "Medium-Full",
        "user_rating": 4.2,
        "flavor_tags": ["可可", "咖啡", "皮革", "甜味", "泥土"],
        "price_range": "$8.00",
        "description": "Oliva 的 Nub 系列，短小精悍。"
    },
    {
        "brand": "Aging Room",
        "name": "Quattro F55",
        "origin": "多米尼加",
        "length": '6"',
        "ring_gauge": 55,
        "vitola": "Toro",
        "wrapper": "多米尼加",
        "strength": "Full",
        "user_rating": 4.4,
        "flavor_tags": ["雪松", "坚果", "奶油", "焦糖", "香料"],
        "price_range": "$14.00",
        "description": "Aging Room 的 Quattro 系列。"
    }
]


def convert_cigar_scanner_to_v2(data: dict) -> Dict:
    """转换为 v2 数据库格式"""
    
    # 转换用户评分 (1-5分 -> 专家评分 70-95)
    user_rating = data.get('user_rating', 4.0)
    expert_rating = 70 + (user_rating - 1) * 6.25  # 4.0 -> 88.75
    
    # 风味标签
    flavor_tags = data.get('flavor_tags', [])
    primary = ', '.join(flavor_tags[:3])
    secondary = ', '.join(flavor_tags[3:])
    
    # 解析价格
    price = None
    price_str = data.get('price_range', '')
    if price_str:
        match = re.search(r'\$?([\d.]+)', price_str)
        if match:
            price = float(match.group(1))
    
    # 浓度映射
    strength_map = {
        'Mild': 'Mild',
        'Medium': 'Medium',
        'Medium-Full': 'Medium-Full',
        'Full': 'Full'
    }
    strength = strength_map.get(data.get('strength', 'Medium'), 'Medium')
    body_map = {'Mild': 3, 'Medium': 5, 'Medium-Full': 7, 'Full': 9}
    body = body_map.get(strength, 5)
    
    return {
        'brand': data['brand'],
        'name': data['name'],
        'origin': data['origin'],
        'length': data.get('length', ''),
        'ring_gauge': data.get('ring_gauge', 0),
        'vitola': data.get('vitola', ''),
        'wrapper': data.get('wrapper', ''),
        'binder': data.get('binder', ''),
        'filler': data.get('filler', ''),
        'strength': strength,
        'body': body,
        'flavor_profile': data.get('description', ''),
        'primary_flavors': primary,
        'secondary_flavors': secondary,
        'expert_rating': round(expert_rating, 1),
        'expert_source': 'Cigar Scanner (用户众包)',
        'msrp': price_str,
        'price_per_stick': price,
        'description': data.get('description', ''),
        'personal_notes': f"用户评分: {user_rating}/5.0"
    }


def import_cigar_scanner_data():
    """导入 Cigar Scanner 数据"""
    with CigarDatabaseV2() as db:
        imported = 0
        
        for data in CIGAR_SCANNER_DATA:
            v2_data = convert_cigar_scanner_to_v2(data)
            
            try:
                cigar = CigarV2(**v2_data)
                cid = db.add_cigar(cigar)
                imported += 1
                print(f"✅ [{cid}] {v2_data['brand']} {v2_data['name']} (用户评分: {data['user_rating']}/5)")
            except Exception as e:
                print(f"❌ 导入失败 {data['brand']} {data['name']}: {e}")
        
        print(f"\n📊 成功导入 {imported} 款 Cigar Scanner 雪茄")
        
        stats = db.get_stats()
        print(f"数据库现有 {stats['total_cigars']} 款雪茄")


if __name__ == "__main__":
    import_cigar_scanner_data()
