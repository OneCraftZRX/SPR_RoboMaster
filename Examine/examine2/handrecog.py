import cv2
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1,detectionCon=0.8)

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img, draw=True, flipType=True)
    if hands:
        hand1 = hands[0]
        fingers1 = detector.fingersUp(hand1)
        if fingers1 == [0, 0, 0, 0, 0]:
            print("石头")
            playerMove = 1
        if fingers1 == [1, 1, 1, 1, 1]:
            playerMove = 2
            print("布")
        if fingers1 == [0, 1, 1, 0, 0]:
            playerMove = 3
            print("剪刀")
    cv2.imshow("Image", img)
    cv2.waitKey(1)