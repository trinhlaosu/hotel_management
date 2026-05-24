"""
Cấu hình Django – Hệ thống Quản lý Khách sạn (nội bộ)
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-hotel-nhom04-2026'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hotel_app.apps.HotelConfig',   # App quản lý khách sạn
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'config.wsgi.application'

# Kết nối MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':   'hotel_management',
        'USER':   'root',
        'PASSWORD': '123456',        
        'HOST':   '127.0.0.1',
        'PORT':   '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# Session – lưu trong database
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400   # 1 ngày

LANGUAGE_CODE = 'vi'
TIME_ZONE     = 'Asia/Ho_Chi_Minh'
USE_I18N      = True
USE_TZ        = True

STATIC_URL          = 'static/'
DEFAULT_AUTO_FIELD  = 'django.db.models.BigAutoField'

