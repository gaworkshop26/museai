import os
import sys
import torch
from PIL import Image
import numpy as np
import torchvision.transforms as transforms
import warnings

# 忽略不必要的警告
warnings.filterwarnings("ignore")

# =================配置区域=================
# 这里假设你的 EleGANt 源码文件夹叫 EleGANt_Lib
LIB_NAME = "EleGANt_Lib"
# 测试用的图片路径 (脚本会自动创建示例图，你也可以替换成自己的)
SRC_PATH = "../test_source.jpg" 
REF_PATH = "../test_ref.jpg"
SAVE_PATH = "../test_result.jpg"
# =========================================

def run_test():
    # 1. 环境定位与路径Hack
    # -----------------------------------
    current_dir = os.getcwd()
    lib_path = os.path.join(current_dir, LIB_NAME)
    
    if not os.path.exists(lib_path):
        print(f"❌ 错误：找不到 {LIB_NAME} 文件夹！请确认它在项目根目录下。")
        return

    print(f"📂 切换工作目录到: {LIB_NAME} (为了满足内部相对路径依赖)")
    # 临时切换进 EleGANt_Lib 目录，因为它的内部代码大量使用了相对路径加载权重
    os.chdir(lib_path)
    sys.path.append(os.getcwd())

    try:
        # 2. 导入模型核心 (必须在切换目录后导入)
        # -----------------------------------
        from options.test_options import TestOptions
        from models.models import create_model
        
        # 3. 模拟命令行参数 (Mock Options)
        # -----------------------------------
        # 我们这里“伪造”所有的启动参数，就像你在命令行输入 python test.py ... 一样
        opt = TestOptions().parse()
        
        # --- 强制覆盖关键参数 ---
        opt.nThreads = 1   # 单线程
        opt.batchSize = 1  # 单张处理
        opt.serial_batches = True 
        opt.no_flip = True 
        opt.display_id = -1 
        opt.name = 'EleGANt' # ⚠️ 这里对应 ckpts 下的文件夹名
        
        # 检查权重文件是否存在
        # 默认逻辑是去 ckpts/EleGANt/latest_net_G.pth 找
        # 如果你直接放在 ckpts/ 下，这里可能需要调整路径逻辑
        ckpt_file = os.path.join(opt.checkpoints_dir, opt.name, 'latest_net_G.pth')
        if not os.path.exists(ckpt_file):
            print(f"⚠️ 警告：在标准路径没找到权重: {ckpt_file}")
            print("尝试在 ckpts/ 根目录查找...")
            opt.name = '.' # 尝试让它直接在 ckpts 下找
            ckpt_file_alt = os.path.join(opt.checkpoints_dir, 'latest_net_G.pth')
            if os.path.exists(ckpt_file_alt):
                print(f"✅ 在 {ckpt_file_alt} 找到了权重！")
            else:
                print("❌ 严重错误：找不到 latest_net_G.pth 权重文件！")
                print(f"请检查文件是否放在 {lib_path}/ckpts/ 目录下。")
                return

        # 4. 初始化模型
        # -----------------------------------
        print("🚀 正在加载 EleGANt 模型 (这可能需要几秒钟)...")
        model = create_model(opt)
        model.setup(opt)
        if opt.eval:
            model.eval()
        print("✅ 模型加载成功！")

        # 5. 准备图片
        # -----------------------------------
        # 如果没有测试图，生成两张假的
        if not os.path.exists(SRC_PATH):
            print("Creating dummy source image...")
            Image.new('RGB', (512, 512), (200, 200, 200)).save(SRC_PATH)
        if not os.path.exists(REF_PATH):
            print("Creating dummy reference image...")
            Image.new('RGB', (512, 512), (100, 50, 50)).save(REF_PATH)

        # 加载并预处理
        transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])

        src_img = Image.open(SRC_PATH).convert('RGB')
        ref_img = Image.open(REF_PATH).convert('RGB')
        
        # 拼装成模型需要的字典格式
        data = {
            'A': transform(src_img).unsqueeze(0), # Source
            'B': transform(ref_img).unsqueeze(0), # Reference
            'A_paths': SRC_PATH, # 只是为了防报错，路径可以随意
            'B_paths': REF_PATH
        }

        # 6. 执行推理
        # -----------------------------------
        print("🎨 开始生成美妆迁移...")
        model.set_input(data)
        model.test()
        
        # 获取结果
        visuals = model.get_current_visuals()
        # visuals['fake_B'] 通常是迁移结果
        res_tensor = visuals['fake_B'] 
        
        # 7. 保存结果
        # -----------------------------------
        res_np = res_tensor[0].cpu().float().detach().numpy()
        res_np = (np.transpose(res_np, (1, 2, 0)) + 1) / 2.0 * 255.0
        res_img = Image.fromarray(res_np.astype(np.uint8))
        
        res_img.save(SAVE_PATH)
        print(f"🎉 成功！结果已保存至根目录: {os.path.abspath(SAVE_PATH)}")

    except Exception as e:
        print(f"\n❌ 运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 恢复工作目录，好习惯
        os.chdir(current_dir)

if __name__ == "__main__":
    # 模拟 sys.argv 防止 argparse 报错
    sys.argv = [sys.argv[0]]
    run_test()