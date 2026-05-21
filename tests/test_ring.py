from find_line_lib.ring import 发现圆坏
import cv2

if __name__ == '__main__':
    rgb_img = cv2.imread('png/圆环 (2).jpg')
    assert rgb_img is not None

    gray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    result = 发现圆坏(bin_img,9)
    assert result is not None

    lp, rp = result

    cv2.circle(rgb_img, lp, 3, (0, 0, 255), -1)
    cv2.circle(rgb_img, rp, 3, (255, 0, 0), -1)
    cv2.imshow('rgb_img', rgb_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(result)
