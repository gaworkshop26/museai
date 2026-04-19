# processor.py
# 这是我们封装的 AI 处理核心，负责把图片喂给模型，并拿到结果
import torch
import torchvision.transforms as transforms
import cv2
import numpy as np
from PIL import Image
from core.model import BiSeNet # 引用核心网络结构

class FaceParser:
    def __init__(self, model_path='weights/79999_iter.pth'):
        self.n_classes = 19
        self.net = BiSeNet(n_classes=self.n_classes)
        self.net.cpu() # 先加载到CPU，如果环境没装CUDA也不会崩
        
        # 加载预训练权重
        try:
            self.net.load_state_dict(torch.load(model_path, map_location='cpu'))
            self.net.eval()
            print(f"✅ 模型加载成功: {model_path}")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            raise e

        # 定义图片预处理（这是BiSeNet模型的硬性要求）
        self.to_tensor = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ])

    def parse(self, image_pil):
        """
        输入: PIL格式的图片
        输出: 语义分割 Mask (Numpy数组)
        """
        # 1. 记录原图尺寸
        w, h = image_pil.size
        
        # 2. 缩放到 512x512 (模型只能处理这个大小)
        img_resized = image_pil.resize((512, 512), Image.BILINEAR)
        
        # 3. 转换格式
        img_tensor = self.to_tensor(img_resized)
        img_tensor = torch.unsqueeze(img_tensor, 0) # 增加一个维度

        # 4. 推理
        with torch.no_grad():
            out = self.net(img_tensor)[0]
            # 获取每个像素概率最大的类别
            parsing = out.squeeze(0).cpu().numpy().argmax(0)
            
        # 5. 把 Mask 放大回原图尺寸
        # 注意使用最近邻插值(INTER_NEAREST)，保证Mask边缘是整数，不会变模糊
        parsing_result = cv2.resize(parsing.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST)
        
        return parsing_result