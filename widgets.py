from functools import partial

import config as cf
import window_detection as wd
from nt_thread import getDictThread, postThread
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout, QVBoxLayout, QSpacerItem
from qfluentwidgets import FluentIcon as fIcon, StrongBodyLabel, TransparentDropDownToolButton, \
    IconWidget, RoundMenu, Action, ImageLabel, ElevatedCardWidget, ProgressRing, BodyLabel, PrimaryPushButton, \
    PrimaryDropDownPushButton, SubtitleLabel, InfoBarPosition, InfoBar, LineEdit, SwitchButton


class BaseWidget(ElevatedCardWidget):
    def __init__(self, parent=None, title='基本组件',
                 icon=fIcon.LIBRARY_FILL.colored(QColor('#666'), QColor('#CCC')) or '/path/to/icon'):
        super().__init__(parent)
        uic.loadUi('./assets/ui/widget-base.ui', self)

        self.parent = parent
        self.title_label = None
        self.icon_label = None
        self.more_options = None
        self.top_layout = None
        self.bottom_layout = None
        self.content_layout = None
        self.title = title
        self.icon = icon
        self.width_threshold = 500  # 设置宽度阈值

        self.initUi()

        self.setMinimumHeight(250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def initUi(self):
        self.top_layout = self.findChild(QHBoxLayout, 'top')
        self.bottom_layout = self.findChild(QHBoxLayout, 'bottom')
        self.content_layout = self.findChild(QVBoxLayout, 'content')

        self.title_label = self.findChild(StrongBodyLabel, 'title_label')
        self.more_options = self.findChild(TransparentDropDownToolButton, 'more_options')

        if type(self.icon) is str:
            self.icon_label = ImageLabel()
            self.icon_label.setImage(self.icon)
        else:
            self.icon_label = IconWidget()
            self.icon_label.setIcon(self.icon)

        more_options_menu = RoundMenu(self)
        more_options_menu.addAction(Action(fIcon.CLOSE, '移除本组件'))

        self.title_label.setText(self.title)
        self.more_options.setFixedSize(32, 26)
        self.icon_label.setFixedSize(18, 18)

        self.more_options.setMenu(more_options_menu)

        self.top_layout.insertWidget(0, self.icon_label)

    def hide_title(self):
        self.title_label.hide()
        self.icon_label.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_width = event.size().width()
        if new_width > self.width_threshold:
            self.setMinimumHeight(300)  # 当宽度超过阈值时，设置新的最小高度
        else:
            self.setMinimumHeight(250)  # 当宽度未超过阈值时，恢复原来的最小高度


class WindowDetectionWidget(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent, '窗口检测', './assets/icon/window-detection.png')
        self.post_thread = None
        self.is_listening = False
        self.using_fake_window = False
        self.fake_window_name = ''

        self.window_name_layout = QHBoxLayout()
        self.window_name_label = BodyLabel()
        self.window_name = LineEdit()

        self.name_layout = QHBoxLayout()
        self.name_label = BodyLabel()
        self.name = LineEdit()

        self.fake_layout = QHBoxLayout()
        self.fake_label = BodyLabel()
        self.update_fake_window = SwitchButton()

        self.play_pause_button = PrimaryPushButton()

        self.fake_label.setText('使用自定义名称：')
        self.update_fake_window.checkedChanged.connect(self.set_using_fake_window)
        self.fake_layout.addWidget(self.fake_label)
        self.fake_layout.addWidget(self.update_fake_window)

        self.name_label.setText('设备名称：')
        self.name.setText(cf.device_name)
        self.name.setPlaceholderText('您的设备名称')

        self.window_name_label.setText('检测窗口：')
        self.window_name.setReadOnly(True)
        self.window_name.setPlaceholderText('检测到的窗口名称将会显示于此')
        self.window_name.textEdited.connect(self.set_fake_window)

        self.play_pause_button.setText('开始检测')
        self.play_pause_button.setIcon(fIcon.PLAY)
        self.play_pause_button.clicked.connect(self.start_listen)

        self.window_name_layout.addWidget(self.window_name_label)
        self.window_name_layout.addWidget(self.window_name)
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name)
        self.content_layout.addLayout(self.name_layout)
        self.content_layout.addLayout(self.window_name_layout)
        self.content_layout.addLayout(self.fake_layout)
        self.content_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.content_layout.addWidget(self.play_pause_button)

        self.update_timer = QTimer()
        self.update_timer.setInterval(cf.check_interval)
        self.update_timer.timeout.connect(self.update_window)

    def set_fake_window(self, text):
        self.fake_window_name = text

    def set_using_fake_window(self, checked):
        self.using_fake_window = checked
        if checked:
            self.window_name.clear()
            self.window_name.setReadOnly(False)
        else:
            self.fake_window_name = ''
            self.window_name.setReadOnly(True)
            self.window_name.clear()

    def start_listen(self):
        if not self.is_listening:
            self.update_window()
            self.play_pause_button.setText('停止上传')
            self.play_pause_button.setIcon(fIcon.PAUSE)
            self.update_timer.start()
            self.is_listening = True
            return

        self.play_pause_button.setText('开始上传')
        self.play_pause_button.setIcon(fIcon.PLAY)
        # self.window_name.clear()
        self.update_timer.stop()
        self.is_listening = False

    def update_window(self):
        def callback(data):
            if self.using_fake_window:
                return
            self.window_name.setText(data[0])

        self.post_thread = postThread(self.fake_window_name)
        self.post_thread.list_signal.connect(callback)
        self.post_thread.start()


