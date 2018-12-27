'''
Created on 2018年12月26日

@author: Freedom
'''
import cv2
import imutils
from imutils.object_detection import non_max_suppression

from PyQt5.Qt import QImage

class VideoDetector(object):

    
    def __init__(self):
        self.__InitData()
    
    def __InitData(self):
        self.hog = cv2.HOGDescriptor() #创建HOG检测器
        self.loadTrained() #载入训练模型
        self.capture = None
        self.frameWidth = 600 #检测帧的宽度一致调整为600像素
        self.brightness = 1 #默认亮度为1
        
    
    def detect_people(self, frame):
        """
        detect humans using HOG descriptor
        Args:
            frame:
        Returns:
            processed frame
        """
        frame = imutils.resize(frame, width=600)
        (rects, weights) = self.hog.detectMultiScale(frame, winStride=(8, 8), padding=(16, 16), scale=1.06)
        #应用非极大抑制方法，通过设置一个阈值来抑制那些重叠的边框
        rects = non_max_suppression(rects, probs=None, overlapThresh=0.65)
        for (x, y, w, h) in rects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        return frame
    
    def adjustBright(self, frame):
        
        if self.brightness >= 1:
            return frame
        
        w = frame.shape[1]
        h = frame.shape[0]
        for x in range(0,w):
            for y in range(0,h):
                frame[y ,x, 0] = int(frame[y, x, 0] * self.brightness)
                frame[y ,x, 1] = int(frame[y, x, 1] * self.brightness)
                frame[y ,x, 2] = int(frame[y, x, 2] * self.brightness)
                
        return frame
    
    #载入视频
    def loadVideo(self, videoPath):
        self.capture =  cv2.VideoCapture(videoPath) 
    
    #关闭视频文件
    def releaseVideo(self):
        self.capture.release() 
        
    #载入训练好的模型
    def loadTrained(self, modelPath=None, useDefault=True):
        if useDefault or modelPath is None:
            #使用opencv自带的模型
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        else:
            self.hog.load(modelPath)
    
    #将opencv读取的图片数据转换为QImage类型
    def frame2qimage(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame[:], frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
        return image
    
    def resizeFrame(self, frame):
        frame_resized = imutils.resize(frame, width=self.frameWidth)
        return frame_resized
        
    def readVideo(self):
        ok, frame = self.capture.read()
        return ok, frame
    