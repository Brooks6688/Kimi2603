import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import sys

# 添加数据库路径
sys.path.insert(0, '/root/.openclaw/workspace/cigar-db')

# 页面配置
st.set_page_config(
    page_title="雪茄数据库 CigarDB",
    page_icon="🚬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #8B4513;
    }
    .cigar-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #8B4513;
    }
    .rating-badge {
        background: #FFD700;
        color: #000;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: bold;
    }
    .origin-tag {
        background: #4a4a4a;
        color: #fff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """加载雪茄数据"""
    db_path = Path(__file__).parent.parent / "cigar-db" / "cigars_v2.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    df = pd.read_sql_query("SELECT * FROM cigars_v2", conn)
    conn.close()
    return df

def get_origins(df):
    """获取所有产地"""
    origins = df['origin'].dropna().unique()
    return sorted([o for o in origins if o])

def get_brands(df):
    """获取所有品牌"""
    brands = df['brand'].dropna().unique()
    return sorted([b for b in brands if b])

def get_strengths(df):
    """获取所有浓度等级"""
    strengths = df['strength'].dropna().unique()
    return sorted([s for s in strengths if s])

def display_cigar_card(cigar):
    """显示雪茄卡片"""
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**{cigar['brand']}**")
            if cigar['line']:
                st.caption(f"*{cigar['line']}*")
            st.markdown(f"### {cigar['name']}")
        
        with col2:
            if cigar['origin']:
                st.markdown(f"🏳️ {cigar['origin']}")
            if cigar['strength']:
                st.markdown(f"💨 {cigar['strength']}")
            size = []
            if cigar['length']:
                size.append(cigar['length'])
            if cigar['ring_gauge']:
                size.append(f"{cigar['ring_gauge']}环")
            if size:
                st.markdown(f"📏 {' × '.join(size)}")
        
        with col3:
            if pd.notna(cigar['expert_rating']):
                st.markdown(f"<span class='rating-badge'>{cigar['expert_rating']:.0f}分</span>", 
                           unsafe_allow_html=True)
            if pd.notna(cigar['price_per_stick']):
                st.markdown(f"💵 ${cigar['price_per_stick']:.2f}")
        
        # 展开详情
        with st.expander("查看详情"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**烟叶成分**")
                st.markdown(f"- 茄衣: {cigar['wrapper'] or '未知'}")
                st.markdown(f"- 茄套: {cigar['binder'] or '未知'}")
                st.markdown(f"- 茄芯: {cigar['filler'] or '未知'}")
                
                if cigar['primary_flavors']:
                    st.markdown("**主要风味**")
                    st.markdown(cigar['primary_flavors'])
                
                if cigar['secondary_flavors']:
                    st.markdown("**次要风味**")
                    st.markdown(cigar['secondary_flavors'])
            
            with col_b:
                if cigar['pairing_drink']:
                    st.markdown("**推荐搭配**")
                    st.markdown(f"🍷 {cigar['pairing_drink']}")
                
                if cigar['best_time']:
                    st.markdown("**最佳时段**")
                    st.markdown(cigar['best_time'])
                
                if cigar['description']:
                    st.markdown("**描述**")
                    st.markdown(cigar['description'][:300] + "..." if len(cigar['description']) > 300 else cigar['description'])
        
        st.divider()

def main():
    # 标题
    st.markdown("<div class='main-header'>🚬 雪茄数据库 CigarDB</div>", 
                unsafe_allow_html=True)
    st.caption("专业雪茄品鉴与推荐系统 | 40+ 款精选雪茄")
    
    # 加载数据
    try:
        df = load_data()
    except Exception as e:
        st.error(f"加载数据库失败: {e}")
        st.info("请确保数据库文件存在: cigar-db/cigars_v2.db")
        return
    
    # 侧边栏筛选
    st.sidebar.header("🔍 筛选条件")
    
    # 搜索
    search_term = st.sidebar.text_input("搜索关键词", placeholder="品牌、风味、产地...")
    
    # 产地筛选
    origins = ["全部"] + get_origins(df)
    selected_origin = st.sidebar.selectbox("产地", origins)
    
    # 品牌筛选
    brands = ["全部"] + get_brands(df)
    selected_brand = st.sidebar.selectbox("品牌", brands)
    
    # 浓度筛选
    strengths = ["全部"] + get_strengths(df)
    selected_strength = st.sidebar.selectbox("浓度", strengths)
    
    # 价格范围
    min_price = float(df['price_per_stick'].min()) if df['price_per_stick'].notna().any() else 0
    max_price = float(df['price_per_stick'].max()) if df['price_per_stick'].notna().any() else 500
    price_range = st.sidebar.slider("价格范围 ($)", 
                                    min_value=int(min_price), 
                                    max_value=int(max_price),
                                    value=(int(min_price), int(max_price)))
    
    # 评分筛选
    min_rating = st.sidebar.slider("最低专家评分", 0, 100, 0)
    
    # 排序方式
    st.sidebar.header("📊 排序")
    sort_options = {
        "专家评分 (高→低)": "expert_rating",
        "价格 (低→高)": "price_per_stick",
        "价格 (高→低)": "price_per_stick_desc",
        "品牌名": "brand"
    }
    sort_by = st.sidebar.selectbox("排序方式", list(sort_options.keys()))
    
    # 应用筛选
    filtered_df = df.copy()
    
    if search_term:
        mask = (
            filtered_df['brand'].str.contains(search_term, case=False, na=False) |
            filtered_df['name'].str.contains(search_term, case=False, na=False) |
            filtered_df['primary_flavors'].str.contains(search_term, case=False, na=False) |
            filtered_df['origin'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if selected_origin != "全部":
        filtered_df = filtered_df[filtered_df['origin'] == selected_origin]
    
    if selected_brand != "全部":
        filtered_df = filtered_df[filtered_df['brand'] == selected_brand]
    
    if selected_strength != "全部":
        filtered_df = filtered_df[filtered_df['strength'] == selected_strength]
    
    filtered_df = filtered_df[
        (filtered_df['price_per_stick'].isna()) | 
        ((filtered_df['price_per_stick'] >= price_range[0]) & 
         (filtered_df['price_per_stick'] <= price_range[1]))
    ]
    
    if min_rating > 0:
        filtered_df = filtered_df[filtered_df['expert_rating'] >= min_rating]
    
    # 排序
    sort_col = sort_options[sort_by]
    if sort_col == "price_per_stick_desc":
        filtered_df = filtered_df.sort_values('price_per_stick', ascending=False)
    elif sort_col == "expert_rating":
        filtered_df = filtered_df.sort_values('expert_rating', ascending=False, na_position='last')
    else:
        filtered_df = filtered_df.sort_values(sort_col, na_position='last')
    
    # 标签页
    tab1, tab2, tab3 = st.tabs(["📋 雪茄列表", "📊 数据统计", "🏆 排行榜"])
    
    with tab1:
        st.markdown(f"**找到 {len(filtered_df)} 款雪茄**")
        
        for _, cigar in filtered_df.iterrows():
            display_cigar_card(cigar)
    
    with tab2:
        st.subheader("数据库统计")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("雪茄总数", len(df))
        with col2:
            st.metric("品牌数量", len(get_brands(df)))
        with col3:
            st.metric("产地数量", len(get_origins(df)))
        with col4:
            humidor_count = df['in_humidor'].sum()
            st.metric("保湿盒中", int(humidor_count))
        
        # 产地分布
        st.subheader("产地分布")
        origin_counts = df['origin'].value_counts().head(10)
        st.bar_chart(origin_counts)
        
        # 浓度分布
        st.subheader("浓度分布")
        strength_counts = df['strength'].value_counts()
        st.bar_chart(strength_counts)
        
        # 价格分布
        st.subheader("价格分布")
        price_df = df[df['price_per_stick'].notna()]
        if len(price_df) > 0:
            st.line_chart(price_df.set_index('brand')['price_per_stick'].sort_values(ascending=False).head(20))
    
    with tab3:
        st.subheader("🏆 专家评分 TOP 10")
        top_rated = df[df['expert_rating'].notna()].nlargest(10, 'expert_rating')
        
        for i, (_, cigar) in enumerate(top_rated.iterrows(), 1):
            cols = st.columns([0.5, 3, 1, 1])
            with cols[0]:
                st.markdown(f"**#{i}**")
            with cols[1]:
                st.markdown(f"**{cigar['brand']} {cigar['name']}**")
                st.caption(f"{cigar['origin']} | {cigar['strength']}")
            with cols[2]:
                st.markdown(f"<span class='rating-badge'>{cigar['expert_rating']:.0f}</span>", 
                           unsafe_allow_html=True)
            with cols[3]:
                if pd.notna(cigar['price_per_stick']):
                    st.markdown(f"${cigar['price_per_stick']:.0f}")
            st.divider()
        
        # 性价比榜单
        st.subheader("💰 性价比 TOP 10")
        value_df = df[(df['expert_rating'].notna()) & (df['price_per_stick'].notna()) & (df['price_per_stick'] > 0)].copy()
        if len(value_df) > 0:
            value_df['value_score'] = value_df['expert_rating'] / value_df['price_per_stick']
            top_value = value_df.nlargest(10, 'value_score')
            
            for i, (_, cigar) in enumerate(top_value.iterrows(), 1):
                cols = st.columns([0.5, 3, 1, 1, 1])
                with cols[0]:
                    st.markdown(f"**#{i}**")
                with cols[1]:
                    st.markdown(f"**{cigar['brand']} {cigar['name']}**")
                with cols[2]:
                    st.markdown(f"{cigar['expert_rating']:.0f}分")
                with cols[3]:
                    st.markdown(f"${cigar['price_per_stick']:.0f}")
                with cols[4]:
                    st.markdown(f"⚡ {cigar['value_score']:.2f}")
                st.divider()

if __name__ == "__main__":
    main()
