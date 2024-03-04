'''
Created on 2018年12月26日

@author: Freedom
'''

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, QMutex

from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QLabel,\
    QComboBox, QFileDialog, QSlider
    
from PyQt5.QtCore import Qt
    
from VideoDetector import VideoDetector

class MainWidget(QWidget):
    
    sigStopVideo = pyqtSignal() #此信号用于正常中断视频行人检测
    sigPause = pyqtSignal() #暂停/继续信号
     
    video_width = 620

    def __init__(self, Parent=None):
        super().__init__(Parent)
        self.__InitData()
        self.__InitView()
        self.__InitSignalSlot() 

    def __InitData(self):
        #初始化数据
        self.currentVideo = "none"
        self.videoDetector = VideoDetector() #创建视频检测器对象
        self.threadVideo = ThreadVideo(self.videoDetector, self) #创建线程

    def __InitView(self):
        #初始化界面
        #设置窗体固定尺寸
        self.setFixedSize(760,420)
        #设置窗体标题
        self.setWindowTitle("pyqt5 行人检测 GUI  1507400052")
        
        #设置整体布局为水平布局
        self.__layoutMain = QHBoxLayout()
        self.__layoutMain.setSpacing(30)
        self.setLayout(self.__layoutMain)
        
        #创建左侧子布局
        self.__layoutLeft = QVBoxLayout()
        self.__layoutLeft.setSpacing(10)
        self.__layoutMain.addLayout(self.__layoutLeft)
        
        self.__labelSVM = QLabel(self)
        self.__labelSVM.setText("选择模型")
        self.__layoutLeft.addWidget(self.__labelSVM)
        
        self.__comboBoxSVM = QComboBox(self)
        self.__comboBoxSVM.addItem("model-m")
        self.__comboBoxSVM.addItem("model-c")
        self.__layoutLeft.addWidget(self.__comboBoxSVM)
        
        self.__btnChoose = QPushButton(self)
        self.__btnChoose.setText("选择视频")  
        self.__layoutLeft.addWidget(self.__btnChoose)
        
        self.__btnDetect = QPushButton(self)
        self.__btnDetect.setText("检测视频")
        self.__layoutLeft.addWidget(self.__btnDetect)
        
        self.__btnPlay = QPushButton(self)
        self.__btnPlay.setText("播放视频")
        self.__layoutLeft.addWidget(self.__btnPlay)
        
        self.__btnPause = QPushButton(self)
        self.__btnPause.setText("暂停/继续")
        self.__layoutLeft.addWidget(self.__btnPause)
        
        self.__btnEnd = QPushButton(self)
        self.__btnEnd.setText("结束活动")
        self.__layoutLeft.addWidget(self.__btnEnd)
        
        self.__btnClear = QPushButton(self)
        self.__btnClear.setText("清屏")
        self.__layoutLeft.addWidget(self.__btnClear)
        
        #亮度调节
        self.__labelBright = QLabel(self)
        self.__labelBright.setText("亮度调节")
        self.__layoutLeft.addWidget(self.__labelBright)
        
        self.__sliderBright = QSlider(self)
        self.__sliderBright.setOrientation( Qt.Horizontal)
        self.__sliderBright.setValue(99)
        self.__layoutLeft.addWidget(self.__sliderBright)
        
        self.__layoutLeft.addStretch() #增加占位符
        
        #创建右侧子布局
        self.__layoutRight = QVBoxLayout()
        self.__layoutMain.addLayout(self.__layoutRight)
        
        self.__labelVideo = QLabel(self) #视频呈现区
        self.__labelVideo.setText("视频呈现区")
        self.__labelVideo.setIndent(300)
        self.__labelVideo.setFixedWidth(MainWidget.video_width)
        self.__layoutRight.addWidget(self.__labelVideo)
        
        self.__labelInfo = QLabel(self) #状态信息
        self.__labelInfo.setText("当前视频:" + self.currentVideo)
        self.__labelInfo.setFixedWidth(MainWidget.video_width)
        self.__labelInfo.setFixedHeight(20)
        self.__layoutRight.addWidget(self.__labelInfo)
        
        self.__layoutRight.addStretch()
        
        self.__imageDefault = QImage(".\\res\\none.bmp")
        self.__pixNow = QPixmap.fromImage(self.__imageDefault)
        self.__labelVideo.setPixmap(self.__pixNow)
        
    def __InitSignalSlot(self):
        #初始化信号和槽
        self.__btnChoose.clicked.connect(self.chooseVideo)
        self.__btnDetect.clicked.connect(self.detectVideo)
        self.__btnEnd.clicked.connect(self.stopDetectVideo)
        self.__btnClear.clicked.connect(self.clearScreen)
        self.__sliderBright.valueChanged.connect(self.brightnessChange)
        self.__btnPause.clicked.connect(self.pauseOrContinue)
        self.__btnPlay.clicked.connect(self.playVideo)
        
    def updateVideoInfo(self):
        self.__labelInfo.setText("当前视频: " + self.currentVideo)

    def chooseVideo(self):
        
        if self.threadVideo.isRunning():
            self.stopDetectVideo()
            
        while self.threadVideo.isRunning():
            pass
            
        self.currentVideo, fileType = QFileDialog.getOpenFileName(self, "选择视频", ".\\", "video(*)")
        print(fileType)
        self.updateVideoInfo()
        
        self.videoDetector.loadVideo(self.currentVideo)
        
        ok, Firstframe = self.videoDetector.readVideo()
        if not ok:
            print("视频存在问题")
            return
        #显示第一帧
        Firstframe = self.videoDetector.resizeFrame(Firstframe) #调整大小
        qimage = self.videoDetector.frame2qimage(Firstframe) #转换为qimage格式
        self.__labelVideo.setPixmap(QPixmap.fromImage(qimage))
        
        self.videoDetector.releaseVideo()
        
    def detectVideo(self):
        if self.__comboBoxSVM.currentText() == "model-c":
            self.videoDetector.loadTrained()
        else:
            self.videoDetector.loadTrained(r".\models\model-mine", useDefault=False)
        
        if not self.threadVideo.isRunning():
            self.threadVideo.switchPlay(playOnly=False) #设置为非播放模式
            self.threadVideo.start() #启动线程
        
    def stopDetectVideo(self):
        print("thread will exit")    
        #self.threadVideo.terminate()
        if self.threadVideo.isRunning():
            self.sigStopVideo.emit()
            
    #暂停/继续
    def pauseOrContinue(self):
        self.sigPause.emit()
        
    #控制线程进入纯播放模式
    def playVideo(self):
        self.threadVideo.switchPlay(playOnly=True)
        if not self.threadVideo.isRunning():
            self.threadVideo.start()
            
    def brightnessChange(self, value):
        newBrightness = round( value / 99, 2);
        self.videoDetector.brightness = newBrightness
        print(newBrightness)
        
    def clearScreen(self):
        self.__labelVideo.setPixmap(QPixmap.fromImage( self.__imageDefault))
        
    def slotGetQimage(self, qimage):
        self.__labelVideo.setPixmap(QPixmap.fromImage(qimage))
    
    def slotDetectNormalDone(self):
        self.clearScreen()
        
