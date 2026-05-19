import cv2
from cv2.typing import MatLike
def 检查路障(binary_img:MatLike, 阈值:int)->MatLike:
    """
    检查二值图像中的路障：将距离过近的两个黑块之间的区域涂黑。

    参数:
        binary_img: 二值图像 (0表示黑色/障碍物, 255表示白色/背景)
        阈值: 两个黑块之间距离小于等于该值时，认为“过近”

    返回:
        处理后的二值图像 (被涂黑的区域变为0)
    """
    # 检查路障
    # 将挨着两个挨着很近的黑块的中间直接涂黑
    if len(binary_img.shape) == 3:
        img = cv2.cvtColor(binary_img, cv2.COLOR_BGR2GRAY)
    else:
        img = binary_img.copy()

    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # 膨胀一下让近的黑块连起来，再腐蚀回去
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (阈值, 阈值))
    dilated = cv2.dilate(255 - img, kernel)  # 膨胀白色区域（原图的黑色）
    closed = cv2.erode(dilated, kernel)      # 腐蚀回去

    return 255 - closed
