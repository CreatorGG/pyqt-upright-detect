'''
Created on 2018年12月26日

@author: Freedom
'''
from PyQt5.QtWidgets import QApplication
import sys

from MainWidget import MainWidget

def main():
    
    app = QApplication(sys.argv) # sys.argv即命令行参数
    
    mainWidget = MainWidget() #新建一个主界面
    mainWidget.show()   #显示主界面
    
    return app.exec_() # app.exec_() 进入消息循环
    

if __name__ == '__main__':
    main()
