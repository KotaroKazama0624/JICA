import pygame.mixer
import time

#mixerモジュールの初期化
pygame.mixer.init()
#音楽ファイルの読み込み
pygame.mixer.music.load("Answer.mp3")
#音楽再生、及び再生回数の設定（-1はループ設定）
pygame.mixer.music.play(-1)

time.sleep(60)
#再生の終了
pygame.mixer.music.stop()
