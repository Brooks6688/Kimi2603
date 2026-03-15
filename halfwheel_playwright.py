#!/usr/bin/env python3
"""
Halfwheel 爬虫 - 使用 Playwright 绕过 Cloudflare
需要先安装: pip install playwright beautifulsoup4
然后运行: playwright install chromium
"""

import json
import time
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict


@dataclass
class HalfwheelReview:
    """Halfwheel 评审数据结构"""
    # 基础信息
    name: str = ""
    brand: str = ""
    line: str = ""
    factory: str = ""
    country: str = ""
    
    # 尺寸
    vitola: str = ""
    length: str = ""
    ring_gauge: int = 0
    
    # 烟叶
    wrapper: str = ""
    binder: str = ""
    filler: str = ""
    
    # 价格
    msrp: str = ""
    release_date: str = ""
    production: str = ""
    
    # 评分 (Halfwheel 使用 0-100)
    score: Optional[float] = None
    
    # 三段式风味描述
    first_third: str = ""
    second_third: str = ""
    final_third: str = ""
    
    # 表现
    draw_score: Optional[int] = None
    burn_score: Optional[int] = None
    construction_score: Optional[int] = None
    
    draw_notes: str = ""
    burn_notes: str = ""
    construction_notes: str = ""
    
    # 完整文本
    full_review: str = ""
    
    # 元数据
    source_url: str = ""
    scraped_at: str = ""
    
    def to_cigar_v2_format(self) -> Dict:
        """转换为 v2 数据库格式"""
        flavor_parts = []
        if self.first_third:
            flavor_parts.append(f"前段: {self.first_third[:100]}")
        if self.second_third:
            flavor_parts.append(f"中段: {self.second_third[:100]}")
        if self.final_third:
            flavor_parts.append(f"尾段: {self.final_third[:100]}")
        
        # 提取风味关键词
        all_text = f"{self.first_third} {self.second_third} {self.final_third}".lower()
        flavor_keywords = {
            'pepper': '胡椒', 'spice': '香料', 'cedar': '雪松',
            'wood': '木质', 'coffee': '咖啡', 'espresso': '浓缩咖啡',
            'cocoa': '可可', 'chocolate': '巧克力', 'leather': '皮革',
            'earth': '泥土', 'nut': '坚果', 'cream': '奶油',
            'sweet': '甜味', 'caramel': '焦糖', 'vanilla': '香草',
            'citrus': '柑橘', 'fruit': '水果', 'floral': '花香'
        }
        
        detected_flavors = []
        for en, cn in flavor_keywords.items():
            if en in all_text and cn not in detected_flavors:
                detected_flavors.append(cn)
        
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
        strength_map = {
            'mild': 'Mild', 'light': 'Mild',
            'medium': 'Medium',
            'full': 'Full', 'strong': 'Full'
        }
        strength = 'Medium'
        for en, val in strength_map.items():
            if en in all_text:
                strength = val
                break
        
        return {
            'brand': self.brand or 'Unknown',
            'name': self.name,
            'origin': self.country,
            'length': self.length,
            'ring_gauge': self.ring_gauge,
            'vitola': self.vitola,
            'wrapper': self.wrapper,
            'binder': self.binder,
            'filler': self.filler,
            'strength': strength,
            'body': 5,  # 默认中等
            'flavor_profile': ' | '.join(flavor_parts),
            'primary_flavors': ', '.join(detected_flavors[:3]),
            'secondary_flavors': ', '.join(detected_flavors[3:6]),
            'expert_rating': self.score,
            'expert_source': 'Halfwheel',
            'price_per_stick': price,
            'msrp': self.msrp,
            'description': self.full_review[:500],
            'release_year': self._extract_year(),
            'personal_notes': f"来源: {self.source_url}\n评分细则: 抽吸{self.draw_score} 燃烧{self.burn_score} 结构{self.construction_score}"
        }
    
    def _extract_year(self) -> Optional[int]:
        """从发布日期或文本中提取年份"""
        if self.release_date:
            match = re.search(r'(20\d{2})', self.release_date)
            if match:
                return int(match.group(1))
        return None


