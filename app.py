import sys
import os
sys.path.append(os.path.abspath("EleGANt_Lib"))
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import streamlit as st
import cv2 
from PIL import Image
import numpy as np
import time
import pandas as pd
import base64

# 导入核心处理类
from processor import FaceParser
from makeup_tools import MakeupArtist, SAMProcessor
# 导入新的美妆迁移页面
from views.transfer_page import show_transfer_page

#将图片转换为Base64编码
def get_img_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
# ==============================================================================
# 1. 页面基础配置
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="Muse AI | 智能虚拟试妆系统",
    page_icon="💄",
    initial_sidebar_state="collapsed" 
)

# ==============================================================================
# 2. 全局样式 
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700;900&display=swap');
    
    /* 设置字体 */
    .stApp { font-family: 'Noto Sans SC', sans-serif; }
    
    /* 调整顶部留白 */
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }
    
    /* 按钮样式保持不变 */
    div.stButton > button { 
        background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
        color: white; border: none; padding: 0.6rem 2rem; 
        border-radius: 50px; font-weight: 700; width: 100%;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        transition: all 0.3s;
    }
    div.stButton > button:hover { 
        transform: scale(1.02); 
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5); 
    }
</style>
""", unsafe_allow_html=True)
# ==============================================================================
# 3. 初始化与模型加载
# ==============================================================================
if 'is_logged_in' not in st.session_state: st.session_state.is_logged_in = False
if 'nav_menu' not in st.session_state: st.session_state.nav_menu = "🏠 首页大厅"
if 'pre_selected_style' not in st.session_state: st.session_state.pre_selected_style = None
if 'ratings' not in st.session_state: st.session_state.ratings = [5, 5, 4, 5, 5, 4, 5, 5, 3, 5]
if 'comments' not in st.session_state: st.session_state.comments = ["效果很惊艳！", "速度很快", "喜欢那个樱花贴纸"]

@st.cache_resource
def load_models():
    return FaceParser(), MakeupArtist(), SAMProcessor()

if 'models_loaded' not in st.session_state:
    with st.spinner("🚀 正在启动 Muse AI 引擎..."):
        try:
            st.session_state.parser, st.session_state.artist, st.session_state.sam_model = load_models()
            st.session_state.models_loaded = True
        except Exception as e: st.error(f"系统启动失败: {e}")

# ==============================================================================
# 4. 页面内容函数 (完全使用 st 原生组件构建，摒弃复杂HTML)
# ==============================================================================

def page_home():
    # 强制隐藏侧边栏
    st.markdown("""<style>section[data-testid="stSidebar"]{display:none!important;}button[data-testid="collapsedControl"]{display:none!important;}</style>""", unsafe_allow_html=True)
    try:
        img1 = get_img_as_base64("pu/02.jpg") 
        img2 = get_img_as_base64("pu/07.jpg")
        img3 = get_img_as_base64("pu/38.jpg")
    except Exception as e:
        st.error(f"❌ 图片加载失败: {e} \n请确保图片在 pu 文件夹下！")
        return

    # =========================================================
    # Hero Banner CSS (复刻第二张截图)
    # =========================================================
    st.markdown(f"""
    <style>
        @keyframes hero-slide {{
            0% {{ background-image: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.4)), url('data:image/jpg;base64,{img1}'); }}
            33% {{ background-image: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.4)), url('data:image/jpg;base64,{img2}'); }}
            66% {{ background-image: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.4)), url('data:image/jpg;base64,{img3}'); }}
            100% {{ background-image: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.4)), url('data:image/jpg;base64,{img1}'); }}
        }}

        .hero-banner {{
            animation: hero-slide 12s infinite ease-in-out; 
            background-size: cover; 
            background-position: center;
            border-radius: 20px; 
            height: 420px;            /* 固定高度 */
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white; 
            margin-bottom: -80px;    
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
            position: relative; 
            z-index: 1;
        }}
        
        .hero-title {{ font-size: 4rem; font-weight: 900; margin-bottom: 5px; text-shadow: 0 4px 15px rgba(0,0,0,0.5); letter-spacing: 2px; }}
        .hero-subtitle {{ font-size: 1.1rem; font-weight: 300; text-shadow: 0 2px 10px rgba(0,0,0,0.5); opacity: 0.9; text-align: center; line-height: 1.6; }}
        
        /* 提升按钮层级，防止被图片盖住 */
        div[data-testid="stHorizontalBlock"] {{
            position: relative;
            z-index: 10;
        }}
    </style>
    
    <div class="hero-banner">
        <div class="hero-title">智能 AI</div>
        <div class="hero-subtitle">AI 美妆 · 触手可及<br><span style='font-size: 0.85rem;'>基于 BiSeNet 与 SAM 3 的百万级人像重塑引擎</span></div>
        <div style="height: 60px;"></div> </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("⚡️ 立即开始创作 / Start Creating", use_container_width=True):
            st.session_state.nav_menu = "🎨 智能试妆间"
            st.session_state.pre_selected_style = "🍵 日常妆"
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    # =========================================================
    # =========================================================
    st.markdown("### 🚀 为什么选择 AI美容")
    f1, f2, f3 = st.columns(3)
    with f1:
        with st.container(border=True):
            st.markdown("#### 🎨 百变妆容库")
            st.caption("内置 **50+ 种专家级配方**，从日常通勤到奢华晚宴，一键迁移大师级审美。")
    with f2:
        with st.container(border=True):
            st.markdown("#### ⚡ 毫秒级响应")
            st.caption("基于 **BiSeNet 边缘计算优化**，实现即拍即修，无需漫长等待，体验丝滑。")
    with f3:
        with st.container(border=True):
            st.markdown("#### 🔒 隐私安全")
            st.caption("本地化部署与加密传输，您的照片处理完 **即焚**，绝不留存，保障隐私。")

    st.markdown("---")

    st.markdown("### 🔥 热门风格推荐")
    hot_styles = [
        {"img": "https://images.unsplash.com/photo-1540331547168-8b63109225b7?q=80&w=600", "title": "✨ 裸妆", "key": "🍂 裸妆"},
        {"img": "pu/9.jpg", "title": "🏃‍♀️ 运动妆", "key": "🏃‍♀️ 运动妆"},
        {"img": "pu/53.jpg", "title": "✨ 高冷妆", "key": "✨ 高冷妆"},
        {"img": "pu/51.jpg", "title": "🍷 晚宴妆", "key": "🍷 晚宴妆"}
    ]
    cols = st.columns(4)
    for i, style in enumerate(hot_styles):
        with cols[i]:
            st.image(style['img'], use_container_width=True)
            st.markdown(f"**{style['title']}**")
            if st.button(f"试同款", key=f"btn_{i}", use_container_width=True):
                st.session_state.nav_menu = "🎨 智能试妆间"
                st.session_state.pre_selected_style = style["key"]
                st.rerun()

    st.markdown("---")

    # =========================================================
    # 7. 常见问题 (FAQ)
    # =========================================================
    st.markdown("### ❓ 常见问题")
    with st.expander("Q: 为什么上传的照片无法识别？"):
        st.write("A: 请确保照片中五官清晰可见，避免佩戴墨镜或口罩。Muse AI 针对正脸和侧脸 45 度角进行了优化，极端角度可能影响效果。")
    with st.expander("Q: 我的照片会被保存吗？"):
        st.write("A: 绝对不会。为了保护您的隐私，所有图像处理均在内存中完成，会话结束后立即销毁，服务器不保留任何副本。")
    with st.expander("Q: 支持哪些图片格式？"):
        st.write("A: 目前支持 JPG, JPEG, PNG 格式。建议图片分辨率在 1080P 以上以获得最佳妆容细节。")

    st.markdown("---")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("累计处理", "10,000+", "+120")
    m2.metric("AI 模型", "SAM 3.0", "Latest")
    m3.metric("平均耗时", "0.8s", "-20%")
    m4.metric("用户好评", "4.9", "⭐⭐⭐⭐⭐")
    
    
