import cv2
import numpy as np


def face_skin_blend(image, blur_strength=100, blend_strength=1.0):
    """
    人脸磨皮 Blend 效果 + 皮肤检测（只磨皮肤，不磨五官）
    :param image: 输入BGR图像
    :param blur_strength: 双边滤波程度 (越大磨皮越重)
    :param blend_strength: 融合系数 (0-1)
    :return: 磨皮后的图像
    """

    # ===================== 【新增】真正的皮肤检测（肤色分割）=====================
    def get_skin_mask(img):
        # 转换到 YCrCb 颜色空间（肤色检测最常用空间）
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        # 提取 Cr、Cb 通道（肤色在这两个通道有固定范围）
        cr = ycrcb[:, :, 1]
        cb = ycrcb[:, :, 2]

        # 标准肤色阈值（专门针对亚洲人肤色优化）
        skin_mask = ((cr >= 133) & (cr <= 173) & (cb >= 77) & (cb <= 127))
        skin_mask = skin_mask.astype(np.float32)

        # 高斯模糊让皮肤边缘更柔和，不生硬
        skin_mask = cv2.GaussianBlur(skin_mask, (7, 7), 0)
        return skin_mask

    # 获取皮肤掩码（只有皮肤区域=1，其他=0）
    skin_mask = get_skin_mask(image)
    skin_mask_3ch = np.stack([skin_mask] * 3, axis=-1)  # 转为3通道
    # ==========================================================================

    # 1. 高频滤波（祛痘）
    img_float = image.astype(np.float32)
    gaussian = cv2.GaussianBlur(img_float, (0, 0), 25)
    high_pass = img_float - gaussian
    remove_acne = img_float - high_pass * 0.85

    # 2. 生成高光滑图
    smooth = cv2.bilateralFilter(image, blur_strength, 75, 75)

    # 3. 生成过渡掩码（原来的逻辑保留）
    gray_original = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_smooth = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    mask = np.abs(gray_original.astype(np.float32) - gray_smooth)
    mask = (mask - mask.min()) / (mask.max() - mask.min() + 1e-5)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    mask_3ch = np.stack([mask] * 3, axis=-1)

    # 只有皮肤区域才应用磨皮，非皮肤区域完全保留原图！
    result = (
            image * (1 - blend_strength * (1 - mask_3ch) * skin_mask_3ch) +
            smooth * (blend_strength * (1 - mask_3ch) * skin_mask_3ch)
    ).astype(np.uint8)
    # ==========================================================================

    return result


# 读取图片
img = cv2.imread("E:/skin_dataset/face.jpg")
# 应用效果
output = face_skin_blend(img, blur_strength=20, blend_strength=0.75)
# 保存结果
cv2.imwrite("blended_skin_face1.jpg", output)