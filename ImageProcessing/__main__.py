# coding:utf-8
from PIL import Image, ImageFont, ImageDraw
import numpy
import os
import time
import re
import datetime
import serial
import math
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import pygame
from pygame.sprite import Sprite


# 图片压缩批处理 压缩为 80*60
def compressImage(srcPath, dstPath):
    # 如果不存在目的目录则创建一个，保持层级结构
    if not os.path.exists(dstPath):
        os.makedirs(dstPath)
    for filename in os.listdir(srcPath):
        # 拼接完整的文件或文件夹路径
        srcFile = os.path.join(srcPath, filename)
        dstFile = os.path.join(dstPath, filename)

        # 如果是文件就处理
        if os.path.isfile(srcFile):
            # 打开原图片缩小后保存，可以用if srcFile.endswith(".jpg")或者split，splitext等函数等针对特定文件压缩
            sImg = Image.open(srcFile)
            dImg = sImg.resize((80, 60), Image.ANTIALIAS)  # 设置压缩尺寸和选项，注意尺寸要用括号
            dImg = dImg.convert('1')
            dImg.save(dstFile)  # 也可以用srcFile原路径保存,或者更改后缀保存，save这个函数后面可以加压缩编码选项JPEG之类的
        # 如果是文件夹就递归
        if os.path.isdir(srcFile):
            compressImage(srcFile, dstFile)


BLACK = False
WHITE = True
COLOR_JUDGE = True

# 校正数组
# 在一条边界线丢失的情况下进行校正
# 校正数据为直道时左边界离中线距离
# 目前数据源于 网友提供的数据资料
# 在机械结构改变后需重新测量校正
CHECK_SUM = 2626
CHECK_ARRAY = [3, 4, 5, 5, 6, 7, 7, 8, 9, 10, 10, 11, 12, 13, 14, 14, 14, 15, 16, 16, 17, 17, 18, 19, 19, 20, 20, 21,
               22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 29, 29, 30, 30, 31, 31, 32, 33, 33, 34, 34, 35, 35,
               36, 36, 37, 37, 38, 39, 40, 41, 41, 41]


def count(array, num):
    count = 0
    for i in array:
        if (i == num):
            count += 1
    return count


