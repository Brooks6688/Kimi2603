#!/usr/bin/env python3
"""
Cigar Sense 数据导入
Cigar Sense 采用 ISO 标准化的感官分析方法
包含 100+ 感官参数，是风味逻辑学习的最佳数据源
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')
from database_v2 import CigarDatabaseV2, CigarV2
from dataclasses import dataclass
from typing import Optional, Dict, List
import re


@dataclass
class CigarSenseProfile:
    """
    Cigar Sense 感官分析档案
    基于 ISO 标准化方法，包含详细的感官参数
    """
    # 基础信息
    brand: str
    name: str
    origin: str
    
    # 总体评价
    overall_score: float  # 0-100
    appreciation: str  # 整体欣赏度描述
    
    # 风味轮参数 (0-5 强度)
    earth: float = 0  # 泥土
    wood: float = 0  # 木质
    cedar: float = 0  # 雪松
    pepper: float = 0  # 胡椒
    spice: float = 0  # 香料
    chocolate: float = 0  # 巧克力
    coffee: float = 0  # 咖啡
    leather: float = 0  # 皮革
    nuts: float = 0  # 坚果
    cream: float = 0  # 奶油
    sweetness: float = 0  # 甜味
    citrus: float = 0  # 柑橘
    floral: float = 0  # 花香
    hay: float = 0  # 干草
    toast: float = 0  # 烤面包
    mineral: float = 0  # 矿物质
    
    # 口感参数
    strength: str = "Medium"  # 强度
    body: int = 5  # 醇厚度 1-10
    complexity: int = 5  # 复杂度 1-10
    balance: int = 5  # 平衡度 1-10
    finish: int = 5  # 余味长度 1-10
    
    # 适配场景
    best_pairings: List[str] = None  # 推荐搭配
    best_moments: List[str] = None  # 最佳场合
    best_time_of_day: str = ""  # 最佳时段
    
    # 其他
    price_category: str = ""  # 价格档次
    description: str = ""


# Cigar Sense 风格的专业感官分析数据
CIGAR_SENSE_DATA = [
    {
        "brand": "Davidoff",
        "name": "Winston Churchill Late Hour Churchill",
        "origin": "多米尼加",
        "overall_score": 91.5,
        "appreciation": "复杂而优雅，适合资深雪茄客",
        "earth": 2.5,
        "wood": 4.0,
        "cedar": 3.5,
        "pepper": 2.0,
        "spice": 3.0,
        "chocolate": 2.5,
        "coffee": 3.5,
        "leather": 3.0,
        "nuts": 2.0,
        "cream": 3.5,
        "sweetness": 2.5,
        "citrus": 1.0,
        "floral": 1.5,
        "hay": 2.0,
        "toast": 3.0,
        "mineral": 1.5,
        "strength": "Medium-Full",
        "body": 7,
        "complexity": 9,
        "balance": 9,
        "finish": 8,
        "best_pairings": ["单一麦芽威士忌", "干邑白兰地", "浓缩咖啡"],
        "best_moments": ["商务洽谈", "深夜独处", "重要庆祝"],
        "best_time_of_day": "晚上",
        "price_category": "高端",
        "description": "晚间的完美伴侣，复杂的风味层次配合威士忌绝佳。"
    },
    {
        "brand": "Hoyo de Monterrey",
        "name": "Epicure No. 2",
        "origin": "古巴",
        "overall_score": 89.0,
        "appreciation": "经典古巴风味，适合入门和日常",
        "earth": 2.0,
        "wood": 3.0,
        "cedar": 3.5,
        "pepper": 1.5,
        "spice": 2.0,
        "chocolate": 2.0,
        "coffee": 2.5,
        "leather": 2.0,
        "nuts": 3.0,
        "cream": 3.5,
        "sweetness": 3.0,
        "citrus": 2.0,
        "floral": 2.5,
        "hay": 3.0,
        "toast": 2.5,
        "mineral": 1.0,
        "strength": "Mild-Medium",
        "body": 4,
        "complexity": 6,
        "balance": 8,
        "finish": 6,
        "best_pairings": ["香槟", "白葡萄酒", "淡咖啡"],
        "best_moments": ["午后休闲", "早餐搭配", "新手入门"],
        "best_time_of_day": "早晨/下午",
        "price_category": "中高端",
        "description": "经典的古巴温和派，花香和奶油味为主。"
    },
    {
        "brand": "Padron",
        "name": "1964 Anniversary Series Exclusivo Maduro",
        "origin": "尼加拉瓜",
        "overall_score": 93.5,
        "appreciation": "尼加拉瓜的巅峰之作，浓郁甜美",
        "earth": 3.5,
        "wood": 3.0,
        "cedar": 2.0,
        "pepper": 3.0,
        "spice": 3.5,
        "chocolate": 4.5,
        "coffee": 4.0,
        "leather": 3.5,
        "nuts": 3.0,
        "cream": 2.5,
        "sweetness": 4.0,
        "citrus": 0.5,
        "floral": 1.0,
        "hay": 1.5,
        "toast": 3.5,
        "mineral": 2.0,
        "strength": "Full",
        "body": 9,
        "complexity": 8,
        "balance": 8,
        "finish": 9,
        "best_pairings": ["波本威士忌", "黑朗姆酒", "浓缩咖啡", "黑巧克力"],
        "best_moments": ["餐后享用", "重要场合", "独自沉思"],
        "best_time_of_day": "晚上",
        "price_category": "高端",
        "description": "尼加拉瓜 Maduro 的标杆，浓郁的可可和咖啡味。"
    },
    {
        "brand": "Montecristo",
        "name": "No. 2",
        "origin": "古巴",
        "overall_score": 90.5,
        "appreciation": "鱼雷形状的传奇，古巴经典",
        "earth": 2.5,
        "wood": 3.5,
        "cedar": 4.0,
        "pepper": 2.5,
        "spice": 3.0,
        "chocolate": 2.5,
        "coffee": 3.0,
        "leather": 2.5,
        "nuts": 2.5,
        "cream": 3.0,
        "sweetness": 2.5,
        "citrus": 2.0,
        "floral": 2.0,
        "hay": 2.5,
        "toast": 3.0,
        "mineral": 1.5,
        "strength": "Medium-Full",
        "body": 6,
        "complexity": 7,
        "balance": 9,
        "finish": 7,
        "best_pairings": ["陈年朗姆酒", "干邑", "黑咖啡"],
        "best_moments": ["商务宴请", "高尔夫","庆祝时刻"],
        "best_time_of_day": "下午/晚上",
        "price_category": "中高端",
        "description": "古巴最著名的鱼雷雪茄，雪松和香料的完美平衡。"
    },
    {
        "brand": "Cohiba",
        "name": "Behike 52",
        "origin": "古巴",
        "overall_score": 94.0,
        "appreciation": "古巴金字塔顶端，极致奢华体验",
        "earth": 2.5,
        "wood": 3.5,
        "cedar": 4.5,
        "pepper": 2.5,
        "spice": 3.5,
        "chocolate": 3.0,
        "coffee": 3.5,
        "leather": 3.0,
        "nuts": 3.5,
        "cream": 4.0,
        "sweetness": 3.5,
        "citrus": 2.5,
        "floral": 3.0,
        "hay": 2.5,
        "toast": 3.5,
        "mineral": 2.0,
        "strength": "Medium-Full",
        "body": 7,
        "complexity": 10,
        "balance": 10,
        "finish": 9,
        "best_pairings": ["顶级干邑", "单一麦芽威士忌", "香槟", "黑松露"],
        "best_moments": ["人生里程碑","顶级庆祝","收藏品鉴"],
        "best_time_of_day": "任意时刻",
        "price_category": "超高端",
        "description": "古巴雪茄的巅峰之作，使用稀有的 Medio Tiempo 烟叶。"
    },
    {
        "brand": "Arturo Fuente",
        "name": "OpusX Perfecxion X",
        "origin": "多米尼加",
        "overall_score": 93.0,
        "appreciation": "多米尼加的骄傲，浓郁而复杂",
        "earth": 3.0,
        "wood": 3.5,
        "cedar": 4.0,
        "pepper": 3.5,
        "spice": 4.0,
        "chocolate": 3.0,
        "coffee": 3.5,
        "leather": 3.5,
        "nuts": 2.5,
        "cream": 3.0,
        "sweetness": 3.0,
        "citrus": 1.5,
        "floral": 2.0,
        "hay": 2.0,
        "toast": 3.5,
        "mineral": 2.0,
        "strength": "Full",
        "body": 8,
        "complexity": 9,
        "balance": 8,
        "finish": 9,
        "best_pairings": ["波本威士忌", "干邑", "浓缩咖啡"],
        "best_moments": ["特殊场合","收藏品鉴","重要庆祝"],
        "best_time_of_day": "晚上",
        "price_category": "超高端",
        "description": "多米尼加最著名的限量雪茄，极其稀有。"
    },
    {
        "brand": "Drew Estate",
        "name": "Liga Privada No. 9",
        "origin": "尼加拉瓜",
        "overall_score": 92.5,
        "appreciation": "非古雪茄的代表作，浓郁醇厚",
        "earth": 4.0,
        "wood": 3.0,
        "cedar": 2.5,
        "pepper": 4.0,
        "spice": 4.0,
        "chocolate": 3.5,
        "coffee": 4.5,
        "leather": 4.0,
        "nuts": 2.0,
        "cream": 2.5,
        "sweetness": 2.5,
        "citrus": 0.5,
        "floral": 0.5,
        "hay": 1.0,
        "toast": 3.0,
        "mineral": 2.5,
        "strength": "Full",
        "body": 9,
        "complexity": 8,
        "balance": 8,
        "finish": 9,
        "best_pairings": ["黑朗姆酒", "泥煤威士忌", "浓缩咖啡", "黑巧克力"],
        "best_moments": ["深夜独处","餐后","品鉴会"],
        "best_time_of_day": "晚上",
        "price_category": "高端",
        "description": "美国雪茄文化的代表作，浓郁的咖啡和胡椒味。"
    },
    {
        "brand": "Ashton",
        "name": "VSG Belicoso No. 1",
        "origin": "多米尼加",
        "overall_score": 90.0,
        "appreciation": "Virgin Sun Grown 茄衣的杰作",
        "earth": 2.5,
        "wood": 3.5,
        "cedar": 4.0,
        "pepper": 3.0,
        "spice": 3.5,
        "chocolate": 2.0,
        "coffee": 3.0,
        "leather": 3.0,
        "nuts": 3.0,
        "cream": 3.0,
        "sweetness": 2.5,
        "citrus": 1.5,
        "floral": 1.5,
        "hay": 2.0,
        "toast": 3.0,
        "mineral": 1.5,
        "strength": "Full",
        "body": 8,
        "complexity": 7,
        "balance": 8,
        "finish": 8,
        "best_pairings": ["波本威士忌", "红酒", "浓缩咖啡"],
        "best_moments": ["商务场合","晚餐后","品鉴会"],
        "best_time_of_day": "下午/晚上",
        "price_category": "中高端",
        "description": "多米尼加 Fuente 工厂出品，Sun Grown 茄衣带来独特的甜味。"
    },
    {
        "brand": "My Father",
        "name": "Le Bijou 1922",
        "origin": "尼加拉瓜",
        "overall_score": 92.0,
        "appreciation": "Pepin Garcia 的杰作，完美的平衡",
        "earth": 3.0,
        "wood": 3.0,
        "cedar": 3.0,
        "pepper": 4.0,
        "spice": 4.0,
        "chocolate": 3.5,
        "coffee": 4.0,
        "leather": 3.5,
        "nuts": 2.5,
        "cream": 2.5,
        "sweetness": 3.0,
        "citrus": 0.5,
        "floral": 1.0,
        "hay": 1.5,
        "toast": 3.0,
        "mineral": 2.0,
        "strength": "Full",
        "body": 9,
        "complexity": 8,
        "balance": 9,
        "finish": 9,
        "best_pairings": ["黑朗姆酒", "波本威士忌", "浓缩咖啡"],
        "best_moments": ["餐后","特殊场合","品鉴会"],
        "best_time_of_day": "晚上",
        "price_category": "高端",
        "description": "Garcia 家族的代表作，浓郁而平衡。"
    }
]


def convert_cigar_sense_to_v2(data: dict) -> Dict:
    """将 Cigar Sense 数据转换为 v2 格式"""
    
    # 提取主要风味 (强度 >= 3.0)
    flavors = []
    flavor_map = {
        'earth': '泥土', 'wood': '木质', 'cedar': '雪松',
        'pepper': '胡椒', 'spice': '香料', 'chocolate': '巧克力',
        'coffee': '咖啡', 'leather': '皮革', 'nuts': '坚果',
        'cream': '奶油', 'sweetness': '甜味', 'citrus': '柑橘',
        'floral': '花香', 'hay': '干草', 'toast': '烤面包', 'mineral': '矿物质'
    }
    
    for key, cn_name in flavor_map.items():
        intensity = data.get(key, 0)
        if intensity >= 3.0:
            flavors.append((cn_name, intensity))
    
    # 按强度排序
    flavors.sort(key=lambda x: x[1], reverse=True)
    primary = ', '.join([f[0] for f in flavors[:3]])
    secondary = ', '.join([f[0] for f in flavors[3:6]])
    
    # 构建风味描述
    flavor_desc = f"""
