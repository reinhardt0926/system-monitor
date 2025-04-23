import sys
import os
from PyQt5.QtWidgets import QApplication
from mnt_src.ui.app import SystemMonitor


def main():
    '''function of starting application'''
    try:
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
    
        icon_path = os.path.join(os.path.dirname(application_path), "resources", "icons", "system_image.ico")
        print(icon_path)
        
        app = QApplication(sys.argv)
        window = SystemMonitor(icon_path)
        window.show()
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        input("아무 키나 눌러 종료하세요....")
        sys.exit(1)
    

if __name__ == "__main__":
    main()