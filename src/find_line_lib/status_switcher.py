from enum import Enum,auto

class 圆坏(Enum):
    class 状态(Enum):
        已发现 = auto()
        准备入环 = auto()
        准备出环 = auto()
        即将出环 = auto()
        出环中 = auto()
        未发现 = auto()
    class 类型(Enum):
        无 = auto()
        左 = auto()
        右 = auto()

class 模型识别状态(Enum):
    未发现 = auto()
    左 = auto()
    直行 = auto()
    右 = auto()

class 目标板状态(Enum):
    未发现 = auto()
    已发现 = auto()
    通过中 = auto()


class status_switcher():
    def __init__(self):
        self.圆坏状态:圆坏.状态=圆坏.状态.未发现
        self.圆坏类型:圆坏.类型=圆坏.类型.无
        self.模型识别:模型识别状态=模型识别状态.未发现
        self.目标板:目标板状态=目标板状态.未发现
