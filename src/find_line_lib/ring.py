from find_line_lib.get_start_point import get_start_point
import cv2
from cv2.typing import MatLike
from numpy import logical_xor

def 发现圆坏(bin_img: MatLike, spilt: int=9) -> tuple[tuple[int, int], tuple[int, int]] | None:
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


def 准备入环(bin_img: MatLike, 跳变阈值: int=55, 从多高开始往下扫: int=50, 扫一行跳多少行: int=8, 中点水平距离相差多少算圆坏: int=20) -> tuple[tuple[int, int], tuple[int, int]] | None:
    h, w = bin_img.shape[:2]

    线长=[]
    线长对应点索引=[]

    for row in range(从多高开始往下扫, h-1, 扫一行跳多少行):
        result = get_start_point(bin_img, start_point=(row, w // 2))
        if result is not None:
            lp, rp = result
            线长.append(rp[0] - lp[0])
            线长对应点索引.append(result)

    for i in range(1, len(线长)):
        # 检测线长的跳变
        # TODO：检查两个跳变确定结果
        if 线长[i] - 线长[i-1] > 跳变阈值:
            print(f"线长变化：{线长[i] - 线长[i-1]}")
            突变前中点=((线长对应点索引[i-1][0][0] + 线长对应点索引[i-1][1][0]) // 2),((线长对应点索引[i-1][0][1] + 线长对应点索引[i-1][1][1]) // 2)
            突变后中点=((线长对应点索引[i][0][0] + 线长对应点索引[i][1][0]) // 2),((线长对应点索引[i][0][1] + 线长对应点索引[i][1][1]) // 2)
            print(f"突变前中点: {突变前中点}, 突变后中点: {突变后中点}")

            # 检测突变前后中点的水平距离，过小则可能是十字而不是圆坏
            if abs(突变前中点[0] - 突变后中点[0]) > 中点水平距离相差多少算圆坏:
                return 突变前中点, 突变后中点

def 准备出环(bin_img: MatLike, 跳变阈值: int=40, 从下往上扫到多高停: int=70, 扫一行跳多少行: int=-8, 中点水平距离相差多少算圆坏: int=20) -> tuple[tuple[int, int], tuple[int, int]] | None:
    h, w = bin_img.shape[:2]

    线长=[]
    线长对应点索引=[]
    
    for row in range(h-1, 从下往上扫到多高停, 扫一行跳多少行):
        result = get_start_point(bin_img, start_point=(row, w // 2))
        if result is not None:
            lp, rp = result
            线长.append(rp[0] - lp[0])
            线长对应点索引.append(result)
            
    for i in range(1, len(线长)):
        # 检测线长的跳变
        # TODO：检查两个跳变确定结果
        # 
        print(f"线长变化：{线长[i] - 线长[i-1]}")
        if 线长[i] - 线长[i-1] > 跳变阈值:
            突变前中点=((线长对应点索引[i-1][0][0] + 线长对应点索引[i-1][1][0]) // 2),((线长对应点索引[i-1][0][1] + 线长对应点索引[i-1][1][1]) // 2)
            突变后中点=((线长对应点索引[i][0][0] + 线长对应点索引[i][1][0]) // 2),((线长对应点索引[i][0][1] + 线长对应点索引[i][1][1]) // 2)
            print(f"突变前中点: {突变前中点}, 突变后中点: {突变后中点}")

            # 检测突变前后中点的水平距离，过小则可能是十字而不是圆坏
            if abs(突变前中点[0] - 突变后中点[0]) > 中点水平距离相差多少算圆坏:
                return 突变前中点, 突变后中点