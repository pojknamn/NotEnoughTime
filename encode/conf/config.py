import os
from sys import platform
from loguru import logger
import telebot

logger.add('all_prog_logs.log', rotation='150 MB')
SPLITTER = os.sep
drives = ["G:/", "E:/"]
drives_friend = ['G:/Films/Арина']
ENCODED_FOLDER = 'edited'
if platform == 'linux':
    drives = ['/mnt/LQ', '/mnt/HQ']
    drives_friend = ['/mnt/LQ/Films/Арина']

BASE_FOLDER_LEN = len(drives[0].split('/'))

DEFAULT_DRIVES = {
    "base_g": {
        'path': drives[0],
        'display_name': 'LQ',
        'option_type': 'workdir',
    },
    "base_e": {
        'path': drives[1],
        'display_name': 'HQ',
        'option_type': 'workdir',
    }
}
DEFAULT_DRIVE_AYRISH = {
    'base_g': {
        'path': drives_friend[0],
        'display_name': 'Фильмы Аришки',
        'option_type': 'workdir',
    }
}
CLOSE_N_CHOOSE = {
    'render': {
        'display_name': 'Выбрать эту папку для рендера.',
        'path': '',
        'option_type': 'render',
    },
    '0': {
        'display_name': 'Закрыть',
        'path': '',
        'option_type': 'close',
    },
    'remove': {
        'display_name': 'Удалить текущую папку',
        'path': '',
        'option_type': 'remove',
    }
}

DEFAULT_OPTIONS = {
    'subtitle': {'text': 'Надо субтитры? [0]', 'default': 0},
    'recursive': {'text': 'Рекурсивно? [1]', 'default': 1},
    'serial': {'text': 'Это сериал? [1]', 'default': 1},
    'speed': {'text': 'Выберите скорость [2.0]', 'default': 2.0},
    'drive': {'text': 'Выберите диск: G:/ или E:/  [0]', 'default': 0},
    'external': {'text': 'Внешнее аудио? [0]', 'default': 0},
}
SUB_N_SPEED = {
    "speed": [
        1.5,
        1.6,
        1.7,
        1.8,
        1.9,
        2.0,
    ],
    "subs": [0, 1]
}

ENCODE_KEYS = ['ticket_id', 'option_type', 'option_value']

# QbittorrentCreds
QBITCREDS = {
    "host": "localhost",
    "port": 8080,
    "username": os.getenv("QUSER"),
    "password": os.getenv("QPASS"),
}

# Telebot options
ADMIN_CHAT_ID = os.getenv('ADMINID')
TG_TOKEN = os.getenv("TGTOKEN")

if not ADMIN_CHAT_ID or not TG_TOKEN:
    raise RuntimeError('Вы не указали Токен или Айди админа')
# Ticket statuses
FAILED = 'F'
CLOSED = 'X'
PENDING = 'P'
WORKING = 'W'
DONE = 'D'
CREATED = 'C'
RMTREE = "R"


class ChatId:
    admin = int(ADMIN_CHAT_ID)
    friend = os.getenv('FRIENDID')


bot_instance = telebot.TeleBot(token=TG_TOKEN)
