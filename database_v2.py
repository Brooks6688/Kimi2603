#!/usr/bin/env python3
"""
雪茄数据库 v2 - 扩展版
支持更详细的风味分析和推荐功能
"""

import sqlite3
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
import math

# 数据库路径
DB_PATH = Path(__file__).parent / "cigars_v2.db"


@dataclass
class CigarV2:
    """增强版雪茄数据模型"""
    # 基础信息
    id: Optional[int] = None
    brand: str = ""  # 品牌
    name: str = ""  # 型号/名称
    line: str = ""  # 系列/产品线
    origin: str = ""  # 产地
    factory: str = ""  # 工厂
    
    # 物理参数
    length: str = ""  # 长度 (mm)
    ring_gauge: int = 0  # 环径
    vitola: str = ""  # 雪茄形状/尺寸类型
    
    # 烟叶成分
    wrapper: str = ""  # 茄衣
    wrapper_origin: str = ""  # 茄衣产地
    binder: str = ""  # 茄套
    binder_origin: str = ""  # 茄套产地
    filler: str = ""  # 茄芯
    filler_origin: str = ""  # 茄芯产地
    
    # 风味档案 (0-10评分)
    strength: str = ""  # 整体浓度 (轻度/中等/浓郁)
    body: int = 0  # 醇厚度 1-10
    
    # 主要风味标签 (逗号分隔)
    flavor_profile: str = ""  # 风味描述
    primary_flavors: str = ""  # 主要风味 (如: 雪松、可可、胡椒)
    secondary_flavors: str = ""  # 次要风味
    finish_notes: str = ""  # 余味
    
    # 评分系统
    expert_rating: Optional[float] = None  # 专家评分 (如 CA 93分)
    expert_source: str = ""  # 评分来源 (Cigar Aficionado/Halfwheel等)
    user_rating: Optional[int] = None  # 个人评分 1-10
    
    # 价格信息
    msrp: str = ""  # 厂商指导价
    current_price: str = ""  # 当前市场价
    price_per_stick: Optional[float] = None  # 单支价格
    price_per_box: Optional[float] = None  # 整盒价格
    currency: str = "USD"  # 货币
    
    # 品鉴建议
    pairing_drink: str = ""  # 推荐搭配饮品
    best_time: str = ""  # 最佳吸食时段
    smoke_duration: str = ""  # 预计抽吸时长
    
    # 其他
    description: str = ""  # 详细描述
    release_year: Optional[int] = None  # 发布年份
    limited_edition: bool = False  # 是否限量版
    availability: str = ""  # 可获得性 (常规/限量/停产)
    
    # 个人记录
    personal_notes: str = ""  # 个人备注
    smoked_count: int = 0  # 已抽数量
    in_humidor: bool = False  # 是否在保湿盒中
    quantity_owned: int = 0  # 拥有数量
    
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CigarDatabaseV2:
    """增强版雪茄数据库管理类"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()
        
        # 雪茄主表 (增强版)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cigars_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                name TEXT NOT NULL,
                line TEXT,
                origin TEXT,
                factory TEXT,
                length TEXT,
                ring_gauge INTEGER,
                vitola TEXT,
                wrapper TEXT,
                wrapper_origin TEXT,
                binder TEXT,
                binder_origin TEXT,
                filler TEXT,
                filler_origin TEXT,
                strength TEXT,
                body INTEGER CHECK(body >= 0 AND body <= 10),
                flavor_profile TEXT,
                primary_flavors TEXT,
                secondary_flavors TEXT,
                finish_notes TEXT,
                expert_rating REAL,
                expert_source TEXT,
                user_rating INTEGER CHECK(user_rating >= 1 AND user_rating <= 10),
                msrp TEXT,
                current_price TEXT,
                price_per_stick REAL,
                price_per_box REAL,
                currency TEXT DEFAULT 'USD',
                pairing_drink TEXT,
                best_time TEXT,
                smoke_duration TEXT,
                description TEXT,
                release_year INTEGER,
                limited_edition BOOLEAN DEFAULT 0,
                availability TEXT,
                personal_notes TEXT,
                smoked_count INTEGER DEFAULT 0,
                in_humidor BOOLEAN DEFAULT 0,
                quantity_owned INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 风味标签表 (用于推荐)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flavor_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cigar_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                intensity INTEGER CHECK(intensity >= 1 AND intensity <= 10),
                FOREIGN KEY (cigar_id) REFERENCES cigars_v2(id) ON DELETE CASCADE
            )
        """)
        
        # 品鉴记录表 (增强版)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasting_notes_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cigar_id INTEGER NOT NULL,
                smoke_date TEXT DEFAULT CURRENT_TIMESTAMP,
                duration_minutes INTEGER,
                draw TEXT,
                burn TEXT,
                ash TEXT,
                strength_perceived INTEGER,
                complexity INTEGER,
                
                -- 风味记录
                earth INTEGER,
                wood INTEGER,
                cedar INTEGER,
                pepper INTEGER,
                spice INTEGER,
                chocolate INTEGER,
                coffee INTEGER,
                leather INTEGER,
                nuts INTEGER,
                cream INTEGER,
                sweetness INTEGER,
                citrus INTEGER,
                floral INTEGER,
                
                flavor_notes TEXT,
                overall_rating INTEGER,
                pairing TEXT,
                mood TEXT,
                notes TEXT,
                FOREIGN KEY (cigar_id) REFERENCES cigars_v2(id) ON DELETE CASCADE
            )
        """)
        
        # 价格追踪表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cigar_id INTEGER NOT NULL,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                price REAL,
                source TEXT,
                currency TEXT,
                FOREIGN KEY (cigar_id) REFERENCES cigars_v2(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def add_cigar(self, cigar: CigarV2) -> int:
        """添加新雪茄"""
        cursor = self.conn.cursor()
        
        fields = [
            'brand', 'name', 'line', 'origin', 'factory',
            'length', 'ring_gauge', 'vitola',
            'wrapper', 'wrapper_origin', 'binder', 'binder_origin', 'filler', 'filler_origin',
            'strength', 'body', 'flavor_profile', 'primary_flavors', 'secondary_flavors', 'finish_notes',
            'expert_rating', 'expert_source', 'user_rating',
            'msrp', 'current_price', 'price_per_stick', 'price_per_box', 'currency',
            'pairing_drink', 'best_time', 'smoke_duration',
            'description', 'release_year', 'limited_edition', 'availability',
            'personal_notes', 'smoked_count', 'in_humidor', 'quantity_owned'
        ]
        
        placeholders = ', '.join(['?' for _ in fields])
        field_names = ', '.join(fields)
        
        values = [getattr(cigar, f) for f in fields]
        
        cursor.execute(f"""
            INSERT INTO cigars_v2 ({field_names}, updated_at)
            VALUES ({placeholders}, CURRENT_TIMESTAMP)
        """, values)
        
        self.conn.commit()
        return cursor.lastrowid
    
    def search_cigars(self, 
                     brand: str = None,
                     origin: str = None,
                     strength: str = None,
                     flavor: str = None,
                     min_rating: float = None,
                     max_price: float = None,
                     pairing: str = None) -> List[Dict]:
        """高级搜索功能"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM cigars_v2 WHERE 1=1"
        params = []
        
        if brand:
            query += " AND brand LIKE ?"
            params.append(f"%{brand}%")
        if origin:
            query += " AND origin LIKE ?"
            params.append(f"%{origin}%")
        if strength:
            query += " AND strength = ?"
            params.append(strength)
        if flavor:
            query += " AND (primary_flavors LIKE ? OR secondary_flavors LIKE ? OR flavor_profile LIKE ?)"
            params.extend([f"%{flavor}%", f"%{flavor}%", f"%{flavor}%"])
        if min_rating:
            query += " AND (expert_rating >= ? OR user_rating >= ?)"
            params.extend([min_rating, min_rating])
        if max_price:
            query += " AND price_per_stick <= ?"
            params.append(max_price)
        if pairing:
            query += " AND pairing_drink LIKE ?"
            params.append(f"%{pairing}%")
        
        query += " ORDER BY expert_rating DESC NULLS LAST, user_rating DESC NULLS LAST"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def recommend_by_flavor(self, liked_cigar_id: int, limit: int = 5) -> List[Dict]:
        """基于风味相似度推荐雪茄"""
        cursor = self.conn.cursor()
        
        # 获取参考雪茄的风味标签
        cursor.execute("SELECT primary_flavors, secondary_flavors, strength FROM cigars_v2 WHERE id = ?", (liked_cigar_id,))
        ref = cursor.fetchone()
        if not ref:
            return []
        
        ref_flavors = set((ref['primary_flavors'] or '').split(',') + (ref['secondary_flavors'] or '').split(','))
        ref_flavors = {f.strip().lower() for f in ref_flavors if f.strip()}
        ref_strength = ref['strength']
        
        # 获取所有其他雪茄
        cursor.execute("SELECT * FROM cigars_v2 WHERE id != ?", (liked_cigar_id,))
        all_cigars = [dict(row) for row in cursor.fetchall()]
        
        # 计算相似度
        scored = []
        for cigar in all_cigars:
            cigar_flavors = set((cigar['primary_flavors'] or '').split(',') + (cigar['secondary_flavors'] or '').split(','))
            cigar_flavors = {f.strip().lower() for f in cigar_flavors if f.strip()}
            
            # 风味重叠度
            common = ref_flavors & cigar_flavors
            flavor_score = len(common) / max(len(ref_flavors), 1)
            
            # 浓度相似度
            strength_match = 1.0 if cigar['strength'] == ref_strength else 0.5
            
            # 综合得分
            total_score = (flavor_score * 0.7 + strength_match * 0.3) * 100
            
            scored.append((total_score, cigar))
        
        # 排序并返回前 N 个
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for s, c in scored[:limit]]
    
    def recommend_by_pairing(self, drink: str, limit: int = 5) -> List[Dict]:
        """根据饮品推荐雪茄"""
        return self.search_cigars(pairing=drink)[:limit]
    
    def get_value_picks(self, limit: int = 5) -> List[Dict]:
        """性价比推荐 (高分低价)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *, 
                   (COALESCE(expert_rating, user_rating * 10) / NULLIF(price_per_stick, 0)) as value_ratio
            FROM cigars_v2
            WHERE price_per_stick IS NOT NULL
              AND (expert_rating IS NOT NULL OR user_rating IS NOT NULL)
            ORDER BY value_ratio DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM cigars_v2")
        total = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as humidor FROM cigars_v2 WHERE in_humidor = 1")
        in_humidor = cursor.fetchone()["humidor"]
        
        cursor.execute("SELECT SUM(quantity_owned) as total_owned FROM cigars_v2")
        total_owned = cursor.fetchone()["total_owned"] or 0
        
        cursor.execute("SELECT SUM(smoked_count) as total_smoked FROM cigars_v2")
        total_smoked = cursor.fetchone()["total_smoked"] or 0
        
        cursor.execute("SELECT DISTINCT origin FROM cigars_v2")
        origins = [row["origin"] for row in cursor.fetchall() if row["origin"]]
        
        cursor.execute("SELECT DISTINCT brand FROM cigars_v2")
        brands = [row["brand"] for row in cursor.fetchall()]
        
        return {
            "total_cigars": total,
            "in_humidor": in_humidor,
            "total_owned": total_owned,
            "total_smoked": total_smoked,
            "origins": origins,
            "brands": brands
        }
    
    def close(self):
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


if __name__ == "__main__":
    # 测试新数据库
    with CigarDatabaseV2() as db:
        print("✅ 雪茄数据库 v2 初始化成功")
        stats = db.get_stats()
        print(f"当前雪茄数: {stats['total_cigars']}")
