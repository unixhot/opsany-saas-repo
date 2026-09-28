# -*- coding: utf-8 -*-
import mongoengine

from config import RUN_VER
if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 本地开发环境
RUN_MODE = 'DEVELOP'

# APP本地静态资源目录
STATIC_URL = '/static/'
UPLOAD_PATH = "E:/womaiyun/"
UPLOAD_SCRIPT_PATH = os.path.join("uploads", APP_CODE, "script")
UPLOAD_COMMAND_PATH = os.path.join("uploads", APP_CODE, "command")

PATH_LIST = [
    os.path.join(UPLOAD_PATH, UPLOAD_SCRIPT_PATH),
    os.path.join(UPLOAD_PATH, UPLOAD_COMMAND_PATH)
]

for PATH in PATH_LIST:
    if not os.path.exists(PATH):
        os.makedirs(PATH)

# APP静态资源目录url
# REMOTE_STATIC_URL = '%sremote/' % STATIC_URL

# Celery 消息队列设置 RabbitMQ
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# Celery 消息队列设置 Redis
BROKER_URL = 'redis://localhost:6379/0'

DEBUG = True

# 本地开发数据库设置
# USE FOLLOWING SQL TO CREATE THE DATABASE NAMED APP_CODE
# SQL: CREATE DATABASE `framework_py` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; # noqa: E501
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': APP_CODE,
        'USER': 'root',
        'PASSWORD': '123456.coM',
        'HOST': '192.168.0.111',
        'PORT': '3306',
    },
}

# MongoDB配置
MONGO_CONN = mongoengine.connect(
    db="devops",  # 需要进行操作的数据库名称
    alias='default',  # 必须定义一个default数据库
    host="192.168.0.111",
    username="devops",
    password="123456.coM",
    port=27017,
    connect=False
)

# 自定义中间件
MIDDLEWARE += (
    'repo.utils.middleware.CreateUserMiddleware',
)

# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings.py 加入版本管理忽略文件中
try:
    from .local_settings import *  # noqa
except ImportError:
    pass


# 线上bk_token，本地调试使用
BK_TOKEN = "SBn_Zo3v8XDMdRqL3GPOCSv7VGqjtMV4g7h_ilhQwhX6mdkos3HKG7QCu4rJt20n"
# SITE_URL本地调试指定为空
SITE_URL = {"SITE_URL": ""}

# Harbor Settings
HARBOR_URL = ""
HARBOR_USERNAME = ""
HARBOR_PASSWORD = ""
