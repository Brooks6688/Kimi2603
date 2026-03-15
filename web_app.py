#!/usr/bin/env python3
"""
雪茄数据库 Web 界面
Flask + SQLite + Bootstrap
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path
import json

app = Flask(__name__)

# 数据库路径
DB_PATH = Path(__file__).parent / "cigars_v2.db"


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    """首页 - 统计和概览"""
    conn = get_db_connection()
    
    # 统计信息
    total = conn.execute("SELECT COUNT(*) as count FROM cigars_v2").fetchone()["count"]
    
    # 产地分布
    origins = conn.execute('''
        SELECT origin, COUNT(*) as count 
        FROM cigars_v2 
        WHERE origin IS NOT NULL AND origin != ''
        GROUP BY origin 
        ORDER BY count DESC
    ''').fetchall()
    
    # 浓度分布
    strengths = conn.execute('''
        SELECT strength, COUNT(*) as count 
        FROM cigars_v2 
        WHERE strength IS NOT NULL AND strength != ''
        GROUP BY strength 
        ORDER BY count DESC
    ''').fetchall()
    
    # 数据来源
    sources = conn.execute('''
        SELECT expert_source, COUNT(*) as count
        FROM cigars_v2
        WHERE expert_source IS NOT NULL AND expert_source != ''
        GROUP BY expert_source
        ORDER BY count DESC
    ''').fetchall()
    
    # 顶级雪茄
    top_cigars = conn.execute('''
        SELECT id, brand, name, origin, expert_rating, price_per_stick, expert_source
        FROM cigars_v2 
        WHERE expert_rating IS NOT NULL
        ORDER BY expert_rating DESC
        LIMIT 10
    ''').fetchall()
    
    # 性价比之选
    value_cigars = conn.execute('''
        SELECT id, brand, name, expert_rating, price_per_stick,
               (expert_rating / NULLIF(price_per_stick, 0)) as value_ratio
        FROM cigars_v2
        WHERE expert_rating IS NOT NULL AND price_per_stick IS NOT NULL AND price_per_stick > 0
        ORDER BY value_ratio DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template("index.html",
                          total=total,
                          origins=origins,
                          strengths=strengths,
                          sources=sources,
                          top_cigars=top_cigars,
                          value_cigars=value_cigars)


@app.route("/cigars")
def list_cigars():
    """雪茄列表页"""
    conn = get_db_connection()
    
    # 筛选参数
    origin = request.args.get("origin", "")
    strength = request.args.get("strength", "")
    search = request.args.get("search", "")
    sort = request.args.get("sort", "rating")
    
    # 构建查询
    query = "SELECT * FROM cigars_v2 WHERE 1=1"
    params = []
    
    if origin:
        query += " AND origin = ?"
        params.append(origin)
    
    if strength:
        query += " AND strength = ?"
        params.append(strength)
    
    if search:
        query += " AND (brand LIKE ? OR name LIKE ? OR primary_flavors LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    
    # 排序
    if sort == "rating":
        query += " ORDER BY expert_rating DESC NULLS LAST, user_rating DESC NULLS LAST"
    elif sort == "price_low":
        query += " ORDER BY price_per_stick ASC NULLS LAST"
    elif sort == "price_high":
        query += " ORDER BY price_per_stick DESC NULLS LAST"
    elif sort == "name":
        query += " ORDER BY brand, name"
    
    cigars = conn.execute(query, params).fetchall()
    
    # 获取筛选选项
    all_origins = conn.execute('''
        SELECT DISTINCT origin FROM cigars_v2 
        WHERE origin IS NOT NULL AND origin != ''
        ORDER BY origin
    ''').fetchall()
    
    all_strengths = conn.execute('''
        SELECT DISTINCT strength FROM cigars_v2 
        WHERE strength IS NOT NULL AND strength != ''
        ORDER BY strength
    ''').fetchall()
    
    conn.close()
    
    return render_template("cigars.html",
                          cigars=cigars,
                          origins=all_origins,
                          strengths=all_strengths,
                          selected_origin=origin,
                          selected_strength=strength,
                          search=search,
                          sort=sort)


@app.route("/cigar/<int:cigar_id>")
def cigar_detail(cigar_id):
    """雪茄详情页"""
    conn = get_db_connection()
    
    cigar = conn.execute("SELECT * FROM cigars_v2 WHERE id = ?", (cigar_id,)).fetchone()
    
    if not cigar:
        return render_template("404.html"), 404
    
    # 获取相似雪茄（基于风味）
    similar = []
    if cigar["primary_flavors"]:
        flavors = cigar["primary_flavors"].split(",")
        if flavors:
            flavor = flavors[0].strip()
            similar = conn.execute('''
                SELECT id, brand, name, origin, expert_rating, primary_flavors
                FROM cigars_v2
                WHERE id != ? AND primary_flavors LIKE ?
                ORDER BY expert_rating DESC NULLS LAST
                LIMIT 5
            ''', (cigar_id, f"%{flavor}%")).fetchall()
    
    # 获取同品牌雪茄
    same_brand = conn.execute('''
        SELECT id, name, expert_rating, price_per_stick
        FROM cigars_v2
        WHERE brand = ? AND id != ?
        ORDER BY expert_rating DESC NULLS LAST
        LIMIT 5
    ''', (cigar["brand"], cigar_id)).fetchall()
    
    conn.close()
    
    return render_template("cigar_detail.html",
                          cigar=cigar,
                          similar=similar,
                          same_brand=same_brand)


@app.route("/search")
def search_page():
    """搜索页面"""
    query = request.args.get("q", "")
    
    if not query:
        return render_template("search.html", results=[], query="")
    
    conn = get_db_connection()
    
    results = conn.execute('''
        SELECT * FROM cigars_v2
        WHERE brand LIKE ? OR name LIKE ? OR origin LIKE ? 
           OR primary_flavors LIKE ? OR secondary_flavors LIKE ?
           OR wrapper LIKE ? OR description LIKE ?
        ORDER BY expert_rating DESC NULLS LAST
        LIMIT 50
    ''', tuple([f"%{query}%"] * 7)).fetchall()
    
    conn.close()
    
    return render_template("search.html", results=results, query=query)


@app.route("/recommend")
def recommend_page():
    """推荐页面"""
    rec_type = request.args.get("type", "flavor")
    
    conn = get_db_connection()
    
    recommendations = []
    
    if rec_type == "value":
        # 性价比推荐
        recommendations = conn.execute('''
            SELECT id, brand, name, origin, expert_rating, price_per_stick,
                   (expert_rating / NULLIF(price_per_stick, 0)) as value_ratio
            FROM cigars_v2
            WHERE expert_rating IS NOT NULL AND price_per_stick IS NOT NULL AND price_per_stick > 0
            ORDER BY value_ratio DESC
            LIMIT 20
        ''').fetchall()
        title = "性价比推荐 (高分低价)"
        
    elif rec_type == "top_rated":
        # 顶级评分
        recommendations = conn.execute('''
            SELECT id, brand, name, origin, expert_rating, expert_source, price_per_stick
            FROM cigars_v2
            WHERE expert_rating IS NOT NULL
            ORDER BY expert_rating DESC
            LIMIT 20
        ''').fetchall()
        title = "顶级评分雪茄"
        
    elif rec_type == "beginner":
        # 新手推荐 (Mild/Medium 浓度，低价)
        recommendations = conn.execute('''
            SELECT id, brand, name, origin, strength, expert_rating, price_per_stick
            FROM cigars_v2
            WHERE strength IN ('Mild', 'Medium', 'Mild-Medium')
              AND price_per_stick IS NOT NULL AND price_per_stick < 15
            ORDER BY expert_rating DESC NULLS LAST
            LIMIT 20
        ''').fetchall()
        title = "新手入门推荐"
        
    elif rec_type == "full_body":
        # 浓郁型推荐
        recommendations = conn.execute('''
            SELECT id, brand, name, origin, strength, expert_rating, price_per_stick
            FROM cigars_v2
            WHERE strength = 'Full'
            ORDER BY expert_rating DESC NULLS LAST
            LIMIT 20
        ''').fetchall()
        title = "浓郁型雪茄推荐"
        
    else:
        # 默认：古巴雪茄
        recommendations = conn.execute('''
            SELECT id, brand, name, origin, expert_rating, price_per_stick
            FROM cigars_v2
            WHERE origin = '古巴'
            ORDER BY expert_rating DESC NULLS LAST
            LIMIT 20
        ''').fetchall()
        title = "古巴雪茄精选"
    
    conn.close()
    
    return render_template("recommend.html",
                          recommendations=recommendations,
                          rec_type=rec_type,
                          title=title)


@app.route("/api/cigars")
def api_cigars():
    """API - 获取雪茄列表"""
    conn = get_db_connection()
    
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    cigars = conn.execute('''
        SELECT id, brand, name, origin, strength, expert_rating, price_per_stick
        FROM cigars_v2
        ORDER BY expert_rating DESC NULLS LAST
        LIMIT ? OFFSET ?
    ''', (limit, offset)).fetchall()
    
    conn.close()
    
    return jsonify([dict(c) for c in cigars])


@app.route("/api/cigar/<int:cigar_id>")
def api_cigar(cigar_id):
    """API - 获取单支雪茄详情"""
    conn = get_db_connection()
    cigar = conn.execute("SELECT * FROM cigars_v2 WHERE id = ?", (cigar_id,)).fetchone()
    conn.close()
    
    if cigar:
        return jsonify(dict(cigar))
    return jsonify({"error": "Not found"}), 404


@app.route("/stats")
def stats_page():
    """统计页面"""
    conn = get_db_connection()
    
    # 品牌统计
    brands = conn.execute('''
        SELECT brand, COUNT(*) as count, AVG(expert_rating) as avg_rating
        FROM cigars_v2
        GROUP BY brand
        ORDER BY count DESC, avg_rating DESC
    ''').fetchall()
    
    # 价格分布
    price_ranges = conn.execute('''
        SELECT 
            CASE 
                WHEN price_per_stick < 10 THEN '< $10'
                WHEN price_per_stick < 15 THEN '$10-15'
                WHEN price_per_stick < 20 THEN '$15-20'
                WHEN price_per_stick < 30 THEN '$20-30'
                ELSE '$30+'
            END as price_range,
            COUNT(*) as count
        FROM cigars_v2
        WHERE price_per_stick IS NOT NULL
        GROUP BY price_range
        ORDER BY MIN(price_per_stick)
    ''').fetchall()
    
    conn.close()
    
    return render_template("stats.html", brands=brands, price_ranges=price_ranges)


if __name__ == "__main__":
    print("🚬 雪茄数据库 Web 界面")
    print("=" * 50)
    print("访问地址: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