def draw_middle(srcFile, dstFile):
    img = Image.open(srcFile)
    img = img.resize((80, 60))
    CAMERA_W, CAMERA_H = img.size
    Left_Broad = [-1 for m in range(CAMERA_H + 4)]
    Right_Broad = [CAMERA_W for m in range(CAMERA_H + 4)]
    Middle_Line = {}
    Middle_Line["Result"] = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    Middle_Line["UnCheck"] = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    Middle_Line["LoseBroadCheck"] = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    Middle_Line["DeviateCheck"] = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    Middle_Line["Result"] = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    Line_use = 0
    Empty = {"Two": 0, "Left": 0, "Right": 0}

    jumpline = 0

    # 赛道扫描+左右边界提取

    try:
        for i in range(CAMERA_W - 1):
            if img.getpixel((i, CAMERA_H - 1)) != BLACK:
                Left_Broad[CAMERA_H - 1] = i
                break
        if (Left_Broad[CAMERA_H - 1] != -1):
            for i in range(Left_Broad[CAMERA_H - 1], CAMERA_W - 1):
                if img.getpixel((i, CAMERA_H - 1)) == BLACK:
                    Right_Broad[CAMERA_H - 1] = i
                    break
        Middle_Line["DeviateCheck"][CAMERA_H - 1] = int((Left_Broad[CAMERA_H - 1] + Right_Broad[CAMERA_H - 1]) / 2)
        Middle_Line["LoseBroadCheck"][CAMERA_H - 1] = int((Left_Broad[CAMERA_H - 1] + Right_Broad[CAMERA_H - 1]) / 2)
        Middle_Line["Result"][CAMERA_H - 1] = int((Left_Broad[CAMERA_H - 1] + Right_Broad[CAMERA_H - 1]) / 2)
    except:
        pass

    for j in range(CAMERA_H - 2, -1, -1):
        Strat_Index = Middle_Line["LoseBroadCheck"][j + 1]
        if Strat_Index < 0:
            Strat_Index = 0
        if Strat_Index >= CAMERA_W:
            Strat_Index = CAMERA_W - 1

        for i in range(Strat_Index, 0, -1):
            if img.getpixel((i, j)) == BLACK:
                Left_Broad[j] = i
                break
        for i in range(Strat_Index, CAMERA_W - 1, 1):
            if img.getpixel((i, j)) == BLACK:
                Right_Broad[j] = i
                break
        # 用于检测可用赛道的顶部
        if (Right_Broad[j] - Left_Broad[j] <= 1):
            Line_use = j
            break
        Middle_Line["UnCheck"][j] = int(((Left_Broad[j] + Right_Broad[j]) / 2))
        Middle_Line["Result"][j] = int(((Left_Broad[j] + Right_Broad[j]) / 2))
        # 补线
        if Right_Broad[j] == CAMERA_W and Left_Broad[j] == -1:
            Middle_Line["LoseBroadCheck"][j] = 40
            Middle_Line["DeviateCheck"][j] = 40
            Middle_Line["Result"][j] = 40
            Empty["Two"] += 1
        elif Right_Broad[j] == CAMERA_W:  # 右无边
            Middle_Line["LoseBroadCheck"][j] = Left_Broad[j] + CHECK_ARRAY[j] - (Left_Broad[j + 1] - Left_Broad[j])
            Middle_Line["DeviateCheck"][j] = Middle_Line["DeviateCheck"][j + 1] - (Left_Broad[j + 1] - Left_Broad[j])
            Middle_Line["Result"][j] = Middle_Line["DeviateCheck"][j]
            Empty["Right"] += 1
        elif Left_Broad[j] == -1:  # 左无边
            Middle_Line["LoseBroadCheck"][j] = Right_Broad[j] - CHECK_ARRAY[j] - (Left_Broad[j + 1] - Left_Broad[j])
            Middle_Line["DeviateCheck"][j] = Middle_Line["DeviateCheck"][j + 1] - (Right_Broad[j + 1] - Right_Broad[j])
            Middle_Line["Result"][j] = Middle_Line["DeviateCheck"][j]
            Empty["Left"] += 1
        else:
            Middle_Line["LoseBroadCheck"][j] = int(((Left_Broad[j] + Right_Broad[j]) / 2))
            Middle_Line["DeviateCheck"][j] = Middle_Line["LoseBroadCheck"][j]
            Middle_Line["Result"][j] = Middle_Line["DeviateCheck"][j]

    for j in range(CAMERA_H - 1, Line_use + 2, -1):
        if abs(Middle_Line["DeviateCheck"][j] - Middle_Line["DeviateCheck"][j + 1]) > 10 \
                and ((Middle_Line["DeviateCheck"][j] - Middle_Line["DeviateCheck"][j + 1]) * (
                Middle_Line["DeviateCheck"][j + 1] - Middle_Line["DeviateCheck"][CAMERA_H - 1])) < 0:
            jumpline = j
            for m in range(CAMERA_H - 1, j, -1):
                Middle_Line["Result"][m] = Middle_Line["LoseBroadCheck"][m]

    enum_RoadState_TOSTR = {
        -5: "LEFT_BIG_TURN",
        -3: "LEFT_OUTRING", -2: "LEFT_INRING", -1: "LEFT_BEFORERING", \
        0: "NONE", \
        3: "RINGHT_OUTRING", 2: "RIGHT_INRING", 1: "RIGHT_BEFORERING",
        4: "Crossing", 5: "RIGHT_BIG_TURN"}

    enum_RoadState_TOINT = {
        "LEFT_BIG_TURN": -5,
        "LEFT_OUTRING": -3, "LEFT_INRING": -2, "LEFT_BEFORERING": -1, \
        "NONE": 0, \
        "RINGHT_OUTRING": 3, "RIGHT_INRING": 2, "RIGHT_BEFORERING": 1,
        "Crossing": 4,
        "RIGHT_BIG_TURN": 5}
    RoadState = 0

    # 十字路口处理
    if Empty["Two"] > 10 and Line_use < 10:
        RoadState = enum_RoadState_TOINT["Crossing"]
    # 大弯道
    if Left_Broad[Line_use + 1] > CAMERA_W - 20 and Line_use > 10:
        RoadState = enum_RoadState_TOINT["RIGHT_BIG_TURN"]
    if Right_Broad[Line_use + 1] < 20 and Line_use > 10:
        RoadState = enum_RoadState_TOINT["LEFT_BIG_TURN"]
    # 圆环处理
    # 第一步圆环前检测下三角区域 （形如|\）
    if (Empty["Two"] == 0 and Line_use <= 10):
        if (Empty["Left"] > 0 and Empty["Right"] == 0):  # 左有空行->圆环可能在左边
            start_Line = CAMERA_H - 5
            end_Line = CAMERA_H - 5
            for k in range(CAMERA_H - 5, Line_use, -1):  # 实际中 从 45 到 35 行中 寻找缺口
                if Left_Broad[k] == -1 and Left_Broad[k + 1] != -1:  # 获得缺口
                    start_Line = k
                    for j in range(start_Line, start_Line + 5):  # 从缺口向下搜索
                        if img.getpixel((0, j)) == BLACK:
                            end_Line = j
                            break
                    if (Left_Broad[end_Line] >= 3):
                        temp = 1
                        for m in range(start_Line, 0, -1):
                            if (Left_Broad[m] != -1):
                                temp *= ((Left_Broad[m] - Left_Broad[m + 1]) * 2)
                                temp += 1
                                if (temp < 0):
                                    RoadState = enum_RoadState_TOINT["LEFT_BEFORERING"]
                                    break
                    if RoadState == enum_RoadState_TOINT["LEFT_BEFORERING"]:
                        break
        if (Empty["Left"] == 0 and Empty["Right"] > 0):  # 左有空行->圆环可能在左边
            start_Line = CAMERA_H - 5
            end_Line = CAMERA_H - 5
            for k in range(CAMERA_H - 5, Line_use, -1):
                if Right_Broad[k] == CAMERA_W and Right_Broad[k + 1] != CAMERA_W:  # 获得缺口
                    start_Line = k
                    for j in range(start_Line, start_Line + 5):  # 从缺口向下搜索
                        if img.getpixel((0, j)) == BLACK:
                            end_Line = j
                            break
                    if (Right_Broad[end_Line] <= CAMERA_W - 4):
                        temp = 1
                        if (Left_Broad[end_Line] >= 3):
                            for m in range(start_Line, 0, -1):
                                if (Left_Broad[m] != -1):
                                    temp *= ((Left_Broad[m] - Left_Broad[m + 1]) * -2)
                                    temp += 1
                                    if (temp < 0):
                                        RoadState = enum_RoadState_TOINT["RIGHT_BEFORERING"]
                                        break
                    if RoadState == enum_RoadState_TOINT["RIGHT_BEFORERING"]:
                        break
    # 第二步检测上三角区域|/ 图像中基本为|___
    if (Empty["Two"] == 0 and Line_use <= 15):
        if (Empty["Left"] > 0):  # 左有空行->圆环可能在左边
            start_Line = CAMERA_H - 5
            end_Line = CAMERA_H - 5
            for i in range(Line_use + 3, CAMERA_H):
                if Left_Broad[i] == -1 and Left_Broad[i - 1] != -1:  # 获得空行处
                    start_Line = i
                    if Left_Broad[start_Line - 1] > 5:
                        RoadState = enum_RoadState_TOINT["LEFT_INRING"]
                        start_Line = start_Line - 3
                        i = Left_Broad[start_Line]
                        j = start_Line
                        while (i > 0 and i < CAMERA_W and j > 0 and j < CAMERA_H):
                            img.putpixel((i, j), BLACK)
                            i += 1
                            j -= 1

        if (Empty["Right"] > 0):  # 左有空行->圆环可能在左边
            start_Line = CAMERA_H - 5
            end_Line = CAMERA_H - 5
            for i in range(Line_use + 3, CAMERA_H):
                if Right_Broad[i] == CAMERA_W and Right_Broad[i - 1] != CAMERA_W:  # 获得缺口
                    start_Line = i
                    if Right_Broad[start_Line - 1] < CAMERA_W - 5:
                        RoadState = enum_RoadState_TOINT["RIGHT_INRING"]

                        start_Line = start_Line - 3
                        i = Right_Broad[start_Line]
                        j = start_Line
                        while (i > 0 and i < CAMERA_W and j > 0 and j < CAMERA_H):
                            img.putpixel((i, j), BLACK)
                            i -= 1
                            j += 1
                        break

    # 第三步圆环图像上黑下白
    if Empty["Two"] > 20 and 10 < Line_use <= Line_use + 5:
        if (RoadState > enum_RoadState_TOINT["NONE"]):
            RoadState = enum_RoadState_TOINT["RINGHT_OUTRING"]
        else:
            RoadState = enum_RoadState_TOINT["LEFT_OUTRING"]

    # 图像绘制
    dimg = img.convert('RGB')  # bmp转jpg
    for j in range(CAMERA_H):
        if (0 <= Middle_Line["DeviateCheck"][j] < CAMERA_W):
            dimg.putpixel((Middle_Line["DeviateCheck"][j], j), (128, 128, 255))
        if (0 <= Middle_Line["LoseBroadCheck"][j] < CAMERA_W):
            dimg.putpixel((Middle_Line["LoseBroadCheck"][j], j), (255, 0, 0))
        if (0 <= Middle_Line["Result"][j] < CAMERA_W):
            dimg.putpixel((Middle_Line["Result"][j], j), (0, 255, 0))
        if (Left_Broad[j] != -1):
            dimg.putpixel((Left_Broad[j], j), (0, 128, 128))
        if (Right_Broad[j] != CAMERA_W):
            dimg.putpixel((Right_Broad[j], j), (200, 0, 200))

    for i in range(CAMERA_W):
        dimg.putpixel((i, jumpline), (128, 255, 200))

    dimg = dimg.resize((800, 600))

    Drawer = ImageDraw.Draw(dimg)
    Drawer.text((0, 0), "LineUse:" + str(Line_use), fill=(255, 0, 0))
    Drawer.text((0, 10), "RoadKind:" + str(enum_RoadState_TOSTR[RoadState]), fill=(255, 0, 0))

    dstFile = dstFile.replace(".BMP", " " + str(enum_RoadState_TOSTR[RoadState]) + ".BMP")
    print(dstFile + " Has Complied")
    dimg.save(dstFile)

    screen.blit(pygame.image.load(dstFile), (0, 0, 800, 600))
    pygame.display.flip()
    pygame.display.set_caption(dstFile)
    time.sleep(0.05)


