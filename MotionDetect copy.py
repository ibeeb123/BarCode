#-*-coding:utf-8-*-
import cv2
import numpy as np
from datetime import datetime
import time
import json
import requests
import os

cap = cv2.VideoCapture("http://192.168.0.199:8091/?action=stream")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

thresh = 25
diff_max = 5
a, b, c = None, None, None

arr=[]                              # 배열 선언
centervalue = int(len(arr)/2)

if cap.isOpened():   
    
    while True:
        cctvhour = datetime.now().hour
        if(cctvhour >=12):
            print("cctv 작동중")
            ret, a = cap.read()
            ret, b = cap.read()
            ret, c = cap.read()
            d = c.copy              # 프레임 형식 복사 저장        
       
            if not ret:
                break        
       
            # 3 프레임의 영상을 모두 흑백으로 전환
            a_gray = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
            b_gray = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
            c_gray = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)

            # 1,2 프레임, 2,3 프레임 영상들의 차를 구함
            diff_ab = cv2.absdiff(a_gray, b_gray)
            diff_bc = cv2.absdiff(b_gray, c_gray)

            # 영상들의 차가 threshold 이상이면 값을 255(백색)으로 만들어줌 threshold
            ret, diff_ab_t = cv2.threshold(diff_ab, thresh, 255, cv2.THRESH_BINARY)
            ret, diff_bc_t = cv2.threshold(diff_bc, thresh, 255, cv2.THRESH_BINARY)

            # 두 영상 차의 공통된 부분을 1(흰색)로 만들어줌
            diff = cv2.bitwise_and(diff_ab_t, diff_bc_t)

            # 영상에서 1이 된 부분을 적당히 확장해줌(morpholgy)
            k = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
            diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, k)

            # 영상에서 1인 부분의 갯수를 셈
            diff_cnt = cv2.countNonZero(diff)
        
            if diff_cnt > diff_max:
                arr.append(c)       
                print(diff_cnt)              
                                                     
                if len(arr) >= 5:                 
                    d = arr[centervalue]
                    shotcheck = cv2.imwrite("uploads/screenshot.jpg", d)
                    image = open("/home/pi/hee/uploads/screenshot.jpg",'rb')

                    files = {'test_image':image}
                    res =requests.post('http://gowoong.com:4000/upload/single', files = files)
                    os.remove("/home/pi/hee/uploads/screenshot.jpg")
                    arr =[]
                    print("배열 초기화")                       
            
                a = b
                b = c                                    
              
            cv2.imshow('motion',c)        
        
            if cv2.waitKey(1) & 0xFF == 27:
                break
        else:
            print("동작중지")                                           

cap.release()
cv2.destroyAllWindows()
	


    