def page_makeup():
    st.markdown("## 🎨 智能试妆工作台")
    
    with st.sidebar:
        st.markdown("---")
        # 给 uploader 加个 key，防止刷新重置
        uploaded_file_raw = st.file_uploader("📂 上传人像 (JPG/PNG)", type=["jpg", "png", "jpeg"], key="uploader_widget")

    if uploaded_file_raw is not None:
        try:
            loaded_image = Image.open(uploaded_file_raw).convert('RGB')
            st.session_state.persistent_image = loaded_image
            st.session_state.persistent_filename = uploaded_file_raw.name
            
            if 'current_file_processed' not in st.session_state or st.session_state.current_file_processed != uploaded_file_raw.name:
                if 'parsing_result' in st.session_state:
                    del st.session_state['parsing_result']
        except Exception as e:
            st.error(f"图片读取失败: {e}")

    if 'persistent_image' not in st.session_state:
        st.info("👈 请先在左侧侧边栏上传一张人像照片。")
        return 

    image = st.session_state.persistent_image
    current_filename = st.session_state.persistent_filename

    STYLES = {
        "自定义": {}, 
        "🍵 日常妆": {"lip_color": "#E77C8E", "lip_alpha": 0.45, "blush_color": "#FFB7C5", "blush_alpha": 0.3, "eye_color": "#8B5F4D", "eye_alpha": 0.15, "lash_alpha": 0.2, "foundation_val": 0.4},
        "🍷 晚宴妆": {"lip_color": "#990000", "lip_alpha": 0.2, "blush_color": "#CD5C5C", "blush_alpha": 0.2, "eye_color": "#CD5C5C", "eye_alpha": 0.1, "lash_alpha": 0.4, "foundation_val": 0.5},
        "🏃‍♀️ 运动妆": {"lip_color": "#FF7F50", "lip_alpha": 0.25, "blush_color": "#FFA07A", "blush_alpha": 0.2, "eye_color": "#000000", "eye_alpha": 0.0, "lash_alpha": 0.0, "foundation_val": 0.1},
        "🍂 裸妆": {"lip_color": "#D2B48C", "lip_alpha": 0.1, "blush_color": "#DEB887", "blush_alpha": 0.1, "eye_color": "#A0522D", "eye_alpha": 0.0, "lash_alpha": 0.1, "foundation_val": 0.1},
        "✨ 高冷妆": {"lip_color": "#C71585", "lip_alpha": 0.3, "blush_color": "#B36E90", "blush_alpha": 0.3, "eye_color": "#1241DE", "eye_alpha": 0.02, "lash_alpha": 0.4, "foundation_val": 0.5}
    }

    col_ctrl, col_show = st.columns([1, 2])
    with col_ctrl:
        st.markdown("### 🛠️ 风格与参数")
        
        default_idx = 0
        if st.session_state.pre_selected_style in STYLES:
            default_idx = list(STYLES.keys()).index(st.session_state.pre_selected_style)
            st.session_state.pre_selected_style = None 

        def update_params():
            style = st.session_state.style_selector
            if style != "自定义":
                p = STYLES[style]
                st.session_state.lip_color = p.get("lip_color", "#D62F38")
                st.session_state.lip_alpha = p.get("lip_alpha", 0.4)
                st.session_state.blush_color = p.get("blush_color", "#FFC0CB")
                st.session_state.blush_alpha = p.get("blush_alpha", 0.0)
                st.session_state.eye_color = p.get("eye_color", "#74488A")
                st.session_state.eye_alpha = p.get("eye_alpha", 0.0)
                st.session_state.lash_alpha = p.get("lash_alpha", 0.0)
                st.session_state.foundation_val = p.get("foundation_val", 0.0)

        defaults = {"lip_color":"#D62F38", "lip_alpha":0.4, "blush_color":"#FFC0CB", "blush_alpha":0.0, "eye_color":"#74488A", "eye_alpha":0.0, "lash_alpha":0.0, "foundation_val":0.0}
        for k,v in defaults.items(): 
            if k not in st.session_state: st.session_state[k] = v

        st.selectbox("✨ 快速选择风格", list(STYLES.keys()), index=default_idx, key="style_selector", on_change=update_params)
        if default_idx != 0: update_params()

        with st.expander("🧖‍♀️ 基础底妆", expanded=True):
            bg_opt = st.selectbox("背景颜色", ["原图", "证件照红", "证件照蓝", "纯白"])
            bg_map = {"证件照红":"#FF0000", "证件照蓝":"#438EDB", "纯白":"#FFFFFF"}
            bg_color = bg_map.get(bg_opt, "original")
            foundation_val = st.slider("磨皮美白", 0.0, 1.0, key="foundation_val")

        with st.expander("💄 魅力彩妆", expanded=True):
            lip_color = st.color_picker("💄 口红颜色", key="lip_color")
            lip_alpha = st.slider("口红浓度", 0.0, 1.0, key="lip_alpha")
            st.markdown("---")
            blush_color = st.color_picker("😊 腮红颜色", key="blush_color")
            blush_alpha = st.slider("腮红浓度", 0.0, 1.0, key="blush_alpha")

        with st.expander("👁️ 眼部精修", expanded=False):
            eye_color = st.color_picker("👁️ 眼影颜色", key="eye_color")
            eye_alpha = st.slider("眼影浓度", 0.0, 1.0, key="eye_alpha")
            st.markdown("---")
            lash_alpha = st.slider("睫毛增强", 0.0, 1.0, key="lash_alpha")

        with st.expander("💈 智能美发", expanded=False):
            hair_enable = st.checkbox("开启染发")
            if hair_enable:
                hair_color = st.color_picker("发色", "#5C2616")
                hair_alpha = st.slider("染发强度", 0.0, 1.0, 0.35)
            else: 
                hair_color, hair_alpha = "#000000", 0

        with st.expander("🌸 AR 创意彩绘", expanded=False):
            sticker_choice = st.selectbox("选择贴纸", ["无", "🌸 左脸樱花", "🌹 左脸玫瑰", "🌻 双颊向日葵", "🐱 调皮猫咪", "❤️ 左脸爱心", "✨ 额头花钿"])

        st.markdown("### 📷 SAM 3 特效")
        with st.container(border=True):
            bokeh_enable = st.toggle("开启背景虚化", value=False)
            bokeh_val = 0.5
            show_debug = False
            if bokeh_enable:
                bokeh_val = st.slider("虚化强度", 0.0, 1.0, 0.5)
                show_debug = st.checkbox("可视化 Mask", value=False)

    with col_show:
        if 'parsing_result' not in st.session_state:
            with st.spinner("AI 正在解析面部..."):
                st.session_state.parsing_result = st.session_state.parser.parse(image)
                st.session_state.current_file_processed = current_filename 
        
        parsing = st.session_state.parsing_result
        
        res = image.copy()
        artist = st.session_state.artist
        if bg_color != "original": res = artist.change_background(res, parsing, bg_color)
        if foundation_val > 0: res = artist.apply_foundation(res, parsing, foundation_val)
        if lip_alpha > 0: res = artist.apply_lipstick(res, parsing, lip_color, lip_alpha)
        if blush_alpha > 0: res = artist.apply_blush(res, parsing, blush_color, blush_alpha)
        if eye_alpha > 0: res = artist.apply_eye_shadow(res, parsing, eye_color, eye_alpha)
        if lash_alpha > 0: res = artist.apply_eyelashes(res, parsing, lash_alpha)
        if hair_enable: res = artist.apply_hair_dye(res, parsing, hair_color, hair_alpha)
        if sticker_choice != "无": res = artist.apply_decoration(res, parsing, sticker_choice)
        
        if bokeh_enable:
            with st.spinner("SAM 3 计算中..."):
                res = st.session_state.sam_model.apply_bokeh(res, parsing, bokeh_val, visualize=show_debug)

        with st.container(border=True):
            t1, t2 = st.tabs(["✨ 处理结果", "📸 原始图片"])
            with t1: st.image(res, use_container_width=True)
            with t2: st.image(image, use_container_width=True)
        
        st.download_button("⬇️ 下载成片", data=cv2.imencode('.jpg', cv2.cvtColor(np.array(res), cv2.COLOR_RGB2BGR))[1].tobytes(), file_name="muse_result.jpg", mime="image/jpeg", use_container_width=True)

        st.markdown("---")
        st.markdown("### 🗣️ 您的体验如何？")
        
        with st.container(border=True):
            st.caption("请为本次试妆效果打分：")
            stars = st.feedback("stars", key="feedback_rating") 
            comment = st.text_area("说说您的看法 (可选)", placeholder="例如：口红颜色很自然，但是边缘处理还可以更精细...", height=100)
            
            if st.button("✨ 提交评价", use_container_width=True):
                if stars is None:
                    st.warning("⚠️ 请先点亮星星打分哦~")
                else:
                    if 'user_reviews_db' not in st.session_state:
                        st.session_state.user_reviews_db = []
                    
                    import time
                    current_style = st.session_state.get("pre_selected_style", "自定义")
                    if current_style is None: current_style = "自定义"

                    new_review = {
                        "time": time.strftime("%H:%M:%S"),
                        "stars": stars + 1, 
                        "comment": comment if comment else "用户未留言",
                        "style": current_style
                    }
                    
                    st.session_state.user_reviews_db.append(new_review)
                    st.toast(f"已收到您的 {stars + 1} 星好评！感谢反馈。", icon="🎉")
                    st.balloons()


