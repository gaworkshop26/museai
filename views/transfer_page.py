import streamlit as st
import tempfile
import os
from PIL import Image
# 引入我们刚才写好的核心逻辑
from core.makeup_transfer import apply_makeup_transfer 

def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        try:
            # 创建临时文件保存上传的图片
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                return tmp_file.name
        except Exception as e:
            st.error(f"文件保存失败: {e}")
            return None
    return None

def show_transfer_page():
    st.markdown("## ✨ EleGANt 美妆迁移实验室")
    st.info("💡 请上传一张素颜照和一张带妆照，AI 将自动复刻妆容。")

    col1, col2 = st.columns(2)
    with col1:
        src_file = st.file_uploader("上传素颜照 (Source)", type=['jpg', 'png', 'jpeg'], key="src")
        if src_file:
            st.image(src_file, caption="素颜照", use_container_width=True)
            
    with col2:
        ref_file = st.file_uploader("上传参考妆容 (Reference)", type=['jpg', 'png', 'jpeg'], key="ref")
        if ref_file:
            st.image(ref_file, caption="参考妆容", use_container_width=True)

    if src_file and ref_file:
        if st.button("🚀 开始复刻妆容", type="primary", use_container_width=True):
            with st.spinner("🎨 AI 正在进行妆容迁移，请稍候...（初次运行可能较慢）"):
                try:
                    # 1. 保存临时文件
                    src_path = save_uploaded_file(src_file)
                    ref_path = save_uploaded_file(ref_file)
                    
                    # 2. 调用模型
                    result_img = apply_makeup_transfer(src_path, ref_path)
                    
                    # 3. 显示结果
                    st.success("✅ 迁移成功！")
                    st.image(result_img, caption="复刻结果", use_container_width=True)
                    
                    # 4. 清理临时文件 (可选)
                    os.remove(src_path)
                    os.remove(ref_path)
                    
                except Exception as e:
                    st.error(f"运行出错: {str(e)}")
                    # 打印详细错误方便调试
                    import traceback
                    st.code(traceback.format_exc())