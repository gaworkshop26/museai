# views/login_page.py
import streamlit as st
import time

def show_login_page():
    # 登录页专属 CSS
    st.markdown("""
    <style>
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding-top: 80px;
        }
        .login-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
            width: 100%;
            max-width: 400px;
            text-align: center;
            border: 1px solid #eee;
        }
        .login-title {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .login-subtitle {
            color: #888;
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)

    # 布局
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("""
        <div class='login-card'>
            <div class='login-title'>Muse AI</div>
            <div class='login-subtitle'>智能面部重塑引擎</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 登录表单 (必须用 Streamlit 原生组件，否则无法交互)
        username = st.text_input("账号", placeholder="admin")
        password = st.text_input("密码", type="password", placeholder="123456")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 登录系统", use_container_width=True):
            if username == "admin" and password == "123456":
                st.session_state.is_logged_in = True
                st.toast("登录成功！跳转中...", icon="✨")
                time.sleep(0.5)
                st.rerun() # 刷新页面，app.py 会检测到登录状态变化
            else:
                st.error("账号或密码错误")
        
        st.markdown("</div>", unsafe_allow_html=True)