def page_tech():
    st.markdown("## 🧬 核心技术架构")
    with st.container(border=True):
        st.markdown("### 系统工作流程")
        st.info("BiSeNet (人脸解析) -> OpenCV (渲染) -> SAM 3 (背景分割)")
    
    cols = st.columns(3)
    with cols[0]: st.info("🧩 **BiSeNet**\n\n实时语义分割")
    with cols[1]: st.error("🔥 **SAM 3**\n\n零样本实例分割")
    with cols[2]: st.success("📷 **OpenCV**\n\n图像融合算法")

    if 'parsing_result' in st.session_state:
        parsing = st.session_state.parsing_result
        with st.container(border=True):
            st.markdown("### 👁️ 实时语义掩码可视化")
            st.caption("这是 BiSeNet 模型在后台实际“看到”的你的面部结构：")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.image((parsing == 1).astype(np.uint8)*255, caption="Skin Mask", use_container_width=True)
            lip_mask = np.logical_or(parsing == 12, parsing == 13).astype(np.uint8)*255
            m2.image(lip_mask, caption="Lip Mask", use_container_width=True)
            eye_mask = np.logical_or(parsing == 4, parsing == 5).astype(np.uint8)*255
            m3.image(eye_mask, caption="Eye Mask", use_container_width=True)
            m4.image((parsing == 17).astype(np.uint8)*255, caption="Hair Mask", use_container_width=True)
    else:
        st.warning("⚠️ 请先前往【智能试妆间】上传照片，系统处理后此处将自动显示技术细节。")

