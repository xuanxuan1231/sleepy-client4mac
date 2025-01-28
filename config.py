import json
import os

status = 0
status_info = {}
status_dict = {}
widgets_config = ['day_progress', 'state', 'window-detection', 'base']

server = 'https://sleepy.rinlit.cn:443'  # 服务器地址
secret = 'RinLitCw114514'  # 密钥
device_name = '🖥️ Rin\'s Potato PC'  # 设备名称
device_id = 'pc-1'  # 设备id，我也不知道怎么用
check_interval = 2000  # 检查间隔（ms）


class ConfigMgr:  # 简易的配置文件管理器
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
        self.config = {}
        self.full_path = os.path.join(self.path, self.filename)

    def load_config(self, default_config):
        if default_config is None:
            print('Warning: default_config is None, use empty config instead.')
            default_config = {}
        # 如果文件存在，加载配置
        if os.path.exists(self.full_path):
            with open(self.full_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config  # 如果文件不存在，使用默认配置
            self.save_config()

    def update_config(self):  # 更新配置
        try:
            with open(self.full_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f'Error: {e}')
            self.config = {}

    def upload_config(self, key=str or list, value=None):
        if type(key) is str:
            self.config[key] = value
        elif type(key) is list:
            for k in key:
                self.config[k] = value
        else:
            raise TypeError('key must be str or list (键的类型必须是字符串或列表)')
        self.save_config()

    def save_config(self):
        with open(self.full_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def __getitem__(self, key):
        return self.config.get(key)

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save_config()

    def __repr__(self):
        return json.dumps(self.config, ensure_ascii=False, indent=4)