class HalfwheelPlaywrightScraper:
    """使用 Playwright 的 Halfwheel 爬虫"""
    
    def __init__(self, output_dir: str = "/root/.openclaw/workspace/cigar-db/halfwheel_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.reviews_file = self.output_dir / "reviews.jsonl"
        self.state_file = self.output_dir / "scraper_state.json"
        
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """加载爬虫状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {'scraped_urls': [], 'failed_urls': [], 'last_run': None}
    
    def _save_state(self):
        """保存爬虫状态"""
        self.state['last_run'] = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _save_review(self, review: HalfwheelReview):
        """保存评审数据"""
        with open(self.reviews_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(review), ensure_ascii=False) + '\n')
        
        self.state['scraped_urls'].append(review.source_url)
        self._save_state()
    
    def parse_review_page(self, page_content: str, url: str) -> Optional[HalfwheelReview]:
        """解析评审页面内容"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(page_content, 'html.parser')
        review = HalfwheelReview()
        review.source_url = url
        review.scraped_at = time.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # 1. 提取标题（雪茄名称）
            title = soup.find('h1', class_='entry-title')
            if title:
                review.name = title.text.strip()
                # 尝试提取品牌
                if '–' in review.name or '-' in review.name:
                    parts = re.split(r'[–-]', review.name, 1)
                    if len(parts) >= 2:
                        review.brand = parts[0].strip()
                        review.name = parts[1].strip()
            
            # 2. 提取评分
            score_elem = soup.find('div', class_=re.compile(r'score|number'))
            if score_elem:
                score_text = score_elem.get_text()
                match = re.search(r'(\d+)', score_text)
                if match:
                    review.score = float(match.group(1))
            
            # 3. 提取规格信息
            # Halfwheel 通常有规格表格
            spec_tables = soup.find_all(['table', 'div'], class_=re.compile(r'spec|detail'))
            for table in spec_tables:
                rows = table.find_all(['tr', 'li', 'div'])
                for row in rows:
                    text = row.get_text().strip()
                    if ':' in text:
                        key, value = text.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if 'brand' in key or '品牌' in key:
                            review.brand = value
                        elif 'factory' in key:
                            review.factory = value
                        elif 'country' in key:
                            review.country = value
                        elif 'vitola' in key:
                            review.vitola = value
                        elif 'length' in key:
                            review.length = value
                        elif 'ring gauge' in key:
                            match = re.search(r'(\d+)', value)
                            if match:
                                review.ring_gauge = int(match.group(1))
                        elif 'wrapper' in key:
                            review.wrapper = value
                        elif 'binder' in key:
                            review.binder = value
                        elif 'filler' in key:
                            review.filler = value
                        elif 'msrp' in key or 'price' in key:
                            review.msrp = value
                        elif 'release' in key or 'date' in key:
                            review.release_date = value
            
            # 4. 提取正文内容
            content = soup.find('div', class_=re.compile(r'entry-content|post-content'))
            if content:
                review.full_review = content.get_text(separator='\n', strip=True)
                
                # 提取三段式描述
                text = review.full_review
                
                # 寻找三段式标记
                patterns = [
                    (r'(?:First Third|First).*?(?=Second Third|Second|$)', 'first'),
                    (r'(?:Second Third|Second).*?(?=Final Third|Final|$)', 'second'),
                    (r'(?:Final Third|Final).*?(?=Notes|Overall|$)', 'final')
                ]
                
                for pattern, section in patterns:
                    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                    if match:
                        content_text = match.group(0).strip()
                        # 清理标题行
                        lines = content_text.split('\n')
                        if len(lines) > 1:
                            content_text = '\n'.join(lines[1:]).strip()
                        
                        if section == 'first':
                            review.first_third = content_text[:400]
                        elif section == 'second':
                            review.second_third = content_text[:400]
                        elif section == 'final':
                            review.final_third = content_text[:400]
            
            return review if review.name else None
            
        except Exception as e:
            print(f"解析错误: {e}")
            return None
    
    def scrape_urls(self, urls: List[str], headless: bool = True):
        """
        使用 Playwright 抓取 URL 列表
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("请先安装 Playwright: pip install playwright")
            print("然后运行: playwright install chromium")
            return
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            page = context.new_page()
            
            for url in urls:
                if url in self.state['scraped_urls']:
                    print(f"⏭️ 跳过已抓取: {url}")
                    continue
                
                print(f"🔍 正在抓取: {url}")
                try:
                    page.goto(url, wait_until='networkidle', timeout=60000)
                    time.sleep(2)  # 等待页面完全加载
                    
                    html = page.content()
                    review = self.parse_review_page(html, url)
                    
                    if review:
                        self._save_review(review)
                        print(f"✅ 成功: {review.name} ({review.score}分)")
                    else:
                        print(f"⚠️ 未能解析: {url}")
                        self.state['failed_urls'].append(url)
                        
                except Exception as e:
                    print(f"❌ 抓取失败 {url}: {e}")
                    self.state['failed_urls'].append(url)
                
                time.sleep(3)  # 礼貌延迟
            
            browser.close()
        
        self._save_state()
        print(f"\n📊 完成! 成功: {len(self.state['scraped_urls'])}, 失败: {len(self.state['failed_urls'])}")
    
    def export_to_v2_database(self, db_path: str = "/root/.openclaw/workspace/cigar-db/cigars_v2.db"):
        """导出到 v2 数据库"""
        import sys
        sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')
        from database_v2 import CigarDatabaseV2, CigarV2
        
        if not self.reviews_file.exists():
            print("没有找到评审数据文件")
            return
        
        reviews = []
        with open(self.reviews_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    reviews.append(json.loads(line))
        
        print(f"准备导入 {len(reviews)} 条评审...")
        
        with CigarDatabaseV2() as db:
            imported = 0
            for r in reviews:
                review = HalfwheelReview(**r)
                data = review.to_cigar_v2_format()
                
                try:
                    cigar = CigarV2(**data)
                    cid = db.add_cigar(cigar)
                    imported += 1
                    print(f"✅ 已导入: {data['brand']} {data['name']} (评分: {data['expert_rating']})")
                except Exception as e:
                    print(f"❌ 导入失败 {data.get('brand', '?')} {data.get('name', '?')}: {e}")
            
            print(f"\n📊 成功导入 {imported} 款雪茄")


# 一些已知的 Halfwheel 高评分雪茄评审链接
# 用户可以通过浏览器访问 halfwheel.com/reviews 获取更多 URL
KNOWN_REVIEWS = [
    # 这些链接需要根据实际情况更新
    # "https://halfwheel.com/review/xxx"
]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Halfwheel 雪茄爬虫')
    parser.add_argument('--urls', nargs='+', help='要抓取的 URL 列表')
    parser.add_argument('--export', action='store_true', help='导出到数据库')
    parser.add_argument('--visible', action='store_true', help='显示浏览器窗口')
    
    args = parser.parse_args()
    
    scraper = HalfwheelPlaywrightScraper()
    
    if args.export:
        scraper.export_to_v2_database()
    elif args.urls:
        scraper.scrape_urls(args.urls, headless=not args.visible)
    else:
        print("Halfwheel 雪茄爬虫")
        print(f"数据目录: {scraper.output_dir}")
        print(f"已抓取: {len(scraper.state['scraped_urls'])} 个页面")
        print(f"失败: {len(scraper.state['failed_urls'])} 个页面")
        print()
        print("用法:")
        print("  python3 halfwheel_playwright.py --urls URL1 URL2 ...  # 抓取指定页面")
        print("  python3 halfwheel_playwright.py --export              # 导出到数据库")
        print("  python3 halfwheel_playwright.py --urls URL --visible  # 显示浏览器")


if __name__ == "__main__":
    main()
