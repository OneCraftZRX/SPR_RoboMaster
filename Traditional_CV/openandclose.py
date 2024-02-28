import cv2 as cv
import numpy as np

def open(image):

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    ret, binary = cv.threshold(gray, 130, 255, cv.THRESH_BINARY)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 6))
    dst = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel)
    cv.imshow("open", dst)
    cv.imwrite("./robo3.png",dst)

def close(image):

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    ret, binary = cv.threshold(gray, 130, 255, cv.THRESH_BINARY)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
    dst = cv.morphologyEx(binary, cv.MORPH_CLOSE, kernel)
    cv.imshow("close", dst)


src = cv.imread("./robo2.png")
cv.imshow("src", src)
open(src)
close(src)


cv.waitKey(0)