class ThreadVideo(QThread):
    
    frameSignal = pyqtSignal(QImage) #此信号发送QImage类型
    sigNormalDone = pyqtSignal() #此信号在线程正常结束时发送

    def __init__(self, videoDetector, mainWidget):
        super().__init__()
        
        self.videoDetector = videoDetector
        self.mainWidget = mainWidget
        
        self.mutex = QMutex() #创建互斥体
        self.mutexPause = QMutex() #暂停/继续互斥体
        
        self.keepRunning = False #保持运行标志
        self.pause = False #暂停标志
        
        self.timeInterval = 20
        self.playOnly = False 
        
        self.frameSignal.connect(self.mainWidget.slotGetQimage)
        self.sigNormalDone.connect(self.mainWidget.slotDetectNormalDone)
        
        self.mainWidget.sigStopVideo.connect(self.slotVideoDetect) #关联终止检测信号和槽函数
        self.mainWidget.sigPause.connect(self.slotPauseContinue)
        
    def run(self):
        self.keepRunning = True
        self.videoDetector.loadVideo(videoPath=self.mainWidget.currentVideo)
       
        if self.playOnly is False:
            self.detectProcess()
        else:
            self.playProcess()
        
        self.videoDetector.releaseVideo()
        
        self.sigNormalDone.emit()
        print("thread run done")
   
    #检测流程     
    def detectProcess(self):
        while True:   
            self.mutex.lock()
            if self.keepRunning is False:
                self.videoDetector.releaseVideo()
                self.mutex.unlock()
                break
            self.mutex.unlock()
            
            self.mutexPause.lock()
            if self.pause:
                self.mutexPause.unlock()
                QThread.msleep(self.timeInterval)
                continue
            self.mutexPause.unlock()
            
            ok, frame = self.videoDetector.readVideo()
            if not ok:
                self.videoDetector.releaseVideo()
                break
            frame = self.videoDetector.resizeFrame(frame) #调整大小
            frame = self.videoDetector.adjustBright(frame) #调整亮度
            frame = self.videoDetector.detect_people(frame) #检测行人并标记
            qimage = self.videoDetector.frame2qimage(frame) #转换为qimage格式
            
            self.frameSignal.emit(qimage)
            
            QThread.msleep(self.timeInterval)   
    
    #播放流程
    def playProcess(self):
        playInterval = self.timeInterval + 10
        
        while True:   
            self.mutex.lock()
            if self.keepRunning is False:
                self.videoDetector.releaseVideo()
                self.mutex.unlock()
                break
            self.mutex.unlock()
            
            self.mutexPause.lock()
            if self.pause:
                self.mutexPause.unlock()
                QThread.msleep(playInterval)
                continue
            self.mutexPause.unlock()
            
            ok, frame = self.videoDetector.readVideo()
            if not ok:
                self.videoDetector.releaseVideo()
                break
            frame = self.videoDetector.resizeFrame(frame) #调整大小
            frame = self.videoDetector.adjustBright(frame) #调整亮度
            qimage = self.videoDetector.frame2qimage(frame) #转换为qimage格式
            
            self.frameSignal.emit(qimage)
            
            QThread.msleep(playInterval)  
      
    #中断视频检测
    def slotVideoDetect(self):
        #如果已经暂停，那么先恢复播放，然后才能正常退出
        if self.pause is True: 
            self.slotPauseContinue()
            
        self.mutex.lock()
        self.keepRunning = False
        self.mutex.unlock()
        
    #终止/暂停
    def slotPauseContinue(self):
        self.mutexPause.lock()
        if self.pause:
            self.pause = False
        else:
            self.pause = True
        self.mutexPause.unlock()
        
    
    #设置是否进入纯播放模式
    def switchPlay(self, playOnly=True):
        self.playOnly = playOnly
        