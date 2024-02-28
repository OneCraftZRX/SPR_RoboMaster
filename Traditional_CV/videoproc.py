from ncsyproclib import ncsyprocs
import cv2
import numpy as np

videoinpath = './test.mp4'
videooutpath = './test_out.mp4'
capture = cv2.VideoCapture(videoinpath)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(videooutpath ,fourcc, 24.0, (640,512), True)
if capture.isOpened():
    while True:
        ret,img_src=capture.read()
        if not ret:break

        #find cnts
        img=img_src.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret1, binary = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #sort cnts
        contours_sorted,boxes=ncsyprocs.sort_contours(contours,'left-to-right')

        #draw cnts
        cv2.drawContours(img_src, contours_sorted, -1, (0, 255, 0), 1)
        # cv2.imshow("Post",img_src)
        # cv2.waitKey(0)
        img_out = ncsyprocs.merge_and_show_max_min(img_src,contours_sorted,2)
        cv2.imshow("Past",img_out)
        cv2.waitKey(0)
        #print("processed1img")
        writer.write(img_out)
else:
    print('视频打开失败！')
writer.release()
print("over")