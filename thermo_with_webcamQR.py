# coding utf-8
import pygame
import time
import numpy as np
import cv2 as cv
import serial
import busio
import board
import adafruit_amg88xx
import pprint
import HTTPWebApp as jica
import smbus
from pyzbar.pyzbar import decode

#Face thermo with webcamQR
class Ftwq:
    def __init__(self):
        #i2c初期化
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)
        #サーモセンサの初期化
        self.sensor = adafruit_amg88xx.AMG88XX(self.i2c_bus, addr=0x69) 
        #初期化のために待つ
        time.sleep(0.2)
        #mixerモジュールの初期化
        pygame.mixer.quit()
        pygame.mixer.pre_init(buffer=128)
        pygame.mixer.init(1)
        time.sleep(0.2)
        # 顔の分類器の作成
        self.faceCascade = cv.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
        #QRコードを受け取るための変数の初期化
        self.student_id = None
        #データベースログイン情報
        self.email = 'testaccount@gmail.com'
        self.password = 'testAccountPassword'
        #HTTPWebAppのインスタンス生成
        self.post_data_app = jica.HTTPWebApp(self.email, self.password)
        #ゲート（設置場所）のID
        self.place_id = '2o6sB6opdUT23pPaK7A6'


    def SendOpen(self):
        ser = serial.Serial('/dev/ttyS0','9600',timeout=0.1)
        ser.write(str.encode("Open;"))
        ser.close()

    def SendClose(self):
        ser = serial.Serial('/dev/ttyS0','9600',timeout=0.1)
        ser.write(str.encode("Close;"))
        ser.close()

    def Answer(self):
        pygame.mixer.music.load("Answer.mp3")
        pygame.mixer.music.play(1)
        time.sleep(1)
        pygame.mixer.music.stop()

    def Wrong(self):
        pygame.mixer.music.load("Wrong.mp3")
        pygame.mixer.music.play(1)
        time.sleep(1)
        pygame.mixer.music.stop()


    def ThermoFace(self):
        # カメラ初期化、処理時間の高速化
        cap = cv.VideoCapture(0)
        cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('H', '2', '6', '4'))

        while True:
            ret, frame = cap.read()
            #h, w, c = frame.shape
            cv.imshow('camera capture', frame)
            
            # 顔検出の処理効率化のために、写真の情報量を落とす（モノクロにする）
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            data = decode(gray)

            if self.student_id is None:
                for symbol in data:
                    self.student_id = data[0][0].decode('utf-8', 'ignore')
                    print(self.student_id)
            else:
                 # 顔の認識
                facerect = self.faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(1, 1))
                if len((facerect)) > 0:
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
                    
                    #体温の補正
                    body_t = round(((36.7/28.5)*max_temp),1)
                    body_T = str(body_t)
                    print(self.student_id + ':' + body_T)
                    #サーバーに場所、学籍番号、体温を送信
                    pprint.pprint(self.post_data_app.postBodyTemperature(self.place_id, self.student_id, body_T))         

                    #一定以上の体温でブザーを鳴らす
                    if body_t < 37.5:
                        self.Answer()
                        self.SendOpen()
                        #self.Answer()
                    else:
                        self.Wrong()
                        self.SendClose()
                        #self.Wrong()

                    self.student_id = None
            
            # ESC
            if cv.waitKey(1) == 27:
                break
        cap.release()
        # 表示したウィンドウを閉じる
        cv.destroyAllWindows()
        print('Stop showing video')
    
    #def main(self):
    #    self.start()

if __name__ == '__main__':
    sample = Ftwq()
    sample.ThermoFace()