class StatusWidget(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent, '切换状态', './assets/icon/check-status.png')
        # status = ['复活啦 ( •̀ ω •́ )✧', '似了 o(TヘTo)']

        self.change_status_thread = None
        menu = RoundMenu()
        # menu.addActions([
        #     Action(fIcon.CALORIES, status[0]),
        #     Action(fIcon.QUIET_HOURS, status[1])
        # ])
        for key, status in cf.status_dict.items():
            menu.addAction(Action(status, triggered=partial(self.change_status, key)))

        self.body_label = BodyLabel()
        self.status_label = SubtitleLabel()
        self.switch_button = PrimaryDropDownPushButton()

        self.body_label.setText(f'当前状态：')  # Body
        self.body_label.setAlignment(Qt.AlignCenter)
        self.status_label.setText(cf.status_info['name'])  # 状态
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setTextColor(QColor('#666'), QColor('#CCC'))
        self.switch_button.setText('设置状态')

        self.switch_button.setIcon(fIcon.MESSAGE)
        self.switch_button.setMenu(menu)

        self.content_layout.addWidget(self.body_label)
        self.content_layout.addWidget(self.status_label)
        self.content_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.content_layout.addWidget(self.switch_button)

    def change_status(self, status):
        def callback(data):
            try:
                print(f'success: [{data["success"]}], code: [{data["code"]}], set_to: [{data["set_to"]}]')
                current_state = cf.status_dict[data['set_to']].split(' - ')[0]

                InfoBar.success(
                    title='更改状态成功',
                    content=f"已将状态更改为 {current_state}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )
                self.status_label.setText(current_state)  # 状态
            except:
                print(f'RawData: {data}')
                InfoBar.error(
                    title='更改状态失败',
                    content=f"错误代码： {data}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )

        self.change_status_thread = getDictThread(f'{cf.server}/set/{cf.secret}/{status}')
        self.change_status_thread.json_signal.connect(callback)
        self.change_status_thread.start()


class DayProgressWidget(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent, '今日进度', './assets/icon/day-progress.png')
        self.body_label = BodyLabel()
        self.body_label.setText(f'{datetime.now().strftime("%H:%M:%S")}\n今天已经过了')
        self.body_label.setFont(QFont('Microsoft YaHei', 12))
        self.body_label.setAlignment(Qt.AlignCenter)

        self.day_progress_ring = ProgressRing()
        self.day_progress_ring.setRange(0, 100)
        self.day_progress_ring.setValue(int((datetime.now().hour * 60 + datetime.now().minute) / 14.4))
        self.day_progress_ring.setFixedSize(100, 100)
        self.day_progress_ring.setStrokeWidth(8)
        self.day_progress_ring.setStyleSheet('font-size: 16px;')
        self.day_progress_ring.setTextVisible(True)

        self.content_layout.setSpacing(22)
        self.content_layout.addWidget(self.body_label)
        self.content_layout.addWidget(self.day_progress_ring)

        self.update_timer = QTimer()
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.update_progress)
        self.update_timer.start()

    def update_progress(self):
        self.day_progress_ring.setValue(int((datetime.now().hour * 60 + datetime.now().minute) / 14.4))
        self.body_label.setText(f'{datetime.now().strftime("%H:%M:%S")}\n今天已经过了')


widgets_config = {
    'base': BaseWidget,
    'state': StatusWidget,
    'day_progress': DayProgressWidget,
    'window-detection': WindowDetectionWidget
}


def get_widget(widget_name):
    for widget in widgets_config:
        if widget == widget_name:
            return widgets_config[widget]
    return BaseWidget