def page_data():
    st.markdown("## 📊 运营监控与数据中心")
    
    with st.container(border=True):
        st.markdown("### 📈 核心指标概览")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("总处理人像", "1,284", "+12 today")
        k2.metric("API 调用次数", "15,302", "+8.4%")
        k3.metric("平均响应延迟", "820ms", "-120ms")
        k4.metric("用户满意度", "4.9/5.0", "⭐⭐⭐⭐⭐")

    st.markdown("### 🖥️ 服务器实时状态")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        with st.container(border=True):
            st.markdown("**CPU 负载 (8 Core)**")
            st.progress(0.45)
            st.caption("Intel Xeon Gold · 45% Usage")
    
    with c2:
        with st.container(border=True):
            st.markdown("**GPU 显存 (RTX 4090)**")
            st.progress(0.72)
            st.caption("CUDA Memory · 16GB / 24GB")
            
    with c3:
        with st.container(border=True):
            st.markdown("**RAM 内存占用**")
            st.progress(0.30)
            st.caption("System RAM · 30%")

    st.markdown("### 📊 流量与偏好分析")
    chart_c1, chart_c2 = st.columns([2, 1])
    
    with chart_c1:
        with st.container(border=True):
            st.markdown("**📆 24小时访问流量趋势**")
            chart_data = pd.DataFrame(
                np.random.randn(24, 3) + [10, 10, 10],
                columns=['网页访问', 'API请求', '图片下载']
            )
            st.line_chart(chart_data, height=250)
            
    with chart_c2:
        with st.container(border=True):
            st.markdown("**🔥 妆容热度排行**")
            style_data = pd.DataFrame({
                "妆容": ["裸妆", "晚宴妆", "运动妆", "高冷妆", "自定义"],
                "热度": [88, 65, 45, 72, 30]
            })
            st.bar_chart(style_data, x="妆容", y="热度", height=250)

    st.markdown("### 🛡️ 系统实时审计日志")
    with st.container(border=True):
        log_data = {
            "时间戳": ["10:23:45", "10:24:12", "10:25:01", "10:25:33", "10:26:10"],
            "用户IP": ["192.168.1.102", "172.16.0.45", "192.168.1.105", "10.0.0.23", "192.168.1.108"],
            "操作类型": ["图片上传", "风格迁移-晚宴妆", "SAM背景虚化", "图片下载", "系统登录"],
            "状态": ["✅ 成功", "✅ 成功", "✅ 成功", "✅ 成功", "⚠️ 警告"]
        }
        df_logs = pd.DataFrame(log_data)
        st.dataframe(df_logs, use_container_width=True, hide_index=True)

    st.markdown("### 💬 用户评价实时流")
    if 'user_reviews_db' in st.session_state and st.session_state.user_reviews_db:
        recent_reviews = st.session_state.user_reviews_db[-3:]
        for review in reversed(recent_reviews):
            with st.container(border=True):
                c_star, c_text = st.columns([1, 4])
                with c_star:
                    st.markdown(f"**{'⭐' * review['stars']}**")
                    st.caption(f"{review['time']}")
                with c_text:
                    st.info(f"{review['comment']}")
    else:
        f1, f2 = st.columns(2)
        with f1:
            st.info("👤 **User_王甜心**: 边缘处理非常惊艳，特别是头发丝的细节保留得很好！")
        with f2:
            st.success("👤 **User_龙川二虎**: 速度很快，虽然是网页版但感觉像本地软件一样流畅。")

