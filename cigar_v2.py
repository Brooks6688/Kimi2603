#!/usr/bin/env python3
"""
雪茄数据库 CLI v2 - 增强版
支持推荐算法、风味分析、价格追踪
"""

import sys
import argparse
sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')
from database_v2 import CigarDatabaseV2, CigarV2


def print_cigar_v2(cigar: dict):
    """格式化显示雪茄详情"""
    print(f"\n{'='*70}")
    print(f"🚬 {cigar['brand']}", end='')
    if cigar['line']:
        print(f" ({cigar['line']})", end='')
    print(f" - {cigar['name']}")
    print(f"{'='*70}")
    
    # 基础信息
    print(f"  产地: {cigar['origin'] or '未知'}", end='')
    if cigar['factory']:
        print(f" | 工厂: {cigar['factory']}")
    else:
        print()
    
    # 尺寸
    size = f"{cigar['length']}"
    if cigar['ring_gauge']:
        size += f" x {cigar['ring_gauge']}环径"
    if cigar['vitola']:
        size += f" ({cigar['vitola']})"
    print(f"  尺寸: {size}")
    
    # 烟叶
    print(f"  茄衣: {cigar['wrapper'] or '未知'}", end='')
    if cigar['wrapper_origin']:
        print(f" ({cigar['wrapper_origin']})", end='')
    print(f" | 茄套: {cigar['binder'] or '未知'}")
    print(f"  茄芯: {cigar['filler'] or '未知'}")
    
    # 风味
    print(f"  浓度: {cigar['strength'] or '未知'}", end='')
    if cigar['body']:
        print(f" (醇厚度: {cigar['body']}/10)")
    else:
        print()
    
    if cigar['primary_flavors']:
        print(f"  主要风味: {cigar['primary_flavors']}")
    if cigar['secondary_flavors']:
        print(f"  次要风味: {cigar['secondary_flavors']}")
    if cigar['finish_notes']:
        print(f"  余味: {cigar['finish_notes']}")
    
    # 评分
    if cigar['expert_rating']:
        source = f" ({cigar['expert_source']})" if cigar['expert_source'] else ""
        print(f"  专家评分: {cigar['expert_rating']}/100{source}")
    if cigar['user_rating']:
        print(f"  个人评分: {'⭐' * cigar['user_rating']}")
    
    # 价格
    if cigar['price_per_stick']:
        print(f"  价格: ${cigar['price_per_stick']:.2f}", end='')
        if cigar['currency'] and cigar['currency'] != 'USD':
            print(f" {cigar['currency']}", end='')
        print()
    
    # 推荐搭配
    if cigar['pairing_drink']:
        print(f"  推荐搭配: {cigar['pairing_drink']}")
    if cigar['best_time']:
        print(f"  最佳时段: {cigar['best_time']}")
    
    # 其他
    if cigar['limited_edition']:
        print(f"  ⚠️ 限量版")
    if cigar['release_year']:
        print(f"  发布年份: {cigar['release_year']}")
    if cigar['description']:
        print(f"  描述: {cigar['description'][:200]}...")
    
    print(f"  ID: {cigar['id']}")


def cmd_list(args):
    """列出雪茄"""
    with CigarDatabaseV2() as db:
        cigars = db.search_cigars(
            brand=args.brand,
            origin=args.origin,
            strength=args.strength,
            flavor=args.flavor,
            min_rating=args.min_rating
        )
        
        if not cigars:
            print("未找到匹配的雪茄")
            return
        
        print(f"\n找到 {len(cigars)} 款雪茄:\n")
        print(f"{'ID':<4} {'品牌':<20} {'型号':<30} {'产地':<10} {'评分':<6} {'价格'}")
        print("-" * 90)
        
        for c in cigars:
            rating = f"{c['expert_rating']:.0f}" if c['expert_rating'] else (f"{'⭐'*c['user_rating']}" if c['user_rating'] else '-')
            price = f"${c['price_per_stick']:.0f}" if c['price_per_stick'] else '-'
            print(f"{c['id']:<4} {c['brand']:<20} {c['name']:<30} {c['origin'] or '-':<10} {rating:<6} {price}")


