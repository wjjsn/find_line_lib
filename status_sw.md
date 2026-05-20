```python
import numpy as np
from enum import Enum,auto

class 圆坏状态(Enum):
    已发现 = auto()
    准备入环 = auto()
    # 已入环 = auto()
    准备出环 = auto()
    出环中 = auto()
    未发现 = auto()

class 模型识别状态(Enum):
    未发现 = auto()
    左 = auto()
    直行 = auto()
    右 = auto()

class status_switcher():
    def __init__(self):
        self.圆坏=圆坏状态.未发现
        self.模型识别=模型识别状态.未发现

def calculateWheelSpeeds(line: np.ndarray) -> tuple[int, int]:
    
    # 用最小二乘法得到线的斜率
    # 根据线的斜率来计算速度增益，用lambda，用非线性。增益大小与base_speed相关

    # 加上base_speed，返回
    return leftSpeed, rightSpeed

def 检查路障(img,用于判断两个黑块多近算近的阈值)->img:
    # 检查路障
    # 将挨着两个挨着很近的黑块的中间直接涂黑
    return img

def 读取模型识别状态(ss):
    test=1
    match test:
        case 1:
            ss.模型识别=模型识别状态.未发现
        case 2:
            ss.模型识别=模型识别状态.左
        case 3:
            ss.模型识别=模型识别状态.直行
        case 4:
            ss.模型识别=模型识别状态.右

def 检查目标板(img,ss)->img:
    #检查一遍目标板
    if 检查成功:
        读取模型识别状态(ss)
        match ss.模型识别:
            case 模型识别状态.未发现:
                # 降低base_speed，等待识别
            case 模型识别状态.左:
                #把左边的线补了
            case 模型识别状态.直行:
                pass
            case 模型识别状态.右:
                #把右边的线补了
    return img

def 赛道元素处理(img,ss)->img:
    img=检查路障(img)
    img=检查目标板(img,ss)
    # 每个case都要对图像进行处理，方便后续找边界
    # 并且也更新状态机
    match ss.圆坏:
        case 圆坏状态.未发现:
            bool,img=发现圆坏(边界,img)
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
    
def 找直行路(img,ss)->np.ndarray（[n][2]n个点）:
    #拿到补好线图片跑一遍八邻域，找到边界线，算中线，返回结果
    

def main()
    ss=status_switcher()
    最终用线=None
    while True:
        rgb_img=opencv读取()
        img=赛道元素处理(rgb_img,ss)
        最终用线:np.ndarray（[n][2]n个点）=找直行路(img,ss)
        
        left_speed, right_speed = calculateWheelSpeeds(最终用线)
        print(打印速度)
    
if __name__ == "__main__":
    main()
    
```
