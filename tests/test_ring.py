from find_line_lib.ring import 发现圆坏,准备入环,准备出环
import cv2

if __name__ == '__main__':
    rgb_img = cv2.imread('png/found_roundabout.jpg')
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
    ######################################################################
    # 测试**准备入环**
    # 
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
    
