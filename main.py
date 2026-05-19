import cv2
import numpy as np
import time
import math
# ========== 宏定义 ==========
IMAGE_H = 120  # 图像高度
IMAGE_W = 188  # 图像宽度

WHITE_PIXEL = 255
BLACK_PIXEL = 0

BORDER_MAX = IMAGE_W - 2  # 边界最大值
BORDER_MIN = 1            # 边界最小值

USE_NUM = IMAGE_H * 3     # 找点的数组成员个数

# 形态学滤波阈值
THRESHOLD_MAX = 255 * 5
THRESHOLD_MIN = 255 * 2

# 颜色定义（BGR格式）
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_CYAN = (255, 255, 0)
COLOR_PURPLE = (255, 0, 255)

# ========== 全局变量 ==========
original_image = np.zeros((IMAGE_H, IMAGE_W), dtype=np.uint8)
bin_image = np.zeros((IMAGE_H, IMAGE_W), dtype=np.uint8)
image_threshold = 0

# 边界数组
l_border = np.zeros(IMAGE_H, dtype=np.uint8)
r_border = np.zeros(IMAGE_H, dtype=np.uint8)
center_line = np.zeros(IMAGE_H, dtype=np.uint8)

# 八邻域数据结构
points_l = np.zeros((USE_NUM, 2), dtype=np.uint16)
points_r = np.zeros((USE_NUM, 2), dtype=np.uint16)
dir_l = np.zeros(USE_NUM, dtype=np.uint16)
dir_r = np.zeros(USE_NUM, dtype=np.uint16)
data_stastics_l = 0
data_stastics_r = 0
hightest = 0

# 起点
start_point_l = [0, 0]
start_point_r = [0, 0]


# ========== 工具函数 ==========
def my_abs(value):
    """求绝对值"""
    return abs(value)


def limit_a_b(x, a, b):
    """限幅"""
    if x < a:
        x = a
    if x > b:
        x = b
    return x


# ========== 图像处理函数 ==========
def otsu_threshold(image):
    """
    大津法（OTSU）计算阈值
    使用OpenCV的API代替手动实现
    """
    # 使用OpenCV的大津法
    threshold, _ = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return threshold


def turn_to_bin():
    """图像二值化"""
    global bin_image, image_threshold

    # 使用OpenCV的大津法
    image_threshold = otsu_threshold(original_image)

    # 二值化
    _, bin_image = cv2.threshold(original_image, image_threshold, 255, cv2.THRESH_BINARY)


def image_filter(bin_img):
    """
    形态学滤波（膨胀和腐蚀思想）
    使用OpenCV的形态学操作代替
    """
    kernel = np.ones((3, 3), np.uint8)

    # 先腐蚀后膨胀（开运算）去除噪声
    opened = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel)

    # 再膨胀（闭运算）填充空洞
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

    return closed


def image_draw_rectan(img):
    """给图像画黑框"""
    img[0:2, :] = 0  # 上边两行变黑
    img[:, 0:2] = 0  # 左边两列变黑
    img[:, IMAGE_W-2:IMAGE_W] = 0  # 右边两列变黑
    return img