def To_all(func, srcPath='img', dstPath=r"D:\des"):
    q = {}
    # 如果不存在目的目录则创建一个，保持层级结构
    if not os.path.exists(dstPath):
        os.makedirs(dstPath)
    for filename in os.listdir(srcPath):
        # 拼接完整的文件或文件夹路径
        srcFile = os.path.join(srcPath, filename)
        # dstFile = dstPath
        dstFile = os.path.join(dstPath, filename.replace(".bmp", ".jpg"))

        # 如果是文件就处理
        if os.path.isfile(srcFile):
            # 打开原图片缩小后保存，可以用if srcFile.endswith(".jpg")或者split，splitext等函数等针对特定文件压缩
            q[int(re.sub("\D", "", srcFile))] = (srcFile, dstFile)
            # func(srcFile,dstFile)

        # 如果是文件夹就递归
        if os.path.isdir(srcFile):
            compressImage(srcFile, dstFile)

    for i in sorted(q.keys()):
        func(q[i][0], q[i][1])


def getCheckArray():
    img = Image.open(r"D:\ZD.BMP")

    CAMERA_W, CAMERA_H = img.size
    Left_Broad = [-1 for m in range(CAMERA_H + 4)]
    Right_Broad = [CAMERA_W for m in range(CAMERA_H + 4)]
    Middle_Line = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]

    Middle_Line[CAMERA_H] = int(CAMERA_W / 2) - 1

    try:
        for j in range(CAMERA_H - 1, 0, -1):
            Strat_Index = 40
            for i in range(Strat_Index, 0, -1):
                if img.getpixel((i, j)) == BLACK:
                    Left_Broad[j] = i
                    break

            for i in range(Strat_Index, CAMERA_W - 1, 1):
                if img.getpixel((i, j)) == BLACK:
                    Right_Broad[j] = i
                    break
            Middle_Line[j] = int((Left_Broad[j] + Right_Broad[j]) / 2)
    except:
        print("error")

    pre_CHECK_ARRAY = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    for i in range(len(pre_CHECK_ARRAY)):
        pre_CHECK_ARRAY[i] = Middle_Line[i] - Left_Broad[i]
    print(pre_CHECK_ARRAY)
    return pre_CHECK_ARRAY


