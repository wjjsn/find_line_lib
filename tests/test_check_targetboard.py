from find_line_lib.targetboard import 检查目标板,draw_corner_points,根据识别状态补线
from find_line_lib.status_switcher import status_switcher,模型识别状态
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
    result =检查目标板(img, ss)
    assert result is not None
    # tl, tr, br, bl = result
    # draw_corner_points(img, [tl, tr, br, bl])
    # cv2.imshow("result", img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    for status in 模型识别状态:
        ss.模型识别 = status
        show_img=根据识别状态补线(bin_img,ss,result)
        cv2.imshow(f"{status}", show_img)
        cv2.waitKey(0)
    cv2.destroyAllWindows()
