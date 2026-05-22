<<<<<<< HEAD
from find_line_lib.ring import 发现圆坏,准备入环,准备出环
=======
from find_line_lib.ring import 发现圆坏,准备入环
from find_line_lib.get_start_point  import get_line_points
>>>>>>> f0dcbbb (发现圆环)
import cv2

if __name__ == '__main__':
    rgb_img = cv2.imread('png/found_roundabout.jpg')
    assert rgb_img is not None

    gray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    res = 发现圆坏(bin_img, 9)
    assert res is not None

    result1, result2 = res
    lp, rp = result1
    xlp, xrp = result2
    """
    cv2.circle(rgb_img, lp, 3, (0, 0, 255), -1)
    cv2.circle(rgb_img, rp, 3, (255, 0, 0), -1)
    cv2.circle(rgb_img, xlp, 3, (0, 0, 255), -1)
    cv2.circle(rgb_img, xrp, 3, (255, 0, 0), -1)
    cv2.line(rgb_img, xlp, xrp, (255, 0, 0), 2)
    cv2.line(rgb_img, lp, rp, (0, 0, 255), 2)
    cv2.imshow('rgb_img', rgb_img)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
<<<<<<< HEAD
<<<<<<< HEAD
=======
    print("中部边界点对 (result1):", result1)
    print("底部边界点对 (result2):", result2)
    
>>>>>>> f0dcbbb (发现圆环)
    ######################################################################
    # 测试**准备入环**
    for img in ["png/enter_roundabout_0.jpg","png/enter_roundabout_1.jpg"]:
        rgb_img = cv2.imread(img)
        assert rgb_img is not None
    
        gray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
        result = 准备入环(bin_img)
        assert result is not None
    
        lp, rp = result
    
        cv2.circle(rgb_img, lp, 3, (0, 0, 255), -1)
        cv2.circle(rgb_img, rp, 3, (255, 0, 0), -1)
        cv2.imshow('bin_img', bin_img)
        cv2.imshow('rgb_img', rgb_img)
        cv2.waitKey(0)
        print(result)
    cv2.destroyAllWindows()
<<<<<<< HEAD

    ######################################################################
    # 测试**准备出环**
    # 
    for img in ["png/exit_roundabout_1.jpg"]:
        rgb_img = cv2.imread(img)
        assert rgb_img is not None
    
        gray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
        result = 准备出环(bin_img,跳变阈值=39,中点水平距离相差多少算圆坏=19)
        assert result is not None
    
        lp, rp = result
    
        cv2.circle(rgb_img, lp, 3, (0, 0, 255), -1)
        cv2.circle(rgb_img, rp, 3, (255, 0, 0), -1)
        cv2.imshow('bin_img', bin_img)
        cv2.imshow('rgb_img', rgb_img)
        cv2.waitKey(0)
        print(result)
    cv2.destroyAllWindows()
    
=======
    print("中部边界点对 (result1):", result1)
    print("底部边界点对 (result2):", result2)
>>>>>>> a3be03e (找到2判断点)
=======
    """
    left_line_data = get_line_points(lp, xlp)
  # 遍历左侧线数据里的每一个逻辑坐标，在图上点一个像素点
    for (lx, ly) in left_line_data:
        # 用 cv2.circle 画微小的点（半径1），或者直接修改像素
        cv2.circle(rgb_img, (lx, ly), 1, (0, 255, 255), -1) # 黄色点

    # 3. 最后照常展示图像
    cv2.imshow("Show Interpolated Lines", rgb_img)
    cv2.waitKey(0)
>>>>>>> f0dcbbb (发现圆环)