def get_average_part_slpoe(srcFile, dstFile):
    img = Image.open(srcFile)
    CAMERA_W, CAMERA_H = img.size
    Left_Broad = [0 for m in range(CAMERA_H + 4)]
    Right_Broad = [CAMERA_W - 1 for m in range(CAMERA_H + 4)]
    UnChecked_Middle_Line = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    Middle_Line = {}
    Middle_Line["Result"] = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    Middle_Line["UnCheck"] = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    Middle_Line["LoseBroadCheck"] = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]
    Middle_Line["DeviateCheck"] = [int(CAMERA_W / 2) for m in range(CAMERA_H + 4)]

    Line_use = 60
    Empty = {"Two": 0, "Left": 0, "Right": 0}
    for j in range(CAMERA_H - 2, 0, -1):
        # 校正数组目前还有较大问题 校正与非校正不连续 或需手动输入？？？
        # 校正后的图像可能右越界可能 但保留数据
        # 防校正后的中线坐标越界
        Strat_Index = Middle_Line["LoseBroadCheck"][j + 1]
        if Strat_Index < 0:
            Strat_Index = 0
        if Strat_Index >= CAMERA_W:
            Strat_Index = CAMERA_W - 1

        for i in range(Strat_Index, 0, -1):
            if img.getpixel((i, j)) == BLACK:
                Left_Broad[j] = i
                break
        for i in range(Strat_Index, CAMERA_W - 1, 1):
            if img.getpixel((i, j)) == BLACK:
                Right_Broad[j] = i
                break
        # 用于检测可用赛道的顶部
        if (Left_Broad[j] >= Right_Broad[j]):
            Line_use = 60 - j
            break
        Middle_Line["UnCheck"][j] = int(((Left_Broad[j] + Right_Broad[j]) / 2))

        if Right_Broad[j] == CAMERA_W - 1 and Left_Broad[j] == 0:
            Middle_Line["LoseBroadCheck"][j] = 40
            Middle_Line["DeviateCheck"][j] = 40
            Middle_Line["DeviateCheck"][j] = 40
            Empty["Two"] += 1
        elif Right_Broad[j] == CAMERA_W - 1:  # 右无边
            Middle_Line["LoseBroadCheck"][j] = Left_Broad[j] + CHECK_ARRAY[j]
            Middle_Line["DeviateCheck"][j] = Middle_Line["DeviateCheck"][j + 1] - (Left_Broad[j + 1] - Left_Broad[j])
            Empty["Right"] += 1
        elif Left_Broad[j] == 0:  # 左无边
            Middle_Line["LoseBroadCheck"][j] = Right_Broad[j] - CHECK_ARRAY[j]
            Middle_Line["DeviateCheck"][j] = Middle_Line["DeviateCheck"][j + 1] - (Right_Broad[j + 1] - Right_Broad[j])
            Empty["Left"] += 1
        else:
            Middle_Line["LoseBroadCheck"][j] = int(((Left_Broad[j] + Right_Broad[j]) / 2))
            Middle_Line["DeviateCheck"][j] = Middle_Line["LoseBroadCheck"][j]

    Weight = [0, 0.5, 0.3, 0.2]
    average_part_slope = [0 for i in range(4)]
    for i in range(3, 18):
        average_part_slope[0] += (Middle_Line["DeviateCheck"][i] - 40) / 15
    average_part_slope[0] = average_part_slope[0]
    for i in range(18, 33):
        average_part_slope[1] += (Middle_Line["DeviateCheck"][i] - 40) / 15
    average_part_slope[1] = average_part_slope[1]
    for i in range(33, 48):
        average_part_slope[2] += (Middle_Line["DeviateCheck"][i] - 40) / 15
    average_part_slope[2] = average_part_slope[2]
    for i in range(48, 57):
        average_part_slope[3] += (Middle_Line["DeviateCheck"][i] - 40) / 9
    average_part_slope[3] = average_part_slope[3]

    with open(dstFile, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([srcFile.split('\\')[-1]] + average_part_slope)


def reSize(srcFile, dstFile):
    img = Image.open(srcFile)
    dimg = img.convert('RGB')  # bmp转jpg
    dstFile = dstFile.replace(".BMP", ".JPG")
    dimg = dimg.resize((800, 600))
    dimg.save(dstFile)


'''
#伪逆透视变换 已弃用
def ImgTranform(srcFile, dstFile):
    img = Image.open(srcFile)
    CAMERA_W, CAMERA_H = img.size
    img = img.convert('1')

    for j in range(CAMERA_H):
        for i in range(CAMERA_W-1,-1,-1):
            value = img.getpixel((i,j))
            TR_X =int((i-40)*Tr[j]+40)
            if (-20<=TR_X<CAMERA_W+20):
                img.putpixel((TR_X+20, j+20), value)
    img = img.resize((800,600))
    img.save(dstFile)
'''


def ShowImg(srcFile, dstFile=""):
    img = Image.open(srcFile)
    plt.imshow(img)
    plt.show()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    To_all(draw_middle, "D:\\SBYH", "D:\\SBYH_DEAL\\")
    To_all(draw_middle, "D:\\TEST", "D:\\TEST_DEAL\\")
    # draw_middle("D:\\SBYH\\SBYH_377.BMP","D:\\SB.BMP")