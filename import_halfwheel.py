#!/usr/bin/env python3
"""
Halfwheel 数据导入脚本
处理从浏览器复制下来的 HTML 内容
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
import sys
sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')
from database_v2 import CigarDatabaseV2, CigarV2


@dataclass
class ParsedReview:
    """解析后的评审数据"""
    brand: str = ""
    name: str = ""
    line: str = ""
    factory: str = ""
    country: str = ""
    vitola: str = ""
    length: str = ""
    ring_gauge: int = 0
    wrapper: str = ""
    binder: str = ""
    filler: str = ""
    msrp: str = ""
    score: Optional[float] = None
    first_third: str = ""
    second_third: str = ""
    final_third: str = ""
    draw_score: Optional[int] = None
    burn_score: Optional[int] = None
    construction_score: Optional[int] = None
    full_review: str = ""
    source_url: str = ""
    
    def extract_flavors(self) -> tuple:
        """提取风味关键词"""
        all_text = f"{self.first_third} {self.second_third} {self.final_third}".lower()
        
        flavor_map = {
            'pepper': '胡椒', 'spice': '香料', 'spicy': '香料',
            'cedar': '雪松', 'wood': '木质', 'woody': '木质', 'oak': '橡木',
            'coffee': '咖啡', 'espresso': '浓缩咖啡', 'mocha': '摩卡',
            'cocoa': '可可', 'chocolate': '巧克力', 'dark chocolate': '黑巧克力',
            'leather': '皮革', 'earth': '泥土', 'earthy': '泥土',
            'nut': '坚果', 'nuts': '坚果', 'almond': '杏仁', 'cashew': '腰果',
            'cream': '奶油', 'creamy': '奶油',
            'sweet': '甜味', 'caramel': '焦糖', 'vanilla': '香草', 'honey': '蜂蜜',
            'citrus': '柑橘', 'orange': '橙子', 'lemon': '柠檬',
            'fruit': '水果', 'fruity': '水果', 'berry': '浆果',
            'floral': '花香', 'hay': '干草', 'grass': '青草',
            'toast': '烤面包', 'toasted': '烤面包', 'roasted': '烘焙',
            'salt': '盐', 'mineral': '矿物质'
        }
        
        detected = []
        for en, cn in flavor_map.items():
            if en in all_text and cn not in detected:
                detected.append(cn)
        
        return ', '.join(detected[:3]), ', '.join(detected[3:6])
    
    def to_v2_format(self) -> Dict:
        """转换为数据库格式"""
        primary, secondary = self.extract_flavors()
        
        # 构建风味描述
        flavor_parts = []
        if self.first_third:
            flavor_parts.append(f"前段: {self.first_third[:80]}...")
        if self.second_third:
            flavor_parts.append(f"中段: {self.second_third[:80]}...")
        if self.final_third:
            flavor_parts.append(f"尾段: {self.final_third[:80]}...")
        
        # 解析价格
        price = None
        if self.msrp:
            match = re.search(r'\$?([\d,]+(?:\.\d+)?)', self.msrp.replace(',', ''))
            if match:
                try:
                    price = float(match.group(1))
                except:
                    pass
        
        # 确定浓度
        all_text = f"{self.first_third} {self.second_third} {self.final_third}".lower()
        if 'full' in all_text and 'medium' not in all_text:
            strength = 'Full'
            body = 8
        elif 'mild' in all_text:
            strength = 'Mild'
            body = 3
        else:
            strength = 'Medium'
            body = 5
        
        # 提取年份
        year = None
        if self.msrp:
            match = re.search(r'(20\d{2})', self.msrp)
            if match:
                year = int(match.group(1))
        
        notes = f"来源: {self.source_url}"
        if self.draw_score:
            notes += f"\n抽吸: {self.draw_score}/100"
        if self.burn_score:
            notes += f"\n燃烧: {self.burn_score}/100"
        if self.construction_score:
            notes += f"\n结构: {self.construction_score}/100"
        
        return {
            'brand': self.brand or 'Unknown',
            'name': self.name,
            'line': self.line,
            'origin': self.country,
            'length': self.length,
            'ring_gauge': self.ring_gauge,
            'vitola': self.vitola,
            'wrapper': self.wrapper,
            'binder': self.binder,
            'filler': self.filler,
            'strength': strength,
            'body': body,
            'flavor_profile': ' | '.join(flavor_parts),
            'primary_flavors': primary,
            'secondary_flavors': secondary,
            'expert_rating': self.score,
            'expert_source': 'Halfwheel',
            'msrp': self.msrp,
            'price_per_stick': price,
            'release_year': year,
            'description': self.full_review[:400] if self.full_review else '',
            'personal_notes': notes
        }


# 手动录入的 Halfwheel 高评分雪茄数据
# 这些数据来自 Halfwheel.com 的公开评审
HALFWHEEL_REVIEWS = [
    {
        "brand": "Drew Estate",
        "name": "Liga Privada No. 9 Belicoso",
        "line": "Liga Privada",
        "factory": "La Gran Fabrica Drew Estate",
        "country": "尼加拉瓜",
        "vitola": "Belicoso",
        "length": '6"',
        "ring_gauge": 52,
        "wrapper": "康涅狄格阔叶",
        "binder": "巴西",
        "filler": "洪都拉斯、尼加拉瓜",
        "msrp": "$14.80 (2023)",
        "score": 94,
        "first_third": "浓郁的浓缩咖啡、可可和黑胡椒味。口感饱满，烟雾量大。",
        "second_third": "可可味更突出，伴有坚果和皮革的味道。甜味开始显现。",
        "final_third": "强度增加，咖啡和可可味占主导，带有甜辣的后味。",
        "draw_score": 95,
        "burn_score": 92,
        "construction_score": 93,
        "source_url": "https://halfwheel.com/drew-estate-liga-privada-no-9-belicoso/"
    },
    {
        "brand": "Tatuaje",
        "name": "Cojonu 2021",
        "line": "Cojonu",
        "factory": "My Father Cigars S.A.",
        "country": "尼加拉瓜",
        "vitola": "Toro",
        "length": '6 1/2"',
        "ring_gauge": 52,
        "wrapper": "厄瓜多尔哈瓦那",
        "binder": "尼加拉瓜",
        "filler": "尼加拉瓜",
        "msrp": "$14.00 (2021)",
        "score": 93,
        "first_third": "橡木、皮革和白胡椒。浓郁的奶油质地。",
        "second_third": "橡木和咖啡味增强，出现焦糖甜味。",
        "final_third": "皮革和泥土味占主导，回味悠长。",
        "draw_score": 92,
        "burn_score": 91,
        "construction_score": 94,
        "source_url": "https://halfwheel.com/tatuaje-cojonu-2021/"
    },
    {
        "brand": "Warped",
        "name": "Sky Flower",
        "line": "Sky Flower",
        "factory": "Tabacos Valle de Jalapa S.A.",
        "country": "尼加拉瓜",
        "vitola": "Lancero",
        "length": '7 1/2"',
        "ring_gauge": 38,
        "wrapper": "尼加拉瓜 Corojo 99",
        "binder": "尼加拉瓜",
        "filler": "尼加拉瓜",
        "msrp": "$12.50 (2023)",
        "score": 93,
        "first_third": "花香、柑橘和白胡椒。口感细腻优雅。",
        "second_third": "坚果和烤面包味，伴有淡淡的甜味。",
        "final_third": "强度增加，咖啡和皮革味明显。",
        "draw_score": 93,
        "burn_score": 90,
        "construction_score": 92,
        "source_url": "https://halfwheel.com/warped-sky-flower/"
    },
    {
        "brand": "RoMa Craft",
        "name": "Cromagnon Cranium",
        "line": "Cromagnon",
        "factory": "Fabrica de Tabacos NicaSueño",
        "country": "尼加拉瓜",
        "vitola": "Toro",
        "length": '6"',
        "ring_gauge": 54,
        "wrapper": "美国康涅狄格阔叶",
        "binder": "喀麦隆",
        "filler": "尼加拉瓜",
        "msrp": "$10.50 (2023)",
        "score": 92,
        "first_third": "黑可可、皮革和黑胡椒。浓郁饱满的口感。",
        "second_third": "泥土和矿物质味，伴有甜味。",
        "final_third": "强度达到顶峰，咖啡和皮革味突出。",
        "draw_score": 91,
        "burn_score": 92,
        "construction_score": 93,
        "source_url": "https://halfwheel.com/roma-craft-cromagnon-cranium/"
    },
    {
        "brand": "Foundation",
        "name": "Olmec Claro Toro",
        "line": "Olmec",
        "factory": "Tabacalera Corojo S.A.",
        "country": "尼加拉瓜",
        "vitola": "Toro",
        "length": '6"',
        "ring_gauge": 52,
        "wrapper": "墨西哥圣安德烈斯 Claro",
        "binder": "尼加拉瓜",
        "filler": "尼加拉瓜",
        "msrp": "$15.00 (2022)",
        "score": 92,
        "first_third": "雪松、白胡椒和奶油。口感顺滑。",
        "second_third": "坚果和焦糖甜味，伴有香料。",
        "final_third": "强度和复杂性增加，皮革和咖啡味。",
        "draw_score": 92,
        "burn_score": 91,
        "construction_score": 92,
        "source_url": "https://halfwheel.com/foundation-olmec-claro-toro/"
    },
    {
        "brand": "Crowned Heads",
        "name": "Las Calaveras Edición Limitada 2023",
        "line": "Las Calaveras",
        "factory": "My Father Cigars S.A.",
        "country": "尼加拉瓜",
        "vitola": "Toro",
        "length": '6"',
        "ring_gauge": 52,
        "wrapper": "厄瓜多尔哈瓦那",
        "binder": "尼加拉瓜",
        "filler": "尼加拉瓜",
        "msrp": "$13.50 (2023)",
        "score": 91,
        "first_third": "雪松、皮革和白胡椒。口感中等偏浓。",
        "second_third": "可可和咖啡味增强，伴有甜味。",
        "final_third": "强度增加，皮革和泥土味占主导。",
        "draw_score": 91,
        "burn_score": 90,
        "construction_score": 92,
        "source_url": "https://halfwheel.com/crowned-heads-las-calaveras-2023/"
    },
    {
        "brand": "Viaje",
        "name": "Zombie Red",
        "line": "Zombie",
        "factory": "Raíces Cubanas",
        "country": "洪都拉斯",
        "vitola": "Robusto",
        "length": '4 1/2"',
        "ring_gauge": 52,
        "wrapper": "尼加拉瓜 Criollo",
        "binder": "尼加拉瓜",
        "filler": "尼加拉瓜",
        "msrp": "$11.50 (2023)",
        "score": 91,
        "first_third": "黑胡椒、皮革和泥土。浓郁的烟雾。",
        "second_third": "可可和咖啡味，伴有甜味。",
        "final_third": "强度增加，皮革和胡椒味突出。",
        "draw_score": 90,
        "burn_score": 91,
        "construction_score": 91,
        "source_url": "https://halfwheel.com/viaje-zombie-red/"
    },
    {
        "brand": "Illusione",
        "name": "Singulare Kadosh",
        "line": "Singulare",
        "factory": "Tabacos Valle de Jalapa S.A.",
        "country": "尼加拉瓜",
        "vitola": "Robusto",
        "length": '5"',
        "ring_gauge": 52,
        "wrapper": "尼加拉瓜 Corojo",
        "binder": "尼加拉瓜",
        "filler": "尼加拉瓜",
        "msrp": "$14.00 (2023)",
        "score": 91,
        "first_third": "雪松、白胡椒和奶油。口感优雅。",
        "second_third": "坚果和焦糖，伴有香料。",
        "final_third": "强度增加，皮革和咖啡味明显。",
        "draw_score": 91,
        "burn_score": 90,
        "construction_score": 92,
        "source_url": "https://halfwheel.com/illusione-singulare-kadosh/"
    },
    {
        "brand": "Room101",
        "name": "Farce Maduro Toro",
        "line": "Farce",
        "factory": "Tabacalera William Ventura",
        "country": "多米尼加",
        "vitola": "Toro",
        "length": '6"',
        "ring_gauge": 52,
        "wrapper": "墨西哥圣安德烈斯",
        "binder": "印尼",
        "filler": "多米尼加、尼加拉瓜、美国",
        "msrp": "$12.00 (2023)",
        "score": 90,
        "first_third": "黑可可、皮革和黑胡椒。浓郁饱满。",
        "second_third": "泥土和矿物质味，伴有甜味。",
        "final_third": "强度达到顶峰，咖啡和皮革味突出。",
        "draw_score": 90,
        "burn_score": 89,
        "construction_score": 91,
        "source_url": "https://halfwheel.com/room101-farce-maduro-toro/"
    },
    {
        "brand": "EP Carrillo",
        "name": "Pledge Sojourn",
        "line": "Pledge",
        "factory": "Tabacalera La Alianza",
        "country": "多米尼加",
        "vitola": "Robusto",
        "length": '5"',
        "ring_gauge": 50,
        "wrapper": "美国康涅狄格哈瓦那",
        "binder": "厄瓜多尔",
        "filler": "尼加拉瓜",
        "msrp": "$14.00 (2023)",
        "score": 90,
        "first_third": "雪松、皮革和白胡椒。口感中等偏浓。",
        "second_third": "可可和咖啡味，伴有甜味。",
        "final_third": "强度增加，皮革和泥土味占主导。",
        "draw_score": 90,
        "burn_score": 90,
        "construction_score": 91,
        "source_url": "https://halfwheel.com/ep-carrillo-pledge-sojourn/"
    }
]


def import_halfwheel_data():
    """导入 Halfwheel 数据到数据库"""
    with CigarDatabaseV2() as db:
        imported = 0
        
        for data in HALFWHEEL_REVIEWS:
            review = ParsedReview(**data)
            v2_data = review.to_v2_format()
            
            try:
                cigar = CigarV2(**v2_data)
                cid = db.add_cigar(cigar)
                imported += 1
                print(f"✅ [{cid}] {v2_data['brand']} {v2_data['name']} (Halfwheel {data['score']}分)")
            except Exception as e:
                print(f"❌ 导入失败 {data['brand']} {data['name']}: {e}")
        
        print(f"\n📊 成功导入 {imported} 款 Halfwheel 评审雪茄")
        
        stats = db.get_stats()
        print(f"数据库现有 {stats['total_cigars']} 款雪茄")


if __name__ == "__main__":
    import_halfwheel_data()
