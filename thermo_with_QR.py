# coding utf-8
import time
import numpy as np
import cv2 as cv
import serial
import busio
import board
import adafruit_amg88xx
import threading
import pprint
import HTTPWebApp as jica

#Face thermo with QR
class Ftwq:
    def __init__(self):
        #i2c初期化
        self.i2c = busio.I2C(board.SCL, board.SDA)
        #サーモセンサの初期化
        self.sensor = adafruit_amg88xx.AMG88XX(self.i2c, addr=0x69)
        #初期化のために待つ
        time.sleep(0.2)
        # 顔の分類器の作成
        self.faceCascade = cv.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
        #threadの作成
        self._thermo_face_task = threading.Thread(target = self.ThermoFace)
        self._QR_read_task = threading.Thread(target = self.QrRead)
        #QRコードを受け取るための変数の初期化
        self.student_id = None
        #データベースログイン情報
        self.email = 'testaccount@gmail.com'
        self.password = 'testAccountPassword'
        #HTTPWebAppのインスタンス生成
        self.post_data_app = jica.HTTPWebApp(self.email, self.password)
        #ゲート（設置場所）のID
        self.place_id = '2o6sB6opdUT23pPaK7A6'

    def QrRead(self):
        while True:
            if self.student_id is None:
                port = "/dev/ttyACM0"
                byte = 4096
                ser = serial.Serial(port=port)
                ret = ser.read_until(b'\r')
                ret = ret.decode("UTF-8")#バイト列を文字列に変換
                self.student_id = ret.strip("\r")#\rを削除
                print(self.student_id)
                ser.close()

    def SendOpen(self):
        ser = serial.Serial('/dev/ttyS0','9600',timeout=0.1)
        ser.write(str.encode("Open;"))
        ser.close()

    def SendClose(self):
        ser = serial.Serial('/dev/ttyS0','9600',timeout=0.1)
        ser.write(str.encode("Close;"))
        ser.close()


    def start(self):
        self._thermo_face_task.start()
        self._QR_read_task.start()

    def ThermoFace(self):
        # カメラ初期化、処理時間の高速化
        cap = cv.VideoCapture(0)
        cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('H', '2', '6', '4'));
        
        while True:
            ret, frame = cap.read()
            h, w, c = frame.shape
            #cv.imshow('camera capture', frame)
            
            # 顔検出の処理効率化のために、写真の情報量を落とす（モノクロにする）
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # 顔の認識
            facerect = self.faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(1, 1))
            
            if (len(facerect) > 0) and (self.student_id is not None):
                for rect in facerect:
                    # 配列のスライス→ rect[開始位置:終了位置] rect[0:2]→[左上X座標, 左上Y座標]
                    cv.rectangle(frame, tuple(rect[0:2]), tuple(rect[0:2]+rect[2:4]), (0, 0, 255), thickness=2)
		
                max_temp = 0.0
                # 8x8の温度配列
                pixels = self.sensor.pixels
                for x in range(len(pixels)):
                    for y in range(len(pixels[0])):
                        # 最大温度を格納する
                        if (pixels[x][y] > max_temp):
                            max_temp = pixels[x][y]
                #print(self.student_id)
                body_T = str(max_temp)
                print(self.student_id + ':' + body_T)
                pprint.pprint(self.post_data_app.postBodyTemperature(self.place_id, self.student_id, body_T))         


                if max_temp < 25:
                    self.SendOpen()
                else:
                    self.SendClose()

                self.student_id = None
            cv.imshow('camera capture', frame)
            
            # ESC
            if cv.waitKey(1) == 27:
                break
        cap.release()
        # 表示したウィンドウを閉じる
        cv.destroyAllWindows()
        print('Stop showing video')
    
    def main(self):
        self.start()

if __name__ == '__main__':
    sample = Ftwq()
    sample.main()
