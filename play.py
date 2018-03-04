import os
import cv2
import numpy as np
import time
import random

#利用adb达成按键功能
def get_screenshot(id):
    os.system('adb shell screencap -p /sdcard/%s.png' % str(id))
    os.system('adb pull /sdcard/%s.png .' % str(id))

#条约功能，flag指示是按照distance跳跃还是原地跳跃
def jump(distance,flag):

    press_time = int(distance * 1.35)

    # 生成随机触摸点
    rand = random.randint(0, 9) * 10

    #distance跳跃
    if flag==0:
        cmd = ('adb shell input swipe %i %i %i %i ' + str(press_time)) \
          % (320 + rand, 410 + rand, 320 + rand, 410 + rand)
        os.system(cmd)
    #原地跳跃，目的是避开检测使得成绩有效
    else:
        cmd = ('adb shell input swipe %i %i %i %i 1'  )  % (320 + rand, 410 + rand, 320 + rand, 410 + rand)
        os.system(cmd)

   # print(cmd)


def get_center(img_canny, ):

    # 边缘检测寻找正方体的上沿和下沿

    y_top = np.nonzero([max(row) for row in img_canny[400:]])[0][0] + 400
    x_top = int(np.mean(np.nonzero(canny_img[y_top])))

    y_bottom = y_top + 50
    for row in range(y_bottom, H):
        if canny_img[row, x_top] != 0:
            y_bottom = row
            break

    x_center, y_center = x_top, (y_top + y_bottom) // 2

    # num = 0
    # maxnum = 0
    # for col in range(y_top, W-1):
    #     for raw in range(x_top-1, 1, -1):
    #         if img_canny[raw][col] == 0:
    #             num += 1
    #         else:
    #             print('col:'+str(col)+'   max:'+str(maxnum)+'   num:'+str(num))
    #             if num > maxnum:
    #                 maxnum = num
    #                 x_center = x_top
    #                 y_center = col
    #             else:
    #                 num=0
    #                 break
    return img_canny, x_center, y_center


jump(530,0)
time.sleep(1)
# 匹配棋子模板
chess = cv2.imread('chess.jpg', 0)
# 匹配“再来一局”模板
lose = cv2.imread('lose.jpg', 0)
# 匹配中心圆点模板
center = cv2.imread('center.jpg', 0)

w1, h1 = chess.shape[::-1]
w2, h2 = center.shape[::-1]

for i in range(10000):

    get_screenshot(0)
    jump(1, 1)
    img_rgb = cv2.imread('%s.png' % 0, 0)

    # 如果匹配到"再玩一局"模板，则循环中止
    res_end = cv2.matchTemplate(img_rgb, lose, cv2.TM_CCOEFF_NORMED)
    if cv2.minMaxLoc(res_end)[1] > 0.95:
        break

    # 匹配棋子模板
    res1 = cv2.matchTemplate(img_rgb, chess, cv2.TM_CCOEFF_NORMED)
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
    center1_loc = (max_loc1[0] + 39, max_loc1[1] + 189)

    # 匹配中心原点模板，
    res2 = cv2.matchTemplate(img_rgb, center, cv2.TM_CCOEFF_NORMED)
    min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(res2)
    #匹配成功
    if max_val2 > 0.95:
        print('found white circle!')
        x_center, y_center = max_loc2[0] + w2 // 2, max_loc2[1] + h2 // 2
    #匹配失败，采用边缘检测获取物体的上下边沿
    else:

        img_rgb = cv2.GaussianBlur(img_rgb, (5, 5), 0)
        canny_img = cv2.Canny(img_rgb, 1, 10)
        H, W = canny_img.shape

        # 消去棋子轮廓
        for k in range(max_loc1[1] - 10, max_loc1[1] + 189):
            for b in range(max_loc1[0] - 10, max_loc1[0] + 100):
                canny_img[k][b] = 0

        img_rgb, x_center, y_center = get_center(canny_img)

    distance = (center1_loc[0] - x_center) ** 2 + (center1_loc[1] - y_center) ** 2
    distance = distance ** 0.5
    jump(distance,0)
    #随机等待若干时间避免跳跃过快
    time.sleep(random.random()+random.randint(1,2))

