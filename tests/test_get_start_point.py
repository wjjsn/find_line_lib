import cv2
from find_line_lib.get_start_point import get_start_point

if __name__ == "__main__":
    img = cv2.imread("png/roadblock_left.jpg")
    img = cv2.resize(img, (640, 480))
    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # 1. 修改了函数名
        h, w = bin_img.shape[:2]

        get_start_point_result = get_start_point(bin_img, (h // 5, w // 2)
            ,direction="horizontal"
        )

        if get_start_point_result is not None:
            start_point_l, start_point_r = get_start_point_result

            # 2. 因为返回的是 int 元组，直接把 start_point_l 和 start_point_r 传给元组参数即可，更干净
            cv2.circle(img, start_point_l, 3, (0, 0, 255), -1)
            cv2.circle(img, start_point_r, 3, (255, 0, 0), -1)

            cv2.imshow("img", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Failed to get start point")
    else:
        print("Failed to load image")
