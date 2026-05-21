from find_line_lib.get_start_point import get_start_point
import cv2
from cv2.typing import MatLike
from numpy import logical_xor

def 发现圆坏(bin_img: MatLike, spilt: int) -> tuple[tuple[int, int], tuple[int, int]] | None:
    h, w = bin_img.shape[:2]
    spilt_height = h/spilt
    start_row = int(spilt_height*(spilt//2))
    end_row = int(spilt_height*(spilt//2+spilt%2))

    min_width = w
    min_width_point:tuple[tuple[int, int], tuple[int, int]]=(0, 0), (0, 0)
    for row in range(start_row, end_row):
        result = get_start_point(bin_img, start_point=(row, w // 2))
        if result is not None:
            lp,rp = result
            lx,ly = lp
            rx,ry = rp
            if rx - lx < min_width:
                min_width = rx - lx
                min_width_point=result

    if min_width_point == ((0, 0), (0, 0)):
        return None

    return min_width_point


def 准备入环(bin_img: MatLike, 跳变阈值: int=50, 从多高开始往下扫: int=50) -> tuple[tuple[int, int], tuple[int, int]] | None:
    h, w = bin_img.shape[:2]

    线长=[]
    线长对应点索引=[]

    for row in range(从多高开始往下扫, h-1, 4):
        result = get_start_point(bin_img, start_point=(row, w // 2))
        if result is not None:
            lp, rp = result
            线长.append(rp[0] - lp[0])
            线长对应点索引.append(result)

    for i in range(1, len(线长)):
        if 线长[i] - 线长[i-1] > 跳变阈值:
            print(线长[i] - 线长[i-1])
            return 线长对应点索引[i-1]
