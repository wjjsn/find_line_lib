from find_line_lib.ring import 发现圆坏,准备入环,准备出环
from find_line_lib.get_start_point import get_start_point
from find_line_lib.status_switcher import status_switcher
import cv2

if __name__ == '__main__':
    for img in ["png/found_left_ring.jpg","png/found_right_ring.jpg"]:
        rgb_img = cv2.imread(img)
        assert rgb_img is not None
    
        gray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
        res = 发现圆坏(bin_img, 9)
        assert res is not None
    
    result1, result2 = res
        lp, rp = result1
    xlp, xrp = result2
    
        cv2.circle(rgb_img, lp, 3, (0, 0, 255), -1)
        cv2.circle(rgb_img, rp, 3, (255, 0, 0), -1)
    cv2.circle(rgb_img, xlp, 3, (0, 0, 255), -1)2
    cv2.circle(rgb_img, xrp, 3, (255, 0, 0), -1)
    cv2.line(rgb_img, xlp, xrp, (255, 0, 0), 2)
    cv2.line(rgb_img, lp, rp, (0, 0, 255), 2)
        cv2.imshow('rgb_img', rgb_img)
        cv2.waitKey(0)
    
        cv2.destroyAllWindows()
    ######################################################################
    # 测试**准备入环**
    # 
    print("测试**准备入环**")
    for img in ["png/enter_left_ring_0.jpg","png/enter_left_ring_1.jpg",
                "png/enter_right_ring_0.jpg","png/enter_right_ring_1.jpg",
                "png/sz-1.jpg","png/sz-2.jpg"]:
        rgb_img = cv2.imread(img)
        assert rgb_img is not None
    
        gray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
        h, w = bin_img.shape[:2]
        result = get_start_point(bin_img, (h-1, w//2))
        assert result is not None
        ss = status_switcher()

        result = 准备入环(bin_img, ss, result)
        if result is None:
            print(f"准备入环失败: {img}, 跳变阈值过高或中点水平距离差值阈值过高，或可能是十字")
            cv2.imshow('bin_img', bin_img)
            cv2.imshow('rgb_img', rgb_img)
            cv2.waitKey(0)
            continue
    
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
    print("测试**准备出环**")
    for img in ["png/exit_left_ring_1.jpg","png/exit_right_ring_1.jpg",
                "png/sz-1.jpg","png/sz-2.jpg"]:
        rgb_img = cv2.imread(img)
        assert rgb_img is not None
    
        gray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        h, w = bin_img.shape[:2]
        result = get_start_point(bin_img, (h-1, w//2))
        assert result is not None
        ss = status_switcher()
        
        result = 准备出环(bin_img, ss, result, 跳变阈值=37, 中点水平距离相差多少算圆坏=19)
        if result is None:
            print(f"准备出环失败: {img}, 跳变阈值过高或中点水平距离差值阈值过高，或可能是十字")
            cv2.imshow('bin_img', bin_img)
            cv2.imshow('rgb_img', rgb_img)
            cv2.waitKey(0)
            continue
    
        lp, rp = result
    
        cv2.circle(rgb_img, lp, 3, (0, 0, 255), -1)
        cv2.circle(rgb_img, rp, 3, (255, 0, 0), -1)
        cv2.imshow('bin_img', bin_img)
        cv2.imshow('rgb_img', rgb_img)
        cv2.waitKey(0)
        print(result)
    cv2.destroyAllWindows()
    
