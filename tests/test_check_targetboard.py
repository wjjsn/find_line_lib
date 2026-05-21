from find_line_lib.targetboard import 检查目标板,draw_corner_points,根据识别状态补线
from find_line_lib.status_switcher import status_switcher,模型识别状态
from find_line_lib.get_start_point import get_start_point
import cv2
from typing import List, Tuple
import numpy as np

# def test_检查目标板():
#     img = cv2.imread("png/targetboard.png")
#     ss = status_switcher()
#     ss.
#     检查目标板(img, ss)


if __name__ == "__main__":
    img = cv2.imread("png/targetboard.png")
    ss = status_switcher()
    ss.模型识别 = 模型识别状态.左
    assert img is not None

    result = 检查目标板(img, ss)
    assert result is not None

    # 生成二值化图提供给 get_start_point 提取起点
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # 按照新逻辑：在外部只计算一次 start_point
    h, w = bin_img.shape[:2]
    start_point_result = get_start_point(bin_img, (h-1,w//2))

    for status in 模型识别状态:
        ss.模型识别 = status

        # 复制一份原图用于当前的测试可视化，不污染原图
        show_img = img.copy()

        # 调用新函数获取线段端点
        line_pts = 根据识别状态补线(ss, start_point_result, result)

        # 如果返回了具体的点，在测试画布上画出来
        if line_pts is not None:
            p1, p2 = line_pts
            cv2.line(show_img, p1, p2, (0, 255, 0), 2)
            print(f"状态【{status}】: 成功获取补线点 {p1} -> {p2}")
        else:
            print(f"状态【{status}】: 无需补线")

        cv2.imshow(f"{status}", show_img)
        cv2.waitKey(0)

    cv2.destroyAllWindows()
