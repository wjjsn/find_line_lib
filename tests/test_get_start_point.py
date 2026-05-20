import cv2
from find_line_lib.get_start_point import get_start_point

def image_draw_rectan(img):
    """给图像画黑框"""
    h, w = img.shape[:2]
    img[0:2, :] = 0  # 上边两行变黑
    img[:, 0:2] = 0  # 左边两列变黑
    img[:, w-2:w] = 0  # 右边两列变黑
    return img

if __name__ == "__main__":
    img = cv2.imread("png/targetboard.png")
    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        # bin_img = image_draw_rectan(bin_img)
        get_start_point_result = get_start_point(bin_img)
        if get_start_point_result is not None:
            start_point_l, start_point_r = get_start_point_result
            cv2.circle(img, (start_point_l[0], start_point_l[1]), 3, (0, 0, 255), -1)
            cv2.circle(img, (start_point_r[0], start_point_r[1]), 3, (255, 0, 0), -1)
            cv2.imshow("img", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Failed to get start point")

    else:
        print("Failed to load image")
