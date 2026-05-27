from enum import Enum,auto
from find_line_lib.check_roadblock import 检查路障
from find_line_lib.targetboard import 检查目标板
from cv2.typing import MatLike
from find_line_lib.status_switcher import status_switcher,圆坏状态,目标板状态
from find_line_lib.ring import 发现圆坏


def 赛道元素处理(img: MatLike,ss: status_switcher)->MatLike:
    # img=检查路障(img)
    # img=检查目标板(img,ss)
    # match ss.目标板:
    #     case 目标板状态.未发现:
    #         #尝试发现目标板
    #         pass
    #     case 目标板状态.已发现
    #         #根据识别状态补线()
    #         pass
    #     case 目标板状态.通过中:
    #         #继续补线，直到红色区域消失,状态变为未发现
    #         pass
    
    # 每个case都要对图像进行处理，方便后续找边界
    # 并且也更新状态机
    match ss.圆坏:
        case 圆坏状态.未发现:
            result=发现圆坏(边界,img)
            if result:
                ss.圆坏=圆坏状态.已发现
                
                # 把圆到靠近车这条线补了
        case 圆坏状态.已发现:
            # 看能不能继续发现，如果能继续发现，状态仍为已发现
            # 若不能继续发现，说明状态变成准备入环
        case 圆坏状态.准备入环:
            # 看能不能继续保持入环，如果不能，说明说明已入环
        case 圆坏状态.准备出环:
            # 检查是否满足出环条件，满足则出环
            # 刚出来的时候把一边涂黑，无法继续保持当前状态时切换下一个状态
        case 圆坏状态.出环中:
            # 把另一边涂黑
            # 完全出了标记ss.圆坏=圆坏状态.未发现
        case _:
            pass
    return img