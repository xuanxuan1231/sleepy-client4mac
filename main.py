import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout

from qfluentwidgets import FluentWindow, SplashScreen, setTheme, Theme
from nt_thread import getDictThread, getListThread

from widgets import *


class SleepyClient(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dashboard_interface = uic.loadUi('./assets/ui/main.ui')
        self.dashboard_interface.setObjectName('mainPage')

        self.widgets_grid = None
        self.get_json_thread = None
        self.get_status_list_thread = None
        self.callback_counter = 0

        self.initUi()
        self.init_subInterface()

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.get_all_json()

    def setup_dashboard(self):
        self.widgets_grid = self.dashboard_interface.findChild(QGridLayout, 'widgets_grid')
        self.widgets_grid.setSpacing(12)

        for i in range(len(cf.widgets_config)):
            # 行列
            row = i // 2
            col = i % 2

            widget_class = get_widget(cf.widgets_config[i])  # 获取 BaseWidget 类
            w = widget_class(self)
            w.setParent(self)
            self.widgets_grid.addWidget(w, row, col)

    def get_all_json(self):
        def check_callbacks():
            self.callback_counter += 1
            if self.callback_counter == 2:
                self.splashScreen.finish()
                self.setup_dashboard()

        def callback_status(data):
            cf.status_info = data['info']
            check_callbacks()

        def callback_list(data):
            for status in data:
                cf.status_dict[status['id']] = f"{status['name']} - {status['desc']}"
            print(cf.status_dict)
            check_callbacks()

        self.get_json_thread = getDictThread(f'{cf.server}/query')
        self.get_json_thread.json_signal.connect(callback_status)
        self.get_json_thread.start()

        self.get_status_list_thread = getListThread(f'{cf.server}/status_list')
        self.get_status_list_thread.json_signal.connect(callback_list)
        self.get_status_list_thread.start()

    def init_subInterface(self):
        self.addSubInterface(self.dashboard_interface, fIcon.TILES, '仪表板')

    def initUi(self):
        setTheme(Theme.AUTO)
        self.resize(800, 600)
        self.setMinimumSize(400, 300)
        self.setWindowTitle('Sleepy Client')
        self.setWindowIcon(QIcon('assets/images/favicon.png'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SleepyClient()
    window.show()
    app.exec_()
