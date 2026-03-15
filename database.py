#!/usr/bin/env python3
"""
雪茄数据库管理工具
Cigar Database Manager
"""

import sqlite3
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "cigars.db"


@dataclass
class Cigar:
    """雪茄数据模型"""
    id: Optional[int] = None
    brand: str = ""  # 品牌
    name: str = ""  # 型号/名称
    origin: str = ""  # 产地
    length: str = ""  # 长度 (如: 124mm)
    ring_gauge: int = 0  # 环径 (如: 50)
    strength: str = ""  # 浓度 (轻度/中等/浓郁)
    flavor_profile: str = ""  # 风味描述
    wrapper: str = ""  # 茄衣
    binder: str = ""  # 茄套
    filler: str = ""  # 茄芯
    price_range: str = ""  # 价格区间
    notes: str = ""  # 备注
    rating: Optional[int] = None  # 个人评分 1-10
    smoked_count: int = 0  # 已抽数量
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CigarDatabase:
    """雪茄数据库管理类"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()
        
        # 雪茄主表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cigars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                name TEXT NOT NULL,
                origin TEXT,
                length TEXT,
                ring_gauge INTEGER,
                strength TEXT,
                flavor_profile TEXT,
                wrapper TEXT,
                binder TEXT,
                filler TEXT,
                price_range TEXT,
                notes TEXT,
                rating INTEGER CHECK(rating >= 1 AND rating <= 10),
                smoked_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 品鉴记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasting_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cigar_id INTEGER NOT NULL,
                smoke_date TEXT DEFAULT CURRENT_TIMESTAMP,
                duration_minutes INTEGER,
                draw TEXT,
                burn TEXT,
                ash TEXT,
                flavor_notes TEXT,
                overall_rating INTEGER CHECK(overall_rating >= 1 AND overall_rating <= 10),
                notes TEXT,
                FOREIGN KEY (cigar_id) REFERENCES cigars(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def add_cigar(self, cigar: Cigar) -> int:
        """添加新雪茄"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO cigars (brand, name, origin, length, ring_gauge, strength, 
                              flavor_profile, wrapper, binder, filler, price_range, 
                              notes, rating, smoked_count, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (cigar.brand, cigar.name, cigar.origin, cigar.length, cigar.ring_gauge,
              cigar.strength, cigar.flavor_profile, cigar.wrapper, cigar.binder,
              cigar.filler, cigar.price_range, cigar.notes, cigar.rating, cigar.smoked_count))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_cigar(self, cigar_id: int) -> Optional[Dict]:
        """获取单个雪茄详情"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM cigars WHERE id = ?", (cigar_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def list_cigars(self, brand: str = None, origin: str = None, 
                    strength: str = None, search: str = None) -> List[Dict]:
        """列出雪茄，支持筛选"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM cigars WHERE 1=1"
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
        if search:
            query += " AND (brand LIKE ? OR name LIKE ? OR flavor_profile LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        
        query += " ORDER BY brand, name"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_cigar(self, cigar_id: int, **kwargs) -> bool:
        """更新雪茄信息"""
        if not kwargs:
            return False
        
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(cigar_id)
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE cigars 
            SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_cigar(self, cigar_id: int) -> bool:
        """删除雪茄"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM cigars WHERE id = ?", (cigar_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def add_tasting_note(self, cigar_id: int, smoke_date: str = None,
                        duration_minutes: int = None, draw: str = None,
                        burn: str = None, ash: str = None, 
                        flavor_notes: str = None, overall_rating: int = None,
                        notes: str = None) -> int:
        """添加品鉴记录"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasting_notes 
            (cigar_id, smoke_date, duration_minutes, draw, burn, ash, 
             flavor_notes, overall_rating, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cigar_id, smoke_date or datetime.now().isoformat(), 
              duration_minutes, draw, burn, ash, flavor_notes, overall_rating, notes))
        
        # 更新已抽数量
        cursor.execute("""
            UPDATE cigars SET smoked_count = smoked_count + 1 
            WHERE id = ?
        """, (cigar_id,))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_tasting_notes(self, cigar_id: int = None) -> List[Dict]:
        """获取品鉴记录"""
        cursor = self.conn.cursor()
        if cigar_id:
            cursor.execute("""
                SELECT t.*, c.brand, c.name 
                FROM tasting_notes t
                JOIN cigars c ON t.cigar_id = c.id
                WHERE t.cigar_id = ?
                ORDER BY t.smoke_date DESC
            """, (cigar_id,))
        else:
            cursor.execute("""
                SELECT t.*, c.brand, c.name 
                FROM tasting_notes t
                JOIN cigars c ON t.cigar_id = c.id
                ORDER BY t.smoke_date DESC
            """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM cigars")
        total = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as tasted FROM tasting_notes")
        tasted = cursor.fetchone()["tasted"]
        
        cursor.execute("SELECT DISTINCT origin FROM cigars")
        origins = [row["origin"] for row in cursor.fetchall() if row["origin"]]
        
        cursor.execute("SELECT DISTINCT brand FROM cigars")
        brands = [row["brand"] for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT c.brand, c.name, COUNT(t.id) as count
            FROM cigars c
            LEFT JOIN tasting_notes t ON c.id = t.cigar_id
            GROUP BY c.id
            ORDER BY count DESC
            LIMIT 5
        """)
        top_cigars = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_cigars": total,
            "total_smoked": tasted,
            "origins": origins,
            "brands": brands,
            "top_cigars": top_cigars
        }
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


# 预设雪茄数据
SAMPLE_CIGARS = [
    Cigar(brand="Cohiba", name="Behike 52", origin="古巴", length="119mm", 
          ring_gauge=52, strength="浓郁", 
          flavor_profile="可可、咖啡、皮革、奶油",
          wrapper="古巴", binder="古巴", filler="古巴",
          price_range="高端"),
    Cigar(brand="Montecristo", name="No. 2", origin="古巴", length="156mm",
          ring_gauge=52, strength="中等偏浓",
          flavor_profile="雪松、坚果、香料、可可",
          wrapper="古巴", binder="古巴", filler="古巴",
          price_range="中高端"),
    Cigar(brand="Romeo y Julieta", name="Wide Churchill", origin="古巴", 
          length="130mm", ring_gauge=55, strength="中等",
          flavor_profile="花香、坚果、香草、奶油",
          wrapper="古巴", binder="古巴", filler="古巴",
          price_range="中端"),
    Cigar(brand="Partagas", name="Serie D No. 4", origin="古巴", 
          length="124mm", ring_gauge=50, strength="浓郁",
          flavor_profile="胡椒、皮革、泥土、咖啡",
          wrapper="古巴", binder="古巴", filler="古巴",
          price_range="中端"),
    Cigar(brand="Hoyo de Monterrey", name="Epicure No. 2", origin="古巴",
          length="124mm", ring_gauge=50, strength="轻度",
          flavor_profile="奶油、蜂蜜、花香、柑橘",
          wrapper="古巴", binder="古巴", filler="古巴",
          price_range="中端"),
    Cigar(brand="Davidoff", name="Winston Churchill Churchill", origin="多米尼加",
          length="178mm", ring_gauge=47, strength="中等",
          flavor_profile="雪松、坚果、奶油、香料",
          wrapper="厄瓜多尔", binder="墨西哥", filler="多米尼加/尼加拉瓜",
          price_range="高端"),
    Cigar(brand="Arturo Fuente", name="Opus X Perfecxion X", origin="多米尼加",
          length="165mm", ring_gauge=48, strength="浓郁",
          flavor_profile="胡椒、皮革、甜味、雪松",
          wrapper="多米尼加", binder="多米尼加", filler="多米尼加",
          price_range="高端"),
    Cigar(brand="Padron", name="1964 Anniversary Series Exclusivo Maduro", 
          origin="尼加拉瓜", length="140mm", ring_gauge=50, strength="浓郁",
          flavor_profile="可可、咖啡、焦糖、香料",
          wrapper="尼加拉瓜", binder="尼加拉瓜", filler="尼加拉瓜",
          price_range="高端"),
]


def init_sample_data():
    """初始化示例数据"""
    with CigarDatabase() as db:
        count = db.list_cigars()
        if len(count) == 0:
            print("🚬 正在导入预设雪茄数据...")
            for cigar in SAMPLE_CIGARS:
                db.add_cigar(cigar)
            print(f"✅ 已导入 {len(SAMPLE_CIGARS)} 款雪茄")
        else:
            print(f"📊 数据库已有 {len(count)} 款雪茄，跳过导入")


if __name__ == "__main__":
    init_sample_data()
    print("数据库初始化完成！")
