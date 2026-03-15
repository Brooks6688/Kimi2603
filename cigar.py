#!/usr/bin/env python3
"""
雪茄数据库 CLI 工具
"""

import sys
import argparse
from database import CigarDatabase, Cigar, init_sample_data


def print_cigar(cigar: dict):
    """格式化显示雪茄信息"""
    print(f"\n{'='*60}")
    print(f"🚬 {cigar['brand']} - {cigar['name']}")
    print(f"{'='*60}")
    print(f"  产地: {cigar['origin'] or '未知'}")
    print(f"  尺寸: {cigar['length'] or '未知'} x {cigar['ring_gauge'] or '未知'}环径")
    print(f"  浓度: {cigar['strength'] or '未知'}")
    print(f"  风味: {cigar['flavor_profile'] or '暂无描述'}")
    print(f"  茄衣: {cigar['wrapper'] or '未知'}")
    print(f"  茄套: {cigar['binder'] or '未知'}")
    print(f"  茄芯: {cigar['filler'] or '未知'}")
    print(f"  价格: {cigar['price_range'] or '未知'}")
    if cigar['rating']:
        print(f"  评分: {'⭐' * cigar['rating']}")
    if cigar['smoked_count']:
        print(f"  已抽: {cigar['smoked_count']} 支")
    if cigar['notes']:
        print(f"  备注: {cigar['notes']}")
    print(f"  ID: {cigar['id']}")


def cmd_list(args):
    """列出雪茄"""
    with CigarDatabase() as db:
        cigars = db.list_cigars(
            brand=args.brand,
            origin=args.origin,
            strength=args.strength,
            search=args.search
        )
        
        if not cigars:
            print("未找到匹配的雪茄")
            return
        
        print(f"\n找到 {len(cigars)} 款雪茄:\n")
        
        for c in cigars:
            rating_str = f" [{'⭐' * c['rating']}]" if c['rating'] else ""
            smoked = f" (已抽{c['smoked_count']}支)" if c['smoked_count'] else ""
            print(f"  [{c['id']:3d}] {c['brand']:<15} {c['name']:<25} "
                  f"{c['strength'] or '-':<6}{rating_str}{smoked}")


def cmd_add(args):
    """添加雪茄"""
    cigar = Cigar(
        brand=args.brand,
        name=args.name,
        origin=args.origin,
        length=args.length,
        ring_gauge=args.ring_gauge,
        strength=args.strength,
        flavor_profile=args.flavor,
        wrapper=args.wrapper,
        binder=args.binder,
        filler=args.filler,
        price_range=args.price,
        notes=args.notes,
        rating=args.rating
    )
    
    with CigarDatabase() as db:
        cid = db.add_cigar(cigar)
        print(f"✅ 已添加雪茄，ID: {cid}")


def cmd_show(args):
    """显示雪茄详情"""
    with CigarDatabase() as db:
        cigar = db.get_cigar(args.id)
        if not cigar:
            print(f"❌ 未找到 ID 为 {args.id} 的雪茄")
            return
        print_cigar(cigar)
        
        # 显示品鉴记录
        notes = db.get_tasting_notes(args.id)
        if notes:
            print(f"\n📋 品鉴记录 ({len(notes)} 条):")
            for n in notes:
                rating = f"{'⭐' * n['overall_rating']}" if n['overall_rating'] else "未评分"
                print(f"  • {n['smoke_date'][:10]} - {rating}")
                if n['notes']:
                    print(f"    {n['notes']}")


def cmd_edit(args):
    """编辑雪茄"""
    updates = {}
    if args.brand: updates['brand'] = args.brand
    if args.name: updates['name'] = args.name
    if args.origin: updates['origin'] = args.origin
    if args.length: updates['length'] = args.length
    if args.ring_gauge: updates['ring_gauge'] = args.ring_gauge
    if args.strength: updates['strength'] = args.strength
    if args.flavor: updates['flavor_profile'] = args.flavor
    if args.wrapper: updates['wrapper'] = args.wrapper
    if args.binder: updates['binder'] = args.binder
    if args.filler: updates['filler'] = args.filler
    if args.price: updates['price_range'] = args.price
    if args.notes: updates['notes'] = args.notes
    if args.rating: updates['rating'] = args.rating
    
    if not updates:
        print("❌ 请指定要修改的字段")
        return
    
    with CigarDatabase() as db:
        if db.update_cigar(args.id, **updates):
            print(f"✅ 已更新 ID {args.id}")
        else:
            print(f"❌ 未找到 ID {args.id}")


