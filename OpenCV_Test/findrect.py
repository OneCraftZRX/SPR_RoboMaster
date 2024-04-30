import cv2
import numpy as np

def sort_contours(cnts, method='left-to-right'):
    reverse = False
    i = 0
    if method == 'right-to-left' or method == 'bottom-to-top':
        reverse = True
    if method == 'bottom-to-top' or method == 'top-to-bottom':
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b: b[1][i], reverse=reverse))
    return (cnts, boundingBoxes)

def show_each2_merge_min(img2proc,cnts):

    length=len(cnts)
    for i in range(length-1):
        print("merge",i,"and",i+1)
        merge_list = []
        merge_list.append(cnts[i])
        merge_list.append(cnts[i+1])
        contours_merge = np.vstack([merge_list[0],merge_list[1]])
        print("time",i)
        print(contours_merge)
        rect = cv2.minAreaRect(contours_merge)
        box = cv2.boxPoints(rect)
        box = np.round(box).astype('int64')
        cv2.drawContours(img2proc, [box], 0, (255, 0, 0), 2)
        print("draw",i,"and",i+1)
        #cv2.drawContours(img2proc, contours_merge, -1, (0, 255, 0), 2)
        
    cv2.imshow('findmergemin', img2proc)

def show_each2_merge_max(img2proc,cnts):
    length=len(cnts)
    for i in range(length-1):
        print("merge",i,"and",i+1)
        merge_list = []
        merge_list.append(cnts[i])
        merge_list.append(cnts[i+1])
        contours_merge = np.vstack([merge_list[0],merge_list[1]])
        x, y, w, h = cv2.boundingRect(contours_merge)
        cv2.rectangle(img2proc, (x, y), (x + w, y + h), (0, 0, 255), 2)
        print("draw",i,"and",i+1)
    cv2.imshow('findmergemax', img2proc)
 
img = cv2.imread('./robo3.png') #, cv2.IMREAD_GRAYSCALE
img_ori=img.copy()
img_findrect1=img.copy()
img_findrect2=img.copy()
img_findmerge1=img.copy()
img_findmerge2=img.copy()
#img_findrect3=img.copy()

    # 转变成单通道
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 二值化,第一个返回值是执行的结果和状态是否成功，第二个返回值才是真正的图片结果
ret, binary = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
    # 轮廓查找,第一个返回值是轮廓，第二个是层级
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
contours_sorted,boxes=sort_contours(contours,'left-to-right')

    # 绘制轮廓
cv2.drawContours(img, contours_sorted, -1, (0, 0, 255), 1)  # 改变的是img这张图
 
cv2.imshow('findedge', img)
cv2.imshow('bin', binary)
print(len(contours_sorted))


for i in range(len(contours_sorted)):
    rect = cv2.minAreaRect(contours_sorted[i])
    box = cv2.boxPoints(rect)
    box = np.round(box).astype('int64')
    # 绘制最小外接矩形
    cv2.drawContours(img_findrect1, [box], 0, (255, 0, 0), 2)
cv2.imshow('findrectmin', img_findrect1)
    
for i in range(len(contours_sorted)):
    # 最大外接矩形
    x, y, w, h = cv2.boundingRect(contours_sorted[i])
    cv2.rectangle(img_findrect2, (x, y), (x + w, y + h), (0, 0, 255), 2)
cv2.imshow('findrectmax', img_findrect2)

show_each2_merge_min(img_findmerge1,contours_sorted)
show_each2_merge_max(img_findmerge2,contours_sorted)

cv2.waitKey(0)
cv2.destroyAllWindows()