from turtle import right
import cv2
from cv2.typing import MatLike
import numpy as np
from find_line_lib.status_switcher import status_switcher, 模型识别状态
from find_line_lib.get_start_point import get_start_point


def create_red_mask(
    hsv: np.ndarray,
    lower_red1: np.ndarray=np.array([0, 100, 100]),
    upper_red1: np.ndarray= np.array([15, 255, 255]),
    lower_red2: np.ndarray=np.array([150, 100, 100]),
    upper_red2: np.ndarray=np.array([180, 255, 255]),
) -> np.ndarray:
    """
    根据HSV颜色空间创建红色区域掩码。

    红色在HSV空间中分布在两端(0-15和150-180)，因此需要两个范围。

    参数:
        hsv: HSV颜色空间的图像
        lower_red1: 红色范围1的下限 (H, S, V)
        upper_red1: 红色范围1的上限 (H, S, V)
        lower_red2: 红色范围2的下限 (H, S, V)
        upper_red2: 红色范围2的上限 (H, S, V)

    返回:
        二值掩码图像，红色区域为白色(255)，其他区域为黑色(0)
    """
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    return cv2.bitwise_or(mask1, mask2)


def apply_morphology(mask: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    对掩码图像进行形态学操作，去除噪声和填充空洞。

    操作流程:
        1. MORPH_CLOSE: 先膨胀后腐蚀，填充白色区域内部的小黑洞
        2. MORPH_OPEN: 先腐蚀后膨胀，去除白色区域边缘的细小噪点

    参数:
        mask: 输入的二值掩码图像
        kernel_size: 形态学操作的核大小，默认3x3

    返回:
        处理后的二值掩码图像
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def filter_center_contours(
    contours: List,
    img_width: int,
    center_ratio: float = 0.5,
    min_area: float = 1000,
    min_width: int = 40,
    min_height: int = 20,
) -> List:
    """
    筛选位于图像中心区域的红色轮廓。

    筛选条件:
        - 轮廓中心X坐标位于图像中央的center_ratio范围内
        - 轮廓面积大于min_area
        - 轮廓宽高大于指定的最小值

    参数:
        contours: opencv找到的所有轮廓列表
        img_width: 原始图像宽度，用于计算中心区域范围
        center_ratio: 中心区域占图像宽度的比例，默认0.5表示中心50%区域
        min_area: 轮廓最小面积阈值，默认1000
        min_width: 轮廓最小宽度(像素)，默认40
        min_height: 轮廓最小高度(像素)，默认20

    返回:
        按面积降序排列的筛选后轮廓列表，每个元素为(轮廓, 面积, x, y, 宽, 高)
    """
    center_range = (
        (0.5 - center_ratio / 2) * img_width,
        (0.5 + center_ratio / 2) * img_width,
    )
    filtered = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, cw, ch = cv2.boundingRect(cnt)
        cnt_center_x = x + cw / 2
        if (
            center_range[0] < cnt_center_x < center_range[1]
            and area > min_area
            and cw > min_width
            and ch > min_height
        ):
            filtered.append((cnt, area, x, y, cw, ch))
    return sorted(filtered, key=lambda r: r[1], reverse=True)


def find_corner_points(
    points: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    从轮廓点集中找出四个角点(左上、右上、右下、左下)。

    算法原理:
        - 左上角 (tl): x + y 的值最小
        - 右下角 (br): x + y 的值最大
        - 右上角 (tr): x - y 的值最大
        - 左下角 (bl): x - y 的值最小

    参数:
        points: 轮廓上所有点的坐标数组，形状为(N, 2)或(N, 1, 2)，每行是[x, y]
    """
    # 健壮性处理：OpenCV的findContours返回的形状通常是 (N, 1, 2)，先reshape成 (N, 2)
    pts = points.reshape(-1, 2)
    
    x = pts[:, 0]
    y = pts[:, 1]

    # 1. 左上和右下通过 x + y 判断
    add = x + y
    tl = pts[np.argmin(add)]
    br = pts[np.argmax(add)]

    # 2. 右上和左下通过 x - y 判断
    diff = x - y
    tr = pts[np.argmax(diff)]  # x大y小，即x-y最大
    bl = pts[np.argmin(diff)]  # x小y大，即x-y最小

    return tl, tr, br, bl

def draw_corner_points(
    result: np.ndarray,
    corners: List[np.ndarray],
    color: Tuple[int, int, int] = (0, 255, 0),
    radius: int = 3,
    thickness: int = -1,
) -> None:
    """
    在图像上绘制角点(圆点)。

    参数:
        result: 绘制目标图像
        corners: 角点坐标列表
        color: 圆点颜色，默认绿色(0, 255, 0)
        radius: 圆点半径，默认3
        thickness: 线条粗细，-1表示实心圆，默认实心
    """
    for point in corners:
        px, py = point.ravel()
        cv2.circle(result, (px, py), radius, color, thickness)

def 检查目标板(rgb_img: MatLike,ss) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]|None:
    h, w = rgb_img.shape[:2]
    hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)

    # 下面调用的函数有很多参数可以改，如果默认的参数效果不好，就改参数
    mask = create_red_mask(hsv)
    mask = apply_morphology(mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    center_contours = filter_center_contours(
        contours, w
    )
    if not center_contours:
        return None
    best_cnt = center_contours[0][0]
    points = best_cnt.reshape(-1, 2)
    return find_corner_points(points)

# 改成接收原图，和start_point，返回两个点，不要把线画原图上去，不要在里面再算一遍start_point
def 根据识别状态补线(bin_img: MatLike, ss: status_switcher, targetboard_point: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]) -> MatLike:
    # 1. 严格对应上一个函数的返回顺序：tl, tr, br, bl (左上, 右上, 右下, 左下)
    tl, tr, br, bl = targetboard_point
    bin_img = bin_img.copy()
    
    if ss.模型识别 == 模型识别状态.未发现 or ss.模型识别 == 模型识别状态.直行:
        return bin_img
        
    # 获取补线的起点
    result = get_start_point(bin_img)
    if result is None:
        return bin_img
        
    left_point, right_point = result
    # 安全转换起点的类型为原生 int
    lx, ly = int(left_point[0]), int(left_point[1])
    rx, ry = int(right_point[0]), int(right_point[1])

    # 2. 理顺业务逻辑
    if ss.模型识别 == 模型识别状态.左:
        # 向左转/识别为左，通常是用右边的起点(rx, ry)去连【左下角】(bl)
        # 或者用左边的起点(lx, ly)去连【左下角】(bl)
        br_x, br_y = int(bl.ravel()[0]), int(bl.ravel()[1])
        cv2.line(bin_img, (rx, ry), (br_x, br_y), (0, 255, 0), 2)
        return bin_img
        
    if ss.模型识别 == 模型识别状态.右:
        # 向右转/识别为右，通常是用左边的起点(lx, ly)去连【右下角】(br)
        bl_x, bl_y = int(br.ravel()[0]), int(br.ravel()[1])
        cv2.line(bin_img, (lx, ly), (bl_x, bl_y), (0, 255, 0), 2)
        return bin_img

    return bin_img
