# views/home_page.py
import streamlit as st
import textwrap  # 👈 [关键] 引入这个工具来自动修复缩进问题

def show_home_page():
    # --- 1. SeaArt 风格专属 CSS ---
    # 使用 textwrap.dedent 自动去除多余空格，防止变成代码块
    st.markdown(textwrap.dedent("""
    <style>
        /* 首页 Hero 区域 */
        .hero-section {
            text-align: center;
            padding: 60px 20px 40px 20px;
            background: radial-gradient(circle at 50% 10%, #fff5f7 0%, #ffffff 100%);
        }
        .hero-title {
            font-size: 4rem;
            font-weight: 900;
            letter-spacing: -2px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
        .hero-subtitle {
            font-size: 1.5rem;
            color: #555;
            font-weight: 400;
            margin-bottom: 40px;
        }
        
        /* 样张卡片特效 */
        .style-card-container img {
            border-radius: 16px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        .style-card-container img:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        
        /* 标题样式 */
        .section-header {
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 40px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
    </style>
    """), unsafe_allow_html=True)

    # --- 2. Hero 区域 (标题 + 按钮) ---
    st.markdown(textwrap.dedent("""
    <div class='hero-section'>
        <div class='hero-title'>AI 美妆 · 触手可及</div>
        <div class='hero-subtitle'>基于 BiSeNet 与 SAM 3 的百万级人像重塑引擎</div>
    </div>
    """), unsafe_allow_html=True)

    # 核心跳转按钮
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("⚡️ 立即开始创作 / Start Creating", use_container_width=True):
            st.session_state.nav_menu = "🎨 智能试妆间"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. 热门风格展示 ---
    st.markdown("<div class='section-header'>🔥 热门款式推荐 / Trending Styles</div>", unsafe_allow_html=True)
    
    img_urls = [
        "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?q=80&w=600&auto=format&fit=crop", # 裸妆
        "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?q=80&w=600&auto=format&fit=crop", # 欧美
        "https://images.unsplash.com/photo-1512413914633-b5043f4041ea?q=80&w=600&auto=format&fit=crop", # 少女
        "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?q=80&w=600&auto=format&fit=crop"  # 晚宴
    ]
    img_titles = ["✨ 华丽裸妆", "🍷 欧美截断式", "🌸 韩系少女", "💃 奢华晚宴"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    for i, col in enumerate([col1, col2, col3, col4]):
        with col:
            # 同样使用 dedent 修复这里的 HTML
            st.markdown(textwrap.dedent(f"""
            <div class='style-card-container'>
                <img src='{img_urls[i]}' style='width:100%;'>
            </div>
            """), unsafe_allow_html=True)
            st.markdown(f"**{img_titles[i]}**")
            st.caption("2.3w人正在使用")

    # --- 4. 更多模型展示 ---
    st.markdown("<div class='section-header'>💎 社区精选模型 / Community Models</div>", unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(textwrap.dedent("""
        <div class='style-card-container'>
            <img src='https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?q=80&w=800&auto=format&fit=crop' style='width:100%;'>
        </div>
        """), unsafe_allow_html=True)
        st.markdown("**🌸 AR 创意彩绘系列**")
        st.caption("包含樱花、玫瑰、花钿等 12 种增强现实贴纸。")
        
    with m2:
        st.markdown(textwrap.dedent("""
        <div class='style-card-container'>
            <img src='https://images.unsplash.com/photo-1500917293891-ef795e70e1f6?q=80&w=800&auto=format&fit=crop' style='width:100%;'>
        </div>
        """), unsafe_allow_html=True)
        st.markdown("**📷 SAM 3 光影大师**")
        st.caption("Meta 最新分割模型加持，自动计算景深。")

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; color:#ccc;'>Designed by Gu Mengfei | Muse AI Lab © 2026</div>", unsafe_allow_html=True)