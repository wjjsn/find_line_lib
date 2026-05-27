from find_line_lib.status_switcher import status_switcher, 圆坏
from find_line_lib.ring import 发现圆坏,准备入环,准备出环
from find_line_lib.get_start_point import get_start_point

import cv2


if __name__ == "__main__":
    ss=status_switcher()

    cap = cv2.VideoCapture("png/left_ring.mp4")
    ss.圆坏状态=圆坏.状态.准备出环
    if cap.isOpened():
        frame_count = 0
        圆坏准备出环计数=0
        cv2.namedWindow('color_img', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('color_img', 400, 300)
        cv2.namedWindow('bin_img', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('bin_img', 400, 300)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count < 3000:
                continue

            img = cv2.resize(frame, (160, 120))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            h, w = bin_img.shape[:2]
            match ss.圆坏状态:
                case 圆坏.状态.未发现:
                    # result=发现圆坏(边界,img)
                    # if result:
                    #     ss.圆坏=圆坏状态.已发现
                    pass

                        # 把圆到靠近车这条线补了
                case 圆坏.状态.已发现:
                    # 看能不能继续发现，如果能继续发现，状态仍为已发现
                    # 若不能继续发现，说明状态变成准备入环
                    pass
                case 圆坏.状态.准备入环:
                    # 看能不能继续保持入环，如果不能，说明说明已入环
                    #
                    result = get_start_point(bin_img, (w//2, h-1))
                    if result is None:
                        continue
                    # lp, rp = result
                    # cv2.circle(img, lp, 3, (0, 0, 255), -1)
                    # cv2.circle(img, rp, 3, (255, 0, 0), -1)
                    result = 准备入环(bin_img,ss,result,跳变阈值=30,中点水平距离相差多少算圆坏=10)
                    if result is None:
                        ss.圆坏状态 = 圆坏.状态.准备出环

                        print(f"切换状态到：{ss.圆坏状态}")
                    else:
                        lp, rp = result
                        cv2.circle(img, lp, 3, (0, 0, 255), -1)
                        cv2.circle(img, rp, 3, (255, 0, 0), -1)



                case 圆坏.状态.准备出环:
                    # 检查是否满足出环条件，满足则出环
                    # 刚出来的时候把一边涂黑，无法继续保持当前状态时切换下一个状态
                    result = get_start_point(bin_img, (w//2, h-1))
                    if result is None:
                        continue
                    # lp, rp = result
                    # cv2.circle(img, lp, 3, (0, 0, 255), -1)
                    # cv2.circle(img, rp, 3, (255, 0, 0), -1)
                    result = 准备出环(bin_img,ss,result,扫一行跳多少行=-9
                        # 跳变阈值=30,中点水平距离相差多少算圆坏=10
                    )
                    if result is None:
                        圆坏准备出环计数=0
                    else:
                        lp, rp = result
                        cv2.circle(img, lp, 3, (0, 0, 255), -1)
                        cv2.circle(img, rp, 3, (255, 0, 0), -1)
                        
                        圆坏准备出环计数+=1
                        if 圆坏准备出环计数 >= 10:
                            ss.圆坏状态 = 圆坏.状态.出环中
                            print(f"切换状态到：{ss.圆坏状态}")
                    pass
                case 圆坏.状态.出环中:
                    # 把另一边涂黑
                    # 完全出了标记ss.圆坏=圆坏状态.未发现
                    pass
                case _:
                    pass

            cv2.imshow("color_img", img)
            cv2.imshow("bin_img", bin_img)
            cv2.waitKey(1)
        print(f"视频结束，总帧数: {frame_count}")