def cmd_show(args):
    """显示雪茄详情"""
    with CigarDatabaseV2() as db:
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM cigars_v2 WHERE id = ?", (args.id,))
        row = cursor.fetchone()
        if not row:
            print(f"❌ 未找到 ID 为 {args.id} 的雪茄")
            return
        print_cigar_v2(dict(row))


def cmd_search(args):
    """搜索雪茄"""
    with CigarDatabaseV2() as db:
        cigars = db.search_cigars(
            brand=args.keyword,
            origin=args.keyword,
            flavor=args.keyword
        )
        
        if not cigars:
            print(f"未找到包含 '{args.keyword}' 的雪茄")
            return
        
        print(f"\n找到 {len(cigars)} 款匹配的雪茄:\n")
        for c in cigars:
            rating = f" ({c['expert_rating']:.0f}分)" if c['expert_rating'] else ""
            print(f"  [{c['id']:2d}] {c['brand']:<20} {c['name']:<30} {c['origin'] or '-':<8}{rating}")


def cmd_recommend(args):
    """推荐雪茄"""
    with CigarDatabaseV2() as db:
        if args.type == 'flavor' and args.id:
            # 基于风味相似度推荐
            print(f"\n🎯 基于雪茄 ID {args.id} 的风味推荐:\n")
            cigars = db.recommend_by_flavor(args.id, limit=args.limit)
            
            cursor = db.conn.cursor()
            cursor.execute("SELECT brand, name FROM cigars_v2 WHERE id = ?", (args.id,))
            ref = cursor.fetchone()
            if ref:
                print(f"参考雪茄: {ref['brand']} {ref['name']}\n")
            
            for i, c in enumerate(cigars, 1):
                print(f"{i}. {c['brand']} {c['name']}")
                print(f"   产地: {c['origin']} | 浓度: {c['strength']}")
                if c['primary_flavors']:
                    print(f"   风味: {c['primary_flavors']}")
                print()
                
        elif args.type == 'pairing' and args.drink:
            # 基于饮品搭配推荐
            print(f"\n🍷 适合搭配 {args.drink} 的雪茄:\n")
            cigars = db.recommend_by_pairing(args.drink, limit=args.limit)
            
            for i, c in enumerate(cigars, 1):
                print(f"{i}. {c['brand']} {c['name']}")
                print(f"   产地: {c['origin']} | 浓度: {c['strength']}")
                print(f"   价格: ${c['price_per_stick']:.2f}" if c['price_per_stick'] else "")
                print()
                
        elif args.type == 'value':
            # 性价比推荐
            print(f"\n💰 性价比最高的雪茄 (评分/价格):\n")
            cigars = db.get_value_picks(limit=args.limit)
            
            for i, c in enumerate(cigars, 1):
                rating = c['expert_rating'] or (c['user_rating'] * 10 if c['user_rating'] else 0)
                price = c['price_per_stick'] or 1
                value = rating / price if price > 0 else 0
                print(f"{i}. {c['brand']} {c['name']}")
                print(f"   评分: {rating:.0f} | 价格: ${price:.2f} | 性价比: {value:.2f}")
                print()


