from find_line_lib.get_start_point import get_start_point,tget_midpoint_np,get_distance
from find_line_lib.status_switcher import status_switcher,圆坏
import cv2
from cv2.typing import MatLike
from numpy import logical_xor

def 发现圆坏(bin_img: MatLike, spilt: int) ->tuple[ tuple[tuple[int, int], tuple[int, int]],tuple[tuple[int, int], tuple[int, int]]]| None:
    h, w = bin_img.shape[:2]
    spilt_height = h/spilt
    start_row = int(spilt_height*(spilt//2))
    end_row = int(spilt_height*(spilt//2+spilt%2))

    s_min_width = w
    s_min_width_point:tuple[tuple[int, int], tuple[int, int]]=(0, 0), (0, 0)
    for row in range(start_row, end_row):
        result = get_start_point(bin_img, start_point=(row, w // 2))
        if result is not None:
            slp,srp = result
            slx,sly = slp
            srx,sry = srp
            if srx - slx < s_min_width:
                s_min_width = srx - slx
                s_min_width_point=result

    if s_min_width_point == ((0, 0), (0, 0)):
        return None
    group1 = s_min_width_point

    start_row = int(spilt_height * (spilt - 1))
    end_row = h  
    
    min_width = w
    min_width_point:tuple[tuple[int, int], tuple[int, int]]=(0, 0), (0, 0)
    for row in range(start_row, end_row):
        result = get_start_point(bin_img, start_point=(row, w // 2))
        if result is not None:
            xlp,xrp = result
            xlx,xly = xlp
            xrx,xry = xrp 
            if xrx - xlx < min_width:
                min_width = xrx - xlx
                zx = (xlx+xrx)//2
                zy = (xly+xry)//2
                zhongdian = zy, zx
                res = get_start_point(
                    bin_img=bin_img,
                    start_point=zhongdian,
                    left_limit=5,
                    right_limit=w-5,
                    direction="horizontal"
                )
                if res is None:
                    min_width_point = None  
                    zlx=0
                    zrx=zx
                    if zrx - zlx > min_width//3:
                        min_width_point=result
                else:
                    zl, zr = res
                    zlx, zly = zl
                    zrx, zry = zr
                    if zrx - zlx > min_width//3:
                        min_width_point=result

    if min_width_point == ((0, 0), (0, 0)):
        return None
    group2 = min_width_point

    if group1 == ((0, 0), (0, 0)) or group2 == ((0, 0), (0, 0)) or group2 is None:
        return None

    # 2. 从真正找到的 group1 中解包出上方的左、右点，计算上方中点 szd
    g1_left, g1_right = group1
    szd = tget_midpoint_np(g1_left, g1_right)

    # 3. 从真正找到的 group2 中解包出下方的左、右点，计算下方中点 xzd
    g2_left, g2_right = group2
    xzd = tget_midpoint_np(g2_left, g2_right)
    #(x,y)
    zd = tget_midpoint_np(xzd, szd)
    #(y,x)
    start_param = (zd[1], zd[0])
    jieguo = get_start_point(bin_img, start_point=start_param)
    if jieguo is None: return None
    jg_left,jg_right = jieguo
    
    left_length = get_distance(zd, jg_left)
    right_length = get_distance(zd, jg_right)
    base_length = get_distance(xzd, g2_left)

    ratio = 1.2

    # 逻辑核心：先用最严格的条件筛选十字，再分流左右环岛
    if left_length > base_length*ratio and right_length > base_length*ratio:
        # 左右两边都变得很宽，说明是十字路口
        print("检测到十字路口")
    elif left_length > base_length*ratio and left_length > right_length*ratio:
        # 只有左边单侧暴增
        print("检测到左环岛")
    elif right_length > base_length and right_length > left_length:
        # 只有右边单侧暴增
        print("检测到右环岛")
    else:
        print("常规赛道区域")

    return jieguo,group2



def 准备入环(bin_img: MatLike, status_switcher: status_switcher, start_point: tuple[tuple[int, int], tuple[int, int]], 跳变阈值: int=55, 从多高开始往下扫: int=50, 扫一行跳多少行: int=8, 中点水平距离相差多少算圆坏: int=20) -> tuple[tuple[int, int], tuple[int, int]] | None:
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
            if 突变前中点[0] - 突变后中点[0] > 中点水平距离相差多少算圆坏:
                if status_switcher.圆坏类型 == 圆坏.类型.左:
                    # 突变前左点，起始点右点
                    return 线长对应点索引[i-1][0], start_point[1]
                else:
                    print(f"实际检测到的圆坏类型是左，不是{status_switcher.圆坏类型}")
                    return 线长对应点索引[i-1][0], start_point[1]
            elif 突变前中点[0] - 突变后中点[0] < -中点水平距离相差多少算圆坏:
                if status_switcher.圆坏类型 == 圆坏.类型.右:
                    # 突变前右点，起始点左点
                    return 线长对应点索引[i-1][1], start_point[0]
                else:
                    print(f"实际检测到的圆坏类型是右，不是{status_switcher.圆坏类型}")
                    return 线长对应点索引[i-1][1], start_point[0]
            else:
                print("突变过小，可能是十字")
                return None

def 准备出环(bin_img: MatLike, status_switcher: status_switcher, start_point: tuple[tuple[int, int], tuple[int, int]], 跳变阈值: int=40, 从下往上扫到多高停: int=70, 扫一行跳多少行: int=-8, 中点水平距离相差多少算圆坏: int=20) -> tuple[tuple[int, int], tuple[int, int]] | None:
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
            if 突变前中点[0] - 突变后中点[0] > 中点水平距离相差多少算圆坏:
                if status_switcher.圆坏类型 == 圆坏.类型.左:
                    # 突变后右点，起始点左点
                    return 线长对应点索引[i][1], start_point[0]
                else:
                    print(f"实际检测到的圆坏类型是右，不是{status_switcher.圆坏类型}")
                    return 线长对应点索引[i][1], start_point[0]
            elif 突变前中点[0] - 突变后中点[0] < -中点水平距离相差多少算圆坏:
                if status_switcher.圆坏类型 == 圆坏.类型.右:
                    # 突变后左点，起始点右点
                    return 线长对应点索引[i][0], start_point[1]
                else:
                    print(f"实际检测到的圆坏类型是左，不是{status_switcher.圆坏类型}")
                    return 线长对应点索引[i][0], start_point[1]
            else:
                print("突变过小，可能是十字")
                return None
