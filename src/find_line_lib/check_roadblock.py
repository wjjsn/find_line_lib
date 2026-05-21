import cv2
import numpy as np
from cv2.typing import MatLike

def 检查路障(binary_img: MatLike, start_point: tuple[tuple[int, int], tuple[int, int]], 阈值: int) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """
    检查二值图像中的路障：同时考虑路障偏左和偏右的情况，并返回对应的避障引导连线。
    
    参数:
        binary_img: 二值图像 (0表示黑色/道路外/路障, 255表示白色/道路)
        start_point: 起始点坐标 (左起点, 右起点)，坐标格式为 (x, y)，即 (列, 行)
        阈值: 路障黑块边缘与对应边界起点横向距离小于等于该值时，认为“过近”

    返回:
        如果触发左侧路障，返回 (左起点, 黑块右下角点)
        如果触发右侧路障，返回 (右起点, 黑块左下角点)
        否则返回 None
    """
    左起点, 右起点 = start_point
    x_left, y_left = 左起点
    x_right, y_right = 右起点
    
    h, w = binary_img.shape[:2]

    # 1. 图像反转，将黑色路障变成白色连通域进行分析
    inverted_img = cv2.bitwise_not(binary_img)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(inverted_img, connectivity=8)
    
    # 2. 遍历所有连通域，寻找位于道路中间、且最靠近下方的路障黑块
    target_label = -1
    max_bottom_y = -1  # 优先找离车身最近（图像下方，y 最大）的路障
    
    for i in range(1, num_labels):
        bx, by, bw, bh, area = stats[i]
        
        # 过滤噪点
        if area < 4:
            continue
            
        # 过滤掉贴着图像最左和最右两侧的“赛道外全黑背景”
        if bx == 0 or (bx + bw) == w:
            continue
            
        # 路障通常在起点的前方（纵向 y <= 起点 y）
        # 记录最靠下方的有效路障
        bottom_y = by + bh
        if bottom_y <= max(y_left, y_right) and bottom_y > max_bottom_y:
            max_bottom_y = bottom_y
            target_label = i

    # 如果没找到任何道路中间的黑块，直接返回
    if target_label == -1:
        return None

    # 3. 提取目标路障黑块的所有像素坐标
    bx, by, bw, bh, _ = stats[target_label]
    pixel_indices = np.where(labels == target_label)
    y_coords = pixel_indices[0]
    x_coords = pixel_indices[1]

    # --- 情况 A：路障在左边，挨左边界太近 ---
    # 计算路障左边缘到左起点的横向距离
    dist_to_left = bx - x_left
    if 0 <= dist_to_left <= 阈值:
        # 此时左边无法通过，连接【左起点】和黑块的【右下角点】引导往右闪避
        idx_se = np.argmax(x_coords + y_coords)
        max_x_at_max_y, max_y = x_coords[idx_se], y_coords[idx_se]
        
        黑块右下角点 = (int(max_x_at_max_y), int(max_y))
        return (左起点, 黑块右下角点)

    # --- 情况 B：路障在右边，挨右边界太近 ---
    # 计算路障右边缘到右起点的横向距离 (右起点的 x 减去 黑块右边缘的 x)
    bx_right = bx + bw
    dist_to_right = x_right - bx_right
    if 0 <= dist_to_right <= 阈值:
        # 此时右边无法通过，连接【右起点】和黑块的【左下角点】引导往左闪避
        idx_sw = np.argmax(y_coords - x_coords)
        min_x_at_max_y, max_y = x_coords[idx_sw], y_coords[idx_sw]
        
        黑块左下角点 = (int(min_x_at_max_y), int(max_y))
        return (右起点, 黑块左下角点)

    return None