def get_start_point(start_row, bin_img):
    """寻找左右边界的起始点"""
    global start_point_l, start_point_r

    l_found = 0
    r_found = 0

    start_point_l = [0, 0]
    start_point_r = [0, 0]

    # 从中间往左边找起点
    for i in range(IMAGE_W // 2, BORDER_MIN, -1):
        start_point_l = [i, start_row]
        if bin_img[start_row, i] == 255 and bin_img[start_row, i - 1] == 0:
            l_found = 1
            break

    # 从中间往右边找起点
    for i in range(IMAGE_W // 2, BORDER_MAX):
        start_point_r = [i, start_row]
        if bin_img[start_row, i] == 255 and bin_img[start_row, i + 1] == 0:
            r_found = 1
            break

    return l_found and r_found


def get_left(total_L):
    """从八邻域边界提取左边线"""
    global l_border

    l_border = np.full(IMAGE_H, BORDER_MIN, dtype=np.uint8)
    h = IMAGE_H - 2

    for j in range(total_L):
        if j >= len(points_l):
            break
        if points_l[j, 1] == h:
            l_border[h] = points_l[j, 0] + 1
            h -= 1
            if h == 0:
                break


def get_right(total_R):
    """从八邻域边界提取右边线"""
    global r_border

    r_border = np.full(IMAGE_H, BORDER_MAX, dtype=np.uint8)
    h = IMAGE_H - 2

    for j in range(total_R):
        if j >= len(points_r):
            break
        if points_r[j, 1] == h:
            r_border[h] = points_r[j, 0] - 1
            h -= 1
            if h == 0:
                break


def search_l_r(break_flag, bin_img, l_stastic, r_stastic,
               l_start_x, l_start_y, r_start_x, r_start_y):
    """
    八邻域边界跟踪
    这是核心算法，保持与原C代码相同的逻辑
    """
    global points_l, points_r, dir_l, dir_r, hightest

    # 定义八个邻域（左边：顺时针）
    seeds_l = np.array([
        [0, 1],   # 上
        [-1, 1],  # 左上
        [-1, 0],  # 左
        [-1, -1], # 左下
        [0, -1],  # 下
        [1, -1],  # 右下
        [1, 0],   # 右
        [1, 1]    # 右上
    ], dtype=np.int8)

    # 定义八个邻域（右边：逆时针）
    seeds_r = np.array([
        [0, 1],   # 上
        [1, 1],   # 右上
        [1, 0],   # 右
        [1, -1],  # 右下
        [0, -1],  # 下
        [-1, -1], # 左下
        [-1, 0],  # 左
        [-1, 1]   # 左上
    ], dtype=np.int8)

    # 关键修复：使用传入的初始值，而不是从0开始
    l_data_statics = l_stastic
    r_data_statics = r_stastic

    # 初始化中心点
    center_point_l = np.array([l_start_x, l_start_y], dtype=np.int16)
    center_point_r = np.array([r_start_x, r_start_y], dtype=np.int16)

    # 开启邻域循环
    while break_flag > 0:
        break_flag -= 1

        # ========== 左边处理 ==========
        # 计算8邻域坐标
        search_fields_l = center_point_l + seeds_l

        # 边界检查并记录当前点
        if 0 <= center_point_l[1] < IMAGE_H and 0 <= center_point_l[0] < IMAGE_W:
            points_l[l_data_statics, 0] = center_point_l[0]
            points_l[l_data_statics, 1] = center_point_l[1]
            l_data_statics += 1

            # 防止数组越界
            if l_data_statics >= USE_NUM:
                break

        # 左边判断 - 寻找边界
        index_l = 0
        temp_l = np.zeros((8, 2), dtype=np.int16)

        for i in range(8):
            # 边界检查
            x1 = int(search_fields_l[i, 0])
            y1 = int(search_fields_l[i, 1])
            x2 = int(search_fields_l[(i + 1) & 7, 0])
            y2 = int(search_fields_l[(i + 1) & 7, 1])

            if 0 <= y1 < IMAGE_H and 0 <= x1 < IMAGE_W and \
               0 <= y2 < IMAGE_H and 0 <= x2 < IMAGE_W:

                if bin_img[y1, x1] == 0 and bin_img[y2, x2] == 255:
                    temp_l[index_l, 0] = x1
                    temp_l[index_l, 1] = y1
                    index_l += 1
                    if l_data_statics - 1 < USE_NUM:
                        dir_l[l_data_statics - 1] = i

        # 更新左边中心点
        if index_l > 0:
            # 选择y值最小的点（最靠上的点）
            center_point_l[0] = temp_l[0, 0]
            center_point_l[1] = temp_l[0, 1]
            for j in range(index_l):
                if center_point_l[1] > temp_l[j, 1]:
                    center_point_l[0] = temp_l[j, 0]
                    center_point_l[1] = temp_l[j, 1]

        # ========== 右边处理 ==========
        # 计算8邻域坐标
        search_fields_r = center_point_r + seeds_r

        # 边界检查并记录当前点
        if 0 <= center_point_r[1] < IMAGE_H and 0 <= center_point_r[0] < IMAGE_W:
            points_r[r_data_statics, 0] = center_point_r[0]
            points_r[r_data_statics, 1] = center_point_r[1]
            r_data_statics += 1

            # 防止数组越界
            if r_data_statics >= USE_NUM:
                break

        # 右边判断
        index_r = 0
        temp_r = np.zeros((8, 2), dtype=np.int16)

        for i in range(8):
            x1 = int(search_fields_r[i, 0])
            y1 = int(search_fields_r[i, 1])
            x2 = int(search_fields_r[(i + 1) & 7, 0])
            y2 = int(search_fields_r[(i + 1) & 7, 1])

            if 0 <= y1 < IMAGE_H and 0 <= x1 < IMAGE_W and \
               0 <= y2 < IMAGE_H and 0 <= x2 < IMAGE_W:

                if bin_img[y1, x1] == 0 and bin_img[y2, x2] == 255:
                    temp_r[index_r, 0] = x1
                    temp_r[index_r, 1] = y1
                    index_r += 1
                    if r_data_statics - 1 < USE_NUM:
                        dir_r[r_data_statics - 1] = i

        # 更新右边中心点
        if index_r > 0:
            center_point_r[0] = temp_r[0, 0]
            center_point_r[1] = temp_r[0, 1]
            for j in range(index_r):
                if center_point_r[1] > temp_r[j, 1]:
                    center_point_r[0] = temp_r[j, 0]
                    center_point_r[1] = temp_r[j, 1]

        # ========== 终止条件检查 ==========
        # 1. 检查是否三次进入同一个点（右边）
        if r_data_statics >= 3:
            if (points_r[r_data_statics-1, 0] == points_r[r_data_statics-2, 0] and
                points_r[r_data_statics-1, 0] == points_r[r_data_statics-3, 0] and
                points_r[r_data_statics-1, 1] == points_r[r_data_statics-2, 1] and
                points_r[r_data_statics-1, 1] == points_r[r_data_statics-3, 1]):
                print("检测到右边重复点，退出")
                break

        # 2. 检查是否三次进入同一个点（左边）
        if l_data_statics >= 3:
            if (points_l[l_data_statics-1, 0] == points_l[l_data_statics-2, 0] and
                points_l[l_data_statics-1, 0] == points_l[l_data_statics-3, 0] and
                points_l[l_data_statics-1, 1] == points_l[l_data_statics-2, 1] and
                points_l[l_data_statics-1, 1] == points_l[l_data_statics-3, 1]):
                print("检测到左边重复点，退出")
                break

        # 3. 检查左右相遇
        if l_data_statics > 0 and r_data_statics > 0:
            if (abs(points_r[r_data_statics-1, 0] - points_l[l_data_statics-1, 0]) < 2 and
                abs(points_r[r_data_statics-1, 1] - points_l[l_data_statics-1, 1]) < 2):
                hightest = (points_r[r_data_statics-1, 1] + points_l[l_data_statics-1, 1]) // 2
                print(f"左右相遇退出，最高点: {hightest}")
                break

        # 如果没有找到任何点，退出循环
        if index_l == 0 and index_r == 0:
            print("未找到边界点，退出")
            break

    return l_data_statics, r_data_statics

# ========== 显示函数 ==========
def draw_debug_info(display_img, bin_img):
    """绘制调试信息"""
    global data_stastics_l, data_stastics_r, hightest

    # 绘制边界点
    for i in range(min(data_stastics_l, len(points_l))):
        x, y = points_l[i, 0] + 2, points_l[i, 1]
        if 0 <= x < IMAGE_W and 0 <= y < IMAGE_H:
            cv2.circle(display_img, (x, y), 1, COLOR_BLUE, -1)

    for i in range(min(data_stastics_r, len(points_r))):
        x, y = points_r[i, 0] - 2, points_r[i, 1]
        if 0 <= x < IMAGE_W and 0 <= y < IMAGE_H:
            cv2.circle(display_img, (x, y), 1, COLOR_RED, -1)

    # 绘制边界线和中线
    for i in range(hightest, IMAGE_H - 1):
        center_line[i] = (l_border[i] + r_border[i]) // 2

        # 绘制左边线（绿色）
        if 0 <= l_border[i] < IMAGE_W:
            cv2.circle(display_img, (l_border[i], i), 1, COLOR_GREEN, -1)

        # 绘制右边线（绿色）
        if 0 <= r_border[i] < IMAGE_W:
            cv2.circle(display_img, (r_border[i], i), 1, COLOR_GREEN, -1)

        # 绘制中线（黄色）
        if 0 <= center_line[i] < IMAGE_W:
            cv2.circle(display_img, (center_line[i], i), 1, COLOR_YELLOW, -1)

    # 绘制起点标记
    cv2.circle(display_img, (start_point_l[0] + 2, start_point_l[1]), 3, COLOR_BLUE, -1)
    cv2.circle(display_img, (start_point_r[0] - 2, start_point_r[1]), 3, COLOR_RED, -1)

    return display_img


# ========== 主处理函数 ==========
def image_process(frame):
    """
    最终处理函数
    """
    global original_image, data_stastics_l, data_stastics_r, hightest
    global points_l, points_r, dir_l, dir_r  # 添加这些全局变量

    # 1. 获取图像（转为灰度图）
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    original_image = cv2.resize(gray, (IMAGE_W, IMAGE_H))

    # 2. 二值化
    turn_to_bin()

    # 3. 形态学滤波
    bin_img_filtered = image_filter(bin_image)

    # 4. 画黑框预处理
    bin_img_filtered = image_draw_rectan(bin_img_filtered)

    # 5. 重要：每帧都重置全局数组
    points_l = np.zeros((USE_NUM, 2), dtype=np.uint16)
    points_r = np.zeros((USE_NUM, 2), dtype=np.uint16)
    dir_l = np.zeros(USE_NUM, dtype=np.uint16)
    dir_r = np.zeros(USE_NUM, dtype=np.uint16)

    # 6. 寻找起点并执行八邻域跟踪
    if get_start_point(IMAGE_H - 2, bin_img_filtered):
        # print("正在开始八邻域...")
        data_stastics_l, data_stastics_r = search_l_r(
            USE_NUM, bin_img_filtered, 0, 0,  # 从0开始
            start_point_l[0], start_point_l[1],
            start_point_r[0], start_point_r[1]
        )
        print(f"八邻域已结束 - 左点: {data_stastics_l}, 右点: {data_stastics_r}", end="\r")

        # 提取边线
        get_left(data_stastics_l)
        get_right(data_stastics_r)
    else:
        print("未找到起点")
        data_stastics_l = 0
        data_stastics_r = 0

    # 7. 创建显示图像
    display_img = cv2.cvtColor(bin_img_filtered, cv2.COLOR_GRAY2BGR)

    # 8. 绘制调试信息（只有找到点时才绘制）
    if data_stastics_l > 0 and data_stastics_r > 0:
        display_img = draw_debug_info(display_img, bin_img_filtered)

    return display_img

def calculate_deviation_fit(center_line, image_w, image_h):
    """
    使用最小二乘法拟合车道中线，计算车头位置的偏差
    更稳定，能预测弯道趋势
    """
    # 收集有效点
    rows = []
    points = []

    # 使用图像下半部分（最相关的部分）
    start_row = image_h // 2
    end_row = image_h - 1

    for row in range(start_row, end_row):
        x = center_line[row]
        if x > 0:  # 有效检测
            rows.append(row)
            points.append(x)

    if len(points) < 2:
        return 0  # 点太少，无法拟合

    # 最小二乘法拟合直线 y = kx + b
    # 注意：这里 y 是行号，x 是列号
    A = np.vstack([rows, np.ones(len(rows))]).T
    k, b = np.linalg.lstsq(A, points, rcond=None)[0]

    # 计算车头位置（底部）的中线x坐标
    bottom_row = image_h - 1
    bottom_center = k * bottom_row + b

    # 计算偏差
    image_center = image_w // 2
    deviation = bottom_center - image_center

    return deviation

# ========== 摄像头循环 ==========
def main():
    """主函数 - 从摄像头获取图像并处理"""

    # 打开摄像头（0表示默认摄像头）
    cap = cv2.VideoCapture("WIN_20260420_11_36_26_Pro.mp4")
    # cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    # 设置摄像头分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fps = 0
    frame_count = 0
    start_time = time.time()

    print("按 'q' 退出")
    print("按 's' 保存当前图像")
    print("按 'r' 重置参数")

    while True:
        # 读取一帧图像
        ret, frame = cap.read()
        if not ret:
            print("无法获取图像")
            break

        # 图像处理
        processed_img = image_process(frame)

        # 显示阈值信息
        # cv2.putText(processed_img, f"Threshold: {image_threshold}", (10, 60),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_CYAN, 1)

        # 显示结果
        deviation = calculate_deviation_fit(center_line, IMAGE_W, IMAGE_H)

        print(f"{"左转" if deviation < 0 else "右转"}: {math.fabs(deviation)}")
        cv2.imshow("image", processed_img)

        # 按键处理
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # 保存图像
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"capture_{timestamp}.png", processed_img)
            print(f"图像已保存: capture_{timestamp}.png")
        elif key == ord('r'):
            # 重置参数（可选）
            print("参数已重置")

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()


# ========== 离线测试函数 ==========
def test_with_image(image_path):
    """使用单张图片进行测试"""
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图像: {image_path}")
        return

    processed = image_process(img)

    cv2.imshow("Original", img)
    cv2.imshow("Processed", processed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # 可以选择运行模式
    # test_with_image("test_image.jpg")  # 测试单张图片
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)  # 创建可调整大小的窗口
    cv2.resizeWindow('image', 1000, 600)
    main()  # 摄像头循环
