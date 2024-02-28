import cv2
import numpy as np

#debug注意图像通道的转换！

class ncsyprocs(object):
    # def makevideo():
    #     videoinpath = 'video.mp4'
    #     videooutpath = 'video_out.mp4'
    #     capture = cv2.VideoCapture(videoinpath)
    #     fourcc = cv2.VideoWriter_fourcc(*'X265')
    #     writer = cv2.VideoWriter(videooutpath ,fourcc, 24.0, (640,512), True)
    #     if capture.isOpened():
    #         while True:
    #             ret,img_src=capture.read()
    #             if not ret:break
    #             img_out = op(img_src)
    #             writer.write(img_out)
    #     else:
    #         print('视频打开失败！')
    #     writer.release()
    #     #现在没用

    def thresholdplus(src,show):
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        ret, dst = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
        #第一个返回值是执行的结果和状态是否成功，第二个返回值才是真正的图片结果
        if show==1:
            cv2.imshow('threshold', dst)
            return dst
        else:
            return dst

    def open_with_threshold(image,show):
        binary=ncsyprocs.thresholdplus(image,0)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 6))
        dst = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        if show==1:
            cv2.imshow("open", dst)
            return dst
        else:
            return dst

    def close_with_threshold(image,show):
        binary=ncsyprocs.thresholdplus(image,0)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dst = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        if show==1:
            cv2.imshow("close_with_threshold", dst)
            return dst
        else:
            return dst

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

    def merge_and_show_max_min(img2proc,cnts,show):
        length=len(cnts)
        merge_list=[0]
        if show==1:
            for i in range(length-1):
                #print("merge",i,"and",i+1)
                merge_temp = []
                merge_temp.append(cnts[i])
                merge_temp.append(cnts[i+1])
                contours_merge = np.vstack([merge_temp[0],merge_temp[1]])
                rect = cv2.minAreaRect(contours_merge)
                box = cv2.boxPoints(rect)
                box = np.round(box).astype('int64')
                cv2.drawContours(img2proc, [box], 0, (255, 0, 0), 2)
            #cv2.imshow('findmergemin', img2proc)
            #cv2.drawContours(img2proc, contours_merge, -1, (0, 255, 0), 2)
        elif show==2:
            for i in range(length-1):
                #print("merge",i,"and",i+1)
                merge_list = []
                merge_list.append(cnts[i])
                merge_list.append(cnts[i+1])
                contours_merge = np.vstack([merge_list[0],merge_list[1]])
                x, y, w, h = cv2.boundingRect(contours_merge)
                cv2.rectangle(img2proc, (x, y), (x + w, y + h), (0, 0, 255), 2)
                #print("draw",i,"and",i+1)
            #cv2.imshow('findmergemax', img2proc)
            #cv2.drawContours(img2proc, contours_merge, -1, (0, 255, 0), 2)
        else:
            for i in range(length-1):
                merge_list.pop(i)
                merge_list.append(cnts[i])
                merge_list.append(cnts[i+1])
            print("merged",len(merge_list),"elements in total")
            return merge_list

    def findrect_max_min(img,cnts,show,method):
        if method=="max":
            for i in range(len(cnts)):
                x, y, w, h = cv2.boundingRect(cnts[i])
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            if show ==1:
                cv2.imshow('findrectmax', img)
                return img
            else:
                return img
        elif method=="min":
            for i in range(len(cnts)):
                rect = cv2.minAreaRect(cnts[i])
                box = cv2.boxPoints(rect)
                box = np.round(box).astype('int64')
                cv2.drawContours(img, [box], 0, (255, 0, 0), 2)
            if show==1:
                cv2.imshow('findrectmin', img)
                return img
            else:
                return img


img = cv2.imread('C:\\Users\\25176\\OneDrive\\Codes\\SPR2024\\TestGit\\MainProject\\robo3.png') 
img_ori=cv2.imread('C:\\Users\\25176\\OneDrive\\Codes\\SPR2024\\TestGit\\MainProject\\robo.png') 
img_bin=cv2.imread('C:\\Users\\25176\\OneDrive\\Codes\\SPR2024\\TestGit\\MainProject\\robo.png')
cv2.imshow("binary", img_bin)

img_findmerge1=img.copy()
img_findmerge2=img.copy()

img_procd1=ncsyprocs.thresholdplus(img_ori,1)
img_procd2=ncsyprocs.open_with_threshold(img_ori,1)
img_findcnts=img.copy()
#close(img_ori,1)

#main
####################################################################################
#find cnts
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, binary = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

#sort cnts
contours_sorted,boxes=ncsyprocs.sort_contours(contours,'left-to-right')

#draw cnts
cv2.drawContours(img_findcnts, contours_sorted, -1, (0, 255, 0), 1)
cv2.imshow('findcnts', img_findcnts)
#cv2.imshow('selected_bin(opened)', binary)

img_findrect1=img.copy()
img_findrect2=img.copy()

ncsyprocs.findrect_max_min(img_findrect1,contours_sorted,1,"max")
ncsyprocs.findrect_max_min(img_findrect2,contours_sorted,1,"min")

ncsyprocs.merge_and_show_max_min(img_findmerge1,contours_sorted,1)
ncsyprocs.merge_and_show_max_min(img_findmerge2,contours_sorted,2)
ncsyprocs.merge_and_show_max_min(img_findmerge2,contours_sorted,0)

cv2.waitKey(0)
cv2.destroyAllWindows()