def cmd_delete(args):
    """删除雪茄"""
    with CigarDatabase() as db:
        if db.delete_cigar(args.id):
            print(f"✅ 已删除 ID {args.id}")
        else:
            print(f"❌ 未找到 ID {args.id}")


def cmd_taste(args):
    """添加品鉴记录"""
    with CigarDatabase() as db:
        # 检查雪茄是否存在
        cigar = db.get_cigar(args.id)
        if not cigar:
            print(f"❌ 未找到 ID 为 {args.id} 的雪茄")
            return
        
        note_id = db.add_tasting_note(
            cigar_id=args.id,
            smoke_date=args.date,
            duration_minutes=args.duration,
            draw=args.draw,
            burn=args.burn,
            ash=args.ash,
            flavor_notes=args.flavor,
            overall_rating=args.rating,
            notes=args.notes
        )
        print(f"✅ 已添加品鉴记录，ID: {note_id}")
        print(f"   雪茄: {cigar['brand']} {cigar['name']}")


def cmd_stats(args):
    """显示统计"""
    with CigarDatabase() as db:
        stats = db.get_stats()
        
        print(f"\n{'='*40}")
        print("📊 雪茄数据库统计")
        print(f"{'='*40}")
        print(f"  雪茄总数: {stats['total_cigars']}")
        print(f"  总品鉴次数: {stats['total_smoked']}")
        print(f"  产地数量: {len(stats['origins'])}")
        print(f"  品牌数量: {len(stats['brands'])}")
        
        if stats['top_cigars']:
            print(f"\n  🏆 最常抽的雪茄:")
            for c in stats['top_cigars'][:5]:
                print(f"     {c['brand']} {c['name']}: {c['count']} 次")


def cmd_search(args):
    """搜索雪茄"""
    with CigarDatabase() as db:
        cigars = db.list_cigars(search=args.keyword)
        
        if not cigars:
            print(f"未找到包含 '{args.keyword}' 的雪茄")
            return
        
        print(f"\n找到 {len(cigars)} 款匹配的雪茄:\n")
        for c in cigars:
            rating_str = f" [{'⭐' * c['rating']}]" if c['rating'] else ""
            print(f"  [{c['id']:3d}] {c['brand']:<15} {c['name']:<25} "
                  f"{c['strength'] or '-':<6}{rating_str}")


