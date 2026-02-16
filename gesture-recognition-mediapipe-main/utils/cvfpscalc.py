from collections import deque
import cv2 as cv
from datetime import datetime

class CvFpsCalc(object):
    def __init__(self, buffer_len=1):
        self._start_tick = cv.getTickCount()
        self._freq = 1000.0 / cv.getTickFrequency()
        self._difftimes = deque(maxlen=buffer_len)

    def get(self):
        current_tick = cv.getTickCount()
        different_time = (current_tick - self._start_tick) * self._freq
        self._start_tick = current_tick

        self._difftimes.append(different_time)

        fps = 1000.0 / (sum(self._difftimes) / len(self._difftimes))
        fps_rounded = round(fps, 2)

        return fps_rounded

class History:
    def __init__(self):
        pass
    
    def save_run(self):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log = date + ' |INFO| The Application is booting'
        file = open ('data/hisorylog.txt','a')
        file.write('\n'+log)
        file.close()
        
    def save(self, action):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log = date + ' |INFO| ' + action
        file = open ('data/hisorylog.txt','a')
        file.write('\n'+log)
        file.close()
    
    def save_error(self, error):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log = date + ' |Error| ' + error
        file = open ('data/hisorylog.txt','a')
        file.write('\n'+log)
        file.close()
        
    def printHistory(self):
        file = open ('data/hisorylog.txt','r')
        mensaje = file.read()
        print(mensaje)
        file.close()
    
    def getHistoryArray(self):
        file = open ('data/hisorylog.txt','r')
        return file.read().split("\n")