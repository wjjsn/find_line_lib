import numpy as np
import math
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

def tget_midpoint_np(point1, point2):
    # 使用 // 2 进行整除，直接得到整数类型的 NumPy 数组
    mid = (np.array(point1) + np.array(point2)) // 2
    # 转换为元组返回，方便后续解包
    return (int(mid[0]), int(mid[1]))


def 检查边界连续性(
    points: list[tuple[int, int]], 
    max_jump: int = 15
) -> tuple[bool, list[int]]:
    """
    检查单边边界线（左边界或右边界）在纵向上的连续性。

    Args:
        points: 边界点列表，格式必须统一为 [(x1, y1), (x2, y2), ...]
                要求按照 Y 轴（行）的顺序依次排列（从下到上或从上到下均可）
        max_jump: 相邻两行之间允许的最大横向（X轴）跳变像素值。超过此值认为是不连续。

    Returns:
        is_continuous: bool, 整体是否连续
        break_indices: list[int], 发生断裂（不连续）的位置索引列表
    """
    if len(points) < 2:
        return True, []

    break_indices = []
    is_continuous = True

    # 遍历所有相邻的点，比对它们的 X 坐标
    for i in range(len(points) - 1):
        curr_x, curr_y = points[i]
        next_x, next_y = points[i + 1]

        # 确保它们确实是相邻行（防止中间漏检），允许 Y 轴方向有方向性步长
        if abs(next_y - curr_y) > 5: 
            # 如果行距隔得太远，横向阈值需要等比例放大，或者这里做特殊处理
            pass

        # 计算横向 X 轴的跳变距离
        x_distance = abs(next_x - curr_x)

        # 如果跳变超过了设定的最大阈值，判定为不连续
        if x_distance > max_jump:
            is_continuous = False
            break_indices.append(i + 1)  # 记录发生断裂的点索引

    return is_continuous, break_indices

def 检查左右两边连续性(
    left_line: list[tuple[int, int]], 
    right_line: list[tuple[int, int]], 
    max_jump: int = 15
) -> dict[str, Any]:
    """
    同时检查左右两条边界线的连续性状态
    """
    # 检查左边
    left_ok, left_breaks = 检查边界连续性(left_line, max_jump)
    # 检查右边
    right_ok, right_breaks = 检查边界连续性(right_line, max_jump)
    
    # 综合评估赛道状态
    track_valid = left_ok and right_ok
    
    return {
        "track_valid": track_valid,       # 赛道两边是否都完美连续
        "left_continuous": left_ok,       # 左边是否连续
        "right_continuous": right_ok,     # 右边是否连续
        "left_break_at": left_breaks,     # 左边断裂处的点索引（方便做丢线保护）
        "right_break_at": right_breaks    # 右边断裂处的点索引
    }

def get_distance(p1: tuple[int, int], p2: tuple[int, int]) -> float:
    """
    计算两点之间的距离
    Args:
        p1: 第一个点 (x1, y1)
        p2: 第二个点 (x2, y2)
    Returns:
        float: 两点之间的浮点数距离
    """
    x1, y1 = p1
    x2, y2 = p2
    
    # 欧几里得距离公式
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)