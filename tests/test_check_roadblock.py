
import cv2 as cv
from find_line_lib.check_roadblock import 检查路障

def test_check_roadblock(image_regression):
    img = cv.imread("png/roadblock.jpg")
    assert img is not None
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, img = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    
    result = 检查路障(img, 110)
    
      # 将 OpenCV 的 mat 矩阵转为普通的 png 字节流
    _, buffer = cv.imencode(".png", result)
    img_bytes = buffer.tobytes()

    # 扔给 image_regression，它只收一个参数！
    image_regression.check(img_bytes)
