"""
优化后的骨架分叉点检测脚本
仅在图像最下方的轮廓（真实路径区域）内提取骨架，并仅在此区域内检测分叉点与端点，彻底隔绝背景干扰。
"""
import cv2
import numpy as np
import os
from skimage.morphology import skeletonize

def 局部找特征点(局部骨架图, 模式="分叉点"):
    """
    只在裁剪出的局部小图上扫描特征点
    模式可选择: "分叉点" (邻居>=3) 或 "端点" (邻居==1)
    """
    点列表 = []
    h, w = 局部骨架图.shape
    
    # 8邻域偏移量
    邻域偏移 = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1),          (0, 1),
                (1, -1),  (1, 0), (1, 1)]
                
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if 局部骨架图[y, x] == 0:
                continue
            
            # 计算8邻域中非零像素的数量
            邻居数 = sum(1 for dy, dx in 邻域偏移 if 局部骨架图[y + dy, x + dx] > 0)
            
            if 模式 == "分叉点" and 邻居数 >= 3:
                点列表.append((x, y))
            elif 模式 == "端点" and 邻居数 == 1:
                点列表.append((x, y))
                
    return 点列表

def 轮廓查找(图片路径):
    """对单张图片进行轮廓查找，只局限在最下方轮廓内部处理"""
    原图 = cv2.imread(图片路径)
    if 原图 is None:
        print(f"无法读取图片: {图片路径}")
        return

    # 1. 基础预处理
    调整后图片 = cv2.resize(原图, (160, 120))
    灰度图 = cv2.cvtColor(调整后图片, cv2.COLOR_BGR2GRAY)
    模糊图 = cv2.GaussianBlur(灰度图, (3, 3), 0)
    _, 二值图 = cv2.threshold(模糊图, 127, 255, cv2.THRESH_BINARY)

    # 把最下面7%区域涂黑
    # h, w = 二值图.shape
    # 涂黑高度 = int(h * 0.07)
    # 二值图[h - 涂黑高度:h, :] = 0

    # 轮廓查找与锁定最下方道路
    轮廓列表, _ = cv2.findContours(二值图, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    最下面轮廓 = None
    最大y值 = -1
    for 轮廓 in 轮廓列表:
        x, y, w, h = cv2.boundingRect(轮廓)
        底部y = y + h
        if 底部y > 最大y值:
            最大y值 = 底部y
            最下面轮廓 = 轮廓

    结果图 = 调整后图片.copy()

    if 最下面轮廓 is not None:
        # 绿色画出我们锁定的“真正道路轮廓”
        cv2.drawContours(结果图, [最下面轮廓], -1, (0, 255, 0), 2)

        # 【核心改动 1】：获取最下面轮廓的外接矩形框（把这条路单独切出来）
        rx, ry, rw, rh = cv2.boundingRect(最下面轮廓)

        # 【核心改动 2】：创建一个只针对这个小矩形框的局部 Mask
        局部二值 = 二值图[ry:ry+rh, rx:rx+rw]
        轮廓mask = np.zeros_like(局部二值)
        
        # 将轮廓坐标平移到局部坐标系中绘制
        平移轮廓 = 最下面轮廓 - [rx, ry]
        cv2.drawContours(轮廓mask, [平移轮廓], -1, 255, -1)

        # 仅抠出这个局部矩形内的马路区域
        局部轮廓区域 = cv2.bitwise_and(局部二值, 局部二值, mask=轮廓mask)

        # 【核心改动 3】：只对这个局部区域进行骨架提取（速度极快）
        局部骨架 = skeletonize(局部轮廓区域 // 255)
        局部骨架 = (局部骨架 * 255).astype(np.uint8)

        # 【核心改动 4】：只在局部骨架中数邻居，杜绝全图背景干扰
        局部分叉点 = 局部找特征点(局部骨架, "分叉点")
        局部端点 = 局部找特征点(局部骨架, "端点")

        # 【核心改动 5】：将局部坐标还原到全图坐标，并画到结果图上
        for (lx, ly) in 局部端点:
            全图x, 全图y = lx + rx, ly + ry
            cv2.circle(结果图, (全图x, 全图y), 3, (255, 0, 0), -1) # 蓝色端点

        for (lx, ly) in 局部分叉点:
            全图x, 全图y = lx + rx, ly + ry
            cv2.circle(结果图, (全图x, 全图y), 5, (0, 0, 255), -1) # 红色分叉点

        # 仅为了显示骨架，在全图上拼一下画面
        全图骨架 = np.zeros_like(二值图)
        全图骨架[ry:ry+rh, rx:rx+rw] = 局部骨架

        print(f"【成功】锁定最下方道路！检测到分叉路口: {len(局部分叉点)} 个, 道路尽头: {len(局部端点)} 个")
    else:
        print("【警告】未找到任何有效道路轮廓")
        全图骨架 = np.zeros_like(二值图)

    # 3. 结果放大展示
    显示原图 = cv2.resize(调整后图片, (400, 300))
    显示骨架 = cv2.resize(全图骨架, (400, 300))
    显示结果图 = cv2.resize(结果图, (400, 300))
    
    cv2.imshow("1. Original", 显示原图)
    cv2.imshow("2. Skeleton (Road Only)", 显示骨架)
    cv2.imshow("3. Result (Target Inside)", 显示结果图)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

def 批量处理():
    png目录 = os.path.join(os.path.dirname(__file__), "png")
    图片列表 = [os.path.join(png目录, f) for f in os.listdir(png目录) if f.endswith((".jpg", ".png"))]
    图片列表.sort()
    
    print(f"开始批量处理，共找到 {len(图片列表)} 张图片...")
    for 图片路径 in 图片列表:
        print(f"\n正在分析: {os.path.basename(图片路径)}")
        轮廓查找(图片路径)

if __name__ == "__main__":
    批量处理()