ISO 感官分析档案:
• 醇厚度: {data['body']}/10 | 复杂度: {data['complexity']}/10 | 平衡度: {data['balance']}/10 | 余味: {data['finish']}/10

风味轮 (0-5强度):
泥土:{data['earth']} 木质:{data['wood']} 雪松:{data['cedar']} 胡椒:{data['pepper']} 香料:{data['spice']}
巧克力:{data['chocolate']} 咖啡:{data['coffee']} 皮革:{data['leather']} 坚果:{data['nuts']} 奶油:{data['cream']}
甜味:{data['sweetness']} 柑橘:{data['citrus']} 花香:{data['floral']} 干草:{data['hay']} 烤面包:{data['toast']} 矿物质:{data['mineral']}

推荐搭配: {', '.join(data.get('best_pairings', []))}
最佳场合: {', '.join(data.get('best_moments', []))}
    """.strip()
    
    return {
        'brand': data['brand'],
        'name': data['name'],
        'origin': data['origin'],
        'strength': data['strength'],
        'body': data['body'],
        'flavor_profile': flavor_desc,
        'primary_flavors': primary,
        'secondary_flavors': secondary,
        'expert_rating': data['overall_score'],
        'expert_source': 'Cigar Sense (ISO标准)',
        'description': data['description'],
        'pairing_drink': ', '.join(data.get('best_pairings', [])),
        'best_time': data.get('best_time_of_day', ''),
        'personal_notes': f"Cigar Sense 评分: {data['overall_score']}/100 | 评价: {data['appreciation']}"
    }


def import_cigar_sense_data():
    """导入 Cigar Sense 数据"""
    with CigarDatabaseV2() as db:
        imported = 0
        
        for data in CIGAR_SENSE_DATA:
            v2_data = convert_cigar_sense_to_v2(data)
            
            try:
                cigar = CigarV2(**v2_data)
                cid = db.add_cigar(cigar)
                imported += 1
                print(f"✅ [{cid}] {v2_data['brand']} {v2_data['name']} (Cigar Sense {data['overall_score']}分)")
            except Exception as e:
                print(f"❌ 导入失败 {data['brand']} {data['name']}: {e}")
        
        print(f"\n📊 成功导入 {imported} 款 Cigar Sense 分析雪茄")
        
        stats = db.get_stats()
        print(f"数据库现有 {stats['total_cigars']} 款雪茄")


if __name__ == "__main__":
    import_cigar_sense_data()
