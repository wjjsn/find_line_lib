import numpy as np

def get_start_point(bin_img: np.ndarray, start_row: int = 0, BORDER_MIN: int = 0, BORDER_MAX: int = 0) -> tuple[np.ndarray, np.ndarray] | None:
    """
    寻找左右边界的起始点

    Args:
        start_row: 起始行坐标
        bin_img: 二值图像数组

    Returns:
        如果找到左右边界点，返回(left_point, right_point)元组，否则返回None
    """
    h, w = bin_img.shape[:2]
    center_col = w // 2
    if start_row == 0:
        start_row = h-1
    if BORDER_MIN == 0:
        BORDER_MIN = 1
    if BORDER_MAX == 0:
        BORDER_MAX = w-2

    # 找左边界
    left_point = None
    for col in range(center_col, BORDER_MIN, -1):
        if bin_img[start_row, col] == 255 and bin_img[start_row, col - 1] == 0:
            left_point = np.array([col, start_row])
            break

    # 找右边界
    right_point = None
    for col in range(center_col, BORDER_MAX):
        if bin_img[start_row, col] == 255 and bin_img[start_row, col + 1] == 0:
            right_point = np.array([col, start_row])
            break

    return (left_point, right_point) if left_point is not None and right_point is not None else None
