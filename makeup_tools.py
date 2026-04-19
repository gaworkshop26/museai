import cv2
import numpy as np
from PIL import Image
from ultralytics import SAM
import os

class MakeupArtist:
    def __init__(self):
        self.parts = {
            'bg': 0, 'skin': 1, 'l_brow': 2, 'r_brow': 3, 'l_eye': 4, 'r_eye': 5,
            'eye_g': 6, 'l_ear': 7, 'r_ear': 8, 'ear_r': 9, 'nose': 10,
            'mouth': 11, 'u_lip': 12, 'l_lip': 13, 'neck': 14, 'neck_l': 15,
            'cloth': 16, 'hair': 17, 'hat': 18
        }

    def _get_mask(self, parsing, part_names):
        mask = np.zeros_like(parsing)
        for name in part_names:
            part_idx = self.parts[name]
            mask = np.logical_or(mask, parsing == part_idx)
        return mask.astype(np.uint8) * 255
    
    def _get_center(self, parsing, idx_list):
        ys, xs = np.where(np.isin(parsing, idx_list))
        if len(ys) == 0: return None
        return (int(np.mean(xs)), int(np.mean(ys)))

    # --- [关键修改] 坐标定位算法升级 ---
    def apply_decoration(self, image, parsing, decoration_type):
        if decoration_type == '无': return image
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 绘图函数区 (保持不变，花样很丰富了)
            def draw_sakura(img, x, y, size):
                petal_color = (203, 192, 255) 
                center_color = (0, 215, 255) 
                r = int(size / 2.5)
                offsets = [
                    (0, -r), (int(r*0.95), int(-r*0.31)), 
                    (int(r*0.59), int(r*0.81)), (int(-r*0.59), int(r*0.81)), 
                    (int(-r*0.95), int(-r*0.31))
                ]
                for dx, dy in offsets:
                    cv2.circle(img, (x+dx, y+dy), int(r*0.9), petal_color, -1)
                    cv2.circle(img, (x+dx, y+dy), int(r*0.3), (255, 255, 255), -1)
                cv2.circle(img, (x, y), int(r*0.6), center_color, -1)

            def draw_rose(img, x, y, size):
                r = int(size / 2)
                cv2.ellipse(img, (x-r, y+r), (r, r//2), 45, 0, 360, (100, 200, 100), -1)
                cv2.ellipse(img, (x+r, y+r), (r, r//2), -45, 0, 360, (100, 200, 100), -1)
                cv2.circle(img, (x, y), r, (100, 100, 220), -1) 
                cv2.circle(img, (x+int(r*0.2), y-int(r*0.2)), int(r*0.6), (120, 120, 255), -1) 

            def draw_sunflower(img, x, y, size):
                r = int(size / 3)
                petal_color = (0, 215, 255) 
                center_color = (19, 69, 139) 
                for angle in range(0, 360, 45):
                    rad = np.deg2rad(angle)
                    px = int(x + r * 1.5 * np.cos(rad))
                    py = int(y + r * 1.5 * np.sin(rad))
                    cv2.circle(img, (px, py), r, petal_color, -1)
                cv2.circle(img, (x, y), int(r*1.2), center_color, -1)

            def draw_heart(img, x, y, size):
                color = (100, 100, 255) 
                r = size // 2
                cv2.circle(img, (x - r//2, y - r//2), r//2, color, -1)
                cv2.circle(img, (x + r//2, y - r//2), r//2, color, -1)
                triangle_cnt = np.array([
                    (x - size, y - r//4),
                    (x + size, y - r//4),
                    (x, y + size)
                ])
                cv2.fillPoly(img, [triangle_cnt], color)

            def draw_whiskers(img, x, y, size, side='left'):
                color = (255, 255, 255) 
                thickness = max(2, size // 15)
                direction = -1 if side == 'left' else 1
                for dy in [-size//2, 0, size//2]:
                    start_pt = (x + (10 * direction), y + dy//2)
                    end_pt = (x + (size * direction), y + dy)
                    cv2.line(img, start_pt, end_pt, color, thickness)
                cv2.circle(img, (x, y), thickness*2, (150, 150, 255), -1)

            def draw_huadian(img, x, y, size):
                color = (0, 0, 180)
                pts = np.array([
                    [x, y - size], [x + size//2, y],
                    [x, y + size], [x - size//2, y]
                ], np.int32)
                cv2.fillPoly(img, [pts], color)

            # --- [核心逻辑修复] 坐标计算 ---
            # l_eye (Index 4) = 画面右侧的眼睛 (Subject Left)
            # r_eye (Index 5) = 画面左侧的眼睛 (Subject Right)
            l_eye = self._get_center(parsing, [4]) 
            r_eye = self._get_center(parsing, [5]) 
            nose = self._get_center(parsing, [10])

            if not nose: return image

            # 基础贴纸大小
            base_size = 40
            if l_eye and r_eye:
                base_size = int(abs(l_eye[0] - r_eye[0]) * 0.35)

            # 1. 计算左脸颊 (Subject Left, 画面右侧)
            l_cheek_x, l_cheek_y = 0, 0
            if l_eye:
                # X轴：不仅用眼睛坐标，还要往外侧(远离鼻子)扩 15%，防止贴在法令纹上
                l_cheek_x = int(l_eye[0] + (l_eye[0] - nose[0]) * 0.15)
                # Y轴：从中间点改为下沉 70% (接近鼻翼高度)，这才是苹果肌
                l_cheek_y = int(l_eye[1] + (nose[1] - l_eye[1]) * 0.7)

            # 2. 计算右脸颊 (Subject Right, 画面左侧)
            r_cheek_x, r_cheek_y = 0, 0
            if r_eye:
                # X轴：往外侧(远离鼻子)扩 15%
                r_cheek_x = int(r_eye[0] + (r_eye[0] - nose[0]) * 0.15)
                # Y轴：下沉 70%
                r_cheek_y = int(r_eye[1] + (nose[1] - r_eye[1]) * 0.7)
            
            # --- 绘制逻辑 ---
            if '樱花' in decoration_type:
                if '左' in decoration_type and l_eye:
                    draw_sakura(img_cv, l_cheek_x, l_cheek_y, base_size)
                elif '右' in decoration_type and r_eye:
                    draw_sakura(img_cv, r_cheek_x, r_cheek_y, base_size)
            
            elif '玫瑰' in decoration_type:
                if '左' in decoration_type and l_eye:
                    draw_rose(img_cv, l_cheek_x, l_cheek_y, base_size)
                elif '右' in decoration_type and r_eye:
                    draw_rose(img_cv, r_cheek_x, r_cheek_y, base_size)

            elif '向日葵' in decoration_type:
                if l_eye: draw_sunflower(img_cv, l_cheek_x, l_cheek_y + 10, base_size)
                if r_eye: draw_sunflower(img_cv, r_cheek_x, r_cheek_y + 10, base_size)

            elif '猫咪' in decoration_type:
                if l_eye: draw_whiskers(img_cv, nose[0] + 40, nose[1], int(base_size*1.5), 'right')
                if r_eye: draw_whiskers(img_cv, nose[0] - 40, nose[1], int(base_size*1.5), 'left')

            elif '爱心' in decoration_type:
                if l_eye: draw_heart(img_cv, l_cheek_x, l_cheek_y, int(base_size*0.8))

            elif '花钿' in decoration_type:
                l_brow = self._get_center(parsing, [2])
                r_brow = self._get_center(parsing, [3])
                if l_brow and r_brow:
                    cx = int((l_brow[0] + r_brow[0]) / 2)
                    cy = int((l_brow[1] + r_brow[1]) / 2) - 30
                    draw_huadian(img_cv, cx, cy, int(base_size*0.4))

            return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
            
        except Exception as e:
            print(f"Decoration Error: {e}")
            return image

    # --- 其他函数保持不变 ---
    def apply_lipstick(self, image, parsing, color_hex, opacity=0.5):
        if opacity == 0: return image
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            color_hex = color_hex.lstrip('#')
            r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            lip_mask = self._get_mask(parsing, ['u_lip', 'l_lip'])
            if np.sum(lip_mask) == 0: return image
            lip_mask_soft = cv2.GaussianBlur(lip_mask, (7, 7), 0) / 255.0
            color_layer = np.zeros_like(img_cv)
            color_layer[:] = [b, g, r]
            lip_mask_3d = np.expand_dims(lip_mask_soft, axis=2)
            output = img_cv * (1 - lip_mask_3d * opacity) + color_layer * (lip_mask_3d * opacity)
            return Image.fromarray(cv2.cvtColor(output.astype(np.uint8), cv2.COLOR_BGR2RGB))
        except: return image

    def apply_hair_dye(self, image, parsing, color_hex, opacity=0.3):
        if opacity == 0: return image
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            color_hex = color_hex.lstrip('#')
            r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            hair_mask = self._get_mask(parsing, ['hair'])
            if np.sum(hair_mask) == 0: return image
            hair_region = cv2.bitwise_and(img_cv, img_cv, mask=hair_mask)
            colored_hair = np.zeros_like(hair_region)
            colored_hair[:] = [b, g, r]
            hair_blended = cv2.addWeighted(hair_region, 1-opacity, colored_hair, opacity, 0)
            mask_inv = cv2.bitwise_not(hair_mask)
            img_bg = cv2.bitwise_and(img_cv, img_cv, mask=mask_inv)
            final = cv2.add(img_bg, cv2.bitwise_and(hair_blended, hair_blended, mask=hair_mask))
            return Image.fromarray(cv2.cvtColor(final, cv2.COLOR_BGR2RGB))
        except: return image

    def apply_foundation(self, image, parsing, intensity=0.0):
        if intensity == 0: return image
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            skin_mask = self._get_mask(parsing, ['skin', 'nose', 'neck', 'neck_l'])
            if np.sum(skin_mask) == 0: return image
            val = int(intensity * 100)
            blurred = cv2.bilateralFilter(img_cv, d=9, sigmaColor=val, sigmaSpace=75)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            v = cv2.add(v, int(intensity * 40)) 
            brightened = cv2.cvtColor(cv2.merge((h, s, v)), cv2.COLOR_HSV2BGR)
            skin_mask_soft = cv2.GaussianBlur(skin_mask, (25, 25), 0) / 255.0
            skin_mask_3d = np.expand_dims(skin_mask_soft, axis=2)
            output = img_cv * (1 - skin_mask_3d) + brightened * skin_mask_3d
            return Image.fromarray(cv2.cvtColor(output.astype(np.uint8), cv2.COLOR_BGR2RGB))
        except: return image

    def change_background(self, image, parsing, color):
        """
        超级优化版：增加亮度过滤，防止背景色覆盖白色衣服
        """
        img_array = np.array(image)
        # 1. 基础背景掩码 (BiSeNet 识别的背景)
        mask = (parsing == 0).astype(np.uint8) * 255
        
        # 2. ⚡ 核心黑科技：提取原图的高亮区域 (比如白色衣服)
        # 将原图转为灰度，亮度大于 220 的通常是白色衣服或强光，我们要保护它
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        bright_areas = (gray > 220).astype(np.uint8) * 255
        
        # 3. 从背景掩码中扣除高亮区域 (如果这块区域很亮，哪怕模型说是背景，我们也不涂颜色)
        mask = cv2.subtract(mask, bright_areas)
        
        # 4. 羽化边缘，让过渡更自然
        mask_blurred = cv2.GaussianBlur(mask, (11, 11), 0) / 255.0
        mask_blurred = np.expand_dims(mask_blurred, axis=-1)
        
        # 5. 生成新背景并融合
        bg_rgb = np.array(list(int(color[i:i+2], 16) for i in (1, 3, 5)))
        bg_img = np.full(img_array.shape, bg_rgb, dtype=np.uint8)
        
        res = img_array * (1 - mask_blurred) + bg_img * mask_blurred
        return Image.fromarray(res.astype(np.uint8))
    
    def apply_eye_shadow(self, image, parsing, color_hex, opacity=0.3):
        if opacity == 0: return image
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            color_hex = color_hex.lstrip('#')
            r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            eye_mask = self._get_mask(parsing, ['l_eye', 'r_eye'])
            if np.sum(eye_mask) == 0: return image
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            eye_shadow_mask = cv2.dilate(eye_mask, kernel, iterations=2)
            eye_shadow_mask = cv2.subtract(eye_shadow_mask, eye_mask)
            eye_shadow_mask = cv2.GaussianBlur(eye_shadow_mask, (15, 15), 0) / 255.0
            color_layer = np.zeros_like(img_cv)
            color_layer[:] = [b, g, r]
            mask_3d = np.expand_dims(eye_shadow_mask, axis=2)
            output = img_cv * (1 - mask_3d * opacity) + color_layer * (mask_3d * opacity)
            return Image.fromarray(cv2.cvtColor(output.astype(np.uint8), cv2.COLOR_BGR2RGB))
        except: return image

    def apply_blush(self, image, parsing, color_hex, opacity=0.3):
        if opacity == 0: return image
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            color_hex = color_hex.lstrip('#')
            r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            
            l_eye_c = self._get_center(parsing, [4])
            r_eye_c = self._get_center(parsing, [5])
            nose_c = self._get_center(parsing, [10])
            
            if not l_eye_c or not r_eye_c or not nose_c: return image 
            
            # 亚洲妆容：眼下腮红
            l_cheek_x = l_eye_c[0]
            l_cheek_y = int(l_eye_c[1] + (nose_c[1] - l_eye_c[1]) * 0.6)
            r_cheek_x = r_eye_c[0]
            r_cheek_y = int(r_eye_c[1] + (nose_c[1] - r_eye_c[1]) * 0.6)
            
            l_center = (l_cheek_x, l_cheek_y)
            r_center = (r_cheek_x, r_cheek_y)

            mask = np.zeros_like(parsing).astype(np.float32)
            
            eye_dist = abs(l_eye_c[0] - r_eye_c[0])
            axis_x = int(eye_dist * 0.25) 
            axis_y = int(eye_dist * 0.18) 
            
            cv2.ellipse(mask, l_center, (axis_x, axis_y), -10, 0, 360, 1, -1)
            cv2.ellipse(mask, r_center, (axis_x, axis_y), 10, 0, 360, 1, -1)
            
            blur_k = int(axis_x * 2) | 1 
            mask = cv2.GaussianBlur(mask, (blur_k, blur_k), 0)
            
            skin_mask = (parsing == 1).astype(np.float32) 
            mask = mask * skin_mask
            
            if np.max(mask) > 0: mask = mask / np.max(mask)

            color_layer = np.zeros_like(img_cv)
            color_layer[:] = [b, g, r]
            
            mask_3d = np.expand_dims(mask, axis=2)
            output = img_cv * (1 - mask_3d * opacity) + color_layer * (mask_3d * opacity)
            return Image.fromarray(cv2.cvtColor(output.astype(np.uint8), cv2.COLOR_BGR2RGB))
        except: return image

    def apply_eyelashes(self, image, parsing, opacity=0.5):
        if opacity == 0: return image
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            eyes_mask = np.logical_or(parsing == 4, parsing == 5).astype(np.uint8) * 255
            if np.sum(eyes_mask) == 0: return image
            contours, _ = cv2.findContours(eyes_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            eyelash_mask = np.zeros_like(eyes_mask)
            cv2.drawContours(eyelash_mask, contours, -1, 255, thickness=2) 
            eyelash_mask = cv2.GaussianBlur(eyelash_mask, (3, 3), 0) / 255.0
            color_layer = np.zeros_like(img_cv) 
            mask_3d = np.expand_dims(eyelash_mask, axis=2)
            output = img_cv * (1 - mask_3d * opacity) + color_layer * (mask_3d * opacity)
            return Image.fromarray(cv2.cvtColor(output.astype(np.uint8), cv2.COLOR_BGR2RGB))
        except: return image


class SAMProcessor:
    def __init__(self):
        self.model = None
        model_name = 'sam3.pt' 
        try:
            if os.path.exists(model_name):
                print(f"🚀 正在加载本地 {model_name}...")
                self.model = SAM(model_name)
                print("✅ SAM 3 模型就绪")
            else:
                print(f"⚠️ 未找到 {model_name}，尝试自动处理...")
                self.model = SAM(model_name) 
        except Exception as e:
            print(f"❌ 模型加载异常: {e}")

    def apply_bokeh(self, image, parsing, blur_strength=0.5, visualize=False):
        if self.model is None and blur_strength == 0: return image
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            orig_h, orig_w = img_cv.shape[:2]
            
            fallback_mask = (parsing > 0).astype(np.uint8) * 255
            used_sam = False
            person_mask = fallback_mask

            try:
                scale_factor = 640 / max(orig_h, orig_w)
                if scale_factor < 1.0:
                    new_w = int(orig_w * scale_factor)
                    new_h = int(orig_h * scale_factor)
                    img_small = cv2.resize(img_cv, (new_w, new_h))
                else:
                    img_small = img_cv
                    scale_factor = 1.0

                y_indices, x_indices = np.where(parsing > 0)
                if len(y_indices) > 0:
                    center_y = int(np.mean(y_indices) * scale_factor)
                    center_x = int(np.mean(x_indices) * scale_factor)
                    input_point = [[center_x, center_y]]
                    
                    results = self.model(img_small, points=input_point, labels=[1], verbose=False)
                    
                    if results and results[0].masks is not None:
                        sam_mask_small = results[0].masks.data[0].cpu().numpy()
                        if np.sum(sam_mask_small) > 100: 
                            mask_resized = cv2.resize((sam_mask_small * 255).astype(np.uint8), (orig_w, orig_h))
                            person_mask = mask_resized
                            used_sam = True
            except Exception as sam_e:
                print(f"SAM 异常: {sam_e}")

            _, person_mask = cv2.threshold(person_mask, 127, 255, cv2.THRESH_BINARY)
            mask_soft = cv2.GaussianBlur(person_mask, (13, 13), 0)

            if visualize:
                green_layer = np.zeros_like(img_cv)
                green_layer[:] = [0, 255, 0]
                output = img_cv.copy()
                mask_indices = mask_soft > 0
                if np.any(mask_indices):
                    output[mask_indices] = cv2.addWeighted(img_cv[mask_indices], 0.7, green_layer[mask_indices], 0.3, 0)
                return Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))

            if blur_strength == 0: return image
            
            k_size = int(blur_strength * 50) * 2 + 1 
            if k_size < 1: k_size = 1
            blurred_bg = cv2.GaussianBlur(img_cv, (k_size, k_size), 0)
            
            mask_3d = np.expand_dims(mask_soft, axis=2) / 255.0
            output = blurred_bg * (1.0 - mask_3d) + img_cv * mask_3d
            
            return Image.fromarray(cv2.cvtColor(output.astype(np.uint8), cv2.COLOR_BGR2RGB))
            
        except Exception as e:
            print(f"全局处理失败: {e}")
            return image