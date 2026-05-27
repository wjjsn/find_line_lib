from skimage.morphology import skeletonize as skeletonize_skimage
import numpy as np


def skeletonize(二值图):
    """
    Zhang-Suen 骨架化算法

    参数:
        二值图: 二值图像，值为 0 或 255

    返回:
        骨架图: 0 或 255 的二值图
    """
    if 二值图.max() > 127:
        骨架 = (二值图 > 127).astype(np.uint8)
    else:
        骨架 = 二值图.astype(np.uint8)

    骨架 = (骨架 > 0).astype(np.uint8)

    h, w = 骨架.shape

    lut = np.array([0, 0, 0, 1, 0, 0, 1, 3, 0, 0, 3, 1, 1, 0,
                    1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0,
                    3, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    2, 0, 0, 0, 3, 0, 2, 2, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0,
                    0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0,
                    3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 3, 0,
                    2, 0, 0, 0, 3, 1, 0, 0, 1, 3, 0, 0, 0, 0,
                    0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 1, 3, 1, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 1, 3,
                    0, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    2, 3, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
                    0, 0, 3, 3, 0, 1, 0, 0, 0, 0, 2, 2, 0, 0,
                    2, 0, 0, 0], dtype=np.uint8)

    skeleton = np.zeros((h + 2, w + 2), dtype=np.uint8)
    skeleton[1:-1, 1:-1] = 骨架
    cleaned_skeleton = skeleton.copy()

    pixel_removed = True
    while pixel_removed:
        pixel_removed = False
        skeleton[1:-1, 1:-1] = 骨架

        for pass_num in range(2):
            first_pass = (pass_num == 0)
            cleaned_skeleton[:, :] = skeleton[:, :]

            for row in range(1, h + 1):
                for col in range(1, w + 1):
                    if skeleton[row, col] == 0:
                        continue

                    neighbors = (skeleton[row - 1, col - 1] +
                                 2 * skeleton[row - 1, col] +
                                 4 * skeleton[row - 1, col + 1] +
                                 8 * skeleton[row, col + 1] +
                                 16 * skeleton[row + 1, col + 1] +
                                 32 * skeleton[row + 1, col] +
                                 64 * skeleton[row + 1, col - 1] +
                                 128 * skeleton[row, col - 1])

                    lut_val = lut[neighbors]

                    if lut_val == 0:
                        continue
                    elif (lut_val == 3 or
                          (lut_val == 1 and first_pass) or
                          (lut_val == 2 and not first_pass)):
                        cleaned_skeleton[row, col] = 0
                        pixel_removed = True

            skeleton[:, :] = cleaned_skeleton[:, :]

        骨架[:, :] = skeleton[1:-1, 1:-1]

    return skeleton[1:-1, 1:-1] * 255


def skeletonize_库(二值图):
    """使用 skimage 库的骨架化函数"""
    if 二值图.max() > 127:
        灰度 = 二值图
    else:
        灰度 = 二值图
    result = skeletonize_skimage(灰度 // 255)
    return (result * 255).astype(np.uint8)