def interactive_mode():
    """交互模式"""
    print("\n🚬 欢迎使用雪茄数据库")
    print("输入 'help' 查看命令，'quit' 退出\n")
    
    while True:
        try:
            cmd = input("> ").strip().lower()
            
            if cmd == 'quit' or cmd == 'exit':
                print("再见！")
                break
            elif cmd == 'help':
                print("""
可用命令:
  list              - 列出所有雪茄
  list <品牌>       - 按品牌筛选
  show <ID>         - 显示雪茄详情
  add               - 添加新雪茄（交互式）
  taste <ID>        - 添加品鉴记录
  stats             - 显示统计
  search <关键词>   - 搜索雪茄
  quit              - 退出
                """)
            elif cmd == 'list':
                with CigarDatabase() as db:
                    cigars = db.list_cigars()
                    for c in cigars:
                        print(f"[{c['id']}] {c['brand']} - {c['name']}")
            elif cmd.startswith('show '):
                try:
                    cid = int(cmd.split()[1])
                    with CigarDatabase() as db:
                        cigar = db.get_cigar(cid)
                        if cigar:
                            print_cigar(cigar)
                        else:
                            print("未找到")
                except:
                    print("用法: show <ID>")
            elif cmd == 'stats':
                class FakeArgs:
                    pass
                cmd_stats(FakeArgs())
            elif cmd == '':
                continue
            else:
                print("未知命令，输入 'help' 查看帮助")
                
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='🚬 雪茄数据库管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s list                           # 列出所有雪茄
  %(prog)s list --brand Cohiba            # 按品牌筛选
  %(prog)s show 1                         # 显示详情
  %(prog)s add --brand "Cohiba" --name "Robusto" --origin "古巴"
  %(prog)s taste 1 --rating 9 --notes "非常顺滑"
  %(prog)s stats                          # 统计信息
  %(prog)s search "浓郁"                   # 搜索关键词
  %(prog)s interactive                    # 交互模式
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # list
    list_parser = subparsers.add_parser('list', help='列出雪茄')
    list_parser.add_argument('--brand', help='按品牌筛选')
    list_parser.add_argument('--origin', help='按产地筛选')
    list_parser.add_argument('--strength', help='按浓度筛选')
    list_parser.add_argument('--search', help='关键词搜索')
    list_parser.set_defaults(func=cmd_list)
    
    # show
    show_parser = subparsers.add_parser('show', help='显示雪茄详情')
    show_parser.add_argument('id', type=int, help='雪茄ID')
    show_parser.set_defaults(func=cmd_show)
    
    # add
    add_parser = subparsers.add_parser('add', help='添加雪茄')
    add_parser.add_argument('--brand', required=True, help='品牌')
    add_parser.add_argument('--name', required=True, help='型号/名称')
    add_parser.add_argument('--origin', help='产地')
    add_parser.add_argument('--length', help='长度')
    add_parser.add_argument('--ring-gauge', type=int, help='环径')
    add_parser.add_argument('--strength', choices=['轻度', '中等', '中等偏浓', '浓郁'], help='浓度')
    add_parser.add_argument('--flavor', help='风味描述')
    add_parser.add_argument('--wrapper', help='茄衣')
    add_parser.add_argument('--binder', help='茄套')
    add_parser.add_argument('--filler', help='茄芯')
    add_parser.add_argument('--price', help='价格区间')
    add_parser.add_argument('--notes', help='备注')
    add_parser.add_argument('--rating', type=int, choices=range(1, 11), help='评分(1-10)')
    add_parser.set_defaults(func=cmd_add)
    
    # edit
    edit_parser = subparsers.add_parser('edit', help='编辑雪茄')
    edit_parser.add_argument('id', type=int, help='雪茄ID')
    edit_parser.add_argument('--brand', help='品牌')
    edit_parser.add_argument('--name', help='型号/名称')
    edit_parser.add_argument('--origin', help='产地')
    edit_parser.add_argument('--length', help='长度')
    edit_parser.add_argument('--ring-gauge', type=int, help='环径')
    edit_parser.add_argument('--strength', choices=['轻度', '中等', '中等偏浓', '浓郁'], help='浓度')
    edit_parser.add_argument('--flavor', help='风味描述')
    edit_parser.add_argument('--wrapper', help='茄衣')
    edit_parser.add_argument('--binder', help='茄套')
    edit_parser.add_argument('--filler', help='茄芯')
    edit_parser.add_argument('--price', help='价格区间')
    edit_parser.add_argument('--notes', help='备注')
    edit_parser.add_argument('--rating', type=int, choices=range(1, 11), help='评分(1-10)')
    edit_parser.set_defaults(func=cmd_edit)
    
    # delete
    delete_parser = subparsers.add_parser('delete', help='删除雪茄')
    delete_parser.add_argument('id', type=int, help='雪茄ID')
    delete_parser.set_defaults(func=cmd_delete)
    
    # taste
    taste_parser = subparsers.add_parser('taste', help='添加品鉴记录')
    taste_parser.add_argument('id', type=int, help='雪茄ID')
    taste_parser.add_argument('--date', help='日期(YYYY-MM-DD)')
    taste_parser.add_argument('--duration', type=int, help='抽吸时长(分钟)')
    taste_parser.add_argument('--draw', choices=['松', '适中', '紧'], help='吸阻')
    taste_parser.add_argument('--burn', choices=['不均匀', '一般', '均匀'], help='燃烧')
    taste_parser.add_argument('--ash', choices=['松散', '一般', '紧实'], help='烟灰')
    taste_parser.add_argument('--flavor', help='风味描述')
    taste_parser.add_argument('--rating', type=int, choices=range(1, 11), help='整体评分(1-10)')
    taste_parser.add_argument('--notes', help='备注')
    taste_parser.set_defaults(func=cmd_taste)
    
    # stats
    stats_parser = subparsers.add_parser('stats', help='统计信息')
    stats_parser.set_defaults(func=cmd_stats)
    
    # search
    search_parser = subparsers.add_parser('search', help='搜索雪茄')
    search_parser.add_argument('keyword', help='关键词')
    search_parser.set_defaults(func=cmd_search)
    
    # interactive
    interactive_parser = subparsers.add_parser('interactive', help='交互模式')
    
    args = parser.parse_args()
    
    if args.command == 'interactive':
        interactive_mode()
    elif args.command and hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