def cmd_stats(args):
    """显示统计"""
    with CigarDatabaseV2() as db:
        stats = db.get_stats()
        
        print(f"\n{'='*50}")
        print("📊 雪茄数据库 v2 统计")
        print(f"{'='*50}")
        print(f"  雪茄总数: {stats['total_cigars']}")
        print(f"  保湿盒中: {stats['in_humidor']} 款")
        print(f"  拥有总数: {stats['total_owned']} 支")
        print(f"  已抽数量: {stats['total_smoked']} 支")
        print(f"  产地数量: {len(stats['origins'])}")
        print(f"  品牌数量: {len(stats['brands'])}")
        
        # 产地分布
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT origin, COUNT(*) as count 
            FROM cigars_v2 
            WHERE origin IS NOT NULL
            GROUP BY origin 
            ORDER BY count DESC
        """)
        origins = cursor.fetchall()
        print(f"\n  📍 产地分布:")
        for row in origins:
            print(f"     {row['origin']}: {row['count']} 款")
        
        # 浓度分布
        cursor.execute("""
            SELECT strength, COUNT(*) as count 
            FROM cigars_v2 
            WHERE strength IS NOT NULL
            GROUP BY strength 
            ORDER BY count DESC
        """)
        strengths = cursor.fetchall()
        print(f"\n  💨 浓度分布:")
        for row in strengths:
            print(f"     {row['strength']}: {row['count']} 款")
        
        # 顶级评分雪茄
        cursor.execute("""
            SELECT brand, name, expert_rating 
            FROM cigars_v2 
            WHERE expert_rating IS NOT NULL
            ORDER BY expert_rating DESC
            LIMIT 5
        """)
        top = cursor.fetchall()
        print(f"\n  🏆 专家评分最高:")
        for row in top:
            print(f"     {row['brand']} {row['name']}: {row['expert_rating']:.0f}分")


def cmd_add(args):
    """添加新雪茄"""
    cigar = CigarV2(
        brand=args.brand,
        name=args.name,
        origin=args.origin,
        length=args.length,
        ring_gauge=args.ring_gauge,
        strength=args.strength,
        wrapper=args.wrapper,
        expert_rating=args.expert_rating,
        price_per_stick=args.price
    )
    
    with CigarDatabaseV2() as db:
        cid = db.add_cigar(cigar)
        print(f"✅ 已添加雪茄，ID: {cid}")


def main():
    parser = argparse.ArgumentParser(
        description='🚬 雪茄数据库 v2 - 专业版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s list                              # 列出所有雪茄
  %(prog)s list --origin 古巴                 # 按产地筛选
  %(prog)s show 1                            # 显示详情
  %(prog)s search "可可"                      # 搜索风味
  %(prog)s recommend --type flavor --id 1    # 相似风味推荐
  %(prog)s recommend --type pairing --drink 威士忌  # 搭配推荐
  %(prog)s recommend --type value            # 性价比推荐
  %(prog)s stats                             # 统计信息
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # list
    list_parser = subparsers.add_parser('list', help='列出雪茄')
    list_parser.add_argument('--brand', help='按品牌筛选')
    list_parser.add_argument('--origin', help='按产地筛选')
    list_parser.add_argument('--strength', help='按浓度筛选')
    list_parser.add_argument('--flavor', help='按风味筛选')
    list_parser.add_argument('--min-rating', type=float, help='最低评分')
    list_parser.set_defaults(func=cmd_list)
    
    # show
    show_parser = subparsers.add_parser('show', help='显示雪茄详情')
    show_parser.add_argument('id', type=int, help='雪茄ID')
    show_parser.set_defaults(func=cmd_show)
    
    # search
    search_parser = subparsers.add_parser('search', help='搜索雪茄')
    search_parser.add_argument('keyword', help='关键词')
    search_parser.set_defaults(func=cmd_search)
    
    # recommend
    rec_parser = subparsers.add_parser('recommend', help='推荐雪茄')
    rec_parser.add_argument('--type', choices=['flavor', 'pairing', 'value'], 
                           default='flavor', help='推荐类型')
    rec_parser.add_argument('--id', type=int, help='参考雪茄ID (flavor类型)')
    rec_parser.add_argument('--drink', help='搭配饮品 (pairing类型)')
    rec_parser.add_argument('--limit', type=int, default=5, help='推荐数量')
    rec_parser.set_defaults(func=cmd_recommend)
    
    # stats
    stats_parser = subparsers.add_parser('stats', help='统计信息')
    stats_parser.set_defaults(func=cmd_stats)
    
    # add
    add_parser = subparsers.add_parser('add', help='添加雪茄')
    add_parser.add_argument('--brand', required=True, help='品牌')
    add_parser.add_argument('--name', required=True, help='型号')
    add_parser.add_argument('--origin', help='产地')
    add_parser.add_argument('--length', help='长度')
    add_parser.add_argument('--ring-gauge', type=int, help='环径')
    add_parser.add_argument('--strength', help='浓度')
    add_parser.add_argument('--wrapper', help='茄衣')
    add_parser.add_argument('--expert-rating', type=float, help='专家评分')
    add_parser.add_argument('--price', type=float, help='价格')
    add_parser.set_defaults(func=cmd_add)
    
    args = parser.parse_args()
    
    if args.command and hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
