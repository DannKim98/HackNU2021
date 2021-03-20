from django.shortcuts import render, redirect
import cv2
import threading
import requests
import telegram_send
import datetime
import numpy as np

# Create your views here.
student = 'Denis Kim'

def main_page(request):
    return render(request,'main_page.html')

def instructions(request):
    if request.method == 'POST':
        return redirect('take_exam')

    return render(request, 'instructions.html')

def detect():
    cap = cv2.VideoCapture(0)
    cap.set(3,480)
    cap.set(4,270)
    cap.set(10,70)

    classNames= []
    classFile = 'coco.names'
    with open(classFile,'rt') as f:
        classNames = f.read().rstrip('\n').split('\n')

    configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    weightsPath = 'frozen_inference_graph.pb'

    net = cv2.dnn_DetectionModel(weightsPath,configPath)
    net.setInputSize(320,320)
    net.setInputScale(1.0/ 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)
    isHelped = False
    isPhone = False
    isGone = False

    while True:
        success,img = cap.read()
        classIds, confs, bbox = net.detect(img,confThreshold=0.5)
        print(classIds,bbox)

        if len(classIds) != 0:
            for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                if classId == 77:
                    cv2.rectangle(img,box,color=(0,0,255),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                            cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,255),2)
                else:
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,255,0),2)

        if np.count_nonzero(classIds == 1) > 1 and not isHelped:
            print('Cheating Behavior is Detected (' + str(np.count_nonzero(classIds == 1)) + ' People are Detected)')
            cv2.imwrite('people.jpg', img)
            with open("people.jpg", "rb") as f:
                telegram_send.send(images=[f], messages=[str(datetime.datetime.now())[:19] + ', ' + student + ': Cheating Behavior is Detected (' + str(np.count_nonzero(classIds == 1)) + ' People are Detected)'])
            isHelped = True

        if [77] in classIds and not isPhone:
            print('Cheating Behavior is Detected (Cell Phone is Detected)')
            cv2.imwrite('cell_phone.jpg', img)
            with open("cell_phone.jpg", "rb") as f:
                telegram_send.send(images=[f], messages=[str(datetime.datetime.now())[:19] + ', ' + student + ': Cheating Behavior is Detected (Cell Phone is Detected)'])
            isPhone = True

        if [1] not in classIds and not isGone:
            print('Cheating Behavior is Detected (Cell Phone is Detected)')
            cv2.imwrite('gone.jpg', img)
            with open("gone.jpg", "rb") as f:
                telegram_send.send(images=[f], messages=[str(datetime.datetime.now())[:19] + ', ' + student + ': Cheating Behavior is Detected (Student Gone)'])
            isGone = True

        # cv2.imshow("Output",img)
        cv2.waitKey(1)

def take_exam(request):
    if request.method == 'POST':
        telegram_send.send(messages=[str(datetime.datetime.now())[:19] + ', ' + student + ' Finished the Exam'])
        return redirect('finished_exam')

    questions = range(1, 5)
    telegram_send.send(messages=[str(datetime.datetime.now())[:19] + ', ' + student + ' Started the Exam'])
    th = threading.Thread(target=detect)
    th.start()
    return render(request,'take_exam.html', {'questions':questions})

def finished_exam(request):
    return render(request, 'finished_exam.html')
