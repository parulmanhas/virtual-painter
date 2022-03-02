import cv2
import HandTrackingModule as htm
from flask import Flask, render_template, request, redirect,Response, session  # importing all the necessary libraries
import os
import numpy as np
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)
conn = sqlite3.connect('minorprojdb.sqlite', check_same_thread=False)

cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/saveuserdata', methods=['POST'])
def saveuserdata():
    Name = request.form.get('Name')
    Email = request.form.get('Email')
    Password = request.form.get('Password')

    cursor.execute( """INSERT INTO `user_data` (`Name`,`Email`,`Password`) VALUES ('{}','{}','{}')""".format(Name, Email, Password))
    conn.commit()

    return render_template('index.html')

@app.route('/signin', methods=['POST'])
def signin():
    Email= request.form.get('Emaill')
    Password = request.form.get('Passwordd')
    cursor.execute(
        """SELECT * FROM `user_data` WHERE `Email` LIKE '{}' AND `Password` LIKE '{}'""".format(Email, Password))
    users = cursor.fetchall()
    if len(users) > 0:
        return redirect('/about')
    else:
        return redirect('/signin')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/Contact')
def Contact():
    return render_template('Contact.html')

@app.route('/knowus')
def knowus():
    return render_template('knowus.html')

@app.route('/video')
def video():

    ##################################
    brushThickness = 15
    eraserThickness = 100

    ###################################
    folderPath = "Header"
    myList = os.listdir(folderPath)
    print(myList)
    overLayList = []
    for imPath in myList:
        image = cv2.imread(f'{folderPath}/{imPath}')
        overLayList.append(image)
    print(len(overLayList))

    header = overLayList[0]
    drawColor = (255, 0, 255)

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = htm.handDetector(detectionCon=int(0.85))
    xp, yp = 0, 0
    imgCanvas = np.zeros((720, 1280, 3), np.uint8)

    while True:
        # 1. Import Image
        success, img = cap.read()
        # flip image- mirror image
        img = cv2.flip(img, 1)

        # 2. Find hand landmarks
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if (len(lmList) != 0):

            # print(lmList)

            # tip of index and middle fingers
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]

            # 3. Check which fingers are up
            fingers = detector.fingersUp()
            print(fingers)

            # 4. If selection mode - 2 fingers are up
            if fingers[1] and fingers[2]:
                xp, yp = 0, 0

                print("Selection mode")
                # checking for click
                if y1 < 125:
                    if 250 < x1 < 400:
                        header = overLayList[0]
                        drawColor = (255, 0, 255)
                    elif 400 < x1 < 550:
                        header = overLayList[1]
                        drawColor = (0, 0, 0)
                    elif 600 < x1 < 750:
                        header = overLayList[2]
                        drawColor = (255, 0, 0)
                    elif 800 < x1 < 1000:
                        header = overLayList[3]
                        drawColor = (0, 255, 0)
                    elif 1050 < x1 < 1200:
                        header = overLayList[4]
                        drawColor = (0, 0, 0)
                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

            # 5. If drawing mode- index finger is up
            if fingers[1] and fingers[2] == False:
                cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
                print("Drawing mode")
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                if drawColor == (0, 0, 0):
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
                else:
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                xp, yp = x1, y1

        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)

        # Setting the header image
        img[0:125, 0:1280] = header
        img = cv2.addWeighted(img, 0.5, imgCanvas, 0, 5, 0)

        cv2.imshow("Canvas", imgCanvas)
        cv2.imshow("Image", img)

        if cv2.waitKey(2) & 0xff == ord('q'):
            break
        cv2.waitKey(1)


# main driver function
if __name__ == '__main__':
    app.run(debug=True)