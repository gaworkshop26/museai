@echo off
echo 正在激活虚拟环境...
call venv\Scripts\activate

echo 正在启动 Muse AI 虚拟试妆系统...
echo 请不要关闭此黑框，浏览器会自动弹出！
streamlit run app.py
pause