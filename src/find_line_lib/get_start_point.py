import numpy as np

def get_start_point(
    bin_img: np.ndarray,
    start_row: int | None = None,
    left_limit: int | None = None,
    right_limit: int | None = None
) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """
    从指定行开始向上逐行扫描，寻找赛道（白色区域）的左右边界起始点。

    Args:
        bin_img: 输入的二值图像（0为黑，255为白）
        start_row: 起始扫描的行坐标（若为None，默认从图像最底部一行开始）
        left_limit: 向左扫描的截止列坐标（防止左越界，若为None则默认为1）
        right_limit: 向右扫描的截止列坐标（防止右越界，若为None则默认为宽度-1）

    Returns:
        如果在哪一行成功找到了左右边界，返回 (left_point, right_point) 坐标元组；
        如果把所有行都找遍了也没找到，返回 None。
    """
    h, w = bin_img.shape[:2]
    center_col = w // 2

    # 1. 整理出清晰、安全的边界参数
    init_row = (h - 1) if start_row is None else start_row
    col_min = 1 if left_limit is None else left_limit
    col_max = (w - 1) if right_limit is None else right_limit

    # 2. 从初始行开始，【垂直向上】循环遍历每一行（行坐标减小代表往上走）
    # range(init_row, -1, -1) 表示从初始行一直往上扫描到第0行
    for current_row in range(init_row, -1, -1):

        left_point = None
        right_point = None

        # 3. 在当前行【向左】寻找跳变点
        for col in range(center_col, col_min, -1):
            if bin_img[current_row, col] == 255 and bin_img[current_row, col - 1] == 0:
                left_point = (col, current_row)
                break
        else:
            # 情况B（补丁）：如果循环正常走完没突破，且中心点是白的，说明从中心到左边界全白
            if bin_img[current_row, center_col] == 255:
                left_point = (col_min, current_row) 

        # 4. 在当前行【向右】寻找跳变点
        for col in range(center_col, col_max):
            if bin_img[current_row, col] == 255 and bin_img[current_row, col + 1] == 0:
                right_point = (col, current_row)
                break
        else:
            # 情况B（补丁）：如果循环正常走完没突破，且中心点是白的，说明从中心到右边界全白
            if bin_img[current_row, center_col] == 255:
                right_point = (col_max, current_row)

        # 5. 检查当前行是否同时找到了左右边界
        if left_point is not None and right_point is not None:
            # 找到了就立刻返回，不再继续往上找了
            return left_point, right_point

    # 6. 如果把所有的行都往上翻遍了依然没凑齐左右边界，说明整张图都找不到合格的起始点
    return None
