import sys
import os
# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 EleGANt_Lib 的上级目录
base_dir = os.path.abspath(os.path.join(current_dir, ".."))
# 把项目根目录加入模块路径
sys.path.insert(0, base_dir)

# 强制打印路径供调试
print("✅ 已添加项目路径:", base_dir)
print("✅ EleGANt_Lib 存在:", os.path.exists(os.path.join(base_dir, "EleGANt_Lib")))
print("✅ training 存在:", os.path.exists(os.path.join(base_dir, "EleGANt_Lib", "training")))

import torch
from PIL import Image
import numpy as np

# ==========================================
# 1. 路径配置与环境注入
# ==========================================
# 获取当前文件(core/makeup_transfer.py)的上一级目录(项目根目录)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELEGANT_LIB_PATH = os.path.join(PROJECT_ROOT, 'EleGANt_Lib')

# 检查路径是否存在
if not os.path.exists(ELEGANT_LIB_PATH):
    raise FileNotFoundError(f"❌ 严重错误：找不到 {ELEGANT_LIB_PATH}，请确保文件夹名字正确且位置正确！")

# 将 EleGANt_Lib 加入 Python 搜索路径，这样才能 import training 等模块
if ELEGANT_LIB_PATH not in sys.path:
    sys.path.append(ELEGANT_LIB_PATH)

# ==========================================
# 2. 动态导入 EleGANt 模块
# ==========================================
try:
    from training.config import get_config
    from training.inference import Inference
except ImportError as e:
    raise ImportError(f"❌ 导入失败：{e}。\n请检查 EleGANt_Lib 文件夹里是否有 training 文件夹。")

# ==========================================
# 3. 模拟参数类 (Mock Arguments)
# ==========================================
class MockArgs:
    def __init__(self):
        # 自动判断使用 CPU 还是 GPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # 权重文件路径
        self.load_path = os.path.join(ELEGANT_LIB_PATH, 'ckpts', 'latest_net_G.pth')
        
        # 这些是 demo.py 里提到的一些默认参数，防止报错我们补上
        self.save_folder = 'results'
        self.name = 'demo'

# ==========================================
# 4. 全局模型缓存 (避免每次点击都重新加载)
# ==========================================
_inference_engine = None

def get_inference_engine():
    """单例模式加载模型"""
    global _inference_engine
    if _inference_engine is None:
        print("⏳ 正在加载 EleGANt 美妆迁移模型...")
        args = MockArgs()
        
        # 检查权重文件
        if not os.path.exists(args.load_path):
            raise FileNotFoundError(f"❌ 找不到权重文件：{args.load_path}\n请下载 latest_net_G.pth 并放入 EleGANt_Lib/ckpts/ 文件夹。")

        # 加载配置 (尝试不传参调用，如果报错则根据情况调整)
        try:
            config = get_config() 
        except:
            # 如果 get_config 需要参数，这里可能需要传入 args
            # 根据常见的 yacs 写法，有时需要 merge_from_file
            # 这里先盲猜它能直接获取默认配置
            config = get_config() 

        # 实例化推理引擎
        _inference_engine = Inference(config, args, args.load_path)
        print("✅ EleGANt 模型加载完成！")
        
    return _inference_engine

def apply_makeup_transfer(source_img_path, ref_img_path):
    """
    供前端调用的核心函数
    :param source_img_path: 素颜图路径 (str)
    :param ref_img_path: 参考妆容图路径 (str)
    :return: 结果图 (PIL Image)
    """
    engine = get_inference_engine()
    
    # 加载图片
    imgA = Image.open(source_img_path).convert('RGB')
    imgB = Image.open(ref_img_path).convert('RGB')

    # 运行迁移
    # postprocess=True 会自动帮我们把 Tensor 转回图片并处理尺寸
    result = engine.transfer(imgA, imgB, postprocess=True)
    
    if result is None:
        raise ValueError("❌ 模型未能生成结果，可能是未检测到人脸。")
        
    return result
