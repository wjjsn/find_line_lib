import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from skimage.morphology import skeletonize as skeletonize_库
from src.find_line_lib.skeletonize import skeletonize, skeletonize_库 as skeletonize_自定义


def main():
    print("=" * 60)
    print("测试: 9x9 矩形")

    测试图 = np.zeros((9, 9), dtype=np.uint8)
    测试图[2:7, 2:7] = 255

    print("输入:")
    print(测试图)
    print(f"输入白点: {np.sum(测试图 > 0)}")

    库结果 = skeletonize_库(测试图 // 255)
    库结果 = (库结果 * 255).astype(np.uint8)
    print(f"\nskimage库 skeletonize: 白点={np.sum(库结果 > 0)}")
    print(库结果)

    自定义结果 = skeletonize_自定义(测试图)
    print(f"\n自定义 skeletonize: 白点={np.sum(自定义结果 > 0)}")
    print(自定义结果)

    cv2.imshow("测试图", cv2.resize(测试图, (300, 300)))
    cv2.imshow("库骨架", cv2.resize(库结果, (300, 300)))
    cv2.imshow("自定义骨架", cv2.resize(自定义结果, (300, 300)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    png目录 = "png"
    输出目录 = "skeleton_compare_output"
    import os
    os.makedirs(输出目录, exist_ok=True)

    图片列表 = [f for f in os.listdir(png目录) if f.endswith((".jpg", ".png"))]
    图片列表.sort()

    print(f"\n处理 {len(图片列表)} 张图片...")
    一致数量 = 0
    for i, 图片名 in enumerate(图片列表):
        图片路径 = os.path.join(png目录, 图片名)
        原图 = cv2.imread(图片路径)
        if 原图 is None:
            continue

        调整后 = cv2.resize(原图, (160, 120))
        灰度图 = cv2.cvtColor(调整后, cv2.COLOR_BGR2GRAY)
        _, 二值图 = cv2.threshold(灰度图, 127, 255, cv2.THRESH_BINARY)

        库骨架 = skeletonize_库(二值图 // 255)
        库骨架 = (库骨架 * 255).astype(np.uint8)
        自定义骨架 = skeletonize_自定义(二值图)

        一致 = np.array_equal(库骨架, 自定义骨架)
        if 一致:
            一致数量 += 1
        print(f"[{i+1}/{len(图片列表)}] {图片名}: {'一致' if 一致 else '不一致'} | 库:{np.sum(库骨架>0)} 自定义:{np.sum(自定义骨架>0)}")

        basename = os.path.basename(图片名)
        name, ext = os.path.splitext(basename)
        cv2.imwrite(os.path.join(输出目录, f"{name}_binary{ext}"), 二值图)
        cv2.imwrite(os.path.join(输出目录, f"{name}_lib{ext}"), 库骨架)
        cv2.imwrite(os.path.join(输出目录, f"{name}_custom{ext}"), 自定义骨架)

        # 显示四个窗口
        显示二值 = cv2.resize(二值图, (400, 300))
        显示库骨架 = cv2.resize(库骨架, (400, 300))
        显示自定义 = cv2.resize(自定义骨架, (400, 300))
        差异图 = np.abs(显示库骨架.astype(int) - 显示自定义.astype(int)).astype(np.uint8)
        显示差异 = cv2.resize(差异图, (400, 300))

        cv2.imshow("原图二值", 显示二值)
        cv2.imshow("库骨架", 显示库骨架)
        cv2.imshow("自定义骨架", 显示自定义)
        cv2.imshow("差异图", 显示差异)
        cv2.waitKey(0)

    print(f"\n汇总: {一致数量}/{len(图片列表)} 一致")
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()