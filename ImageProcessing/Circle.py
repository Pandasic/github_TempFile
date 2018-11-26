import numpy as np
import matplotlib.pyplot as plt
from skimage import draw,transform,feature

img = np.zeros((250, 250,3), dtype=np.uint8)
rr, cc = draw.circle_perimeter(60, 60, 50)  #以半径50画一个圆
rr1, cc1 = draw.circle_perimeter(150, 150, 60) #以半径60画一个圆
img[cc, rr,:] =255
img[cc1, rr1,:] =255

fig, (ax0,ax1) = plt.subplots(1,2, figsize=(8, 5))

ax0.imshow(img)  #显示原图
ax0.set_title('origin image')

hough_radii = np.arange(50, 80, 5)  #半径范围
hough_res =transform.hough_circle(img[:,:,0], hough_radii)  #圆变换

centers = []  #保存所有圆心点坐标
accums = []   #累积值
radii = []    #半径

for radius, h in zip(hough_radii, hough_res):
    #每一个半径值，取出其中两个圆
    num_peaks = 2
    peaks =feature.peak_local_max(h, num_peaks=num_peaks) #取出峰值
    centers.extend(peaks)
    accums.extend(h[peaks[:, 0], peaks[:, 1]])
    radii.extend([radius] * num_peaks)

#画出最接近的圆
image =np.copy(img)
for idx in np.argsort(accums)[::-1][:2]:
    center_x, center_y = centers[idx]
    radius = radii[idx]
    cx, cy =draw.circle_perimeter(center_y, center_x, radius)
    image[cy, cx] =(255,0,0)

ax1.imshow(image)
ax1.set_title('detected image')
plt.show()