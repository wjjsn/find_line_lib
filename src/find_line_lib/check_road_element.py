from enum import Enum,auto
from find_line_lib.check_roadblock import 检查路障


class 圆坏状态(Enum):
    已发现 = auto()
    准备入环 = auto()
    # 已入环 = auto()
    准备出环 = auto()
    出环中 = auto()
    未发现 = auto()

def 赛道元素处理(img,ss)->img:
    img=检查路障(img,15)
    
    # 每个case都要对图像进行处理，方便后续找边界
    # 并且也更新状态机
    match ss.圆坏:
        case 圆坏状态.未发现:
            bool=发现圆坏(边界,img)
            if bool:
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