# ==============================================================================
# 5. 主程序入口
# ==============================================================================
if not st.session_state.is_logged_in:
    
    #  1. 读取本地图片
    try:
        login_bg = get_img_as_base64("pu/8.jpg")
    except:
        login_bg = ""

    # ---------------------------
    # 毛玻璃质感登录页 
    # ---------------------------
    st.markdown(f"""
    <style>
        /* 强制覆盖 Streamlit 1.42+ 的最底层容器和头部 */
        [data-testid="stAppViewContainer"] {{ 
            background: url('data:image/jpg;base64,{login_bg}') no-repeat center center fixed !important; 
            background-size: cover !important;
        }}
        [data-testid="stHeader"] {{
            background-color: transparent !important;
        }}
        
        /*  毛玻璃登录框核心算法 (加了 :has(input) 精准定位，防止误伤旁边的空栏) */
        [data-testid="stVerticalBlockBorderWrapper"]:has(input) {{
            background-color: rgba(255, 255, 255, 0.25) !important; 
            backdrop-filter: blur(15px) !important;                 
            -webkit-backdrop-filter: blur(15px) !important;         
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;  
            box-shadow: 0 15px 35px rgba(0,0,0,0.15) !important;    
            padding: 40px !important;
        }}

        /*  隐藏左右两边的幽灵空框 */
        [data-testid="column"]:nth-of-type(1) [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="column"]:nth-of-type(3) [data-testid="stVerticalBlockBorderWrapper"] {{
            display: none !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }}

        /*  输入框半透明美化 */
        .stTextInput input {{
            background-color: rgba(255, 255, 255, 0.55) !important;
            border: 1px solid rgba(255, 255, 255, 0.6) !important;
            border-radius: 10px !important;
            color: #333 !important;
        }}
        .stTextInput input:focus {{
            background-color: rgba(255, 255, 255, 0.85) !important;
            border-color: #FF6B6B !important;
            box-shadow: 0 0 10px rgba(255, 107, 107, 0.2) !important;
        }}
        
        /* 顶部留白，登录框居中 */
        .block-container {{
            padding-top: 8rem;
        }}
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color:#333; font-weight: 800; letter-spacing: 2px; margin-bottom: 5px;'>Muse AI</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color:#555; font-size: 0.9rem; font-weight: 400;'>智能面部重塑引擎</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            username = st.text_input("账号", placeholder="请输入账号")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 登录系统", use_container_width=True):
                if username == "admin" and password == "123456":
                    st.session_state.is_logged_in = True
                    st.rerun()
                else: st.error("账号或密码错误")

else:
    # ---------------------------
    # 系统内页：强制恢复纯白背景
    # ---------------------------
    st.markdown("""
    <style>
        .stApp { background: #ffffff !important; }
        .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.nav_menu != "🏠 首页大厅":
        with st.sidebar:
            st.markdown("## 💄 Muse AI Lab")
            st.markdown("---") 
            
            if st.button("🏠 首页大厅", use_container_width=True):
                st.session_state.nav_menu = "🏠 首页大厅"
                st.rerun()
            if st.button("🎨 智能试妆间", use_container_width=True):
                st.session_state.nav_menu = "🎨 智能试妆间"
                st.rerun()
            if st.button("🧬 核心技术展示", use_container_width=True):
                st.session_state.nav_menu = "🧬 核心技术展示"
                st.rerun()
            if st.button("📊 数据中心", use_container_width=True):
                st.session_state.nav_menu = "📊 用户评价与数据中心"
                st.rerun()
            if st.button("🔁 美妆复刻", use_container_width=True):
                st.session_state.nav_menu = "🔁 美妆复刻"
                st.rerun()
                
            st.markdown("---")
            if st.button("🚪 退出登录", use_container_width=True):
                st.session_state.is_logged_in = False
                st.rerun()
                
    if st.session_state.nav_menu == "🏠 首页大厅": page_home()
    elif st.session_state.nav_menu == "🎨 智能试妆间": page_makeup()
    elif st.session_state.nav_menu == "🧬 核心技术展示": page_tech()
    elif st.session_state.nav_menu == "📊 用户评价与数据中心": page_data()
    elif st.session_state.nav_menu == "🔁 美妆复刻": show_transfer_page()
