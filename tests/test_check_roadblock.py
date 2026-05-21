
import cv2 as cv
from find_line_lib.check_roadblock import 检查路障
from find_line_lib.get_start_point import get_start_point

def test_check_roadblock(image_regression):
    img = cv.imread("png/roadblock.jpg")
    assert img is not None
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, bin_img = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)

    h, w = bin_img.shape[:2]
    start_point_result = get_start_point(bin_img, (h-1,w//2))
    assert get_start_point_result is not None

    # TODO : 阈值改为分辨率自适应
    result = 检查路障(img, get_start_point_result, 900)
    assert result is not None

    p1, p2 = result
    cv.line(img, p1, p2, (0, 0, 255), 2)
      # 将 OpenCV 的 mat 矩阵转为普通的 png 字节流
    _, buffer = cv.imencode(".png", img)
    img_bytes = buffer.tobytes()

    # 扔给 image_regression，它只收一个参数！
    image_regression.check(img_bytes)


if __name__ == "__main__":
    for img_file in ["png/roadblock_left.jpg", "png/roadblock_right.jpg"]:
        img = cv.imread(img_file)
        assert img is not None
        img = cv.resize(img, (640, 480))
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        _, bin_img = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    
        h, w = bin_img.shape[:2]
        get_start_point_result = get_start_point(bin_img, (h-1,w//2))
        assert get_start_point_result is not None
    
        result = 检查路障(bin_img, get_start_point_result, 150)
        assert result is not None
    
        p1, p2 = result
        cv.line(img, p1, p2, (0, 0, 255), 2)
        cv.imshow("result", img)
        cv.waitKey(0)
    cv.destroyAllWindows()