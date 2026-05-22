import numpy as np
from typing import Literal

def get_start_point(
    bin_img: np.ndarray,
    start_point: tuple[int, int],
    left_limit: int | None = None,
    right_limit: int | None = None,
    upper_limit: int | None = None,
    lower_limit: int | None = None,
    direction: Literal["horizontal", "vertical"] = "horizontal"
) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """
    从指定行开始向上逐行扫描，寻找赛道（白色区域）的左右边界起始点。

    Args:
        bin_img: 输入的二值图像（0为黑，255为白）
        start_point: 起始扫描的坐标点 (row, col)，若为None则根据direction默认
            - horizontal模式：默认从图像底部中心 (h-1, w//2) 开始
            - vertical模式：默认从图像底部中心 (h-1, w//2) 开始
        left_limit: 向左扫描的截止列坐标（防止左越界，若为None则默认为1）
        right_limit: 向右扫描的截止列坐标（防止右越界，若为None则默认为宽度-1）
        upper_limit: 向上扫描的截止行坐标（若为None则默认为1）
        lower_limit: 向下扫描的截止行坐标（若为None则默认为高度-1）
        direction: 扫描方向
            - "horizontal"：从起点水平扩展，向左找左边界，向右找右边界
            - "vertical"：从起点垂直扩展，向上找上边界，向下找下边界

    Returns:
        如果在哪一行成功找到了左右边界，返回 (left_point, right_point) 坐标元组；
        如果把所有行都找遍了也没找到，返回 None。
    """
    h, w = bin_img.shape[:2]
    center_col = w // 2

    # 1. 整理出清晰、安全的边界参数
    col_min = 1 if left_limit is None else left_limit
    col_max = (w - 1) if right_limit is None else right_limit
    row_min = 1 if upper_limit is None else upper_limit
    row_max = (h - 1) if lower_limit is None else lower_limit

    if direction == "horizontal":
        # 水平模式：从 start_point 开始水平扫描
        init_row = h - 1 if start_point is None else start_point[0]
        init_col = center_col if start_point is None else start_point[1]

        left_point = None
        right_point = None

        # 3. 在当前行【向左】寻找跳变点
        for col in range(init_col, col_min, -1):
            if bin_img[init_row, col] == 255 and bin_img[init_row, col - 1] == 0:
                left_point = (col, init_row)
                break
        else:
            # 情况B（补丁）：如果循环正常走完没突破，且中心点是白的，说明从中心到左边界全白
            if bin_img[init_row, init_col] == 255:
                left_point = (col_min, init_row)

        # 4. 在当前行【向右】寻找跳变点
        for col in range(init_col, col_max):
            if bin_img[init_row, col] == 255 and bin_img[init_row, col + 1] == 0:
                right_point = (col, init_row)
                break
        else:
            # 情况B（补丁）：如果循环正常走完没突破，且中心点是白的，说明从中心到右边界全白
            if bin_img[init_row, init_col] == 255:
                right_point = (col_max, init_row)

        # 5. 检查当前行是否同时找到了左右边界
        if left_point is not None and right_point is not None:
            return left_point, right_point

    else:
        # 2. 从初始行开始，【垂直】循环遍历每一行
        init_row = h - 1 if start_point is None else start_point[0]
        init_col = center_col if start_point is None else start_point[1]

        upper_point = None
        lower_point = None

        # 向上扫描，找上边界
        for row in range(init_row, row_min - 1, -1):
            if bin_img[row, init_col] == 255 and bin_img[row - 1, init_col] == 0:
                upper_point = (init_col, row)
                break
        else:
            if bin_img[init_row, init_col] == 255:
                upper_point = (init_col, row_min)

        # 向下扫描，找下边界
        for row in range(init_row, row_max):
            if bin_img[row, init_col] == 255 and bin_img[row + 1, init_col] == 0:
                lower_point = (init_col, row)
                break
        else:
            if bin_img[init_row, init_col] == 255:
                lower_point = (init_col, row_max)

        # 检查是否同时找到了上下边界
        if upper_point is not None and lower_point is not None:
            return upper_point, lower_point

    # 6. 如果把所有的行都往上翻遍了依然没凑齐左右边界，说明整张图都找不到合格的起始点
    return None

def get_line_points(p1, p2):
    """
    数据逻辑连线：传入任意两个点 p1(x1, y1) 和 p2(x2, y2)
    利用直线方程，计算并返回这两点之间每一行的完整坐标列表。
    """
    x1, y1 = p1
    x2, y2 = p2
    
    line_data = []
    
    # 确定行（y坐标）的起始和终点
    start_y = min(y1, y2)
    end_y = max(y1, y2)
    
    total_rows = end_y - start_y
    
    for y in range(start_y, end_y + 1):
        if total_rows == 0:
            weight = 0
        else:
            # 计算当前行在纵向跨度上的比例
            weight = (y - start_y) / total_rows
            
        # 根据比例，计算当前行对应的 x 坐标
        current_x = int(x1 + (x2 - x1) * weight)
        
        # 将每一行的逻辑坐标 (x, y) 存入列表
        line_data.append((current_x, y))
        
    return line_data