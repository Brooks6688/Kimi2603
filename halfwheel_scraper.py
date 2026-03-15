#!/usr/bin/env python3
"""
Halfwheel 雪茄数据爬虫
基于浏览器自动化绕过 Cloudflare 防护
"""

import json
import time
import sqlite3
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import re


@dataclass
class HalfwheelCigar:
    """Halfwheel 雪茄数据结构"""
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
    
    # 价格与数量
    msrp: str = ""
    release_date: str = ""
    production: str = ""
    
    # 评分
    score: Optional[float] = None
    
    # 风味描述
    first_third: str = ""  # 前段
    second_third: str = ""  # 中段
    final_third: str = ""  # 尾段
    
    # 其他
    draw: str = ""
    burn: str = ""
    construction: str = ""
    aroma: str = ""
    
    # 完整评审文本
    full_review: str = ""
    
    # 元数据
    source_url: str = ""
    scraped_at: str = ""


class HalfwheelScraper:
    """Halfwheel 爬虫主类"""
    
    BASE_URL = "https://halfwheel.com"
    REVIEWS_URL = "https://halfwheel.com/reviews"
    
    def __init__(self, output_dir: str = "/root/.openclaw/workspace/cigar-db/halfwheel_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session_file = self.output_dir / "scraped_urls.json"
        self.data_file = self.output_dir / "halfwheel_cigars.jsonl"
        
        # 加载已抓取的 URL
        self.scraped_urls = self._load_scraped_urls()
    
    def _load_scraped_urls(self) -> set:
        """加载已抓取的 URL 列表"""
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def _save_scraped_url(self, url: str):
        """保存已抓取的 URL"""
        self.scraped_urls.add(url)
        with open(self.session_file, 'w') as f:
            json.dump(list(self.scraped_urls), f)
    
    def _save_cigar(self, cigar: HalfwheelCigar):
        """保存雪茄数据到 JSONL"""
        with open(self.data_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(cigar), ensure_ascii=False) + '\n')
    
    def get_review_links(self, page: int = 1) -> List[str]:
        """
        获取评审页面链接列表
        由于无法直接抓取，这里提供一个手动添加的方法
        """
        # 在实际使用时，可以通过浏览器获取这些链接
        # 这里返回一些示例链接供测试
        sample_urls = [
            # 可以在这里添加已知的评审页面 URL
        ]
        return sample_urls
    
    def parse_review_html(self, html: str, url: str) -> Optional[HalfwheelCigar]:
        """
        解析评审页面 HTML
        需要根据实际情况调整选择器
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        cigar = HalfwheelCigar()
        cigar.source_url = url
        cigar.scraped_at = time.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # 标题通常是文章标题
            title_elem = soup.find('h1', class_='entry-title')
            if title_elem:
                cigar.name = title_elem.text.strip()
            
            # 评分 - 通常在评分框中
            score_elem = soup.find('div', class_=re.compile(r'score|rating'))
            if score_elem:
                score_text = score_elem.text.strip()
                match = re.search(r'(\d+)', score_text)
                if match:
                    cigar.score = float(match.group(1))
            
            # 规格信息 - 通常在规格表格或列表中
            specs = soup.find('div', class_=re.compile(r'spec|detail'))
            if specs:
                for item in specs.find_all(['li', 'div', 'p']):
                    text = item.get_text().strip()
                    
                    # 品牌
                    if 'Brand:' in text or '品牌' in text:
                        cigar.brand = text.split(':', 1)[-1].strip()
                    
                    # 工厂
                    elif 'Factory:' in text:
                        cigar.factory = text.split(':', 1)[-1].strip()
                    
                    # 产地
                    elif 'Country:' in text:
                        cigar.country = text.split(':', 1)[-1].strip()
                    
                    # 尺寸
                    elif 'Vitola:' in text:
                        cigar.vitola = text.split(':', 1)[-1].strip()
                    
                    # 长度
                    elif 'Length:' in text:
                        cigar.length = text.split(':', 1)[-1].strip()
                    
                    # 环径
                    elif 'Ring Gauge:' in text:
                        match = re.search(r'(\d+)', text)
                        if match:
                            cigar.ring_gauge = int(match.group(1))
                    
                    # 茄衣
                    elif 'Wrapper:' in text:
                        cigar.wrapper = text.split(':', 1)[-1].strip()
                    
                    # 茄套
                    elif 'Binder:' in text:
                        cigar.binder = text.split(':', 1)[-1].strip()
                    
                    # 茄芯
                    elif 'Filler:' in text:
                        cigar.filler = text.split(':', 1)[-1].strip()
                    
                    # 价格
                    elif 'MSRP:' in text or 'Price:' in text:
                        cigar.msrp = text.split(':', 1)[-1].strip()
            
            # 完整评审文本
            content = soup.find('div', class_=re.compile(r'entry-content|content'))
            if content:
                cigar.full_review = content.get_text(separator='\n').strip()
                
                # 尝试提取三段式描述
                text = cigar.full_review
                
                # 前段
                first_match = re.search(r'(?:First Third|前段|First).*?(?=Second|$)', text, re.DOTALL)
                if first_match:
                    cigar.first_third = first_match.group(0)[:500]
                
                # 中段
                second_match = re.search(r'(?:Second Third|中段|Second).*?(?=Final|$)', text, re.DOTALL)
                if second_match:
                    cigar.second_third = second_match.group(0)[:500]
                
                # 尾段
                final_match = re.search(r'(?:Final Third|尾段|Final).*?(?=Notes|$)', text, re.DOTALL)
                if final_match:
                    cigar.final_third = final_match.group(0)[:500]
            
            return cigar
            
        except Exception as e:
            print(f"解析错误: {e}")
            return None
    
    def scrape_single_url(self, url: str) -> Optional[HalfwheelCigar]:
        """抓取单个评审页面"""
        import requests
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            cigar = self.parse_review_html(response.text, url)
            if cigar:
                self._save_cigar(cigar)
                self._save_scraped_url(url)
                print(f"✅ 已抓取: {cigar.name} ({cigar.score}分)")
                return cigar
                
        except Exception as e:
            print(f"❌ 抓取失败 {url}: {e}")
            return None
    
    def export_to_sqlite(self, db_path: str = "/root/.openclaw/workspace/cigar-db/cigars_v2.db"):
        """将 JSONL 数据导入 SQLite"""
        if not self.data_file.exists():
            print("没有数据文件可导入")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 读取 JSONL
        cigars = []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    cigars.append(json.loads(line))
        
        # 插入数据
        imported = 0
        for c in cigars:
            try:
                cursor.execute('''
                    INSERT INTO cigars_v2 
                    (brand, name, origin, length, ring_gauge, wrapper, binder, filler,
                     strength, flavor_profile, expert_rating, expert_source, price_per_stick,
                     description, personal_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    c.get('brand', ''),
                    c.get('name', ''),
                    c.get('country', ''),
                    c.get('length', ''),
                    c.get('ring_gauge', 0),
                    c.get('wrapper', ''),
                    c.get('binder', ''),
                    c.get('filler', ''),
                    'Medium',  # 默认浓度
                    f"{c.get('first_third', '')} | {c.get('second_third', '')} | {c.get('final_third', '')}",
                    c.get('score'),
                    'Halfwheel',
                    self._parse_price(c.get('msrp', '')),
                    c.get('full_review', '')[:500],
                    f"来源: {c.get('source_url', '')}"
                ))
                imported += 1
            except Exception as e:
                print(f"导入失败: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ 成功导入 {imported} 款雪茄到数据库")
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """解析价格字符串"""
        if not price_str:
            return None
        match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
        if match:
            try:
                return float(match.group())
            except:
                pass
        return None


def scrape_with_browser(urls: List[str]):
    """
    使用浏览器自动化抓取
    需要 OpenClaw 的 browser 工具配合
    """
    scraper = HalfwheelScraper()
    
    for url in urls:
        if url in scraper.scraped_urls:
            print(f"跳过已抓取: {url}")
            continue
        
        print(f"正在抓取: {url}")
        # 这里需要配合 browser 工具获取页面 HTML
        # 然后调用 scraper.parse_review_html()


# 手动添加一些已知的优秀评审链接供测试
SAMPLE_URLS = [
    # 用户可以在这里添加具体的 Halfwheel 评审页面 URL
]


if __name__ == "__main__":
    import sys
    
    scraper = HalfwheelScraper()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "export":
            scraper.export_to_sqlite()
        elif sys.argv[1] == "test" and len(sys.argv) > 2:
            # 测试单个 URL
            url = sys.argv[2]
            cigar = scraper.scrape_single_url(url)
            if cigar:
                print(json.dumps(asdict(cigar), indent=2, ensure_ascii=False))
        else:
            print("用法:")
            print("  python3 halfwheel_scraper.py export          # 导出到数据库")
            print("  python3 halfwheel_scraper.py test <url>      # 测试单个 URL")
    else:
        print("Halfwheel 雪茄爬虫")
        print(f"数据目录: {scraper.output_dir}")
        print(f"已抓取: {len(scraper.scraped_urls)} 个页面")
